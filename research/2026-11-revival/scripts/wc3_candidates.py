#!/usr/bin/env python3
"""Build 9-candidates.json (report 9, Warcraft III) from the local Warcraft III extract.

The classification is by hand and lives in this file: which lines are elvish, which wiki spelling
each one matches, and which class it is in (a: in the lexicon, b: on the wiki only, c: new to both).
The script looks up each line's exact text, file, line number and sound file in the gitignored
.wc3-extract/ folder (written by tools/wc3/extract_text.py) and the lexicon's current values for
the fixes, then writes the candidates file. With a second argument it also writes report 9's
findings table. From the repo root:

  python3 -I research/2026-11-revival/scripts/wc3_candidates.py . [table.md]

Standard library only, Python 3.9 compatible.
"""
import glob
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tools", "wc3"))
import mine  # noqa: E402  (tools/wc3/mine.py: the same subtitle and string-table parsers the miner uses)

REPO = sys.argv[1] if len(sys.argv) > 1 else "."
OUT_MD = sys.argv[2] if len(sys.argv) > 2 else None
X = os.path.join(REPO, ".wc3-extract")
BUILD = "Warcraft III 3.0.1.24371"
EN = "War3.w3mod:_Locales/enUS.w3mod:"
NE_Q = "https://warcraft.wiki.gg/wiki/Quotes_of_Warcraft_III/Night_Elf_Sentinels#"
HU_Q = "https://warcraft.wiki.gg/wiki/Quotes_of_Warcraft_III/Human_Alliance#"
NEUTRAL_Q = "https://warcraft.wiki.gg/wiki/Quotes_of_Warcraft_III/Neutral#"
HEROES_Q = "https://warcraft.wiki.gg/wiki/Quotes_of_Warcraft_III/Neutral_Heroes#"
DARN_U = "https://warcraft.wiki.gg/wiki/Darnassian#Untranslated_phrases"
DARN_P = "https://warcraft.wiki.gg/wiki/Darnassian#Darnassian_primer_(official_translations)"
THAL_U = "https://warcraft.wiki.gg/wiki/Thalassian#Untranslated_words_or_phrases"
NAZJA = "https://warcraft.wiki.gg/wiki/Nazja#Phrases"
BASE = "Warcraft III 3.0 file mining (tools/wc3/extract_text.py, tools/wc3/mine.py)"
METHOD = BASE + "; line matched to the wiki's quote list by unit and sound file"
METHOD_TEXT = BASE + "; matched to the wiki by text and speaker"


def fdf_lines():
    out = {}
    for f in sorted(glob.glob(os.path.join(X, "casc/War3.w3mod/_Locales/enUS.w3mod/Strings/Dialogue*Base.fdf"))):
        for i, key, text in mine.parse_fdf(mine.read_text(f)):
            out[key] = (os.path.basename(f), i, text)
    return out


def slk_sounds():
    out = {}
    for f in sorted(glob.glob(os.path.join(X, "casc/War3.w3mod/UI/SoundInfo/Dialogue*Base.slk"))):
        cur = {}
        for line in open(f, encoding="utf-8", errors="replace"):
            if not line.startswith("C;"):
                continue
            x = val = None
            for p in line.rstrip("\n").split(";")[1:]:
                if p.startswith("Y"):
                    if cur.get(3) and cur.get(2):
                        out.setdefault(cur[3], []).append(cur[2])
                    cur = {}
                elif p.startswith("X"):
                    x = int(p[1:])
                elif p.startswith("K"):
                    val = p[1:].strip('"')
            if x is not None:
                cur[x] = val
        if cur.get(3) and cur.get(2):
            out.setdefault(cur[3], []).append(cur[2])
    return out


REFORGED = os.path.join(X, "maps/War3.w3mod/Campaign/Reforged")


def map_strings(mp, locale=None):
    """{string id: text} of a Reforged campaign map's string table, enUS or one locale."""
    path = os.path.join(REFORGED, mp + ".w3x", ("_Locales/%s.w3mod/" % locale if locale else "") + "war3map.wts")
    return {sid: text.strip() for sid, _c, text in mine.parse_wts(mine.read_text(path))}


def wav_stems(text):
    """Voice file names (lowercase, no folder or extension) in a wiki quote or a sound table path."""
    return set(m.lower() for m in re.findall(r"([A-Za-z0-9]+)\.(?:wav|flac|ogg|mp3)\b", text))


