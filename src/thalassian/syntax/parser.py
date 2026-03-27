import re
from typing import List, Dict, Optional
from ..core.lexicon import load_lexicon
from ..morphology.pluralization import apply_plural
from ..morphology.agglutination import PRONOUN_SUFFIXES_EN, PRONOUN_SUFFIXES_UK

# Optional NLP imports
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    USE_EN_NLP = True
except Exception:
    USE_EN_NLP = False

try:
    import pymorphy3
    morph = pymorphy3.MorphAnalyzer(lang='uk')
    USE_UK_NLP = True
except ImportError:
    USE_UK_NLP = False

DROP_WORDS_EN = {"for", "to", "in", "on", "with", "by", "of", "and", "but", "the", "a", "an"}
DROP_WORDS_UK = {"для", "в", "до", "на", "з", "за", "від", "про", "і", "та", "але"}

def find_word_en(lexicon: List[Dict], target_en: str) -> Optional[Dict]:
    target_en = target_en.lower()
    for entry in lexicon:
        if "en" in entry.get("translation", {}):
            en_words = re.findall(r"[a-z']+", entry["translation"]["en"].lower())
            if target_en in en_words:
                return entry
    return None

def find_word_uk(lexicon: List[Dict], target_uk: str) -> Optional[Dict]:
    target_uk = target_uk.lower()
    for entry in lexicon:
        if "uk" in entry.get("translation", {}):
            uk_words = re.findall(r"[а-яєіїґ']+", entry["translation"]["uk"].lower())
            if target_uk in uk_words:
                return entry
    return None

def compile_sentence_en(en_sentence: str, lexicon: List[Dict] = None) -> str:
    if lexicon is None:
        lexicon = load_lexicon()
        
    if USE_EN_NLP:
        doc = nlp(en_sentence)
        tokens = [(token.text, token.lemma_.lower(), token.tag_ in ["NNS", "NNPS"]) for token in doc]
    else:
        raw_tokens = re.findall(r"[A-Za-z']+|[.,!?;]", en_sentence)
        tokens = []
        for t in raw_tokens:
            if re.match(r"[.,!?;]", t):
                tokens.append((t, t, False))
            else:
                is_pl = t.endswith('s') and len(t) > 3 and not t.endswith('ss')
                lemma = t[:-1].lower() if is_pl else t.lower()
                tokens.append((t, lemma, is_pl))

    translated_tokens = []
    i = 0
    while i < len(tokens):
        word, lemma, is_plural = tokens[i]
        
        if re.match(r"[.,!?;]", word):
            if translated_tokens:
                translated_tokens[-1] += word
            i += 1
            continue
            
        if lemma in DROP_WORDS_EN or word.lower() in DROP_WORDS_EN:
            i += 1
            continue
            
        suffix = ""
        if i + 1 < len(tokens):
            _, next_lemma, _ = tokens[i+1]
            if next_lemma in PRONOUN_SUFFIXES_EN:
                suffix = "'" + PRONOUN_SUFFIXES_EN[next_lemma]
                i += 1
                
        found = find_word_en(lexicon, lemma)
        if not found and not USE_EN_NLP and is_plural:
             found = find_word_en(lexicon, word.lower())
             
        if found:
            elven_word = found.get("word", "")
            if is_plural and found.get("pos") == "noun":
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

def compile_sentence_uk(uk_sentence: str, lexicon: List[Dict] = None) -> str:
    if lexicon is None:
        lexicon = load_lexicon()
        
    tokens = re.findall(r"[А-Яа-яЄєІіЇїҐґ']+|[.,!?;]", uk_sentence)
    
    translated_tokens = []
    i = 0
    while i < len(tokens):
        word = tokens[i]
        
        if re.match(r"[.,!?;]", word):
            if translated_tokens:
                translated_tokens[-1] += word
            i += 1
            continue
            
        lower_word = word.lower()
        lemma = lower_word
        is_plural = False
        
        if USE_UK_NLP:
            parsed = morph.parse(lower_word)[0]
            lemma = parsed.normal_form
            if 'plur' in parsed.tag:
                is_plural = True
        else:
            if lower_word in ["нас", "нам", "ми"]: lemma = "ми"
            elif lower_word in ["мене", "мені", "я"]: lemma = "я"
            elif lower_word in ["тебе", "тобі", "ти"]: lemma = "ти"
            elif lower_word.endswith(('и', 'і', 'ї')) and len(lower_word) > 2:
                is_plural = True
                lemma = lower_word[:-1]

        if lemma in DROP_WORDS_UK or lower_word in DROP_WORDS_UK:
            i += 1
            continue
            
        suffix = ""
        if i + 1 < len(tokens):
            next_word = tokens[i+1].lower()
            next_lemma = next_word
            if USE_UK_NLP:
                next_parsed = morph.parse(next_word)[0]
                next_lemma = next_parsed.normal_form
            else:
                if next_word in ["нас", "нам", "ми"]: next_lemma = "ми"
                elif next_word in ["мене", "мені", "я"]: next_lemma = "я"
                elif next_word in ["тебе", "тобі", "ти"]: next_lemma = "ти"
                
            if next_lemma in PRONOUN_SUFFIXES_UK:
                suffix = "'" + PRONOUN_SUFFIXES_UK[next_lemma]
                i += 1 
                
        found = find_word_uk(lexicon, lemma)
        if not found and not USE_UK_NLP and is_plural:
            found = find_word_uk(lexicon, lower_word)
            
        if found:
            elven_word = found.get("word", "")
            if is_plural and found.get("pos") == "noun":
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
