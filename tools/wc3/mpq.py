#!/usr/bin/env python3
"""Minimal read-only MPQ reader for Warcraft III maps (.w3m, .w3x, .w3n).

Standard library only and Python 3.9 compatible. Reads MPQ format version 0/1
archives from bytes in memory: the encrypted hash and block tables, single-unit
and sectored files, file encryption (with the fix-key flag), and the zlib and
bzip2 compressions that map text files use. PKWARE implode, Huffman and ADPCM
(audio) are reported as unsupported instead of decoded.

Usage:
  python3 mpq.py list    map.w3x
  python3 mpq.py extract map.w3x war3map.wts war3map.j --out outdir
"""
import argparse
import bz2
import os
import struct
import sys
import zlib

_M32 = 0xFFFFFFFF


def _crypt_table():
    table = [0] * 0x500
    seed = 0x00100001
    for i in range(0x100):
        idx = i
        for _ in range(5):
            seed = (seed * 125 + 3) % 0x2AAAAB
            hi = (seed & 0xFFFF) << 16
            seed = (seed * 125 + 3) % 0x2AAAAB
            lo = seed & 0xFFFF
            table[idx] = hi | lo
            idx += 0x100
    return table


CRYPT = _crypt_table()
HASH_OFFSET, HASH_A, HASH_B, HASH_KEY = 0, 1, 2, 3


def name_bytes(name):
    """A member name as the archive stores it: str names round-trip through surrogateescape."""
    return name if isinstance(name, bytes) else name.encode("utf-8", "surrogateescape")


def display_name(name):
    """A member name that is safe to print or use as a file name (bytes that are not UTF-8 become U+FFFD)."""
    return name_bytes(name).decode("utf-8", "replace")


def hash_string(s, kind):
    """Storm's name hash. Like Storm, it upper-cases ASCII letters only, maps '/' to '\\' and
    hashes the raw bytes, so non-ASCII names hash as the archive's own bytes."""
    seed1, seed2 = 0x7FED7FED, 0xEEEEEEEE
    for ch in name_bytes(s):
        if 0x61 <= ch <= 0x7A:
            ch -= 0x20
        elif ch == 0x2F:
            ch = 0x5C
        seed1 = CRYPT[(kind << 8) + ch] ^ ((seed1 + seed2) & _M32)
        seed2 = (ch + seed1 + seed2 + (seed2 << 5) + 3) & _M32
    return seed1


def decrypt(data, key):
    """Decrypt whole 32-bit words; trailing bytes (len % 4) are left as they are."""
    n = len(data) // 4
    words = struct.unpack_from("<%dI" % n, data)
    out = []
    seed = 0xEEEEEEEE
    for v in words:
        seed = (seed + CRYPT[0x400 + (key & 0xFF)]) & _M32
        ch = v ^ ((key + seed) & _M32)
        out.append(ch)
        key = ((((~key) << 0x15) + 0x11111111) & _M32) | (key >> 0x0B)
        seed = (ch + seed + (seed << 5) + 3) & _M32
    return struct.pack("<%dI" % n, *out) + data[n * 4:]


FILE_IMPLODE = 0x00000100
FILE_COMPRESS = 0x00000200
FILE_ENCRYPTED = 0x00010000
FILE_FIX_KEY = 0x00020000
FILE_SINGLE_UNIT = 0x01000000
FILE_DELETE_MARKER = 0x02000000
FILE_SECTOR_CRC = 0x04000000
FILE_EXISTS = 0x80000000


class Unsupported(Exception):
    pass


class NotMPQ(ValueError):
    """The data holds no MPQ header at a 512-byte boundary."""


def _decompress(buf, expected):
    """Decompress one MPQ sector with a leading compression-mask byte."""
    if not buf:
        return buf
    mask = buf[0]
    data = buf[1:]
    if mask == 0x12:
        raise Unsupported("LZMA")  # 0x12 is LZMA on its own, not bzip2 (0x10) plus zlib (0x02)
    if mask & ~(0x02 | 0x10):
        raise Unsupported("compression mask 0x%02x" % mask)
    if mask & 0x10:
        data = bz2.decompress(data)
    if mask & 0x02:
        data = zlib.decompress(data)
    return data


