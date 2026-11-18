import re
from typing import List, Dict, Optional
from ..core.lexicon import load_lexicon
from ..morphology.agglutination import PRONOUN_FORMS_EN, PRONOUN_FORMS_UK, POSSESSIVES_EN, POSSESSIVES_UK

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

# "and" is not dropped: canon rea. "by" is dropped except where it opens an oath or invocation, where it is
# anar' ("By the light", Anar'alah); the "by" of a passive is not anar' ("Saved by magic", Ama noral'arkhana).
DROP_WORDS_EN = {"for", "to", "in", "on", "with", "of", "by", "but", "the", "a", "an"}
DROP_WORDS_UK = {"для", "в", "до", "на", "з", "за", "від", "про", "але"}
# Words that translate but never take a pronoun suffix: "and you" is not "rea'a".
FUNCTION_WORDS_EN = DROP_WORDS_EN | {"and"}
FUNCTION_WORDS_UK = DROP_WORDS_UK | {"і", "та"}
# Pronouns and possessives have their own forms (grammar section 5), never a lexicon word.
PRONOUNS_EN = set(PRONOUN_FORMS_EN) | set(POSSESSIVES_EN)
PRONOUNS_UK = set(PRONOUN_FORMS_UK) | set(POSSESSIVES_UK)
ARTICLES_EN = {"the", "a", "an"}
WORD_EN = r"[a-z']+"
WORD_UK = r"[а-яєіїґ']+"

# Lookup prefers what Blizzard glossed over what was inferred or generated (report 1, bug 2).
BASIS_RANK = {"attested": 0, "segment": 1, "name": 2, "epithet": 2, "inferred": 3, "unverified": 4, "generated": 5}

def canon_rank(entry: Dict) -> tuple:
    """Sort key: canon_basis first, then Thalassian before the other dialects."""
    return (BASIS_RANK.get(entry.get("canon_basis"), len(BASIS_RANK)),
            0 if entry.get("source") == "thalassian" else 1)

def is_phrase(entry: Dict) -> bool:
    """Whole phrases (e.g. "anar'alah" = "by the Light") are not used for word-by-word lookup."""
    return entry.get("pos") == "phrase" or " " in entry.get("word", "")

def gloss_proper(gloss: str) -> str:
    """The gloss without commentary: parentheses go first, because they may hold a ';'
    ("the Veiled One (title of ...; rebel battle cry)"), then everything after the first ';'."""
    return re.sub(r"\([^)]*\)", " ", gloss.lower()).split(";")[0]

def gloss_senses(gloss: str) -> List[str]:
    """Whole senses of the gloss proper: "guide/lead, show" -> ["guide", "lead", "show"]."""
    return [s.strip() for s in re.split(r"[/,]", gloss_proper(gloss)) if s.strip()]

MAX_MENTION_WORDS = 3

def mention_words(gloss: str, pattern: str) -> List[str]:
    """Words a gloss mentions, from its short senses only ("break through"). A longer sense is a
    description, not a translation: "Valanaar: the Skyborne town and skydocks on Zephras Isle"
    must not translate "town" or "isle"."""
    words = []
    for sense in gloss_senses(gloss):
        sense_words = re.findall(pattern, sense)
        if len(sense_words) <= MAX_MENTION_WORDS:
            words += sense_words
    return words

def _find_word(lexicon: List[Dict], target: str, lang: str, pattern: str) -> Optional[Dict]:
    target = target.lower()
    candidates = [e for e in lexicon if lang in e.get("translation", {}) and not is_phrase(e)]
    # An entry whose sense is exactly the word wins over one that only mentions it ("light" vs "Light of the Forest").
    # Among equals the most canon entry wins, in lexicon order on ties: "keeper" is dinoriel, not delar.
    for matches in (lambda g: target in gloss_senses(g), lambda g: target in mention_words(g, pattern)):
        found = [e for e in candidates if matches(e["translation"][lang])]
        if found:
            return min(found, key=canon_rank)
    return None

def find_word_en(lexicon: List[Dict], target_en: str) -> Optional[Dict]:
    return _find_word(lexicon, target_en, "en", WORD_EN)

def find_word_uk(lexicon: List[Dict], target_uk: str) -> Optional[Dict]:
    return _find_word(lexicon, target_uk, "uk", WORD_UK)

CONTRACTIONS_EN = ((r"'re\b", " are"), (r"'m\b", " am"), (r"'ve\b", " have"), (r"'ll\b", " will"))

