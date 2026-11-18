#!/usr/bin/env python3
"""WDC5 (WoW DB2) reader driven by WoWDBDefs .dbd definitions. Stdlib only.

  python3 db2.py dump --dbd WoWDBDefs/definitions --build 1.60.1.70938 \
      --db2 dbfilesclient/broadcasttext.db2 --out BroadcastText.csv

The DBD gives column names and types; the DB2 file's own field storage info
gives offsets, bit widths, pallets and common data. Supports non-sparse and
sparse (offset map) tables, id lists, copy tables and relationship maps.
"""
import argparse
import csv
import os
import re
import struct
import sys


# --------------------------------------------------------------------------
# DBD parsing
# --------------------------------------------------------------------------
class DBDField(object):
    __slots__ = ("name", "size", "signed", "array", "is_id", "noninline", "relation", "type")

    def __repr__(self):
        return "%s<%s%s>[%s]%s" % (self.name, "" if self.signed else "u", self.size, self.array, self.type)


class DBDVersion(object):
    def __init__(self):
        self.layouts = set()
        self.builds = set()
        self.ranges = []
        self.fields = []


def parse_build(s):
    return tuple(int(x) for x in s.strip().split("."))


class DBD(object):
    def __init__(self, path):
        self.name = os.path.splitext(os.path.basename(path))[0]
        self.columns = {}
        self.versions = []
        with open(path, encoding="utf-8") as f:
            text = f.read()
        blocks = re.split(r"\n\s*\n", text.strip())
        for block in blocks:
            lines = [l.split("//")[0].rstrip() for l in block.splitlines()]
            lines = [l for l in lines if l.strip()]
            if not lines:
                continue
            if lines[0].strip() == "COLUMNS":
                for l in lines[1:]:
                    m = re.match(r"(\w+)(?:<([^>]*)>)?\s+(\w+)(\?)?", l.strip())
                    if m:
                        self.columns[m.group(3)] = m.group(1)
                continue
            v = DBDVersion()
            for l in lines:
                s = l.strip()
                if s.startswith("LAYOUT"):
                    v.layouts.update(x.strip().upper() for x in s[6:].split(","))
                elif s.startswith("BUILD"):
                    for part in s[5:].split(","):
                        part = part.strip()
                        if "-" in part:
                            a, b = part.split("-")
                            v.ranges.append((parse_build(a), parse_build(b)))
                        elif part:
                            v.builds.add(parse_build(part))
                elif s.startswith("COMMENT"):
                    continue
                else:
                    m = re.match(r"(?:\$([\w,]+)\$)?(\w+)(?:<(u?)(\d+)>)?(?:\[(\d+)\])?", s)
                    if not m:
                        continue
                    fld = DBDField()
                    ann = (m.group(1) or "").split(",")
                    fld.name = m.group(2)
                    fld.signed = m.group(3) != "u"
                    fld.size = int(m.group(4)) if m.group(4) else 32
                    fld.array = int(m.group(5)) if m.group(5) else 1
                    fld.is_id = "id" in ann
                    fld.noninline = "noninline" in ann
                    fld.relation = "relation" in ann
                    fld.type = self.columns.get(fld.name, "int")
                    v.fields.append(fld)
            if v.fields:
                self.versions.append(v)

    def find(self, build=None, layout=None):
        b = parse_build(build) if build else None
        if b is not None:
            for v in self.versions:
                if b in v.builds or any(lo <= b <= hi for lo, hi in v.ranges):
                    if layout is None or not v.layouts or layout.upper() in v.layouts:
                        return v
        if layout is not None:
            for v in self.versions:
                if layout.upper() in v.layouts:
                    return v
        return None


# --------------------------------------------------------------------------
# WDC5 reader
# --------------------------------------------------------------------------
HEADER_FMT = "<9IHH7I"


