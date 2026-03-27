def apply_plural(word: str) -> str:
    """Applies Thalassian pluralization rules to a given word."""
    if word.endswith('e'):
        return word + "i"
    elif word.endswith(('a', 'o', 'u')):
        return word[:-1] + "ei"
    return word + "i"