class MPQ(object):
    def __init__(self, data):
        self.data = data
        base = 0
        while True:
            base = data.find(b"MPQ\x1a", base)
            if base < 0:
                raise NotMPQ("no MPQ header")
            if base % 512 == 0:
                break
            base += 1
        self.base = base
        (hsize, _asize, version, shift, hpos, bpos, hcount,
         bcount) = struct.unpack_from("<IIHHIIII", data, base + 4)
        self.version = version
        self.sector_size = 512 << shift
        raw = data[base + hpos:base + hpos + 16 * hcount]
        raw = decrypt(raw, hash_string("(hash table)", HASH_KEY))
        self.hash = [struct.unpack_from("<IIHHI", raw, i * 16) for i in range(len(raw) // 16)]
        raw = data[base + bpos:base + bpos + 16 * bcount]
        raw = decrypt(raw, hash_string("(block table)", HASH_KEY))
        self.blocks = [struct.unpack_from("<IIII", raw, i * 16) for i in range(len(raw) // 16)]

    def find(self, name):
        if not self.hash:
            return None
        n = len(self.hash)
        start = hash_string(name, HASH_OFFSET) % n
        a, b = hash_string(name, HASH_A), hash_string(name, HASH_B)
        for i in range(n):
            ha, hb, _loc, _plat, bi = self.hash[(start + i) % n]
            if bi == 0xFFFFFFFF:
                return None
            if ha == a and hb == b and bi < len(self.blocks):
                return bi
        return None

    def has(self, name):
        return self.find(name) is not None

    def read(self, name):
        bi = self.find(name)
        if bi is None:
            raise KeyError(name)
        off, csize, fsize, flags = self.blocks[bi]
        if not flags & FILE_EXISTS or flags & FILE_DELETE_MARKER:
            raise KeyError(name)
        if flags & FILE_IMPLODE:
            raise Unsupported("PKWARE implode")
        start = self.base + off
        key = 0
        if flags & FILE_ENCRYPTED:
            key = hash_string(name_bytes(name).replace(b"/", b"\\").split(b"\\")[-1], HASH_KEY)
            if flags & FILE_FIX_KEY:
                key = ((key + off) ^ fsize) & _M32
        if flags & FILE_SINGLE_UNIT:
            buf = self.data[start:start + csize]
            if flags & FILE_ENCRYPTED:
                buf = decrypt(buf, key)
            if flags & FILE_COMPRESS and csize < fsize:
                buf = _decompress(buf, fsize)
            return buf[:fsize]
        nsec = (fsize + self.sector_size - 1) // self.sector_size
        if not flags & FILE_COMPRESS:
            out = []
            for s in range(nsec):
                seg = self.data[start + s * self.sector_size:start + min(fsize, (s + 1) * self.sector_size)]
                out.append(decrypt(seg, (key + s) & _M32) if flags & FILE_ENCRYPTED else seg)
            return b"".join(out)[:fsize]
        ntab = nsec + 1 + (1 if flags & FILE_SECTOR_CRC else 0)
        tab = self.data[start:start + 4 * ntab]
        if flags & FILE_ENCRYPTED:
            tab = decrypt(tab, (key - 1) & _M32)
        offs = struct.unpack("<%dI" % ntab, tab)
        out = []
        for s in range(nsec):
            seg = self.data[start + offs[s]:start + offs[s + 1]]
            if flags & FILE_ENCRYPTED:
                seg = decrypt(seg, (key + s) & _M32)
            want = min(self.sector_size, fsize - s * self.sector_size)
            out.append(_decompress(seg, want) if len(seg) < want else seg)
        return b"".join(out)[:fsize]

    def listfile(self):
        """Names from the archive's own (listfile), if it has one."""
        try:
            raw = self.read("(listfile)")
        except (KeyError, Unsupported, zlib.error, OSError, ValueError, EOFError, struct.error, IndexError):
            return []
        names = []
        # surrogateescape keeps names that are not UTF-8 (older maps use the system code page) hashable
        for line in raw.decode("utf-8", "surrogateescape").replace("\r", "\n").split("\n"):
            line = line.strip().split(";")[0]
            if line:
                names.append(line)
        return names


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["list", "extract"])
    ap.add_argument("archive")
    ap.add_argument("names", nargs="*")
    ap.add_argument("--out", default=".")
    a = ap.parse_args(argv)
    with open(a.archive, "rb") as f:
        m = MPQ(f.read())
    if a.cmd == "list":
        for n in m.listfile():
            print(display_name(n))
        return
    for n in a.names:
        dst = os.path.abspath(os.path.join(a.out, display_name(n).replace("\\", "/")))
        if not dst.startswith(os.path.abspath(a.out) + os.sep):
            print("SKIP", n, "(path leaves the output folder)")
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "wb") as g:
            g.write(m.read(n))
        print("wrote", dst)


if __name__ == "__main__":
    sys.exit(main())
