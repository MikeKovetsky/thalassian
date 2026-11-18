import io
import sys
import unittest
from contextlib import redirect_stdout
from unittest import mock

from thalassian.cli.main import main, single_forms


def run_cli(*args):
    out = io.StringIO()
    with mock.patch.object(sys, "argv", ["thalassian", *args]), redirect_stdout(out):
        main()
    return [line[2:] for line in out.getvalue().splitlines() if line.startswith("- ")]


class TestGenerators(unittest.TestCase):
    def test_single_forms_drop_phrases_and_split_composite_roots(self):
        self.assertEqual(single_forms(["al diel shala", "Bal'a", "anar + alah", "zephr + -as", "al + aketh (cf. Akir)"]),
                         ["bal'a", "anar", "alah", "zephr", "al"])

    def test_generated_roots_are_single_words(self):
        # The lexicon has canon phrases and composite roots; the chains must not learn spaces or '+'.
        roots = run_cli("generate-roots", "-n", "300")
        self.assertEqual(len(roots), 300)
        for root in roots:
            self.assertRegex(root, r"^[A-Za-z']+$")

    def test_generated_words_are_single_words(self):
        words = run_cli("generate-words", "-n", "100")
        self.assertTrue(words)
        for word in words:
            self.assertRegex(word, r"^[A-Za-z']+$")


if __name__ == "__main__":
    unittest.main()
