import unittest

from thalassian.core.lexicon import load_lexicon
from thalassian.syntax.parser import find_word_en, find_word_uk, gloss_senses, gloss_words


class TestGlossProper(unittest.TestCase):
    def test_parenthesis_holding_a_semicolon_is_commentary(self):
        # The parenthesis has to go before the ';' split, or "(title ...;" leaks into the gloss.
        self.assertEqual(gloss_senses("the Veiled One (title of the masked leader; rebel battle cry)"),
                         ["the veiled one"])
        self.assertEqual(gloss_words("(invocation/blessing particle; exact meaning unknown)", r"[a-z']+"), [])

    def test_text_after_semicolon_is_commentary(self):
        self.assertEqual(gloss_senses("children of noble birth; high elves"), ["children of noble birth"])
        self.assertEqual(gloss_senses("guide/lead, show"), ["guide", "lead", "show"])


class TestWordLookup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lexicon = load_lexicon()

    def word_for(self, english):
        found = find_word_en(self.lexicon, english)
        return found["word"] if found else None

    def test_commentary_words_find_nothing(self):
        # Words that occur only in the commentary of shal'nan ("title of the masked first leader")
        # and anu ("invocation/blessing particle; exact meaning unknown").
        for english in ("leader", "title", "masked", "blessing", "particle"):
            self.assertNotIn(self.word_for(english), ("shal'nan", "anu"), english)

    def test_commentary_words_find_nothing_uk(self):
        found = find_word_uk(self.lexicon, "частка")  # "particle", inside anu's parenthesized uk gloss
        self.assertNotEqual(found and found["word"], "anu")

    def test_exact_sense_beats_a_mention(self):
        # "light" is the whole sense of Thalassian alah; other entries only mention it.
        self.assertEqual(self.word_for("light"), "alah")

    def test_phrases_are_not_used_word_by_word(self):
        # "breaking" occurs only in the glosses of the phrase "shindu fallah na".
        word = self.word_for("breaking")
        self.assertTrue(word is None or " " not in word, word)


if __name__ == "__main__":
    unittest.main()