def expand_contractions(text: str) -> str:
    """Typographic apostrophes made plain, and "they're" spelled "they are", keeping the case."""
    text = text.replace("’", "'")
    for contraction, full in CONTRACTIONS_EN:
        text = re.sub(contraction, full, text, flags=re.IGNORECASE)
    return text

def phrase_key(text: str, lang: str) -> tuple:
    """The words of a gloss sense or an input span, without punctuation or English articles."""
    if lang == "en":
        return tuple(w for w in re.findall(WORD_EN, expand_contractions(text).lower()) if w not in ARTICLES_EN)
    return tuple(re.findall(WORD_UK, text.lower()))

def build_phrasebook(lexicon: List[Dict], lang: str) -> Dict[tuple, Dict]:
    """Every gloss sense of two or more words, mapped to its most canon entry: "children of the blood" ->
    sin'dorei, "the sun guides us" -> anu belore dela'na. A phrase's gloss splits only at '/', because its
    commas are inside the sense ("greetings, traveler"); a word's commas separate senses ("father, papa")."""
    book = {}
    for entry in lexicon:
        gloss = entry.get("translation", {}).get(lang)
        if not gloss:
            continue
        senses = gloss_proper(gloss).split("/") if is_phrase(entry) else gloss_senses(gloss)
        for sense in senses:
            key = phrase_key(sense, lang)
            if len(key) >= 2 and (key not in book or canon_rank(entry) < canon_rank(book[key])):
                book[key] = entry
    return book

def _attach(first: str, second: str) -> str:
    """first'second. An untranslated part stays in its brackets, as a pronoun suffix does ("[bind]'o"),
    so the hybrid engine can fill it in place."""
    return f"{first}'{second}" if first and second else first or second

class ASTNode:
    def compile(self, lexicon: List[Dict], lang: str) -> str:
        raise NotImplementedError

class WordNode(ASTNode):
    """A word or a punctuation mark. is_plural only lets "travelers" find "traveler": nouns have no plural
    (grammar 3.2), so the elven word never changes."""
    def __init__(self, original: str, lemma: str, is_plural: bool, is_punct: bool = False, pos: str = ""):
        self.original = original
        self.lemma = lemma
        self.is_plural = is_plural
        self.is_punct = is_punct
        self.pos = pos

    def is_any(self, words) -> bool:
        return not self.is_punct and (self.lemma in words or self.original.lower() in words)

    def entry(self, lexicon: List[Dict], lang: str) -> Optional[Dict]:
        find_word = find_word_en if lang == 'en' else find_word_uk
        found = find_word(lexicon, self.lemma)
        if not found and self.is_plural:
            found = find_word(lexicon, self.original.lower())
        return found

    def compile(self, lexicon: List[Dict], lang: str) -> str:
        if self.is_punct:
            return self.original

        if self.is_any(DROP_WORDS_EN if lang == 'en' else DROP_WORDS_UK):
            return ""

        form = self.pronoun_form(lang)
        if form:
            return form

        found = self.entry(lexicon, lang)
        return found.get("word", "") if found else f"[{self.original}]"

    def pronoun_form(self, lang: str) -> Optional[str]:
        """The free form of a pronoun or possessive standing on its own ("we" -> na, "you" -> a)."""
        if self.is_punct:
            return None
        forms = PRONOUN_FORMS_EN if lang == 'en' else PRONOUN_FORMS_UK
        possessives = POSSESSIVES_EN if lang == 'en' else POSSESSIVES_UK
        for key in (self.original.lower(), self.lemma):
            if key in forms:
                return forms[key]
            if key in possessives:
                return possessives[key][0]
        return None

class FixedNode(ASTNode):
    """A whole canon phrase or compound found by the phrasebook."""
    def __init__(self, text: str):
        self.text = text

    def compile(self, lexicon: List[Dict], lang: str) -> str:
        return self.text

class ProcliticNode(ASTNode):
    """"By the light" -> anar'alah: in oaths and invocations canon joins anar before its object (Anar'alah,
    Anar'endal dracon, and six untranslated exclamations of the same shape)."""
    def __init__(self, word: WordNode, target: ASTNode):
        self.word = word
        self.target = target

    def compile(self, lexicon: List[Dict], lang: str) -> str:
        found = find_word_en(lexicon, self.word.lemma)
        return _attach(found["word"] if found else "", self.target.compile(lexicon, lang))

