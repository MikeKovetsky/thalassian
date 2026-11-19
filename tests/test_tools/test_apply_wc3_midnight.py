"""research/2026-11-revival/scripts/apply_wc3_midnight.py: its policy for each action, that a second run changes
nothing, and the lexicon it produced from reports 9 to 11."""
import copy
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "research", "2026-11-revival", "scripts"))
import apply_wc3_midnight as W  # noqa: E402

from thalassian.core.lexicon import load_lexicon  # noqa: E402
from thalassian.syntax.parser import compile_sentence_en  # noqa: E402

EV_OLD = {"quote": "Shan'do = Honored Teacher.", "where": "https://warcraft.wiki.gg/wiki/Darnassian"}
EV_NEW = {"quote": "Shan'do Stormrage will be defenseless!", "where": "NightElf03.w3x STRING 186"}


def entry(word, source="darnassian", evidence=(EV_OLD,), **extra):
    return dict({"word": word, "translation": {"en": "teacher", "uk": "учитель"}, "pos": "noun", "canon": True,
                 "root": word, "notes": "Old note.", "source": source, "canon_basis": "segment",
                 "evidence": [dict(ev) for ev in evidence]}, **extra)


def fix(word, field, old, new, confidence="high", evidence=None):
    c = {"action": "fix", "word": word, "field": field, "old": old, "new": new, "confidence": confidence,
         "method": "test", "reason": "Why. More."}
    if evidence is not None:
        c["evidence"] = [dict(ev) for ev in evidence]
    return c


def add(word, confidence="high", source="darnassian", canon=True, basis="attested", **extra):
    return dict({"action": "add", "word": word, "translation": {"en": "honored teacher", "uk": "шановний учитель"},
                 "pos": "noun", "canon": canon, "root": "shan + do", "notes": "A title. More.", "source": source,
                 "canon_basis": basis, "evidence": [dict(EV_OLD), dict(EV_NEW)], "method": "test",
                 "confidence": confidence, "reason": "Glossed twice."}, **extra)


def note(word, confidence="low"):
    return {"action": "note", "word": word, "translation": None, "source": "darnassian", "canon_basis": None,
            "notes": "Unglossed. Spelled differently.", "evidence": [dict(EV_NEW)], "method": "test",
            "confidence": confidence, "reason": "Recorded."}


