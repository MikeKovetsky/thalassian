"""Merge the three 2026-11 candidate files into src/thalassian/data/lexicon.json.

Policy (decided in the main session, recorded in research/2026-11-revival/merge-log.md):
- Adds, fixes, demotions and removals are applied at high and medium confidence.
  Low-confidence items stay in the candidate files and are listed in the log.
- A fix is applied only if its "old" value still matches the lexicon; otherwise it is logged as stale.
- When several files add the same word, one entry wins and the evidence of all of them is merged.
  Skyborne words prefer file 3 (client-checked race research), then 2, then 1; other words prefer 1, 2, 3.
  The highest confidence among the files is kept.
- Every entry gets "canon_basis": attested | segment | epithet | localization | name | inferred |
  generated | unverified. Existing canon entries keep canon:true with basis "segment" unless the review
  lists them as attested (tier A of 1-review-and-methods.md section 1.1).
- When file 1 removes a word and file 2 only annotates it, the removal wins (logged as a conflict).
- Decisions the files leave open are in MANUAL, and notes or parts of speech that still describe a gloss
  the audit replaced are fixed by CORRECTIONS; both are logged.

The merge runs once, on the pre-revival lexicon (commit 42eb9cf). apply_localization.py then applies
4-candidates.json on top, apply_voice.py applies 5-candidates.json, apply_audit.py applies 8-candidates.json
(report 8; generate_words.py wrote that file and is not part of the recipe), and apply_wc3_midnight.py applies
9-, 10- and 11-candidates.json (reports 9 to 11). To reproduce lexicon.json and merge-log.md, from the repo root:
  git show 42eb9cf:src/thalassian/data/lexicon.json > src/thalassian/data/lexicon.json
  python3 research/2026-11-revival/scripts/merge_candidates.py
  python3 research/2026-11-revival/scripts/apply_localization.py
  python3 research/2026-11-revival/scripts/apply_voice.py
  python3 research/2026-11-revival/scripts/apply_audit.py
  python3 research/2026-11-revival/scripts/apply_wc3_midnight.py
"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
LEX = os.path.join(ROOT, "src", "thalassian", "data", "lexicon.json")
RES = os.path.join(ROOT, "research", "2026-11-revival")
LOG = os.path.join(RES, "merge-log.md")

APPLY = {"high", "medium"}
RANK = {"high": 3, "medium": 2, "low": 1}
TIER_A = {"belore", "rea", "aranal", "finel", "minda", "min'da", "anda", "an'da", "lura", "shal'na"}

# Decisions the candidate files leave open: word -> (fields to set on the added entry, why).
MANUAL = {
    "eluvi'ana": (
        dict(canon=True, canon_basis="epithet", source="skyborne", confidence="high",
             notes="Darnassian (Skyborne dialect). A sword (item 276188, flavor text 'The Night Dancer.'), raised in "
                   "spell 1314923 ('Raising Eluvi'ana, the Night Dancer.'); twin of Eluvi'tor. The epithet may not "
                   "be a literal translation: if it were, ana would mean 'dancer', against Thalassian ana "
                   "'fare/status'."),
        "The wiki primer (official translations) lists it, and the client shows it as a sword's epithet, so it is "
        "canon with basis epithet. File 1 won the merge with empty notes; the notes come from file 3."),
}

# Post-merge consistency: text that still describes a gloss the audit replaced or removed.
# (word, field, old text, new text, why). Notes and translations replace a substring; pos must match exactly.
GREAT = "the canon gloss is 'Justice for our people', with no 'great'"
KINGDOM = "'kingdom' comes only from the non-canon RPG; thalas is 'home'"
NO_EL = "el 'peace' was removed as a mis-segmentation of diel"
CORRECTIONS = [
    ("anore", "notes", "Used in 'ashal'anore' (great people).",
     "Used in 'Selama ashal'anore' (Justice for our people).", GREAT),
    ("ashal", "notes", "(Justice for our great people)", "(Justice for our people)", GREAT),
    ("selama", "notes", "(Justice for our great people)", "(Justice for our people)", GREAT),
    ("thiel", "notes", "Diminutive root; contrasts with ashal (great)", "Diminutive root.",
     "ashal no longer means 'great'"),
    ("quel", "notes", "Quel'Thalas (High Kingdom)", "Quel'Thalas (High Home)", KINGDOM),
    ("thalas", "notes", "Quel'Thalas (High Kingdom)", "Quel'Thalas (High Home)", KINGDOM),
    ("eldre'thalas", "notes", "thalas (home/kingdom)", "thalas (home)", KINGDOM),
    ("as", "notes", "'home/kingdom' (lexicon)", "'home' (lexicon)", KINGDOM),
    ("dash", "notes", "(Greetings/Peace be with you)", "(Greetings)", "'peace' was the unsupported old gloss"),
    ("anu'shalla", "notes", "Midnight (12.0) Alpha: Anu'shalla Void Owl.",
     "Formerly cited as 'Midnight (12.0) Alpha: Anu'shalla Void Owl'.", "that provenance was wrong"),
    ("alon", "notes", "(Hail the sun's eternal blessing)",
     "(an old fan reading, 'Hail the sun's eternal blessing'; the phrase is untranslated, and no source gives "
     "anu = 'hail')", "anu = 'hail' is unsupported"),
    ("shal'nan", "notes",
     "Not related to Thalassian shal'na 'no!/please' (similar shape only); compare Darnassian Shal'nar 'aunt'.",
     "Similar in shape to Thalassian shal'na and Darnassian Shal'nar, both 'aunt', but not related in meaning.",
     "shal'na now means 'aunt'"),
    ("aeesha'el banu zepharaalis", "translation.en", "may peace and the winds of Zephras go with you",
     "may the winds of Zephras go with you", NO_EL),
    ("aeesha'el banu zepharaalis", "translation.uk", "хай мир і вітри Зефраса будуть з тобою",
     "хай вітри Зефраса будуть з тобою", NO_EL),
    ("aeesha'el banu zepharaalis", "notes", "their glosses are guesses.",
     "their glosses are guesses. An earlier 'peace' reading of aeesha'el rested on el 'peace', which the audit "
     "removed.", NO_EL),
    ("dris", "notes", "New fundamental root for eye/sight; used in many compounds",
     "Darnassian 'eye', segmented from Elun'dris 'the Eye of Elune'. First added in March 2026 as a generated "
     "word.", "re-sourced as a Darnassian morpheme"),
    ("anar", "pos", "noun", "preposition", "its gloss is 'by'"),
    ("ashal", "pos", "adjective", "preposition", "its gloss is 'for'"),
    ("ru", "pos", "verb", "particle", "its gloss is a future/modal particle"),
]


def key(word):
    return word.strip().lower()


def load(name):
    with open(os.path.join(RES, name), encoding="utf-8") as fh:
        return json.load(fh)


def basis_for_new(entry):
    method = (entry.get("method") or "").lower()
    if not entry.get("canon"):
        return "inferred"
    if "locali" in method:
        return "localization"
    if "epithet" in method:
        return "epithet"
    if "referent" in method or "place name" in method or "alias" in method:
        return "name"
    if "segment" in method:
        return "segment"
    return "attested"


def merge_evidence(*lists):
    seen, out = set(), []
    for lst in lists:
        for ev in lst or []:
            k = (ev.get("quote"), ev.get("where"))
            if k not in seen:
                seen.add(k)
                out.append(ev)
    return out


def apply_corrections(lexicon, log):
    for word, field, old, new, why in CORRECTIONS:
        label = f"{word}.{field}"
        entry = next((e for e in lexicon if key(e["word"]) == key(word)), None)
        if entry is None:
            log["stale"].append(f"{label}: word not found")
            continue
        holder, name = (entry["translation"], field.split(".", 1)[1]) if "." in field else (entry, field)
        current = holder.get(name, "")
        if (current != old) if field == "pos" else (old not in current):
            log["stale"].append(f"{label}: {old!r} not in current value {current!r}")
            continue
        holder[name] = new if field == "pos" else current.replace(old, new)
        log["corrected"].append(f"{label}: {why}")


def main():
    with open(LEX, encoding="utf-8") as fh:
        lexicon = json.load(fh)
    if any("canon_basis" in e for e in lexicon):
        sys.exit("lexicon.json already carries canon_basis, so the merge has been applied; running it again would "
                 "duplicate every added entry. Restore the pre-merge lexicon first (see this script's docstring).")
    files = {n: load(f"{n}-candidates.json") for n in ("1", "2", "3")}
    log = {"applied": [], "skipped_low": [], "stale": [], "conflicts": [], "added": [], "removed": [],
           "demoted": [], "merged_adds": [], "manual": [], "corrected": []}

    def find(word, old=None, field=None):
        hits = [e for e in lexicon if key(e["word"]) == key(word)]
        if len(hits) > 1 and field is not None:
            hits = [e for e in hits if e.get(field) == old] or hits
        return hits[0] if hits else None

    # Existing entries: initial canon_basis.
    for e in lexicon:
        if e.get("canon"):
            e["canon_basis"] = "attested" if key(e["word"]) in TIER_A else "segment"
        elif e.get("source") in ("generated", "generated_swadesh"):
            e["canon_basis"] = "generated"
        else:
            e["canon_basis"] = "inferred"

    items = [(n, c) for n, lst in files.items() for c in lst]
    removals = {key(c["word"]) for n, c in items if c["action"] == "remove" and c["confidence"] in APPLY}

    # 1. Fixes (field edits other than renames), then renames.
    fixes = [(n, c) for n, c in items if c["action"] == "fix"]
    fixes.sort(key=lambda nc: nc[1]["field"] == "word")
    for n, c in fixes:
        label = f"{c['word']}.{c['field']} (file {n}, {c['confidence']})"
        if c["confidence"] not in APPLY:
            log["skipped_low"].append(label)
            continue
        if key(c["word"]) in removals:
            log["conflicts"].append(f"{label}: word is removed by file 1, so this fix is dropped")
            continue
        entry = find(c["word"], c.get("old"), c["field"])
        if entry is None:
            log["stale"].append(f"{label}: word not found")
            continue
        if entry.get(c["field"]) != c.get("old"):
            log["stale"].append(f"{label}: current value {entry.get(c['field'])!r} != old {c.get('old')!r}")
            continue
        entry[c["field"]] = c["new"]
        entry["evidence"] = merge_evidence(entry.get("evidence"), c.get("evidence"))
        log["applied"].append(label)

    # A fix can re-source a generated entry (dris: generated_swadesh -> darnassian); its basis follows.
    for e in lexicon:
        if e["canon_basis"] == "generated" and e.get("source") not in ("generated", "generated_swadesh"):
            e["canon_basis"] = "inferred"

    # 2. Demotions.
    for n, c in items:
        if c["action"] != "demote":
            continue
        if c["confidence"] not in APPLY:
            log["skipped_low"].append(f"demote {c['word']} (file {n})")
            continue
        entry = find(c["word"])
        if entry is None:
            log["stale"].append(f"demote {c['word']}: not found")
            continue
        entry["canon"] = False
        entry["canon_basis"] = "unverified"
        reason = c.get("reason", "").strip()
        note = entry.get("notes", "").rstrip()
        if note and note[-1] not in ".!?":
            note += "."
        entry["notes"] = (note + f" Not canon (2026-11 audit): {reason}").strip()
        entry["evidence"] = merge_evidence(entry.get("evidence"), c.get("evidence"))
        log["demoted"].append(f"{c['word']}: {reason}")

    # 3. Removals.
    for n, c in items:
        if c["action"] != "remove":
            continue
        if c["confidence"] not in APPLY:
            log["skipped_low"].append(f"remove {c['word']} (file {n}): {c.get('reason', '')}")
            continue
        before = len(lexicon)
        lexicon[:] = [e for e in lexicon if key(e["word"]) != key(c["word"])]
        if len(lexicon) == before:
            log["stale"].append(f"remove {c['word']}: not found")
        else:
            log["removed"].append(f"{c['word']} ({c['confidence']}): {c.get('reason', '')}")

    # 4. Adds, grouped by word.
    groups = {}
    for n, c in items:
        if c["action"] == "add":
            groups.setdefault(key(c["word"]), []).append((n, c))
    for w, group in groups.items():
        best_conf = max(RANK[c["confidence"]] for _, c in group)
        if best_conf < RANK["medium"]:
            for n, c in group:
                log["skipped_low"].append(f"add {c['word']} (file {n}): {c['translation'].get('en')}")
            continue
        skyborne = any(c.get("source") == "skyborne" for _, c in group)
        order = ("3", "2", "1") if skyborne else ("1", "2", "3")
        group.sort(key=lambda nc: (-RANK[nc[1]["confidence"]], order.index(nc[0])))
        n, win = group[0]
        entry = {k: win[k] for k in ("word", "translation", "pos", "canon", "root", "notes", "source")}
        entry["canon_basis"] = basis_for_new(win)
        entry["confidence"] = win["confidence"]
        entry["method"] = win.get("method", "")
        entry["evidence"] = merge_evidence(*(c.get("evidence") for _, c in group))
        if w in MANUAL:
            changes, why = MANUAL[w]
            entry.update(changes)
            set_fields = ", ".join(f"{k}={v!r}" for k, v in changes.items() if k != "notes")
            log["manual"].append(f"{win['word']}: {why} Set {set_fields} and the notes.")
        if len(group) > 1:
            others = ", ".join(f"file {m} ({c['confidence']}, canon={c['canon']}, source={c.get('source')})"
                               for m, c in group[1:])
            log["merged_adds"].append(f"{win['word']}: kept file {n} ({win['confidence']}, canon={win['canon']}, "
                                      f"source={win.get('source')}); merged evidence from {others}")
        same = [e for e in lexicon if key(e["word"]) == w and e.get("source") == entry["source"]]
        if same:
            log["conflicts"].append(f"add {win['word']}: an entry with the same word and source exists; kept both")
        lexicon.append(entry)
        log["added"].append(f"{win['word']} [{entry['source']}, {entry['confidence']}, {entry['canon_basis']}]: "
                            f"{entry['translation'].get('en')}")

    apply_corrections(lexicon, log)

    with open(LEX, "w", encoding="utf-8") as fh:
        json.dump(lexicon, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    with open(LOG, "w", encoding="utf-8") as fh:
        fh.write("# Merge log: 2026-11 candidates into lexicon.json\n\n")
        fh.write(f"Result: {len(lexicon)} entries. Generated by `scripts/merge_candidates.py`; policy in its docstring.\n\n")
        for sect, title in (("added", "Added"), ("applied", "Fixes applied"), ("demoted", "Demoted to canon:false"),
                            ("removed", "Removed"), ("merged_adds", "Same word proposed by several files"),
                            ("manual", "Manual decisions"),
                            ("corrected", "Post-merge consistency corrections"),
                            ("conflicts", "Conflicts and how they were settled"), ("stale", "Stale or unmatched"),
                            ("skipped_low", "Held back (low confidence)")):
            rows = log[sect]
            fh.write(f"## {title} ({len(rows)})\n\n")
            fh.writelines(f"{i}. {r}\n" for i, r in enumerate(rows, 1))
            fh.write("\n")
    print(json.dumps({k: len(v) for k, v in log.items()}), "total", len(lexicon))


if __name__ == "__main__":
    sys.exit(main())