FDF = fdf_lines()
SND = slk_sounds()
LEX = {e["word"]: e for e in json.load(open(os.path.join(REPO, "src/thalassian/data/lexicon.json")))}


def unit_ev(key, quote=None):
    f, ln, text = FDF[key]
    snd = sorted(set(SND.get(key, [])))
    where = "%s, %sStrings/%s line %d (%s%s)" % (BUILD, EN, f, ln, key,
                                                 ", sound " + " / ".join(snd) if snd else "")
    return {"quote": quote or text, "where": where}, text, "%s:%d" % (f, ln)


def map_ev(mp, sid, quote, locale=None, speaker=None, sound=None):
    path = "War3.w3mod:Campaign/Reforged/%s.w3x" % mp
    text = map_strings(mp, locale).get(sid, "")
    if quote.rstrip(".…").split("…")[0].strip() not in text:
        raise SystemExit("quote not found in %s STRING %d (%s): %r" % (mp, sid, locale or "enUS", quote))
    bits = [x for x in (speaker and "speaker " + speaker, sound and "sound " + sound) if x]
    where = "%s, %s, %swar3map.wts STRING %d%s" % (BUILD, path, (locale + " ") if locale else "", sid,
                                                    " (" + "; ".join(bits) + ")" if bits else "")
    return {"quote": quote, "where": where}


def item_ev(item_id, quote):
    f = os.path.join(X, "casc/War3.w3mod/_Locales/enUS.w3mod/Units/ItemStrings.txt")
    lines = open(f, encoding="utf-8", errors="replace").read().split("\n")
    start = lines.index("[%s]" % item_id)
    for i in range(start, start + 8):
        if lines[i].startswith("Description=") and quote.rstrip(".…") in lines[i]:
            return {"quote": quote, "where": "%s, %sUnits/ItemStrings.txt line %d (item [%s])" % (
                BUILD, EN, i + 1, item_id)}
    raise SystemExit("item quote not found: %s" % item_id)


cands = []
rows = []  # markdown rows: (class, blizzard, speaker, where, wiki, meaning)

# ---------------------------------------------------------------- (b) with a meaning: two adds
# Every Reforged campaign string with Shan'do, its speaker, and its zhTW, zhCN, koKR and ruRU renderings.
SHAN = []
for d in sorted(glob.glob(os.path.join(REFORGED, "*", "*.w3x"))):
    mp = os.path.relpath(d, REFORGED)[:-4]
    en = map_strings(mp)
    ids = [sid for sid, t in sorted(en.items()) if re.search(r"shan['’]do", t, re.I)]
    if not ids:
        continue
    conv_path = os.path.join(d, "conversation.json")
    conv = mine.parse_conversation(conv_path) if os.path.exists(conv_path) else {}
    loc = {l: map_strings(mp, l) for l in ("zhTW", "zhCN", "koKR", "ruRU")}
    for sid in ids:
        nid = conv.get(sid, (None,))[0]
        SHAN.append({"map": mp, "sid": sid, "speaker": en.get(nid, "") if isinstance(nid, int) else "",
                     "zhTW": "尊師" in loc["zhTW"].get(sid, ""), "zhCN": "大导师" in loc["zhCN"].get(sid, ""),
                     "koKR": "샨도" in loc["koKR"].get(sid, ""),
                     "ruRU": bool(re.search(r"шан['’]до", loc["ruRU"].get(sid, ""), re.I))})
N_SHAN = len(SHAN)
if not all(r["zhTW"] and r["zhCN"] for r in SHAN):
    raise SystemExit("a Shan'do string without 尊師 (zhTW) or 大导师 (zhCN)")
N_CLASSIC = sum(1 for f in glob.glob(os.path.join(X, "maps/War3.w3mod/Campaign/Classic/*/*.w3[mx]/war3map.wts"))
                for _i, _c, t in mine.parse_wts(mine.read_text(f)) if re.search(r"shan['’]do", t, re.I))
SHAN_SPEAKERS = Counter(r["speaker"] or "no speaker" for r in SHAN)
SHAN_WHO = ", ".join("%s (%d)" % kv for kv in sorted(SHAN_SPEAKERS.items(),
                                                     key=lambda kv: (-kv[1], kv[0] == "no speaker", kv[0])))
