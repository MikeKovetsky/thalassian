#!/usr/bin/env python3
"""Minimal read-only reader for a local World of Warcraft CASC storage.

Standard library only and Python 3.9 compatible, so it can run on the machine
that holds the game install (the Mac mini here) without installing anything.
It never writes inside the install directory.

Supports: .build.info, build config, local v7 .idx indices (Data/data and
Data/ecache), BLTE (N/Z/F/E chunks, Salsa20 decryption with known TACT keys),
the encoding file (CKey -> EKey) and the MFST root (FileDataID -> CKey, v1/v2).

Usage examples (run where the install lives):
  python3 casc.py info    --install "/Applications/World of Warcraft" --product wowf
  python3 casc.py rootcsv --install ... --product wowf --out root.csv
  python3 casc.py extract --install ... --product wowf --list files.txt --out outdir \
      [--keys TACTKeys-WoW.txt]
files.txt: one "FileDataID;relative/path" per line. Files are written to outdir/path.
"""
import argparse
import hashlib
import os
import struct
import sys
import zlib

# --------------------------------------------------------------------------
# Salsa20 (16-byte key variant used by TACT)
# --------------------------------------------------------------------------
_M32 = 0xFFFFFFFF


def _rotl(v, c):
    return ((v << c) & _M32) | (v >> (32 - c))


def _salsa20_block(state):
    x = list(state)
    for _ in range(10):
        # column round
        x[4] ^= _rotl((x[0] + x[12]) & _M32, 7)
        x[8] ^= _rotl((x[4] + x[0]) & _M32, 9)
        x[12] ^= _rotl((x[8] + x[4]) & _M32, 13)
        x[0] ^= _rotl((x[12] + x[8]) & _M32, 18)
        x[9] ^= _rotl((x[5] + x[1]) & _M32, 7)
        x[13] ^= _rotl((x[9] + x[5]) & _M32, 9)
        x[1] ^= _rotl((x[13] + x[9]) & _M32, 13)
        x[5] ^= _rotl((x[1] + x[13]) & _M32, 18)
        x[14] ^= _rotl((x[10] + x[6]) & _M32, 7)
        x[2] ^= _rotl((x[14] + x[10]) & _M32, 9)
        x[6] ^= _rotl((x[2] + x[14]) & _M32, 13)
        x[10] ^= _rotl((x[6] + x[2]) & _M32, 18)
        x[3] ^= _rotl((x[15] + x[11]) & _M32, 7)
        x[7] ^= _rotl((x[3] + x[15]) & _M32, 9)
        x[11] ^= _rotl((x[7] + x[3]) & _M32, 13)
        x[15] ^= _rotl((x[11] + x[7]) & _M32, 18)
        # row round
        x[1] ^= _rotl((x[0] + x[3]) & _M32, 7)
        x[2] ^= _rotl((x[1] + x[0]) & _M32, 9)
        x[3] ^= _rotl((x[2] + x[1]) & _M32, 13)
        x[0] ^= _rotl((x[3] + x[2]) & _M32, 18)
        x[6] ^= _rotl((x[5] + x[4]) & _M32, 7)
        x[7] ^= _rotl((x[6] + x[5]) & _M32, 9)
        x[4] ^= _rotl((x[7] + x[6]) & _M32, 13)
        x[5] ^= _rotl((x[4] + x[7]) & _M32, 18)
        x[11] ^= _rotl((x[10] + x[9]) & _M32, 7)
        x[8] ^= _rotl((x[11] + x[10]) & _M32, 9)
        x[9] ^= _rotl((x[8] + x[11]) & _M32, 13)
        x[10] ^= _rotl((x[9] + x[8]) & _M32, 18)
        x[12] ^= _rotl((x[15] + x[14]) & _M32, 7)
        x[13] ^= _rotl((x[12] + x[15]) & _M32, 9)
        x[14] ^= _rotl((x[13] + x[12]) & _M32, 13)
        x[15] ^= _rotl((x[14] + x[13]) & _M32, 18)
    return struct.pack("<16I", *[(x[i] + state[i]) & _M32 for i in range(16)])


