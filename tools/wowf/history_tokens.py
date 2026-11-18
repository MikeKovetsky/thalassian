#!/usr/bin/env python3
"""Elvish-looking tokens in the project's own past (every blob in git history)
that are not entries in the current lexicon.json.

  python3 -I tools/wowf/history_tokens.py --repo . --out .wowf-extract/analysis/history_tokens.csv

A token is collected when it
  * has an inner apostrophe (Sin'dorei, Bal'a) and is not an English
    contraction or possessive, or
  * sits inside an Elvish phrase: a quoted/backticked/italic span in which at
    least one token is a current lexicon word or an apostrophe form.
For each token the first commit and file where it appears and a context line
are kept, plus whether the lexicon has it whole, has all its apostrophe parts,
or lacks it.
"""
import argparse
import csv
import json
import os
import re
import subprocess

APOS = "'’"
TOKEN = re.compile(r"[A-Za-zÀ-ÿ]+(?:['’][A-Za-zÀ-ÿ]+)*")
SPAN = re.compile(r"[\"“*`_]([^\"”*`_\n]{2,120})[\"”*`_]")
CONTRACTIONS = re.compile(r"^[a-z]+['’](s|t|ll|re|ve|d|m)$", re.I)
ENGLISH_APOS = {"o'clock", "ma'am", "y'all", "rock'n'roll", "n't"}


def git(repo, *args):
    return subprocess.run(["git", "-C", repo] + list(args), capture_output=True, text=True,
                          errors="replace").stdout


def norm(t):
    return t.replace("’", "'").lower()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--lexicon", default="src/thalassian/data/lexicon.json")
    ap.add_argument("--out", required=True)
    ap.add_argument("--words", default="/usr/share/dict/words")
    a = ap.parse_args(argv)
    lex = json.load(open(os.path.join(a.repo, a.lexicon), encoding="utf-8"))
    lexwords = {norm(e["word"]) for e in lex}
    lexroots = {norm(e.get("root") or "") for e in lex}
    english = set()
    if os.path.exists(a.words):
        english = {w.strip().lower() for w in open(a.words, encoding="utf-8", errors="replace")}

    # every commit, oldest first, so the first sighting is the origin
    commits = git(a.repo, "rev-list", "--all", "--reverse").split()
    seen_blobs = set()
    found = {}
    for c in commits:
        for line in git(a.repo, "ls-tree", "-r", c).splitlines():
            meta, path = line.split("\t", 1)
            _mode, typ, blob = meta.split()
            if typ != "blob" or blob in seen_blobs:
                continue
            seen_blobs.add(blob)
            if not re.search(r"\.(md|json|py|html|txt|js|toml|yml|yaml|cfg)$", path):
                continue
            text = git(a.repo, "cat-file", "-p", blob)
            for ln in text.splitlines():
                cands = []
                for m in TOKEN.finditer(ln):
                    t = m.group(0)
                    if any(x in t for x in APOS) and not CONTRACTIONS.match(t) and norm(t) not in ENGLISH_APOS:
                        cands.append((t, "apostrophe"))
                for sm in SPAN.finditer(ln):
                    toks = TOKEN.findall(sm.group(1))
                    if any(norm(t) in lexwords or any(x in t for x in APOS) for t in toks):
                        for t in toks:
                            if len(t) > 1 and not CONTRACTIONS.match(t):
                                cands.append((t, "phrase"))
                for t, why in cands:
                    k = norm(t)
                    if k in found:
                        found[k]["hits"] += 1
                        continue
                    found[k] = dict(token=t, why=why, first_commit=c[:7], path=path,
                                    context=ln.strip()[:240], hits=1)
    rows = []
    for k, r in found.items():
        parts = [p for p in k.split("'") if p]
        if k in lexwords:
            status = "in_lexicon"
        elif parts and all(p in lexwords or p in lexroots for p in parts):
            status = "parts_in_lexicon"
        elif r["why"] == "phrase" and k in english:
            continue  # English word that happened to sit in a quoted span
        else:
            status = "absent"
        r["status"] = status
        rows.append(r)
    rows.sort(key=lambda r: (r["status"], r["token"].lower()))
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["token", "status", "why", "hits", "first_commit", "path", "context"])
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    print(Counter(r["status"] for r in rows), "blobs", len(seen_blobs))


if __name__ == "__main__":
    main()
