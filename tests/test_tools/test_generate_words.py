"""research/2026-11-revival/scripts/generate_words.py: the model, the filters, the selection, and the committed
8-candidates.json. Nothing here needs the local scrambler files or the system word list."""
import json
import math
import os
import random
import re
import sys
import unittest
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "research", "2026-11-revival", "scripts"))
import generate_words as g  # noqa: E402

TRAIN = ["thalas", "belore", "dorei", "selama", "shala", "alann", "anore", "dinoriel", "shorel", "aranal", "talah",
         "sinu", "diel", "elor", "bindel", "melorn", "arkhana", "falor"]


def entry(word, source="thalassian", basis="segment", en="x"):
    return {"word": word, "source": source, "canon_basis": basis, "translation": {"en": en, "uk": "x"}}


def inventory(lexicon=None, forms=(), scramblers=(), english=(), foreign=None, alphabet="abdefghijklmnoprstuvwyz"):
    """A toy inventory. The toy training set is too small for MIN_LETTER_PARTS, so the alphabet is set by hand."""
    lexicon = lexicon if lexicon is not None else [entry(w) for w in TRAIN]
    inv = g.Inventory(lexicon, list(forms), list(scramblers), set(english), foreign={} if foreign is None else foreign)
    if alphabet:
        inv.alphabet = set(alphabet)
    return inv


class TestKneserNey(unittest.TestCase):
    def setUp(self):
        self.model = g.KneserNey(TRAIN)

    def test_every_distribution_sums_to_one(self):
        for ctx in ("", "t", "th", "tha", "zzz", "qqqq"):
            self.assertAlmostEqual(sum(self.model.dist(ctx).values()), 1.0, places=9, msg=ctx)

    def test_a_seen_continuation_beats_an_unseen_one(self):
        self.assertGreater(self.model.dist("tha")["l"], self.model.dist("tha")["k"])
        self.assertGreater(self.model.score("thalas"), self.model.score("khzrrk"))

    def test_lower_orders_use_continuation_counts(self):
        # The unigram count of a symbol is how many different symbols precede it, not how often it occurs.
        model = g.KneserNey(["aaaa", "ba"])
        self.assertEqual(model.counts[0][""]["a"], 3)  # preceded by "^", "a" and "b"
        self.assertEqual(model.counts[0][""]["b"], 1)

    def test_sampling_is_deterministic_and_stays_in_the_alphabet(self):
        a = [self.model.sample(random.Random(5)) for _ in range(3)]
        rng1, rng2 = random.Random(9), random.Random(9)
        self.assertEqual([self.model.sample(rng1) for _ in range(50)], [self.model.sample(rng2) for _ in range(50)])
        self.assertEqual(len(set(a)), 1)
        letters = set("".join(TRAIN))
        for w in (self.model.sample(random.Random(i)) for i in range(200)):
            if w is not None:
                self.assertLessEqual(set(w), letters)

    def test_score_is_log_probability_per_character_with_the_end_symbol(self):
        self.assertAlmostEqual(self.model.score("dorei"), self.model.logp("dorei") / 6)

    def test_seed_comes_from_the_meaning_alone(self):
        self.assertEqual(g.seed_for("water"), 16773596909112)  # the seed in morlath's method
        self.assertNotEqual(g.seed_for("water"), g.seed_for("fire"))

    def test_percentile_against_leave_one_out_scores(self):
        yardstick = g.loo_scores(TRAIN)
        self.assertEqual(len(yardstick), len(TRAIN))
        self.assertEqual(yardstick, sorted(yardstick))
        self.assertEqual(g.percentile(yardstick[0] - 1, yardstick), 0.0)
        self.assertEqual(g.percentile(yardstick[-1] + 1, yardstick), 100.0)


