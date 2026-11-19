"""Mine warcraft.wiki.gg's Midnight-era pages for elvish words and phrases (report 10).

Midnight-era means added in patches 11.2.5 to 12.1.7, or filed under a Midnight zone, instance or storyline
category, or carrying a Midnight level ({{Level|Mn...}}). The script reads only the wiki's public API (api.php),
with a generic User-Agent, one request at a time and at least a second apart, and caches every response in CACHE,
a folder outside the repo. Standard library only, Python 3.9.

From the repo root:
  python3 research/2026-11-revival/scripts/midnight_wiki.py enumerate CACHE
  python3 research/2026-11-revival/scripts/midnight_wiki.py fetch CACHE
  python3 research/2026-11-revival/scripts/midnight_wiki.py speakers CACHE
  python3 research/2026-11-revival/scripts/midnight_wiki.py extract CACHE REPO OUT.json
  python3 research/2026-11-revival/scripts/midnight_wiki.py check CACHE REPO

enumerate  writes CACHE/titles.json: every page found, with how it was found ("added:12.0.1", "patchtpl:12.0.0",
           "tpl:Mn-section", "cat:Harandar quests", "search:insource:..."). Sources: the wiki's "Added in patch X"
           categories, pages that use a {{Patch X}} template of the range, pages that use the wiki's Midnight markers
           {{Mn-section}} and {{Mn-inline}} (the latter also through {{Expac|Midnight}}), a walk of the Midnight
           categories (four levels down), and CirrusSearch insource: queries for Midnight level templates.
fetch      writes CACHE/pages/b*.json, the raw wikitext of every title (50 titles per request), and the wiki's
           Thalassian, Darnassian and Shalassian pages to CACHE/lang/.
speakers   fetches the pages of speakers the corpus quotes but did not fetch, so their race can be read.
extract    reads the cache, the lexicon (REPO/src/thalassian/data/lexicon.json) and the scrambler word list
           (REPO/.wowf-extract/LanguageWords.csv, local and gitignored; without it the scrambler check is skipped),
           and writes OUT.json: one record per elvish-looking phrase with page, section, speaker, line and its
           classification, plus summary counts. A phrase is a run of tokens that are joined by an apostrophe
           (contractions, possessives and dropped g's excluded), or are lexicon or language-page words that are
           not English, or, in quoted speech, are not English (macOS /usr/share/dict). The output is a review list:
           which phrases are elvish, and which have an in-game gloss, is decided by reading the lines (report 10).
check      a completeness test of the enumeration: searches the whole wiki for every elvish lexicon form of four or
           more letters and the wiki's untranslated Thalassian phrases, then fetches each page outside titles.json
           that holds one of the rarer forms (60 hits or fewer) and lists those that carry a Midnight marker (a
           {{Patch}} template of the range, {{Mn-section}}, {{Mn-inline}}, {{Expac|Midnight}} or a Midnight level).
           Writes CACHE/check.json.
"""
import csv
import hashlib
import json
import os
import random
import re
import sys
import time
import urllib.parse
import urllib.request

API = "https://warcraft.wiki.gg/api.php"
UA = "thalassian-research/1.0"
GAP = 1.0
PATCHES = ["11.2.5", "11.2.7", "12.0.0", "12.0.1", "12.0.5", "12.0.7", "12.1.0", "12.1.5", "12.1.7"]
LANG_PAGES = ["Thalassian", "Darnassian", "Shalassian"]
CAT_ROOTS = [
    "Midnight", "Midnight delves", "Harandar", "Voidstorm", "Zul'Aman", "Amani Tribe quests", "Amani Tribe rewards",
    "Arator's Journey quests", "Silvermoon Court quests", "Silvermoon Court rewards", "Haranir characters", "Haranir quests",
    "Midnight Season 1", "Midnight Season 2", "Midnight Fishing", "Midnight Season 1 achievements", "Midnight Season 1 gear",
    "Midnight Season 1 items", "Midnight Season 1 quests", "Midnight Season 1 rewards", "Midnight Season 2 achievements",
    "Midnight Season 2 gear", "Midnight Season 2 items", "Midnight Season 2 quests", "Midnight bonus objectives",
    "Midnight crafted items", "Midnight crafting reagent items", "Midnight currency", "Midnight delve NPCs", "Midnight delve items",
    "Midnight delve mobs", "Midnight delve objects", "Midnight delve powers", "Midnight delve quests", "Midnight labyrinths",
    "Midnight meta quests", "Midnight profession equipment", "Midnight profession knowledge items", "Midnight quest chain templates",
    "Midnight quests", "Midnight rare elite mobs", "Midnight rare mobs", "Midnight seasons", "Midnight toys", "Midnight world drops",
    "Midnight world quests", "Midnight instances", "Midnight subzone project"]
CAT_SKIP = re.compile(r"\(Burning Crusade\)|\(kingdom\)|Ghostlands|concept art|beta testers|developer showcases|"
                      r"Zul'Aman \(instance\)|Sunwell Plateau|image requests", re.I)
