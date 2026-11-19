# Forsaken Kingdom voice transcription (Warcraft III 3.0)

Run on 2026-11-18 over all 1,233 voice files of Forsaken Kingdom, the new campaign of Warcraft III: Reforged 3.0 (build 3.0.1.24371). The campaign's maps are encrypted (see [report 9](9-warcraft-iii.md)), so its voice files are the only way into its dialogue. Speech-to-text listeners on fal.ai heard them under a hard cap of $5.40; the run cost $5.05.

## Findings

1. **The new campaign has no elvish words.** All 1,233 files are English. Wizper (Whisper v3) heard every file and detected English in all of them. A second model family, Gemini 3.8 Flash, heard 116 of them: the 103 files of Sylvanas and the four speakers whose names look elven, and every other file that names Ilastar, Quel'Thalas, Windrunner or the Sunwell. It answered for 105 and found English in every one. The five answers it marked "mixed" are English lines with a name in them: *Quel'Thalas* once, *Ilastar* three times and *Anya* once. No line holds an elvish formula, not even Sylvanas's 45 lines. In the original campaign, by contrast, she says *Anar'alah belore* and *Bash'a no falor talah*.
2. **Two elvish names are spoken.** Both listener families heard them.
   - *Quel'Thalas*, already in the lexicon ("High Home"), comes up twice. Anya says "And for the fall of Quel'Thalas!", and Ilastar says "Quel'Thalas has fallen, and the Sunwell is gone." Gemini hears it as kwel-THA-las; Wizper writes it without stress.
   - *Ilastar*, the speaker's name, which looks elven (see finding 3), is said in 10 files. Ilastar says it twice ("Ilastar Songbreeze, at your service" and "I am Ilastar Songbreeze, and you gave me the greatest gift of all: my demise"), and Garek says it in eight files. Blizzard writes it *Ilastar*: it is the proper name of the Cleric hero and of its undead form, the Shadow Priest (`Units/CampaignUnitStrings.txt:143` and `:151`), and of the item *Ilastar's Backpack* (`Units/ItemStrings.txt:2688`). Gemini's IPA puts the stress on the first syllable in all 10 readings and has [ˈɪlɪstɑːɹ], [ˈɪlɪstɑɹ] or [ˈɪləstɑːɹ] in 9: IL-i-star, with a weak middle vowel. Wizper wrote Illistar, Ilyastar, Illustar, Ilyasdar, Ylastar and Illestan. It is a personal name with no gloss, new to the lexicon and the wiki pages. The surname, Songbreeze, is English, and no readable game text has it.
3. **Anya is an elf, a dark ranger of Quel'Thalas, by her own words.** Ilastar is very probably one too. The table below has what each speaker says.
4. **The two Sentinel lines of mission Orc04 now have machine readings.** Report 9 left them untranscribed. Gemini and Scribe v2 agree on roughly *anaduna ?alore isera duna ban?os* and *ash-te-rod ne-fanas*. The wiki writes them by ear as *Anu dunah thalore. Iseradune banthalos* and *Ash'therod nethanas*. Where the wiki has *th* (*thalore*, *nethanas*), every listener heard *f* or *v*. Wizper turned the first line into English ("I'm going to make a flower ...") and heard no words in the second. WoW's Darnassian scrambler list has five words close to these lines, two of them spelled as the wiki spells them (see "Older elvish lines").
5. **The classic voice of the 23 elvish unit lines decides some of report 9's spelling conflicts.** For 15 lines, the game's subtitles and the wiki's by-ear spellings differ. Of those 15, the voice sides with the wiki in 6, including Maiev's *Ashal thera'das*, which Blizzard spells *Al'shar Thoridas*, and Malfurion's *Ash'thero danador*, which Blizzard spells *Ash'thera'falla-dor*. It sides with Blizzard in 4, including the Demon Hunter's *Anu'dor anu'dor*, which the wiki has as *Anato retetour*. Two lines are mixed, two are told apart only by spelling, and one ending is unresolved. Blizzard spells the Warden's *Morothoray katal* the way it sounds: both listeners heard "moro thore katal". The table is under "Older elvish lines".

