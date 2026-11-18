"""Apply 4-candidates.json (Blizzard localization mining) to the merged lexicon.

Runs after merge_candidates.py, on the lexicon that merge produced. Same policy: high and medium
confidence only, and a fix applies only while its "old" value still matches; anything else is logged.
Appends a section to merge-log.md. From the repo root:
  python3 research/2026-11-revival/scripts/apply_localization.py
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
LEX = os.path.join(ROOT, "src", "thalassian", "data", "lexicon.json")
RES = os.path.join(ROOT, "research", "2026-11-revival")
APPLY = {"high", "medium"}
MARK = "## Localization mining (4-candidates.json)"
# The full review (commit 0bbb47b) already rewrote these notes to drop "great people", so the
# files' "old" values no longer match. The localization notes keep that wording and add the
# 12.0.7 source and the zhTW/koKR renderings, so they are applied over the reviewed text.
SUPERSEDES_REVIEWED_NOTES = {"anore", "selama"}


def main():
    with open(LEX, encoding="utf-8") as fh:
        lexicon = json.load(fh)
    with open(os.path.join(RES, "4-candidates.json"), encoding="utf-8") as fh:
        candidates = json.load(fh)
    log_path = os.path.join(RES, "merge-log.md")
    with open(log_path, encoding="utf-8") as fh:
        log_text = fh.read()
    if MARK in log_text:
        raise SystemExit("4-candidates.json is already applied (see merge-log.md); nothing to do.")

    applied, stale, held = [], [], []
    for c in candidates:
        label = f"{c['action']} {c['word']}{'.' + c['field'] if c.get('field') else ''} ({c['confidence']})"
        if c["confidence"] not in APPLY or c["action"] != "fix":
            held.append(label)
            continue
        hits = [e for e in lexicon if e["word"].lower() == c["word"].lower()]
        if len(hits) == 1 and hits[0].get(c["field"]) == c["new"]:
            applied.append(label + ": already current")
            continue
        superseding = c.get("field") == "notes" and c["word"].lower() in SUPERSEDES_REVIEWED_NOTES
        if len(hits) != 1 or (hits[0].get(c["field"]) != c.get("old") and not superseding):
            stale.append(label)
            continue
        if superseding and hits[0].get(c["field"]) != c.get("old"):
            label += ": applied over the reviewed notes (see SUPERSEDES_REVIEWED_NOTES)"
        hits[0][c["field"]] = c["new"]
        applied.append(label)

    with open(LEX, "w", encoding="utf-8") as fh:
        json.dump(lexicon, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(f"\n{MARK}\n\n")
        for title, rows in (("Applied", applied), ("Stale (old value no longer matches)", stale),
                            ("Held back (low confidence or not a fix)", held)):
            fh.write(f"### {title} ({len(rows)})\n\n")
            fh.writelines(f"{i}. {r}\n" for i, r in enumerate(rows, 1))
            fh.write("\n")
    print(f"applied {len(applied)}, stale {len(stale)}, held {len(held)}")
    for r in stale:
        print("  stale:", r)


if __name__ == "__main__":
    main()
