"""Generate the new word forms of report 8 and write every proposal to 8-candidates.json.

8-candidates.json holds every action of the November 2026 reconstruction audit: remove, fix, note, regenerate and
add, each with confidence, reason and evidence. apply_audit.py applies it to the lexicon.

Model. An order-4 interpolated Kneser-Ney character model with word-start and word-end symbols (report 1, Method 7),
trained on the parts of attested elven forms: the lexicon's Thalassian, Darnassian, Shalassian and Skyborne entries
that are not generated or unverified, plus the elven branches of 7-forms.json (not its Titan and Zandali controls),
split with shared_core.parts(). The English surnames inside attested names (ENGLISH_NAME_PARTS: Feathermoon,
Shadowsong ...) are left out of the training, not out of the checks.

Seeds. Every form is drawn with random.Random(seed), where the seed is the first 12 hex digits of the SHA-256 of the
meaning. The same inputs always give the same forms.

Filters. A sample is rejected if it:
1. uses a letter that fewer than five attested parts use (q, x and c), ends in -is or -ael, has no vowel, or breaks
   report 1's phonotactic filter (three consonants in a row, a tripled letter, an ending other than a vowel or
   l r n s h th sh m d x, or a word-initial cluster other than th, sh and dr);
2. is an English word or name of three letters or more (/usr/share/dict/words and propernames), or a word in FOREIGN:
   the real words in other languages that the audit flagged, and those a reading of this script's output found;
3. equals, or (at four letters or more) is one edit from, an attested elven form or part, names and words of unknown
   meaning included;
4. contains an attested part of three letters or more whose meaning is known, or any attested part of four letters
   or more, or (at four letters or more) is itself inside an attested form, like sira in Sira'kess;
5. equals, or (at four letters or more) is one edit from, a scrambler word of any in-game language or a Titan or
   Zandali form;
6. equals, or is one edit from, a word of the lexicon or another new word, when either word has four letters or more
   (the audit's test for minimal pairs: tala ~ tal).
Below four letters only equality counts, as in the audit: 94% of the model's three-letter words are one edit from some
scrambler word.

Selection. The length is drawn first, from the lengths of the attested words within the range (function words 2 to 4
letters, content words 3 to 7). Of SAMPLES samples, the one of that length with the best Kneser-Ney log-probability
per character (end symbol included) is kept. Its score and its percentile among the attested parts (each scored
leave-one-out) go into the entry's method.

Inputs that are not in git. The scrambler lists (.wowf-extract/LanguageWords.csv and
.wowf-extract/origins/scramblers.json), the audit's candidates and coverage table (.wowf-extract/audit/) and the
system word list are local. That is why the output, 8-candidates.json, is committed: it is the reviewable input of
apply_audit.py, and the recipe in merge_candidates.py's docstring never runs this script.

To rebuild 8-candidates.json, run the first four commands of that recipe (the lexicon as apply_voice.py leaves it),
then, from the repo root:
  python3 research/2026-11-revival/scripts/generate_words.py
"""
import bisect
import csv
import hashlib
import json
import math
import os
import random
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from corpus import CORPUS  # noqa: E402
from merge_candidates import LEX, LOG, RES, ROOT, key  # noqa: E402
from shared_core import parts  # noqa: E402

WX = os.path.join(ROOT, ".wowf-extract")
AUDIT = os.path.join(WX, "audit", "vocab-candidates.json")
COVERAGE = os.path.join(WX, "audit", "coverage.json")
LANGUAGE_WORDS = os.path.join(WX, "LanguageWords.csv")
SCRAMBLERS = os.path.join(WX, "origins", "scramblers.json")
ENGLISH = ("/usr/share/dict/words", "/usr/share/dict/propernames")
FORMS = os.path.join(RES, "7-forms.json")
OUT = os.path.join(RES, "8-candidates.json")
FINDINGS = "research/2026-11-revival/8-audit/vocab-findings.md"

ELVEN = ("thalassian", "darnassian", "shalassian", "skyborne")
CONTROLS = ("titan", "zandali")
START, END = "^", "$"
ORDER = 4
SAMPLES = 10000
LENGTHS = {"function": (2, 4), "content": (3, 7)}
LETTERS = "abcdefghijklmnopqrstuvwxyz"
MIN_LETTER_PARTS = 5  # a letter fewer attested parts use (q, x, c) is outside the alphabet

# ---------------------------------------------------------------------------------------------------------------------
# The model


class KneserNey:
    """Interpolated Kneser-Ney character model with word-start and word-end symbols.

    The highest order counts n-grams; each lower order counts how many different characters precede an n-gram
    (continuation counts). The lowest order is interpolated with a uniform distribution over the alphabet and the
    end symbol, so every symbol has some probability."""

    def __init__(self, words, order=ORDER, discount=0.75, alphabet=None):
        self.order, self.d = order, discount
        self.symbols = sorted(set(alphabet or "").union(*map(set, words)) | {END})
        self.counts = [defaultdict(Counter) for _ in range(order)]
        seen = set()
        top = order - 1
        for w in words:
            s = START * top + w + END
            for i in range(top, len(s)):
                ch = s[i]
                self.counts[top][s[i - top:i]][ch] += 1
                for k in range(top):
                    ctx = s[i - k:i]
                    if (k, s[i - k - 1], ctx, ch) not in seen:
                        seen.add((k, s[i - k - 1], ctx, ch))
                        self.counts[k][ctx][ch] += 1
        self._cache = {}

    def dist(self, ctx):
        """The distribution of the next symbol after ctx, as a dict over self.symbols. It sums to 1."""
        ctx = (START * (self.order - 1) + ctx)[-(self.order - 1):]
        if ctx in self._cache:
            return self._cache[ctx][0]
        p = {s: 1 / len(self.symbols) for s in self.symbols}
        for k in range(self.order):
            c = self.counts[k].get(ctx[len(ctx) - k:] if k else "")
            if not c:
                continue
            tot = sum(c.values())
            lam = self.d * len(c) / tot
            p = {s: max(c[s] - self.d, 0) / tot + lam * p[s] for s in self.symbols}
        cum, acc = [], 0.0
        for s in self.symbols:
            acc += p[s]
            cum.append(acc)
        self._cache[ctx] = (p, cum)
        return p

    def logp(self, word):
        """Natural log-probability of the word, end symbol included; minus infinity if it has an unknown letter."""
        if set(word) - set(self.symbols):
            return -math.inf
        s = START * (self.order - 1) + word + END
        return sum(math.log(self.dist(s[:i])[s[i]]) for i in range(self.order - 1, len(s)))

    def score(self, word):
        """Log-probability per character, end symbol included: the audit's measure."""
        return self.logp(word) / (len(word) + 1)

    def sample(self, rng, maxlen=12):
        """One word, or None if it runs past maxlen letters."""
        s = ""
        while len(s) <= maxlen:
            self.dist(s)
            cum = self._cache[(START * (self.order - 1) + s)[-(self.order - 1):]][1]
            ch = self.symbols[min(bisect.bisect_right(cum, rng.random() * cum[-1]), len(cum) - 1)]
            if ch == END:
                return s
            s += ch
        return None


