"""Pronouns, per docs/methodology/grammar.md section 5.

One form serves every role. After a verb it is an object clitic joined by an apostrophe ("guide us" ->
dela'na); anywhere else it is a free word ("we" -> na). 'na (us) and 'o (me) are canon; 'a (you) and 'dan
(him, her, it, them) are the project's invention. anu is a wish particle, not "we", and there is no
separate "they" (grammar 2.5 and 5.3). The English and Ukrainian tables cover the same persons, the
Ukrainian ones in every case, and web/translator.js holds the same tables.
"""
PRONOUN_FORMS_EN = {
    "we": "na", "us": "na",
    "i": "o", "me": "o",
    "you": "a",
    "he": "dan", "she": "dan", "it": "dan", "they": "dan", "him": "dan", "her": "dan", "them": "dan",
}

PRONOUN_FORMS_UK = {
    "ми": "na", "нас": "na", "нам": "na", "нами": "na",
    "я": "o", "мене": "o", "мені": "o", "мною": "o",
    "ти": "a", "тебе": "a", "тобі": "a", "тобою": "a", "ви": "a", "вас": "a", "вам": "a", "вами": "a",
    "він": "dan", "вона": "dan", "воно": "dan", "вони": "dan", "його": "dan", "її": "dan", "їх": "dan",
    "йому": "dan", "їй": "dan", "їм": "dan", "ним": "dan", "нею": "dan", "ними": "dan", "нього": "dan",
    "неї": "dan", "них": "dan", "ньому": "dan", "ній": "dan",
}

# A subject is a free word before its verb (grammar 5.3), so these subject forms never join the word before
# them: "then we guide them" is [then] na dela'dan, not [then]'na.
SUBJECTS_EN = {"i", "we", "he", "she", "they"}
SUBJECTS_UK = {"я", "ми", "ти", "ви", "він", "вона", "воно", "вони"}

# Possessive determiners: (form, whether it comes before the noun). mal "your" comes first (canon: Elu'meniel
# mal alann, "may peace calm your heart"); na "our" follows the noun; o "my" and dan "his, her, its, their"
# follow it by analogy (invented). Darnassian dal "your" is not used. "yours", "ours", "hers" and "theirs"
# take the same forms ("mine" is left out, because it is also a noun).
POSSESSIVES_EN = {
    "your": ("mal", True), "yours": ("mal", True), "our": ("na", False), "ours": ("na", False),
    "my": ("o", False), "his": ("dan", False), "her": ("dan", False), "hers": ("dan", False),
    "its": ("dan", False), "their": ("dan", False), "theirs": ("dan", False),
}

POSSESSIVES_UK = {
    **dict.fromkeys(("твій", "твого", "твоєму", "твоїм", "твоя", "твоєї", "твоїй", "твою", "твоєю", "твоє", "твої",
                     "твоїх", "твоїми", "ваш", "вашого", "вашому", "вашим", "ваша", "вашої", "вашій", "вашу",
                     "вашою", "ваше", "ваші", "ваших", "вашими"), ("mal", True)),
    **dict.fromkeys(("наш", "нашого", "нашому", "нашим", "наша", "нашої", "нашій", "нашу", "нашою", "наше", "наші",
                     "наших", "нашими"), ("na", False)),
    **dict.fromkeys(("мій", "мого", "моєму", "моїм", "моя", "моєї", "моїй", "мою", "моєю", "моє", "мої", "моїх",
                     "моїми"), ("o", False)),
    **dict.fromkeys(("його", "її", "їхній", "їхнього", "їхньому", "їхнім", "їхня", "їхньої", "їхню", "їхньою",
                     "їхнє", "їхні", "їхніх", "їхніми"), ("dan", False)),
}


def get_pronoun_suffix(lemma: str, language: str = "en") -> str:
    """The Thalassian form of a pronoun, or None."""
    return (PRONOUN_FORMS_EN if language == "en" else PRONOUN_FORMS_UK).get(lemma)
