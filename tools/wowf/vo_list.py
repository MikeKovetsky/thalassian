#!/usr/bin/env python3
"""List voice-over files of a race or NPC voice set, with the sound kits and
NPC sound slots that use them, so someone can listen and transcribe.

  python3 -I tools/wowf/vo_list.py --base .wowf-extract \
      --path-regex 'sound/character/skyborne|sound/creature/(7478487|7478494)/' \
      --out .wowf-extract/skyborne_vo_files.csv

Inputs are the dumps written by export_all.py (files_in_build.csv,
SoundKitEntry.csv, db2/NPCSounds.csv, db2/CreatureSoundData.csv). The
"category" column is the emote or slot taken from the file name (hello, bye,
thank, greetings, farewell...), which is what the line means in game.
"""
import argparse
import csv
import os
import re
from collections import defaultdict

csv.field_size_limit(1 << 30)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", required=True)
    ap.add_argument("--path-regex", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    rx = re.compile(a.path_regex, re.I)
    files = {}
    with open(os.path.join(a.base, "files_in_build.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if rx.search(r["path"]):
                files[int(r["fdid"])] = r
    kits = defaultdict(set)
    with open(os.path.join(a.base, "SoundKitEntry.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            fd = int(r["FileDataID"] or 0)
            if fd in files:
                kits[fd].add(int(r["SoundKitID"]))
    slots = defaultdict(set)
    for table in ("NPCSounds", "CreatureSoundData"):
        p = os.path.join(a.base, "db2", table + ".csv")
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                for col, v in r.items():
                    if col.startswith("_") or col == "ID" or not v or not v.lstrip("-").isdigit():
                        continue
                    slots[int(v)].add("%s#%s.%s" % (table, r["_id"], col))
    rows = []
    for fd, r in sorted(files.items()):
        name = os.path.basename(r["path"])
        m = re.match(r"(?:vo_[a-z_]+?_(?:male|female)_|\d+_)([a-z0-9_]+?)(?:_\d+)?\.ogg$", name)
        cat = m.group(1) if m else ""
        ks = sorted(kits.get(fd, ()))
        used = sorted(set().union(*[slots.get(k, set()) for k in ks])) if ks else []
        rows.append({"fdid": fd, "path": r["path"], "category": cat, "present_locally": r["present_locally"],
                     "soundkits": " ".join(map(str, ks)), "used_by": " ".join(used[:6])})
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["fdid"])
        w.writeheader()
        w.writerows(rows)
    print("files", len(rows), "with soundkit", sum(1 for r in rows if r["soundkits"]))


if __name__ == "__main__":
    main()