def seed_for(meaning):
    """A seed from the meaning alone: the first 12 hex digits of its SHA-256."""
    return int(hashlib.sha256(meaning.encode("utf-8")).hexdigest()[:12], 16)


def loo_scores(train):
    """Each training part scored by a model trained on all the others, sorted: the yardstick for percentiles."""
    alphabet = set("".join(train))
    return sorted(KneserNey(train[:i] + train[i + 1:], alphabet=alphabet).score(w) for i, w in enumerate(train))


def percentile(score, yardstick):
    """The share of the yardstick below the score, in percent."""
    return 100.0 * bisect.bisect_left(yardstick, score) / len(yardstick)


# ---------------------------------------------------------------------------------------------------------------------
# What a new word must not resemble


def keys(form):
    """The letter runs of a form, and each space-separated word with its apostrophes and hyphens removed:
    "Anar'alah belore" -> {"anar", "alah", "belore", "anaralah"}."""
    low = form.lower()
    out = set(re.findall(r"[a-z]+", low))
    for token in low.split():
        joined = "".join(re.findall(r"[a-z]+", token))
        if joined:
            out.add(joined)
    return out


def one_edit(word):
    """Every string one deletion, substitution or insertion away from word."""
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    out = {a + b[1:] for a, b in splits if b}
    out |= {a + c + b[1:] for a, b in splits if b for c in LETTERS}
    out |= {a + c + b for a, b in splits for c in LETTERS}
    out.discard(word)
    return out


def near(word, pool, symmetric=False):
    """The pool word that word equals, or (at four letters or more) is one edit from; None if there is none.

    symmetric: the four letters may be the pool word's, as in the audit's check of invented words against each other
    (tala ~ tal): a three-letter word is then also near the four-letter words one insertion away."""
    if word in pool:
        return word
    if len(word) >= 4:
        hits = one_edit(word) & pool
    elif symmetric:
        hits = {v for v in one_edit(word) if len(v) >= 4} & pool
    else:
        hits = set()
    return min(hits) if hits else None


VOWELS = set("aeiouy")
INITIAL_CLUSTERS = ("th", "sh", "dr")


def phonotactic(word):
    """Report 1's filter (phono.py syllables_ok), plus its proposed ban on initial clusters other than th, sh, dr."""
    w = word.replace("th", "θ").replace("sh", "ʃ")
    run = 0
    for c in w:
        run = run + 1 if c not in VOWELS else 0
        if run >= 3:
            return False
    if re.search(r"(.)\1\1", word):
        return False
    if w[-1] not in VOWELS and w[-1] not in "lrnsθʃmdhx":
        return False
    if len(word) > 1 and word[0] not in VOWELS and word[1] not in VOWELS and not word.startswith(INITIAL_CLUSTERS):
        return False
    return True


# English surnames and words inside attested names and lines (Shandris Feathermoon, Maiev Shadowsong, the Nazja war
# cry Ash'thero sanguine). They stay in the collision checks, but the model does not learn elvish from them: with them
# it drew words such as "moonel".
ENGLISH_NAME_PARTS = frozenset({
    "feathermoon", "mooncrest", "moonfang", "nightblade", "ravencrest", "rivertree", "shadowsong", "stareye",
    "stormrage", "sunstrider", "whisperwind", "millicent", "serene", "sanguine", "sauguine",
})

