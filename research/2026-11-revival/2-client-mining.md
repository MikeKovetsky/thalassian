# Phase 2: mining the WoW Forever client

**Answer first.** The WoW Forever client (product `wowf`, 1.60.1.70938) is readable end to end, and
it holds one genuinely new Elvish source: the Skyborne, a high-elf race whose own name is
**shen'dorei** ("hidden people"), with a language of their own (Languages row 310) and a new zone
of Elvish place names on Zephras Isle. It gives **three meanings the project never had**:
*shen'dorei* = the Skyborne, *Esarus thar no'Darador* = "By Blood and Honor We Serve", and
*Jai'vhanel* = "Swordfeather". It does **not** contain NPC speech in bulk: the text the project
mined from Wowhead for Midnight lives on Blizzard's servers, and the client only keeps what one
player has seen. None of the Elvish words the project skipped in March gets a meaning from this
client.

Candidates: [2-candidates.json](2-candidates.json) (18 additions, 9 corrections). Raw data and
scripts: `.wowf-extract/` (local only, see its README) and `tools/wowf/`.

## 1. What the client can and cannot tell us

**It can tell us:**

1. **Exact Blizzard spellings** of every place, race, faction, item, spell and achievement name in
   this product: 811,592 strings in all.
2. **Name-to-meaning pairs where Blizzard states them**: race names next to lore names
   (ChrRaces), a motto with its translation (a page text), an alias in a quest ("also known as").
3. **The garble word lists** the game uses to scramble speech in each language (LanguageWords).
   These are a phonotactic corpus: real Blizzard word shapes, but meaningless filler.
