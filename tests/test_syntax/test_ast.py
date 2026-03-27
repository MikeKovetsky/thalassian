import unittest
from thalassian.core.lexicon import load_lexicon
from thalassian.syntax.parser import compile_sentence_en

class TestThalassianAST(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lexicon = load_lexicon()
        
    def test_basic_noun(self):
        res = compile_sentence_en("sun", self.lexicon)
        self.assertEqual(res.strip().lower(), "belore")
        
    def test_pronoun_agglutination_us(self):
        res = compile_sentence_en("guide us", self.lexicon)
        self.assertEqual(res.strip().lower(), "dela'na")
        
    def test_punctuation_preservation(self):
        res = compile_sentence_en("sun, guide us!", self.lexicon)
        self.assertEqual(res.strip().lower(), "belore, dela'na!")
        
    def test_drop_prepositions(self):
        res = compile_sentence_en("justice for our people", self.lexicon)
        self.assertNotIn("for", res.lower())
        self.assertIn("selama", res.lower())
        self.assertIn("anore", res.lower())

if __name__ == '__main__':
    unittest.main()