class DB2(object):
    def __init__(self, path, dbd, build=None):
        with open(path, "rb") as f:
            self.data = data = f.read()
        self.path = path
        magic = data[:4]
        if magic != b"WDC5":
            raise ValueError("%s: unsupported magic %r" % (path, magic))
        self.schema = data[8:136].split(b"\0")[0].decode("ascii", "replace")
        (self.record_count, self.field_count, self.record_size, self.string_table_size,
         self.table_hash, self.layout_hash, self.min_id, self.max_id, self.locale,
         self.flags, self.id_index, self.total_field_count, self.bitpacked_offset,
         self.lookup_column_count, self.storage_info_size, self.common_size,
         self.pallet_size, self.section_count) = struct.unpack_from(HEADER_FMT, data, 136)
        pos = 136 + struct.calcsize(HEADER_FMT)
        self.layout = "%08X" % self.layout_hash
        self.sections = []
        for _ in range(self.section_count):
            sec = struct.unpack_from("<Q8I", data, pos)
            self.sections.append(dict(zip(
                ("tact_key", "file_offset", "record_count", "string_table_size",
                 "offset_records_end", "id_list_size", "relationship_size",
                 "offset_map_count", "copy_table_count"), sec)))
            pos += 40
        self.field_struct = [struct.unpack_from("<hH", data, pos + 4 * i) for i in range(self.total_field_count)]
        pos += 4 * self.total_field_count
        self.storage = []
        for i in range(self.storage_info_size // 24):
            self.storage.append(struct.unpack_from("<HHIIIII", data, pos + 24 * i))
        pos += self.storage_info_size
        # pallet and common blocks, per field
        self.pallets = {}
        self.commons = {}
        ppos = pos
        cpos = pos + self.pallet_size
        for fi, (off_bits, size_bits, add_size, stype, v1, v2, v3) in enumerate(self.storage):
            if stype in (3, 4):
                n = add_size // 4
                self.pallets[fi] = struct.unpack_from("<%dI" % n, data, ppos)
                ppos += add_size
            elif stype == 2:
                n = add_size // 8
                m = {}
                for j in range(n):
                    rid, val = struct.unpack_from("<II", data, cpos + 8 * j)
                    m[rid] = val
                self.commons[fi] = (m, v1)
                cpos += add_size
        self.sparse = bool(self.flags & 1)
        self.dbd = dbd
        self.version = dbd.find(build, self.layout) if dbd else None
        if self.version is None:
            raise ValueError("%s: no DBD version for build %s layout %s" % (path, build, self.layout))
        self.inline_fields = [f for f in self.version.fields if not f.noninline]
        if len(self.inline_fields) != self.field_count:
            raise ValueError("%s: DBD has %d inline fields, file has %d" % (
                path, len(self.inline_fields), self.field_count))
        self.encrypted_sections = 0

    # ---- value helpers ----
    @staticmethod
    def _conv(raw, fld, bits=32):
        if fld.type == "float":
            return struct.unpack("<f", struct.pack("<I", raw & 0xFFFFFFFF))[0]
        if fld.signed and bits and raw >= (1 << (bits - 1)):
            return raw - (1 << bits)
        return raw

    def rows(self):
        data = self.data
        total_records_bytes = self.record_count * self.record_size
        # concatenated string tables of all sections (non-sparse only)
        strings = bytearray()
        for s in self.sections:
            if not self.sparse:
                st = s["file_offset"] + s["record_count"] * self.record_size
                strings += data[st:st + s["string_table_size"]]
        strings = bytes(strings)
        global_index = 0
        for s in self.sections:
            pos = s["file_offset"]
            if self.sparse:
                rec_base = pos
                pos = s["offset_records_end"]
            else:
                rec_base = pos
                pos += s["record_count"] * self.record_size + s["string_table_size"]
            id_list = struct.unpack_from("<%dI" % (s["id_list_size"] // 4), data, pos)
            pos += s["id_list_size"]
            copies = [struct.unpack_from("<II", data, pos + 8 * j) for j in range(s["copy_table_count"])]
            pos += 8 * s["copy_table_count"]
            offset_map = [struct.unpack_from("<IH", data, pos + 6 * j) for j in range(s["offset_map_count"])]
            pos += 6 * s["offset_map_count"]
            relmap = {}
            if s["relationship_size"]:
                n, _mn, _mx = struct.unpack_from("<III", data, pos)
                for j in range(n):
                    fid, ridx = struct.unpack_from("<II", data, pos + 12 + 8 * j)
                    relmap[ridx] = fid
                pos += s["relationship_size"]
            om_ids = struct.unpack_from("<%dI" % s["offset_map_count"], data, pos) if self.sparse else ()
            if s["tact_key"]:
                # encrypted section: if the client could not decrypt it the bytes are zero
                body = data[s["file_offset"]:s["file_offset"] + max(1, s["record_count"] * self.record_size)]
                if not any(body):
                    self.encrypted_sections += 1
                    global_index += s["record_count"]
                    continue
            by_id = {}
            for i in range(s["record_count"]):
                if self.sparse:
                    off, size = offset_map[i]
                    rec = data[off:off + size]
                    row = self._read_sparse(rec)
                else:
                    off = rec_base + i * self.record_size
                    rec = data[off:off + self.record_size]
                    row = self._read_fixed(rec, global_index, strings, total_records_bytes, id_list[i] if id_list else None)
                rid = None
                if id_list:
                    rid = id_list[i]
                elif self.sparse and om_ids:
                    rid = om_ids[i]
                for f in self.version.fields:
                    if f.noninline and f.is_id:
                        row[f.name] = rid
                    elif f.noninline and f.relation:
                        row[f.name] = relmap.get(i, 0)
                if rid is None:
                    idf = self.inline_fields[self.id_index] if self.id_index < len(self.inline_fields) else None
                    rid = row.get(idf.name) if idf else i
                    if isinstance(rid, list):
                        rid = rid[0]
                row["_id"] = rid
                by_id[rid] = row
                global_index += 1
                yield row
            for new_id, src_id in copies:
                src = by_id.get(src_id)
                if src is None:
                    continue
                row = dict(src)
                row["_id"] = new_id
                for f in self.version.fields:
                    if f.is_id:
                        row[f.name] = new_id
                yield row

    def _read_fixed(self, rec, gidx, strings, total_records_bytes, rid):
        row = {}
        recint = None
        for fi, fld in enumerate(self.inline_fields):
            off_bits, size_bits, _add, stype, v1, v2, v3 = self.storage[fi]
            if stype == 0:
                base = off_bits // 8
                if fld.type in ("string", "locstring"):
                    vals = []
                    for k in range(fld.array):
                        p = base + 4 * k
                        ofs = struct.unpack_from("<I", rec, p)[0]
                        if ofs == 0:
                            vals.append("")
                            continue
                        sp = gidx * self.record_size + p + ofs - total_records_bytes
                        if 0 <= sp < len(strings):
                            e = strings.find(b"\0", sp)
                            vals.append(strings[sp:e].decode("utf-8", "replace"))
                        else:
                            vals.append("")
                    row[fld.name] = vals if fld.array > 1 else vals[0]
                    continue
                esize = (size_bits // 8) // fld.array if fld.array else size_bits // 8
                if fld.type == "float":
                    esize = 4
                vals = []
                for k in range(fld.array):
                    raw = int.from_bytes(rec[base + k * esize: base + (k + 1) * esize], "little")
                    vals.append(self._conv(raw, fld, esize * 8))
                row[fld.name] = vals if fld.array > 1 else vals[0]
            elif stype in (1, 5):
                if recint is None:
                    recint = int.from_bytes(rec, "little")
                raw = (recint >> off_bits) & ((1 << size_bits) - 1)
                if stype == 5 and raw >= (1 << (size_bits - 1)):
                    raw -= 1 << size_bits
                row[fld.name] = self._conv(raw, fld, 0 if stype == 5 else size_bits) if fld.type == "float" else raw
            elif stype == 2:
                row[fld.name] = None  # filled below once the record ID is known
            elif stype in (3, 4):
                if recint is None:
                    recint = int.from_bytes(rec, "little")
                idx = (recint >> off_bits) & ((1 << size_bits) - 1)
                pal = self.pallets[fi]
                if stype == 3:
                    row[fld.name] = self._conv(pal[idx], fld, 32) if idx < len(pal) else None
                else:
                    cnt = v3
                    row[fld.name] = [self._conv(x, fld, 32) for x in pal[idx * cnt:(idx + 1) * cnt]]
            else:
                row[fld.name] = None
        if self.commons:
            if rid is None:
                idf = self.inline_fields[self.id_index]
                rid = row.get(idf.name)
            for fi, fld in enumerate(self.inline_fields):
                if self.storage[fi][3] == 2:
                    m, default = self.commons[fi]
                    row[fld.name] = self._conv(m.get(rid, default), fld, 32)
        return row

    def _read_sparse(self, rec):
        row = {}
        p = 0
        for fld in self.inline_fields:
            vals = []
            for _ in range(fld.array):
                if fld.type in ("string", "locstring"):
                    e = rec.find(b"\0", p)
                    if e < 0:
                        e = len(rec)
                    vals.append(rec[p:e].decode("utf-8", "replace"))
                    p = e + 1
                else:
                    n = 4 if fld.type == "float" else fld.size // 8
                    raw = int.from_bytes(rec[p:p + n], "little")
                    p += n
                    vals.append(self._conv(raw, fld, n * 8))
            row[fld.name] = vals if fld.array > 1 else vals[0]
        return row

    def columns(self):
        cols = []
        for f in self.version.fields:
            if f.array > 1:
                cols += ["%s[%d]" % (f.name, i) for i in range(f.array)]
            else:
                cols.append(f.name)
        return cols


def flatten(row, version):
    out = {}
    for f in version.fields:
        v = row.get(f.name)
        if f.array > 1:
            v = v if isinstance(v, (list, tuple)) else [v] * f.array
            for i in range(f.array):
                out["%s[%d]" % (f.name, i)] = v[i] if i < len(v) else ""
        else:
            out[f.name] = v
    return out


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=header, extrasaction="ignore")
        w.writeheader()
        n = 0
        for r in rows:
            w.writerow(r)
            n += 1
    return n


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["dump", "info"])
    ap.add_argument("--dbd", required=True, help="WoWDBDefs definitions folder")
    ap.add_argument("--build", required=True)
    ap.add_argument("--db2", required=True)
    ap.add_argument("--table", help="table name (default: from file name, matched case-insensitively)")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    name = a.table or os.path.splitext(os.path.basename(a.db2))[0]
    defs = {os.path.splitext(n)[0].lower(): os.path.join(a.dbd, n) for n in os.listdir(a.dbd)}
    dbd = DBD(defs[name.lower()])
    t = DB2(a.db2, dbd, a.build)
    if a.cmd == "info":
        print(dbd.name, "records", t.record_count, "fields", t.field_count, "layout", t.layout,
              "sparse", t.sparse, "sections", t.section_count)
        for fi, f in enumerate(t.inline_fields):
            print(fi, f, t.storage[fi])
        return
    rows = (flatten(r, t.version) for r in t.rows())
    n = write_csv(a.out, t.columns(), rows)
    print(dbd.name, n, "rows")


if __name__ == "__main__":
    main()
