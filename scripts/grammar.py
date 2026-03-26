import json
import os
import re

def load_lexicon():
    path = os.path.join(os.path.dirname(__file__), '../data/lexicon.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_word(lexicon, target_uk):
    for entry in lexicon:
        if target_uk.lower() in entry["translation"]["uk"].lower():
            return entry
    return None

def apply_plural(word):
    if word.endswith(('a', 'e', 'o', 'u')):
        if word.endswith('e'):
            return word + "i" # dore -> dorei (simplified)
        return word[:-1] + "ei" # sindo -> sindorei
    return word + "i" # alar -> alari

def compile_sentence(uk_sentence, lexicon):
    words = re.findall(r'\b\w+\b', uk_sentence)
    translated = []
    
    for word in words:
        # Check for plural marker (very basic ukrainian heuristics for demo)
        is_plural = False
        base_word = word
        if word.endswith(('и', 'і', 'ї')) and len(word) > 2:
            is_plural = True
            base_word = word[:-1] # rudimentary stemming
            
        found = find_word(lexicon, base_word) or find_word(lexicon, word)
        
        if found:
            elven_word = found["word"]
            if is_plural and found["pos"] == "noun":
                elven_word = apply_plural(elven_word)
            translated.append(elven_word.capitalize())
        else:
            # Word not in dictionary, leave as is (wrapped in brackets)
            translated.append(f"[{word}]")
            
    return " ".join(translated)

if __name__ == "__main__":
    lexicon = load_lexicon()
    
    # Test sentences
    test_cases = [
        "Сонце",
        "Сонце веде",
        "Фенікс",
        "Фенікси",
        "Магія і вогонь",
        "Смерть мандрівник"
    ]
    
    print("--- Grammar Compiler Test ---")
    for sentence in test_cases:
        elven = compile_sentence(sentence, lexicon)
        print(f"UK: {sentence}")
        print(f"TH: {elven}\n")