class TestFilters(unittest.TestCase):
    def test_a_letter_needs_five_attested_parts(self):
        inv = inventory(alphabet=None)
        self.assertEqual(inv.alphabet, {ch for ch in set("".join(TRAIN))
                                        if sum(ch in w for w in TRAIN) >= g.MIN_LETTER_PARTS})
        self.assertEqual(inv.reject("khalas"), "alphabet")  # k: arkhana only

    def test_near_needs_four_letters_for_one_edit(self):
        self.assertEqual(g.near("tala", {"tal"}), "tal")
        self.assertEqual(g.near("tal", {"tal"}), "tal")
        self.assertIsNone(g.near("tel", {"tal"}))
        self.assertIsNone(g.near("tolar", {"tal"}))
        self.assertEqual(g.near("talor", {"falor"}), "falor")

    def test_phonotactics(self):
        for word in ("thalas", "shindel", "drali", "anu"):
            self.assertTrue(g.phonotactic(word), word)
        for word in ("rthalah", "anksa", "allla", "belok", "kras"):
            self.assertFalse(g.phonotactic(word), word)

    def test_keys_split_and_join(self):
        self.assertEqual(g.keys("Anar'alah belore"), {"anar", "alah", "belore", "anaralah"})

    def test_each_reason(self):
        lexicon = [entry(w) for w in TRAIN] + [entry("nubu", "generated", "generated", "fast"),
                                               entry("delar", "thalassian", "unverified", "(unknown)")]
        forms = [{"form": "Thala nar'valas", "branch": "shalassian"}, {"form": "Fa'da", "branch": "zandali"}]
        inv = inventory(lexicon, forms, scramblers=["Kazum'nobu", "Shari"], english={"moon", "sir"},
                        foreign={"meir": "given name"})
        cases = {
            "qalas": "alphabet",  # q is in no training part
            "thelis": "ending -is or -ael", "dris'ael".replace("'", ""): "ending -is or -ael",
            "rthala": "phonotactics", "sir": "English word", "meir": "word in another language",
            "thala": "attested form", "delar": "attested form", "valas": "attested form",
            "selamo": "attested form",  # one edit from selama
            "ishelor": "contains a part with a known meaning",  # elor
            "vadiel": "contains a part with a known meaning",  # diel
            "ovalasi": "contains an attested part of four letters or more",  # valas, meaning unknown
            "orel": "is inside an attested form",  # shorel
            "fada": "Titan or Zandali form", "nobu": "scrambler word", "shari": "scrambler word",
            "nubi": "lexicon word",
        }
        for word, why in cases.items():
            self.assertEqual(inv.reject(word), why, word)
        self.assertEqual(inv.reject("vemon", ["vemor"]), "another new word")
        self.assertIsNone(inv.reject("vemon"))

    def test_a_short_word_is_only_rejected_when_equal(self):
        inv = inventory()
        self.assertIsNone(inv.reject("ves"))
        self.assertEqual(inv.reject("ves", ["ves"]), "another new word")
        self.assertIsNone(inv.reject("ves", ["vas"]))

    def test_english_name_parts_are_not_learned_but_still_block(self):
        forms = [{"form": "Maiev Shadowsong", "branch": "ancient-name"}]
        inv = inventory(forms=forms)
        self.assertIn("maiev", inv.train)
        self.assertNotIn("shadowsong", inv.train)
        self.assertEqual(inv.reject("shadowson"), "attested form")

    def test_generated_and_unverified_entries_are_not_learned(self):
        inv = inventory([entry("thalas"), entry("nubu", "generated", "generated"), entry("delar", "thalassian",
                                                                                          "unverified")])
        self.assertEqual(inv.train, ["thalas"])


