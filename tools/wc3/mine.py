#!/usr/bin/env python3
"""Find elvish words and phrases in the Warcraft III text extract.

  python3 -I tools/wc3/mine.py --base .wc3-extract --lexicon src/thalassian/data/lexicon.json \
      [--wowf .wowf-extract] [--wiki Thalassian.txt Darnassian.txt]

Reads what extract_text.py wrote and writes, under <base>/analysis/:
  records.tsv   every structured text record (unit voice subtitles, map string tables with their
                speaker and sound file, cinematic subtitles, other text lines)
  hits.tsv      records holding at least one elvish-looking token, with the flags that fired
  tokens.tsv    one row per elvish-looking token: count, flags, lexicon / wiki status, first places
  locales.tsv   for every map string-table hit, the same string in the 13 other locales the maps carry
  audio.tsv     voice files of elven speakers: unit voice sets and campaign dialogue, with sizes

A token counts as elvish-looking when it is not an English dictionary word and at least one of
these holds: it or one of its apostrophe/hyphen parts is a lexicon form (lex); it contains a known
elvish root (root); the speaker is an elf (elf); it is joined by an apostrophe or hyphen (joined);
or a character-trigram model trained on Blizzard's elvish forms scores it high (model). Names and
English words pass too; the report separates them by hand.
Standard library only, Python 3.9 compatible.
"""
import argparse
import csv
import json
import math
import os
import random
import re
from collections import Counter, defaultdict

TOKEN = re.compile(r"[A-Za-zÀ-ÿ]+(?:['’\-][A-Za-zÀ-ÿ]+)*")
CONTRACTION = re.compile(r"^[a-z]+'(s|t|ll|re|ve|d|m)$")
ROOTS = ["dorei", "quel", "thalas", "belore", "anar", "alah", "shan", "adore", "ishnu", "andu", "fallah",
         "falah", "shorel", "aran", "elune", "elun", "kaldorei", "sindorei", "sin'dorei", "thero", "ashal",
         "selama", "dora", "shindu", "bal'a", "anu", "thoras", "ethil", "dieb", "ishera", "endo", "enah",
         "aseph", "balla", "thera", "doral", "manore", "thas", "drassil", "kalimdor", "zin", "azshar",
         "suramar", "nordrassil", "teldrassil", "shalla", "alon", "ilisar", "bandu", "fandu", "karath"]
ELF_SPEAKER = re.compile(
    r"BLOODELF|BLOOD_ELF|SYLVANAS|KAEL|SPELLBREAKER|NIGHTELF|NAISHA|DARKRANGER|BANSHEE|MAIEV|SHANDRIS|"
    r"TYRANDE|ILLIDAN|FURION|MALFURION|WARDEN|PRIESTESS|SENTINEL|HUNTRESS|ARCHER|DRUID|DEMON_HUNTER|"
    r"FORSAKENRANGER|HIGHELF|HIGH_ELF|\bELF\b|\bELVES\b|VEREESA|ALLERIA|LIADRIN|ANASTERIAN|ROMMATH|"
    r"LOR'THEMAR|LORTHEMAR|DATH'REMAR", re.I)
# campaign speaker unit IDs of elves (Warcraft III raw codes)
ELF_UNIT_IDS = {
    "Hkal": "Kael'thas", "Hvwd": "Sylvanas", "Hvsh": "Lady Vashj", "Uvng": "Sylvanas (banshee)",
    "Etyr": "Tyrande", "Efur": "Furion", "Ekgg": "Malfurion", "Eill": "Illidan", "Eevi": "Illidan (demon)",
    "Ewrd": "Maiev", "Ewar": "Warden", "Eshd": "Shandris", "Emoo": "Priestess of the Moon",
    "Edem": "Demon Hunter", "Ekee": "Keeper of the Grove", "Ecen": "Cenarius", "Ekgg2": "Malfurion",
    "Hblm": "Blood Mage", "hspt": "Spell Breaker", "hdhw": "Dragonhawk Rider", "nhea": "High Elf Archer",
    "nhef": "High Elf Female", "nhem": "High Elf Male", "nbee": "Blood Elf Engineer", "nbel": "Blood Elf",
    "Udth": "Sylvanas", "Usyl": "Sylvanas", "Nbbc": "Kael'thas", "Hgar": "Garithos", "Hvwd2": "Sylvanas",
    "earc": "Archer", "esen": "Huntress", "edry": "Dryad", "edot": "Druid of the Talon",
    "edoc": "Druid of the Claw", "Ntin": "Tinker",
}
GLOSS_CUES = re.compile(r"\b(mean(s|ing)?|translat\w*|tongue|language|word for|called|known as|"
                        r"thalassian|darnassian|elvish|elven tongue|in the old|ancient tongue)\b", re.I)