# the wiki's untranslated Thalassian phrases (Thalassian page, 2026-11-18), searched by `check` with the lexicon forms
UNTRANSLATED = ["Anar'anel belore", "Andu fallah", "Anar'alash denal", "Anar'dalel", "Anu bala belore", "belore'alon",
                "Aranal, ledel", "Balamore shanal", "Belesa menoor", "Diel fin'al", "Endala finel endal", "Felomin ashal",
                "Quel'falan danas", "Selama am'oronor", "Selama amor'anore", "Sha'amoor", "Thalas'din belore",
                "Endorel aluminor", "Ishnu alah terro shar", "Ishera-do", "Bandal"]
MIDNIGHT_MARK = re.compile(r"\{\{\s*[Pp]atch[ _](?:11\.2\.[57]|12\.\d\.\d)|\{\{\s*[Mm]n-(?:section|inline)|"
                           r"\{\{\s*[Ee]xpac\|\s*Midnight|\{\{\s*[Ll]evel\s*\|\s*Mn|Mn-max")
SEARCHES = ['insource:"Mn-max"', 'insource:/\\{\\{[Ll]evel\\|Mn/', 'insource:"level = Mn"', 'insource:"Mn-"']


# ---------------------------------------------------------------- API with cache

class Wiki:
    def __init__(self, cache):
        self.dir = os.path.join(cache, "api-cache")
        os.makedirs(self.dir, exist_ok=True)
        self.last = 0.0

    def get(self, **params):
        params.setdefault("format", "json")
        params.setdefault("formatversion", "2")
        query = urllib.parse.urlencode(sorted(params.items()))
        path = os.path.join(self.dir, hashlib.sha1(query.encode()).hexdigest() + ".json")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                return json.load(fh)
        for attempt in range(4):
            wait = GAP - (time.time() - self.last)
            if wait > 0:
                time.sleep(wait)
            req = urllib.request.Request(API + "?" + query, headers={"User-Agent": UA})
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    data = json.load(r)
                self.last = time.time()
                break
            except Exception as e:  # network hiccup: back off and retry
                self.last = time.time()
                print("retry", attempt, e, file=sys.stderr)
                time.sleep(5 * (attempt + 1))
        else:
            raise RuntimeError("request failed: " + query)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh)
        return data

    def iterate(self, **params):
        cont = {}
        while True:
            d = self.get(**params, **cont)
            yield d
            if "continue" not in d:
                return
            cont = d["continue"]


# ---------------------------------------------------------------- enumerate and fetch