# Real words in other languages. The first group repeats what the audit flagged (vocab-findings.md section 8); the
# second was found by reading this script's output, and each was rejected and drawn again.
FOREIGN = {
    "morn": "Sindarin 'black'", "mith": "Sindarin 'grey'", "oris": "Latin 'of the mouth'", "os": "Latin 'bone'",
    "on": "Russian, Ukrainian 'he'", "sir": "Ukrainian 'cheese'", "sira": "Ukrainian 'grey'",
    "rashist": "Ukrainian wartime pejorative", "san": "Ukrainian 'rank'", "tabe": "Belarusian 'to you'",
    "aluta": "Portuguese 'the struggle'", "doras": "Irish 'door'", "tora": "Hebrew 'Torah'", "elara": "given name",
    "sorin": "given name", "neal": "given name", "astor": "surname", "dara": "given name", "lanelot": "Lancelot",
    # found by reading the output
    "thatar": "reads as 'Tatar'", "shinel": "Ukrainian шинель 'greatcoat'", "rei": "Portuguese 'king'",
    "faros": "Spanish 'lighthouses'", "therion": "Greek 'beast'", "malen": "German 'to paint'",
    "amei": "Portuguese 'I loved'", "mallas": "Spanish 'meshes'", "meir": "given name", "ilir": "given name",
    "nos": "Latin, Spanish 'we, us'", "har": "Swedish 'has'", "adil": "given name", "ela": "Portuguese 'she'",
    "ius": "Latin 'law'", "ros": "reads as Ukrainian рос- 'Russia'", "jal": "Hindi 'water'", "ello": "Spanish 'it'",
    "melonos": "holds English 'melon'", "nel": "Italian 'in the'", "kus": "vulgar in Hebrew and Arabic",
    "fane": "English 'temple' (archaic)", "var": "Swedish 'was'", "nas": "Ukrainian нас 'us'",
    "dieth": "English 'dies' (archaic)", "kiril": "given name", "mei": "Dutch 'May'", "zal": "Ukrainian зал 'hall'",
    "los": "Spanish 'the'", "sel": "French 'salt'", "dir": "German 'to you'", "nai": "Greek 'yes'",
    "mol": "the unit mol", "dil": "Hindi 'heart'", "jas": "Dutch 'coat'", "eldil": "C. S. Lewis's eldil",
    "eldar": "Tolkien's Eldar", "olas": "Spanish 'waves'", "rai": "Ukrainian рай 'paradise'",
    "illius": "Latin 'of that one'", "saral": "Hindi 'simple'", "vate": "Italian 'bard'",
    "farei": "Portuguese 'I will do'", "shith": "reads as English 'shit'", "fas": "Latin 'divine law'",
    "kurama": "a character in Naruto", "tyne": "the river Tyne", "zor": "Turkish, Persian 'hard, force'",
    "aros": "Spanish 'hoops'", "farol": "Portuguese, Spanish 'lighthouse'", "ames": "surname; French 'souls'",
    "dre": "Dr. Dre", "tos": "Spanish 'cough'", "zir": "Ukrainian зір 'sight'", "bir": "Turkish 'one'",
    "dei": "Italian 'of the'", "bei": "German 'at'", "ena": "Greek 'one'", "ero": "reads as 'erotic'",
    "bil": "Danish 'car'", "bai": "Chinese 'white'", "valen": "Spanish 'they are worth'",
    "fallian": "holds English 'fall'", "des": "French 'of the'", "has": "English 'has'", "meri": "Finnish 'sea'",
    "inu": "Japanese 'dog'", "sarei": "Italian 'I would be'", "fai": "Italian 'you do'", "dai": "Italian 'come on'",
    "ono": "Ukrainian оно 'it'", "der": "German 'the'", "sos": "SOS", "fos": "Greek 'light'",
    "haja": "Portuguese 'let there be'", "vae": "Latin 'woe'", "vos": "Spanish, Latin 'you'", "jah": "Jah",
    "annan": "a surname", "therian": "English 'therian'", "tir": "French 'shot'", "meru": "Mount Meru",
    "ars": "Latin 'art'", "zei": "Dutch 'said'", "beso": "Spanish 'kiss'", "ola": "Spanish 'wave'",
    "zon": "Dutch 'sun'", "zai": "Chinese 'at'", "ili": "Russian или 'or'", "gai": "French 'cheerful'",
    "sor": "Russian сор 'rubbish'", "fil": "French 'thread'", "une": "French 'a'", "lesta": "Italian 'quick'",
    "karal": "Russian карал 'punished'", "onu": "Turkish 'him'", "vir": "Latin 'man'", "aas": "Dutch 'carrion'",
    "zes": "Dutch 'six'", "bita": "Swedish 'bite'", "hus": "Swedish 'house'", "zia": "Italian 'aunt'",
    "vin": "French 'wine'", "dia": "Spanish 'day'", "kia": "a car brand", "rir": "Portuguese 'to laugh'",
    "hos": "Swedish 'at'",
}


class Inventory:
    """Everything a new word is checked against, with the reason each check gives."""

    def __init__(self, lexicon, forms, scrambler_words, english, foreign=FOREIGN, extra_attested=()):
        elven_forms = [f for f in forms if f["branch"] not in CONTROLS and f.get("kind") != "scrambler"]
        control_forms = [f for f in forms if f["branch"] in CONTROLS]
        self.train = sorted({p for f in training_forms(lexicon, forms) for p in parts(f)} - ENGLISH_NAME_PARTS)
        uses = Counter(ch for p in self.train for ch in set(p))
        self.alphabet = {ch for ch, n in uses.items() if n >= MIN_LETTER_PARTS}
        attested = set()
        for e in lexicon:
            if e.get("canon_basis") != "generated":
                attested |= keys(e["word"])
        for f in elven_forms:
            attested |= keys(f["form"])
        for form in extra_attested:
            attested |= keys(form)
        self.pools = {
            "attested": attested,
            "scrambler": set().union(*(keys(w) for w in scrambler_words)) if scrambler_words else set(),
            "control": set().union(*(keys(f["form"]) for f in control_forms)) if control_forms else set(),
            "lexicon": set().union(*(keys(e["word"]) for e in lexicon)) if lexicon else set(),
        }
        self.known = sorted(known_parts(lexicon))
        self.long_parts = sorted({k for k in attested if len(k) >= 4 and k not in self.known})
        self.english = {w for w in english if len(w) >= 3}
        lengths = Counter(len(k) for k in attested)
        self.length_weights = {n: lengths[n] for n in range(1, max(lengths) + 1)}
        self.foreign = dict(foreign)

    def reject(self, word, new_words=()):
        """The first reason the word is rejected, or None if it passes."""
        if set(word) - self.alphabet:
            return "alphabet"
        if word.endswith(("is", "ael")):
            return "ending -is or -ael"
        if not phonotactic(word) or not set(word) & VOWELS:
            return "phonotactics"
        if word in self.english:
            return "English word"
        if word in self.foreign:
            return "word in another language"
        if near(word, self.pools["attested"]):
            return "attested form"
        if any(p in word for p in self.known):
            return "contains a part with a known meaning"
        if any(p in word for p in self.long_parts):
            return "contains an attested part of four letters or more"
        if len(word) >= 4 and any(word in p for p in self.pools["attested"]):
            return "is inside an attested form"
        for name, label in (("scrambler", "scrambler word"), ("control", "Titan or Zandali form")):
            if near(word, self.pools[name]):
                return label
        if near(word, self.pools["lexicon"], symmetric=True):
            return "lexicon word"
        if near(word, set(new_words), symmetric=True):
            return "another new word"
        return None


