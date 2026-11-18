"""Both translators against the canon: report 1's bugs 1-4 and 12, the rules of docs/methodology/grammar.md,
and the 39 official Thalassian phrases as gold. The Python engine is src/thalassian/syntax/parser.py; the web
engine is web/translator.js, run under node. No test expects output the canon contradicts.
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
from thalassian.morphology.agglutination import (  # noqa: E402
    PRONOUN_FORMS_EN, PRONOUN_FORMS_UK, POSSESSIVES_EN, POSSESSIVES_UK)

UKRAINIAN = ["сонце і ліс", "справедливість для тебе", "ми ведемо їх", "твоє серце", "я веду тебе"]
UKRAINIAN_GOLD = ["Belore rea thas", "Selama a", "Na [ведемо]'dan", "Mal alann", "O [веду]'a"]
PHRASES = [p for p, _ in E.GOLD]
GLOSSES = [g for _, g in E.GOLD]
# Word by word (phrasebook off), the rules alone must give these canon forms, apostrophes included. A name
# ("X of the Y", capitalized) is a compound, modifier first (grammar 3.3); any other "of" phrase puts the head
# first (3.4); "By", opening an oath, is anar' (7.2).
RULE_GOLD = {
    "Children of the Blood": "Sin'dorei", "Children of the Void": "Ren'dorei",
    "Light of the Forest": "Thas'alah", "Valor of the Forest": "Thas'dorah",
    "The light of the sun": "Alah belore", "The breath of the dragon": "Endal dracon",
    "The chill of death": "Falor talah",
    "By the light": "Anar'alah", "By the light of the sun": "Anar'alah belore",
    "By the breath of the dragon": "Anar'endal dracon", "And": "Rea",
}
# The glosses both engines reproduce word by word on 2026-11-18 (9 before the fix, which had no phrasebook).
# "Exact" compares words, as E.score does, so "Ban dinoriel" counts for Ban'dinoriel. The corpus writes
# "Children of the blood" in lower case, so word by word it is an ordinary phrase, dorei sin; the phrasebook
# gives the canon name.
WORD_BY_WORD_EXACT = [
    "Ranger Lord", "By the light", "By the light of the sun", "By the breath of the dragon", "Father", "Rise",
    "Gate keeper", "The sun", "Flame strike", "Mother", "High home", "And", "Aunt", "Farewell", "Help me forget",
]


class EngineCases:
    """The same cases for both engines. A subclass sets translate(inputs, phrasebook)."""

    def tr(self, text, phrasebook=True):
        return self.translate([text], phrasebook)[0]

    def test_and_is_rea(self):
        # Bug 1: canon rea (and) was dropped.
        self.assertEqual(self.translate(["and", "the sun and the forest"]), ["Rea", "Belore rea thas"])

    def test_by_is_anar_only_where_it_opens_an_oath(self):
        # Grammar 7.2: anar' is the "by" of oaths and invocations, a "By" that opens a clause. Any other "by" is
        # left out. The "by" of a passive is not anar': the canon line "Saved by magic" is Ama noral'arkhana,
        # which only the phrasebook gives.
        self.assertEqual(self.translate(["By the light", "We rise by the light", "Rise, by the light!", "by"],
                                        phrasebook=False),
                         ["Anar'alah", "Na aranal alah", "Aranal, anar'alah!", ""])
        self.assertEqual(self.tr("Saved by magic"), "Ama noral'arkhana")

    def test_lookup_prefers_canon(self):
        # Bug 2: keeper was delar (unverified) before dinoriel (segment).
        self.assertEqual(self.tr("keeper"), "Dinoriel")

    def test_pronoun_after_a_dropped_word_is_kept(self):
        # Bug 3: "Justice for you" lost its "you".
        self.assertEqual(self.tr("Justice for you"), "Selama a")

    def test_pronouns_follow_grammar_section_5(self):
        # Object pronouns join the verb; a subject pronoun is the same form as a free word before it. anu is a
        # wish particle and danu is gone, so neither is a pronoun.
        self.assertEqual(self.translate(["We guide them", "I guide you", "guide us", "help me", "guide her",
                                         "and you", "we", "they"]),
                         ["Na dela'dan", "O dela'a", "Dela'na", "Vendel'o", "Dela'dan", "Rea a", "Na", "Dan"])

    def test_possessives(self):
        # Grammar 5.2: Thalassian mal "your" before the noun (Mal alann), not Darnassian dal; na "our" after it.
        self.assertEqual(self.translate(["Your heart", "Our hearts", "guide her heart"]),
                         ["Mal alann", "Alann na", "Dela alann dan"])

    def test_nouns_have_no_plural(self):
        # Grammar 3.2: number is unmarked, so neither engine adds -i or -ei.
        self.assertEqual(self.translate(["The rangers guide us", "travels", "hearts"]),
                         ["Alar dela'na", "Shala", "Alann"])

    def test_of_phrases_put_the_head_first_and_names_compound(self):
        # Bug 4: "children of the blood" was "Dorei sin" even as a name; and canon alah belore, endal dracon
        # and falor talah put the head first.
        self.assertEqual(self.translate(list(RULE_GOLD), phrasebook=False), list(RULE_GOLD.values()))

    def test_name_ends_before_a_verb(self):
        # A verb after Y does not make the name longer. "the children of the sun" is not a name, and not in the
        # phrasebook (Belore'dorei is glossed "child of the sun"), so its head comes first.
        self.assertEqual(self.tr("The Children of the Blood guide us", phrasebook=False), "Sin'dorei dela'na")
        self.assertEqual(self.tr("The children of the sun rise"), "Dorei belore aranal")

    def test_compound_needs_a_noun_head(self):
        # anaria (speak) is a verb, so "Speak of the Sun" is not a name.
        self.assertEqual(self.tr("Speak of the Sun", phrasebook=False), "Anaria belore")

    def test_phrasebook_takes_the_longest_span_over_commas_and_contractions(self):
        self.assertEqual(self.translate(["The sun guides us.", "Greetings, traveler", "They're breaking through!",
                                         "They’re breaking through", "those who remain hidden"]),
                         ["Anu belore dela'na.", "Bal'a dash, malanore", "Shindu fallah na!", "Shindu fallah na",
                          "Shen'dralar"])

    def test_whole_phrase_fills_its_clause(self):
        # The clause-opening anu of Anu belore dela'na must not land mid-sentence.
        self.assertEqual(self.tr("The light of the sun guides us"), "Alah belore dela'na")

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
        self.assertEqual([compile_sentence_uk(s, lexicon) for s in UKRAINIAN], UKRAINIAN_GOLD)

    def test_english_and_ukrainian_pronouns_agree(self):
        self.assertEqual(set(PRONOUN_FORMS_EN.values()), set(PRONOUN_FORMS_UK.values()))
        self.assertEqual(set(POSSESSIVES_EN.values()), set(POSSESSIVES_UK.values()))
        self.assertNotIn("anu", set(PRONOUN_FORMS_EN.values()) | set(PRONOUN_FORMS_UK.values()))


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
            # "guided" is dela only through spaCy's lemma; anar', the names and the head-first "of" phrase are the
            # regex builder's rules.
            self.assertEqual(compile_sentence_en("By the light of the forest guided us", lexicon, phrasebook=False),
                             "Anar'alah thas dela'na")
            self.assertEqual(compile_sentence_en("The Light of the Forest guided us", lexicon, phrasebook=False),
                             "Thas'alah dela'na")
            self.assertEqual(compile_sentence_en("The light of the forest guided us", lexicon, phrasebook=False),
                             "Alah thas dela'na")
        self.assertEqual(compile_sentence_en("guided us", lexicon), "[guided]'na")


@unittest.skipUnless(E.NODE, "node is not installed")
class TestWebEngine(EngineCases, unittest.TestCase):
    def translate(self, inputs, phrasebook=True, **options):
        return E.web_translate(inputs, phrasebook=phrasebook, **options)

    def reverse(self, inputs, **options):
        return E.web_translate(inputs, "reverse", **options)

    def test_canon_only_drops_inferred_phrases_and_words(self):
        # morin'aminor ("quiet serenity") and dorah ("valor") are inferred; vendel'o eranu is attested.
        inputs = ["quiet serenity", "valor", "help me forget"]
        self.assertEqual(self.translate(inputs), ["Morin'aminor", "Dorah", "Vendel'o eranu"])
        self.assertEqual(self.translate(inputs, canonOnly=True), ["[quiet] [serenity]", "[valor]", "Vendel'o eranu"])

    def test_ukrainian_matches_the_python_engine(self):
        self.assertEqual(self.translate(UKRAINIAN), UKRAINIAN_GOLD)

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

    def test_reverse_reads_pronouns_and_no_plural(self):
        # The free pronouns and mal are not lexicon entries; a noun has no plural form to undo.
        self.assertEqual(self.reverse(["O dela'a", "Mal alann", "Na dela'dan", "doreii"]),
                         ["I/me/my guide you", "your heart", "us/our guide him/her/it/them", "[doreii]"])

    def test_reverse_matches_whole_phrases_first(self):
        self.assertEqual(self.reverse(["Bal'a dash, malanore!", "Al diel shala", "Doral ana'diel?"]),
                         ["greetings, traveler!", "safe travels", "how fare you?"])

    def test_reverse_canon_only_skips_generated_words(self):
        # Any one-word generated entry; the vocabulary audit may replace the generated words.
        word = next(e["word"] for e in load_lexicon() if e.get("canon_basis") == "generated"
                    and e["word"].isalpha() and e["word"] not in ("o", "a", "dan", "mal"))
        self.assertEqual(self.reverse([word], canonOnly=True), [f"[{word}]"])
        self.assertNotEqual(self.reverse([word]), [f"[{word}]"])

    def test_reverse_reads_every_canon_phrase(self):
        outputs = self.reverse(PHRASES)
        self.assertFalse([o for o in outputs if "[" in o])
        exact, _ = E.score(list(zip(GLOSSES, outputs)))
        self.assertGreaterEqual(exact, 32)  # 6 of 39 before the fix


if __name__ == "__main__":
    unittest.main()
