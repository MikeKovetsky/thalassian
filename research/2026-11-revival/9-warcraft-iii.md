# Warcraft III: Reforged 3.0 game files (build 3.0.1.24371)

Date: 2026-11-18. Input: the local install in `/Applications/Warcraft III` (product `w3`, region eu, build 3.0.1.24371, English text and speech only), read without writing to it and without starting the game. Tools: [tools/wc3](../../tools/wc3/). Candidates: [9-candidates.json](9-candidates.json), built by [scripts/wc3_candidates.py](scripts/wc3_candidates.py). No earlier pass read Warcraft III files; the Warcraft III lines already in the lexicon came through the wiki.

## What this pass found

1. **Two titles get a second, independent Blizzard gloss and can enter the lexicon.** The lexicon had only their parts (*shan*, *do*, *thero*).
   - *Shan'do* "honored teacher" is Malfurion's title in 21 Reforged campaign strings; Maiev says 14 of them. Blizzard's zhTW localization renders it 尊師 ("honored teacher") in all 21, and zhCN renders it 大导师 ("grand teacher") in all 21. The wiki primer gives "Honored Teacher" from the Warcraft Encyclopedia and APG. Two sources agree, so this is confirmed.
   - *Thero'shan* "honored student" is spelled *thero-shan* in the game, in Malfurion's line to the druids of the claw (NightElf05). zhTW renders it 愛徒 ("beloved disciple"). "Student" is confirmed by two sources; "honored" rests on the primer alone.
