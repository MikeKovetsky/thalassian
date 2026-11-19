"""research/2026-11-revival/scripts/apply_audit.py: its policy for each action, and the lexicon it produced."""
import copy
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "research", "2026-11-revival", "scripts"))
import apply_audit  # noqa: E402

from thalassian.core.lexicon import load_lexicon  # noqa: E402

EV = {"quote": "carth: KN -4.60 nats/char", "where": "research/2026-11-revival/8-audit/vocab-findings.md"}


def entry(word, source="generated", basis="generated", en="work", **extra):
    return dict({"word": word, "translation": {"uk": "uk", "en": en}, "pos": "verb", "canon": False, "root": word,
                 "notes": "Old note.", "source": source, "canon_basis": basis}, **extra)


def remove(word, source="generated", confidence="high"):
    return {"action": "remove", "word": word, "source": source, "confidence": confidence, "reason": "Why.",
            "summary": "why", "evidence": [EV]}


def fix(word, field, old, new, confidence="medium", source="generated"):
    return {"action": "fix", "word": word, "source": source, "field": field, "old": old, "new": new,
            "confidence": confidence, "reason": "Why.", "evidence": [EV]}


def regenerate(word, new, confidence="medium", source="generated"):
    return {"action": "regenerate", "word": word, "source": source, "new": new, "confidence": confidence,
            "method": "generate_words.py: seed 1", "notes": f"Replaced {word}: why (November 2026 audit).",
            "reason": "Why.", "summary": "why", "evidence": [EV], "meaning": "work"}


def add(word, confidence="medium", source="generated", canon=False):
    return {"action": "add", "word": word, "translation": {"en": "water", "uk": "вода"}, "pos": "noun",
            "canon": canon, "root": word, "notes": "Swadesh-207 item 150.", "source": source,
            "canon_basis": "generated", "confidence": confidence, "method": "generate_words.py: seed 2",
            "evidence": [], "reason": "Missing.", "summary": "water", "swadesh": 150}