NOUN_POS = {"noun", "proper noun"}

def _is_noun(node: Optional[ASTNode], lexicon: List[Dict], lang: str) -> bool:
    entry = node.entry(lexicon, lang) if isinstance(node, WordNode) else None
    return bool(entry) and entry.get("pos") in NOUN_POS

class CompoundNode(ASTNode):
    """A name: "Children of the Blood" -> sin'dorei. Compounds put the modifier first and the head last
    (grammar 3.3), and they name things: peoples, places, weapons, titles. apply_compounds_en builds one
    only for a capitalized "X of the Y"; an ordinary "of" phrase stays free, head first (grammar 3.4).
    It also stays free when the head is not an elven noun or the name goes on past the modifier: the
    modifier is not a noun, or a noun follows it. A verb after the modifier ends the name: "the Children
    of the Blood guide us" is sin'dorei dela'na. `after` is the content word after the modifier, if any."""
    def __init__(self, head: WordNode, modifier: WordNode, after: Optional[ASTNode] = None):
        self.head = head
        self.modifier = modifier
        self.after = after

    def compile(self, lexicon: List[Dict], lang: str) -> str:
        head, modifier = self.head.compile(lexicon, lang), self.modifier.compile(lexicon, lang)
        goes_on = self.after is not None and (
            not _is_noun(self.modifier, lexicon, lang) or _is_noun(self.after, lexicon, lang))
        if _is_noun(self.head, lexicon, lang) and not goes_on:
            return _attach(modifier, head)
        return " ".join(p for p in (head, modifier) if p)

class PossessiveNode(ASTNode):
    """"your heart" -> mal alann, "our hearts" -> alann na (grammar 5.2)."""
    def __init__(self, word: WordNode, target: ASTNode, form: str, before: bool):
        self.word = word
        self.target = target
        self.form = form
        self.before = before

    def compile(self, lexicon: List[Dict], lang: str) -> str:
        target = self.target.compile(lexicon, lang)
        parts = (self.form, target) if self.before else (target, self.form)
        return " ".join(p for p in parts if p)

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
        if not self.pronoun:
            return base
        if not base:
            # A dropped base must not take the pronoun with it ("justice for you").
            return self.pronoun.compile(lexicon, lang)
        form = self.pronoun.pronoun_form(lang)
        if form:
            parts = base.split(" ")
            parts[-1] += "'" + form
            return " ".join(parts)
        return base + " " + self.pronoun.compile(lexicon, lang)

def _clause_start(nodes: List[ASTNode], i: int) -> bool:
    """Whether nodes[i] opens a clause: nothing but articles before it, back to the start or punctuation."""
    k = i - 1
    while k >= 0 and isinstance(nodes[k], WordNode) and nodes[k].is_any(ARTICLES_EN):
        k -= 1
    return k < 0 or (isinstance(nodes[k], WordNode) and nodes[k].is_punct)

def _clause_end(nodes: List[ASTNode], j: int) -> bool:
    return j + 1 >= len(nodes) or (isinstance(nodes[j + 1], WordNode) and nodes[j + 1].is_punct)

def apply_phrasebook(nodes: List[WordNode], book: Dict[tuple, Dict], lang: str) -> List[ASTNode]:
    """Replace the longest spans whose words equal a phrasebook sense. A span starts at a word that
    counts (not an article) and may run over commas, but not over other punctuation. A whole phrase is a
    fixed formula used whole (grammar 8), so it must fill its clause: "The light of the sun guides us"
    must not put the clause-opening anu of anu belore dela'na in the middle."""
    longest = max((len(k) for k in book), default=0)
    out, i = [], 0
    while i < len(nodes):
        best = None
        if not nodes[i].is_punct and phrase_key(nodes[i].original, lang):
            key, j = (), i
            while j < len(nodes) and len(key) < longest:
                node = nodes[j]
                if node.is_punct and node.original != ",":
                    break
                if not node.is_punct:
                    words = phrase_key(node.original, lang)
                    key += words
                    if words and key in book and (not is_phrase(book[key]) or (
                            _clause_start(nodes, i) and _clause_end(nodes, j))):
                        best = (j, book[key])
                j += 1
        if best:
            out.append(FixedNode(best[1]["word"]))
            i = best[0] + 1
        else:
            out.append(nodes[i])
            i += 1
    return out