def salsa20_xor(key, nonce, data):
    """Salsa20/20 keystream XOR. key: 16 or 32 bytes, nonce: 8 bytes."""
    if len(key) == 16:
        const = b"expand 16-byte k"
        k1 = k2 = key
    else:
        const = b"expand 32-byte k"
        k1, k2 = key[:16], key[16:]
    c = struct.unpack("<4I", const)
    kw1 = struct.unpack("<4I", k1)
    kw2 = struct.unpack("<4I", k2)
    nw = struct.unpack("<2I", nonce)
    out = bytearray(len(data))
    nblocks = (len(data) + 63) // 64
    for b in range(nblocks):
        state = [c[0], kw1[0], kw1[1], kw1[2], kw1[3], c[1], nw[0], nw[1],
                 b & _M32, (b >> 32) & _M32, c[2], kw2[0], kw2[1], kw2[2], kw2[3], c[3]]
        ks = _salsa20_block(state)
        seg = data[b * 64:(b + 1) * 64]
        n = len(seg)
        x = int.from_bytes(seg, "little") ^ int.from_bytes(ks[:n], "little")
        out[b * 64:b * 64 + n] = x.to_bytes(n, "little")
    return bytes(out)


# --------------------------------------------------------------------------
# Jenkins96 (hashlittle2) for root name hashes
# --------------------------------------------------------------------------
def _rot(x, k):
    return ((x << k) | (x >> (32 - k))) & _M32


def hashlittle2(data, pc=0, pb=0):
    length = len(data)
    a = b = c = (0xDEADBEEF + length + pc) & _M32
    c = (c + pb) & _M32
    i = 0
    while length > 12:
        a = (a + struct.unpack_from("<I", data, i)[0]) & _M32
        b = (b + struct.unpack_from("<I", data, i + 4)[0]) & _M32
        c = (c + struct.unpack_from("<I", data, i + 8)[0]) & _M32
        a = (a - c) & _M32; a ^= _rot(c, 4); c = (c + b) & _M32
        b = (b - a) & _M32; b ^= _rot(a, 6); a = (a + c) & _M32
        c = (c - b) & _M32; c ^= _rot(b, 8); b = (b + a) & _M32
        a = (a - c) & _M32; a ^= _rot(c, 16); c = (c + b) & _M32
        b = (b - a) & _M32; b ^= _rot(a, 19); a = (a + c) & _M32
        c = (c - b) & _M32; c ^= _rot(b, 4); b = (b + a) & _M32
        length -= 12
        i += 12
    if length == 0:
        return c, b
    tail = data[i:] + b"\0" * (12 - length)
    a = (a + struct.unpack_from("<I", tail, 0)[0]) & _M32
    b = (b + struct.unpack_from("<I", tail, 4)[0]) & _M32
    c = (c + struct.unpack_from("<I", tail, 8)[0]) & _M32
    c ^= b; c = (c - _rot(b, 14)) & _M32
    a ^= c; a = (a - _rot(c, 11)) & _M32
    b ^= a; b = (b - _rot(a, 25)) & _M32
    c ^= b; c = (c - _rot(b, 16)) & _M32
    a ^= c; a = (a - _rot(c, 4)) & _M32
    b ^= a; b = (b - _rot(a, 14)) & _M32
    c ^= b; c = (c - _rot(b, 24)) & _M32
    return c, b


def name_hash(path):
    p = path.upper().replace("/", "\\").encode("ascii", "replace")
    c, b = hashlittle2(p)
    return (c << 32) | b


