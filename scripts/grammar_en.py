import json
import os
import re

try:
    import spacy
    # Load small english model: python -m spacy download en_core_web_sm
    # Since we are just writing the architecture, we will assume it's installed or fallback
    nlp = spacy.load("en_core_web_sm")
    USE_EN_NLP = True
except Exception:
    USE_EN_NLP = False

def load_lexicon():
    path = os.path.join(os.path.dirname(__file__), '../data/lexicon.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

PRONOUN_SUFFIXES_EN = {
    "us": "na", "we": "anu", 
    "you": "a", 
    "i": "o", "me": "o", 
    "them": "dan", "they": "danu"
}

DROP_WORDS_EN = {"for", "to", "in", "on", "with", "by", "of", "and", "but", "the", "a", "an"}

def find_word_en(lexicon, target_en):
    target_en = target_en.lower()
    for entry in lexicon:
        en_words = re.findall(r'[a-z\']+', entry["translation"]["en"].lower())
        if target_en in en_words:
            return entry
    return None

def apply_plural(word):
    if word.endswith('e'):
        return word + "i"
    elif word.endswith(('a', 'o', 'u')):
        return word[:-1] + "ei"
    return word + "i"

def compile_sentence_en(en_sentence, lexicon):
    if USE_EN_NLP:
        doc = nlp(en_sentence)
        tokens = [(token.text, token.lemma_.lower(), token.tag_ == "NNS" or token.tag_ == "NNPS") for token in doc]
    else:
        # Fallback naive EN parsing
        raw_tokens = re.findall(r'[A-Za-z\']+|[.,!?;]', en_sentence)
        tokens = []
        for t in raw_tokens:
            if re.match(r'[.,!?;]', t):
                tokens.append((t, t, False))
            else:
                is_pl = t.endswith('s') and len(t) > 3 and not t.endswith('ss')
                lemma = t[:-1].lower() if is_pl else t.lower()
                tokens.append((t, lemma, is_pl))

    translated_tokens = []
    i = 0
    while i < len(tokens):
        word, lemma, is_plural = tokens[i]
        
        if re.match(r'[.,!?;]', word):
            if translated_tokens:
                translated_tokens[-1] += word
            i += 1
            continue
            
        if lemma in DROP_WORDS_EN or word.lower() in DROP_WORDS_EN:
            i += 1
            continue
            
        suffix = ""
        # Agglutinate object pronouns
        if i + 1 < len(tokens):
            next_word, next_lemma, _ = tokens[i+1]
            if next_lemma in PRONOUN_SUFFIXES_EN:
                suffix = "'" + PRONOUN_SUFFIXES_EN[next_lemma]
                i += 1
                
        found = find_word_en(lexicon, lemma)
        if not found and not USE_EN_NLP and is_plural:
             found = find_word_en(lexicon, word.lower())
             
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
    print(f"English NLP Engine Enabled: {USE_EN_NLP}\n")
    
    test_cases = [
        "The sun guides us.",
        "Justice for our people.",
        "Taste the chill of true death!"
    ]
    
    print("--- Grammar Compiler V2 Test (English) ---")
    for sentence in test_cases:
        elven = compile_sentence_en(sentence, lexicon)
        print(f"EN: {sentence}")
        print(f"TH: {elven.capitalize()}\n")
