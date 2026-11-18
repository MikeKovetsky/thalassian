"""research/2026-11-revival/scripts/apply_localization.py: its fix policy, and the lexicon it produced."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "research", "2026-11-revival", "scripts"))
import apply_localization  # noqa: E402

from thalassian.core.lexicon import load_lexicon  # noqa: E402

EV_OLD = {"quote": "Old quote.", "where": "https://example.org/old"}
EV_NEW = {"quote": "New quote.", "where": "https://example.org/new"}


def fix(word, old, new, confidence="high", evidence=(EV_NEW,)):
    return {"action": "fix", "word": word, "field": "notes", "old": old, "new": new,
            "evidence": [dict(ev) for ev in evidence], "confidence": confidence}


class TestApplyFixes(unittest.TestCase):
    def setUp(self):
        self.lexicon = [{"word": "Anore", "notes": "Old note.", "evidence": [dict(EV_OLD)]}]

    def test_fix_sets_the_field_and_merges_its_evidence_once(self):
        applied, stale, held = apply_localization.apply_fixes(
            self.lexicon, [fix("anore", "Old note.", "New note.", evidence=(EV_OLD, EV_NEW))])
        self.assertEqual(self.lexicon[0]["notes"], "New note.")
        self.assertEqual(self.lexicon[0]["evidence"], [EV_OLD, EV_NEW])
        self.assertEqual((len(applied), stale, held), (1, [], []))

    def test_entry_without_evidence_gets_the_fix_evidence(self):
        lexicon = [{"word": "selama", "notes": "Old."}]
        apply_localization.apply_fixes(lexicon, [fix("selama", "Old.", "New.")])
        self.assertEqual(lexicon[0]["evidence"], [EV_NEW])

    def test_fix_whose_old_value_no_longer_matches_is_stale(self):
        applied, stale, held = apply_localization.apply_fixes(
            self.lexicon, [fix("anore", "An earlier note.", "New note."), fix("missing", "Old.", "New.")])
        self.assertEqual(self.lexicon[0], {"word": "Anore", "notes": "Old note.", "evidence": [EV_OLD]})
        self.assertEqual((applied, len(stale), held), ([], 2, []))

    def test_low_confidence_fixes_and_adds_are_held_back(self):
        add = {"action": "add", "word": "anar'alash denal", "confidence": "high"}
        applied, stale, held = apply_localization.apply_fixes(
            self.lexicon, [fix("anore", "Old note.", "New note.", confidence="low"), add])
        self.assertEqual(self.lexicon[0]["notes"], "Old note.")
        self.assertEqual((applied, stale, len(held)), ([], [], 2))


class TestLocalizationEvidenceInLexicon(unittest.TestCase):
    def test_every_applied_fix_left_its_evidence_in_the_lexicon(self):
        with open(os.path.join(apply_localization.RES, "4-candidates.json"), encoding="utf-8") as fh:
            candidates = json.load(fh)
        lexicon = load_lexicon()
        for c in candidates:
            if c["action"] != "fix" or c["confidence"] not in apply_localization.APPLY:
                continue
            entries = [e for e in lexicon if apply_localization.key(e["word"]) == apply_localization.key(c["word"])]
            self.assertEqual(len(entries), 1, c["word"])
            for ev in c["evidence"]:
                self.assertIn(ev, entries[0].get("evidence", []), f"{c['word']}.{c['field']}")


if __name__ == "__main__":
    unittest.main()