shan_ev = [
    {"quote": "Shan'do = Honored Teacher. (A title and term of respect.)", "where": DARN_P},
    map_ev("ROC/NightElf03", 186, "Shan'do Stormrage will be defenseless!", speaker="Dryad",
           sound="N03Dryad15"),
    map_ev("ROC/NightElf03", 186, "這樣怒風尊師會毫無防備！", "zhTW"),
    map_ev("ROC/NightElf03", 186, "怒风大导师岌岌可危！", "zhCN"),
]
cands.append({
    "action": "add", "word": "shan'do",
    "translation": {"en": "honored teacher (a title)", "uk": "шановний учитель (звертання)"},
    "pos": "noun", "canon": True, "root": "shan + do",
    "notes": ("Malfurion's title in Warcraft III (Shan'do Stormrage), in %d Reforged campaign strings (%d in "
              "the classic maps), said by %s. zhTW renders it 尊師 'honored teacher' and zhCN 大导师 'grand "
              "teacher' in all %d; koKR transliterates it in %d and ruRU in %d. The lexicon had only its "
              "parts, shan 'honored' and do 'teacher'." % (
                  N_SHAN, N_CLASSIC, SHAN_WHO, N_SHAN, sum(r["koKR"] for r in SHAN),
                  sum(r["ruRU"] for r in SHAN))),
    "source": "darnassian", "canon_basis": "attested", "evidence": shan_ev, "method": METHOD_TEXT +
    "; zhTW and zhCN map string tables", "confidence": "high",
    "reason": ("Blizzard glosses it twice, independently: the Warcraft Encyclopedia and APG (via the wiki "
               "primer) and the Warcraft III zhTW localization (尊師, every time)."),
})
rows.append(("b", "Shan'do", SHAN_WHO,
             "Reforged/ROC/NightElf03.w3x STRING 186, and %d more strings" % (N_SHAN - 1), "Shan'do",
             "**honored teacher**: wiki primer, and zhTW 尊師 in all %d strings (attested, confirmed)" % N_SHAN))

thero_ev = [
    {"quote": "Thero'shan = Honored student. (A title and term of respect.)", "where": DARN_P},
    map_ev("ROC/NightElf05", 139, "All is well, thero-shan.", speaker="Malfurion Stormrage",
           sound="N05Furion68"),
    map_ev("ROC/NightElf05", 139, "愛徒，別在意。", "zhTW"),
]
cands.append({
    "action": "add", "word": "thero'shan",
    "translation": {"en": "honored student (a title)", "uk": "шановний учень (звертання)"},
    "pos": "noun", "canon": True, "root": "thero + shan",
    "notes": ("Warcraft III spells it thero-shan: Malfurion to the druids of the claw (NightElf05). zhTW "
              "renders it 愛徒 'beloved disciple'; zhCN keeps the Latin text, koKR and ruRU transliterate. "
              "Head first (thero 'student' + shan 'honored'), the reverse of shan'do. Thero'shan is also "
              "in WoW's Darnassian, Thalassian and Shen'dorei scrambler lists (LanguageWords), so WoW "
              "occurrences of it may be garble."),
    "source": "darnassian", "canon_basis": "attested", "evidence": thero_ev, "method": METHOD_TEXT +
    "; zhTW map string table", "confidence": "high",
    "reason": ("The wiki primer (Warcraft Encyclopedia, APG) glosses it; Blizzard's zhTW localization "
               "independently agrees on 'student/disciple' (愛徒). 'Honored' rests on the primer alone."),
})
rows.append(("b", "thero-shan", "Malfurion (NightElf05)", "Reforged/ROC/NightElf05.w3x STRING 139",
             "Thero'shan", "**honored student**: wiki primer, and zhTW 愛徒 'beloved disciple' (attested; "
             "'student' confirmed)"))