def training_forms(lexicon, forms):
    """The attested elven forms the model learns from."""
    out = [e["word"] for e in lexicon
           if e.get("source") in ELVEN and e.get("canon_basis") not in ("generated", "unverified")]
    out += [f["form"] for f in forms if f["branch"] not in CONTROLS and f.get("kind") != "scrambler"]
    return out


def known_parts(lexicon):
    """One-part elven entries of three letters or more whose meaning is known (not generated, not unverified, not
    glossed '(unknown ...')."""
    out = set()
    for e in lexicon:
        if e.get("source") not in ELVEN or e.get("canon_basis") in ("generated", "unverified"):
            continue
        if e["translation"]["en"].startswith("(unknown"):
            continue
        letters = re.findall(r"[a-z]+", e["word"].lower())
        if len(letters) == 1 and len(letters[0]) >= 3:
            out.add(letters[0])
    return out


def choose(meaning, kind, model, inventory, new_words, yardstick, samples=SAMPLES):
    """The best-scoring sample for the meaning that passes every filter, with its score and percentile.

    The length is drawn first, from the lengths of the attested words within the kind's range (report 1's length
    matching): the per-character score rewards length, so without it every content word came out at seven letters.
    If no sample of that length passes, the nearest length that has one is used."""
    lo, hi = LENGTHS[kind]
    seed = seed_for(meaning)
    rng = random.Random(seed)
    lengths = list(range(lo, hi + 1))
    target = rng.choices(lengths, [inventory.length_weights.get(n, 0) for n in lengths])[0]
    valid, rejected = defaultdict(set), Counter()
    for _ in range(samples):
        w = model.sample(rng)
        if w is None or not lo <= len(w) <= hi:
            rejected["length"] += 1
            continue
        if w in valid[len(w)]:
            continue
        why = inventory.reject(w, new_words)
        if why:
            rejected[why] += 1
            continue
        valid[len(w)].add(w)
    for n in sorted(lengths, key=lambda n: (abs(n - target), n)):
        if valid[n]:
            best = max(valid[n], key=lambda w: (model.score(w), w))
            break
    else:
        raise RuntimeError(f"no sample for {meaning!r} passes the filters: {dict(rejected)}")
    score = model.score(best)
    return {"word": best, "seed": seed, "samples": samples, "length": target, "score": round(score, 3),
            "percentile": round(percentile(score, yardstick), 1), "valid": len(valid[len(best)]),
            "rejected": dict(rejected)}


def method(choice, meaning):
    return (f"generate_words.py: order-4 Kneser-Ney character model, best of {choice['samples']} samples, "
            f"seed {choice['seed']} "
            f"(SHA-256 of '{meaning}'); {choice['score']:.2f} nats per character, at percentile "
            f"{choice['percentile']:.0f} of the attested parts")


# ---------------------------------------------------------------------------------------------------------------------
# Inputs


def phono_list(name):
    """A word list that phono.py holds as a string constant (UNTR: untranslated attested phrases; parser: the wiki's
    Thalassian word parser, a scrambler list). phono.py runs on import, so its source is read instead."""
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "phono.py"), encoding="utf-8") as fh:
        src = fh.read()
    return re.search(name + r' = """(.*?)"""', src, re.S).group(1).split()


def load_inputs(lexicon_path=LEX):
    with open(lexicon_path, encoding="utf-8") as fh:
        lexicon = json.load(fh)
    with open(FORMS, encoding="utf-8") as fh:
        forms = json.load(fh)
    with open(LANGUAGE_WORDS, encoding="utf-8") as fh:
        scrambler = [r["Word"] for r in csv.DictReader(fh)]
    with open(SCRAMBLERS, encoding="utf-8") as fh:
        scrambler += [x["form"] for x in json.load(fh)]
    scrambler += phono_list("parser")
    english = set()
    for path in ENGLISH:
        with open(path, encoding="utf-8") as fh:
            english |= {w.strip().lower() for w in fh}
    extra = [ph for _, ph, *_ in CORPUS] + phono_list("UNTR")
    return lexicon, Inventory(lexicon, forms, scrambler, english, extra_attested=extra)


# ---------------------------------------------------------------------------------------------------------------------
# The decisions taken on the audit's proposals (report 8, "What was decided")

# Grammar section 5.3: a subject pronoun is the object form used as a free word, so the generated subject pronouns
# go, even where the audit proposed new forms for them.
REMOVE_INSTEAD = {
    "on": "grammar.md section 5.3 makes a subject pronoun the object form used as a free word (o 'I'), so the "
          "generated nominative is removed rather than regenerated.",
    "il'ore": "grammar.md section 5.3 makes a subject pronoun the object form used as a free word (a 'you'), so the "
              "generated pronoun is removed rather than regenerated.",
}

# isera is an attested Darnassian form (Ysera's name, the scrambler word Isera'duna), not a generated word, so
# apply_audit.py cannot regenerate it. The audit's proposal is carried out as a removal plus a generated "green".
REPLACE_UNVERIFIED = {"isera": (173, "green", "green", "зелений", "adjective")}

# Glosses that join two senses (vocab-findings.md section 4): the regenerated word keeps one.
GLOSS_FIXES = {
    "carth": ("work", "працювати",
              "'work/do' joins two senses; 'do' may be Darnassian karath (Ash karath 'Do it'), so 'work' is kept."),
    "ashad": ("find", "знаходити", "'find/seek' joins two senses; the first is kept."),
    "iel": ("love", "любити", "'love/desire' joins two senses; the first is kept."),
    "reom": ("food", "їжа", "'food/bread' joins two senses; the wider one is kept."),
    "isbab": ("fortress", "фортеця",
              "'fortress/house' joins two senses; 'house' overlaps canon thalas 'home' and inferred dor."),
    "dara": ("good", "добрий", "'good/pleasant' joins two senses, and the Ukrainian dropped 'pleasant'; 'good' "
                               "(Swadesh-207 item 185) is kept."),
}

