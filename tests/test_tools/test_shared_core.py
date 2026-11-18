"""research/2026-11-revival/scripts/shared_core.py: how parts are split, matched and tiered."""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "research", "2026-11-revival", "scripts"))
import shared_core  # noqa: E402


def form(text, branch):
    return {"form": text, "branch": branch}


class TestParts(unittest.TestCase):
    def test_splits_at_apostrophes_hyphens_and_spaces_and_drops_short_parts(self):
        self.assertEqual(shared_core.parts("Ba'anthalso-dorei!"), ["anthalso", "dorei"])
        self.assertEqual(shared_core.parts("Zin-Azshari adore."), ["zin", "azshari", "adore"])
        self.assertEqual(shared_core.parts("Ash’toras denil"), ["ash", "toras", "denil"])


class TestLexiconForms(unittest.TestCase):
    def test_keeps_only_daughter_entries_that_are_not_generated_or_unverified(self):
        def entry(word, source, basis):
            return {"word": word, "source": source, "canon_basis": basis, "translation": {"en": word}}
        lexicon = [entry("kaldorei", "darnassian", "attested"), entry("shen", "skyborne", "inferred"),
                   entry("thala", "thalassian", "generated"), entry("anu", "thalassian", "unverified"),
                   entry("sorae", "generated", "generated"), entry("x", "extrapolated", "inferred")]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "lexicon.json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(lexicon, fh)
            forms = shared_core.lexicon_forms(path)
        self.assertEqual([(f["form"], f["branch"]) for f in forms], [("kaldorei", "darnassian"), ("shen", "skyborne")])


class TestWitnesses(unittest.TestCase):
    def test_a_solid_compound_counts_for_both_halves_when_both_are_known(self):
        found = shared_core.witnesses([form("kaldorei", "darnassian"), form("kal", "darnassian"),
                                       form("sin'dorei", "thalassian")])
        self.assertEqual(found["dorei"]["darnassian"]["inside"], {"kaldorei"})
        self.assertEqual(found["kal"]["darnassian"], {"exact": {"kal"}, "inside": {"kaldorei"}})

    def test_a_solid_compound_gives_nothing_when_one_half_is_unknown(self):
        found = shared_core.witnesses([form("kaldorei", "darnassian"), form("kal", "thalassian")])
        self.assertNotIn("dorei", found)
        self.assertEqual(sorted(found["kal"]), ["thalassian"])

    def test_the_last_split_leaves_a_tail_of_three_letters(self):
        found = shared_core.witnesses([form("aranal", "thalassian"), form("ara", "ancient-name"),
                                       form("nal", "darnassian")])
        self.assertEqual(found["nal"]["thalassian"]["inside"], {"aranal"})

    def test_a_word_in_two_daughters_counts_for_both(self):
        found = shared_core.witnesses([form("alah", "darnassian"), form("alah", "thalassian")])
        self.assertEqual(sorted(found["alah"]), ["darnassian", "thalassian"])


class TestCore(unittest.TestCase):
    def test_tiers(self):
        forms = [form("Sin'dorei", "thalassian"), form("Shal'dorei", "shalassian"), form("Shen'dorei", "skyborne"),
                 form("Elun'dris", "ancient-name"), form("Elune-adore", "darnassian"), form("dris", "darnassian"),
                 form("Elun'dris", "thalassian"), form("Azshara", "ancient-name")]
        tiers = {r["part"]: r["tier"] for r in shared_core.core(forms)}
        self.assertEqual(tiers["dorei"], 2)  # three daughters
        self.assertEqual(tiers["dris"], 1)  # before the Sundering, and two daughters
        self.assertEqual(tiers["azshara"], 3)  # before the Sundering only
        self.assertNotIn("shal", tiers)  # one daughter

    def test_a_phrase_quoted_in_several_daughters_counts_once(self):
        line = "Tor ilisar'thera'nal!"
        forms = [form("tor ilisar'thera'nal", "darnassian"), form(line, "shalassian"), form(line, "nazja"),
                 form(line, "ancient-speech")]
        found = shared_core.witnesses(forms)
        self.assertEqual(sorted(found["ilisar"]), ["ancient", "darnassian"])

    def test_a_control_never_counts_as_a_daughter(self):
        forms = [form("sin'dorei", "thalassian"), form("kal'dorei", "darnassian"), form("dorei", "zandali")]
        self.assertEqual(shared_core.core(forms), [])
        hits, total = shared_core.shared_rate(forms, "zandali")
        self.assertEqual((hits, total), (["dorei"], 1))

    def test_a_control_is_listed_apart_from_the_branches(self):
        forms = [form("sin'dorei", "thalassian"), form("shal'dorei", "shalassian"), form("shen'dorei", "skyborne"),
                 form("dorei", "zandali")]
        [row] = [r for r in shared_core.core(forms) if r["part"] == "dorei"]
        self.assertEqual(sorted(row["branches"]), ["shalassian", "skyborne", "thalassian"])
        self.assertEqual(row["controls"], ["zandali"])

    def test_a_daughter_is_not_counted_as_sharing_with_itself(self):
        forms = [form("dorei", "thalassian"), form("sin'dorei", "thalassian"), form("kal'dorei", "darnassian")]
        self.assertEqual(shared_core.shared_rate(forms, "thalassian"), ([], 2))
        forms.append(form("shal'dorei", "shalassian"))
        self.assertEqual(shared_core.shared_rate(forms, "thalassian"), (["dorei"], 2))


if __name__ == "__main__":
    unittest.main()