# ---------------------------------------------------------------- (a) fixes
old = LEX["anu'dorini talah"]
ev_ana, _, loc_ana = unit_ev("NIGHTELF_UNIT_HERO_MALFURION_STORMRAGE_WARCRY1")
cands.append({
    "action": "fix", "word": "anu'dorini talah", "field": "evidence", "old": old["evidence"],
    "new": old["evidence"] + [ev_ana, {"quote": "Anu'dorini Talah! (MalfurionWarcry1.wav)",
                                      "where": NE_Q + "Malfurion_Stormrage"}],
    "confidence": "high", "method": METHOD,
    "reason": ("Malfurion's Warcraft III war cry is this phrase; the game's own subtitle spells it "
               "Ana'doreini talah. Same line by unit and sound file. Adds the game text, not a new gloss."),
})
cands.append({
    "action": "fix", "word": "anu'dorini talah", "field": "notes", "old": old.get("notes"),
    "new": (old.get("notes") or "") + " Warcraft III's own subtitle spells it Ana'doreini talah "
    "(Malfurion's ready and war-cry lines).",
    "confidence": "high", "method": METHOD, "evidence": [ev_ana],
    "reason": "Records Blizzard's spelling next to the wiki's.",
})
rows.append(("a", "Ana'doreini talah!", "Malfurion (unit war cry)", loc_ana, "Anu'dorini Talah",
             "let my will be known (lexicon, attested); Blizzard's spelling differs"))

old = LEX["sin'dorei"]
ev_band = item_ev("ebsd", "The sin'dorei, or children of the blood, renamed themselves in honor of "
                          "those whom Arthas slaughtered…")
cands.append({
    "action": "fix", "word": "sin'dorei", "field": "evidence", "old": old["evidence"],
    "new": old["evidence"] + [ev_band], "confidence": "high", "method": BASE,
    "reason": ("Second, independent Blizzard gloss: the 3.0 gear item Band of the Sin'dorei pairs "
               "sin'dorei with 'children of the blood'. The only source so far was the Warcraft "
               "Encyclopedia."),
})
rows.append(("a", "sin'dorei", "item Band of the Sin'dorei (3.0 gear)", "Units/ItemStrings.txt:3289",
             "Sin'dorei", "**children of the blood**: the item says so; second Blizzard source (attested, "
             "confirmed)"))

old = LEX["shindu sin'dorei"]
ev_echo = item_ev("eref", "By the light of the sun, our enemies are breaking through. Failing children "
                          "of the blood…")
cands.append({
    "action": "fix", "word": "shindu sin'dorei", "field": "evidence", "old": old["evidence"],
    "new": old["evidence"] + [ev_echo], "confidence": "low", "method": BASE,
    "reason": ("The 3.0 gear item Echoes of the Fallen repeats, clause for clause, the English the primer "
               "gives for anar'alah belore, shindu fallah na and shindu sin'dorei. The item has no "
               "Thalassian, so it confirms only the English wording, not the pairing; low for that reason."),
})
rows.append(("a", "(English only)", "item Echoes of the Fallen (3.0 gear)", "Units/ItemStrings.txt:2784",
             "Anar'alah belore / Shindu fallah na / Shindu sin'dorei",
             "the primer's English for these three, word for word; no elvish in the item"))

# ---------------------------------------------------------------- (a) campaign lines already in the lexicon
for word, mp, sid, quote, spk in [
        ("ishnu-alah", "ROC/NightElf02", 219, "Ishnu-alah, sisters!", "Tyrande"),
        ("ishnu-dal-dieb", "ROC/NightElf02", 76, "Ishnu-dal-dieb, Shandris.", "Tyrande"),
        ("elune-adore", "ROC/NightElf02", 200, "Elune-adore, Priestess.", "Archer"),
        ("fandu-dath-belore", "ROC/NightElf02", 217, "Fandu-dath-belore?", "Archer"),
        ("andu-falah-dor", "ROC/NightElf04", 288, "Then I will put an end to their curse! Andu-falah-dor!",
         "Tyrande"),
        ("bandu thoribas", "ROC/NightElf01", 55, "Bandu thoribas, mortals!", "Tyrande"),
        ("anar'alah belore", "ROC/Undead05", 63, "Then I'll make my stand here, butcher. Anar'alah belore.",
         "Sylvanas"),
        ("bash'a no falor talah", "ROC/Undead05", 115, "Bash'a no falor talah!", "Sylvanas"),
        ("shindu fallah na", "ROC/Undead03", 51, "Shindu fallah Na! Fall back to the second gate!",
         "Sylvanas"),
        ("ash karath", "TFT/NightElfX05", 120, "Ash Karath!", "Illidan"),
        ("ande'thoras-ethil", "TFT/NightElfX08", 219, "Ande'thoras-ethil, brother.", "Malfurion")]:
    map_ev(mp, sid, quote)  # asserts the quote is there
    tr = LEX[word]["translation"]["en"]
    rows.append(("a", quote, spk, "Reforged/%s.w3x STRING %d" % (mp, sid), "same", tr + " (lexicon)"))
