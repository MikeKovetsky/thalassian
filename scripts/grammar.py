import json
import os
import re

def load_lexicon():
    path = os.path.join(os.path.dirname(__file__), '../data/lexicon.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Elvish Pronoun Suffixes (Canon/Extrapolated)
PRONOUN_SUFFIXES = {
    "нас": "na", "ми": "anu", "нам": "na",
    "ти": "a", "тобі": "a", "тебе": "a",
    "я": "o", "мені": "o", "мене": "o",
    "їх": "dan", "вони": "danu"
}

# Words to simply drop (No prepositions in Elvish)
DROP_WORDS = {"для", "в", "до", "на", "з", "за", "від", "про", "і", "та", "але"}

def find_word(lexicon, target_uk):
    target_uk = target_uk.lower()
    for entry in lexicon:
        uk_words = re.findall(r'[а-яєіїґ\']+', entry["translation"]["uk"].lower())
        if target_uk in uk_words:
            return entry
    return None

def apply_plural(word):
    if word.endswith('e'):
        return word + "i"
    elif word.endswith(('a', 'o', 'u')):
        return word[:-1] + "ei"
    return word + "i"

def compile_sentence(uk_sentence, lexicon):
    # Split sentence into words keeping punctuation separate
    tokens = re.findall(r'[А-Яа-яЄєІіЇїҐґ\']+|[.,!?;]', uk_sentence)
    
    translated_tokens = []
    i = 0
    while i < len(tokens):
        word = tokens[i]
        
        # Keep punctuation as is
        if re.match(r'[.,!?;]', word):
            if translated_tokens:
                translated_tokens[-1] += word
            i += 1
            continue
            
        lower_word = word.lower()
        
        # Rule 1: Drop prepositions/conjunctions
        if lower_word in DROP_WORDS:
            i += 1
            continue
            
        # Check if the NEXT word is a pronoun that needs to be agglutinated (suffix)
        suffix = ""
        if i + 1 < len(tokens):
            next_word = tokens[i+1].lower()
            if next_word in PRONOUN_SUFFIXES:
                suffix = "'" + PRONOUN_SUFFIXES[next_word]
                # We skip the next word since it's now a suffix
                i += 1
        
        # Look up current word
        is_plural = False
        search_word = lower_word
        
        if search_word.endswith(('и', 'і', 'ї')) and len(search_word) > 2:
            is_plural = True
            search_word = search_word[:-1]
            
        found = find_word(lexicon, search_word)
        if not found and is_plural:
            found = find_word(lexicon, lower_word)
            
        # Determine translation
        if found:
            elven_word = found["word"]
            if is_plural and found["pos"] == "noun":
                elven_word = apply_plural(elven_word)
            
            # Capitalize if it's the first word or start of sentence
            if len(translated_tokens) == 0 or translated_tokens[-1].endswith(('. ', '! ', '? ')):
                elven_word = elven_word.capitalize()
            elif not suffix:
                # Normal capitalization rules (just keep base case from DB unless starting)
                pass 
                
            # Rule 3: Adjectives combine with following nouns (if next is a noun)
            # For simplicity in V2, we just output it. True combining requires full parsing.
            
            translated_tokens.append(elven_word + suffix)
        else:
            # Word not in dictionary
            translated_tokens.append(f"[{word}]{suffix}")
            
        i += 1
        
    # Join with spaces, but fix punctuation spaces
    result = " ".join(translated_tokens)
    result = result.replace(" ,", ",").replace(" .", ".").replace(" !", "!").replace(" ?", "?")
    return result

if __name__ == "__main__":
    lexicon = load_lexicon()
    
    test_cases = [
        "Сонце веде нас.",
        "Смакуй холод справжньої смерті!",
        "Справедливість для нашого народу.",
        "Великий фенікс летить до нас.",
        "Сонце зігріває мене."
    ]
    
    print("--- Grammar Compiler V2 Test (Agglutinative Elvish) ---")
    for sentence in test_cases:
        elven = compile_sentence(sentence, lexicon)
        print(f"UK: {sentence}")
        print(f"TH: {elven.capitalize()}\n")