# The audit's notes on these compounds say to rebuild them if their part is regenerated; it is.
REBUILD = {"thas'ore": ("ore", "thas'{}"), "rashis'ael": ("rashis", "{}'ael")}

FUNCTION_WORDS = {"era", "ore"}  # this, one: a demonstrative and a number, so 2 to 4 letters

# One-line reasons for the notes the lexicon keeps ("Replaced <old>: <why> (November 2026 audit).") and for the log.
WHY = {
    "carth": "a poor fit ('rth' is in no attested form), and an echo of Darnassian karath 'do it'",
    "iel": "iel was also the Swadesh words' suffix 'small' and the end of canon dinoriel, so thas'iel read "
           "'forest-love'",
    "ashad": "one letter from ashal (Selama ashal'anore) and from Shalassian ashar 'duel'",
    "sir": "English 'sir', and Ukrainian сир 'cheese'",
    "reom": "a poor fit (the vowel pair 'eo' is in no attested form)",
    "isbab": "a poor fit (final -b and 'bab' are almost absent from attested forms)",
    "dara": "a night elf and Skyborne name in the game's name generator, one letter from Shalassian dora 'thanks'",
    "nubu": "the least canon-like invented word, one letter from the Orcish scrambler word nobu",
    "morn": "Sindarin (Tolkien) for 'black, dark' and English 'morning', one letter from canon morin",
    "san": "the san of Shalassian Shal'san Tora, an untranslated line",
    "ubelala": "initial u- and 'lala' are in no attested word, and it held bel- of belore 'sun'",
    "sindor": "sin 'blood' + dor 'land' read 'blood-land', like Sin'dorei",
    "felash": "it read fel + ash, 'fire-ash'",
    "talu": "it began with tal 'death' and was one letter from Shalassian tanu",
    "llarana": "initial ll- is in no attested word, and it was one letter from the Skyborne name Larana",
    "ururann": "a poor fit ('uru' is in no attested form)",
    "onar": "one letter from canon anar 'by'",
    "tora": "the Tora of Shalassian Shal'san Tora, an untranslated line; it also reads as Torah",
    "lanelot": "one letter from 'Lancelot', and a poor fit",
    "era": "the Era of the untranslated Nazja line Era'sazjar!, and English 'era'",
    "ore": "ore ends six canon words (belore, anore, malanore ...), inviting parses such as bel-ore; English 'ore'",
    "dorin": "one letter from Darnassian dorini (Anu'dorini talah), with an invented singular -in on dorei",
    "thas'nor": "canon nor is 'heavens', so thas'nor read 'forest-heavens'",
    "dris'al": "al 'the/of' is invented, and dris'al was one letter from dris'ael 'see'",
    "rashis": "it reads as Ukrainian рашист, a wartime pejorative",
    "oris": "Latin oris 'of the mouth'",
    "talor": "one letter from canon falor 'chill', and it began with tal 'death'",
    "shalis": "it gave shal- the invented sense 'stride'; canon shal is 'night, shadow'",
    "ethis": "one letter from ethil, a part of the shared core (Ande'thoras-ethil)",
    "thalis": "it gave thalas the invented sense 'hearth', and was one letter from thalas",
    "lura'sin": "lura is 'sea' and sin 'blood', so it read 'sea-blood', a noun",
    "elara": "one letter from Darnassian alara (Alara'shinu), and built on el, a removed mis-segmentation",
    "ishari": "it held the scrambler word Shari, the reason shari was removed in November",
    "ish'thero": "canon thero is 'student', so it read '(inner) student', a noun",
    "anor'ael": "anor is the Suramar place name Tel'anor, one letter from anar and anore",
    "thas'ore": "it was built on ore 'one', which was regenerated",
    "rashis'ael": "it was built on rashis 'nose', which was regenerated",
    # removals
    "sira": "it duplicated sir 'day', is the first part of the naga group Sira'kess, and reads as Ukrainian сіра "
            "'grey'",
    "thala": "it is the attested Shalassian thala (Thala nar'valas, untranslated), and duplicated anor'ael 'live'",
    "mith": "it duplicated canon anaria 'speak/say', and is Sindarin for 'grey'",
    "doras": "it duplicated ishari 'know', and was one letter from dora, dorah and doral",
    "fa": "it duplicated thas'ore 'tree', and its Ukrainian added 'forest' (canon thas)",
    "tala": "it duplicated dris'ael 'see', and was one letter from canon tal and talah",
    "selorue": "it duplicated thelis'ael 'hear', and held canon elor 'sleep'",
    "al'ore": "it rested on an invented anu 'self', duplicated on 'I', and was one letter from adore and anore",
    "nath": "it duplicated la 'not', was one letter from Darnassian anath, and is part of the Orcish scrambler word "
            "Gul'nath",
    "on": "grammar section 5.3 uses the object form o as the subject; on is also English, and Russian он 'he'",
    "il'ore": "grammar section 5.3 uses the object form a as the subject; il- 'you' and ore 'one' were invented",
    "isera": "it is Ysera's name and part of the scrambler word Isera'duna, with the guess 'green'; 'green' gets a "
             "generated word",
}

