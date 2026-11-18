"""Pronouns, per docs/methodology/grammar.md section 5.

One form serves every role. After a verb it is an object clitic joined by an apostrophe ("guide us" ->
dela'na); anywhere else it is a free word ("we" -> na). 'na (us) and 'o (me) are canon; 'a (you) and 'dan
(him, her, it, them) are the project's invention. anu is a wish particle, not "we", and there is no
separate "they" (grammar 2.5 and 5.3). The English and Ukrainian tables cover the same persons.
"""
PRONOUN_FORMS_EN = {
    "we": "na", "us": "na",
    "i": "o", "me": "o",
    "you": "a",
    "he": "dan", "she": "dan", "it": "dan", "they": "dan", "him": "dan", "her": "dan", "them": "dan",
}

PRONOUN_FORMS_UK = {
    "ми": "na", "нас": "na", "нам": "na",
    "я": "o", "мене": "o", "мені": "o",
    "ти": "a", "тебе": "a", "тобі": "a", "ви": "a", "вас": "a", "вам": "a",
    "він": "dan", "вона": "dan", "воно": "dan", "вони": "dan",
    "його": "dan", "її": "dan", "їх": "dan", "йому": "dan", "їй": "dan", "їм": "dan",
}

# Possessive determiners: (form, whether it comes before the noun). mal "your" comes first (canon: Elu'meniel
# mal alann, "may peace calm your heart"); na "our" follows the noun; o "my" and dan "his, her, its, their"
# follow it by analogy (invented). Darnassian dal "your" is not used.
POSSESSIVES_EN = {
    "your": ("mal", True), "our": ("na", False), "my": ("o", False),
    "his": ("dan", False), "her": ("dan", False), "its": ("dan", False), "their": ("dan", False),
}

POSSESSIVES_UK = {
    **dict.fromkeys(("твій", "твоя", "твоє", "твої", "ваш", "ваша", "ваше", "ваші"), ("mal", True)),
    **dict.fromkeys(("наш", "наша", "наше", "наші"), ("na", False)),
    **dict.fromkeys(("мій", "моя", "моє", "мої"), ("o", False)),
    **dict.fromkeys(("його", "її", "їхній", "їхня", "їхнє", "їхні"), ("dan", False)),
}


def get_pronoun_suffix(lemma: str, language: str = "en") -> str:
    """The Thalassian form of a pronoun, or None."""
    return (PRONOUN_FORMS_EN if language == "en" else PRONOUN_FORMS_UK).get(lemma)