def _is_content(node: ASTNode, function_words, pronouns) -> bool:
    """A node that translates to an elven word of its own: not punctuation, a function word or a pronoun."""
    if isinstance(node, WordNode):
        return not node.is_punct and not node.is_any(function_words) and not node.is_any(pronouns)
    return True

def apply_proclitics_en(nodes: List[ASTNode]) -> List[ASTNode]:
    """"By [the] X", opening a clause, -> anar'X. Any other "by" is dropped."""
    out, i = [], 0
    while i < len(nodes):
        node = nodes[i]
        if isinstance(node, WordNode) and node.is_any({"by"}) and _clause_start(nodes, i):
            k = i + 1
            while k < len(nodes) and isinstance(nodes[k], WordNode) and nodes[k].is_any(ARTICLES_EN):
                k += 1
            if k < len(nodes) and _is_content(nodes[k], FUNCTION_WORDS_EN, PRONOUNS_EN):
                out.append(ProcliticNode(node, nodes[k]))
                i = k + 1
                continue
        out.append(node)
        i += 1
    return out

def _capitalized(node: ASTNode) -> bool:
    return isinstance(node, WordNode) and node.original[:1].isupper()

def apply_compounds_en(nodes: List[ASTNode]) -> List[ASTNode]:
    """A name, "X of [the] Y" with X and Y capitalized ("Light of the Forest"), -> Y'X; CompoundNode decides,
    from the lexicon, whether the name goes on past Y. Any other "of" phrase is left as it is: "of" and
    "the" drop out and the head comes first, as in canon alah belore, endal dracon and falor talah."""
    content = lambda n: isinstance(n, WordNode) and _is_content(n, FUNCTION_WORDS_EN, PRONOUNS_EN)
    out, i = [], 0
    while i < len(nodes):
        node = nodes[i]
        if isinstance(node, WordNode) and node.is_any({"of"}) and out and content(out[-1]) and _capitalized(out[-1]):
            k = i + 1
            while k < len(nodes) and isinstance(nodes[k], WordNode) and nodes[k].is_any(ARTICLES_EN):
                k += 1
            if k < len(nodes) and content(nodes[k]) and _capitalized(nodes[k]):
                nxt = nodes[k + 1] if k + 1 < len(nodes) else None
                after = nxt if nxt is not None and _is_content(nxt, FUNCTION_WORDS_EN, PRONOUNS_EN) else None
                out[-1] = CompoundNode(out[-1], nodes[k], after)
                i = k + 1
                continue
        out.append(node)
        i += 1
    return out

def apply_possessives(nodes: List[ASTNode], possessives, function_words, pronouns) -> List[ASTNode]:
    """A possessive before a content word: mal goes before it, na, o and dan after it (grammar 5.2).
    Anywhere else a possessive word is a pronoun ("guide her" -> dela'dan)."""
    out, i = [], 0
    while i < len(nodes):
        node = nodes[i]
        nxt = nodes[i + 1] if i + 1 < len(nodes) else None
        if isinstance(node, WordNode) and node.is_any(possessives) and nxt is not None and \
                _is_content(nxt, function_words, pronouns):
            key = node.original.lower() if node.original.lower() in possessives else node.lemma
            form, before = possessives[key]
            out.append(PossessiveNode(node, nxt, form, before))
            i += 2
        else:
            out.append(node)
            i += 1
    return out

def pair_pronouns(nodes: List[ASTNode], pronouns, function_words) -> List[ASTNode]:
    """A word followed by an object pronoun takes it as a suffix ("guide us" -> dela'na). A function word
    does not ("justice for you" keeps its "you"), nor does a pronoun: "I guide you" is o dela'a, with the
    subject a free word before the verb (grammar 5.3)."""
    out, i = [], 0
    while i < len(nodes):
        node = nodes[i]
        nxt = nodes[i + 1] if i + 1 < len(nodes) else None
        if (isinstance(node, WordNode) and not node.is_punct and not node.is_any(function_words)
                and not node.is_any(pronouns) and isinstance(nxt, WordNode) and nxt.is_any(pronouns)):
            out.append(Verb([node], pronoun=nxt))
            i += 2
        else:
            out.append(node)
            i += 1
    return out

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

