#!/usr/bin/env python3
"""Rank Elvish-looking tokens in the client corpus that are not in lexicon.json.

  python3 -I tools/wowf/mine_tokens.py --base .wowf-extract \
      --lexicon src/thalassian/data/lexicon.json --out .wowf-extract/analysis/client_tokens.csv

Scoring: a character-trigram naive Bayes model. Positive class: the game's own
Elvish garble lists (LanguageWords for Darnassian 2, Thalassian 10 and
Shen'dorei 310), the Skyborne name generator lists (NameGen races 95/96, only
single-word entries that are not English) and the canon Elvish lexicon entries.
Negative class: the garble lists of every other language plus a sample of
English dictionary words. A token's score is the mean per-trigram log-odds.
Flags add what the model cannot see: inner apostrophe, known Elvish affixes,
whether the token is a LanguageWords garble word, and gloss cues in context.
"""
import argparse
import csv
import json
import math
import os
import random
import re
from collections import Counter, defaultdict

csv.field_size_limit(1 << 30)
TOKEN = re.compile(r"[A-Za-zÀ-ÿ]+(?:['’][A-Za-zÀ-ÿ]+)*")
CAMEL = re.compile(r"[A-Z][a-zà-ÿ]+|[a-zà-ÿ]+")
CONTRACTION = re.compile(r"^[a-z]+'(s|t|ll|re|ve|d|m)$")
NOISE_TABLES = {"ManifestInterfaceData", "Hotfixes", "UiTextureAtlasElement", "UiTextureAtlasMember",
                "WorldStateExpression", "ChatProfanity", "NamesProfanity", "LanguageWords",
                "UiTextureKit", "Cfg_Regions", "Cfg_Categories", "Cfg_Languages", "Cfg_Timezones",
                "SoundEmitters", "UiModelSceneActor", "UiWidgetVisualization", "UiWidgetVisTypeDataReq",
                "SpellVisualEffectName", "UiMapAssignment", "ModelFileData", "TextureFileData",
                "SceneScriptText", "SceneScriptGlobalText", "SceneScriptPackage", "SpellDescriptionVariables",
                "BattlepayCurrency", "WbAccessControlList", "ConfigurationWarning", "LightSkybox", "GameMode",
                "ClientSettings", "SoundMixGroup", "ScreenEffect", "SpellMissileMotion", "CollectableSourceInfo"}
NOISE_FIELDS = {"BaseTag", "ZoneName", "ClientPrefix", "ClientFileString"}
ELVISH_LANGS = {"2", "10", "310"}
AFFIXES = ["dorei", "thalas", "thas", "alah", "belore", "quel", "sin'", "kal'", "shal", "shan", "aran",
           "anar", "anu", "ore", "dor", "iel", "ath", "ashal", "ama", "shen", "thal", "aessina", "drassil",
           "nar", "aal", "aan", "ael", "ilas", "elun", "falla", "ethil"]
GLOSS_CUES = re.compile(r"\b(mean(s|ing)?|translat\w*|tongue|language|word for|called|known as|"
                        r"thalassian|darnassian|shen'dorei|elvish|elven|in the old)\b", re.I)


def norm(t):
    return t.replace("’", "'").lower()


def trigrams(w):
    w = "^" + w + "$"
    return [w[i:i + 3] for i in range(len(w) - 2)]


