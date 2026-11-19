"""Apply 9-, 10- and 11-candidates.json (reports 9 to 11: Warcraft III's game files, Midnight's text on the wiki, and
the voice of Warcraft III's new campaign) to the lexicon.

Runs after apply_audit.py, with the same policy: high and medium confidence only; everything else is listed in the
log. The files are applied in that order, each on the lexicon the one before it left. The actions:
- fix: sets a field only while its "old" value still matches, and merges the fix's evidence into the entry
  (apply_localization.apply_fixes). In each file the fixes of "evidence" go first, because another fix of the same
  entry merges its own evidence and would leave them stale.
- add: appends the entry when no entry has the same word and source. Its fields must fit the canon_basis table of
  docs/methodology/lexicon.md: a canon entry is attested, segment, epithet or name, any other is name, inferred or
  unverified, and it has both glosses, a method and evidence with a quote and a place. An add that does not fit is
  refused, so the candidate is fixed in its file and not here.
- note: changes nothing and is listed.
Any other action is refused, before anything changes. Appends one section per file to merge-log.md; a file whose
section is there already is skipped, so running the script again changes nothing. From the repo root:
  python3 research/2026-11-revival/scripts/apply_wc3_midnight.py
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import merge_candidates  # noqa: E402
from apply_audit import label  # noqa: E402
from apply_localization import apply_fixes  # noqa: E402
from apply_voice import ENTRY_FIELDS  # noqa: E402
from merge_candidates import APPLY, key  # noqa: E402

LEX, LOG, RES = merge_candidates.LEX, merge_candidates.LOG, merge_candidates.RES
# (file number, section title, report)
FILES = (("9", "Warcraft III game files", "9-warcraft-iii.md"),
         ("10", "Midnight's text on the wiki", "10-midnight-wiki.md"),
         ("11", "Forsaken Kingdom voice", "11-forsaken-kingdom-voice.md"))
ACTIONS = ("fix", "add", "note")
CANON_BASES = ("attested", "segment", "epithet", "name")
NON_CANON_BASES = ("name", "inferred", "unverified")
SECTIONS = (("added", "Added"), ("fixed", "Fixes applied"), ("noted", "Noted, no change"),
            ("stale", "Stale (the entry or its old value no longer matches, or the word and source exist)"),
            ("held", "Held back (low confidence)"))


def mark(number, title):
    return f"## {title} ({number}-candidates.json)"


def gist(c):
    """For the log, the first sentence of why a fix is proposed, or of what an add or a note says."""
    first, second = ("reason", "notes") if c["action"] == "fix" else ("notes", "reason")
    text = (c.get(first) or c.get(second) or "").strip()
    return re.split(r"(?<=\.)\s", text, maxsplit=1)[0]


def check_add(c):
    """Refuse an add whose fields do not fit docs/methodology/lexicon.md, section 3."""
    problems = [f"no {k}" for k in ENTRY_FIELDS if k not in c]
    if not problems:
        allowed = CANON_BASES if c["canon"] else NON_CANON_BASES
        if c["canon_basis"] not in allowed:
            problems.append(f"canon {c['canon']} with canon_basis {c['canon_basis']!r} (allowed: {', '.join(allowed)})")
        if not (c["translation"] or {}).get("en") or not (c["translation"] or {}).get("uk"):
            problems.append("an English or Ukrainian gloss is missing")
        if not c["method"]:
            problems.append("no method")
        if not c["evidence"] or not all(ev.get("quote") and ev.get("where") for ev in c["evidence"]):
            problems.append("no evidence, or evidence without a quote and a place")
    if problems:
        raise ValueError(f"{c['word']}: apply_wc3_midnight.py refuses this add: {'; '.join(problems)}")


def apply_report(lexicon, candidates):
    """Apply one candidates file to the lexicon in place; return the log rows by section. Raises before changing
    anything if an action is unknown or an add does not fit the lexicon's fields."""
    unknown = [c for c in candidates if c["action"] not in ACTIONS]
    if unknown:
        raise ValueError(f"{unknown[0]['word']}: apply_wc3_midnight.py does not know the action "
                         f"{unknown[0]['action']!r}")
    for c in candidates:
        if c["action"] == "add" and c["confidence"] in APPLY:
            check_add(c)
    log = {name: [] for name, _ in SECTIONS}

    fixes = sorted((c for c in candidates if c["action"] == "fix" and c["confidence"] in APPLY),
                   key=lambda c: c["field"] != "evidence")
    log["fixed"], log["stale"], _ = apply_fixes(lexicon, fixes)

    for c in candidates:
        if c["confidence"] not in APPLY:
            log["held"].append(f"{label(c)}: {gist(c)}")
        elif c["action"] == "note":
            log["noted"].append(f"{label(c)}: {gist(c)}")
        elif c["action"] == "fix":
            continue
        elif any(key(e["word"]) == key(c["word"]) and e.get("source") == c["source"] for e in lexicon):
            log["stale"].append(f"{label(c)}: an entry with the same word and source exists")
        else:
            lexicon.append({k: c[k] for k in ENTRY_FIELDS})
            log["added"].append(f"{c['word']} [{c['source']}, {c['confidence']}, {c['canon_basis']}]: "
                                f"{c['translation']['en']}")
    return log


def main():
    with open(LEX, encoding="utf-8") as fh:
        lexicon = json.load(fh)
    with open(LOG, encoding="utf-8") as fh:
        done = fh.read()

    sections = []
    for number, title, report in FILES:
        if mark(number, title) in done:
            print(f"{number}-candidates.json is already applied (see merge-log.md); skipped.")
            continue
        with open(os.path.join(RES, f"{number}-candidates.json"), encoding="utf-8") as fh:
            candidates = json.load(fh)
        log = apply_report(lexicon, candidates)
        sections.append((number, title, report, log, len(lexicon)))
        print(f"{number}: " + ", ".join(f"{name} {len(rows)}" for name, rows in log.items()), "| total", len(lexicon))
        for r in log["stale"]:
            print("  stale:", r)
    if not sections:
        sys.exit("9-, 10- and 11-candidates.json are already applied (see merge-log.md); nothing to do.")

    with open(LEX, "w", encoding="utf-8") as fh:
        json.dump(lexicon, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    with open(LOG, "a", encoding="utf-8") as fh:
        for number, title, report, log, total in sections:
            fh.write(f"\n{mark(number, title)}\n\nGenerated by `scripts/apply_wc3_midnight.py`; see "
                     f"[report {number}]({report}). Result: {total} entries.\n\n")
            for name, heading in SECTIONS:
                rows = log[name]
                fh.write(f"### {heading} ({len(rows)})\n\n")
                fh.writelines(f"{i}. {r}\n" for i, r in enumerate(rows, 1))
                fh.write("\n")


if __name__ == "__main__":
    main()