def tokens_en(en_sentence: str) -> List[WordNode]:
    """Words and punctuation. The plural guess (a final -s, not -ss, on a word of four letters or more)
    only finds the singular's entry."""
    tokens = []
    for t in re.findall(r"[A-Za-z']+|[.,!?;]", expand_contractions(en_sentence)):
        if re.match(r"[.,!?;]", t):
            tokens.append(WordNode(t, t, False, True))
        else:
            is_pl = t.endswith('s') and len(t) > 3 and not t.endswith('ss')
            lemma = t[:-1].lower() if is_pl else t.lower()
            tokens.append(WordNode(t, lemma, is_pl, False))
    return tokens

def canon_passes_en(tokens: List[WordNode], phrasebook: Optional[Dict[tuple, Dict]] = None) -> Sentence:
    """The passes in canon order: whole phrases first, then "By X" (anar'X), then names "X of the Y" (Y'X),
    then possessives, then pronoun suffixes. Word order follows the input."""
    nodes = apply_phrasebook(tokens, phrasebook or {}, "en")
    nodes = apply_compounds_en(apply_proclitics_en(nodes))
    nodes = apply_possessives(nodes, POSSESSIVES_EN, FUNCTION_WORDS_EN, PRONOUNS_EN)
    return Sentence(front=pair_pronouns(nodes, PRONOUNS_EN, FUNCTION_WORDS_EN))

def build_ast_en_fallback(en_sentence: str, phrasebook: Optional[Dict[tuple, Dict]] = None) -> Sentence:
    """The regex builder."""
    return canon_passes_en(tokens_en(en_sentence), phrasebook)

def build_ast_en_spacy(en_sentence: str, phrasebook: Optional[Dict[tuple, Dict]] = None) -> Sentence:
    """The regex builder's words and passes, with spaCy's lemma, plural tag and part of speech for each
    word that spaCy reads as the same token ("guided" -> guide). So the canon phrases, anar' and the
    compounds apply when spaCy is installed too, as the pymorphy3 builder does for Ukrainian."""
    tokens = tokens_en(en_sentence)
    by_start = {t.idx: t for t in nlp(" ".join(node.original for node in tokens))}
    start = 0
    for node in tokens:
        token = by_start.get(start)
        if not node.is_punct and token is not None and token.text == node.original:
            node.lemma, node.pos = token.lemma_.lower(), token.pos_
            node.is_plural = token.tag_ in ("NNS", "NNPS")
        start += len(node.original) + 1
    return canon_passes_en(tokens, phrasebook)

def compile_sentence_en(en_sentence: str, lexicon: List[Dict] = None, phrasebook: bool = True) -> str:
    """phrasebook=False translates word by word, to score the rules without the canon phrases they are
    checked against."""
    if lexicon is None:
        lexicon = load_lexicon()
    book = build_phrasebook(lexicon, "en") if phrasebook else None
    if USE_EN_NLP:
        ast = build_ast_en_spacy(en_sentence, book)
    else:
        ast = build_ast_en_fallback(en_sentence, book)
    return ast.compile(lexicon, lang='en')

def build_ast_uk_fallback(uk_sentence: str, phrasebook: Optional[Dict[tuple, Dict]] = None) -> Sentence:
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
            
    nodes = apply_phrasebook(word_nodes, phrasebook or {}, "uk")
    nodes = apply_possessives(nodes, POSSESSIVES_UK, FUNCTION_WORDS_UK, PRONOUNS_UK)
    return Sentence(front=pair_pronouns(nodes, PRONOUNS_UK, FUNCTION_WORDS_UK))

def build_ast_uk_pymorphy(uk_sentence: str, phrasebook: Optional[Dict[tuple, Dict]] = None) -> Sentence:
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

    nodes = apply_phrasebook(word_nodes, phrasebook or {}, "uk")
    nodes = apply_possessives(nodes, POSSESSIVES_UK, FUNCTION_WORDS_UK, PRONOUNS_UK)
    return Sentence(front=pair_pronouns(nodes, PRONOUNS_UK, FUNCTION_WORDS_UK))

def compile_sentence_uk(uk_sentence: str, lexicon: List[Dict] = None, phrasebook: bool = True) -> str:
    if lexicon is None:
        lexicon = load_lexicon()
    book = build_phrasebook(lexicon, "uk") if phrasebook else None
    if USE_UK_NLP:
        ast = build_ast_uk_pymorphy(uk_sentence, book)
    else:
        ast = build_ast_uk_fallback(uk_sentence, book)
    return ast.compile(lexicon, lang='uk')