class TestApplyReport(unittest.TestCase):
    def test_fix_applies_only_while_old_matches_and_merges_its_evidence(self):
        lexicon = [entry("do")]
        log = W.apply_report(lexicon, [fix("do", "notes", "Old note.", "New note.", evidence=[EV_NEW]),
                                       fix("do", "pos", "verb", "particle")])
        self.assertEqual((lexicon[0]["notes"], lexicon[0]["pos"]), ("New note.", "noun"))
        self.assertEqual(lexicon[0]["evidence"], [EV_OLD, EV_NEW])
        self.assertEqual(log["fixed"], ["fix do.notes (high)"])
        self.assertEqual(log["stale"], ["fix do.pos (high)"])

    def test_an_evidence_fix_goes_before_a_fix_that_merges_evidence_into_the_same_entry(self):
        # In the file the notes fix comes first; run first, it would merge EV_NEW and leave the evidence fix stale.
        third = {"quote": "Anu'dorini Talah!", "where": "wiki quote list"}
        lexicon = [entry("anu'dorini talah")]
        log = W.apply_report(lexicon, [
            fix("anu'dorini talah", "notes", "Old note.", "New note.", evidence=[EV_NEW]),
            fix("anu'dorini talah", "evidence", [EV_OLD], [EV_OLD, EV_NEW, third])])
        self.assertEqual(lexicon[0]["evidence"], [EV_OLD, EV_NEW, third])
        self.assertEqual(lexicon[0]["notes"], "New note.")
        self.assertEqual((len(log["fixed"]), log["stale"]), (2, []))

    def test_add_appends_the_entry_fields_once_per_word_and_source(self):
        lexicon = [entry("shan'do")]
        log = W.apply_report(lexicon, [add("shan'do"), add("Shan'do", source="thalassian"), add("thero'shan")])
        self.assertEqual([(e["word"], e["source"]) for e in lexicon],
                         [("shan'do", "darnassian"), ("Shan'do", "thalassian"), ("thero'shan", "darnassian")])
        self.assertEqual(set(lexicon[1]), set(W.ENTRY_FIELDS))
        self.assertEqual(log["added"], ["Shan'do [thalassian, high, attested]: honored teacher",
                                        "thero'shan [darnassian, high, attested]: honored teacher"])
        self.assertEqual(log["stale"], ["add shan'do (high): an entry with the same word and source exists"])

    def test_an_add_must_fit_the_canon_basis_table(self):
        lexicon = []
        W.apply_report(lexicon, [add("arcan'dor", basis="name"), add("ilastar", canon=False, basis="name"),
                                 add("morothoray katal", canon=False, basis="inferred")])
        self.assertEqual(len(lexicon), 3)
        for bad in (add("shan'do", basis="inferred"), add("shan'do", canon=False, basis="epithet"),
                    add("shan'do", canon=False, basis="generated")):
            with self.assertRaises(ValueError):
                W.apply_report([], [bad])

    def test_an_add_without_a_gloss_method_or_quoted_evidence_is_refused(self):
        for bad in (add("shan'do", translation={"en": "honored teacher", "uk": ""}), add("shan'do", method=""),
                    add("shan'do", evidence=[]), add("shan'do", evidence=[{"quote": "", "where": "w"}])):
            with self.assertRaises(ValueError):
                W.apply_report([], [bad])
        incomplete = add("shan'do")
        del incomplete["canon_basis"]
        with self.assertRaises(ValueError):
            W.apply_report([], [incomplete])

    def test_a_refused_add_changes_nothing_even_after_a_good_fix(self):
        lexicon = [entry("do")]
        before = copy.deepcopy(lexicon)
        with self.assertRaises(ValueError):
            W.apply_report(lexicon, [fix("do", "notes", "Old note.", "New note."), add("shan'do", method="")])
        self.assertEqual(lexicon, before)

    def test_low_confidence_is_held_and_a_note_changes_nothing(self):
        lexicon = [entry("do")]
        before = copy.deepcopy(lexicon)
        incomplete_low_add = add("aradash", confidence="low")
        del incomplete_low_add["canon_basis"]  # held, so its fields are not checked (11-candidates.json has these)
        log = W.apply_report(lexicon, [fix("do", "notes", "Old note.", "New.", confidence="low"),
                                       incomplete_low_add, note("anu'dora"), note("andu fallah", "medium")])
        self.assertEqual(lexicon, before)
        self.assertEqual(log["held"], ["fix do.notes (low): Why.", "add aradash (low): A title.",
                                       "note anu'dora (low): Unglossed."])
        self.assertEqual(log["noted"], ["note andu fallah (medium): Unglossed."])

    def test_an_unknown_action_is_refused_before_anything_changes(self):
        lexicon = [entry("do")]
        before = copy.deepcopy(lexicon)
        for action in ("remove", "demote", "regenerate"):
            with self.assertRaises(ValueError):
                W.apply_report(lexicon, [fix("do", "notes", "Old note.", "New."), add("shan'do"),
                                         {"action": action, "word": "do", "confidence": "high"}])
            self.assertEqual(lexicon, before)

    def test_applying_the_same_candidates_twice_changes_nothing_the_second_time(self):
        lexicon = [entry("do"), entry("sin'dorei", source="thalassian")]
        candidates = [fix("do", "notes", "Old note.", "New.", evidence=[EV_NEW]),
                      fix("sin'dorei", "evidence", [EV_OLD], [EV_OLD, EV_NEW]), add("shan'do"), note("anu'dora")]
        W.apply_report(lexicon, candidates)
        once = copy.deepcopy(lexicon)
        log = W.apply_report(lexicon, candidates)
        self.assertEqual(lexicon, once)
        self.assertEqual((log["fixed"], log["added"], len(log["stale"]), len(log["held"])), ([], [], 3, 1))