ev, _, loc = unit_ev("NIGHTELF_UNIT_HERO_MAIEV_WARCRY1")
rows.append(("a", "Tor ilisar'thera'nal!", "Maiev (unit war cry)", loc, "same",
             LEX["tor ilisar'thera'nal"]["translation"]["en"] + " (lexicon)"))

# ---------------------------------------------------------------- (b)/(c) unglossed unit lines
UNIT = [
    # key, source, speaker, wiki spelling, wiki where, class, extra note
    ("HUMAN_UNIT_HERO_BLOODELF_MAGE_YES1", "thalassian", "Blood Mage", "Andu fallah. (BloodElfMageYes1.wav)", HU_Q + "Blood_Mage", "b", ""),
    ("HUMAN_UNIT_HERO_BLOODELF_MAGE_YES3", "thalassian", "Blood Mage", "Aseph-ah-balla nah. (BloodElfMageYes3.wav)", HU_Q + "Blood_Mage", "b", ""),
    ("HUMAN_UNIT_HERO_BLOODELF_MAGE_WHAT2", "thalassian", "Blood Mage", "Ishera-do. (BloodElfMageWhat5.wav)",
     HU_Q + "Blood_Mage", "b", "The game files it as What2 and the wiki as What5: the Blood Mage's five What lines are the same set, numbered in a different order."),
    ("HUMAN_UNIT_HERO_KAEL_WARCRY1", "thalassian", "Kael'thas", "Endo-enah Quel'Thalas! (KaelWarcry1.wav)",
     HU_Q + "Prince_Kael'thas", "b", "Quel'Thalas is known; endo-enah is not."),
    ("HUMAN_UNIT_SPELLBREAKER_WARCRY1", "thalassian", "Spell Breaker", "Endirina-dor Highborne! (SpellbreakerWarcry1.wav)",
     HU_Q + "Spell_Breaker", "b", "Blizzard spells it Inde'rinah-dor; the wiki hears Endirina-dor."),
    ("NIGHTELF_UNIT_HERO_TYRANDE_YESATTACK1", "darnassian", "Tyrande; also Malfurion and the Druid of the Claw",
     "Anu'dora! (TyrandeYesAttack1.wav)", NE_Q + "Tyrande_Whisperwind", "b",
     "Same text for Malfurion (YES4) and the Druid of the Claw (YES4). Shares anu'dor- with anu'dorini talah."),
    ("NIGHTELF_UNIT_HERO_TYRANDE_YESATTACK2", "darnassian", "Tyrande", "Hinduli rathal! (TyrandeYesAttack2.wav)",
     NE_Q + "Tyrande_Whisperwind", "b", "The Darnassian page spells it Hinduli rethal. Blizzard: Enu ri'fah."),
    ("NIGHTELF_UNIT_HERO_TYRANDE_WHAT3", "darnassian", "Tyrande", "Ashre thoraman. (TyrandeWhat3.wav)",
     NE_Q + "Tyrande_Whisperwind", "b", ""),
    ("NIGHTELF_UNIT_HERO_TYRANDE_PISSED4", "darnassian", "Tyrande", "Anu therador mali. (TyrandePissed4.wav)",
     NE_Q + "Tyrande_Whisperwind", "b", ""),
    ("NIGHTELF_UNIT_HERO_MALFURION_STORMRAGE_ATTACK1", "darnassian", "Malfurion",
     "Tor falah-no dorah! (MalfurionYesAttack1.wav)", NE_Q + "Malfurion_Stormrage", "b",
     "The Darnassian page lists it too, as Tor falah-no dorah."),
    ("NIGHTELF_UNIT_HERO_MALFURION_STORMRAGE_YES2", "darnassian", "Malfurion",
     "Ash'thero danador. (MalfurionYes2.wav)", NE_Q + "Malfurion_Stormrage", "b", ""),
    ("NIGHTELF_UNIT_HERO_MAIEV_ATTACK3", "darnassian", "Maiev", "Ashal thera'das! (MaievYesAttack3.wav)",
     NE_Q + "Maiev_Shadowsong", "b",
     "The Darnassian page spells it Ash'al theradas. Blizzard's al'shar is in WoW's Darnassian, Thalassian and "
     "Shen'dorei scrambler lists, so WoW's garble words drew on Warcraft III."),
    ("NIGHTELF_UNIT_HERO_WARDEN_WHAT4", "darnassian", "Warden", "Ashbalanol. (HeroWardenWhat4.wav)",
     NE_Q + "Warden", "b", ""),
    ("NIGHTELF_UNIT_HERO_WARDEN_WHAT3", "darnassian", "Warden", "Bathel'daelune. (HeroWardenWhat3.wav)",
     NE_Q + "Warden", "b", "Blizzard's spelling holds the goddess's name: Benthai del Elune."),
    ("NIGHTELF_UNIT_HERO_DEMON_HUNTER_YES3", "darnassian", "Demon Hunter (also the female demon hunter)",
     "Deronica. (HeroDemonHunterYes3.wav)", NE_Q + "Demon_Hunter", "b", ""),
    ("NIGHTELF_UNIT_HERO_DEMON_HUNTER_YES1", "darnassian", "Demon Hunter (also the female demon hunter)",
     "Anato retetour! (HeroDemonHunterYes1.wav)", NE_Q + "Demon_Hunter", "b",
     "Blizzard: Anu'dor anu'dor, again the anu'dor- of anu'dora and anu'dorini talah."),
    ("NIGHTELF_UNIT_NAISHA_WARCRY1", "darnassian", "Naisha", "Ara'denu thelore! (NaishaWarcry1.wav)",
     NE_Q + "Naisha", "b", ""),
    ("NAGA_UNIT_SIREN_YES3", "nazja", "Naga Siren", "Ash'valana thure. (NagaSirenYes3.wav)",
     NEUTRAL_Q + "Naga_Siren", "b",
     "The Nazja page has no such line; it lists Osh'bala-tharei, by ear, for the Naga Siren in Warcraft III, "
     "probably the same line, since it is the Siren's only non-English one (inferred)."),
    ("NAGA_UNIT_LADYVASHJ_YESATTACK3", "nazja", "Lady Vashj", "Era'sazjar! (LadyVashjYesAttack3.wav)",
     HEROES_Q + "Naga_Sea_Witch", "b", "Not on the Nazja page."),
    ("NAGA_UNIT_LADYVASHJ_WARCRY1", "nazja", "Lady Vashj", "Athero bath'rilas! (LadyVashjWarcry1.wav)",
     HEROES_Q + "Naga_Sea_Witch", "b", "The Nazja page lists it too, as a phonetic spelling."),
    ("NIGHTELF_UNIT_HERO_WARDEN_YES3", "darnassian", "Warden", None, NE_Q + "Warden", "c",
     "The wiki's Warden list skips HeroWardenYes3, and no wiki page has the phrase."),
]
for key, src, spk, wiki, wiki_where, cls, extra in UNIT:
    ev, text, loc = unit_ev(key)
    word = text.rstrip(".!").lower()
    evidence = [ev]
    if wiki:
        evidence.append({"quote": wiki, "where": wiki_where})
    # same voice file in the game's sound table and on the wiki: the same line; otherwise text and speaker
    same_file = bool(wiki) and bool(wav_stems(wiki) & wav_stems(" ".join(SND.get(key, []))))
    method = METHOD if same_file else METHOD_TEXT if wiki else BASE
    note = ("Unglossed. Blizzard's subtitle spelling for a %s line%s." % (spk, (
        "; the wiki spells it " + wiki.split(" (")[0].rstrip(".!")) if wiki else ", on no wiki page"))
    if extra:
        note += " " + extra
    cands.append({
        "action": "note", "word": word, "translation": None, "source": src, "canon_basis": None,
        "notes": note, "evidence": evidence, "method": method,
        "confidence": "low",
        "reason": ("New to both the lexicon and the wiki." if cls == "c" else
                   "On the wiki, not in the lexicon.") + " No source pairs it with English.",
    })
    rows.append((cls, text, spk, loc, wiki.split(" (")[0] if wiki else "none", "unglossed"))