# --------------------------------------------------------------------------
# Key list
# --------------------------------------------------------------------------
def load_keys(paths):
    """Load TACT keys from files with lines 'KEYNAME KEY [...]' (hex)."""
    keys = {}
    for p in paths or []:
        with open(p, encoding="utf-8", errors="replace") as f:
            for line in f:
                parts = line.replace(";", " ").split()
                if len(parts) >= 2 and len(parts[0]) == 16 and len(parts[1]) == 32:
                    try:
                        keys[parts[0].upper()] = bytes.fromhex(parts[1])
                    except ValueError:
                        pass
    return keys


class MissingKey(Exception):
    pass


# --------------------------------------------------------------------------
# BLTE
# --------------------------------------------------------------------------
def blte_decode(data, keys=None, missing=None, zero_missing=True):
    """Decode a BLTE blob. Chunks encrypted with an unknown key become zero
    bytes (if zero_missing) and the key name is added to the `missing` set."""
    if data[:4] != b"BLTE":
        raise ValueError("not BLTE")
    header_size = struct.unpack_from(">I", data, 4)[0]
    chunks = []
    if header_size == 0:
        chunks.append((len(data) - 8, None, 8))
    else:
        flags = data[8]
        count = int.from_bytes(data[9:12], "big")
        pos = 12
        entry = 24 if flags == 0x0F else 40
        off = header_size
        for _ in range(count):
            csize, dsize = struct.unpack_from(">II", data, pos)
            chunks.append((csize, dsize, off))
            off += csize
            pos += entry
    out = []
    for idx, (csize, dsize, off) in enumerate(chunks):
        out.append(_blte_chunk(data[off:off + csize], idx, dsize, keys, missing, zero_missing))
    return b"".join(out)


def _blte_chunk(chunk, index, dsize, keys, missing, zero_missing):
    mode = chunk[:1]
    if mode == b"N":
        return chunk[1:]
    if mode == b"Z":
        return zlib.decompress(chunk[1:])
    if mode == b"F":
        return blte_decode(chunk[1:], keys, missing, zero_missing)
    if mode == b"E":
        p = 1
        kn_len = chunk[p]; p += 1
        key_name = chunk[p:p + kn_len][::-1].hex().upper(); p += kn_len
        iv_len = chunk[p]; p += 1
        iv = bytearray(chunk[p:p + iv_len]); p += iv_len
        enc_type = chunk[p:p + 1]; p += 1
        key = (keys or {}).get(key_name)
        if key is None or enc_type != b"S":
            if missing is not None:
                missing.add(key_name)
            if zero_missing and dsize is not None:
                return b"\0" * dsize
            raise MissingKey(key_name)
        for i in range(4):
            iv[i] ^= (index >> (i * 8)) & 0xFF
        nonce = bytes(iv) + b"\0" * (8 - len(iv))
        dec = salsa20_xor(key, nonce, chunk[p:])
        return _blte_chunk(dec, index, dsize, keys, missing, zero_missing)
    if not chunk:
        return b""
    raise ValueError("unknown BLTE chunk mode %r" % mode)


# --------------------------------------------------------------------------
# Local storage
# --------------------------------------------------------------------------
def read_build_info(install):
    with open(os.path.join(install, ".build.info"), encoding="utf-8") as f:
        lines = [l.rstrip("\n") for l in f if l.strip()]
    cols = [c.split("!")[0] for c in lines[0].split("|")]
    return [dict(zip(cols, l.split("|"))) for l in lines[1:]]