### What the English says about the speakers

| Speaker (files) | What the lines say | Elf? |
|---|---|---|
| Sylvanas (45) | Others call her Lady Sylvanas Windrunner and the Dark Lady. All of her lines are English. | Yes, already known. |
| Anya (221) | "In life, I served under Sylvanas. We both died defending our kingdom against the Scourge." Of Kel'Thuzad: "he slaughtered my people and defiled the Sunwell." She calls the Dark Rangers "my sisters". Ilastar calls her "Dark Ranger", and she answers "My future is with the Forsaken". | **Yes.** She is a dark ranger, an undead elf of Quel'Thalas, in her own words, though she never uses the word "elf" of herself. The game's unit strings, outside the maps, also name her hero unit Dark Ranger (`Units/CampaignUnitStrings.txt:1430`). |
| Ilastar (52) | "Ilastar Songbreeze, at your service." In the prologue, Ilastar heals the party and calls on the Light, then is infected by plague spores in Stratholme ("We're infected!"). Ilastar returns "remade in undeath" as a servant of the Lich King. To Anya: "Quel'Thalas has fallen, and the Sunwell is gone. The Scourge are our future now." | **Probably.** "Our future" ties Ilastar to Anya's people, but no line says "elf". |
| Kaelystia (2) | An undead just freed from the Scourge: "You will burn in the fires of my magic!" Kaelystia then accepts Anya's call to join the Forsaken. | Not stated. |
| Melisara (2) | Speaks at a camp in the same mission (A1M3) in which Anya says "There's a Dark Ranger camp ahead." | Not stated; possibly a dark ranger. |
| Lorthiras (2) | "This is not the end, little mortals." The line comes right after civilians describe "a demon, wings and horns and cloven feet". | Very probably a dreadlord, not an elf: report 9 found *Lorthiras* among the game's stock Dreadlord names (`Units/UndeadUnitStrings.txt:57`). |

No line says the names Kaelystia, Melisara or Lorthiras aloud, so how they sound is unknown. Varimathras, Putress, Kel'Thuzad and the rest are not elves. Four banshee lines are English, and they do not say who the banshees were in life.

## Counts

