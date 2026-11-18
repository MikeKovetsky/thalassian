"""Data checks for lexicon.json, against the canon_basis table in docs/methodology/lexicon.md."""
import unittest
from collections import Counter

from thalassian.core.lexicon import load_lexicon

CANON_BASES = {"attested", "segment", "epithet", "name"}
NON_CANON_BASES = {"name", "inferred", "generated", "unverified"}
GENERATED_SOURCES = {"generated", "generated_swadesh"}


class TestLexiconIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lexicon = load_lexicon()

    def test_canon_flag_matches_basis(self):
        for e in self.lexicon:
            allowed = CANON_BASES if e["canon"] else NON_CANON_BASES
            self.assertIn(e.get("canon_basis"), allowed, e["word"])

    def test_generated_basis_only_for_generated_sources(self):
        # A generated word that turned out to be attested (dris) is re-sourced, and its basis must follow.
        for e in self.lexicon:
            self.assertEqual(e["canon_basis"] == "generated", e["source"] in GENERATED_SOURCES, e["word"])

    def test_every_entry_has_en_and_uk(self):
        # Both translators read both glosses.
        for e in self.lexicon:
            self.assertTrue(e["translation"].get("en") and e["translation"].get("uk"), e["word"])

    def test_homographs_differ_in_source(self):
        counts = Counter((e["word"].lower(), e["source"]) for e in self.lexicon)
        self.assertEqual([k for k, n in counts.items() if n > 1], [])

    def test_revival_entries_carry_evidence(self):
        for e in self.lexicon:
            if "confidence" in e:
                self.assertIn(e["confidence"], ("high", "medium"), e["word"])
                self.assertTrue(e.get("evidence"), e["word"])


if __name__ == "__main__":
    unittest.main()