LOCALES = ["deDE", "esES", "esMX", "frFR", "itIT", "jaJP", "koKR", "plPL", "ptBR", "ruRU", "thTH", "zhCN",
           "zhTW"]
ORCISH_GARBLE_IDS = {"1"}  # Orcish in LanguageWords; used only as negative training data


def norm(t):
    return t.replace("’", "'").lower()


def trigrams(w):
    w = "^" + w + "$"
    return [w[i:i + 3] for i in range(len(w) - 2)]


class NB(object):
    """Character-trigram naive Bayes, as in tools/wowf/mine_tokens.py."""

    def __init__(self, pos, neg, lam=0.7):
        self.p, self.n = Counter(), Counter()
        for w in pos:
            self.p.update(trigrams(w))
        for w in neg:
            self.n.update(trigrams(w))
        self.pt, self.nt = sum(self.p.values()) or 1, sum(self.n.values()) or 1
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


# --------------------------------------------------------------------------
# parsers
# --------------------------------------------------------------------------
def read_text(path):
    with open(path, "rb") as f:
        raw = f.read()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    return raw.decode("utf-8", "replace")


FDF_LINE = re.compile(r'^\s*([A-Za-z0-9_]+)\s+"(.*)",?\s*$')
SLOT = re.compile(r"_(WHAT|YES|YESATTACK|WARCRY|READY|PISSED|DEATH|TAUNT|ATTACK|SPELL|BIRTH|HIT|LOOP|FULL|"
                  r"LOADING|DONE|MORPH|MORPHED|ALTERNATE|ALTERNATEDEATH|CHILDDEATH|DEATHEXPLODE|S|A|D|U|H|L|M|F)"
                  r"\d*$")


def parse_fdf(text):
    for i, line in enumerate(text.splitlines(), 1):
        m = FDF_LINE.match(line)
        if m:
            yield i, m.group(1), m.group(2)


def parse_wts(text):
    """Yield (string id, comment, text) from a war3map.wts / war3campaign.wts string table."""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        m = re.match(r"\s*STRING\s+(\d+)", lines[i])
        if not m:
            i += 1
            continue
        sid = int(m.group(1))
        i += 1
        comment = []
        while i < len(lines) and lines[i].strip() != "{":
            if lines[i].strip().startswith("//"):
                comment.append(lines[i].strip()[2:].strip())
            i += 1
        i += 1
        body = []
        while i < len(lines) and lines[i].rstrip() != "}":
            body.append(lines[i])
            i += 1
        i += 1
        yield sid, " ".join(comment), "\n".join(body)


def parse_srt(text):
    for block in re.split(r"\r?\n\s*\r?\n", text):
        ls = [l for l in block.splitlines() if l.strip()]
        if len(ls) >= 3 and "-->" in ls[1]:
            yield ls[0].strip(), ls[1].strip(), " ".join(ls[2:])


def parse_conversation(path):
    """dialogueId -> (speaker name string id, speaker unit id, sound file, conversation name)."""
    out = {}
    try:
        d = json.loads(read_text(path))
    except ValueError:
        return out
    for conv, items in (d.get("conversation") or {}).items():
        for it in items or []:
            did = it.get("dialogueId")
            if isinstance(did, int):
                out[did] = (it.get("speakerNameId"), it.get("speakerUnitID") or "", it.get("soundFile") or "",
                            conv)
    return out


