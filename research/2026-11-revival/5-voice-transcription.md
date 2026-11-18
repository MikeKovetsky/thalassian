# Skyborne voice transcription

Run on 2026-11-18 over the 196 Skyborne voice files extracted from the WoW Forever client (1.60.1.70938), using four speech-to-text listeners on fal.ai. The spend cap was $3, and the run spent $1.61.

## Findings

1. **Most Skyborne voice lines are English.** Of 196 files, 12 hold an elvish formula and 8 more say an elvish name inside an English line. The rest are English, such as /hello "Gale's greetings, friend" and /bye "May the winds guide you", apart from seven wordless sounds (sighs, laughs, rasps and a sob).
2. **The letter's farewell is spoken.** Two Skyborne NPC voice sets say *aeesha'el banu zephrali* as a farewell. This is the closing line of the druid trainer's letter, *Aeesha'el banu zepharaalis* (`MailTemplate` 652), with *zephrali* "of Zephras" as the last word. Report 3 knew the phrase only from that letter.
3. **All four elvish formulas contain *banu*:**
   - *banu alah* is the female /hello, and two NPC voice sets use it as a greeting.
   - *banu adora* is a greeting of both NPC voice sets.
   - *aradash ... banu* is a greeting of both NPC voice sets; its middle word is unresolved.
   - *aeesha'el banu zephrali* is the farewell above.
4. ***banu* names what the blessing invokes: the winds, or their blessing.** It stands where *Elune* stands in Darnassian *Elune-adore* "Elune be with you", and where *ishnu* "good fortune" stands in *Ishnu-alah* "good fortune to you". Almost every English blessing of the same voices invokes the winds; the only NPC blessings below that do not are "May you always land with grace" and "The Skysight will guide you". (Of all 49 English NPC greetings and farewells, 25 mention the wind; most of the rest are shop lines and plain hellos and goodbyes.) For example, one NPC voice set greets with both *banu alah* and, probably, "Favorable winds to you, friend" (Wizper alone heard it, as "wins"). Medium confidence.
5. **Three names are now heard, not just read:**
   - *shen'dorei* is "shen-dor-eye", ending in "eye", in the /charge "For the Shen'dorei!". Where the stress falls is unclear.
   - *Zephras* has two syllables, "ZEF-ras", in 14 of its 20 readings; the rest give *Zephyrus* or *Zephyros*.
   - *Shen'dar* is in "Shen'dar will not fall".

Applied to the lexicon (314 entries, up from 310) by [scripts/apply_voice.py](scripts/apply_voice.py):
- **4 new entries:** *banu*, *banu alah*, *banu adora* and *aeesha'el banu zephrali*.
- **6 notes updated:** *aeesha'el banu zepharaalis*, *zephrali*, *shen'dorei*, *shen'dar*, *zephras* and *adore*.
- **3 held back as low confidence:** *aeesha'el* alone, *aradash*, and a note on *anu*.

Every candidate, with the readings behind it, is in [5-candidates.json](5-candidates.json): four for each voice line, except "Favorable wins to you, friend", which Wizper alone heard.

## Method

**Source.** The source is 196 Ogg files (6.5 minutes) in the local, gitignored `.wowf-extract/skyborne_vo/`:
- Every player emote line for both sexes.
- All 30 greetings and 29 farewells of the two Skyborne NPC voice sets (folders 7478487 and 7478494, played through `NPCSounds` 3764, 3773 to 3776 and 3820).

The client lists 392 more Skyborne voice files that were not extracted. Most are combat sounds: attack 57, alert 43, critical attack 41, wound 36, wind-up 27, death 21 and aggro 11.

**Listeners.** The four listeners come from three model families: OpenAI's Whisper, ElevenLabs and Google's Gemini. Two Gemini models count as one family.
- Wizper (fal's Whisper v3).
- ElevenLabs Scribe v2.
- Gemini 3.1 Pro and Gemini 3.8 Flash, through fal's audio router.

The Gemini models got a blind prompt (in [scripts/transcribe.py](scripts/transcribe.py)). It asks for English text, IPA and a plain romanization, and it does not say what the line is for or which words to expect. No lexicon words were given to any listener.

**Order.**
1. Three listeners (Wizper, Scribe v2 and Gemini 3.1 Pro) heard the 10 lines that report 3 listed as most worth hearing. All 10 turned out to be English. Gemini 3.8 Flash's 10 requests were rejected, because they turned reasoning off, which the router refuses, and they were not repeated.
2. Wizper, the cheapest listener, heard the other 186 lines.
3. The other three listeners heard 22 lines: the 20 where Wizper's reading was not English or had an elvish name, the line it heard as "The sky site will guide you" (it is "The Skysight will guide you"), and the one line where Wizper had timed out, which turned out to be English ("For the Windshapers!").

**Readings.** A form is accepted when listeners from at least two families agree on it. Where the letter, an item name or a Darnassian phrase already writes the word, its spelling is kept, even against the listeners' vowels (see the spelling choices below). Meanings come only from the slot that plays the line (the emote, or the NPC's greeting or farewell list) and from the English lines in the same slot. They never come from the listeners.

