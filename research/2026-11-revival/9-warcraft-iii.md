# Warcraft III: Reforged 3.0 game files (build 3.0.1.24371)

Date: 2026-11-18. Input: the local install in `/Applications/Warcraft III` (product `w3`, region eu, build 3.0.1.24371, English text and speech only), read without writing to it and without starting the game. Tools: [tools/wc3](../../tools/wc3/). Candidates: [9-candidates.json](9-candidates.json), built by [scripts/wc3_candidates.py](scripts/wc3_candidates.py). No earlier pass read Warcraft III files; the Warcraft III lines already in the lexicon came through the wiki.

## What this pass found

1. **Two titles get a second, independent Blizzard gloss and can enter the lexicon.** The lexicon had only their parts (*shan*, *do*, *thero*).
   - *Shan'do* "honored teacher" is Malfurion's title in 15 campaign strings. Blizzard's zhTW localization renders it 尊師 ("honored teacher") in all 15, and zhCN renders it 大导师 ("grand teacher"). The wiki primer gives "Honored Teacher" from the Warcraft Encyclopedia and APG. Two sources agree, so this is confirmed.
   - *Thero'shan* "honored student" is spelled *thero-shan* in the game, in Malfurion's line to the druids of the claw (NightElf05). zhTW renders it 愛徒 ("beloved disciple"). "Student" is confirmed by two sources; "honored" rests on the primer alone.