def read_config(install, key):
    p = os.path.join(install, "Data", "config", key[:2], key[2:4], key)
    out = {}
    with open(p, encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip()
    return out


class LocalIndex(object):
    """v7 .idx files of one storage directory (Data/data or Data/ecache)."""

    def __init__(self, folder):
        self.folder = folder
        self.entries = {}
        best = {}
        for name in os.listdir(folder):
            if name.endswith(".idx") and len(name) == 14:
                bucket, ver = int(name[:2], 16), int(name[2:10], 16)
                if bucket not in best or ver > best[bucket][0]:
                    best[bucket] = (ver, name)
        for bucket, (ver, name) in sorted(best.items()):
            self._load(os.path.join(folder, name))

    def _load(self, path):
        with open(path, "rb") as f:
            raw = f.read()
        (hsize, _hhash, version, _bucket, _extra, size_len, offs_len, key_len,
         offs_bits) = struct.unpack_from("<IIHBBBBBB", raw, 0)
        if version != 7:
            raise ValueError("unsupported idx version %d in %s" % (version, path))
        pos = (8 + hsize + 0x0F) & ~0x0F
        entries_size = struct.unpack_from("<I", raw, pos)[0]
        pos += 8
        esz = key_len + offs_len + size_len
        mask = (1 << offs_bits) - 1
        end = pos + entries_size
        while pos + esz <= end:
            key = raw[pos:pos + key_len]
            so = int.from_bytes(raw[pos + key_len:pos + key_len + offs_len], "big")
            size = int.from_bytes(raw[pos + key_len + offs_len:pos + esz], "little")
            pos += esz
            if key not in self.entries:
                self.entries[key] = (so >> offs_bits, so & mask, size)

    def read(self, ekey):
        e = self.entries.get(ekey[:9])
        if e is None:
            return None
        archive, offset, size = e
        with open(os.path.join(self.folder, "data.%03d" % archive), "rb") as f:
            f.seek(offset)
            blob = f.read(size)
        return blob[0x1E:]


class CASC(object):
    def __init__(self, install, product=None, keys=None, log=sys.stderr):
        self.install = install
        self.keys = keys or {}
        self.missing_keys = set()
        self.log = log
        infos = read_build_info(install)
        info = None
        for row in infos:
            if product is None or row.get("Product") == product:
                info = row
                break
        if info is None:
            raise SystemExit("product %r not in .build.info" % product)
        self.info = info
        self.build_config = read_config(install, info["Build Key"])
        self.stores = []
        for sub in ("data", "ecache"):
            d = os.path.join(install, "Data", sub)
            if os.path.isdir(d):
                self.stores.append(LocalIndex(d))
        self._ce_index = None
        self.root = None

    # ---- raw access ----
    def read_ekey(self, ekey, zero_missing=True):
        for st in self.stores:
            blob = st.read(ekey)
            if blob is not None:
                return blte_decode(blob, self.keys, self.missing_keys, zero_missing)
        return None

    def has_ekey(self, ekey):
        return any(ekey[:9] in st.entries for st in self.stores)

    # ---- encoding ----
    def load_encoding(self):
        ckey_hex, ekey_hex = self.build_config["encoding"].split()
        data = self.read_ekey(bytes.fromhex(ekey_hex))
        if data is None or data[:2] != b"EN":
            raise SystemExit("encoding file not found locally")
        (_ver, ck_size, ek_size, ce_page_kb, _es_page_kb, ce_pages, _es_pages, _unk,
         espec_size) = struct.unpack_from(">BBBHHIIBI", data, 2)
        pos = 22 + espec_size
        firsts = []
        for i in range(ce_pages):
            firsts.append(data[pos:pos + ck_size])
            pos += ck_size + 16
        self._enc = data
        self._enc_pages_start = pos
        self._enc_page_size = ce_page_kb * 1024
        self._enc_firsts = firsts
        self._ck = ck_size
        self._ek = ek_size

    def ckey_to_ekeys(self, ckey):
        """Return (decoded size, [ekeys]) or None."""
        import bisect
        if not hasattr(self, "_enc"):
            self.load_encoding()
        i = bisect.bisect_right(self._enc_firsts, ckey) - 1
        if i < 0:
            return None
        data = self._enc
        pos = self._enc_pages_start + i * self._enc_page_size
        end = pos + self._enc_page_size
        ck = self._ck
        ek = self._ek
        while pos < end:
            n = data[pos]
            if n == 0:
                break
            size = int.from_bytes(data[pos + 1:pos + 6], "big")
            key = data[pos + 6:pos + 6 + ck]
            if key == ckey:
                ekeys = [data[pos + 6 + ck + j * ek:pos + 6 + ck + (j + 1) * ek] for j in range(n)]
                return size, ekeys
            if key > ckey:
                break
            pos += 6 + ck + n * ek
        return None

    def read_ckey(self, ckey, zero_missing=True):
        r = self.ckey_to_ekeys(ckey)
        if r is None:
            return None
        for ek in r[1]:
            if self.has_ekey(ek):
                return self.read_ekey(ek, zero_missing)
        return None

    # ---- root ----
    def load_root(self):
        """Parse the MFST root into a list of (fdid, ckey, locale, content, namehash)."""
        root_ckey = bytes.fromhex(self.build_config["root"].split()[0])
        data = self.read_ckey(root_ckey)
        if data is None:
            raise SystemExit("root not found locally")
        recs = []
        magic = data[:4]
        pos = 0
        version = 1
        if magic == b"TSFM":
            hs, ver = struct.unpack_from("<II", data, 4)
            if hs < 0x100 and ver in (1, 2, 3):
                version = ver
                pos = hs
            else:
                pos = 12
        else:
            raise SystemExit("legacy (pre-MFST) root not supported")
        n = len(data)
        while pos + 12 <= n:
            if version >= 2:
                num, locale, f1, f2 = struct.unpack_from("<IIII", data, pos)
                f3 = data[pos + 16]
                content = f1 | f2 | (f3 << 17)
                pos += 17
            else:
                num, content, locale = struct.unpack_from("<III", data, pos)
                pos += 12
            deltas = struct.unpack_from("<%di" % num, data, pos)
            pos += 4 * num
            ckeys_pos = pos
            pos += 16 * num
            has_names = not (content & 0x10000000)
            names_pos = pos
            if has_names:
                pos += 8 * num
            fd = -1
            for j in range(num):
                fd = fd + 1 + deltas[j]
                ck = data[ckeys_pos + 16 * j:ckeys_pos + 16 * (j + 1)]
                nh = struct.unpack_from("<Q", data, names_pos + 8 * j)[0] if has_names else None
                recs.append((fd, ck, locale, content, nh))
        self.root = recs
        self.root_version = version
        return recs

    def fdid_map(self, locale_mask=0x2):
        """FileDataID -> ckey, preferring entries for the given locale and
        without the LowViolence (0x80) flag."""
        if self.root is None:
            self.load_root()
        best = {}
        for fd, ck, loc, content, _nh in self.root:
            if not (loc & locale_mask) and loc != 0xFFFFFFFF and loc != 0:
                continue
            score = 0 if content & 0x80 else 1
            cur = best.get(fd)
            if cur is None or score > cur[1]:
                best[fd] = (ck, score)
        return {k: v[0] for k, v in best.items()}


# --------------------------------------------------------------------------
# Files that are not on disk: fetch from Blizzard's public CDN
# --------------------------------------------------------------------------
def find_in_cdn_indices(install, ekeys):
    """Look the EKeys up in the local copies of the CDN archive indices
    (Data/indices/<archive>.index). Returns {ekey: (archive, offset, size)}."""
    folder = os.path.join(install, "Data", "indices")
    hits = {}
    want = set(ekeys)
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".index") or not want - set(hits):
            continue
        with open(os.path.join(folder, name), "rb") as f:
            data = f.read()
        nblocks = (len(data) - 28) // (4096 + 24)
        limit = nblocks * 4096
        for ek in want - set(hits):
            p = data.find(ek)
            while p != -1 and p < limit:
                if (p % 4096) % 24 == 0:
                    size, off = struct.unpack_from(">II", data, p + 16)
                    hits[ek] = (name[:-6], off, size)
                    break
                p = data.find(ek, p + 1)
    return hits