## Elvish lines

The columns give each listener's reading, verbatim. The Gemini columns give the romanization; where a line mixes English and elvish, it is joined to the English words in the order spoken.

| FileDataID | Slot | Wizper | Scribe v2 | Gemini 3.1 Pro | Gemini 3.8 Flash | Reading |
|---|---|---|---|---|---|---|
| 7744899 | /hello (female) | Banu Allah. | Banu Allah | banu ala | banu ala | *banu alah* |
| 7744493 | /hello (male) | Anu Allah. | Benu Allah | anu ala | anu ala | *banu alah*? (b unclear) |
| 7744800 | NPC greetings (set 7478487) | Banu Allah. | Banu Allah | banu ala | banu ala | *banu alah* |
| 7745203 | NPC greetings (set 7478494) | Banu Allah | [outro jingle] | banu ala | banu alah | *banu alah* |
| 7744796 | NPC greetings (set 7478487) | Banu Adora. | Banu Adora | banu adora | Banu Adorha | *banu adora* |
| 8268710 | NPC greetings (set 7478494) | Banu Adora. | バヌー・アドラ | banu adura | banu adora | *banu adora* |
| 7744878 | NPC greetings (set 7478494) | Banu Adara. | Banu Adhara | panu adara | banu adora | *banu adora* (or adara) |
| 7745197 | NPC greetings (set 7478494) | The new Ardura. | The new Adura | The new adura | The new adura | unresolved; perhaps *banu adora* |
| 7744799 | NPC greetings (set 7478487) | Aradash Ishtalah Banu | Aradash i Talha Banu | aradash ith tala banu | aradash ith dala banu | *aradash ? banu* |
| 7745202 | NPC greetings (set 7478494) | Aradash Estalav Banu. | Aradas Efdala Banu | aradash eftala banu | Ara ash estala banu | *aradash ? banu* |
| 7744790 | NPC farewell (set 7478487) | I share Banu Zafrali. | Ayesha Banu Zafraly | ai shei el banu, zefrali | ai sheyel banu zafrali | *aeesha'el banu zephrali* |
| 7745188 | NPC farewell (set 7478494) | Harshael Bono Zafrali | Hi, I'm Shael Bonu Zephrali. | a sheal banu zafra li | ha'she'al bonu zefrali | *aeesha'el banu zephrali* (three heard *bono* or *bonu*) |

**Spelling choices:**
- *alah* follows *Ishnu-alah*; the listeners heard *Allah* (Wizper and Scribe), *ala* or *alah*.
- *banu* follows the letter and the other farewell file. In file 7745188, three of four listeners, one from each family, heard *bono* or *bonu*, so the two-family rule alone would give *bonu* there.
- *adora* is spelled as heard, not as Darnassian *adore*. Across the three clear files it was heard as *adora* 8 times out of 12, *adara* 3 times and *adura* once.
- *aeesha'el* follows the letter's spelling; it sounds like "ai-SHAY-el".
- *zephrali* follows the item names ("Zephrali Chainmail"), although five of its eight readings begin with *zaf-*. The voice has no final *-s*, unlike the letter's *zepharaalis*.

## Names in English lines

| FileDataID | Slot | Wizper | Scribe v2 | Gemini 3.1 Pro | Gemini 3.8 Flash | Reading |
|---|---|---|---|---|---|---|
| 7744476 | /charge (male) | For the Shendorai! | For the Shen Dorai | For the shen'dorai | For the shen'dorai | For the Shen'dorei! |
| 7744883 | /charge (female) | For the Shindorai! | For the Shindo Rai | For the shindurai | For the sin'dorei | For the Shen'dorei! |
| 8268889 | NPC greetings (set 7478494) | Shendar will not fall. | Shendar will not fall | shindal will not fall | shandal will not fall | Shen'dar will not fall. |
| 7744477 | /cheer (male) | For the glory of Zephrys Isle! | For the glory of Zephrys Isle! | For the glory of Zephrys Isle! | For the glory of Zephrys Isle! | For the glory of Zephras Isle! |
| 7744884 | /cheer (female) | For the glory of Zephyr's Isle! | For the glory of Zephrys Isle | For the glory of Zephyrus Isle! | For the glory of Zephyros Isle! | For the glory of Zephras Isle! |
| 7744798 | NPC greetings (set 7478487) | Zephyrus will not fall. | Zephrys will not fall | Zephyrus will not fall | Zephrys will not fall. | Zephras will not fall. |
| 7745200 | NPC greetings (set 7478494) | Zephrys will not fall. | Zephyrus will not fall | Zafres will not fall. | Zafras will not fall. | Zephras will not fall. |
| 7744874 | NPC farewell (set 7478494) | Zephrys will endure. | Zephrys will endure | Zephyrus will endure. | Zephrus will endure | Zephras will endure. |