2. **The new 3.0 gear items give *sin'dorei* its second Blizzard gloss.** The Band of the Sin'dorei says the sin'dorei are "children of the blood" (`Units/ItemStrings.txt:3289`). Until now the Warcraft Encyclopedia was the only source.
3. **The game has its own spelling for 22 elvish unit lines that the wiki writes down by ear, and 15 of them differ.** For 18 of them, the game's sound table and the wiki's [quote lists](https://warcraft.wiki.gg/wiki/Quotes_of_Warcraft_III/Night_Elf_Sentinels#Warden) name the same voice file, so they are the same line. The other 4 (one Blood Mage line and the 3 naga lines) match by text and speaker. Examples: Malfurion's *Anu'dorini Talah* is *Ana'doreini talah* in the game, Maiev's *Ashal thera'das* is *Al'shar Thoridas*, the Warden's *Ashbalanol* is *Ash'valanor* and *Bathel'daelune* is *Benthai del Elune*, the Demon Hunter's *Deronica* is *Dorune'ka*, and the Spell Breaker's *Endirina-dor* is *Inde'rinah-dor*. None of these lines is glossed anywhere.
4. **One line is new to both the lexicon and the wiki:** the Warden's *Morothoray katal* (`DialogueNightElfBase.fdf:173`). The wiki's Warden list skips that voice file. It is unglossed.
5. **WoW's language scrambler appears to borrow from Warcraft III.** Blizzard's spelling *al'shar* (Maiev's line) is a word in WoW's Darnassian, Thalassian and Shen'dorei garble lists, and so are *andu*, *thero'shan* and *talah*. A WoW line that uses one of these words may be scrambler output, so it does not count as an independent source for them.
6. **The new campaign's text is locked.** The 20 Forsaken Kingdom maps are encrypted, so none of their subtitles or quest text could be read. Its 1,233 voice files are local, including 45 Sylvanas lines and four speakers whose names look elven, but no free speech-to-text tool is installed, so they are not transcribed.
7. **Every other elvish line is already known.** 12 phrases already in the lexicon (11 campaign lines and Maiev's war cry *Tor ilisar'thera'nal*) appear with the lexicon's spelling and add nothing new. Only Shan'do and thero-shan are translated by a localization: zhCN and zhTW keep the other elvish lines in Latin letters, and koKR and ruRU transliterate them.

## What Warcraft III 3.0 is, and how much of it this pass could read

Patch 3.0 added **Forsaken Kingdom**, the first new Warcraft III campaign in 23 years ([PC Gamer](https://www.pcgamer.com/games/rts/blizzard-just-dropped-a-new-warcraft-3-campaign-the-first-in-23-years/)). Blizzard's [deep-dive recap](https://news.blizzard.com/en-us/article/24298590/warcraft-iii-reforged-forsaken-kingdom-deep-dive-recap) describes two parts: a prologue, *The Last Days of Lordaeron*, with four linear missions, and a main campaign with a soft open-world RPG structure set in Stratholme and the Undercity. The patch also brought a new hero (the Forsaken Paladin), gear slots and items, a Definitive Edition graphics mode and a 24-unit selection cap. The installed build is 3.0.1; [Liquipedia's Patch 3.0.1 page](https://liquipedia.net/warcraft/Patch_3.0.1) dates it to October 19, 2026, which is not independently confirmed.

| Part of 3.0 | In the files | Read? |
|---|---|---|
| Prologue maps (speakers Garek, Landen, Ilastar, Uther, Arthas ...) | `Campaign/ForsakenKingdom/HumanRE01`–`04` and `HumanRE02Interlude`, `.w3xd` | No: encrypted |
| Main campaign maps | 15 `UndeadRE*.w3xd` maps | No: encrypted |
| Prologue voice | 330 files, 15.8 MB (`Sound/Dialogue/HumanRECamp`) | Listed, not transcribed |
| Main campaign voice | 903 files, 56.7 MB (`Sound/Dialogue/UndeadRECamp`) | Listed, not transcribed |
| Lip-sync files (FaceFX) | 240 local, 726 not downloaded | Read: speaker names and line IDs only, no words |
| Gear items (Garek's and Anya's backpacks, Band of the Sin'dorei, Echoes of the Fallen, the Dark Ranger set ...) | `Units/ItemStrings.txt` | Read |
| Forsaken Paladin voice subtitles | `Strings/DialogueCreepsBase.fdf` | Read: English only |
| Closing cinematic captions | `Movies/Captions/OutroRE.srt` | Read: English only |

The encryption is DRM on the paid campaign; this pass did not try to break it. The voice files are the only way into the new campaign's dialogue.

Sylvanas, a known elf, has 45 files in the new campaign. Four more speakers have names that look elven, which is not confirmed: Ilastar (52 files), Lorthiras (2, prologue), Kaelystia (2) and Melisara (2). Anya has 221 files; her race is not stated anywhere this pass could read.

## Method

1. **Storage.** [tools/wc3/w3casc.py](../../tools/wc3/w3casc.py) reads the CASC storage through the unchanged [tools/wowf/casc.py](../../tools/wowf/casc.py). Warcraft III's root file is plain text, one `path|content key|tags` line per file; 105,285 of its 175,345 entries are present locally.
2. **Maps.** [tools/wc3/mpq.py](../../tools/wc3/mpq.py) is a small read-only MPQ reader for the `.w3m`/`.w3x` maps: it handles the encrypted hash and block tables, sectored and encrypted files, and zlib and bzip2 compression. It read 466 of the 486 maps. Each map carries its string table in 13 more locales, so localized campaign text is available even with only English installed.
3. **Extraction.** [tools/wc3/extract_text.py](../../tools/wc3/extract_text.py) writes every text file, map string table, map script and lip-sync name list to the gitignored `.wc3-extract/` folder: 479 text files (28.3 MB), 1,964 FaceFX name lists and 10,973 map members, in about 7 seconds.
4. **Mining.** [tools/wc3/mine.py](../../tools/wc3/mine.py) parses the unit subtitles (`Strings/Dialogue*Base.fdf`), the map string tables with their speakers and sound files (from each map's `conversation.json`), the cinematic captions and all other text. It flags a token when it is not an English word and is a lexicon form, contains an elvish root, is spoken by an elf, is joined by an apostrophe or hyphen, or scores high on a character-trigram model trained on Blizzard's elvish forms. It took about 49 seconds: 4,272,491 text records, 41,353 with a flagged token, and 1,895 distinct flagged tokens, most of them names or English.
5. **Hand review.** Each flagged line was checked against the lexicon and the wiki: the [Thalassian](https://warcraft.wiki.gg/wiki/Thalassian#Untranslated_words_or_phrases), [Darnassian](https://warcraft.wiki.gg/wiki/Darnassian#Untranslated_phrases) and [Nazja](https://warcraft.wiki.gg/wiki/Nazja#Phrases) pages, and the [Night Elf](https://warcraft.wiki.gg/wiki/Quotes_of_Warcraft_III/Night_Elf_Sentinels) and [Human](https://warcraft.wiki.gg/wiki/Quotes_of_Warcraft_III/Human_Alliance) quote lists, fetched raw on 2026-11-18. A unit line matches a wiki line when both point to the same voice file: the game's sound table (`UI/SoundInfo/Dialogue*Base.slk`) maps each subtitle key to its file, and the wiki names the file next to each quote. That holds for 18 of the 22 unit lines; the other 4 match by text and speaker.
6. **Meanings.** A meaning counts only when the game text, or a cited source, pairs the elvish with English. Context such as "Farewell ..." next to *En'shu falah-nah* is recorded as context and not as a gloss.

## Counts

| | Count |
|---|---|
| Elvish words and phrases found | 41 |
| (a) already in the lexicon | 14: 11 campaign phrases, 2 unit lines (*Ana'doreini talah*, *Tor ilisar'thera'nal*) and *sin'dorei* |
| (b) on the wiki, not in the lexicon | 26 (5 Thalassian, 16 Darnassian, 5 Nazja) |
| (c) new to both | 1 (*Morothoray katal*) |
| With a meaning | 16: the 14 in (a), plus *Shan'do* and *thero'shan* from (b) |
| New meanings for the lexicon | 2 (*shan'do*, *thero'shan*); 1 second source (*sin'dorei*) |
| Excluded after review | 3: *Haieee kibah!* (a film reference, says the wiki), *Seert neerg evol'eah!* (English spelled backwards) and *Ishnu'porah* (said by Cairne, a tauren) |
| Campaign voice files of elven speakers (all campaigns) | 1,005 (63.0 MB), not counting the HD and DE copies |
| New-campaign voice files | 1,233 (72.5 MB) |

The three place names on the wiki that also appear in the game, *Izal-Shurah*, *Arauk-nashal* (in a Reforged Maiev line) and *Quel'Danas*, have no gloss and are left out of the counts.

## Findings

"Where" is a path in the build: unit subtitles are under `War3.w3mod:_Locales/enUS.w3mod:Strings/`, items under `War3.w3mod:_Locales/enUS.w3mod:`, and map strings under `War3.w3mod:Campaign/`. The candidates file has each one's full path, key and sound file. "Unglossed" means no source pairs the line with English, so it is not independently confirmed what it means.

| Class | Blizzard's text | Speaker | Where | Wiki spelling | Meaning and basis |
|---|---|---|---|---|---|
| (a) lexicon | Ana'doreini talah! | Malfurion (unit war cry) | `DialogueNightElfBase.fdf:138` | Anu'dorini Talah | let my will be known (lexicon, attested); Blizzard's spelling differs |
| (a) lexicon | sin'dorei | item Band of the Sin'dorei (3.0 gear) | `Units/ItemStrings.txt:3289` | Sin'dorei | **children of the blood**: the item says so; second Blizzard source (attested, confirmed) |
| (a) lexicon | (English only) | item Echoes of the Fallen (3.0 gear) | `Units/ItemStrings.txt:2784` | Anar'alah belore / Shindu fallah na / Shindu sin'dorei | the primer's English for these three, word for word; no elvish in the item |
| (a) lexicon | Ishnu-alah, sisters! | Tyrande | `Reforged/ROC/NightElf02.w3x STRING 219` | same | good fortune to you (lexicon) |
| (a) lexicon | Ishnu-dal-dieb, Shandris. | Tyrande | `Reforged/ROC/NightElf02.w3x STRING 76` | same | good fortune to your family (lexicon) |
| (a) lexicon | Elune-adore, Priestess. | Archer | `Reforged/ROC/NightElf02.w3x STRING 200` | same | Elune be with you (lexicon) |
| (a) lexicon | Fandu-dath-belore? | Archer | `Reforged/ROC/NightElf02.w3x STRING 217` | same | who goes there? (lexicon) |
| (a) lexicon | Then I will put an end to their curse! Andu-falah-dor! | Tyrande | `Reforged/ROC/NightElf04.w3x STRING 288` | same | let balance be restored (lexicon) |
| (a) lexicon | Bandu thoribas, mortals! | Tyrande | `Reforged/ROC/NightElf01.w3x STRING 55` | same | prepare to fight (lexicon) |
| (a) lexicon | Then I'll make my stand here, butcher. Anar'alah belore. | Sylvanas | `Reforged/ROC/Undead05.w3x STRING 63` | same | by the light of the sun (lexicon) |
| (a) lexicon | Bash'a no falor talah! | Sylvanas | `Reforged/ROC/Undead05.w3x STRING 115` | same | taste the chill of true death (lexicon) |
| (a) lexicon | Shindu fallah Na! Fall back to the second gate! | Sylvanas | `Reforged/ROC/Undead03.w3x STRING 51` | same | they're breaking through! / our enemies are breaking through (lexicon) |
| (a) lexicon | Ash Karath! | Illidan | `Reforged/TFT/NightElfX05.w3x STRING 120` | same | do it (lexicon) |
| (a) lexicon | Ande'thoras-ethil, brother. | Malfurion | `Reforged/TFT/NightElfX08.w3x STRING 219` | same | may your troubles be diminished (lexicon) |
| (a) lexicon | Tor ilisar'thera'nal! | Maiev (unit war cry) | `DialogueNightElfBase.fdf:159` | same | let our enemies beware (lexicon) |
| (b) wiki | Shan'do | Druid of the Claw, Dryad (NightElf03, NightElf05) | `Reforged/ROC/NightElf03.w3x STRING 186, and 14 more strings` | Shan'do | **honored teacher**: wiki primer, and zhTW 尊師 in all 15 strings (attested, confirmed) |
| (b) wiki | thero-shan | Malfurion (NightElf05) | `Reforged/ROC/NightElf05.w3x STRING 139` | Thero'shan | **honored student**: wiki primer, and zhTW 愛徒 'beloved disciple' (attested; 'student' confirmed) |
| (b) wiki | Andu fallah. | Blood Mage | `DialogueHumanBase.fdf:175` | Andu fallah. | unglossed |
| (b) wiki | Aseph-ah-balla nah. | Blood Mage | `DialogueHumanBase.fdf:173` | Aseph-ah-balla nah. | unglossed |
| (b) wiki | Ish-shera-do. | Blood Mage | `DialogueHumanBase.fdf:179` | Ishera-do. | unglossed |
| (b) wiki | Endo-enah Quel'Thalas! | Kael'thas | `DialogueHumanBase.fdf:161` | Endo-enah Quel'Thalas! | unglossed |
| (b) wiki | Inde'rinah-dor Highborne! | Spell Breaker | `DialogueHumanBase.fdf:201` | Endirina-dor Highborne! | unglossed |
| (b) wiki | Anu'dora! | Tyrande; also Malfurion and the Druid of the Claw | `DialogueNightElfBase.fdf:52` | Anu'dora! | unglossed |
| (b) wiki | Enu ri'fah! | Tyrande | `DialogueNightElfBase.fdf:51` | Hinduli rathal! | unglossed |
| (b) wiki | Ashe'tor'aman. | Tyrande | `DialogueNightElfBase.fdf:58` | Ashre thoraman. | unglossed |
| (b) wiki | Anu'therador mali | Tyrande | `DialogueNightElfBase.fdf:64` | Anu therador mali. | unglossed |
| (b) wiki | Tor fal-anu'dora! | Malfurion | `DialogueNightElfBase.fdf:128` | Tor falah-no dorah! | unglossed |
| (b) wiki | Ash'thera'falla-dor. | Malfurion | `DialogueNightElfBase.fdf:131` | Ash'thero danador. | unglossed |
| (b) wiki | Al'shar Thoridas! | Maiev | `DialogueNightElfBase.fdf:146` | Ashal thera'das! | unglossed |
| (b) wiki | Ash'valanor | Warden | `DialogueNightElfBase.fdf:177` | Ashbalanol. | unglossed |
| (b) wiki | Benthai del Elune | Warden | `DialogueNightElfBase.fdf:178` | Bathel'daelune. | unglossed |
| (b) wiki | Dorune'ka | Demon Hunter (also the female demon hunter) | `DialogueNightElfBase.fdf:300` | Deronica. | unglossed |
| (b) wiki | Anu'dor anu'dor. | Demon Hunter (also the female demon hunter) | `DialogueNightElfBase.fdf:302` | Anato retetour! | unglossed |
| (b) wiki | Ara'deno'filorei! | Naisha | `DialogueNightElfBase.fdf:223` | Ara'denu thelore! | unglossed |
| (b) wiki | Ash'valana thure. | Naga Siren | `DialogueNagaBase.fdf:24` | Ash'valana thure. | unglossed |
| (b) wiki | Era'sazjar! | Lady Vashj | `DialogueNagaBase.fdf:81` | Era'sazjar! | unglossed |
| (b) wiki | Athero bathre'las! | Lady Vashj | `DialogueNagaBase.fdf:95` | Athero bath'rilas! | unglossed |
| (b) wiki | … Anadunathara! | Tyrande | `Reforged/ROC/Prologue01.w3x STRING 557` | Ana duna thera | unglossed |
| (b) wiki | … En'shu falah-nah. | Illidan | `Reforged/TFT/NightElfX08Finale.w3x STRING 267` | En'shu falah-nah | unglossed; farewell context (inferred) |
| (b) wiki | Ash-thero-sauguine! Ba'anthalso-dorei! | Naga (myrmidon) | `Reforged/TFT/NightElfX02.w3x STRING 122` | Ash-thero-sauguine! (also Ash'thero sanguine!) and Ba'anthalso-dorei! | unglossed (two phrases) |
| (c) new | Morothoray katal | Warden | `DialogueNightElfBase.fdf:173` | none | unglossed |
| excluded | Haieee kibah! | Night Elf Runner | `DialogueNightElfBase.fdf:201` |  | Not elvish: the wiki marks Aieee kibah! as a film reference (Women of the Prehistoric Planet). |
| excluded | Seert neerg evol'eah! | Demon Hunter | `DialogueNightElfBase.fdf:312` |  | Not elvish: a joke line, 'Hae'love green trees' spelled backwards. |
| excluded | Ishnu'porah. | Cairne | `DialogueOrcBase.fdf:41` |  | Not elvish: Cairne Bloodhoof, a tauren; ishnu here is not evidence for Darnassian ishnu. |

## Parts that recur (leads, not meanings)

These are inferred from spelling alone. None of them is a gloss, and none is proposed for the lexicon.

1. **anu'dor-** appears in *Anu'dora* (Tyrande, Malfurion, the Druid of the Claw), *Anu'dor anu'dor* (the Demon Hunter), *Tor fal-anu'dora* (Malfurion) and *Ana'doreini talah*, which is the lexicon's *anu'dorini talah* "let my will be known".
2. **fal(l)a(h)** appears in *Andu fallah*, *Tor fal-anu'dora*, *Ash'thera'falla-dor*, *En'shu falah-nah* and the known *andu-falah-dor* and *shindu fallah na*. Both *En'shu falah-nah* and *andu-falah-dor* (report 4) are said at a parting.
3. **-dor** ends *Inde'rinah-dor*, *Ash'thera'falla-dor* and the known *andu-falah-dor*.
4. **ash'ther- / athero** appears in Malfurion's *Ash'thera'falla-dor* and in the naga lines *Ash-thero-sauguine* and *Athero bathre'las*; report 7 already counts *thero* in the shared core.

## Limits

1. The new campaign's maps are encrypted, so its text is not covered at all. Only its items, the Forsaken Paladin's subtitles, the closing captions and the list of its voice files are.
2. No speech was transcribed. The unit lines have Blizzard subtitles, but the two Sentinel lines in the orc mission Orc04 (`O04FemaleNEA04.ogg` and `O04FemaleNEB05.ogg`) have none. The wiki writes the Sentinels' lines in that mission by ear as *Anu dunah thalore. Iseradune banthalos* and *Ash'therod nethanas*.
3. The game's spellings are Blizzard's own, but nobody has checked them against the voice yet. The wiki's spellings are by ear. Where the two differ, the voice files would show which is closer.
4. Only English text is installed. The maps carry 13 more locales, but the unit subtitles and items exist only in English locally. The Japanese and Thai campaign string tables are about a quarter the size of the English ones and hold none of the elvish lines.
5. A single build cannot show which lines are new in 3.0. The gear items are 3.0 content by their names (Garek's and Anya's backpacks belong to the new campaign's heroes); the rest is older.

## What would add more

1. **Chinese unit subtitles.** The zhTW and zhCN versions of the unit subtitle and item files are in the storage's index but not downloaded. Their localizers translated *thero-shan* and *Shan'do*, so they may have translated some of the 21 unglossed unit lines too. Cost: adding zhTW and zhCN text in the Battle.net app downloads about 60 MB of non-speech files per locale (about 540 MB each with speech). After that, `extract_text.py --locales enUS,zhTW,zhCN` reads them in seconds.
2. **Transcribing the new campaign.** The 1,233 new-campaign voice files (72.5 MB) are the only way to its dialogue. Report 5 paid $2.59 for 588 files on fal.ai, so all 1,233 would cost about $5.40, and only Sylvanas and the four elven-looking names (103 files) about $0.45. That is under the $20 limit but still paid, so it waits for a yes. A free local option, whisper.cpp, would need a download first. `ffmpeg` is installed; no speech-to-text tool is.
3. **Transcribing the two Orc04 Sentinel lines** (119 KB) and the 23 elvish unit lines. That would settle their spellings against the voice. It costs a few cents on the same service.
4. **The new campaign's text** would need the decrypted maps. This pass does not try that.

## Reproduce

From the repo root. The first command takes about 7 seconds, the second about 49 seconds and writes `.wc3-extract/analysis/` (`records.tsv` is 443 MB).

```
python3 tools/wc3/extract_text.py --install "/Applications/Warcraft III" --out .wc3-extract
```

```
python3 -I tools/wc3/mine.py --base .wc3-extract --lexicon src/thalassian/data/lexicon.json --wowf .wowf-extract --wiki Thalassian.txt Darnassian.txt
```

```
python3 -I research/2026-11-revival/scripts/wc3_candidates.py .
```

The two wiki files are the raw pages, for example `https://warcraft.wiki.gg/index.php?title=Thalassian&action=raw`. The extract is Blizzard data and stays out of git; this report and the candidates file quote only single lines.
