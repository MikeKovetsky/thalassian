import re
from typing import List, Dict, Optional, Union
from ..core.lexicon import load_lexicon
from ..morphology.pluralization import apply_plural
from ..morphology.agglutination import PRONOUN_SUFFIXES_EN, PRONOUN_SUFFIXES_UK

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

class ASTNode:
    def compile(self, lexicon: List[Dict], lang: str) -> str:
        raise NotImplementedError

class WordNode(ASTNode):
    def __init__(self, original: str, lemma: str, is_plural: bool, is_punct: bool = False, pos: str = ""):
        self.original = original
        self.lemma = lemma
        self.is_plural = is_plural
        self.is_punct = is_punct
        self.pos = pos

    def compile(self, lexicon: List[Dict], lang: str) -> str:
        if self.is_punct:
            return self.original

        DROP_WORDS = DROP_WORDS_EN if lang == 'en' else DROP_WORDS_UK
        if self.lemma in DROP_WORDS or self.original.lower() in DROP_WORDS:
            return ""

        find_word = find_word_en if lang == 'en' else find_word_uk
        found = find_word(lexicon, self.lemma)
        if not found and self.is_plural:
            found = find_word(lexicon, self.original.lower())

        if found:
            elven_word = found.get("word", "")
            if self.is_plural and found.get("pos") == "noun":
                elven_word = apply_plural(elven_word)
            return elven_word
        else:
            return f"[{self.original}]"

class PhraseNode(ASTNode):
    def __init__(self, words: List[WordNode]):
        self.words = words

    def compile(self, lexicon: List[Dict], lang: str) -> str:
        parts = [w.compile(lexicon, lang) for w in self.words]
        return " ".join([p for p in parts if p])

class Subject(PhraseNode): pass
class Object(PhraseNode): pass
class PrepositionalPhrase(PhraseNode): pass

class Verb(PhraseNode):
    def __init__(self, words: List[WordNode], pronoun: Optional[WordNode] = None):
        super().__init__(words)
        self.pronoun = pronoun

    def compile(self, lexicon: List[Dict], lang: str) -> str:
        base = super().compile(lexicon, lang)
        if not base:
            return ""
        if self.pronoun:
            PRON_MAP = PRONOUN_SUFFIXES_EN if lang == 'en' else PRONOUN_SUFFIXES_UK
            pron_key = self.pronoun.original.lower()
            if pron_key not in PRON_MAP:
                pron_key = self.pronoun.lemma
                
            if pron_key in PRON_MAP:
                parts = base.split(" ")
                parts[-1] += "'" + PRON_MAP[pron_key]
                return " ".join(parts)
            else:
                return base + " " + self.pronoun.compile(lexicon, lang)
        return base

class Sentence(ASTNode):
    def __init__(self, subject: Optional[Subject] = None, 
                 verb: Optional[Verb] = None, 
                 obj: Optional[Object] = None, 
                 prep_phrases: List[PrepositionalPhrase] = None,
                 front: List[ASTNode] = None,
                 back: List[ASTNode] = None):
        self.subject = subject
        self.verb = verb
        self.obj = obj
        self.prep_phrases = prep_phrases or []
        self.front = front or []
        self.back = back or []

    def compile(self, lexicon: List[Dict], lang: str) -> str:
        parts = []
        for w in self.front:
            c = w.compile(lexicon, lang)
            if c: parts.append(c)
        if self.subject:
            c = self.subject.compile(lexicon, lang)
            if c: parts.append(c)
        if self.verb:
            c = self.verb.compile(lexicon, lang)
            if c: parts.append(c)
        if self.obj:
            c = self.obj.compile(lexicon, lang)
            if c: parts.append(c)
        for pp in self.prep_phrases:
            c = pp.compile(lexicon, lang)
            if c: parts.append(c)
        for w in self.back:
            c = w.compile(lexicon, lang)
            if c: parts.append(c)
            
        text = " ".join(parts)
        text = text.replace(" ,", ",").replace(" .", ".").replace(" !", "!").replace(" ?", "?")
        
        sentences = []
        for s in re.split(r'(?<=[.!?])\s+', text):
            if s:
                sentences.append(s[0].upper() + s[1:])
        if sentences:
            return " ".join(sentences)
        return text.capitalize() if text else ""

def build_ast_en_fallback(en_sentence: str) -> Sentence:
    raw_tokens = re.findall(r"[A-Za-z']+|[.,!?;]", en_sentence)
    tokens = []
    for t in raw_tokens:
        if re.match(r"[.,!?;]", t):
            tokens.append(WordNode(t, t, False, True))
        else:
            is_pl = t.endswith('s') and len(t) > 3 and not t.endswith('ss')
            lemma = t[:-1].lower() if is_pl else t.lower()
            tokens.append(WordNode(t, lemma, is_pl, False))
            
    components = []
    i = 0
    PRONOUNS_EN = set(PRONOUN_SUFFIXES_EN.keys())
    while i < len(tokens):
        w = tokens[i]
        if not w.is_punct and i + 1 < len(tokens) and (tokens[i+1].lemma in PRONOUNS_EN or tokens[i+1].original.lower() in PRONOUNS_EN):
            verb = Verb([w], pronoun=tokens[i+1])
            components.append(verb)
            i += 2
        else:
            components.append(w)
            i += 1
    return Sentence(front=components)

