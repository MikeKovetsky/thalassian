#!/usr/bin/env python3
"""Pull the text out of the client's WDB caches (Cache/WDB/<locale>/*.wdb).

WDB files are what the server sent the client about creatures, quests, game
objects and book pages the player actually met. Layout: a 24-byte header
(magic, build, locale, record size, version, unk) then records of
(uint32 id, uint32 size, data). Field layouts change every build, so this
reader does not decode fields; it lists the readable UTF-8 strings of each
record in order, which is what a text corpus needs.

  python3 wdb.py --out wdb.jsonl creaturecache.wdb questcache.wdb ...
"""
import argparse
import json
import os
import re
import struct

STR_RE = re.compile(rb"[\x20-\x7e\x80-\xff\r\n\t]{3,}")


def read_wdb(path):
    with open(path, "rb") as f:
        d = f.read()
    magic = d[:4][::-1].decode("ascii", "replace")
    build = struct.unpack_from("<I", d, 4)[0]
    pos = 24
    out = []
    while pos + 8 <= len(d):
        rid, size = struct.unpack_from("<II", d, pos)
        if rid == 0 and size == 0:
            break
        data = d[pos + 8:pos + 8 + size]
        pos += 8 + size
        strings = []
        for m in STR_RE.finditer(data):
            raw = m.group(0)
            try:
                s = raw.decode("utf-8")
            except UnicodeDecodeError:
                continue
            s = s.strip()
            # a bitpacked length byte can sit right before a string and look like a letter
            if sum(c.isalpha() for c in s) >= 2:
                strings.append(s)
        out.append({"id": rid, "size": size, "strings": strings})
    return magic, build, out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("files", nargs="+")
    a = ap.parse_args(argv)
    n = 0
    with open(a.out, "w", encoding="utf-8") as f:
        for p in a.files:
            magic, build, recs = read_wdb(p)
            name = os.path.splitext(os.path.basename(p))[0]
            for r in recs:
                r = dict(cache=name, magic=magic, build=build, **r)
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
                n += 1
            print(name, magic, build, len(recs), "records")
    print("wrote", n, "records to", a.out)


if __name__ == "__main__":
    main()
