"""research/2026-11-revival/scripts/apply_voice.py: its add policy, and the lexicon it produced."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "research", "2026-11-revival", "scripts"))
import apply_voice  # noqa: E402

from thalassian.core.lexicon import load_lexicon  # noqa: E402

EV = {"quote": "/hello: 'Banu Allah'", "where": "client voice file sound/x_7744899.ogg"}


def add(word, confidence="medium", source="skyborne", canon=False):
    return {"action": "add", "word": word, "translation": {"en": "en", "uk": "uk"}, "pos": "phrase",
            "canon": canon, "root": word, "notes": "Note.", "source": source, "evidence": [dict(EV)],
            "method": "voice", "confidence": confidence}


class TestApplyAdds(unittest.TestCase):
    def test_medium_add_becomes_an_inferred_entry_without_candidate_fields(self):
        lexicon = []
        added, duplicate, held = apply_voice.apply_adds(lexicon, [add("banu alah")])
        self.assertEqual((len(added), duplicate, held), (1, [], []))
        self.assertEqual(set(lexicon[0]), set(apply_voice.ENTRY_FIELDS))
        self.assertEqual(lexicon[0]["canon_basis"], "inferred")
        self.assertEqual(lexicon[0]["evidence"], [EV])

    def test_low_add_is_held_and_fixes_are_ignored(self):
        lexicon = []
        fix = {"action": "fix", "word": "anu", "confidence": "high"}
        added, duplicate, held = apply_voice.apply_adds(lexicon, [add("aradash", confidence="low"), fix])
        self.assertEqual((lexicon, added, duplicate, len(held)), ([], [], [], 1))

    def test_same_word_and_source_is_a_duplicate_but_another_source_is_not(self):
        lexicon = [{"word": "Banu", "source": "skyborne"}]
        added, duplicate, held = apply_voice.apply_adds(
            lexicon, [add("banu"), add("banu", source="thalassian")])
        self.assertEqual((len(added), len(duplicate), held), (1, 1, []))
        self.assertEqual([e["source"] for e in lexicon], ["skyborne", "thalassian"])

    def test_canon_add_is_refused(self):
        with self.assertRaises(ValueError):
            apply_voice.apply_adds([], [add("banu", canon=True)])


class TestVoiceEntriesInLexicon(unittest.TestCase):
    def test_every_applied_candidate_left_its_evidence_in_the_lexicon(self):
        with open(os.path.join(apply_voice.RES, "5-candidates.json"), encoding="utf-8") as fh:
            candidates = json.load(fh)
        lexicon = load_lexicon()
        for c in candidates:
            entries = [e for e in lexicon if apply_voice.key(e["word"]) == apply_voice.key(c["word"])
                       and (c["action"] == "fix" or e["source"] == c["source"])]
            if c["confidence"] not in apply_voice.APPLY:
                if c["action"] == "add":
                    self.assertEqual(entries, [], c["word"])
                continue
            self.assertEqual(len(entries), 1, c["word"])
            for ev in c["evidence"]:
                self.assertIn(ev, entries[0].get("evidence", []), c["word"])
            if c["action"] == "add":
                self.assertEqual(entries[0]["canon_basis"], "inferred", c["word"])
            else:
                self.assertEqual(entries[0][c["field"]], c["new"], c["word"])


if __name__ == "__main__":
    unittest.main()