# ---------------------------------------------------------------- (b) unglossed campaign lines
CAMP = [
    ("anadunathara", "darnassian", "ROC/Prologue01", 557,
     "You outlanders will answer for Cenarius's death. Anadunathara!", "Tyrande", "N01Tyrande13",
     "Ana duna thera", DARN_U, "Reforged text only: the classic maps have no such string."),
    ("en'shu falah-nah", "darnassian", "TFT/NightElfX08Finale", 267,
     "Farewell, brother--Tyrande. I doubt our paths will cross again. En'shu falah-nah.", "Illidan",
     "S08Illidan51", "En'shu falah-nah", DARN_U,
     "Context only: a farewell (inferred, not a gloss). falah also ends andu-falah-dor, which report 4 found "
     "said at a parting."),
    ("ash-thero-sauguine", "nazja", "TFT/NightElfX02", 122, "Ash-thero-sauguine! Ba'anthalso-dorei!",
     "Naga (myrmidon)", "S02Naga17", "Ash-thero-sauguine! / Ash'thero sanguine!", NAZJA,
     "Also in NightElfX04. Spelled sauguine in both the classic and Reforged maps."),
    ("ba'anthalso-dorei", "nazja", "TFT/NightElfX02", 122, "Ash-thero-sauguine! Ba'anthalso-dorei!",
     "Naga (myrmidon)", "S02Naga17", "Ba'anthalso-dorei!", NAZJA, "Ends in -dorei, as the elven 'people' "
     "names do (inferred)."),
]
for word, src, mp, sid, quote, spk, snd, wiki, wiki_where, extra in CAMP:
    ev = map_ev(mp, sid, quote, speaker=spk, sound=snd)
    cands.append({
        "action": "note", "word": word, "translation": None, "source": src, "canon_basis": None,
        "notes": "Unglossed. " + extra, "evidence": [ev, {"quote": wiki, "where": wiki_where}],
        "method": METHOD_TEXT, "confidence": "low",
        "reason": "On the wiki, not in the lexicon. No source pairs it with English.",
    })
    rows.append(("b", quote if len(quote) < 50 else "… " + quote.split(". ")[-1], spk,
                 "Reforged/%s.w3x STRING %d" % (mp, sid), wiki,
                 "unglossed; farewell context (inferred)" if word == "en'shu falah-nah" else "unglossed"))

