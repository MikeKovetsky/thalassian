"""Both translators against the canon: report 1's bugs 1-4 and 12, and the 39 official Thalassian phrases as
gold. The Python engine is src/thalassian/syntax/parser.py; the web engine is web/translator.js, run under node.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "research", "2026-11-revival", "scripts"))
import evaltranslator as E  # noqa: E402

from thalassian.core.lexicon import load_lexicon  # noqa: E402
from thalassian.syntax.parser import compile_sentence_uk  # noqa: E402

PHRASES = [p for p, _ in E.GOLD]
GLOSSES = [g for _, g in E.GOLD]
# Word by word (phrasebook off), the rules alone must still give these canon forms.
RULE_GOLD = {
    "Children of the blood": "Sin'dorei", "Children of the void": "Ren'dorei",
    "Light of the forest": "Thas'alah", "Valor of the forest": "Thas'dorah",
    "Failing children of the blood": "Shindu sin'dorei",
    "By the light": "Anar'alah", "By the light of the sun": "Anar'alah belore",
    "By the breath of the dragon": "Anar'endal dracon", "And": "Rea", "Gate keeper": "Ban'dinoriel",
}


class EngineCases:
    """The same cases for both engines. A subclass sets translate(inputs, phrasebook)."""

    def tr(self, text, phrasebook=True):
        return self.translate([text], phrasebook)[0]

    def test_and_and_by_are_not_dropped(self):
        # Bug 1: canon rea (and) and anar (by).
        self.assertEqual(self.translate(["and", "the sun and the forest", "by"]), ["Rea", "Belore rea thas", "Anar"])

    def test_lookup_prefers_canon(self):
        # Bug 2: keeper was delar (unverified) before dinoriel (segment); you was Darnassian alah.
        self.assertEqual(self.tr("keeper"), "Dinoriel")
        self.assertNotIn(self.tr("you").lower(), ("alah", "isil"))

    def test_pronoun_after_a_dropped_word_is_kept(self):
        # Bug 3: "Justice for you" lost its "you".
        self.assertEqual(self.tr("Justice for you"), "Selama " + self.tr("you").lower())

    def test_modifier_comes_first_in_compounds(self):
        # Bug 4: "children of the blood" was "Dorei sin".
        outputs = self.translate(list(RULE_GOLD), phrasebook=False)
        for (english, canon), out in zip(RULE_GOLD.items(), outputs):
            self.assertEqual(E.words(out), E.words(canon), english)

    def test_of_before_a_longer_phrase_stays_a_free_genitive(self):
        # Canon falor talah, "the chill of true death": head first.
        self.assertEqual(self.tr("taste the chill of true death", phrasebook=False), "Bash'a falor [true] talah")

    def test_compound_needs_a_noun_head(self):
        # anaria (speak) is a verb, so "speak of the sun" is not a compound.
        self.assertEqual(self.tr("speak of the sun", phrasebook=False), "Anaria belore")

    def test_phrasebook_takes_the_longest_span_over_commas_and_contractions(self):
        self.assertEqual(self.translate(["The sun guides us.", "Greetings, traveler", "They're breaking through!"]),
                         ["Anu belore dela'na.", "Bal'a dash, malanore", "Shindu fallah na!"])

    def test_phrasebook_reproduces_every_canon_phrase(self):
        for phrase, gloss, out in zip(PHRASES, GLOSSES, self.translate(GLOSSES)):
            self.assertEqual(E.words(out), E.words(phrase), gloss)

    def test_word_by_word_score_does_not_regress(self):
        # 20 of 39 exact on 2026-11-18, against 9 before the fix (which had no phrasebook).
        exact, _ = E.score(list(zip(PHRASES, self.translate(GLOSSES, phrasebook=False))))
        self.assertGreaterEqual(exact, 20)


class TestPythonEngine(EngineCases, unittest.TestCase):
    def translate(self, inputs, phrasebook=True):
        return E.python_translate(inputs, phrasebook)

    def test_ukrainian_and_and_kept_pronoun(self):
        lexicon = load_lexicon()
        self.assertEqual(compile_sentence_uk("сонце і ліс", lexicon), "Belore rea thas")
        self.assertEqual(compile_sentence_uk("справедливість для тебе", lexicon),
                         "Selama " + compile_sentence_uk("ти", lexicon).lower())


@unittest.skipUnless(E.NODE, "node is not installed")
class TestWebEngine(EngineCases, unittest.TestCase):
    def translate(self, inputs, phrasebook=True):
        return E.web_translate(inputs, phrasebook=phrasebook)

    def reverse(self, inputs, **options):
        return E.web_translate(inputs, "reverse", **options)

    def test_words_named_like_object_properties(self):
        # "constructor" once found Object.prototype.constructor in the pronoun tables.
        self.assertEqual(self.translate(["guide constructor"]), ["Dela [constructor]"])
        self.assertEqual(self.reverse(["zzz'constructor"]), ["[zzz] [constructor]"])

    def test_reverse_looks_up_whole_words_before_splitting(self):
        # Bug 12: every word was split at its apostrophes, so Bal'a became "[bal] you".
        self.assertEqual(self.reverse(["Bal'a", "Shal'na", "Bash'a", "Anar'alah", "Belore dela'na"]),
                         ["greetings", "aunt", "taste", "by the Light", "sun guide us"])

    def test_reverse_reads_curly_and_quoted_apostrophes(self):
        # Phones type ’; quote marks around a word are not part of it; 'o (me) keeps its apostrophe.
        self.assertEqual(self.reverse(["Bal’a", "'Bal'a'", "Anar’alah belore", "'Bal'a dash, malanore'", "Selama 'o"]),
                         ["greetings", "greetings", "by the light of the sun", "greetings, traveler", "justice me"])

    def test_reverse_matches_whole_phrases_first(self):
        self.assertEqual(self.reverse(["Bal'a dash, malanore!", "Al diel shala", "Doral ana'diel?"]),
                         ["greetings, traveler!", "safe travels", "how fare you?"])

    def test_reverse_canon_only_skips_generated_words(self):
        self.assertEqual(self.reverse(["la"], canonOnly=True), ["[la]"])
        self.assertNotEqual(self.reverse(["la"]), ["[la]"])

    def test_reverse_reads_every_canon_phrase(self):
        outputs = self.reverse(PHRASES)
        self.assertFalse([o for o in outputs if "[" in o])
        exact, _ = E.score(list(zip(GLOSSES, outputs)))
        self.assertGreaterEqual(exact, 32)  # 6 of 39 before the fix


if __name__ == "__main__":
    unittest.main()
