#!/usr/bin/env python3
"""Reader for the client's hotfix cache (Cache/ADB/<locale>/DBCache.bin, 'XFTH' v9).

Each entry carries a table hash, a record ID, a status and (for valid rows) the
row data in the "uncompressed" hotfix layout: fields in DBD order, ints at their
DBD width, floats 4 bytes, strings inline and NUL-terminated, the non-inline ID
left out. Table hashes are resolved with WoWDBDefs' manifest.json.

  python3 hotfix.py --cache DBCache.bin --dbd WoWDBDefs --build 1.60.1.70938 --out outdir
Writes outdir/<Table>.csv (valid rows; status column for deletes) and a summary.
"""
import argparse
import csv
import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db2 import DBD, flatten  # noqa: E402

STATUS = {1: "valid", 2: "deleted", 3: "invalid", 4: "notpublic"}


def read_entries(path):
    with open(path, "rb") as f:
        d = f.read()
    if d[:4] != b"XFTH":
        raise ValueError("not a DBCache.bin")
    version, build = struct.unpack_from("<II", d, 4)
    if version != 9:
        raise ValueError("unsupported DBCache version %d" % version)
    pos = 44
    out = []
    while pos + 32 <= len(d):
        if d[pos:pos + 4] != b"XFTH":
            raise ValueError("desync at %d" % pos)
        region, push_id, unique_id, table_hash, record_id, size = struct.unpack_from("<iiIIII", d, pos + 4)
        status = d[pos + 28]
        data = d[pos + 32:pos + 32 + size]
        out.append(dict(region=region, push_id=push_id, unique_id=unique_id, table_hash=table_hash,
                        record_id=record_id, status=status, data=data))
        pos += 32 + size
    return build, out


def parse_row(data, fields, record_id):
    """Parse hotfix row bytes with the given DBD fields. Returns (row, consumed)."""
    row = {}
    p = 0
    for f in fields:
        if f.noninline and f.is_id:
            row[f.name] = record_id
            continue
        vals = []
        for _ in range(f.array):
            if f.type in ("string", "locstring"):
                e = data.find(b"\0", p)
                if e < 0:
                    raise ValueError("unterminated string")
                vals.append(data[p:e].decode("utf-8", "replace"))
                p = e + 1
            elif f.type == "float":
                if p + 4 > len(data):
                    raise ValueError("short")
                vals.append(struct.unpack_from("<f", data, p)[0])
                p += 4
            else:
                n = f.size // 8
                if p + n > len(data):
                    raise ValueError("short")
                vals.append(int.from_bytes(data[p:p + n], "little", signed=f.signed))
                p += n
        row[f.name] = vals if f.array > 1 else vals[0]
    return row, p


def parse_table_rows(entries, dbd, build):
    """Try the DBD version for this build; relation fields may or may not be inline."""
    v = dbd.find(build)
    if v is None:
        return None, "no DBD version for build"
    with_rel = [f for f in v.fields]
    without_rel = [f for f in v.fields if not (f.noninline and f.relation)]
    rows = []
    errors = 0
    for e in entries:
        if e["status"] != 1 or not e["data"]:
            continue
        row = None
        for fields in (with_rel, without_rel):
            try:
                r, used = parse_row(e["data"], [f if not (f.noninline and f.relation) else _inline(f) for f in fields], e["record_id"])
            except Exception:
                continue
            rest = e["data"][used:]
            # some rows carry a 28-byte trailer that starts with the TactKey table
            # hash (0xDF2F53CF); the row fields themselves are complete
            if used == len(e["data"]) or (len(rest) == 28 and rest[:4] == b"\xcf\x53\x2f\xdf"):
                row = r
                break
        if row is None:
            errors += 1
            continue
        row["_push_id"] = e["push_id"]
        row["_record_id"] = e["record_id"]
        rows.append(row)
    return (v, rows, errors), None


def _inline(f):
    import copy
    g = copy.copy(f)
    g.noninline = False
    return g


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cache", required=True)
    ap.add_argument("--dbd", required=True, help="WoWDBDefs repo root (definitions/ and manifest.json)")
    ap.add_argument("--build", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tables", nargs="*", help="only these tables (default: all)")
    a = ap.parse_args(argv)
    manifest = json.load(open(os.path.join(a.dbd, "manifest.json")))
    names = {int(m["tableHash"], 16): m["tableName"] for m in manifest if m.get("tableHash")}
    defs_dir = os.path.join(a.dbd, "definitions")
    build, entries = read_entries(a.cache)
    by_table = {}
    for e in entries:
        by_table.setdefault(e["table_hash"], []).append(e)
    os.makedirs(a.out, exist_ok=True)
    summary = []
    for th, es in sorted(by_table.items(), key=lambda kv: names.get(kv[0], "~%08X" % kv[0])):
        name = names.get(th, "Unknown_%08X" % th)
        counts = {}
        for e in es:
            counts[STATUS.get(e["status"], str(e["status"]))] = counts.get(STATUS.get(e["status"], str(e["status"])), 0) + 1
        info = dict(table=name, table_hash="%08X" % th, entries=len(es), **counts)
        if a.tables and name not in a.tables:
            continue
        path = os.path.join(defs_dir, name + ".dbd")
        if not os.path.exists(path):
            info["note"] = "no DBD"
            summary.append(info)
            continue
        res, err = parse_table_rows(es, DBD(path), a.build)
        if err:
            info["note"] = err
            summary.append(info)
            continue
        v, rows, errors = res
        info["parsed"] = len(rows)
        info["parse_errors"] = errors
        if rows:
            cols = ["_record_id", "_push_id"]
            for f in v.fields:
                cols += ["%s[%d]" % (f.name, i) for i in range(f.array)] if f.array > 1 else [f.name]
            with open(os.path.join(a.out, name + ".csv"), "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
                w.writeheader()
                for r in rows:
                    fr = flatten(r, v)
                    fr["_record_id"] = r["_record_id"]
                    fr["_push_id"] = r["_push_id"]
                    w.writerow(fr)
        # deleted / not-public record IDs are useful too (content the server hides)
        dels = [e for e in es if e["status"] != 1]
        if dels:
            with open(os.path.join(a.out, name + ".status.csv"), "w", newline="") as fh:
                w = csv.writer(fh)
                w.writerow(["record_id", "push_id", "status"])
                for e in dels:
                    w.writerow([e["record_id"], e["push_id"], STATUS.get(e["status"], e["status"])])
        summary.append(info)
    with open(os.path.join(a.out, "_summary.json"), "w") as fh:
        json.dump(dict(build=build, entries=len(entries), tables=summary), fh, indent=1)
    print("build", build, "entries", len(entries), "tables", len(summary))
    for s in summary:
        print(s)


if __name__ == "__main__":
    main()