class TestMain(unittest.TestCase):
    """main() on a copy: one section per file, and a second run that changes no byte."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        d = self.dir.name
        self.lex, self.log = os.path.join(d, "lexicon.json"), os.path.join(d, "merge-log.md")
        files = {"9": [add("shan'do"), note("anu'dora")],
                 "10": [fix("do", "notes", "Old note.", "New.", confidence="medium", evidence=[EV_NEW])],
                 "11": [add("morothoray katal", confidence="low", canon=False, basis="inferred")]}
        for number, candidates in files.items():
            with open(os.path.join(d, f"{number}-candidates.json"), "w", encoding="utf-8") as fh:
                json.dump(candidates, fh)
        with open(self.lex, "w", encoding="utf-8") as fh:
            json.dump([entry("do")], fh)
        with open(self.log, "w", encoding="utf-8") as fh:
            fh.write("# Merge log\n")
        for name, value in (("LEX", self.lex), ("LOG", self.log), ("RES", d)):
            patcher = mock.patch.object(W, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def read(self):
        with open(self.lex, "rb") as a, open(self.log, "rb") as b:
            return a.read(), b.read()

    def run_main(self):
        with mock.patch("builtins.print"):
            W.main()

    def test_one_section_per_file_and_a_second_run_changes_no_byte(self):
        self.run_main()
        lexicon, log = self.read()
        self.assertEqual([e["word"] for e in json.loads(lexicon)], ["do", "shan'do"])
        text = log.decode("utf-8")
        for number, title, _ in W.FILES:
            self.assertEqual(text.count(W.mark(number, title)), 1)
        self.assertIn("Result: 2 entries.", text)
        with self.assertRaises(SystemExit):
            self.run_main()
        self.assertEqual(self.read(), (lexicon, log))

    def test_a_file_already_in_the_log_is_skipped(self):
        with open(self.log, "a", encoding="utf-8") as fh:
            fh.write(f"\n{W.mark(*W.FILES[0][:2])}\n")
        self.run_main()
        lexicon, log = self.read()
        self.assertEqual([e["word"] for e in json.loads(lexicon)], ["do"])
        self.assertEqual(json.loads(lexicon)[0]["notes"], "New.")
        self.assertEqual([line for line in log.decode("utf-8").splitlines() if line.startswith("## ")],
                         [W.mark(number, title) for number, title, _ in W.FILES])


class TestReportsInLexicon(unittest.TestCase):
    """Whatever 9-, 10- and 11-candidates.json hold, the lexicon shows every candidate the policy applies."""

    @classmethod
    def setUpClass(cls):
        cls.lexicon = load_lexicon()
        cls.files = []
        for number, _, _ in W.FILES:
            with open(os.path.join(W.RES, f"{number}-candidates.json"), encoding="utf-8") as fh:
                cls.files.append(json.load(fh))

    def find(self, word, source=None):
        return [e for e in self.lexicon
                if W.key(e["word"]) == W.key(word) and (source is None or e["source"] == source)]

    def test_every_add_is_applied_or_held_by_its_confidence(self):
        for c in (c for f in self.files for c in f if c["action"] == "add"):
            hits = self.find(c["word"], c["source"])
            if c["confidence"] in W.APPLY:
                self.assertEqual(hits, [{k: c[k] for k in W.ENTRY_FIELDS}], c["word"])
            else:
                self.assertEqual(hits, [], c["word"])

    def test_every_applied_fix_holds_with_its_evidence(self):
        final = {}
        fixes = [c for f in self.files for c in f if c["action"] == "fix" and c["confidence"] in W.APPLY]
        for c in fixes:
            final[(W.key(c["word"]), c["field"])] = c["new"]
        for c in fixes:
            hits = self.find(c["word"])
            self.assertEqual(len(hits), 1, c["word"])
            if c["field"] == "evidence":
                # A later file may add to the same evidence (report 10's sin'dorei builds on report 9's).
                for ev in c["new"]:
                    self.assertIn(ev, hits[0]["evidence"], c["word"])
            else:
                self.assertEqual(hits[0][c["field"]], final[(W.key(c["word"]), c["field"])], c["word"])
            for ev in c.get("evidence", []):
                self.assertIn(ev, hits[0]["evidence"], c["word"])

    def test_a_held_fix_is_not_in_the_lexicon(self):
        for c in (c for f in self.files for c in f if c["action"] == "fix" and c["confidence"] not in W.APPLY):
            hits = self.find(c["word"])
            self.assertEqual(len(hits), 1, c["word"])
            self.assertNotEqual(hits[0][c["field"]], c["new"], c["word"])

    def test_an_added_name_or_epithet_does_not_translate_the_words_of_its_gloss(self):
        # An epithet is not a translation (docs/methodology/lexicon.md, section 3): "talon" must not become
        # Belo'melorn, nor "dawnsong" Alah'endal.
        for c in (c for f in self.files for c in f if c["action"] == "add" and c["confidence"] in W.APPLY
                  and c["canon_basis"] in ("name", "epithet")):
            for word in set(c["translation"]["en"].replace("'", " ").replace(":", " ").split()):
                self.assertNotEqual(compile_sentence_en(word, self.lexicon).lower(), c["word"].lower(),
                                    f"{word} -> {c['word']}")


if __name__ == "__main__":
    unittest.main()
