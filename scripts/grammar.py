import json
import os
import re

def load_lexicon():
    path = os.path.join(os.path.dirname(__file__), '../data/lexicon.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_word(lexicon, target_uk):
    target_uk = target_uk.lower()
    for entry in lexicon:
        # Check if it's an exact word in the translation string
        uk_words = re.findall(r'[а-яєіїґ\']+', entry["translation"]["uk"].lower())
        if target_uk in uk_words:
            return entry
    return None

def apply_plural(word):
    if word.endswith('e'):
        return word + "i" # dore -> dorei (simplified)
    elif word.endswith(('a', 'o', 'u')):
        return word[:-1] + "ei" # sindo -> sindorei
    return word + "i" # alar -> alari

def compile_sentence(uk_sentence, lexicon):
    words = re.findall(r'[А-Яа-яЄєІіЇїҐґ\']+', uk_sentence)
    translated = []
    
    for word in words:
        is_plural = False
        search_word = word.lower()
        
        # Naive Ukrainian stemming for demo purposes
        if search_word.endswith(('и', 'і', 'ї')) and len(search_word) > 2:
            is_plural = True
            search_word = search_word[:-1]
            
        found = find_word(lexicon, search_word)
        if not found and is_plural:
            # Maybe the word wasn't plural in ukrainian, try the original word
            found = find_word(lexicon, word.lower())
            
        if found:
            elven_word = found["word"]
            if is_plural and found["pos"] == "noun":
                elven_word = apply_plural(elven_word)
            translated.append(elven_word.capitalize())
        else:
            translated.append(f"[{word}]")
            
    return " ".join(translated)

if __name__ == "__main__":
    lexicon = load_lexicon()
    
    test_cases = [
        "Сонце",
        "Фенікс",
        "Фенікси",
        "Магія і вогонь",
        "Кров мандрівника",
        "Справедливість для народу"
    ]
    
    print("--- Grammar Compiler V1 Test ---")
    for sentence in test_cases:
        elven = compile_sentence(sentence, lexicon)
        print(f"UK: {sentence}")
        print(f"TH: {elven}\n")