# ---------------------------------------------------------------- excluded
for key, spk, why in [("NIGHTELF_UNIT_RUNNER_WARCRY1", "Night Elf Runner",
                  "Not elvish: the wiki marks Aieee kibah! as a film reference (Women of the Prehistoric Planet)."),
                 ("NIGHTELF_UNIT_HERO_DEMON_HUNTER_PISSED5", "Demon Hunter",
                  "Not elvish: a joke line, 'Hae'love green trees' spelled backwards."),
                 ("ORC_UNIT_HERO_CAIRNE_YES2", "Cairne", "Not elvish: Cairne Bloodhoof, a tauren; ishnu here is "
                  "not evidence for Darnassian ishnu.")]:
    ev, text, loc = unit_ev(key)
    cands.append({"action": "note", "word": text.rstrip(".!").lower(), "translation": None,
                  "source": None, "canon_basis": None, "notes": why, "evidence": [ev], "method": BASE,
                  "confidence": "low", "reason": "Excluded, recorded so later passes skip it."})
    rows.append(("x", text, spk, loc, "", why))

out = os.path.join(REPO, "research/2026-11-revival/9-candidates.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(cands, f, ensure_ascii=False, indent=1)
    f.write("\n")
order = {"a": 0, "b": 1, "c": 2, "x": 3}
label = {"a": "(a) lexicon", "b": "(b) wiki", "c": "(c) new", "x": "excluded"}
with open(OUT_MD or os.devnull, "w", encoding="utf-8") as f:
    f.write("| Class | Blizzard's text | Speaker | Where | Wiki spelling | Meaning and basis |\n")
    f.write("|---|---|---|---|---|---|\n")
    for r in sorted(rows, key=lambda r: order[r[0]]):
        f.write("| %s | %s | %s | `%s` | %s | %s |\n" % (label[r[0]], r[1], r[2], r[3], r[4] or "", r[5]))
print("wrote", out, "(%d candidates, %d table rows)" % (len(cands), len(rows)))
