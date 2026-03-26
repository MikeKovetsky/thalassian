import json
import os
import re

# Try to import pymorphy3 for Ukrainian NLP
try:
    import pymorphy3
    # Require ukrainian dicts installed: pip install pymorphy3-dicts-uk
    morph = pymorphy3.MorphAnalyzer(lang='uk')
    USE_NLP = True
except ImportError:
    USE_NLP = False

def load_lexicon():
    path = os.path.join(os.path.dirname(__file__), '../data/lexicon.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

PRONOUN_SUFFIXES = {
    "ми": "na", "ти": "a", "я": "o", "вони": "dan"
}
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
    tokens = re.findall(r'[А-Яа-яЄєІіЇїҐґ\']+|[.,!?;]', uk_sentence)
    
    translated_tokens = []
    i = 0
    while i < len(tokens):
        word = tokens[i]
        
        if re.match(r'[.,!?;]', word):
            if translated_tokens:
                translated_tokens[-1] += word
            i += 1
            continue
            
        lower_word = word.lower()
        lemma = lower_word
        is_plural = False
        is_pronoun = False
        
        if USE_NLP:
            parsed = morph.parse(lower_word)[0]
            lemma = parsed.normal_form
            if 'plur' in parsed.tag:
                is_plural = True
            if 'NPRO' in parsed.tag:
                is_pronoun = True
        else:
            # Fallback naive logic
            if lower_word in ["нас", "нам", "ми"]: lemma = "ми"; is_pronoun = True
            elif lower_word in ["мене", "мені", "я"]: lemma = "я"; is_pronoun = True
            elif lower_word in ["тебе", "тобі", "ти"]: lemma = "ти"; is_pronoun = True
            elif lower_word.endswith(('и', 'і', 'ї')) and len(lower_word) > 2:
                is_plural = True
                lemma = lower_word[:-1]

        if lemma in DROP_WORDS or lower_word in DROP_WORDS:
            i += 1
            continue
            
        suffix = ""
        # Look ahead for pronouns to agglutinate
        if i + 1 < len(tokens):
            next_word = tokens[i+1].lower()
            next_lemma = next_word
            if USE_NLP:
                next_parsed = morph.parse(next_word)[0]
                next_lemma = next_parsed.normal_form
            else:
                if next_word in ["нас", "нам", "ми"]: next_lemma = "ми"
                elif next_word in ["мене", "мені", "я"]: next_lemma = "я"
                elif next_word in ["тебе", "тобі", "ти"]: next_lemma = "ти"
                
            if next_lemma in PRONOUN_SUFFIXES:
                suffix = "'" + PRONOUN_SUFFIXES[next_lemma]
                i += 1 # skip next word
                
        found = find_word(lexicon, lemma)
        if not found and not USE_NLP and is_plural:
            found = find_word(lexicon, lower_word)
            
        if found:
            elven_word = found["word"]
            if is_plural and found["pos"] == "noun":
                elven_word = apply_plural(elven_word)
            
            if len(translated_tokens) == 0 or translated_tokens[-1].endswith(('. ', '! ', '? ')):
                elven_word = elven_word.capitalize()
                
            translated_tokens.append(elven_word + suffix)
        else:
            translated_tokens.append(f"[{word}]{suffix}")
            
        i += 1
        
    result = " ".join(translated_tokens)
    result = result.replace(" ,", ",").replace(" .", ".").replace(" !", "!").replace(" ?", "?")
    return result

if __name__ == "__main__":
    lexicon = load_lexicon()
    print(f"NLP Engine Enabled: {USE_NLP}\n")
    
    test_cases = [
        "Сонце веде нас.",
        "Смакуй холод справжньої смерті!",
        "Справедливість для нашого народу."
    ]
    
    for sentence in test_cases:
        elven = compile_sentence(sentence, lexicon)
        print(f"UK: {sentence}")
        print(f"TH: {elven.capitalize()}\n")
