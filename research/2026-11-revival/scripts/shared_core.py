"""Find the word parts that several elven branches share (report 7).

From the repo root:
  python3 research/2026-11-revival/scripts/shared_core.py <forms.json> [<forms.json> ...] [--out core.json]

Each forms file is a JSON array of objects with at least "form" and "branch". The lexicon's own Thalassian,
Darnassian, Shalassian and Skyborne entries are added under those branches (invented and unverified entries
are left out). Scrambler words carry no meaning and are skipped.

A form is split into parts at spaces, apostrophes and hyphens. A part is attested in a branch when some form of
that branch has it as a whole part ("exact"), or when a longer part of that branch is it plus another known part
("inside": kaldorei is kal + dorei). Parts shorter than three letters are left out, because they match by chance.
A phrase found word for word in several daughter branches is one quotation, not several witnesses: it counts only
for the first of them in the order below (Thalyssra's "Tor ilisar'thera'nal" is Darnassian, not Shalassian). A
one-word form such as "alah" is never a quotation: the same word in two branches is what the core looks for.

The five daughter branches are Darnassian, Thalassian, Shalassian, Skyborne and Nazja. Names and speech from before
the Sundering are a sixth witness, "ancient". Any other branch (Titan, Zandali) is a control: it shows how often
unrelated words match by chance.
"""
import json
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from merge_candidates import LEX  # noqa: E402

DAUGHTERS = ("darnassian", "thalassian", "shalassian", "skyborne", "nazja")
ANCIENT = {"ancient-name": "ancient", "ancient-speech": "ancient"}
MIN_PART = 3


def text(form):
    """The form's letters only, for spotting the same phrase twice:
    "Tor ilisar'thera'nal!" -> "tor ilisar thera nal"."""
    return " ".join(re.findall(r"[a-z]+", form.lower()))


def parts(form):
    """The words of text() that are MIN_PART letters or longer: "Ba'anthalso-dorei!" -> ["anthalso", "dorei"]."""
    return [p for p in text(form).split() if len(p) >= MIN_PART]


def lexicon_forms(path=LEX):
    with open(path, encoding="utf-8") as fh:
        lexicon = json.load(fh)
    return [{"form": e["word"], "branch": e["source"], "gloss": e["translation"]["en"], "origin": "lexicon"}
            for e in lexicon
            if e.get("source") in DAUGHTERS and e.get("canon_basis") not in ("generated", "unverified")]


def without_quotations(forms):
    """Drop a daughter-branch phrase whose text an earlier daughter branch (in DAUGHTERS order) already has. One-word
    forms are kept: Thalassian alah "light" is not a quotation of Darnassian alah "to you"."""
    def quotable(f):
        return f["branch"] in DAUGHTERS and " " in text(f["form"])

    first = {}
    for f in forms:
        if quotable(f):
            t = text(f["form"])
            if t not in first or DAUGHTERS.index(f["branch"]) < DAUGHTERS.index(first[t]):
                first[t] = f["branch"]
    return [f for f in forms if not quotable(f) or first[text(f["form"])] == f["branch"]]


def witnesses(forms):
    """part -> branch -> {"exact": {forms}, "inside": {forms}}: sets of the forms that show the part."""
    whole = defaultdict(lambda: defaultdict(set))  # part -> branch -> forms having it as a whole part
    for f in without_quotations(forms):
        for p in parts(f["form"]):
            whole[p][ANCIENT.get(f["branch"], f["branch"])].add(f["form"])
    found = defaultdict(lambda: defaultdict(lambda: {"exact": set(), "inside": set()}))
    for part, branches in whole.items():
        for branch, fs in branches.items():
            found[part][branch]["exact"] |= fs
    # A compound written solid counts for both halves when both are known parts: kaldorei = kal + dorei.
    for longer, branches in whole.items():
        for i in range(MIN_PART, len(longer) - MIN_PART + 1):
            head, tail = longer[:i], longer[i:]
            if head in whole and tail in whole:
                for branch, fs in branches.items():
                    found[head][branch]["inside"] |= fs
                    found[tail][branch]["inside"] |= fs
    return found


def tier(branches):
    """1: before the Sundering and in two daughters or more. 2: three daughters or more. 3: before the Sundering,
    with one daughter or none. None: anything else."""
    daughters = sum(b in DAUGHTERS for b in branches)
    if "ancient" in branches:
        return 1 if daughters >= 2 else 3
    return 2 if daughters >= 3 else None


def core(forms):
    rows = []
    for part, by in witnesses(forms).items():
        elven = {b: v for b, v in by.items() if b in DAUGHTERS or b == "ancient"}
        t = tier(elven)
        if t is None:
            continue
        rows.append({
            "part": part, "tier": t,
            "branches": {b: {"exact": sorted(v["exact"]), "inside": sorted(v["inside"])} for b, v in sorted(elven.items())},
            "controls": sorted(b for b in by if b not in elven),
        })
    return sorted(rows, key=lambda r: (r["tier"], -len(r["branches"]), r["part"]))


def shared_rate(forms, branch):
    """The share of a branch's parts that two daughter branches or more (other than itself) also have. For a
    control (Titan, Zandali) this is the noise floor of the matching; for a daughter it is the signal."""
    found = witnesses(forms)
    own = [p for p, by in found.items() if branch in by]
    hits = sorted(p for p in own if sum(b in DAUGHTERS and b != branch for b in found[p]) >= 2)
    return hits, len(own)


def main(argv):
    out = None
    if "--out" in argv:
        i = argv.index("--out")
        out = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    forms = lexicon_forms()
    for path in argv:
        with open(path, encoding="utf-8") as fh:
            forms += [f for f in json.load(fh) if f.get("kind") != "scrambler"]
    rows = core(forms)
    counts = defaultdict(int)
    for f in forms:
        counts[ANCIENT.get(f["branch"], f["branch"])] += 1
    print("forms per branch:", dict(sorted(counts.items())))
    for t in (1, 2, 3):
        sel = [r for r in rows if r["tier"] == t]
        print(f"tier {t}: {len(sel)}")
        for r in sel:
            print("  ", r["part"], "|", ", ".join(f"{b}:{len(v['exact'])}+{len(v['inside'])}" for b, v in r["branches"].items()),
                  "| controls:", ",".join(r["controls"]) or "-")
    for branch in sorted({ANCIENT.get(f["branch"], f["branch"]) for f in forms}):
        hits, total = shared_rate(forms, branch)
        kind = "daughter" if branch in DAUGHTERS else "witness" if branch == "ancient" else "control"
        print(f"{kind} {branch}: {len(hits)} of {total} parts ({len(hits) / max(total, 1):.0%}) are shared with two "
              f"other daughters or more{': ' + ', '.join(hits) if kind != 'daughter' else ''}")
    if out:
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, ensure_ascii=False, indent=1)
            fh.write("\n")


if __name__ == "__main__":
    main(sys.argv[1:])