class TestChoose(unittest.TestCase):
    def setUp(self):
        self.inv = inventory(alphabet="".join(TRAIN))
        self.model = g.KneserNey(self.inv.train)
        self.yardstick = g.loo_scores(self.inv.train)

    def test_choice_is_deterministic_in_range_and_passes_the_filters(self):
        a = g.choose("water", "content", self.model, self.inv, [], self.yardstick, samples=800)
        b = g.choose("water", "content", self.model, self.inv, [], self.yardstick, samples=800)
        self.assertEqual(a, b)
        self.assertTrue(3 <= len(a["word"]) <= 7)
        self.assertIsNone(self.inv.reject(a["word"]))
        self.assertEqual(a["seed"], g.seed_for("water"))

    def test_choice_is_the_best_scoring_valid_sample_of_its_length(self):
        c = g.choose("fire", "content", self.model, self.inv, [], self.yardstick, samples=800)
        rng = random.Random(g.seed_for("fire"))
        rng.choices([0], [1])  # the length draw
        same_length = set()
        for _ in range(800):
            w = self.model.sample(rng)
            if w and len(w) == len(c["word"]) and self.inv.reject(w) is None:
                same_length.add(w)
        self.assertEqual(c["word"], max(same_length, key=lambda w: (self.model.score(w), w)))

    def test_a_taken_word_is_not_chosen_again(self):
        first = g.choose("salt", "content", self.model, self.inv, [], self.yardstick, samples=800)["word"]
        second = g.choose("salt", "content", self.model, self.inv, [first], self.yardstick, samples=800)["word"]
        self.assertNotEqual(first, second)
        self.assertIsNone(g.near(second, {first}))


class TestCommittedCandidates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(g.OUT, encoding="utf-8") as fh:
            cls.candidates = json.load(fh)

    def drawn(self):
        """(meaning, form, candidate) for every form the model drew."""
        for c in self.candidates:
            if c.get("score") is None:
                continue
            if c["action"] == "regenerate":
                yield c["meaning"], c["new"], c
            else:
                label = next((m for n, m, *_ in g.SWADESH_ADDS if n == c.get("swadesh")),
                             g.REPLACE_UNVERIFIED.get("isera", (None, None))[1])
                yield label, c["word"], c

    def test_every_action_is_known_and_has_a_reason_and_confidence(self):
        for c in self.candidates:
            self.assertIn(c["action"], ("remove", "fix", "note", "regenerate", "add"), c["word"])
            self.assertIn(c["confidence"], ("high", "medium", "low"), c["word"])
            self.assertTrue(c["reason"], c["word"])
            self.assertIsInstance(c["evidence"], list, c["word"])

    def test_drawn_forms_name_their_seed_and_keep_the_rules(self):
        forms = []
        for meaning, form, c in self.drawn():
            forms.append(form)
            self.assertIn(f"seed {g.seed_for(meaning)} (SHA-256 of '{meaning}')", c["method"], form)
            function = (c["action"] == "regenerate" and c["word"] in g.FUNCTION_WORDS) or any(
                n == c.get("swadesh") and kind == "function" for n, *_, kind in g.SWADESH_ADDS)
            lo, hi = g.LENGTHS["function" if function else "content"]
            self.assertTrue(lo <= len(form) <= hi, form)
            self.assertTrue(re.fullmatch(r"[a-z]+", form), form)
            self.assertFalse(form.endswith(("is", "ael")), form)
            self.assertTrue(g.phonotactic(form), form)
            self.assertNotIn(form, g.FOREIGN, form)
            self.assertFalse(set(form) & set("qxc"), form)
        self.assertEqual(len(forms), len(set(forms)))
        for i, a in enumerate(forms):
            for b in forms[i + 1:]:
                self.assertIsNone(g.near(a, {b}), (a, b))

    def test_every_missing_swadesh_meaning_gets_one_add(self):
        items = Counter(c.get("swadesh") for c in self.candidates if c["action"] == "add" and c["confidence"] != "low")
        self.assertEqual(set(items.values()), {1})
        expected = {n for n, *_ in g.SWADESH_ADDS} | {3, 173}  # he ('dan) and green (isera's replacement)
        self.assertEqual({n for n in items if n}, expected)

    def test_the_decisions(self):
        by = {(c["action"], c["word"]): c for c in self.candidates}
        for word in ("on", "il'ore", "al'ore", "nath", "isera"):
            self.assertIn(("remove", word), by)
        self.assertNotIn(("regenerate", "on"), by)
        self.assertEqual(by[("add", "mal")]["confidence"], "low")
        self.assertEqual(by[("fix", "la")]["new"], "particle")
        self.assertIn(("add", "'a"), by)
        self.assertIn(("add", "'dan"), by)
        ore = by[("regenerate", "ore")]["new"]
        self.assertEqual(by[("regenerate", "thas'ore")]["new"], f"thas'{ore}")


if __name__ == "__main__":
    unittest.main()