# Swadesh-207 meanings that coverage.json lists as missing ("he" is covered by 'dan): item, meaning, English gloss,
# Ukrainian gloss, part of speech, kind. Question words, conjunctions, numbers, demonstratives and the two
# prepositions are function words.
SWADESH_ADDS = (
    (8, "that", "that", "той", "pronoun", "function"),
    (9, "here", "here", "тут", "adverb", "function"),
    (12, "what", "what", "що", "pronoun", "function"),
    (13, "where", "where", "де", "adverb", "function"),
    (14, "when", "when", "коли", "adverb", "function"),
    (18, "many", "many", "багато", "adjective", "content"),
    (19, "some", "some", "деякі", "adjective", "content"),
    (20, "few", "few", "небагато", "adjective", "content"),
    (21, "other", "other", "інший", "adjective", "content"),
    (24, "three", "three", "три", "adjective", "function"),
    (25, "four", "four", "чотири", "adjective", "function"),
    (26, "five", "five", "п'ять", "adjective", "function"),
    (27, "big", "big", "великий", "adjective", "content"),
    (29, "wide", "wide", "широкий", "adjective", "content"),
    (30, "thick", "thick", "товстий", "adjective", "content"),
    (33, "short", "short", "короткий", "adjective", "content"),
    (34, "narrow", "narrow", "вузький", "adjective", "content"),
    (35, "thin", "thin", "тонкий", "adjective", "content"),
    (37, "man (adult male)", "man (adult male)", "чоловік", "noun", "content"),
    (40, "wife", "wife", "дружина", "noun", "content"),
    (41, "husband", "husband", "чоловік (у шлюбі)", "noun", "content"),
    (44, "animal", "animal", "тварина", "noun", "content"),
    (48, "louse", "louse", "воша", "noun", "content"),
    (49, "snake", "snake", "змія", "noun", "content"),
    (50, "worm", "worm", "черв'як", "noun", "content"),
    (53, "stick", "stick", "палиця", "noun", "content"),
    (54, "fruit", "fruit", "плід", "noun", "content"),
    (58, "bark (of a tree)", "bark (of a tree)", "кора", "noun", "content"),
    (59, "flower", "flower", "квітка", "noun", "content"),
    (60, "grass", "grass", "трава", "noun", "content"),
    (61, "rope", "rope", "мотузка", "noun", "content"),
    (66, "fat (noun)", "fat (noun)", "жир", "noun", "content"),
    (68, "horn", "horn", "ріг", "noun", "content"),
    (69, "tail", "tail", "хвіст", "noun", "content"),
    (79, "fingernail", "fingernail", "ніготь", "noun", "content"),
    (82, "knee", "knee", "коліно", "noun", "content"),
    (86, "guts", "guts", "нутрощі", "noun", "content"),
    (88, "back", "back (of the body)", "спина", "noun", "content"),
    (89, "breast", "breast", "груди", "noun", "content"),
    (91, "liver", "liver", "печінка", "noun", "content"),
    (95, "to suck", "suck", "смоктати", "verb", "content"),
    (96, "to spit", "spit", "плювати", "verb", "content"),
    (97, "to vomit", "vomit", "блювати", "verb", "content"),
    (112, "to hunt", "hunt", "полювати", "verb", "content"),
    (114, "to cut", "cut", "різати", "verb", "content"),
    (115, "to split", "split", "розколювати", "verb", "content"),
    (116, "to stab", "stab", "колоти", "verb", "content"),
    (117, "to scratch", "scratch", "дряпати", "verb", "content"),
    (118, "to dig", "dig", "копати", "verb", "content"),
    (119, "to swim", "swim", "плавати", "verb", "content"),
    (122, "to come", "come", "приходити", "verb", "content"),
    (123, "to lie (as in a bed)", "lie (down)", "лежати", "verb", "content"),
    (124, "to sit", "sit", "сидіти", "verb", "content"),
    (126, "to turn (intransitive)", "turn (around)", "повертатися", "verb", "content"),
    (127, "to fall", "fall", "падати", "verb", "content"),
    (128, "to give", "give", "давати", "verb", "content"),
    (129, "to hold", "hold", "тримати", "verb", "content"),
    (130, "to squeeze", "squeeze", "стискати", "verb", "content"),
    (131, "to rub", "rub", "терти", "verb", "content"),
    (132, "to wash", "wash", "мити", "verb", "content"),
    (133, "to wipe", "wipe", "витирати", "verb", "content"),
    (134, "to pull", "pull", "тягнути", "verb", "content"),
    (135, "to push", "push", "штовхати", "verb", "content"),
    (136, "to throw", "throw", "кидати", "verb", "content"),
    (137, "to tie", "tie", "зв'язувати", "verb", "content"),
    (138, "to sew", "sew", "шити", "verb", "content"),
    (139, "to count", "count", "рахувати", "verb", "content"),
    (141, "to sing", "sing", "співати", "verb", "content"),
    (142, "to play", "play", "грати", "verb", "content"),
    (143, "to float", "float", "триматися на воді", "verb", "content"),
    (144, "to flow", "flow", "текти", "verb", "content"),
    (146, "to swell", "swell", "набрякати", "verb", "content"),
    (148, "moon", "moon", "місяць", "noun", "content"),
    (150, "water", "water", "вода", "noun", "content"),
    (151, "rain", "rain", "дощ", "noun", "content"),
    (152, "river", "river", "річка", "noun", "content"),
    (153, "lake", "lake", "озеро", "noun", "content"),
    (155, "salt", "salt", "сіль", "noun", "content"),
    (157, "sand", "sand", "пісок", "noun", "content"),
    (158, "dust", "dust", "пил", "noun", "content"),
    (160, "cloud", "cloud", "хмара", "noun", "content"),
    (161, "fog", "fog", "туман", "noun", "content"),
    (165, "ice", "ice", "лід", "noun", "content"),
    (166, "smoke", "smoke", "дим", "noun", "content"),
    (168, "ash", "ash", "попіл", "noun", "content"),
    (169, "to burn", "burn", "горіти", "verb", "content"),
    (171, "mountain", "mountain", "гора", "noun", "content"),
    (174, "yellow", "yellow", "жовтий", "adjective", "content"),
    (179, "year", "year", "рік", "noun", "content"),
    (180, "warm", "warm", "теплий", "adjective", "content"),
    (182, "full", "full", "повний", "adjective", "content"),
    (186, "bad", "bad", "поганий", "adjective", "content"),
    (187, "rotten", "rotten", "гнилий", "adjective", "content"),
    (188, "dirty", "dirty", "брудний", "adjective", "content"),
    (189, "straight", "straight", "прямий", "adjective", "content"),
    (190, "round", "round", "круглий", "adjective", "content"),
    (191, "sharp (as a knife)", "sharp (as a knife)", "гострий", "adjective", "content"),
    (192, "dull (as a knife)", "dull (as a knife)", "тупий", "adjective", "content"),
    (193, "smooth", "smooth", "гладкий", "adjective", "content"),
    (194, "wet", "wet", "мокрий", "adjective", "content"),
    (195, "dry", "dry", "сухий", "adjective", "content"),
    (196, "correct (right)", "correct", "правильний", "adjective", "content"),
    (197, "near", "near", "близько", "adverb", "content"),
    (198, "far", "far", "далеко", "adverb", "content"),
    (199, "right (side)", "right (side)", "правий", "adjective", "content"),
    (200, "left", "left (side)", "лівий", "adjective", "content"),
    (201, "at", "at", "біля, при", "preposition", "function"),
    (202, "in", "in", "у, в", "preposition", "function"),
    (205, "if", "if", "якщо", "conjunction", "function"),
    (206, "because", "because", "бо, тому що", "conjunction", "function"),
    (207, "name", "name", "ім'я", "noun", "content"),
)
PROCLITICS = {"at", "in"}

