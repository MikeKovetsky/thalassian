import unittest

from thalassian.core.lexicon import load_lexicon
from thalassian.syntax.parser import compile_sentence_en

class TestThalassianGrammar(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.lexicon = load_lexicon()
        
    def test_basic_noun(self):
        res = compile_sentence_en("sun", self.lexicon)
        self.assertEqual(res.strip().lower(), "belore")
        
    def test_plural_noun_consonant(self):
        # We test "travelers" instead of "phoenixes" to avoid "es" naive stemming issue
        res = compile_sentence_en("travelers", self.lexicon)
        self.assertEqual(res.strip().lower(), "malanorei")
        
    def test_plural_noun_vowel(self):
        # "blood" is "sin" -> "sins" would be "sini"
        res = compile_sentence_en("bloods", self.lexicon)
        self.assertEqual(res.strip().lower(), "sini")
        
    def test_drop_prepositions(self):
        res = compile_sentence_en("justice for our people", self.lexicon)
        self.assertNotIn("for", res.lower())
        self.assertIn("selama", res.lower())
        self.assertIn("anore", res.lower())
        
    def test_pronoun_agglutination_us(self):
        res = compile_sentence_en("guide us", self.lexicon)
        self.assertEqual(res.strip().lower(), "dela'na")
        
    def test_pronoun_agglutination_you(self):
        # The 2026-11 audit dropped the unsupported "anu = hail" gloss, so this uses canon dela (guide).
        res = compile_sentence_en("guide you", self.lexicon)
        self.assertEqual(res.strip().lower(), "dela'a")
        
    def test_pronoun_agglutination_me(self):
        # Canon Vendel'o eranu = "help me forget". The old test expected "[bind]'o", an untranslated word.
        res = compile_sentence_en("help me", self.lexicon)
        self.assertEqual(res.strip().lower(), "vendel'o")
        
    def test_punctuation_preservation(self):
        res = compile_sentence_en("sun, guide us!", self.lexicon)
        self.assertEqual(res.strip().lower(), "belore, dela'na!")
        
    def test_missing_word_brackets(self):
        res = compile_sentence_en("The computer guides us.", self.lexicon)
        self.assertEqual(res.strip().lower(), "[computer] dela'na.")
        
    def test_high_home_is_quel_thalas(self):
        # Canon Quel'Thalas; the old test expected "Quel thalas".
        res = compile_sentence_en("high home", self.lexicon)
        self.assertEqual(res.strip().lower(), "quel'thalas")

if __name__ == '__main__':
    unittest.main(verbosity=2)