4. **The name generator lists** (NameGen) for each race, including 537 new Skyborne names.
5. **Voice-over files** whose meaning is fixed by the game: emote lines (hello, bye, thank you,
   you're welcome) and NPC greetings and farewells. We extracted the 196 Skyborne ones.

**It cannot tell us:**

1. **NPC speech.** BroadcastText.db2 ships with 12 rows (the Skyborne intro cinematic). The other
   127 lines came from the server when this account met those NPCs. No cached line is tagged
   Thalassian (10) or Shen'dorei (310); all are Common (7) or untagged (0).
2. **Quest text**, except the 99 quests this account has seen (`questcache.wdb`). QuestV2.db2 has
   IDs and flags only.
3. **What a garble word means.** LanguageWords exists to produce fake speech.
4. **Hidden content.** Three TACT keys are not public (`0DA4670DB36FB2A9`, `DA0E7785727A0A65`,
   `3146BA4C4ECDBFAB`); they hide 61 DB2 sections, including parts of AreaTable, Map, QuestV2,
   Spell, SpellName and ItemSparse.
5. **The words of the voice lines.** They are audio; someone has to listen and transcribe. Done for the 196 extracted files on 2026-11-18, by up to four machine listeners ([report 5](5-voice-transcription.md)).

## 2. How the data was read

`tools/wowf/casc.py` (Python standard library only) runs on the Mac mini against the local CASC
storage: it reads `.build.info`, the v7 indices, the encoding file and the version-2 MFST root,
decodes BLTE (zlib, and Salsa20 with the community key list), and writes only the requested files
to `~/thalassian-scratch` (218 MB at peak, deleted afterwards). No 48 GB copy was needed.
`tools/wowf/db2.py` reads WDC5 with [WoWDBDefs](https://github.com/wowdev/WoWDBDefs) definitions,
`hotfix.py` reads `DBCache.bin` (XFTH v9), `wdb.py` reads the WDB caches, and `export_all.py`
writes the CSVs. The whole run, `tools/wowf/run_all.sh`, takes 1 min 28 s from scratch.

**Parser check against an independent source.** The retail tables published by
[wago.tools](https://wago.tools/db2/LanguageWords) (retail 12.1.5.70961, built with Blizzard's
DBCD library) match ours: 1,486 of 1,488 shared LanguageWords rows are identical, and the two that
differ are real Forever edits (the Zombie language's "Brains", "Braainss"). All 102 Thalassian and
102 Darnassian garble words are identical to retail.

## 3. Inventory

| Source | Rows here | What it can give | What it cannot |
|---|---:|---|---|
| BroadcastText (NPC speech) | 139 (12 shipped + 127 cached) | English text, LanguageID, sound kit for lines seen in play | Bulk speech; any Thalassian or Shen'dorei-tagged line (none cached) |
| Languages | 16 | Language names; **310 "Shen'dorei" is new** | Grammar, meanings |
| LanguageWords | 1,592 | Garble lists: Darnassian 102, Thalassian 102, Shen'dorei 102 | Meanings (filler by design) |
| ChrRaces | 58 | Race name next to lore name: Kaldorei, Sin'dorei, Shal'dorei, Ren'dorei and **Shen'dorei (95, 96)** | Etymology |
| NameGen | 2,737 | Name stock per race; races 95/96 (Skyborne) are new | Meanings |
| Creature + creaturecache | 189 + 795 | NPC names and titles met in play | NPCs not met; Zephras Isle NPCs are mostly absent |
| AreaTable, WMOAreaTable, Map, UiMap | 1,404, 52,737, 78, 60 | Every place name, including Zephras Isle, Shen'dralas and the new dungeons | Etymology; hidden rows in 2 encrypted AreaTable sections |
| ItemSparse, ItemSearchName, ItemSet | 24,750, 11,589, 545 | Item names and flavor text (e.g. "Valanaar" missive, "Shen'dorei Windwell") | Hidden rows in 1 encrypted section |
| Spell, SpellName | 32,492 each | Spell names and descriptions (Eluvi'ana, Eluvi'tor) | Spell shouts (server-side) |
| Achievement, Toy, Mount, CharTitles | 495, 22, 144, 41 | Names | Nothing Elvish beyond place names |
| Faction | 253 | Shen'dorei, Shen'dralar, High Order, Windshapers, Al'Aketh with descriptions | |
| MailTemplate | 112 | Letters; #652 is a Shen'dorei druid's letter with an Elvish closing line | |
| GlobalStrings (interface) | 27,403 | All UI strings; race intro text | Elvish beyond names |
| questcache.wdb | 99 quests | Full quest text for quests seen (Darkshore, Ashenvale, Stormwind) | Any Zephras Isle quest (not played yet) |
| pagetextcache.wdb | 1 page | Turalyon memorial with *Esarus thar no'Darador* | |
| DBCache.bin hotfixes | 98,746 entries, 245 tables | Server-pushed rows, 5 TACT keys, deleted-row IDs | The 3 missing keys |
| Root + listfile | 1,251,159 files | Which files exist; the Skyborne voice folders | Words inside audio |
| Logs | Hotfix, Sound, QuestCache, Tact | Which tables and quests the server sent | No text |

## 4. What is new compared with the retail Midnight data

Checked against retail 12.1.5.70961 tables from [wago.tools](https://wago.tools/db2/Languages).

1. **The Skyborne race exists only here.** Retail has ChrRaces rows 95 and 96 as "TBD NPC Race 1"
   and "TBD NPC Race 2"; Forever names them High Order Skyborne (Alliance, Common, default class
   Mage) and Windshaper Skyborne (Horde, Orcish, default class Shaman), lore name Shen'dorei,
   models falling back to the Blood Elf.
2. **Language 310 "Shen'dorei" exists only here.** Its 102 garble words are the Darnassian list
   word for word, so the client treats Shen'dorei as Darnassian-sounding. The Thalassian and
   Darnassian lists differ in only one spelling: Thalassian *Fallah* / *Shindu'fallah'na* against
   Darnassian *Falla* / *Shindu'falla'na*.
3. **New NameGen lists** for races 95/96 (537 names). Their signature is long vowels written
   double, rare elsewhere: *Alaan, Valaan, Algaan, Fandaal, Jesaan, Vraal, Lokaa, Elransiaal,
   Tevaan, Falfaan, Sriaal, Zriaal, Beliaa*. Several are English wind words given an Elvish ending:
   *Zepha* (zephyr), *Cyclaas* (cyclone), *Sirocaas* and *Siroccaa* (sirocco), *Zephraalis*.
4. **New Elvish place names**: Zephras Isle with Valanaar, Shen'dar, Thendal, Falaath and the
   Ruins of Ban'aethal; and Shen'dralas, a new Kalimdor zone around Desolace's Valley of Bones.
5. **Retail has what Forever lacks**: 45 languages against 16, including Shalassian (181, 141
   garble words) and a second Thalassian (182). Forever has none of the Midnight content.

## 5. The words we skipped

### 5a. From the project's own past

`tools/wowf/history_tokens.py` read every blob in the repo's git history (93 blobs). It found 94
Elvish-looking tokens that never became lexicon entries (plus 31 whose parts are entries). About 40
are real Elvish; the rest are English or code. Two words were also dropped from the lexicon after
the first commit: *bal* "hello" and *sindo* "blood".

**Result: the Forever client gives none of them a meaning.** It is a Vanilla-era world plus the
Skyborne, so the Midnight and Burning Crusade phrases are simply not in it.

| Skipped token (where it was) | In the client? |
|---|---|
| *a'manore, anu'men, Band'or, Elu'meniel, felallan, Felomin, lor'ma, noral'arkhana, Shalla'tor, An'da, Min'da* (lexicon notes) | Absent |
| *Anu'dorini, Fal'inrush, Arcan'dor, Xal'atath* (sample text in the deleted `scraper_wowhead.py`) | Absent. *Anu'dorini* is close to the garble word *Anu'dorinni'talah*. |
| *Ameth'Aran, Bashal'Aran* (lexicon notes for *aran*) | Present as Darkshore ruins (AreaTable 447, 446), with Lake Al'Ameth (259) and Ordil'Aran (412). No meaning. |
| *Quel'Thalas, Quel'Serrar, Felo'melorn, Kael'thas, Quel'dorei* | Present as names only |
| *E'rath, Omnas, Rath-domaas, Ith'el, Ith'nala, Kanesh* (notes for *rath* and *kanesh*) | Absent from Forever, but all six are words in **retail's Shalassian garble list** (wago.tools, LanguageWords 181). See the corrections. |
| *bal, sindo* (dropped entries) | No evidence either way |
| *anu'a, Ari'a, Carth'o, dal'thielin, dalah'shola, Dorei'a, Mith'o, dela'ash* | The project's own generated output, not skipped canon |

### 5b. From the client corpus

`tools/wowf/mine_tokens.py` scored the 20,333 non-English tokens in the corpus with a trigram
model trained on Blizzard's own Elvish word shapes (the three Elvish garble lists, the Skyborne
names and the canon lexicon) against every other language's garble list and English. The 420
highest-scoring tokens (after dropping tokens seen only in the name generator or in file names)
were read by hand, together with every string carrying a gloss cue ("also known as", "means",
"translate") and every Elvish name followed by an English epithet. Ranked by evidence strength:

| Rank | Form | Meaning | Evidence | Strength |
|---|---|---|---|---|
| 1 | **shen'dorei** | hidden people; the Skyborne | ChrRaces 95/96 pair "Skyborne" with lore name "Shen'dorei"; BroadcastText 316349 "These "Skyborne," as they call themselves"; Languages 310; [Blizzard: "the Skyborne, also known as the shen'dorei or hidden people"](https://worldofwarcraft.blizzard.com/en-us/news/24304071) | High, canon |
| 2 | **esarus thar no'darador** | "By Blood and Honor We Serve" | pagetextcache 290: "Esarus thar no'Darador' - By Blood and Honor We Serve." | High, canon (phrase only; word order not stated) |
| 3 | **eldre'thalas** | the ancient Highborne city, now Dire Maul | BroadcastText 307136 "...Eldre'Thalas - the ancient city of my people... Dire Maul, I believe it is commonly called these days" | High (referent) |
| 4 | **shen'dralar** | Highborne order of Eldre'Thalas | Faction 809; BroadcastText 313613 "I still count myself among the Shen'dralar" | High (referent) |
| 5 | **jai'vhanel** | "Swordfeather" (owl in Darkshore) | questcache 98025: the owl "Jai'vhanel" also known as "Swordfeather" | Medium, canon alias |
| 6 | **shen** | hidden | shen'dorei = "hidden people" minus *dorei*; the same stem names the Shen'dralar, Shen'dralas and Shen'dar. A "sky" reading from the English name Skyborne does not fit Shen'dralar. | Medium, inferred |
| 7 | **-naar** | place, settlement | Dolanaar, Astranaar, Thalanaar, Falanaar, Vor'danaar and the new Valanaar are all elven places | Medium, inferred |
| 8 | **eluvi'ana** | "the Night Dancer", an ancient Shen'dorei spirit | Spell 1314923: "Raising Eluvi'ana, the Night Dancer." | Medium (epithet, may not be literal) |
| 9 | **valanaar, shen'dar, shen'dralas** | Skyborne town; Zephras highlands and village; new Kalimdor zone | AreaTable 16638, 16623/16624, 16651; GameObjects 652536/7; items | Medium (referents) |
| 10 | **eluvi'tor, thendal, falaath, ban'aethal, zephras** | Imbued Hilt; Zephras place names | Spell 1314956; AreaTable 16622, 16636, 16833, 16593 | Low (names only) |
| 11 | **aeesha'el banu zepharaalis** | closing blessing of a Shen'dorei letter, untranslated | MailTemplate 652, before the signature of Lotheluum Starbreeze | Low |
| 12 | **ursera** | a clawed, feathered Zephras beast | Item names only (ItemSparse 251918 and others) | Low |

Seen but not proposed, because the client gives no referent or the name is not Elvish:
*Quel'Shalla* (a 1.60.1 quest, CriteriaTree 234624), *Urs'endris*, *Lotheluum*, *Ur'seris*,
*Al'Aketh* and *Akir* (the air cult and Al'Akir the Windlord, elemental naming), *Rohashi* (from
Rohash, an air-elemental boss whose portrait `UI-EJ-BOSS-Rohash.blp` is in the client),
*Ataal'Byzal* and *I'lalai* (troll), *Krol'dok* (orc).

**Overlap with [3-candidates.json](3-candidates.json).** That file came from the web and covers
*shen'dorei, shen, shen'dralar, eluvi'ana, naar, aeesha'el banu zepharaalis, ursera* too. The
meanings agree; this file adds the client row IDs as evidence. Its gloss "Those Who Remain Hidden"
for Shen'dralar (from *Chronicle* Vol. 1) is not in the client, but fits *shen* = hidden.

## 6. Corrections to the lexicon

1. **dorei**: add Shen'dorei to the notes (ChrRaces 95/96).
2. **ethala, shari, thera, osa**: the lexicon calls these generated roots, but each is already a
   Blizzard garble word in the Darnassian, Thalassian and Shen'dorei lists. The meanings stay the
   project's own; the notes should say the form is attested.
3. **fallah**: the Thalassian garble list holds *Shindu'fallah'na* as one filler entry, so an
   in-game "Shindu fallah na!" can be garbled speech. Keep the gloss only with a non-garble source.
4. **rath, kanesh**: every word of *E'rath omnas*, *Rath-domaas* and *Ith'el kanesh* is in retail's
   Shalassian garble list; same caution.
5. **aran**: add Ordil'Aran (AreaTable 412) as a third attestation.

## 7. What is worth mining next

1. **Transcribe the Skyborne voice lines** (done on 2026-11-18: [report 5](5-voice-transcription.md)). 87 of the 196 extracted files have a meaning the game
   fixes: NPC greetings (30) and farewells (29), and player hello (8), bye (6), thank you (6),
   welcome (4) and you're welcome (4). This is how *Bal'a dash, malanore* became known for blood
   elves. Files: `.wowf-extract/skyborne_vo/`, list with categories in
   `.wowf-extract/skyborne_vo_files.csv`. To hear the female hello lines on the MacBook:

   ```
   for f in .wowf-extract/skyborne_vo/sound/character/skyborne_elf_female/*_hello_*.ogg; do echo "$f"; afplay "$f"; done
   ```

2. **Play a Skyborne character through Zephras Isle, then re-run `tools/wowf/run_all.sh`.** The
   quest, NPC and speech caches only fill with what is played; this account has played Stormwind,
   Darkshore and Ashenvale. After a Zephras run, the caches should hold the Zephras quest text, NPC
   names and any lines tagged Shen'dorei (LanguageID 310).
3. **Use the Skyborne NameGen list as a phonotactic corpus** for `phonetics/markov.py`: 537 names
   with the doubled-vowel pattern, in `.wowf-extract/NameGen.csv` (RaceID 95, 96).
4. **Check retail's Shalassian list against the lexicon.** wago.tools serves it as CSV
   ([LanguageWords](https://wago.tools/db2/LanguageWords), LanguageID 181); 39 of its 141 words are
   Shalassian-only.
5. **Re-run when the three missing TACT keys appear** in [wowdev/TACTKeys](https://github.com/wowdev/TACTKeys/blob/master/WoW.txt);
   the hidden AreaTable, Map, QuestV2 and Spell sections are likely unreleased Forever content.