# The object clitics of grammar section 5.1 [invented]: (word, English, Ukrainian, Swadesh item or None).
CLITICS = (
    ("'a", "you (2nd person object enclitic)", "тебе, вас (енклітика)", None,
     "Object enclitic, joined to the verb by an apostrophe (dela'a 'guides you'). Before the verb, the free form a is "
     "the subject 'you' (grammar section 5.3). No Thalassian form for 'you' is attested."),
    ("'dan", "him, her, it, them (3rd person object enclitic)", "його, її, їх (енклітика)", 3,
     "Object enclitic, joined to the verb by an apostrophe (dela'dan 'guides them'), for every gender, number and "
     "role (grammar section 10, item 3). Before the verb, the free form dan is the subject (section 5.3). Covers "
     "Swadesh-207 item 3, 'he'."),
)

MAL = {
    "action": "add", "word": "mal", "translation": {"en": "your (possessive, before the noun)", "uk": "твій, ваш"},
    "pos": "pronoun", "canon": False, "root": "mal",
    "notes": "Elu'meniel mal alann = May peace calm your heart; alann = heart, so mal = your by elimination.",
    "source": "thalassian", "canon_basis": "inferred", "confidence": "low",
    "method": "cross-situational alignment (elimination)",
    "evidence": [{"quote": "Elu'meniel mal alann = May peace calm your heart.",
                  "where": "https://warcraft.wiki.gg/wiki/Thalassian#Thalassian_primer_(official_translations)"}],
    "reason": "Held back again. November held mal at low confidence (1-candidates.json; merge-log.md, 'Held back') "
              "because its meaning rests on elimination within one phrase. That still holds: the in-game line "
              "(BroadcastText 302501, report 4) confirms the form but not its meaning, and the split is not unique, "
              "since Thalassian often leaves 'your' unsaid (Anaria shola 'Speak your business'), so mal could as well "
              "be 'calm'. grammar.md section 5.2 keeps mal as [canon, weak].",
    "summary": "its meaning still rests on elimination within one phrase",
}


def short(word):
    return WHY[key(word)]


def finding_evidence(c):
    """The audit's evidence for a candidate, plus where the finding is written up."""
    return list(c.get("evidence", [])) + [{"quote": "November 2026 vocabulary audit: " + ", ".join(c["findings"]),
                                           "where": FINDINGS}]


def generated_entry(word, en, uk, pos, notes, confidence, method_text, evidence):
    return {"word": word, "translation": {"en": en, "uk": uk}, "pos": pos, "canon": False, "root": word,
            "notes": notes, "source": "generated", "canon_basis": "generated", "confidence": confidence,
            "method": method_text, "evidence": evidence}