## The English formulas in the same slots

These lines show what the elvish formulas sit beside. They are Wizper's readings. Most were heard by Wizper alone; the 10 lines report 3 shortlisted were also heard by Scribe v2 and Gemini 3.1 Pro, and the "Skysight" line by the other three listeners. Three slips are corrected: "wins" for "winds" twice (heard by Wizper alone, so the correction is a guess), and "sky site" for "Skysight", which the other three listeners heard as "sky sight" or "Skysight".

1. **/hello:** "Hello."; "Land with grace."; "Gale's greetings, friend."
2. **/bye:** "Goodbye."; "Until we meet again."; "May the winds guide you."
3. **/welcome:** "Welcome, friends."; "Winds welcome you."
4. **/thank:** "Thank you."; "Much appreciated."; "I won't forget this kindness."
5. **/cheer:** "Fair winds prevail!"; the female line was heard as "Their wins will prevail", probably "Fair winds will prevail".
6. **NPC greetings:**
   - "Favorable winds to you, friend."
   - "Sure winds and clear skies to you."
   - "The Windshapers welcome you."
   - "What has the wind brought?"
   - "What have the winds brought me today?"
   - "Gale's greetings, friend."
   - Shop lines such as "Sky-high quality at rock-bottom prices."
7. **NPC farewells:**
   - "Run with the winds."
   - "May the winds guide your path."
   - "May the winds bless you."
   - "Blessing of the winds upon you."
   - "Beware the still winds."
   - "There's an ill wind about. Take care."
   - "May you always land with grace."
   - "The Skysight will guide you."
   - "The Windshapers do not forget."
   - "Until we meet again."

## Limits

1. **No person has listened to these files.** Machine listeners map unfamiliar speech onto real words: Wizper heard "I share" and "Harshael", and Scribe heard "Hi, I'm Shael", all for *aeesha'el*. That is why a form needs two families to agree.
2. **The Gemini models' own notes are unreliable.** Some said "no audio file was provided" or that they worked "from the provided text", although their readings match the other listeners'. Gemini 3.8 Flash wrote the lore word *sin'dorei* for a line the other three heard as *Shindorai*, so a model that knows Warcraft can hear what it expects. Gemini 3.1 Pro heard "Gale's greetings" once as "Chaos greetings".
3. **Vowels and stress are the weakest part** (*adora*, *adara* or *adura*). Consonant skeletons agree far better.
4. **Some forms stay unresolved:**
   - The middle word of the *aradash ... banu* greeting. One file was heard as *ishtalah*, *i talha*, *ith tala* and *ith dala*; the other as *estalav*, *efdala*, *eftala* and *estala*.
   - File 7745197, which three listeners heard as "The new Adura" and Wizper as "The new Ardura".
   - The male /hello, which three of four listeners heard as *anu ala*.

## Spend

Totals from the run's ledger (local, in `.wowf-extract/transcripts/ledger.jsonl`):

| Listener | Calls completed | Cost (USD) | How the cost is known |
|---|---|---|---|
| Wizper | 196 | 0.57 | $0.00111 a second, times wall time including upload: an upper bound (fal's Wizper page listed $0 a compute second when checked on 2026-11-18); one timeout is logged at its $0.006 estimate |
| ElevenLabs Scribe v2 | 32 | 0.26 | fal's listed $0.008 a minute, counted as a whole minute per call: an upper bound |
| Gemini 3.1 Pro | 32 | 0.74 | The router's reported cost per call, $0.008 to $0.049 depending on how long the model reasoned |
| Gemini 3.8 Flash | 22 | 0.04 | The router's reported cost per call |
| **Total** | 282 | **1.61** | Cap $3.00 |

Sixteen more requests were rejected (HTTP 422, which fal does not bill) or failed locally before reaching fal, and are logged at $0. The total is not independently confirmed: the API key cannot read fal's billing page, so the figure rests on the router's reports and on fal's listed prices.

## Next steps

1. **A person listening to the 12 elvish files** (24 seconds of audio, in `.wowf-extract/skyborne_vo/`) would settle the vowels, the *aradash* middle word and file 7745197.
2. **The 392 unextracted files.**
   - The 11 aggro lines and the alert lines are the likeliest to hold more battle cries.
   - `tools/wowf/run_all.sh` can extract them on the Mac mini.
   - Wizper would transcribe them for about $1 at this run's rate.
3. **A Skyborne play session on the Mac mini** would cache the Zephras Isle quest text. That text is served by Blizzard's servers, so the client files on disk don't have it.
