"""Apply 8-candidates.json (report 8, the reconstruction audit) to the lexicon.

Runs after apply_voice.py, with the same policy: high and medium confidence only; everything else is listed in the
log. The actions:
- remove: deletes the entry with that word and source. Only a generated or unverified entry can be removed; a
  removal of anything else is refused.
- fix: sets a field only while its "old" value still matches; a "new" of null deletes the field. The audit's evidence
  is about the old value, so it stays in 8-candidates.json and is not merged into the entry.
- regenerate: gives an existing generated entry that still has the old form its new form. The meaning, part of
  speech and glosses stay; the root becomes the new form, and the source, method, confidence, evidence and notes are
  those of the candidate.
- add: appends the entry when no entry has the same word and source. A canon add is refused.
- note: changes nothing and is listed.
Any other action is refused. Appends a section to merge-log.md. From the repo root:
  python3 research/2026-11-revival/scripts/apply_audit.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_voice import ENTRY_FIELDS  # noqa: E402
from merge_candidates import APPLY, LEX, LOG, RES, key  # noqa: E402

MARK = "## Reconstruction audit (8-candidates.json)"
ORDER = ("remove", "fix", "regenerate", "add", "note")
REMOVABLE = ("generated", "unverified")
SECTIONS = (("removed", "Removed"), ("fixed", "Fixes applied"), ("regenerated", "Regenerated (old -> new)"),
            ("added", "Added"), ("noted", "Noted, no change"),
            ("stale", "Stale (the entry or its old value no longer matches)"), ("held", "Held back (low confidence)"))


def matches(lexicon, c):
    """The entries with the candidate's word, and its source when it names one."""
    return [e for e in lexicon
            if key(e["word"]) == key(c["word"]) and ("source" not in c or e.get("source") == c["source"])]


def change(c):
    """What a fix changed, short enough for the log; 8-candidates.json has both values in full."""
    old, new = c["old"], c["new"]
    if new is None:
        return "deleted"
    if c["field"] == "translation":
        return f"en {old['en']!r} -> {new['en']!r}; uk {old['uk']!r} -> {new['uk']!r}"
    if len(old) + len(new) <= 100:
        return f"{old!r} -> {new!r}"
    return "rewritten (both texts are in 8-candidates.json)"


def label(c):
    field = "." + c["field"] if c["action"] == "fix" else ""
    return f"{c['action']} {c['word']}{field} ({c['confidence']})"


def ordered(entry):
    """The entry with the lexicon's field order; fields outside ENTRY_FIELDS keep their place after them."""
    return {**{k: entry[k] for k in ENTRY_FIELDS if k in entry}, **{k: v for k, v in entry.items()
                                                                     if k not in ENTRY_FIELDS}}


def apply_audit(lexicon, candidates):
    """Apply the candidates to the lexicon in place; return the log rows by section."""
    unknown = [c for c in candidates if c["action"] not in ORDER]
    if unknown:
        raise ValueError(f"{unknown[0]['word']}: apply_audit.py does not know the action {unknown[0]['action']!r}")
    log = {name: [] for name, _ in SECTIONS}
    todo = []
    for c in candidates:
        if c["confidence"] in APPLY:
            todo.append(c)
        else:
            log["held"].append(f"{label(c)}: {c.get('summary') or c['reason']}")
    todo.sort(key=lambda c: ORDER.index(c["action"]))

    for c in todo:
        hits = matches(lexicon, c)
        act = c["action"]
        if act == "remove":
            if len(hits) != 1:
                log["stale"].append(f"{label(c)}: {len(hits)} entries match")
                continue
            if hits[0].get("canon") or hits[0].get("canon_basis") not in REMOVABLE:
                raise ValueError(f"{c['word']}: apply_audit.py removes only generated or unverified entries")
            lexicon.remove(hits[0])
            log["removed"].append(f"{c['word']} [{c['source']}] ({c['confidence']}): {c['summary']}")
        elif act == "fix":
            if len(hits) != 1 or hits[0].get(c["field"]) != c["old"]:
                log["stale"].append(f"{label(c)}: {len(hits)} entries match, or the old value has changed")
                continue
            if c["new"] is None:
                del hits[0][c["field"]]
            else:
                hits[0][c["field"]] = c["new"]
            log["fixed"].append(f"{c['word']}.{c['field']} ({c['confidence']}): {change(c)}")
        elif act == "regenerate":
            taken = [e for e in lexicon if key(e["word"]) == key(c["new"]) and e.get("source") == "generated"]
            if len(hits) != 1 or hits[0].get("canon_basis") != "generated" or taken:
                log["stale"].append(f"{label(c)}: no single generated entry with the old form, or the new form "
                                    "is taken")
                continue
            entry = hits[0]
            entry.update(word=c["new"], root=c["new"], source="generated", canon=False, canon_basis="generated",
                         notes=c["notes"], confidence=c["confidence"], method=c["method"], evidence=c["evidence"])
            lexicon[lexicon.index(entry)] = ordered(entry)
            log["regenerated"].append(f"{c['word']} -> {c['new']} ({c['confidence']}): "
                                      f"{entry['translation']['en']}; {c['summary']}")
        elif act == "add":
            if c.get("canon"):
                raise ValueError(f"{c['word']}: an audit add is never canon")
            if any(e.get("source") == c["source"] for e in hits):
                log["stale"].append(f"{label(c)}: an entry with the same word and source exists")
                continue
            lexicon.append({k: c[k] for k in ENTRY_FIELDS})
            item = f", Swadesh-207 item {c['swadesh']}" if c.get("swadesh") else ""
            log["added"].append(f"{c['word']} ({c['confidence']}): {c['translation']['en']}{item}")
        else:
            log["noted"].append(f"{c['word']} ({c['confidence']}): {c['reason']}")
    return log


def main():
    with open(LEX, encoding="utf-8") as fh:
        lexicon = json.load(fh)
    with open(os.path.join(RES, "8-candidates.json"), encoding="utf-8") as fh:
        candidates = json.load(fh)
    with open(LOG, encoding="utf-8") as fh:
        if MARK in fh.read():
            sys.exit("8-candidates.json is already applied (see merge-log.md); nothing to do.")

    log = apply_audit(lexicon, candidates)

    with open(LEX, "w", encoding="utf-8") as fh:
        json.dump(lexicon, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(f"\n{MARK}\n\nGenerated by `scripts/apply_audit.py` from the proposals `scripts/generate_words.py` "
                 f"wrote; see [report 8](8-reconstruction-audit.md). Result: {len(lexicon)} entries.\n\n")
        for name, title in SECTIONS:
            rows = log[name]
            fh.write(f"### {title} ({len(rows)})\n\n")
            fh.writelines(f"{i}. {r}\n" for i, r in enumerate(rows, 1))
            fh.write("\n")
    print(", ".join(f"{name} {len(rows)}" for name, rows in log.items()), "| total", len(lexicon))
    for r in log["stale"]:
        print("  stale:", r)


if __name__ == "__main__":
    main()