def build(lexicon, inventory, audit, yardstick=None, samples=SAMPLES):
    """Every action of report 8, in the order apply_audit.py logs them. Generation follows the same order, so each
    new word is checked against the ones drawn before it."""
    model = KneserNey(inventory.train)
    yardstick = yardstick if yardstick is not None else loo_scores(inventory.train)
    entries = {(key(e["word"]), e["source"]): e for e in lexicon}
    new_words = [w.strip("'") for w, *_ in CLITICS]
    regenerated = {}
    out = []

    def draw(meaning, kind):
        choice = choose(meaning, kind, model, inventory, new_words, yardstick, samples)
        new_words.append(choice["word"])
        return choice

    for c in audit:
        word, act = key(c["word"]), c["action"]
        base = {"word": c["word"], "source": c["source"]}
        if act == "remove" or (act == "regenerate" and (word in REMOVE_INSTEAD or word in REPLACE_UNVERIFIED)):
            reason = c["reason"]
            if word in REMOVE_INSTEAD:
                reason = REMOVE_INSTEAD[word] + " Audit: " + reason
            out.append(dict(base, action="remove", canon_basis=c["canon_basis"], meaning=c["meaning"],
                            confidence=c["confidence"], reason=reason, summary=short(word),
                            evidence=finding_evidence(c)))
            if word in REPLACE_UNVERIFIED:
                n, meaning, en, uk, pos = REPLACE_UNVERIFIED[word]
                choice = draw(meaning, "content")
                note = (f"Replaced {c['word']}: {short(word)} (November 2026 audit). Swadesh-207 item {n}.")
                out.append(dict(generated_entry(choice["word"], en, uk, pos, note, c["confidence"],
                                                method(choice, meaning), finding_evidence(c)),
                                action="add", swadesh=n, reason=c["reason"], summary=en,
                                score=choice["score"], percentile=choice["percentile"]))
        elif act == "fix":
            for f in [c] + c.get("also_fix", []):
                out.append(dict(base, action="fix", field=f["field"], old=f["old"], new=f["new"],
                                confidence=c["confidence"], reason=c["reason"], evidence=list(c.get("evidence", []))))
        elif act == "note" and word in REBUILD:
            part, pattern = REBUILD[word]
            new = pattern.format(regenerated[part])
            entry = entries[(word, c["source"])]
            out.append(dict(base, action="regenerate", new=new, confidence=c["confidence"],
                            method=f"rebuilt with the regenerated {part} -> {regenerated[part]} (generate_words.py)",
                            notes=f"Replaced {c['word']}: {short(word)} (November 2026 audit).",
                            reason=c["reason"], summary=short(word), evidence=finding_evidence(c),
                            meaning=entry["translation"]["en"]))
            new_words.append(new)
        elif act == "note":
            out.append(dict(base, action="note", confidence=c["confidence"], reason=c["reason"],
                            evidence=list(c.get("evidence", []))))
        elif act == "regenerate" and c["confidence"] not in ("high", "medium"):
            out.append(dict(base, action="regenerate", new=None, confidence=c["confidence"], reason=c["reason"],
                            summary=c["reason"].split(". ")[0], evidence=finding_evidence(c), meaning=c["meaning"]))
        elif act == "regenerate":
            entry = entries[(word, c["source"])]
            en = entry["translation"]["en"]
            if word in GLOSS_FIXES:
                en, uk, why = GLOSS_FIXES[word]
                new_tr = {"en": en, "uk": uk}
                if entry["translation"] != new_tr:
                    out.append(dict(base, action="fix", field="translation", old=entry["translation"], new=new_tr,
                                    confidence=c["confidence"], reason=why,
                                    evidence=[{"quote": "Glosses that join two senses: " + entry["translation"]["en"],
                                               "where": FINDINGS + "#4-sense-problems"}]))
            choice = draw(en, "function" if word in FUNCTION_WORDS else "content")
            regenerated[word] = choice["word"]
            out.append(dict(base, action="regenerate", new=choice["word"], confidence=c["confidence"],
                            method=method(choice, en), notes=f"Replaced {c['word']}: {short(word)} "
                                                              "(November 2026 audit).",
                            reason=c["reason"], summary=short(word), evidence=finding_evidence(c), meaning=en,
                            score=choice["score"], percentile=choice["percentile"]))
        else:
            raise ValueError(f"{c['word']}: unknown audit action {act!r}")

    for word, en, uk, n, notes in CLITICS:
        convention = "invented by convention: docs/methodology/grammar.md section 5.1 (no generator, no seed)"
        out.append(dict(generated_entry(word, en, uk, "pronoun", notes, "medium", convention, []),
                        action="add", swadesh=n, reason="grammar.md section 5.1 lists it as the invented object form.",
                        summary=en))
    out.append(dict(MAL))
    for n, meaning, en, uk, pos, kind in SWADESH_ADDS:
        choice = draw(meaning, kind)
        notes = f"Swadesh-207 item {n}, missing before the November 2026 audit (report 8)."
        if meaning in PROCLITICS:
            notes += (" A proclitic: join it to the next word with an apostrophe, as anar' 'by' (grammar section 10, "
                      "item 13).")
        out.append(dict(generated_entry(choice["word"], en, uk, pos, notes, "medium", method(choice, meaning), []),
                        action="add", swadesh=n, reason=f"Swadesh-207 item {n} ('{meaning}') had no entry.",
                        summary=en, score=choice["score"], percentile=choice["percentile"]))
    return out


def coverage_counts(coverage, candidates):
    """Swadesh-207 statuses before and after the candidates (high and medium confidence only)."""
    applied = [c for c in candidates if c["confidence"] in ("high", "medium")]
    removed = {key(c["word"]) for c in applied if c["action"] == "remove"}
    added = {c["swadesh"] for c in applied if c["action"] == "add" and c.get("swadesh")}
    after = Counter()
    for row in coverage["rows"]:
        status = row["status"]
        if row["n"] in added and status in ("missing", "unverified_only"):
            status = "invented_only"
        elif status == "invented_only" and all(key(w["word"]) in removed for w in row["invented"]):
            status = "missing"
        after[status] += 1
    return dict(Counter(r["status"] for r in coverage["rows"])), dict(after)


def main():
    with open(LOG, encoding="utf-8") as fh:
        from apply_audit import MARK
        if MARK in fh.read():
            sys.exit("8-candidates.json is already applied (see merge-log.md). Rebuild the lexicon up to "
                     "apply_voice.py first (merge_candidates.py's docstring), then run this script.")
    lexicon, inventory = load_inputs()
    with open(AUDIT, encoding="utf-8") as fh:
        audit = json.load(fh)["candidates"]
    with open(COVERAGE, encoding="utf-8") as fh:
        coverage = json.load(fh)
    missing = {r["meaning"] for r in coverage["rows"] if r["status"] == "missing"}
    assert missing - {"he"} == {m for _, m, *_ in SWADESH_ADDS}, missing ^ {m for _, m, *_ in SWADESH_ADDS}
    candidates = build(lexicon, inventory, audit)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(candidates, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("actions:", dict(Counter((c["action"], c["confidence"]) for c in candidates)))
    before, after = coverage_counts(coverage, candidates)
    print("Swadesh-207 before:", before)
    print("Swadesh-207 after: ", after)
    for c in candidates:
        if c["action"] in ("add", "regenerate") and c.get("score") is not None:
            print(f"  {c['action']:10s} {c.get('word', ''):12s} -> {c.get('new') or c['word']:10s} "
                  f"{c.get('meaning') or c['translation']['en']:22s} {c['score']:7.3f} {c['percentile']:5.1f}")


if __name__ == "__main__":
    main()