def enumerate_pages(cache):
    wiki = Wiki(cache)
    found = {}

    def add(title, src):
        found.setdefault(title, set()).add(src)

    for v in PATCHES:
        for d in wiki.iterate(action="query", list="categorymembers", cmtitle="Category:Added in patch " + v, cmlimit="500", cmnamespace="0"):
            for p in d["query"]["categorymembers"]:
                add(p["title"], "added:" + v)
        for d in wiki.iterate(action="query", list="embeddedin", eititle="Template:Patch " + v, eilimit="500", einamespace="0"):
            for p in d["query"]["embeddedin"]:
                add(p["title"], "patchtpl:" + v)
    for tpl in ("Mn-section", "Mn-inline"):  # the wiki's Midnight markers ({{Expac|Midnight}} uses Mn-inline)
        for d in wiki.iterate(action="query", list="embeddedin", eititle="Template:" + tpl, eilimit="500", einamespace="0"):
            for p in d["query"]["embeddedin"]:
                add(p["title"], "tpl:" + tpl)
    seen = set()

    def walk(cat, depth):
        if cat in seen or CAT_SKIP.search(cat):
            return
        seen.add(cat)
        for d in wiki.iterate(action="query", list="categorymembers", cmtitle=cat, cmlimit="500", cmnamespace="0|14"):
            for p in d["query"]["categorymembers"]:
                if p["ns"] == 14:
                    if depth < 4:
                        walk(p["title"], depth + 1)
                else:
                    add(p["title"], "cat:" + cat[len("Category:"):])
    for root in CAT_ROOTS:
        walk("Category:" + root, 0)
    for q in SEARCHES:
        for d in wiki.iterate(action="query", list="search", srsearch=q, srlimit="500", srnamespace="0", srwhat="text", srprop=""):
            for p in d["query"]["search"]:
                add(p["title"], "search:" + q)
    out = {k: sorted(v) for k, v in sorted(found.items())}
    with open(os.path.join(cache, "titles.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=0)
    with open(os.path.join(cache, "categories-walked.json"), "w", encoding="utf-8") as fh:
        json.dump(sorted(seen), fh, ensure_ascii=False, indent=0)
    print(len(out), "titles;", len(seen), "categories walked")


def fetched_titles(cache):
    have = set()
    pdir = os.path.join(cache, "pages")
    if os.path.isdir(pdir):
        for f in os.listdir(pdir):
            with open(os.path.join(pdir, f), encoding="utf-8") as fh:
                for p in json.load(fh):
                    have.add(p["title"])
                    have.update(p.get("aliases", []))
    return have


def fetch_titles(cache, titles):
    wiki = Wiki(cache)
    pdir = os.path.join(cache, "pages")
    os.makedirs(pdir, exist_ok=True)
    have = fetched_titles(cache)
    todo = [t for t in titles if t not in have]
    print(len(todo), "to fetch of", len(titles))
    for i in range(0, len(todo), 50):
        batch = todo[i:i + 50]
        d = wiki.get(action="query", prop="revisions", rvprop="content|timestamp|ids", rvslots="main",
                     titles="|".join(batch), redirects="1")
        q = d["query"]
        alias = {}
        for k in ("normalized", "redirects"):
            for r in q.get(k, []):
                alias.setdefault(r["to"], []).append(r["from"])
        for to in list(alias):  # normalized -> redirect chains
            for frm in list(alias[to]):
                alias[to].extend(alias.get(frm, []))
        recs = []
        for p in q["pages"]:
            if p.get("missing") or p.get("invalid"):
                recs.append({"title": p["title"], "missing": True, "aliases": alias.get(p["title"], [])})
            elif "revisions" in p:
                rv = p["revisions"][0]
                recs.append({"title": p["title"], "pageid": p["pageid"], "revid": rv["revid"], "timestamp": rv["timestamp"],
                             "text": rv["slots"]["main"]["content"], "aliases": alias.get(p["title"], [])})
        name = "b%05d.json" % len(os.listdir(pdir))
        with open(os.path.join(pdir, name), "w", encoding="utf-8") as fh:
            json.dump(recs, fh, ensure_ascii=False)
        if i and i % 2500 == 0:
            print(i, flush=True)


def fetch(cache):
    with open(os.path.join(cache, "titles.json"), encoding="utf-8") as fh:
        titles = sorted(json.load(fh))
    fetch_titles(cache, titles)
    ldir = os.path.join(cache, "lang")
    os.makedirs(ldir, exist_ok=True)
    wiki = Wiki(cache)
    d = wiki.get(action="query", prop="revisions", rvprop="content|ids", rvslots="main", titles="|".join(LANG_PAGES))
    for p in d["query"]["pages"]:
        with open(os.path.join(ldir, p["title"] + ".txt"), "w", encoding="utf-8") as fh:
            fh.write(p["revisions"][0]["slots"]["main"]["content"])


# ---------------------------------------------------------------- wikitext

def scan_templates(text):
    """(start, end, inner) of every {{...}}, at any depth; {{{params}}} are skipped."""
    stack, out, i, n = [], [], 0, len(text)
    while i < n - 1:
        two = text[i:i + 2]
        if two == "{{":
            if text[i:i + 3] == "{{{":
                j = text.find("}}}", i + 3)
                if j < 0:
                    break
                i = j + 3
                continue
            stack.append(i)
            i += 2
            continue
        if two == "}}" and stack:
            s = stack.pop()
            out.append((s, i + 2, text[s + 2:i]))
            i += 2
            continue
        i += 1
    return out


def split_params(inner):
    parts, dt, dl, cur, i = [], 0, 0, [], 0
    while i < len(inner):
        two = inner[i:i + 2]
        if two in ("{{", "[["):
            if two == "{{":
                dt += 1
            else:
                dl += 1
            cur.append(two)
            i += 2
            continue
        if two == "}}" and dt:
            dt -= 1
            cur.append(two)
            i += 2
            continue
        if two == "]]" and dl:
            dl -= 1
            cur.append(two)
            i += 2
            continue
        if inner[i] == "|" and not dt and not dl:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(inner[i])
        i += 1
    parts.append("".join(cur))
    return parts


def top_templates(text):
    tops, last = [], -1
    for s, e, inner in sorted(scan_templates(text)):
        if s >= last:
            ps = split_params(inner)
            tops.append((s, e, ps[0].strip(), ps[1:]))
            last = e
    return tops


LINK = re.compile(r"\[\[(?:[^\[\]|]*\|)?([^\[\]]*)\]\]")
EXT = re.compile(r"\[(?:https?:)?//[^\s\]]+\s*([^\]]*)\]")
TAG = re.compile(r"<ref[^>/]*/>|<ref[^>]*>.*?</ref>|<!--.*?-->|<br\s*/?>|</?(?:small|span|div|center|i|b|u|s|big|sup|sub|poem|"
                 r"blockquote|nowiki|onlyinclude|includeonly|noinclude)[^>]*>", re.S | re.I)
SECTION = re.compile(r"^(={2,6})\s*(.*?)\s*\1\s*$", re.M)
KV = re.compile(r"\s*([\w ]+?)\s*=(.*)$", re.S)


def plain(s):
    s = TAG.sub(" ", s)
    for _ in range(3):
        s = LINK.sub(lambda m: m.group(1), s)
    s = EXT.sub(lambda m: m.group(1), s)
    return s.replace("'''", "").replace("''", "").replace("&nbsp;", " ")


def link_targets(text):
    return [m.group(1).split("|")[0].split("#")[0].strip() for m in re.finditer(r"\[\[([^\[\]]+)\]\]", text)]


def sections(text):
    out, name, pos = [], "(lead)", 0
    for m in SECTION.finditer(text):
        out.append((name, pos, m.start()))
        name, pos = plain(m.group(2)).strip(), m.end()
    out.append((name, pos, len(text)))
    return out


def section_at(secs, pos):
    for name, s, e in secs:
        if s <= pos < e:
            return name
    return secs[-1][0]


ERA_MARK = re.compile(r"\{\{\s*([A-Za-z]+)-(?:section|inline)\b|\{\{\s*[Ee]xpac\s*\|\s*([A-Za-z: ]+?)\s*[|}]")
ERA_CODES = {"wow", "bc", "wotlk", "cata", "mop", "wod", "legion", "bfa", "sl", "df", "tww", "mn", "novel", "comic", "rpg",
             "manga", "hs", "hots", "film", "movie"}
ERA_NAMES = {"midnight": "mn", "the war within": "tww", "dragonflight": "df", "shadowlands": "sl", "battle for azeroth": "bfa",
             "legion": "legion", "warlords of draenor": "wod", "mists of pandaria": "mop", "cataclysm": "cata",
             "wrath of the lich king": "wotlk", "the burning crusade": "bc"}


def era_spans(text):
    """(start, end, era) for sections and ';' sub-headings whose opening lines carry an expansion marker such as
    {{Mn-section}}, {{Sl-section}}, {{Mn-inline}} or {{Expac|Midnight}}. Later (inner) spans win."""
    heads = [(m.start(), m.end()) for m in SECTION.finditer(text)]
    subs = [(m.start(), m.end()) for m in re.finditer(r"^;[^\n]*$", text, re.M)]
    bounds = sorted([h[0] for h in heads] + [s0 for s0, _ in subs] + [len(text)])
    spans = []
    for start in [0] + [h[0] for h in heads] + [s0 for s0, _ in subs]:
        end = min([b for b in bounds if b > start] or [len(text)])
        if start in [h[0] for h in heads]:  # a heading's span runs to the next heading, over its ';' sub-headings
            end = min([h[0] for h in heads if h[0] > start] or [len(text)])
        head = text[start:min(end, start + 400)]
        lines = []
        for i, ln in enumerate(head.split("\n")[:3]):
            if i and ln.startswith((";", "=")):
                break  # stop at the next sub-heading: its marker is its own
            lines.append(ln)
        for m in ERA_MARK.finditer("\n".join(lines)):
            era = (m.group(1) or "").lower() or ERA_NAMES.get((m.group(2) or "").strip().lower(), "")
            era = {"midnight": "mn", "shadowlands": "sl", "tbc": "bc", "vanilla": "wow"}.get(era, era)
            if era in ERA_CODES:
                spans.append((start, end, era))
                break
    return spans


def era_at(spans, pos):
    best = None
    for s0, e0, era in spans:
        if s0 <= pos < e0 and (best is None or s0 >= best[0]):
            best = (s0, era)
    return best[1] if best else ""


def tname(n):
    return n.strip().lower().replace("_", " ")


TEXT_KEYS = {"name", "title", "flavor", "flavortext", "description", "desc", "text", "tooltip", "subtitle", "caption", "note",
             "notes", "quote", "lore", "objective", "objectives", "criteria", "reward", "rewards", "tagline", "lorename", "nickname",
             "alias", "aliases", "epithet", "titles", "tag", "label", "gossip", "flavour", "use", "equip", "proc", "content", "rcov",
             "buff_desc", "set", "location", "affiliation", "subzone", "zone", "boss", "mount", "pet", "toy", "speaker", "author"}


def segments(title, text):
    """Lines of a page with their context: kind (speech:say, gossip, quote, field:..., prose), speaker, section."""
    secs = sections(text)
    segs, covered = [], []

    def kvs(ps):
        return {m.group(1).strip().lower(): m.group(2) for m in (KV.match(p) for p in ps) if m}

    def positional(ps):
        return [p for p in ps if not KV.match(p) or p.strip().startswith("[[")]

    def handle(name, ps, pos):
        n, pa = tname(name), positional(ps)
        sec = section_at(secs, pos)
        if n == "text" and len(pa) >= 2:
            speaker = plain(pa[1]).strip() if len(pa) >= 3 else ""
            line = "|".join(pa[2:]) if len(pa) >= 3 else pa[1]
            segs.append({"kind": "speech:" + tname(pa[0]), "speaker": speaker, "section": sec, "text": line, "pos": pos})
            return True
        if n in ("dialogue", "dialog"):
            speaker = plain(kvs(ps).get("title", "")).strip() or title
            body = [p for p in ps if not re.match(r"\s*title\s*=", p)]
            segs.append({"kind": "gossip", "speaker": speaker, "section": sec, "text": "|".join(body), "pos": pos})
            return True
        if n in ("quote", "q", "cquote", "blockquote", "speech", "npcquote"):
            segs.append({"kind": "quote", "speaker": plain(pa[1]).strip() if len(pa) > 1 else "", "section": sec,
                         "text": pa[0] if pa else "", "pos": pos})
            return True
        if n == "gossip":
            segs.append({"kind": "gossip-option", "speaker": "", "section": sec, "text": "|".join(pa), "pos": pos})
            return True
        return False

    for s, e, name, ps in top_templates(text):
        covered.append((s, e))
        if handle(name, ps, s):
            continue
        inner = text[s + 2:e - 2]
        for s2, e2, n2, p2 in (top_templates(inner) if "{{" in inner else []):
            handle(n2, p2, s + 2 + s2)
        n = tname(name)
        for p in ps:
            m = KV.match(p)
            if m and m.group(1).strip().lower() in TEXT_KEYS:
                segs.append({"kind": "field:%s.%s" % (n, m.group(1).strip().lower()), "speaker": "", "section": section_at(secs, s),
                             "text": m.group(2), "pos": s})
            elif not m and len(p.split()) >= 4 and "{{" not in p:
                segs.append({"kind": "tplarg:" + n, "speaker": "", "section": section_at(secs, s), "text": p, "pos": s})
    pos = 0
    for s, e in sorted(covered) + [(len(text), len(text))]:
        if s > pos:
            off = pos
            for line in text[pos:s].split("\n"):
                if line.strip() and not line.lstrip().startswith(("[[Category:", "[[File:", "[[Image:", "__")):
                    segs.append({"kind": "prose", "speaker": "", "section": section_at(secs, off), "text": line, "pos": off})
                off += len(line) + 1
        pos = max(pos, e)
    spans = era_spans(text)
    for sg in segs:
        sg["era"] = era_at(spans, sg["pos"])
    segs.sort(key=lambda d: d["pos"])
    return segs


def clean(s):
    """Plain text of a line: inline templates reduced to their text."""
    for _ in range(4):
        tops = top_templates(s)
        if not tops:
            break
        out, pos = [], 0
        for a, b, name, ps in tops:
            out.append(s[pos:a])
            pos = b
            n = tname(name)
            pa = [p for p in ps if not re.match(r"\s*[\w ]+\s*=", p)]
            if n == "text" and len(pa) >= 3:
                out.append("%s %ss: %s" % (plain(pa[1]).strip(), tname(pa[0]), "|".join(pa[2:])))
            elif n == "gossip":
                out.append(" ".join(pa))
            elif n in ("name", "race", "class", "gender", "genderchoice", "g", "player"):
                out.append("<" + ("|".join(pa) if pa else n) + ">")
            elif n.startswith(("elinks", "patch", "stub", "nav", "sectionstub", "citation", "cite", "ref", "main", "see also",
                               "icon", "questbox", "npcbox", "itembox")):
                out.append(" ")
            elif pa:
                out.append(pa[-1])
        out.append(s[pos:])
        s = "".join(out)
    return re.sub(r"\s+", " ", plain(s)).strip(" :*#;")


# ---------------------------------------------------------------- vocabularies

def norm(s):
    return s.replace("’", "'").replace("‘", "'").replace("`", "'").lower().strip()


def parts(s):
    return [p for p in re.split(r"[\s'\-,.!?]+", norm(s)) if p]


def load_english():
    words = set()
    for f in ("/usr/share/dict/words", "/usr/share/dict/web2a"):
        if os.path.exists(f):
            with open(f, encoding="utf-8", errors="ignore") as fh:
                for line in fh:
                    for t in re.split(r"[\s-]+", line.strip()):
                        if t:
                            words.add(t.lower())
    return words


def language_page_vocab(ldir):
    """Bold terms, table terms and parser words on the wiki's language pages: {term: [(page, section)]}."""
    out = {}
    for f in sorted(os.listdir(ldir)):
        page = f[:-4]
        with open(os.path.join(ldir, f), encoding="utf-8") as fh:
            text = fh.read()
        secs = sections(text)
        for m in re.finditer(r"'''(.+?)'''", text):
            term = plain(m.group(0)).strip().strip(":=—-").strip()
            if term and len(term) < 120:
                out.setdefault(norm(term).strip("!?.,"), []).append((page, section_at(secs, m.start())))
        for m in re.finditer(r"^\|\s*([^|\n]+?)\s*\|\|", text, re.M):
            term = plain(m.group(1)).strip()
            if term and len(term) < 80:
                out.setdefault(norm(term).strip("!?.,"), []).append((page, section_at(secs, m.start())))
        for name, s, e in secs:
            if "parser" in name.lower():
                for m in re.finditer(r"^\|\s*([A-Z][^|\n]*,[^|\n]*)$", text[s:e], re.M):
                    for w in m.group(1).split(","):
                        if w.strip():
                            out.setdefault(norm(w), []).append((page, name))
    return out


DIALECT = set("""dat dem dis dey de den dere dese dose wit ya mon da deir gonna wanna gotta lemme gimme kinda sorta outta hmm hmmm
nevermind anymore cutscene ain't dunno ok okay elven elvish elves dwarven draenei naaru nerubian worshipper worshippers teleport
teleports teleported teleporting runestone runestones hawkstrider hawkstriders guildmate guildmates began became flies died larger
truest fel lightforged worgen goblin goblins orcish voidwalker voidwalkers spellbreaker spellbreakers warband delve delves delver
delvers loa mana arcanist magister magisters farstrider farstriders hmph heh ha hah ahh ah ooh oh uh um er huh eh argh grr bah pah
tsk shh mmm mmmm psst oof ohh c'mon y'know y'all ya'll o'clock""".split())
CONTR_END = {"s", "t", "re", "ll", "ve", "d", "m"}
STOP = set("""a an as at be by do go he if in is it me my no of on or so to up us we all and any are but can for had has her him
his its may not now one our out she the too two was who why you also from have into just like more most much only over some such
than that them then they this were what when will with your""".split())


class Classifier:
    def __init__(self, repo, ldir):
        self.eng = load_english()
        with open(os.path.join(repo, "src/thalassian/data/lexicon.json"), encoding="utf-8") as fh:
            self.lexicon = json.load(fh)
        self.lex = {}
        for e in self.lexicon:
            self.lex.setdefault(norm(e["word"]).strip("!.?"), []).append(e)
        self.lexparts = {p for w in self.lex for p in parts(w)}
        self.wiki = language_page_vocab(ldir)
        self.wikiparts = {p for w in self.wiki for p in parts(w)}
        self.scr = {}
        path = os.path.join(repo, ".wowf-extract/LanguageWords.csv")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                for r in csv.DictReader(fh):
                    self.scr.setdefault(r["LanguageID"], set()).add(norm(r["Word"]))
        self.scr_elf = self.scr.get("10", set()) | self.scr.get("2", set()) | self.scr.get("310", set())

    def is_eng(self, w):
        w = w.lower()
        if w in self.eng:
            return True
        for suf, rep in (("ies", "y"), ("es", ""), ("s", ""), ("ed", ""), ("ed", "e"), ("ing", ""), ("ing", "e"), ("ly", ""),
                         ("er", ""), ("est", ""), ("ness", ""), ("ment", ""), ("ful", ""), ("less", ""), ("ish", ""), ("ers", ""),
                         ("ings", ""), ("iest", "y"), ("ied", "y"), ("ier", "y")):
            if w.endswith(suf) and len(w) - len(suf) + len(rep) >= 3:
                b = w[:-len(suf)] + rep
                if b in self.eng:
                    return True
                if suf in ("ed", "ing", "er", "est") and len(b) > 3 and b[-1] == b[-2] and b[:-1] in self.eng:
                    return True
        return False

    def token(self, raw):
        t = raw.replace("’", "'").strip("-")
        gdrop = t.endswith("'") and not t.startswith("'")
        t = t.strip("'")
        low = t.lower()
        ps = [p for p in re.split(r"['\-]", low) if p]
        english = low in DIALECT or (bool(ps) and ps[0] in DIALECT and len(ps) == 2 and ps[1] in CONTR_END)
        if len(ps) >= 2 and ps[-1] in CONTR_END and (self.is_eng("".join(ps[:-1])) or self.is_eng(ps[0])
                                                     or (ps[0].endswith("n") and ps[-1] == "t") or ps[-1] == "s"):
            if ps[-1] == "s" and len(ps) > 2 and re.search(r"'s$", low):  # possessive of an apostrophe name: Xal'atath's
                t = t[:-2]
                low, ps = t.lower(), ps[:-1]
            else:
                english = True
        if gdrop and (self.is_eng(low + "g") or self.is_eng(low)):
            english = True
        apost = not english and "'" in t and len(ps) >= 2
        eng = english or (not apost and all(self.is_eng(p) for p in ps))
        lex = low in self.lex or (bool(ps) and not eng and all(p in self.lexparts for p in ps))
        wiki = low in self.wiki or (bool(ps) and not eng and all(p in self.wikiparts for p in ps))
        return {"t": t, "low": low, "apost": apost, "eng": eng, "lex": lex, "wiki": wiki, "scr": low in self.scr_elf,
                "cap": t[:1].isupper()}


# ---------------------------------------------------------------- extract

TOK = re.compile(r"[A-Za-zÀ-ɏ]+(?:['’\-][A-Za-zÀ-ɏ]+)*'?")
LANGTAG = re.compile(r"\[(Thalassian|Darnassian|Shalassian|Shen'dorei|Elvish|Nazja|Zandali|Troll|Common|Orcish|Draconic|Titan|"
                     r"Kalimag|Demonic|Shath'Yar|Haranir|Rutaani)\]", re.I)
GLOSSCUE = re.compile(r"\b(means?|meaning|translat\w*|in Thalassian|Thalassian (?:for|word|phrase|term)|in Darnassian|"
                      r"Darnassian (?:for|word)|in Shalassian|our (?:old |ancient |native )?(?:tongue|language)|elven (?:word|phrase|tongue)|"
                      r"old tongue|ancient tongue|we call|called it|the word|literally|roughly)\b", re.I)
PATCHRE = re.compile(r"\{\{\s*[Pp]atch[ _](\d+\.\d+\.\d+[a-z]?)\s*\|([^{}]*)\}\}")
SPEECHY = ("speech", "gossip", "quote", "field:book.content")
SPEECHY_SECTIONS = {"description", "progress", "completion", "quotes", "dialogue", "gossip", "notes", "quest text", "text",
                    "transcript", "content", "lyrics", "inscription"}
ELF_RACE = re.compile(r"elf|elves|elven|dorei|highborne|nightborne|skyborne|san'layn|darkfallen", re.I)


def load_pages(cache):
    pages = {}
    pdir = os.path.join(cache, "pages")
    for f in sorted(os.listdir(pdir)):
        with open(os.path.join(pdir, f), encoding="utf-8") as fh:
            for p in json.load(fh):
                if not p.get("missing"):
                    pages[p["title"]] = p
    return pages


def vtuple(v):
    return tuple(int(x) for x in re.findall(r"\d+", v)[:3])


def older_page(p):
    """True when a {{Patch}} template says the page's subject was added before 11.2.5."""
    return any(vtuple(m.group(1)) < vtuple(PATCHES[0]) and re.search(r"added\s*=|note\s*=\s*Added", m.group(2), re.I)
               for m in PATCHRE.finditer(p["text"]))


def page_status(p, src):
    """added (in 11.2.5-12.1.7), midnight-cat, midnight-level, changed (only changed by a Midnight patch), or other."""
    added, changed = [], []
    for m in PATCHRE.finditer(p["text"]):
        if m.group(1) in PATCHES:
            (added if re.search(r"added\s*=|note\s*=\s*Added", m.group(2), re.I) else changed).append(m.group(1))
    added += [s[6:] for s in src if s.startswith("added:")]
    if added:
        return "added", min(added, key=lambda v: PATCHES.index(v))
    cats = [s[4:] for s in src if s.startswith("cat:")]
    if cats:
        return "midnight-cat", cats[0]
    if re.search(r"\{\{\s*[Ll]evel\s*\|\s*Mn", p["text"]) or "Mn-max" in p["text"]:
        return "midnight-level", "Mn"
    if changed:
        return "changed", min(changed, key=lambda v: PATCHES.index(v))
    return "other", ""


def npc_races(pages):
    out = {}
    for title, p in pages.items():
        for s, e, name, ps in top_templates(p["text"]):
            if tname(name) in ("npcbox", "npcbox2"):
                for x in ps:
                    m = re.match(r"\s*race\s*=(.*)$", x, re.S)
                    if m:
                        for t in [title] + p.get("aliases", []):
                            out[t] = plain(m.group(1)).strip()
                break
    return out


def speakers_of(pages):
    names = set()
    for title, p in pages.items():
        for s, e, inner in scan_templates(p["text"]):
            ps = split_params(inner)
            if tname(ps[0]) == "text" and len(ps) >= 4:
                names.add(plain(ps[2]).strip())
            elif tname(ps[0]) in ("dialogue", "dialog"):
                for x in ps[1:]:
                    m = re.match(r"\s*title\s*=(.*)$", x, re.S)
                    if m:
                        names.add(plain(m.group(1)).strip())
    return {n for n in names if n and len(n) < 80 and not re.search(r"[<>{}\[\]|#]", n)}


def extract(cache, repo, out_path):
    with open(os.path.join(cache, "titles.json"), encoding="utf-8") as fh:
        enum = json.load(fh)
    pages = load_pages(cache)
    clf = Classifier(repo, os.path.join(cache, "lang"))
    races = npc_races(pages)
    name_words = set()
    for title, p in pages.items():
        for t in [title] + link_targets(p["text"]):
            name_words.update(norm(m.group(0)) for m in TOK.finditer(t))
    recs, seen = [], set()
    status_count = {}
    mn_pages, mn_segments = set(), 0
    for title in sorted(pages):
        p = pages[title]
        src = enum.get(title, [])
        for a in p.get("aliases", []):
            src = src + enum.get(a, [])
        st = page_status(p, src)
        status_count[st[0]] = status_count.get(st[0], 0) + 1
        older = older_page(p)
        for sg in segments(title, p["text"]):
            line = clean(sg["text"])
            if len(line) < 2:
                continue
            mline = sg["era"] == "mn" or (not sg["era"] and (st[0] == "added" or
                                                              (st[0] in ("midnight-cat", "midnight-level") and not older)))
            if mline:
                mn_pages.add(title)
                mn_segments += 1
            speechy = sg["kind"].startswith(SPEECHY) or sg["section"].lower() in SPEECHY_SECTIONS
            toks = []
            for m in TOK.finditer(line):
                ti = clf.token(m.group(0))
                ti["name"] = ti["cap"] and ti["low"] in name_words
                if ti["apost"] or ((ti["lex"] or ti["wiki"] or ti["scr"]) and not ti["eng"]):
                    ti["tier"] = 1
                elif speechy and not ti["eng"] and len(ti["low"]) >= 3:
                    ti["tier"] = 2 if not ti["cap"] else (3 if not ti["name"] else 0)
                else:
                    ti["tier"] = 0
                toks.append((m.start(), m.end(), ti))
            # an English-looking word that is also an elvish word ("bala", "dash", "na") joins a neighbouring run;
            # a common English word ("no", "do") joins only between two elvish words
            for _ in range(2):
                for i, (a, b, ti) in enumerate(toks):
                    low = ti["low"]
                    if ti["tier"] or not (low in clf.lex or low in clf.wiki or ti["scr"] or
                                          (len(low) >= 4 and (low in clf.lexparts or low in clf.wikiparts))):
                        continue
                    near = []
                    for j in (i - 1, i + 1):
                        if 0 <= j < len(toks) and toks[j][2]["tier"] == 1 and not toks[j][2].get("joined"):
                            gap = line[min(b, toks[j][1]):max(a, toks[j][0])]
                            if re.fullmatch(r"[\s,\-\u2014\u2026]*", gap):
                                near.append(j)
                    if len(near) == 2 or (near and low not in STOP):
                        ti["tier"] = 1
                        ti["joined"] = True
            cand = [x for x in toks if x[2]["tier"]]
            tag = LANGTAG.findall(line)
            if not cand and not tag:
                continue
            runs, cur = [], []
            for a, b, ti in cand:
                if cur and re.fullmatch(r"[\s,\-—…]*", line[cur[-1][1]:a]):
                    cur.append((a, b, ti))
                else:
                    if cur:
                        runs.append(cur)
                    cur = [(a, b, ti)]
            if cur:
                runs.append(cur)
            if not runs and tag:
                runs = [[]]
            cue = GLOSSCUE.search(line)
            spk = sg["speaker"]
            for run in runs:
                phrase = line[run[0][0]:run[-1][1]] if run else ""
                key = (title, norm(phrase), line)
                if key in seen:
                    continue
                seen.add(key)
                rt = [ti for _, _, ti in run]
                low = norm(phrase)
                lowparts = parts(phrase)
                recs.append({
                    "page": title, "url": "https://warcraft.wiki.gg/wiki/" + urllib.parse.quote(title.replace(" ", "_"), safe="'(),:"),
                    "status": st[0], "patch": st[1], "section": sg["section"], "era_marker": sg["era"],
                    "midnight_line": mline,
                    "kind": sg["kind"], "speaker": spk,
                    "speaker_race": races.get(spk, ""), "phrase": phrase, "line": line[:600],
                    "tier": min((t["tier"] for t in rt), default=0), "max_tier": max((t["tier"] for t in rt), default=0),
                    "all_names": bool(rt) and all(t["name"] or (t["cap"] and t["apost"] and t["low"] in name_words) for t in rt),
                    "in_lexicon": low in clf.lex, "parts_in_lexicon": bool(lowparts) and all(x in clf.lexparts for x in lowparts),
                    "on_wiki_language_pages": low in clf.wiki, "parts_on_wiki": bool(lowparts) and all(x in clf.wikiparts for x in lowparts),
                    "all_scrambler": bool(rt) and all(t["low"] in clf.scr_elf or all(x in clf.scr_elf for x in parts(t["low"])) for t in rt),
                    "tag": tag, "gloss_cue": cue.group(0) if cue else ""})
    summary = {"pages_fetched": len(pages), "titles_enumerated": len(enum), "page_status": status_count,
               "pages_with_midnight_text": len(mn_pages), "midnight_segments": mn_segments, "records": len(recs),
               "midnight_records": sum(1 for r in recs if r["midnight_line"]), "scrambler_words_loaded": len(clf.scr_elf)}
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump({"summary": summary, "records": recs}, fh, ensure_ascii=False, indent=0)
    print(json.dumps(summary, indent=1))


def check(cache, repo):
    """Search the whole wiki for elvish forms; list pages outside titles.json that carry a Midnight marker."""
    wiki = Wiki(cache)
    with open(os.path.join(cache, "titles.json"), encoding="utf-8") as fh:
        titles = set(json.load(fh))
    with open(os.path.join(repo, "src", "thalassian", "data", "lexicon.json"), encoding="utf-8") as fh:
        lexicon = json.load(fh)
    forms = set(UNTRANSLATED)
    for e in lexicon:
        if e.get("canon_basis") in ("attested", "segment", "inferred", "epithet", "unverified") and \
                e.get("source") in ("thalassian", "darnassian", "shalassian", "skyborne", "unattributed"):
            w = e["word"].strip("!?.")
            if len(w) >= 4:
                forms.add(w)
    hits = {}
    for f in sorted(forms):
        hits[f] = [p["title"] for d in wiki.iterate(action="query", list="search", srsearch='"%s"' % f, srlimit="500",
                                                     srnamespace="0", srprop="") for p in d["query"]["search"]]
    rare = [f for f, v in hits.items() if len(v) <= 60]
    outside = sorted({t for f in rare for t in hits[f] if t not in titles})
    marked = {}
    for i in range(0, len(outside), 50):
        d = wiki.get(action="query", prop="revisions", rvprop="content", rvslots="main", titles="|".join(outside[i:i + 50]))
        for p in d["query"]["pages"]:
            if "revisions" in p and MIDNIGHT_MARK.search(p["revisions"][0]["slots"]["main"]["content"]):
                marked[p["title"]] = sorted(f for f in rare if p["title"] in hits[f])
    result = {"forms": len(forms), "page_hits": sum(len(v) for v in hits.values()),
              "pages_outside_set_any_form": len({t for v in hits.values() for t in v if t not in titles}),
              "rare_forms": len(rare), "outside_pages_checked": len(outside), "outside_with_midnight_marker": marked,
              "hits": hits}
    with open(os.path.join(cache, "check.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=0)
    print(json.dumps({k: v for k, v in result.items() if k != "hits"}, ensure_ascii=False, indent=1))


def main(argv):
    if len(argv) < 3 or argv[1] not in ("enumerate", "fetch", "speakers", "extract", "check") or \
            (argv[1] == "extract" and len(argv) < 5) or (argv[1] == "check" and len(argv) < 4):
        print(__doc__)
        return 2
    cache = argv[2]
    os.makedirs(cache, exist_ok=True)
    if argv[1] == "enumerate":
        enumerate_pages(cache)
    elif argv[1] == "fetch":
        fetch(cache)
    elif argv[1] == "speakers":
        pages = load_pages(cache)
        names = sorted(speakers_of(pages) - fetched_titles(cache))
        print(len(names), "speaker pages to fetch")
        fetch_titles(cache, names)
    elif argv[1] == "check":
        check(cache, argv[3])
    else:
        extract(cache, argv[3], argv[4])
    return 0


if __name__ == "__main__":
    random.seed(0)
    sys.exit(main(sys.argv))