# --------------------------------------------------------------------------
# records
# --------------------------------------------------------------------------
def collect(base):
    """Yield dicts: kind, file, loc, speaker, unit, sound, text, context."""
    casc_root = os.path.join(base, "casc")
    for dp, _dn, fns in os.walk(casc_root):
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, base)
            text = read_text(p)
            low = fn.lower()
            if low.endswith(".fdf"):
                for ln, key, s in parse_fdf(text):
                    speaker = SLOT.sub("", key) if "_UNIT_" in key else ""
                    yield {"kind": "fdf", "file": rel, "loc": "%s#%s" % (ln, key), "speaker": speaker,
                           "unit": "", "sound": "", "text": s, "context": key}
                continue
            if low.endswith(".srt"):
                for n, tc, s in parse_srt(text):
                    yield {"kind": "srt", "file": rel, "loc": "cue %s %s" % (n, tc), "speaker": "", "unit": "",
                           "sound": "", "text": s, "context": ""}
                continue
            for ln, line in enumerate(text.splitlines(), 1):
                if line.strip():
                    yield {"kind": "text", "file": rel, "loc": str(ln), "speaker": "", "unit": "", "sound": "",
                           "text": line.strip()[:2000], "context": ""}
    maps_root = os.path.join(base, "maps")
    for dp, _dn, fns in os.walk(maps_root):
        if "_Locales" in dp:
            continue
        if "war3map.wts" not in fns and "war3campaign.wts" not in fns and not any(
                f.endswith((".txt", ".fdf", ".j", ".lua")) for f in fns):
            continue
        conv = parse_conversation(os.path.join(dp, "conversation.json")) if "conversation.json" in fns else {}
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, base)
            if fn.endswith(".wts"):
                strings = {sid: (c, s) for sid, c, s in parse_wts(read_text(p))}
                for sid, (comment, s) in strings.items():
                    spk, unit, sound, cname = "", "", "", ""
                    if sid in conv:
                        nid, unit, sound, cname = conv[sid]
                        spk = strings.get(nid, ("", ""))[1] if isinstance(nid, int) else ""
                    yield {"kind": "wts", "file": rel, "loc": "STRING %d" % sid, "speaker": spk, "unit": unit,
                           "sound": sound, "text": s, "context": (comment + " " + cname).strip()}
            elif fn.endswith((".txt", ".fdf", ".j", ".lua", ".toc", ".strings.txt")):
                text = read_text(p)
                for ln, line in enumerate(text.splitlines(), 1):
                    # scripts: only string literals matter; other text: whole line
                    if fn.endswith((".j", ".lua")):
                        lits = re.findall(r'"((?:[^"\\]|\\.)*)"', line)
                        line = " | ".join(l for l in lits if " " in l or "'" in l)
                        if not line:
                            continue
                    if line.strip():
                        yield {"kind": "map-" + fn.rsplit(".", 1)[-1], "file": rel, "loc": str(ln), "speaker": "",
                               "unit": "", "sound": "", "text": line.strip()[:2000], "context": ""}
    facefx_root = os.path.join(base, "facefx")
    for dp, _dn, fns in os.walk(facefx_root):
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, base)
            for ln, line in enumerate(read_text(p).splitlines(), 1):
                if line.strip():
                    yield {"kind": "facefx", "file": rel, "loc": str(ln), "speaker": "", "unit": "", "sound": "",
                           "text": line.strip(), "context": ""}


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def load_lexicon(path):
    lex = json.load(open(path, encoding="utf-8"))
    words, parts, canon_pos = {}, set(), set()
    for e in lex:
        w = norm(e["word"])
        words[w] = e.get("canon_basis") or ""
        if e.get("canon_basis") not in ("generated",) and e.get("source") not in ("generated",
                                                                                    "generated_swadesh"):
            for p in re.split(r"[' \-,!?.]+", w):
                if len(p) >= 3:
                    parts.add(p)
            if e.get("source") in ("thalassian", "darnassian", "shalassian", "skyborne"):
                canon_pos.add(w)
    return lex, words, parts, canon_pos