class NB(object):
    """Trigram naive Bayes; each class model is interpolated with the pooled
    distribution so trigrams neither class has seen score close to zero."""

    def __init__(self, pos, neg, lam=0.7):
        self.p = Counter()
        self.n = Counter()
        for w in pos:
            self.p.update(trigrams(w))
        for w in neg:
            self.n.update(trigrams(w))
        self.pt = sum(self.p.values())
        self.nt = sum(self.n.values())
        self.v = len(set(self.p) | set(self.n)) + 1
        self.lam = lam

    def score(self, w):
        g = trigrams(w)
        s = 0.0
        for t in g:
            bg = (self.p[t] + self.n[t] + 1.0) / (self.pt + self.nt + self.v)
            pp = self.lam * self.p[t] / self.pt + (1 - self.lam) * bg
            pn = self.lam * self.n[t] / self.nt + (1 - self.lam) * bg
            s += math.log(pp) - math.log(pn)
        return s / max(1, len(g))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", required=True)
    ap.add_argument("--lexicon", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--words", default="/usr/share/dict/words")
    a = ap.parse_args(argv)
    random.seed(7)
    lex = json.load(open(a.lexicon, encoding="utf-8"))
    lexwords = {norm(e["word"]) for e in lex}
    lexparts = set()
    for w in lexwords:
        lexparts.update(p for p in w.split("'") if p)
    english = {w.strip().lower() for w in open(a.words, encoding="utf-8", errors="replace") if w.strip()}

    # ---- training data from the client itself ----
    lw = list(csv.DictReader(open(os.path.join(a.base, "LanguageWords.csv"), encoding="utf-8")))
    garble = defaultdict(set)
    for r in lw:
        garble[r["LanguageID"]].add(norm(r["Word"]))
    elvish_garble = set().union(*[garble[k] for k in ELVISH_LANGS])
    pos = set(w for w in elvish_garble if len(w) > 2)
    ng = os.path.join(a.base, "db2", "NameGen.csv")
    if os.path.exists(ng):
        for r in csv.DictReader(open(ng, encoding="utf-8")):
            if r["RaceID"] in ("95", "96") and norm(r["Name"]) not in english and " " not in r["Name"]:
                pos.add(norm(r["Name"]))
    for e in lex:
        if e.get("canon") and e.get("source") in ("thalassian", "darnassian", "shalassian"):
            pos.add(norm(e["word"]))
    neg = set()
    for k, ws in garble.items():
        if k not in ELVISH_LANGS:
            neg.update(w for w in ws if len(w) > 2)
    eng_sample = random.sample(sorted(w for w in english if len(w) > 3), 30000)
    neg.update(eng_sample)
    model = NB(sorted(pos), sorted(neg))

    # ---- tokens from the corpus ----
    stats = {}
    with open(os.path.join(a.base, "corpus.jsonl"), encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r.get("table") in NOISE_TABLES or r.get("field") in NOISE_FIELDS:
                continue
            text = r["text"]
            toks = []
            for m in TOKEN.finditer(text):
                t = m.group(0)
                if "'" not in t and "’" not in t and re.search(r"[a-z][A-Z]", t):
                    toks += CAMEL.findall(t)  # internal names such as ZephrasIsle
                else:
                    toks.append(t)
            for t in toks:
                k = norm(t)
                if len(k) < 3 or CONTRACTION.match(k) or re.search(r"[A-Z]{2}", t) or "cff" in k:
                    continue
                if not re.search(r"[aeiouy]", k):
                    continue
                if k.endswith("'s"):
                    k = k[:-2]
                    t = t[:-2]
                if "'" not in k and k in english:
                    continue
                st = stats.get(k)
                if st is None:
                    st = stats[k] = {"token": t, "count": 0, "tables": Counter(), "where": [], "contexts": [],
                                     "gloss_contexts": []}
                st["count"] += 1
                st["tables"][r.get("table") or r["src"]] += 1
                if len(st["where"]) < 6:
                    st["where"].append(r["where"])
                    st["contexts"].append(text[:300])
                if GLOSS_CUES.search(text) and len(st["gloss_contexts"]) < 3:
                    st["gloss_contexts"].append("%s :: %s" % (r["where"], text[:400]))
    rows = []
    for k, st in stats.items():
        parts = [p for p in k.split("'") if p]
        in_lex = k in lexwords
        parts_in_lex = bool(parts) and all(p in lexwords or p in lexparts for p in parts)
        score = model.score(k)
        affix = [x for x in AFFIXES if x in k]
        rows.append({
            "token": st["token"], "norm": k, "score": round(score, 3), "count": st["count"],
            "apostrophe": int("'" in k), "affixes": " ".join(affix),
            "in_lexicon": int(in_lex), "parts_in_lexicon": int(parts_in_lex and not in_lex),
            "garble_word": ",".join(sorted(lang for lang, ws in garble.items() if k in ws)),
            "tables": " ".join("%s:%d" % kv for kv in st["tables"].most_common(6)),
            "where": " | ".join(st["where"]), "contexts": " || ".join(st["contexts"][:3]),
            "gloss_contexts": " || ".join(st["gloss_contexts"]),
        })
    rows.sort(key=lambda r: -r["score"])
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("tokens", len(rows), "positive", len(pos), "negative", len(neg))


if __name__ == "__main__":
    main()