def cdn_get(hosts, path, key, rng=None, timeout=60):
    try:
        from urllib.request import Request, urlopen
    except ImportError:  # pragma: no cover
        raise
    last = None
    for host in hosts:
        url = "http://%s/%s/data/%s/%s/%s" % (host, path, key[:2], key[2:4], key)
        req = Request(url, headers={"User-Agent": "casc-reader"})
        if rng:
            req.add_header("Range", "bytes=%d-%d" % (rng[0], rng[0] + rng[1] - 1))
        try:
            with urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:  # try the next host
            last = e
    raise last


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["info", "rootcsv", "extract", "cdnfetch"],
                    help="cdnfetch: like extract, but files that are not on disk are range-downloaded "
                         "from the CDN hosts in .build.info (free, public)")
    ap.add_argument("--install", required=True)
    ap.add_argument("--product", default=None)
    ap.add_argument("--keys", nargs="*", default=[])
    ap.add_argument("--list")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    keys = load_keys(a.keys)
    c = CASC(a.install, a.product, keys)
    if a.cmd == "info":
        print("product", c.info.get("Product"), "version", c.info.get("Version"))
        for k in ("build-name", "root", "encoding", "build-uid"):
            print(k, "=", c.build_config.get(k))
        print("index entries:", [len(s.entries) for s in c.stores])
        recs = c.load_root()
        print("root version", c.root_version, "records", len(recs),
              "unique fdids", len(set(r[0] for r in recs)))
        return
    if a.cmd == "rootcsv":
        recs = c.load_root()
        present = 0
        with open(a.out, "w") as f:
            f.write("fdid;ckey;locale;content;namehash;local\n")
            enc = {}
            for fd, ck, loc, content, nh in recs:
                r = c.ckey_to_ekeys(ck)
                local = int(bool(r) and any(c.has_ekey(e) for e in r[1]))
                present += local
                f.write("%d;%s;%08x;%08x;%s;%d\n" % (fd, ck.hex(), loc, content,
                                                     "" if nh is None else "%016x" % nh, local))
        print("wrote", len(recs), "root records,", present, "present locally")
        return
    if a.cmd in ("extract", "cdnfetch"):
        fmap = c.fdid_map()
        ok = miss = 0
        with open(a.list, encoding="utf-8") as f:
            items = [l.strip().split(";", 1) for l in f if l.strip()]
        remote = {}
        if a.cmd == "cdnfetch":
            need = {}
            for fd_s, _rel in items:
                ck = fmap.get(int(fd_s))
                r = c.ckey_to_ekeys(ck) if ck else None
                if r and not any(c.has_ekey(e) for e in r[1]):
                    need[int(fd_s)] = r[1][0]
            hits = find_in_cdn_indices(a.install, list(need.values()))
            hosts = c.info.get("CDN Hosts", "").split()
            path = c.info.get("CDN Path", "tpr/wow")
            for fd, ek in need.items():
                h = hits.get(ek)
                try:
                    blob = cdn_get(hosts, path, h[0], (h[1], h[2])) if h else cdn_get(hosts, path, ek.hex())
                    remote[fd] = blte_decode(blob, c.keys, c.missing_keys, True)
                except Exception as e:
                    print("CDN FAIL", fd, e)
            print("fetched from CDN:", len(remote), "of", len(need), "not on disk")
        for fd_s, rel in items:
            fd = int(fd_s)
            ck = fmap.get(fd)
            data = remote.get(fd)
            if data is None:
                data = c.read_ckey(ck) if ck else None
            if data is None:
                miss += 1
                print("MISSING", fd, rel)
                continue
            dst = os.path.join(a.out, rel.replace("\\", "/"))
            os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
            with open(dst, "wb") as g:
                g.write(data)
            ok += 1
        print("extracted", ok, "missing", miss)
        if c.missing_keys:
            print("unknown TACT keys (zeroed chunks):", " ".join(sorted(c.missing_keys)))
        return


if __name__ == "__main__":
    main()
