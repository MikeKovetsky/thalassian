"""research/2026-11-revival/scripts/shared_core.py: how parts are split, matched and tiered."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "research", "2026-11-revival", "scripts"))
import shared_core  # noqa: E402


def form(text, branch):
    return {"form": text, "branch": branch}


class TestParts(unittest.TestCase):
    def test_splits_at_apostrophes_hyphens_and_spaces_and_drops_short_parts(self):
        self.assertEqual(shared_core.parts("Ba'anthalso-dorei!"), ["anthalso", "dorei"])
        self.assertEqual(shared_core.parts("Zin-Azshari adore."), ["zin", "azshari", "adore"])


class TestWitnesses(unittest.TestCase):
    def test_a_solid_compound_counts_only_when_both_halves_are_known(self):
        found = shared_core.witnesses([form("kaldorei", "darnassian"), form("kal", "darnassian"),
                                       form("sin'dorei", "thalassian"), form("dorah", "thalassian")])
        self.assertEqual(found["dorei"]["darnassian"]["inside"], {"kaldorei"})
        # "dora" is not a known part, so dorah gives nothing to anything.
        self.assertNotIn("dora", found)


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


if __name__ == "__main__":
    unittest.main()