| | Count |
|---|---|
| New-campaign files heard | 1,233 of 1,233 (113.0 minutes) |
| Elvish words or phrases in them | 0 |
| Elvish names in them | 2: *Quel'Thalas* (a: in the lexicon) and *Ilastar* (c: new to both; a personal name, unglossed) |
| Older elvish lines heard (report 9's list) | 25 (44 seconds): (a) 2, (b) 22, (c) 1 |
| New meanings | 0. The game pairs none of these lines with English. |

The classes are (a) already in the lexicon, (b) on the wiki but not in the lexicon, and (c) new to both. "The wiki" here is its [Thalassian](https://warcraft.wiki.gg/wiki/Thalassian) and [Darnassian](https://warcraft.wiki.gg/wiki/Darnassian#Untranslated_phrases) pages and, for the older lines, the [Nazja](https://warcraft.wiki.gg/wiki/Nazja#Phrases) page and the Warcraft III quote lists that report 9 used; Naisha's line and the three naga lines are only on those. The raw pages were fetched on 2026-11-18. The older lines' classes follow report 9. Sunwell, Windrunner and Songbreeze are English names, so they are not counted.

Proposals are in [11-candidates.json](11-candidates.json). There are two notes on lexicon entries: how *Quel'Thalas* is said in 3.0, and the voice check of *Tor ilisar'thera'nal*. There are also three low-confidence entries, held back by the merge policy: *Morothoray katal* and the two Orc04 Sentinel lines, with their readings. *Morothoray katal* is also a low-confidence note in [9-candidates.json](9-candidates.json); the entry here repeats that note's subtitle evidence and adds the voice, so a merge would combine the two. The other 20 older lines are already in 9-candidates.json, and their readings are below. *Anu'dorini talah* gets no new note, because report 9 already fixes the same field. *Ilastar* gets no entry: it is a personal name with no gloss, and report 9 also left unglossed names out.

## Older elvish lines

Report 9 lists these lines. The voice files are the classic (SD) recordings under `War3.w3mod:_Locales/enUS.w3mod:Units/`, plus the two Orc04 files under `Sound/Dialogue/OrcCampaign/Orc04/`. They were extracted read-only to the local `.wc3-extract/extra_vo/`. The listener columns are verbatim; Gemini's column is its romanization, or its English text for Lady Vashj's war cry, where it gave no romanization. "Voice" says which written spelling the two families' shared reading is closer to.

| Line | Blizzard | Wiki (by ear) | Wizper | Gemini 3.8 Flash | Voice |
|---|---|---|---|---|---|
| Malfurion war cry | Ana'doreini talah! | Anu'dorini Talah | Anodorini Talar. | ano durini tala | wiki and lexicon (*-dorini*); first word heard *ano* |
| Maiev war cry | Tor ilisar'thera'nal! | same | Tor Ilyasar Tharanol! | tor ilis ar theran al | as written |
| Blood Mage | Andu fallah. | same | Andou Fala. | andu fala | as written |
| Blood Mage | Aseph-ah-balla nah. | same | a Seth Abalanar. | a'setha bala'naa | both heard *th* for *ph* (see Limits) |
| Blood Mage | Ish-shera-do. | Ishera-do. | You share a dough. | isharado | both fit |
| Kael'thas | Endo-enah Quel'Thalas! | same | And Oanna, quoth Elas, | Endo'ana Quel'thalas | as written; second word heard *-ana* |
| Spell Breaker | Inde'rinah-dor Highborne! | Endirina-dor Highborne! | Enderina Dorhaiborn! | en deri na dor hyborn | mixed: *En-* as the wiki, *-de-* as Blizzard |
| Tyrande | Anu'dora! | same | Anu Dora! | anu'dora | as written |
| Tyrande | Enu ri'fah! | Hinduli rathal! | In duly reffered. | enduli rafad | mixed: *enduli* as the wiki, *f* as Blizzard |
| Tyrande | Ashe'tor'aman. | Ashre thoraman. | Ashithoraman. | ashrathoraman | wiki (*thoraman*) |
| Tyrande | Anu'therador mali | Anu therador mali. | Anu Therador Mali. | anu'therador mali | both fit |
| Malfurion | Tor fal-anu'dora! | Tor falah-no dorah! | Torfala Nordora. | tor'fala no'dora | wiki (*-no-*) |
| Malfurion | Ash'thera'falla-dor. | Ash'thero danador. | Ashtarudana, though. | ashtero ganador | wiki: neither heard *falla* |
| Maiev | Al'shar Thoridas! | Ashal thera'das! | Ashal Tharadas. | a'shal theradas | wiki (*ashal*) |
| Warden | Ash'valanor | Ashbalanol. | Ashfa Lanong. | ash fala no | Blizzard (*f* or *v*, not *b*); no final *r* or *l* heard (Wizper *-nong*, Gemini *-no*) |
| Warden | Benthai del Elune | Bathel'daelune. | Bentha Delelune. | pentha delilun | Blizzard |
| Warden | Morothoray katal | none | Moro thore katal. | moro thore katal | as written |
| Demon Hunter | Dorune'ka | Deronica. | Doranek. | doranai kaal | Blizzard (*dor-n-k*) |
| Demon Hunter | Anu'dor anu'dor. | Anato retetour! | Anadur, Anadur. | ana'dor ana'dor | Blizzard |
| Naisha | Ara'deno'filorei! | Ara'denu thelore! | Arradanil thilore! | Aradanil thilore | wiki (*th*; see Limits) |
| Naga Siren | Ash'valana thure. | same | Ashwala Mathare. | ash'valavathare | as written; last word heard *thare* |
| Lady Vashj | Era'sazjar! | same | Verassajah! | berasaja | as written, but both heard a *b* or *v* first and no final *r* |
| Lady Vashj | Athero bathre'las! | Athero bath'rilas! | Zero butthole-ness! | A sparrow bothers us! | *athero bath-* (Scribe v2: "Athero bathrinus"); the ending is unresolved |
| Sentinel, Orc04 | (no subtitle) | Anu dunah thalore. Iseradune banthalos | I'm going to make a flower. And you're going to make a bunch. | ana duna valore isera duna bandolos | Scribe v2: "Anaduna farore i sera duna banthros"; *f* or *v* for the wiki's *th* |
| Sentinel, Orc04 | (no subtitle) | Ash'therod nethanas | - | esh te rod ne fanas | Scribe v2: "Asteroth Nefanas"; *f* for the wiki's *th* |

Report 9 found that Blizzard's *al'shar* is a word in WoW's language-scrambler lists. The voice says *ashal* there, so the scrambler's word follows the subtitle's spelling, not the sound. The wiki's Darnassian scrambler list (its [In-game parser](https://warcraft.wiki.gg/wiki/Darnassian#In-game_parser) section) also has words of the two Orc04 lines, which have no subtitle:
- *Ash'therod* and *Banthalos*, spelled as the wiki spells them in the lines;
- *Isera'duna*, close to the wiki's *Iseradune*; the two families heard *isera duna* and *i sera duna*;
- *Anoduna*, close to the wiki's *Anu dunah*;
- *Neph'anis*, close to *nethanas* as both families heard it (*ne fanas*, *Nefanas*), with *ph* where they heard *f*.

If the scrambler drew on Warcraft III here too, these would be Blizzard's own spellings of those words. The wiki's by-ear spellings may instead have borrowed from the list. Neither is confirmed.

## Method

**Source.** The 1,233 Ogg files of the campaign were extracted read-only to the gitignored `.wc3-extract/forsaken_vo/`. The prologue has 330 under `Sound/Dialogue/HumanRECamp/`, and the main campaign has 903 under `.../UndeadRECamp/`. They run 113.0 minutes in all: 5.5 seconds on average, and 16.9 seconds at most (durations by ffmpeg). The speaker is the last part of each file name. The 25 older lines were extracted from the same local storage by [tools/wc3/w3casc.py](../../tools/wc3/w3casc.py), with no download.

**Listeners.** The listeners came from three model families, through [scripts/transcribe.py](scripts/transcribe.py), unchanged from report 5:
- Wizper (fal's Whisper v3);
- Gemini 3.8 Flash, through fal's audio router, with the script's blind prompt, which asks for English text, IPA and a romanization and never says what a line is or which words to expect;
- ElevenLabs Scribe v2.

No lexicon word was given to any listener.

**Order.**
1. Wizper heard the files in priority order:
   1. Sylvanas and the four speakers whose names look elven (Ilastar, Lorthiras, Kaelystia, Melisara), 103 files. Report 9 had found that Lorthiras is a stock Dreadlord name; its 2 files were heard here anyway.
   2. Anya, 221 files.
   3. Everyone else, 909 files. Speakers with fewer files came first and Garek's 367 came last, with the files of scenes that elves share first within each speaker.

   The first 20 calls cost $0.060, which projected $3.72 for all 1,233. Four parallel processes then made each call slower, and Wizper's cost is wall time, so their 114 calls averaged $0.0055 against $0.0037 one at a time. They were stopped between calls, and the rest ran one at a time. A stop at $5.22 was set to keep room for the second-family checks. Wizper never reached it: its 1,233 files cost $4.73. Four calls failed (two timeouts and two HTTP 500s at upload) and were heard on retry.
2. Every Wizper reading was scanned, and the 221 Anya readings were also read in full. The scan looked for:
   - a language other than English;
   - words outside the system dictionary;
   - inner apostrophes;
   - elvish terms (*quel*, *thalas*, *dorei*, *belore*, *elf* and others) and lexicon forms;
   - lines with few words for their length.

   Apart from English words and names that are not elven, such as Kel'Thuzad, Naxxramas and Stratholme, the only hits were names tied to the elves, in 16 files: Ilastar (10 files), Quel'Thalas (2), Windrunner (3) and the Sunwell (2; one file has both Quel'Thalas and the Sunwell).
3. Gemini 3.8 Flash heard 116 new-campaign files:
   - all 16 files that name Ilastar, Quel'Thalas, Windrunner or the Sunwell;
   - the other 100 files of the five elf-looking speakers.

   It answered for 105, all English except for names (see finding 1). Gemini's safety filter blocked 7 Sylvanas lines (HTTP 422, not billed), and 4 answers came back empty. So 92 of the 103 elf-speaker files have a second-family reading.
4. Report 9's 23 unit lines and the 2 Orc04 Sentinel lines were heard by Wizper and Gemini 3.8 Flash. Scribe v2 heard three lines: the two Orc04 lines, which have no subtitle and where Wizper gave English for one and nothing for the other, and Lady Vashj's war cry, where Wizper and Gemini both gave English.

**Readings.** As in report 5, a form counts when two families agree on it. Where Blizzard writes the word, its spelling is kept. A meaning comes only from what the game pairs with the elvish, and nothing here is paired with English. The race of each speaker comes from what the lines themselves say, checked against the game's unit strings where they name the speaker.

## Spend

Totals from the run's ledger (local, in `.wc3-extract/forsaken_vo_transcripts/ledger.jsonl`):

| Listener | Calls | Cost (USD) | How the cost is known |
|---|---|---|---|
| Wizper, new campaign | 1,237 (1,233 completed, 4 failed and retried) | 4.73 | $0.00111 a second of wall time, upload included: an upper bound. The 4 failures are logged at their $0.006 estimate. |
| Gemini 3.8 Flash, new campaign | 116 (105 answers, 7 blocked, 4 empty) | 0.18 | The router's reported cost per call. It reported $0 for the 4 empty answers and for 4 of the 105 answers; the 7 blocked calls (HTTP 422) are logged at $0. |
| Wizper, older lines | 25 | 0.06 | As above |
| Gemini 3.8 Flash, older lines | 25 | 0.06 | As above |
| Scribe v2, older lines | 3 | 0.02 | fal's listed $0.008 a minute, counted as a whole minute per call: an upper bound |
| **Total** | 1,406 | **5.05** | Cap $5.40, so $0.35 was left |

The total is not independently confirmed: the API key cannot read fal's billing page, so the figure rests on the router's reports, including the 8 calls it reported at $0, and on fal's listed prices.

## Limits

1. **No person has listened.** Every reading rests on the machines.
2. **For 1,128 of the 1,233 files, Wizper is the only listener.** Wizper can turn elvish into English: Vashj's war cry became "Zero butthole-ness!" and the first Orc04 line "I'm going to make a flower". So a short elvish phrase in a minor speaker's line could hide behind an odd English reading. The scan in step 2 and the full read of Anya's lines found none. The second family answered for 92 of the 103 files of Sylvanas and the four elf-looking speakers. Anya's 221 files rest on Wizper alone, apart from 4.
3. **The listeners confuse *f* and *th*, and *v* and *b*.** The open points are *Aseph* (heard *seth*), *filorei* (heard *thilore*), and the wiki's *thalore* and *nethanas* (heard with *f* or *v*). A person should settle these four points.
4. **Gemini knows Warcraft.** It wrote *Naxxramas* where Wizper heard "Nox Romus", and *Kaelastar* once for Ilastar. Where it agrees with a lore spelling, it is a weaker second family than Scribe. The Orc04 lines have Scribe's reading too.
5. **Only the classic recordings of the older lines were heard,** not the Reforged re-recordings in `_HD.w3mod`.
6. **The speakers' names come from the file names.** The game's unit strings, outside the maps, confirm two of them: Anya is the Dark Ranger hero, and Ilastar the Cleric and, undead, the Shadow Priest (`Units/CampaignUnitStrings.txt`). The encrypted maps would give the subtitles and the other speakers' units, and this pass did not try to open them.

## Next steps

1. **A person listening to the four *f*/*th* points and to Ilastar's name** would settle them. The four points are 13 seconds of audio in `.wc3-extract/extra_vo/`. The 10 files that say Ilastar's name are in `.wc3-extract/forsaken_vo/`.
2. **The Reforged (HD) recordings of the 23 unit lines** would show whether the new voice actors say them as the classic ones do. Two listeners would cost about $0.12 on the same service.