def build_ast_en_spacy(en_sentence: str) -> Sentence:
    doc = nlp(en_sentence)
    root = next((t for t in doc if t.dep_ == "ROOT"), None)
    
    if not root:
        return Sentence(front=[WordNode(t.text, t.lemma_.lower(), False, t.is_punct) for t in doc])

    chunks = {"subject": [], "verb": [root], "obj": [], "prep_phrases": [], "front": [], "back": []}

    for child in root.children:
        subtree = list(child.subtree)
        if child.dep_ in ["nsubj", "nsubjpass", "csubj", "csubjpass"]:
            chunks["subject"].extend(subtree)
        elif child.dep_ in ["dobj", "pobj", "attr"] and child.head == root:
            chunks["obj"].extend(subtree)
        elif child.dep_ == "prep":
            chunks["prep_phrases"].append(subtree)
        else:
            if child.is_punct:
                if child.i < root.i: chunks["front"].extend(subtree)
                else: chunks["back"].extend(subtree)
            elif child.i < root.i:
                chunks["front"].extend(subtree)
            else:
                chunks["verb"].extend(subtree)

    used = set()
    used.add(root.i)
    for group in ["subject", "obj", "front", "back"]:
        used.update([t.i for t in chunks[group]])
    for pp in chunks["prep_phrases"]:
        used.update([t.i for t in pp])
    used.update([t.i for t in chunks["verb"]])
    
    for t in doc:
        if t.i not in used:
            if t.i < root.i:
                chunks["front"].append(t)
            else:
                chunks["back"].append(t)

    def to_words(tokens):
        tokens = sorted(tokens, key=lambda t: t.i)
        return [WordNode(t.text, t.lemma_.lower(), t.tag_ in ["NNS", "NNPS"], t.is_punct, pos=t.pos_) for t in tokens]

    subject = Subject(to_words(chunks["subject"])) if chunks["subject"] else None
    obj = Object(to_words(chunks["obj"])) if chunks["obj"] else None
    verb = Verb(to_words(chunks["verb"])) if chunks["verb"] else None
    prep_phrases = [PrepositionalPhrase(to_words(pp)) for pp in chunks["prep_phrases"]]
    front = to_words(chunks["front"])
    back = to_words(chunks["back"])
    
    PRONOUNS_EN = set(PRONOUN_SUFFIXES_EN.keys())
    if obj and len(obj.words) == 1 and (obj.words[0].lemma in PRONOUNS_EN or obj.words[0].original.lower() in PRONOUNS_EN) and verb:
        verb.pronoun = obj.words[0]
        obj = None

    return Sentence(subject, verb, obj, prep_phrases, front, back)

def compile_sentence_en(en_sentence: str, lexicon: List[Dict] = None) -> str:
    if lexicon is None:
        lexicon = load_lexicon()
    if USE_EN_NLP:
        ast = build_ast_en_spacy(en_sentence)
    else:
        ast = build_ast_en_fallback(en_sentence)
    return ast.compile(lexicon, lang='en')

def build_ast_uk_fallback(uk_sentence: str) -> Sentence:
    tokens = re.findall(r"[А-Яа-яЄєІіЇїҐґ']+|[.,!?;]", uk_sentence)
    word_nodes = []
    for t in tokens:
        if re.match(r"[.,!?;]", t):
            word_nodes.append(WordNode(t, t, False, True))
        else:
            lower_word = t.lower()
            lemma = lower_word
            is_plural = False
            if lower_word in ["нас", "нам", "ми"]: lemma = "ми"
            elif lower_word in ["мене", "мені", "я"]: lemma = "я"
            elif lower_word in ["тебе", "тобі", "ти"]: lemma = "ти"
            elif lower_word.endswith(('и', 'і', 'ї')) and len(lower_word) > 2:
                is_plural = True
                lemma = lower_word[:-1]
            word_nodes.append(WordNode(t, lemma, is_plural, False))
            
    components = []
    i = 0
    PRONOUNS_UK = set(PRONOUN_SUFFIXES_UK.keys())
    while i < len(word_nodes):
        w = word_nodes[i]
        if not w.is_punct and i + 1 < len(word_nodes) and (word_nodes[i+1].lemma in PRONOUNS_UK or word_nodes[i+1].original.lower() in PRONOUNS_UK):
            verb = Verb([w], pronoun=word_nodes[i+1])
            components.append(verb)
            i += 2
        else:
            components.append(w)
            i += 1
    return Sentence(front=components)

def build_ast_uk_pymorphy(uk_sentence: str) -> Sentence:
    tokens = re.findall(r"[А-Яа-яЄєІіЇїҐґ']+|[.,!?;]", uk_sentence)
    word_nodes = []
    for t in tokens:
        if re.match(r"[.,!?;]", t):
            word_nodes.append(WordNode(t, t, False, True))
        else:
            lower_word = t.lower()
            parsed = morph.parse(lower_word)[0]
            lemma = parsed.normal_form
            is_plural = 'plur' in parsed.tag
            word_nodes.append(WordNode(t, lemma, is_plural, False, pos=str(parsed.tag.POS)))

    components = []
    i = 0
    PRONOUNS_UK = set(PRONOUN_SUFFIXES_UK.keys())
    while i < len(word_nodes):
        w = word_nodes[i]
        if not w.is_punct and i + 1 < len(word_nodes) and (word_nodes[i+1].lemma in PRONOUNS_UK or word_nodes[i+1].original.lower() in PRONOUNS_UK):
            verb = Verb([w], pronoun=word_nodes[i+1])
            components.append(verb)
            i += 2
        else:
            components.append(w)
            i += 1
    return Sentence(front=components)

def compile_sentence_uk(uk_sentence: str, lexicon: List[Dict] = None) -> str:
    if lexicon is None:
        lexicon = load_lexicon()
    if USE_UK_NLP:
        ast = build_ast_uk_pymorphy(uk_sentence)
    else:
        ast = build_ast_uk_fallback(uk_sentence)
    return ast.compile(lexicon, lang='uk')
