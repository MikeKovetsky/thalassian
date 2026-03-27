PRONOUN_SUFFIXES_EN = {
    "us": "na", "we": "anu", 
    "you": "a", 
    "i": "o", "me": "o", 
    "them": "dan", "they": "danu"
}

PRONOUN_SUFFIXES_UK = {
    "ми": "na", "ти": "a", "я": "o", "вони": "dan"
}

def get_pronoun_suffix(lemma: str, language: str = "en") -> str:
    """Returns the Thalassian agglutinative suffix for a pronoun lemma."""
    if language == "en":
        return PRONOUN_SUFFIXES_EN.get(lemma)
    elif language == "uk":
        return PRONOUN_SUFFIXES_UK.get(lemma)
    return None
