#!/usr/bin/env python3
"""Read-only access to a local Warcraft III (Reforged, product "w3") CASC storage.

Standard library only and Python 3.9 compatible. It reuses tools/wowf/casc.py for
.build.info, the build config, the local v7 indices, the encoding file and BLTE,
and adds what Warcraft III does differently: its root file is plain text, one
"path|content key|tag|tag" line per file, with paths such as
"War3.w3mod:_Locales/enUS.w3mod:Units/HumanUnitStrings.txt". The ":" marks a
nested .w3mod package; this reader keeps the full path and only maps ":" to "/"
when it writes a file.

It never writes inside the install directory and never starts the game.

Usage:
  python3 w3casc.py info  --install "/Applications/Warcraft III"
  python3 w3casc.py files --install ... --out .wc3-extract/filelist.tsv
  python3 w3casc.py extract --install ... --match '\\.(txt|fdf)$' --out .wc3-extract/casc
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "wowf"))
import casc  # noqa: E402  (tools/wowf/casc.py, unchanged)

PRODUCT = "w3"


class RootEntry(object):
    __slots__ = ("path", "ckey", "tags")

    def __init__(self, path, ckey, tags):
        self.path = path
        self.ckey = ckey
        self.tags = tags

    @property
    def locale(self):
        """The locale of a localized file (from its _Locales/xxXX.w3mod folder), else ''."""
        m = re.search(r"_Locales[/\\]([a-zA-Z]{4})\.w3mod:", self.path)
        return m.group(1) if m else ""


def parse_text_root(data):
    """Parse the Warcraft III text root: one 'path|ckey|tag|tag' line per file."""
    out = []
    for raw in data.decode("utf-8", "replace").splitlines():
        parts = raw.split("|")
        if len(parts) < 2 or not re.fullmatch(r"[0-9a-fA-F]{32}", parts[1] or ""):
            continue
        out.append(RootEntry(parts[0], bytes.fromhex(parts[1]), [t for t in parts[2:] if t]))
    return out


class W3Storage(object):
    def __init__(self, install, product=PRODUCT):
        self.casc = casc.CASC(install, product)
        self.build_name = self.casc.build_config.get("build-name", "")
        root_ckey = bytes.fromhex(self.casc.build_config["root"].split()[0])
        data = self.casc.read_ckey(root_ckey)
        if data is None:
            raise SystemExit("root file not found in the local storage")
        self.entries = parse_text_root(data)

    def lookup(self, entry):
        """(decoded size, present locally) for a root entry; size -1 if unknown."""
        r = self.casc.ckey_to_ekeys(entry.ckey)
        if not r:
            return -1, False
        return r[0], any(self.casc.has_ekey(e) for e in r[1])

    def read(self, entry):
        return self.casc.read_ckey(entry.ckey)


def out_name(path):
    """A relative output path for a root path: ':' and '\\' become '/'."""
    return path.replace("\\", "/").replace(":", "/")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["info", "files", "extract"])
    ap.add_argument("--install", default="/Applications/Warcraft III")
    ap.add_argument("--out")
    ap.add_argument("--match", help="regular expression (case-insensitive) on the root path")
    ap.add_argument("--locales", default="enUS",
                    help="comma list of locales to keep for localized files (default enUS); 'all' keeps every one")
    a = ap.parse_args(argv)
    st = W3Storage(a.install)
    if a.cmd == "info":
        print("product", st.casc.info.get("Product"), "version", st.casc.info.get("Version"),
              "build", st.build_name)
        print("root entries", len(st.entries))
        return
    if a.cmd == "files":
        n = present = 0
        with open(a.out, "w", encoding="utf-8") as f:
            f.write("path\tckey\ttags\tlocale\tsize\tlocal\n")
            for e in st.entries:
                size, local = st.lookup(e)
                n += 1
                present += local
                f.write("%s\t%s\t%s\t%s\t%d\t%d\n" % (e.path, e.ckey.hex(), ",".join(e.tags), e.locale,
                                                       size, int(local)))
        print("wrote", n, "root entries,", present, "present locally, to", a.out)
        return
    if a.cmd == "extract":
        rx = re.compile(a.match, re.I) if a.match else None
        keep = None if a.locales == "all" else set(a.locales.split(","))
        ok = skipped = 0
        for e in st.entries:
            if rx and not rx.search(e.path):
                continue
            if keep is not None and e.locale and e.locale not in keep:
                continue
            why = casc.extract_file(st.casc, e.ckey, a.out, out_name(e.path))
            if why:
                skipped += 1
                print("SKIP", e.path, "(%s)" % why)
            else:
                ok += 1
        print("extracted", ok, "skipped", skipped)


if __name__ == "__main__":
    main()
