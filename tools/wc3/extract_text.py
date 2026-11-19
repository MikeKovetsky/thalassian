#!/usr/bin/env python3
"""Extract every text source of a local Warcraft III install into a local folder.

Read-only: it opens the CASC storage with w3casc.py and the maps with mpq.py, and
writes only under --out (the gitignored .wc3-extract/ folder by default). It never
writes inside the install and never starts the game. Standard library only,
Python 3.9 compatible.

Writes:
  filelist.tsv                 every root entry: path, content key, tags, locale, size, present locally
  casc/<path>                  text files from the storage (string tables, .fdf, .slk, subtitles,
                               credits, json ...), enUS plus unlocalized
  facefx/<path>.names.txt      the names inside FaceFX lip-sync files (speaker and line IDs)
  maps/<map path>/<member>     text members of every .w3m/.w3x map: war3map.wts, war3map.j,
                               war3map.lua, war3campaign.wts, *.txt, and the readable strings of
                               the binary object files (<member>.strings.txt)
  maps_index.tsv               per map: status (ok, encrypted, error), members found, members written
  summary.json                 counts

Usage:
  python3 tools/wc3/extract_text.py --install "/Applications/Warcraft III" --out .wc3-extract
"""
import argparse
import json
import os
import re
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w3casc  # noqa: E402
import mpq  # noqa: E402

TEXT_EXT = {"txt", "fdf", "slk", "srt", "json", "j", "lua", "pld", "wai", "ini", "html", "wts", "toc", "xml",
            "csv", "lnk"}
FACEFX_EXT = {"animset_ingame", "facefx_ingame"}
MAP_EXT = {"w3m", "w3x", "w3n"}
# map members that are text
MAP_TEXT = ["war3map.wts", "war3map.j", "scripts\\war3map.j", "war3map.lua", "war3campaign.wts",
            "war3mapSkin.txt", "war3mapMisc.txt", "war3mapExtra.txt", "war3campaignSkin.txt",
            "war3campaignMisc.txt", "war3mapUnits.doo"]
# binary members whose readable strings can hold names and tooltips written inline
MAP_BINARY = ["war3map.w3i", "war3map.w3u", "war3map.w3t", "war3map.w3a", "war3map.w3b", "war3map.w3d",
              "war3map.w3h", "war3map.w3q", "war3map.wtg", "war3map.wct", "war3map.imp",
              "war3campaign.w3u", "war3campaign.w3t", "war3campaign.w3a", "war3campaign.w3b",
              "war3campaign.w3d", "war3campaign.w3h", "war3campaign.w3q", "war3campaign.w3f"]
PRINTABLE = re.compile(rb"[\x20-\x7e\t\r\n\x80-\xff]{4,}")


def ext_of(path):
    base = path.replace("\\", "/").rsplit("/", 1)[-1]
    return base.rsplit(".", 1)[-1].lower() if "." in base else ""


def readable_strings(data, minlen=4):
    out = []
    for m in PRINTABLE.finditer(data):
        s = m.group(0).decode("utf-8", "replace").strip()
        if len(s) >= minlen and s.count("�") * 4 < len(s):
            out.append(s)
    return out


def write(out_root, rel, data):
    dst = os.path.abspath(os.path.join(out_root, rel))
    if not dst.startswith(os.path.abspath(out_root) + os.sep):
        return False
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "wb") as g:
        g.write(data)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--install", default="/Applications/Warcraft III")
    ap.add_argument("--out", default=".wc3-extract")
    ap.add_argument("--locales", default="enUS")
    a = ap.parse_args(argv)
    keep = set(a.locales.split(","))
    st = w3casc.W3Storage(a.install)
    os.makedirs(a.out, exist_ok=True)
    counts = {"build": st.build_name, "root_entries": len(st.entries), "present_locally": 0,
              "text_files": 0, "text_bytes": 0, "facefx_files": 0, "maps": 0, "maps_ok": 0,
              "maps_encrypted": 0, "maps_error": 0, "map_members_written": 0, "skipped_not_local": 0,
              "skipped_other_locale": 0}
    idx_rows = []
    with open(os.path.join(a.out, "filelist.tsv"), "w", encoding="utf-8") as fl:
        fl.write("path\tckey\ttags\tlocale\tsize\tlocal\n")
        for e in st.entries:
            size, local = st.lookup(e)
            counts["present_locally"] += int(local)
            fl.write("%s\t%s\t%s\t%s\t%d\t%d\n" % (e.path, e.ckey.hex(), ",".join(e.tags), e.locale, size,
                                                   int(local)))
            ext = ext_of(e.path)
            is_map = ext in MAP_EXT or ext == "w3xd"
            if ext not in TEXT_EXT and ext not in FACEFX_EXT and not is_map:
                continue
            if e.locale and e.locale not in keep:
                counts["skipped_other_locale"] += 1
                continue
            if not local:
                counts["skipped_not_local"] += 1
                continue
            data = st.read(e)
            if data is None:
                counts["skipped_not_local"] += 1
                continue
            rel = w3casc.out_name(e.path)
            if ext in TEXT_EXT:
                if write(os.path.join(a.out, "casc"), rel, data):
                    counts["text_files"] += 1
                    counts["text_bytes"] += len(data)
            elif ext in FACEFX_EXT:
                names = sorted(set(s for s in readable_strings(data, 3) if not s.startswith("Fx")))
                if write(os.path.join(a.out, "facefx"), rel + ".names.txt", ("\n".join(names) + "\n").encode()):
                    counts["facefx_files"] += 1
            else:
                counts["maps"] += 1
                status, found, written = extract_map(data, os.path.join(a.out, "maps", rel))
                counts["maps_" + status] += 1
                counts["map_members_written"] += written
                idx_rows.append((e.path, status, len(data), found, written))
    with open(os.path.join(a.out, "maps_index.tsv"), "w", encoding="utf-8") as f:
        f.write("map\tstatus\tbytes\tmembers_found\tmembers_written\n")
        for r in idx_rows:
            f.write("%s\t%s\t%d\t%s\t%d\n" % r)
    with open(os.path.join(a.out, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(counts, f, indent=1)
    print(json.dumps(counts, indent=1))


def extract_map(data, out_dir):
    """Write the text members of one map. Returns (status, members found, members written)."""
    try:
        m = mpq.MPQ(data)
    except ValueError:
        return "encrypted", "", 0
    names = set(m.listfile())
    for n in MAP_TEXT + MAP_BINARY:
        if m.has(n):
            names.add(n)
    found = []
    written = 0
    for n in sorted(names):
        ext = ext_of(n)
        binary = n in MAP_BINARY or ext in ("w3u", "w3t", "w3a", "w3b", "w3d", "w3h", "w3q", "w3i", "wtg",
                                             "wct", "imp", "w3f")
        if not binary and ext not in TEXT_EXT and ext not in ("wts", "doo"):
            continue
        if ext == "doo":
            continue
        try:
            raw = m.read(n)
        except (KeyError, mpq.Unsupported, zlib.error, OSError, ValueError, EOFError) as ex:
            found.append("%s(!%s)" % (n, type(ex).__name__))
            continue
        found.append(n)
        rel = n.replace("\\", "/")
        if binary:
            raw = ("\n".join(readable_strings(raw)) + "\n").encode("utf-8")
            rel += ".strings.txt"
        if write(out_dir, rel, raw):
            written += 1
    return "ok", ",".join(found), written


if __name__ == "__main__":
    main()