def load_wiki(paths):
    """Bolded forms and every lowercase token of the wiki language pages."""
    forms, toks = set(), set()
    for p in paths or []:
        if not os.path.exists(p):
            continue
        t = read_text(p)
        for m in re.finditer(r"'''(.+?)'''", t):
            forms.add(norm(re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", m.group(1))).strip(" !.?"))
        for m in TOKEN.finditer(t):
            toks.add(norm(m.group(0)))
    return forms, toks


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", default=".wc3-extract")
    ap.add_argument("--lexicon", default="src/thalassian/data/lexicon.json")
    ap.add_argument("--wowf", default=".wowf-extract", help="optional: WoW garble lists for the model")
    ap.add_argument("--wiki", nargs="*", default=[], help="optional: raw wiki pages (Thalassian, Darnassian)")
    ap.add_argument("--words", nargs="*", default=["/usr/share/dict/words", "/usr/share/dict/web2a"])
    ap.add_argument("--threshold", type=float, default=0.6)
    a = ap.parse_args(argv)
    random.seed(7)
    out_dir = os.path.join(a.base, "analysis")
    os.makedirs(out_dir, exist_ok=True)
    lex, lexwords, lexparts, canon_pos = load_lexicon(a.lexicon)
    wiki_forms, wiki_toks = load_wiki(a.wiki)
    english = set()
    for wp in a.words:
        if os.path.exists(wp):
            for w in open(wp, encoding="utf-8", errors="replace"):
                for x in w.strip().lower().split():
                    english.add(x)

    # model: positive = canon elvish lexicon forms (+ WoW elvish garble words), negative = other garble + English
    pos = set(p for w in canon_pos for p in re.split(r"[' \-]+", w) if len(p) > 2)
    neg = set(random.sample(sorted(w for w in english if len(w) > 3), 30000))
    lw = os.path.join(a.wowf, "LanguageWords.csv")
    if os.path.exists(lw):
        for r in csv.DictReader(open(lw, encoding="utf-8")):
            w = norm(r["Word"])
            if len(w) <= 2:
                continue
            (pos if r["LanguageID"] in ("2", "10", "310") else neg).add(w)
    model = NB(sorted(pos), sorted(neg))

    def english_word(k):
        if k in english:
            return True
        for suf in ("s", "es", "ed", "ing", "ly", "er", "est", "'s"):
            if k.endswith(suf) and k[:-len(suf)] in english:
                return True
        if k.endswith("ied") and k[:-3] + "y" in english:
            return True
        return False

    tokens = {}
    hits = []
    nrec = 0
    with open(os.path.join(out_dir, "records.tsv"), "w", encoding="utf-8") as rf:
        rf.write("kind\tfile\tloc\tspeaker\tunit\tsound\ttext\tcontext\n")
        for r in collect(a.base):
            nrec += 1
            clean = lambda s: s.replace("\t", " ").replace("\n", " \\n ").replace("\r", "")  # noqa: E731
            rf.write("\t".join(clean(str(r[k])) for k in ("kind", "file", "loc", "speaker", "unit", "sound",
                                                            "text", "context")) + "\n")
            text = re.sub(r"\|c[0-9a-fA-F]{8}|\|r|\|n", " ", r["text"])
            elf = bool(ELF_SPEAKER.search(r["speaker"]) or r["unit"] in ELF_UNIT_IDS)
            fired = []
            for m in TOKEN.finditer(text):
                t = m.group(0)
                k = norm(t)
                if k.endswith("'s"):
                    k, t = k[:-2], t[:-2]
                if len(k) < 3 or CONTRACTION.match(k) or re.search(r"[A-Z]{2}", t[1:]) or "_" in t:
                    continue
                if not re.search(r"[aeiouy]", k):
                    continue
                parts = [p for p in re.split(r"['\-]", k) if p]
                joined = len(parts) > 1
                if not joined and english_word(k):
                    continue
                if joined and all(english_word(p) for p in parts):
                    continue
                flags = []
                if k in lexwords or any(p in lexwords or p in lexparts for p in parts if len(p) >= 3):
                    flags.append("lex")
                if any(x in k for x in ROOTS if len(x) >= 4) or any(p in ROOTS for p in parts):
                    flags.append("root")
                if elf:
                    flags.append("elf")
                if joined:
                    flags.append("joined")
                sc = model.score(k.replace("-", "'"))
                if sc > a.threshold:
                    flags.append("model")
                if not flags or flags == ["joined"] and sc < 0:
                    continue
                fired.append((t, k, flags, sc))
                st = tokens.get(k)
                if st is None:
                    st = tokens[k] = {"token": t, "count": 0, "flags": set(), "score": round(sc, 3), "kinds": Counter(),
                                      "where": [], "speakers": Counter(), "gloss": []}
                st["count"] += 1
                st["flags"].update(flags)
                st["kinds"][r["kind"]] += 1
                if r["speaker"]:
                    st["speakers"][r["speaker"]] += 1
                if len(st["where"]) < 5:
                    st["where"].append("%s:%s :: %s" % (r["file"], r["loc"], text[:200]))
                if GLOSS_CUES.search(text) and len(st["gloss"]) < 3:
                    st["gloss"].append("%s:%s :: %s" % (r["file"], r["loc"], text[:300]))
            if fired:
                hits.append((r, fired, elf))

    with open(os.path.join(out_dir, "hits.tsv"), "w", encoding="utf-8") as f:
        f.write("kind\tfile\tloc\tspeaker\tunit\tsound\ttokens\tflags\ttext\tcontext\n")
        for r, fired, _elf in hits:
            f.write("\t".join([r["kind"], r["file"], r["loc"], r["speaker"], ELF_UNIT_IDS.get(r["unit"], r["unit"]),
                               r["sound"], " ".join(t for t, _k, _f, _s in fired),
                               " ".join("%s:%s" % (k, "+".join(fl)) for _t, k, fl, _s in fired),
                               r["text"].replace("\t", " ").replace("\n", " \\n ").replace("\r", ""),
                               r["context"].replace("\t", " ")]) + "\n")
    with open(os.path.join(out_dir, "tokens.tsv"), "w", encoding="utf-8") as f:
        f.write("token\tnorm\tcount\tscore\tflags\tin_lexicon\tlexicon_basis\ton_wiki\tkinds\tspeakers\twhere\tgloss_contexts\n")
        for k, st in sorted(tokens.items(), key=lambda kv: (-len(kv[1]["flags"]), -kv[1]["score"])):
            f.write("\t".join([st["token"], k, str(st["count"]), str(st["score"]), "+".join(sorted(st["flags"])),
                               str(int(k in lexwords)), lexwords.get(k, ""),
                               str(int(k in wiki_toks or k in wiki_forms)),
                               " ".join("%s:%d" % kv for kv in st["kinds"].most_common()),
                               " ".join("%s:%d" % kv for kv in st["speakers"].most_common(4)),
                               " || ".join(st["where"]).replace("\t", " ").replace("\n", " "),
                               " || ".join(st["gloss"]).replace("\t", " ").replace("\n", " ")]) + "\n")
    write_locales(a.base, out_dir, hits)
    write_audio(a.base, out_dir)
    print("records", nrec, "hit records", len(hits), "tokens", len(tokens), "model pos/neg", len(pos), len(neg))


def write_locales(base, out_dir, hits):
    """For each wts hit, the same string id in each locale table the map carries."""
    cache = {}
    with open(os.path.join(out_dir, "locales.tsv"), "w", encoding="utf-8") as f:
        f.write("file\tstring\tlocale\ttext\n")
        for r, _fired, _elf in hits:
            if r["kind"] != "wts":
                continue
            sid = int(r["loc"].split()[1])
            mapdir = os.path.dirname(os.path.join(base, r["file"]))
            name = os.path.basename(r["file"])
            f.write("%s\t%d\tenUS\t%s\n" % (r["file"], sid, r["text"].replace("\n", " \\n ").replace("\t", " ")))
            for loc in LOCALES:
                p = os.path.join(mapdir, "_Locales", loc + ".w3mod", name)
                if p not in cache:
                    cache[p] = ({s: t for s, _c, t in parse_wts(read_text(p))} if os.path.exists(p) else {})
                t = cache[p].get(sid)
                if t is not None:
                    f.write("%s\t%d\t%s\t%s\n" % (r["file"], sid, loc, t.replace("\n", " \\n ").replace("\t", " ")))


AUDIO_SPEAKER = re.compile(
    r"(BloodElf|BloodMage|HeroBloodElf|SpellBreaker|DragonHawk|Kael|Sylvanas|HighElf|Sorceress|Priest|"
    r"NightElf|Archer|Huntress|Sentinel|Dryad|Druid|DemonHunter|Illidan|Furion|Malfurion|Tyrande|Maiev|Shandris|"
    r"Naisha|Warden|PriestessOfTheMoon|HeroMoonPriestess|KeeperOfTheGrove|Cenarius|DarkRanger|Banshee|"
    r"HippogryphRider|ForsakenRanger|Vashj)", re.I)


def write_audio(base, out_dir):
    """Voice files whose path names an elven speaker (enUS and unlocalized only)."""
    fl = os.path.join(base, "filelist.tsv")
    if not os.path.exists(fl):
        return
    with open(fl, encoding="utf-8") as f, open(os.path.join(out_dir, "audio.tsv"), "w", encoding="utf-8") as g:
        g.write("path\tspeaker\tsize\tlocal\n")
        next(f)
        for line in f:
            p = line.rstrip("\n").split("\t")
            path, loc = p[0], p[3]
            if loc and loc != "enUS":
                continue
            if not re.search(r"\.(flac|ogg|mp3|wav)$", path, re.I) or "/Dialogue/" not in path.replace("\\", "/") \
                    and "/Units/" not in path.replace("\\", "/"):
                continue
            m = AUDIO_SPEAKER.search(path.rsplit("/", 1)[-1]) or AUDIO_SPEAKER.search(path)
            if m:
                g.write("%s\t%s\t%s\t%s\n" % (path, m.group(1), p[4], p[5]))


if __name__ == "__main__":
    main()