2. **The new 3.0 gear items give *sin'dorei* its second Blizzard gloss.** The Band of the Sin'dorei says the sin'dorei are "children of the blood" (`Units/ItemStrings.txt:3289`). Until now the Warcraft Encyclopedia was the only source.
3. **The game has its own spelling for 22 elvish unit lines that the wiki writes down by ear, and 15 of them differ.** For 21 of them, the game's sound table and the wiki's [quote lists](https://warcraft.wiki.gg/wiki/Quotes_of_Warcraft_III/Night_Elf_Sentinels#Warden) name the same voice file, so they are the same line. The Blood Mage's *Ish-shera-do* matches by text and speaker, because the wiki files it under another number. Examples: Malfurion's *Anu'dorini Talah* is *Ana'doreini talah* in the game, Maiev's *Ashal thera'das* is *Al'shar Thoridas*, the Warden's *Ashbalanol* is *Ash'valanor* and *Bathel'daelune* is *Benthai del Elune*, the Demon Hunter's *Deronica* is *Dorune'ka*, and the Spell Breaker's *Endirina-dor* is *Inde'rinah-dor*. None of these lines is glossed anywhere.
4. **One line is new to both the lexicon and the wiki:** the Warden's *Morothoray katal* (`DialogueNightElfBase.fdf:173`). The wiki's Warden list skips that voice file. It is unglossed.
5. **WoW's language scrambler appears to borrow from Warcraft III.** Blizzard's spelling *al'shar* (Maiev's line) is a word in WoW's Darnassian, Thalassian and Shen'dorei garble lists, and so are *andu*, *thero'shan* and *talah*. A WoW line that uses one of these words may be scrambler output, so it does not count as an independent source for them.
6. **The new campaign's maps are encrypted; the rest of its text was read and has no elvish.** The 20 Forsaken Kingdom maps could not be read, so their dialogue, subtitles and in-mission text are not covered. The new heroes' 160 voice subtitles, the gear items, the campaign and mission names, the closing captions and two new scenario maps were read, and one of those maps holds the main campaign's quest titles. None of it has an elvish word. The campaign's 1,233 voice files are local, including 45 Sylvanas lines and three speakers whose names look elven, but no free speech-to-text tool is installed, so they are not transcribed.
7. **Every other elvish line is already known.** 12 phrases already in the lexicon (11 campaign lines and Maiev's war cry *Tor ilisar'thera'nal*) appear with the lexicon's spelling and add nothing new. Only Shan'do and thero-shan are translated by a localization: zhCN and zhTW keep the other elvish lines in Latin letters, and koKR and ruRU transliterate them.

## What Warcraft III 3.0 is, and how much of it this pass could read

Patch 3.0 added **Forsaken Kingdom**, the first new Warcraft III campaign in 23 years ([PC Gamer](https://www.pcgamer.com/games/rts/blizzard-just-dropped-a-new-warcraft-3-campaign-the-first-in-23-years/)). Blizzard's [deep-dive recap](https://news.blizzard.com/en-us/article/24298590/warcraft-iii-reforged-forsaken-kingdom-deep-dive-recap) describes two parts: a prologue, *The Last Days of Lordaeron*, with four linear missions, and a main campaign with a soft open-world RPG structure set in Stratholme and the Undercity. The patch also brought a new hero (the Forsaken Paladin), gear slots and items, a Definitive Edition graphics mode and a 24-unit selection cap. The installed build is 3.0.1; [Liquipedia's Patch 3.0.1 page](https://liquipedia.net/warcraft/Patch_3.0.1) dates it to October 19, 2026, which is not independently confirmed.

| Part of 3.0 | In the files | Read? |
|---|---|---|
| Prologue maps (speakers Garek, Landen, Ilastar, Uther, Arthas ...) | `Campaign/ForsakenKingdom/HumanRE01`–`04` and `HumanRE02Interlude`, `.w3xd` | No: encrypted |
| Main campaign maps | 15 `UndeadRE*.w3xd` maps | No: encrypted |
| Prologue voice | 330 files, 15.8 MB (`Sound/Dialogue/HumanRECamp`) | Listed, not transcribed |
| Main campaign voice | 903 files, 56.7 MB (`Sound/Dialogue/UndeadRECamp`) | Listed, not transcribed |
| Lip-sync files (FaceFX) | 230 local; 726 not downloaded (66 in each of the 11 other locales) | Read: speaker names and line IDs only, no words |
| The new heroes' voice subtitles: Garek (four versions), Landen, Ilastar and Undead Ilastar, Anya and the Forsaken Paladin | 160 lines in `Strings/DialogueHumanBase.fdf`, `DialogueUndeadBase.fdf` and `DialogueCreepsBase.fdf` | Read: English only |
| Gear items (Garek's and Anya's backpacks, Band of the Sin'dorei, Echoes of the Fallen, the Dark Ranger set ...) | `Units/ItemStrings.txt` | Read |
| Campaign, mission and cinematic names (*The Last Days of Lordaeron*, *Forsaken Kingdom*, *Homecoming* ... *Sacrifice*) | `UI/FrameDef/GlobalStrings.fdf` lines 1238–1241 and 1334–1344, `UI/CampaignInfoDLC01.txt` | Read |
| Scenario maps *Forgotten Hollow* and *Silverpine Sprint* | `Maps/ForsakenKingdom/Scenario/`, `.w3x` | Read: Forgotten Hollow's strings 556–680 are the main campaign's quest titles |
| Closing cinematic captions | `Movies/Captions/OutroRE.srt` | Read: English only |
| Opening cinematic captions (*A Lone Ship*) | none: `Movies/Captions/` has no `IntroRE.srt` | Nothing to read |

None of the new campaign's text that could be read holds an elvish word. The miner also reads every other text file in the storage whole, the unit, ability and item strings among them.

The 20 `.w3xd` maps look encrypted inside the file itself, not by the storage. Their storage layer is plain zlib, but the decoded file (5,628,151 bytes for HumanRE01) has no MPQ header and is close to random, 7.9998 bits per byte over its first megabyte. The files do not say why. Both parts are tagged `Expansion="DLC01"` in `UI/CampaignInfoDLC01.txt`, and only the prologue is open by default (`DefaultOpen=1`). This pass did not try to break the encryption, so the voice files are the only way into the new campaign's dialogue.

Sylvanas, a known elf, has 45 files in the new campaign. Three more speakers have names that look elven, which is not confirmed: Ilastar (52 files), Kaelystia (2) and Melisara (2). Ilastar's subtitles are those of a servant of the Holy Light ("Are you here for confession?"), which does not settle the race. Lorthiras, in two prologue files, is not one of them: it is a stock Dreadlord name (`Units/UndeadUnitStrings.txt:57`). Anya has 221 files; her subtitles make her one of Sylvanas's Forsaken ("I serve the Forsaken."), and her race in life is not stated anywhere this pass could read.

## Method

1. **Storage.** [tools/wc3/w3casc.py](../../tools/wc3/w3casc.py) reads the CASC storage through the unchanged [tools/wowf/casc.py](../../tools/wowf/casc.py). Warcraft III's root file is plain text, one `path|content key|tags` line per file; 105,285 of its 175,345 entries are present locally.
2. **Maps.** [tools/wc3/mpq.py](../../tools/wc3/mpq.py) is a small read-only MPQ reader for the `.w3m`/`.w3x` maps: it handles the encrypted hash and block tables, sectored and encrypted files, and zlib and bzip2 compression. It read 466 of the 486 maps. Each map carries its string table in 13 more locales, so localized campaign text is available even with only English installed.
3. **Extraction.** [tools/wc3/extract_text.py](../../tools/wc3/extract_text.py) writes every text file, map string table, map script and lip-sync name list to the gitignored `.wc3-extract/` folder: 479 text files (28.3 MB), 1,964 FaceFX name lists and 10,973 map members, in about 7 seconds.
4. **Mining.** [tools/wc3/mine.py](../../tools/wc3/mine.py) parses the unit subtitles (`Strings/Dialogue*Base.fdf`), the map string tables with their speakers and sound files (from each map's `conversation.json`), the cinematic captions and all other text. It flags a token when it is neither an English word nor a hyphenated compound of English words, and it is a lexicon form, contains an elvish root, is spoken by an elf, is joined by an apostrophe or hyphen, or scores high on a character-trigram model trained on Blizzard's elvish forms. It takes about 45 seconds: 4,272,386 text records, 41,956 with a flagged token, and 1,950 distinct flagged tokens, most of them names or English. It also lists the voice files named for an elf, an elven unit or a naga (`audio.tsv`).
5. **Hand review.** Each flagged line was checked against the lexicon and the wiki: the [Thalassian](https://warcraft.wiki.gg/wiki/Thalassian#Untranslated_words_or_phrases), [Darnassian](https://warcraft.wiki.gg/wiki/Darnassian#Untranslated_phrases) and [Nazja](https://warcraft.wiki.gg/wiki/Nazja#Phrases) pages, and the [Night Elf](https://warcraft.wiki.gg/wiki/Quotes_of_Warcraft_III/Night_Elf_Sentinels), [Human](https://warcraft.wiki.gg/wiki/Quotes_of_Warcraft_III/Human_Alliance), [Neutral](https://warcraft.wiki.gg/wiki/Quotes_of_Warcraft_III/Neutral#Naga_Siren) and [Neutral Heroes](https://warcraft.wiki.gg/wiki/Quotes_of_Warcraft_III/Neutral_Heroes#Naga_Sea_Witch) quote lists, fetched raw on 2026-11-18. A unit line matches a wiki line when both point to the same voice file: the game's sound table (`UI/SoundInfo/Dialogue*Base.slk`) maps each subtitle key to its file, and the wiki names the file next to each quote. That holds for 21 of the 22 unit lines; the Blood Mage's *Ish-shera-do* matches by text and speaker. The three naga unit lines are on the two Neutral lists. The Nazja page has only *Athero bath'rilas* of them, and it lists *Osh'bala-tharei* for the Naga Siren, probably the same line heard differently, since it is the Siren's only line that is not English (inferred).
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
| Campaign voice files named for an elf, an elven unit or a naga (all campaigns) | 905 (56.4 MB), not counting the HD and DE copies |
| Unit voice files named the same way | 679 (17.7 MB), not counting the HD and DE copies |
| New-campaign voice files | 1,233 (72.5 MB) |

The voice counts go by the name in the file name, so Sylvanas, the banshees, the dryads and Cenarius are in them, and the human priests are not. The three place names on the wiki that also appear in the game, *Izal-Shurah*, *Arauk-nashal* (in a Reforged Maiev line) and *Quel'Danas*, have no gloss and are left out of the counts.

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
| (b) wiki | Shan'do | Maiev Shadowsong (14), Druid of the Claw (3), Druid of the Talon (1), Dryad (1), Runner (1), no speaker (1) | `Reforged/ROC/NightElf03.w3x STRING 186, and 20 more strings` | Shan'do | **honored teacher**: wiki primer, and zhTW 尊師 in all 21 strings (attested, confirmed) |
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
| (b) wiki | Ash-thero-sauguine! Ba'anthalso-dorei! | Naga (myrmidon) | `Reforged/TFT/NightElfX02.w3x STRING 122` | Ash-thero-sauguine! / Ash'thero sanguine! | unglossed |
| (b) wiki | Ash-thero-sauguine! Ba'anthalso-dorei! | Naga (myrmidon) | `Reforged/TFT/NightElfX02.w3x STRING 122` | Ba'anthalso-dorei! | unglossed |
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

1. The new campaign's 20 maps are encrypted, so its dialogue, subtitles and in-mission text are not covered. Its hero subtitles, items, campaign and mission names, closing captions, two scenario maps and the list of its voice files are.
2. No speech was transcribed. The unit lines have Blizzard subtitles, but the two Sentinel lines in the orc mission Orc04 (`O04FemaleNEA04.ogg` and `O04FemaleNEB05.ogg`) have none. The wiki writes the Sentinels' lines in that mission by ear as *Anu dunah thalore. Iseradune banthalos* and *Ash'therod nethanas*.
3. The game's spellings are Blizzard's own, but nobody has checked them against the voice yet. The wiki's spellings are by ear. Where the two differ, the voice files would show which is closer.
4. Only English text is installed. The maps carry 13 more locales, but the unit subtitles and items exist only in English locally. The Japanese and Thai campaign string tables are about a seventh the size of the English ones (14% and 13% in all) and hold none of the elvish campaign strings.
5. A single build cannot show which lines are new in 3.0. The gear items are 3.0 content by their names (Garek's and Anya's backpacks belong to the new campaign's heroes); the rest is older.

## What would add more

1. **Chinese unit subtitles.** The zhTW and zhCN versions of the unit subtitle and item files are in the storage's index but not downloaded. Their localizers translated *thero-shan* and *Shan'do*, so they may have translated some of the 21 unglossed unit lines too. Cost: adding zhTW and zhCN text in the Battle.net app downloads about 60 MB of non-speech files per locale (about 540 MB each with speech). After that, `extract_text.py --locales enUS,zhTW,zhCN` reads them in seconds.
2. **Transcribing the new campaign.** The 1,233 new-campaign voice files (72.5 MB) are the only way to its dialogue. Report 5 paid $2.59 for 588 files on fal.ai, so all 1,233 would cost about $5.40, and only Sylvanas and the three elven-looking names (101 files) about $0.44. That is under the $20 limit but still paid, so it waits for a yes. A free local option, whisper.cpp, would need a download first. `ffmpeg` is installed; no speech-to-text tool is.
3. **Transcribing the two Orc04 Sentinel lines** (119 KB) and the 23 elvish unit lines. That would settle their spellings against the voice. It costs a few cents on the same service.
4. **The new campaign's text** would need the decrypted maps. This pass does not try that.

## Applied

[scripts/apply_wc3_midnight.py](scripts/apply_wc3_midnight.py) applied the high- and medium-confidence candidates after the audit ([merge log](merge-log.md#warcraft-iii-game-files-9-candidatesjson)). One was corrected first, on 2026-11-19: the Ukrainian gloss of *shan'do* is "шановний вчитель", spelled as in the gloss of *do*, "вчитель". Both translators read each word of a two-word gloss as a translation, so "учитель", which *do* lacks, had turned into the title.

## Reproduce

From the repo root. The first command takes about 8 seconds. The second takes about 45 seconds, writes `.wc3-extract/analysis/` (`records.tsv` is 443 MB) and prints the voice-file counts. Save the raw [Thalassian](https://warcraft.wiki.gg/index.php?title=Thalassian&action=raw) and [Darnassian](https://warcraft.wiki.gg/index.php?title=Darnassian&action=raw) pages as `Thalassian.txt` and `Darnassian.txt` first; the miner stops if a file it is given is missing.

```
python3 tools/wc3/extract_text.py --install "/Applications/Warcraft III" --out .wc3-extract
```

```
python3 -I tools/wc3/mine.py --base .wc3-extract --lexicon src/thalassian/data/lexicon.json --wowf .wowf-extract --wiki Thalassian.txt Darnassian.txt
```

```
python3 -I research/2026-11-revival/scripts/wc3_candidates.py .
```

The script takes the fixes' old values from lexicon.json, so it rebuilds 9-candidates.json byte for byte only on the lexicon that apply_audit.py leaves (416 entries). Run the recipe in the docstring of [merge_candidates.py](scripts/merge_candidates.py) up to apply_audit.py first, and apply_wc3_midnight.py after.

The tests for the readers, parsers and miner need no game files:

```
python3 -m unittest tests.test_tools.test_wc3
```

The extract is Blizzard data and stays out of git; this report and the candidates file quote only single lines.