class TestActions(unittest.TestCase):
    def test_remove_deletes_only_the_named_generated_or_unverified_entry(self):
        lexicon = [entry("tala"), entry("tala", source="thalassian", basis="unverified"), entry("dris'ael")]
        log = apply_audit.apply_audit(lexicon, [remove("tala"), remove("tala", source="thalassian")])
        self.assertEqual([e["word"] for e in lexicon], ["dris'ael"])
        self.assertEqual(len(log["removed"]), 2)

    def test_removing_a_canon_or_inferred_entry_is_refused(self):
        for basis, canon in (("segment", True), ("inferred", False)):
            with self.assertRaises(ValueError):
                apply_audit.apply_audit([entry("tal", source="thalassian", basis=basis, canon=canon)],
                                        [remove("tal", source="thalassian")])

    def test_a_missing_word_is_stale(self):
        lexicon = [entry("dris'ael")]
        log = apply_audit.apply_audit(lexicon, [remove("tala"), fix("tala", "pos", "verb", "noun"),
                                                regenerate("tala", "vemon")])
        self.assertEqual(len(log["stale"]), 3)
        self.assertEqual(lexicon, [entry("dris'ael")])

    def test_fix_applies_only_while_old_matches_and_keeps_the_entry_evidence(self):
        lexicon = [entry("la", pos="adverb", evidence=[{"quote": "q", "where": "w"}])]
        log = apply_audit.apply_audit(lexicon, [fix("la", "pos", "adverb", "particle"),
                                                fix("la", "notes", "Another note.", "New.")])
        self.assertEqual(lexicon[0]["pos"], "particle")
        self.assertEqual(lexicon[0]["notes"], "Old note.")
        self.assertEqual(lexicon[0]["evidence"], [{"quote": "q", "where": "w"}])
        self.assertEqual((len(log["fixed"]), len(log["stale"])), (1, 1))

    def test_fix_with_null_deletes_the_field(self):
        lexicon = [entry("nu", evidence=[{"quote": "Anar'alah = By the light.", "where": "w"}])]
        apply_audit.apply_audit(lexicon, [fix("nu", "evidence", lexicon[0]["evidence"], None)])
        self.assertNotIn("evidence", lexicon[0])

    def test_regenerate_replaces_the_form_and_keeps_the_meaning(self):
        lexicon = [entry("carth", source="generated_swadesh"), entry("dris'ael")]
        log = apply_audit.apply_audit(lexicon, [regenerate("carth", "sharius", source="generated_swadesh")])
        e = lexicon[0]
        self.assertEqual((e["word"], e["root"], e["source"], e["canon_basis"]),
                         ("sharius", "sharius", "generated", "generated"))
        self.assertEqual((e["translation"], e["pos"]), ({"uk": "uk", "en": "work"}, "verb"))
        self.assertEqual((e["confidence"], e["method"], e["evidence"]), ("medium", "generate_words.py: seed 1", [EV]))
        self.assertEqual(e["notes"], "Replaced carth: why (November 2026 audit).")
        self.assertEqual(list(e)[:len(apply_audit.ENTRY_FIELDS)], list(apply_audit.ENTRY_FIELDS))
        self.assertEqual(log["regenerated"], ["carth -> sharius (medium): work; why"])

    def test_regenerate_needs_a_generated_entry_and_a_free_form(self):
        # The new form is taken by a generated entry (sharius), or by an attested one of another source (shius).
        lexicon = [entry("isera", source="darnassian", basis="unverified"), entry("carth"), entry("sharius"),
                   entry("nubu"), entry("shius", source="thalassian", basis="attested")]
        before = copy.deepcopy(lexicon)
        log = apply_audit.apply_audit(lexicon, [regenerate("isera", "vemon", source="darnassian"),
                                                regenerate("carth", "sharius"), regenerate("nubu", "Shius")])
        self.assertEqual((lexicon, len(log["stale"])), (before, 3))

    def test_add_appends_the_entry_fields_once(self):
        lexicon = [entry("morlath")]
        log = apply_audit.apply_audit(lexicon, [add("morlath"), add("vemon"), add("vemon", source="thalassian")])
        self.assertEqual([e["word"] for e in lexicon], ["morlath", "vemon", "vemon"])
        self.assertEqual(set(lexicon[1]), set(apply_audit.ENTRY_FIELDS))
        self.assertEqual((len(log["added"]), len(log["stale"])), (2, 1))
        self.assertEqual(log["added"][0], "vemon (medium): water, Swadesh-207 item 150")

    def test_a_canon_add_is_refused(self):
        with self.assertRaises(ValueError):
            apply_audit.apply_audit([], [add("vemon", canon=True)])

    def test_removals_run_before_adds(self):
        lexicon = [entry("isera")]
        apply_audit.apply_audit(lexicon, [add("isera"), remove("isera")])
        self.assertEqual(len(lexicon), 1)
        self.assertEqual(lexicon[0]["translation"]["en"], "water")

    def test_low_confidence_is_held_and_a_note_changes_nothing(self):
        lexicon = [entry("tala"), entry("othina")]
        before = copy.deepcopy(lexicon)
        note = {"action": "note", "word": "othina", "source": "generated", "confidence": "medium",
                "reason": "Decide.", "evidence": []}
        log = apply_audit.apply_audit(lexicon, [remove("tala", confidence="low"), add("vemon", confidence="low"),
                                                note])
        self.assertEqual(lexicon, before)
        self.assertEqual((len(log["held"]), log["noted"]), (2, ["othina (medium): Decide."]))

    def test_an_unknown_action_is_refused_before_anything_changes(self):
        lexicon = [entry("tala")]
        with self.assertRaises(ValueError):
            apply_audit.apply_audit(lexicon, [remove("tala"), {"action": "demote", "word": "tala",
                                                               "confidence": "high"}])
        self.assertEqual(len(lexicon), 1)


class TestAuditInLexicon(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(apply_audit.RES, "8-candidates.json"), encoding="utf-8") as fh:
            cls.candidates = json.load(fh)
        cls.lexicon = load_lexicon()

    def find(self, word, source=None):
        return [e for e in self.lexicon if apply_audit.key(e["word"]) == apply_audit.key(word)
                and (source is None or e["source"] == source)]

    def test_every_applied_candidate_is_in_the_lexicon(self):
        for c in self.candidates:
            applied = c["confidence"] in apply_audit.APPLY
            if c["action"] == "remove":
                self.assertEqual(bool(self.find(c["word"], c["source"])), not applied, c["word"])
            elif c["action"] == "regenerate" and applied:
                self.assertEqual(self.find(c["word"], c["source"]), [], c["word"])
                new = self.find(c["new"], "generated")
                self.assertEqual(len(new), 1, c["new"])
                self.assertEqual((new[0]["method"], new[0]["evidence"]), (c["method"], c["evidence"]), c["new"])
            elif c["action"] == "add":
                hits = self.find(c["word"], c["source"])
                self.assertEqual(len(hits), int(applied), c["word"])
                if applied:
                    self.assertEqual(hits[0], {k: c[k] for k in apply_audit.ENTRY_FIELDS}, c["word"])
            elif c["action"] == "fix" and applied:
                regenerated = {x["word"]: x["new"] for x in self.candidates
                               if x["action"] == "regenerate" and x["confidence"] in apply_audit.APPLY}
                hits = (self.find(regenerated[c["word"]], "generated") if c["word"] in regenerated
                        else self.find(c["word"], c["source"]))
                self.assertEqual(len(hits), 1, c["word"])
                if c["new"] is None:
                    self.assertNotIn(c["field"], hits[0], c["word"])
                else:
                    self.assertEqual(hits[0][c["field"]], c["new"], c["word"])


if __name__ == "__main__":
    unittest.main()
