"""Both translators against the canon: report 1's bugs 1-4 and 12, and the 39 official Thalassian phrases as
gold. The Python engine is src/thalassian/syntax/parser.py; the web engine is web/translator.js, run under node.
"""
import os
import sys
import unittest
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "research", "2026-11-revival", "scripts"))
import evaltranslator as E  # noqa: E402

from thalassian.core.lexicon import load_lexicon  # noqa: E402
from thalassian.syntax import parser  # noqa: E402
from thalassian.syntax.parser import compile_sentence_en, compile_sentence_uk  # noqa: E402

PHRASES = [p for p, _ in E.GOLD]
GLOSSES = [g for _, g in E.GOLD]
# Word by word (phrasebook off), the rules alone must still give these canon forms, apostrophes included.
RULE_GOLD = {
    "Children of the blood": "Sin'dorei", "Children of the void": "Ren'dorei",
    "Light of the forest": "Thas'alah", "Valor of the forest": "Thas'dorah",
    "Failing children of the blood": "Shindu sin'dorei",
    "By the light": "Anar'alah", "By the light of the sun": "Anar'alah belore",
    "By the breath of the dragon": "Anar'endal dracon", "And": "Rea",
}
# The glosses both engines reproduce word by word on 2026-11-18 (9 before the fix, which had no phrasebook).
# "Exact" compares words, as E.score does, so "Ban dinoriel" counts for Ban'dinoriel.
WORD_BY_WORD_EXACT = [
    "Ranger Lord", "By the light", "By the light of the sun", "By the breath of the dragon", "Father", "Rise",
    "Gate keeper", "The sun", "Flame strike", "Mother", "High home", "And", "Children of the void", "Aunt",
    "Failing children of the blood", "Farewell", "Children of the blood", "Light of the forest",
    "Valor of the forest", "Help me forget",
]


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

    def test_function_words_take_no_pronoun_suffix(self):
        # "and you" is not rea'a, and "by you" is not anar'a.
        self.assertEqual([out.split()[0] for out in self.translate(["and you", "by you"])], ["Rea", "Anar"])

    def test_modifier_comes_first_in_compounds(self):
        # Bug 4: "children of the blood" was "Dorei sin".
        self.assertEqual(self.translate(list(RULE_GOLD), phrasebook=False), list(RULE_GOLD.values()))

    def test_compound_ends_before_a_verb(self):
        # A verb after Y does not make the "of" phrase longer. "children of the sun" is not in the
        # phrasebook (Belore'dorei is glossed "child of the sun"), so the rules build it either way.
        self.assertEqual(self.tr("The children of the blood guide us", phrasebook=False), "Sin'dorei dela'na")
        self.assertEqual(self.tr("The children of the sun rise"), "Belore'dorei aranal")

    def test_of_before_a_longer_phrase_stays_a_free_genitive(self):
        # Canon falor talah, "the chill of true death", and Ann'da anore, "father of our people": head first.
        self.assertEqual(self.translate(["taste the chill of true death", "father of our people"], phrasebook=False),
                         ["Bash'a falor [true] talah", "Ann'da na anore"])

    def test_compound_needs_a_noun_head(self):
        # anaria (speak) is a verb, so "speak of the sun" is not a compound.
        self.assertEqual(self.tr("speak of the sun", phrasebook=False), "Anaria belore")

    def test_phrasebook_takes_the_longest_span_over_commas_and_contractions(self):
        self.assertEqual(self.translate(["The sun guides us.", "Greetings, traveler", "They're breaking through!",
                                         "They’re breaking through", "those who remain hidden"]),
                         ["Anu belore dela'na.", "Bal'a dash, malanore", "Shindu fallah na!", "Shindu fallah na",
                          "Shen'dralar"])

    def test_phrasebook_reproduces_every_canon_phrase(self):
        for phrase, gloss, out in zip(PHRASES, GLOSSES, self.translate(GLOSSES)):
            self.assertEqual(E.words(out), E.words(phrase), gloss)

    def test_word_by_word_score_does_not_regress(self):
        outputs = self.translate(GLOSSES, phrasebook=False)
        exact = [g for p, g, out in zip(PHRASES, GLOSSES, outputs) if E.words(out) == E.words(p)]
        self.assertEqual([g for g in WORD_BY_WORD_EXACT if g not in exact], [])


class TestPythonEngine(EngineCases, unittest.TestCase):
    def translate(self, inputs, phrasebook=True):
        return E.python_translate(inputs, phrasebook)

    def test_ukrainian_and_and_kept_pronoun(self):
        lexicon = load_lexicon()
        self.assertEqual(compile_sentence_uk("сонце і ліс", lexicon), "Belore rea thas")
        self.assertEqual(compile_sentence_uk("справедливість для тебе", lexicon),
                         "Selama " + compile_sentence_uk("ти", lexicon).lower())


class TestSpacyBuilder(unittest.TestCase):
    """With spaCy installed, the English builder takes spaCy's lemmas but must run the same passes. spaCy is
    not installed here, so a stand-in gives the lemmas and tags spaCy gives these words."""
    LEMMAS = {"guided": ("guide", "VBD", "VERB"), "us": ("we", "PRP", "PRON")}

    def nlp(self, text):
        tokens, start = [], 0
        for word in text.split(" "):
            lemma, tag, pos = self.LEMMAS.get(word.lower(), (word.lower(), "NN", "NOUN"))
            tokens.append(SimpleNamespace(text=word, idx=start, lemma_=lemma, tag_=tag, pos_=pos))
            start += len(word) + 1
        return tokens

    def test_spacy_lemmas_with_the_canon_passes(self):
        lexicon = load_lexicon()
        with mock.patch.object(parser, "nlp", self.nlp, create=True), mock.patch.object(parser, "USE_EN_NLP", True):
            self.assertEqual(compile_sentence_en("The sun guides us.", lexicon), "Anu belore dela'na.")
            # "guided" is dela only through spaCy's lemma; anar' and the compound are the regex builder's rules.
            self.assertEqual(compile_sentence_en("By the light of the forest guided us", lexicon, phrasebook=False),
                             "Anar'alah thas dela'na")
            self.assertEqual(compile_sentence_en("The light of the forest guided us", lexicon, phrasebook=False),
                             "Thas'alah dela'na")
        self.assertEqual(compile_sentence_en("guided us", lexicon), "[guided]'na")


@unittest.skipUnless(E.NODE, "node is not installed")
class TestWebEngine(EngineCases, unittest.TestCase):
    def translate(self, inputs, phrasebook=True, **options):
        return E.web_translate(inputs, phrasebook=phrasebook, **options)

    def reverse(self, inputs, **options):
        return E.web_translate(inputs, "reverse", **options)

    def test_canon_only_drops_inferred_phrases_and_words(self):
        # morin'aminor ("quiet serenity") and 'o ("me") are inferred; vendel'o eranu is attested.
        inputs = ["quiet serenity", "me", "help me forget"]
        self.assertEqual(self.translate(inputs), ["Morin'aminor", "'o", "Vendel'o eranu"])
        self.assertEqual(self.translate(inputs, canonOnly=True), ["[quiet] [serenity]", "[me]", "Vendel'o eranu"])

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
