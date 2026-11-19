# 10. Elvish in Midnight's server-side text, from the wiki

Date: 2026-11-18. Input: [warcraft.wiki.gg](https://warcraft.wiki.gg/wiki/World_of_Warcraft:_Midnight), read through its public API, for every page of patches 11.2.5 to 12.1.7. Output: [10-candidates.json](10-candidates.json), 14 candidates: 10 fixes, 2 additions and 2 notes (table at the end). Script: [midnight_wiki.py](scripts/midnight_wiki.py).

## Top findings

1. **Midnight adds no new glossed elvish.** In 18,075 wiki pages with Midnight text, the only line where a character explains elvish in English is still Vereesa Windrunner's "Selama ashal'anore, Blood Knight. Justice for our people." ([A Favor for Kinduru](https://warcraft.wiki.gg/wiki/A_Favor_for_Kinduru#Notes), 12.0.7). [Report 4](4-localization-mining.md) already added it.
2. **No elvish phrase in Midnight text is new to both the lexicon and the wiki.** Of the 14 elvish phrases on Midnight pages, 11 are in the lexicon, 3 are on the wiki's language pages only, and none is new to both.
3. **The known greetings get new uses.** *Anu belore dela'na* is a toast for Lord Saltheril and a parting wish for Lor'themar Theron. *Al diel shala* and *Shorel'aran* close Aethas Sunreaver's weekly quests. *Sinu a'manore* and *Shorel'aran* are Magister Astalor Bloodsworn's on-click greeting and farewell. *Anar'anel belore* is a cheer at good news. Each one fits its gloss, and the candidates add them as evidence.
4. **Two phrases stay untranslated:** *Quel'falan danas!*, the last line of the Silversun Compact (12.0.1), and *Anu bala belore'alon*, the last line of [The World Awaits](https://warcraft.wiki.gg/wiki/The_World_Awaits_(Midnight)#Completion) (12.0.1). No character, quest text or item explains either one.
5. **Two item names carry English epithets that are not translations:** *Alah'endal, the Dawnsong* (an axe) and *Belo'melorn, the Shattered Talon* (a dagger). The client's own item table confirms both names. The wiki's readings "Lightbreath" and "Sunstrike" are editors' guesses. The world boss *Lu'ashal*, a dragonhawk grown huge on Holy energy, is a second Midnight name where *lu-* goes with the Light.
6. **One line is scrambler output.** Knight Anais's "[Thalassian] Ishnu alah terro shar..." ([Bury Me Not](https://warcraft.wiki.gg/wiki/Bury_Me_Not#Notes), 12.0.1) is what non-speakers see for "Until even stars fade...". [Report 1](1-review-and-methods.md) found this first. The wiki's primer still lists it as an official translation.

## Method

1. **Enumerate.** The script collected every page the wiki ties to patches 11.2.5 to 12.1.7, one request a second, with a generic User-Agent, 50 titles per request. It used five sources:
   1. the "Added in patch X" categories;
   2. pages that use a `{{Patch X}}` template of the range;
   3. pages that use the wiki's Midnight markers `{{Mn-section}}` and `{{Mn-inline}}` (`{{Expac|Midnight}}` uses the latter);
   4. a walk four levels down from 48 Midnight zone, faction and storyline categories;
   5. CirrusSearch `insource:` queries for Midnight level templates.
2. **Fetch.** It read the raw wikitext of every page, the pages of the speakers the corpus quotes (for their race), and the wiki's Thalassian, Darnassian and Shalassian pages.
3. **Find the Midnight text.** A line counts as Midnight text if it sits in a section the wiki marks as Midnight, or if the page was added in the range and the line has no other era marker. Quoted speech comes from `{{Text|say|Speaker|...}}`, `{{Dialogue}}` and quote templates, and quest text from the Description, Progress, Completion and Notes sections.
4. **Find elvish.** A phrase is a run of words with an elvish apostrophe (not a contraction or possessive), or lexicon and language-page words that are not English. In speech, any word that is not in the macOS word list also counts.
5. **Read.** The script's 20,913 Midnight records were reviewed by hand: the 198 phrases that are not names, every line with a gloss cue ("means", "in Thalassian", "translate"), every line with a language tag, and the non-English words of elven speakers.
6. **Cross-check** with a second source (see below), and write the candidates.

## Enumeration, and how complete it is

| Source | Pages | Pages no earlier source found |
|---|---:|---:|
| "Added in patch" categories, 11.2.5 to 12.1.7 | 17,130 | 17,130 |
| `{{Patch X}}` templates of the range | 22,335 | 5,217 |
| `{{Mn-inline}}` and `{{Mn-section}}` | 21,706 | 3,949 |
| Walk of 363 Midnight categories | 8,557 | 313 |
| `insource:` searches for Midnight levels | 2,849 | 90 |
| **Total** | | **26,699** |

1. All 26,699 pages were fetched, with the speaker pages: 27,384 pages in all. Of those, 18,075 have Midnight text (216,088 lines or fields).
2. **First check: the wiki's own lists.** The wiki's [Thalassian page](https://warcraft.wiki.gg/wiki/Thalassian#Proper_nouns) lists 13 proper nouns that occur in Midnight text. It also cites six Midnight pages for its phrases: Bury Me Not, Lu'selama and What Might Come in the primer, and Sunfire to the Blade, The World Awaits and the Silversun Compact among the untranslated ones. The script found all of them.
3. **Second check: a search of the whole wiki.** The `check` step searched the whole wiki for 195 elvish forms: every lexicon form of four or more letters, and the wiki's untranslated phrases. That gave 14,826 page hits. For the 170 rarer forms (60 hits or fewer), it fetched all 547 hit pages outside the set. Only 3 of them carry a Midnight marker:
   1. [Skyborne](https://warcraft.wiki.gg/wiki/Skyborne) and [Zephras Isle](https://warcraft.wiki.gg/wiki/Zephras_Isle) are WoW Forever pages that mention a Midnight housing dye.
   2. The other is the [Thalassian page](https://warcraft.wiki.gg/wiki/Thalassian) itself.

   So the enumeration missed no Midnight page that uses a rarer known form. The 25 common forms (Quel'Thalas, kaldorei, sin'dorei and the like) were not checked this way.
4. **What it cannot see.** Text that the wiki does not transcribe is out of reach. Many NPCs' on-click and gossip lines are missing from the wiki. For example, the wiki says *Anu bala belore alon* is "a click quote by blood elf civilians in Midnight", but no NPC page among the 27,384 quotes it. The wiki's only Midnight source for it is The World Awaits.

## Counts

1. **Script level.** On Midnight lines the script found 1,112 distinct phrases of the apostrophe or lexicon tier:
   1. 914 are names only (places, NPCs, items).
   2. The other 198 sort into 23 in the lexicon, 10 on the wiki's language pages, and 165 in neither.
   3. Reading the 165 showed none is elvish. They are troll (*hash'ura*, *hash'ey*, *Tokobo'ne na Amani'Zar*), Haranir, ethereal, draenei and Shath'Yar words, plus wiki file names and typos.
2. **After reading: 14 elvish phrases on Midnight lines.**
   1. (a) In the lexicon: 11.
   2. (b) On the wiki's language pages, not in the lexicon: 3.
   3. (c) New to both: 0.
3. **With an in-game English meaning: 5.**
   1. One is a spoken gloss: Vereesa's *Selama ashal'anore*, already in the lexicon.
   2. Four are item or mount names with an English epithet: *Lu'selama, Light's Justice* and *Anu'shalla, Shadow's Guidance* (both in the lexicon), and *Alah'endal, the Dawnsong* and *Belo'melorn, the Shattered Talon* (new to the lexicon). Only the first two read as translations.
   3. Every other phrase gets its function from context only: a greeting, a farewell, a toast or a cheer.
4. **Scrambler output: 1 line.** See the scrambler check below.

## Findings: elvish phrases in Midnight text

| Phrase | Class | Where (patch) | Speaker | Context | English pairing |
|---|---|---|---|---|---|
| Selama ashal'anore | a | [A Favor for Kinduru](https://warcraft.wiki.gg/wiki/A_Favor_for_Kinduru#Notes) (12.0.7) | Vereesa Windrunner | "...Blood Knight. Justice for our people." | Yes, the speaker glosses it |
| Anu belore dela'na | a | [Fortify the Runestones: Magisters](https://warcraft.wiki.gg/wiki/Fortify_the_Runestones:_Magisters#Notes) and [Shades of the Row](https://warcraft.wiki.gg/wiki/Fortify_the_Runestones:_Shades_of_the_Row#Notes) (12.0.1) | Lord Saltheril | Ends a toast, "A toast to the Magisters..." | No |
| Anu belore dela'na | a | [No Fear of the Dark](https://warcraft.wiki.gg/wiki/No_Fear_of_the_Dark#Notes), [Fractured](https://warcraft.wiki.gg/wiki/Fractured#Completion) (12.0.1) | Lor'themar Theron | Before a mission; "I hope you find him soon. Anu belore dela'na, <Name>." | No |
| Anu belore dela'na; Al diel shala | a | [Lord Saltheril](https://warcraft.wiki.gg/wiki/Lord_Saltheril#On-click) (12.0.1 on-clicks) | Lord Saltheril | On-click greeting; on-click farewell | No (the English on-click lines beside them are separate voice lines) |
| Al diel shala | a | [An Original Path Through Time](https://warcraft.wiki.gg/wiki/An_Original_Path_Through_Time_(Midnight)#Completion) (12.0.7) | Aethas Sunreaver | "Al diel shala, <name>." closes the quest | No |
| Bal'a dash, malanore | a | [Enchanted Naga Scroll](https://warcraft.wiki.gg/wiki/Enchanted_Naga_Scroll_(quest)#Notes) (12.0.5), [Bloodguard Nelric](https://warcraft.wiki.gg/wiki/Bloodguard_Nelric#Quotes), [Paved in Ash](https://warcraft.wiki.gg/wiki/Paved_in_Ash_(Horde)#Notes) (12.0.1) | Aethas; Nelric; Magistrix Nizara | Opens gossip; Aethas adds "Welcome to Silvermoon." | Context only |
| Sinu a'manore | a | [The World Awaits](https://warcraft.wiki.gg/wiki/The_World_Awaits_(Midnight)#Description) (12.0.1), [Magister Astalor Bloodsworn](https://warcraft.wiki.gg/wiki/Magister_Astalor_Bloodsworn#On-click) | Aethas; Astalor | Opens a quest; on-click greeting | No |
| Shorel'aran | a | [Emissary of War](https://warcraft.wiki.gg/wiki/Emissary_of_War_(Midnight)#Description) (12.0.1), [Magister Astalor Bloodsworn](https://warcraft.wiki.gg/wiki/Magister_Astalor_Bloodsworn#On-click) | Aethas; Astalor | Last word of a quest; on-click farewell | No |
| Anar'anel belore | a | [Sunfire to the Blade](https://warcraft.wiki.gg/wiki/Sunfire_to_the_Blade#Completion) (12.0.1) | Knight-Lord Sunguard | "Anar'anel belore! You love to hear it." | Context only (a cheer) |
| Anar'alah belore | a | [Ever Painting](https://warcraft.wiki.gg/wiki/Ever_Painting) (12.0.0) | (none) | Title of a painter's easel in Eversong | No |
| Shal'na | a | [What Might Come](https://warcraft.wiki.gg/wiki/What_Might_Come#Notes) (11.2.7) | Arator | "Shal'na! Come back to us." | Already handled (aunt) |
| Three sung fragments of the Lament of the Highborne (two phrases, plus part of *selama ashal'anore*) | a | [Repent of the Highborne](https://warcraft.wiki.gg/wiki/Repent_of_the_Highborne) (11.2.7) | Sylvanas Windrunner | Sung in a cinematic | Not quoted here, because they are song lyrics. All are in the lexicon. |
| Anu bala belore'alon | b | [The World Awaits](https://warcraft.wiki.gg/wiki/The_World_Awaits_(Midnight)#Completion) (12.0.1) | Aethas Sunreaver | "Your efforts are known and appreciated. Anu bala belore'alon." | No, already handled |
| Quel'falan danas | b | [The Silversun Compact (object)](https://warcraft.wiki.gg/wiki/The_Silversun_Compact_(object)#Content) (12.0.1) | Signed by Vereesa and Aethas | "In memory of Theramore, Dalaran, and the Sunwell. Quel'falan danas!" | No |
| Ishnu alah terro shar | b | [Bury Me Not](https://warcraft.wiki.gg/wiki/Bury_Me_Not#Notes) (12.0.1) | Knight Anais | Scrambler output for "Until even stars fade..." | Not elvish |

## Names in Midnight text

None of these has a spoken gloss. They are listed for completeness.

1. **Names with an English epithet.**
   1. [Alah'endal, the Dawnsong](https://warcraft.wiki.gg/wiki/Alah%27endal,_the_Dawnsong#Speculation) (item 249296, 12.0.1) is new to the lexicon. Its parts read *alah* "light" (inferred) and *endal* "breath" (segment). The wiki's "Lightbreath" is marked as speculation.
   2. [Belo'melorn, the Shattered Talon](https://warcraft.wiki.gg/wiki/Belo%27melorn,_the_Shattered_Talon#Trivia) (item 249283, 12.0.1) is new to the lexicon. In beta it was Belo'ren's Mystic Talon, so *belo-* probably comes from the phoenix [Belo'ren, Child of Al'ar](https://warcraft.wiki.gg/wiki/Belo%27ren,_Child_of_Al%27ar). The wiki's "Sunstrike" is an editor's guess.
   3. *Lu'selama, Light's Justice* (12.1.5) and *Anu'shalla, Shadow's Guidance* (12.0.0) are already in the lexicon. The client's Mount table describes Anu'shalla's wings as cutting the sky "like shadows on a moonlit night", which fits *shalla* "shadow".
2. **Names on the wiki's list but not in the lexicon:** Ath'Ran and Lash'Ra (Lightbloom areas), Shan'dor and Falithas (runestones), Scintilas Falls, Shan'dorah, Belanise, Sinara, Sintalia, and Sin'gria (the wiki says it is a pun on sangria).
3. **Names in neither:**
   1. [Lu'ashal](https://warcraft.wiki.gg/wiki/Lu%27ashal#Adventure_Guide) is a world boss in Eversong, a dragonhawk the Adventure Guide says grew huge "from the surging Holy energy". That fits *lu* "light".
   2. The rest have no gloss: the arcane golems Construct V'anore, E'nui and Ali'a; the food Kale'thas Sunsalad; the NPC Fel'orei Moonstrider; the Kal'delar armor set.
4. **Out of scope.** The Haranir villages carry English epithets, such as *Har'mara, Village of Balance*, but Haranir is not elvish. The troll (Zandali), draenei and Shath'Yar lines were skipped.

## Untranslated: nobody explains these

1. *Quel'falan danas!* ends the [Silversun Compact](https://warcraft.wiki.gg/wiki/The_Silversun_Compact_(object)#Content), a pact for mages to work together against world-ending threats, signed by Vereesa Windrunner and Aethas Sunreaver. Only *quel* "high" is known. Candidate: a low-confidence note.
2. *Anu bala belore'alon* is Aethas's sign-off in The World Awaits. It was already handled, and the wiki adds nothing new.
3. *Anar'anel belore* has no gloss either. The lexicon's "For the sun!" is inferred, and Knight-Lord Sunguard's cheer fits it.
4. Item names *Alah'endal* and *Belo'melorn* have epithets but no literal translation.

## Scrambler check

1. Only one Midnight line has every word in the scrambler list: Knight Anais's "[Thalassian] Ishnu alah terro shar..." in [Bury Me Not](https://warcraft.wiki.gg/wiki/Bury_Me_Not#Notes).
2. All four words are in the Thalassian scrambler list (language 10, 102 words). The Darnassian (2) and Shen'dorei (310) lists are the same.
3. The same page also has the understood line, "[Thalassian] Until even stars fade...". Its word lengths, 5-4-5-4, match the scrambled words one for one.
4. The wiki's [Thalassian primer](https://warcraft.wiki.gg/wiki/Thalassian#Thalassian_primer_(official_translations)) still lists "Ishnu alah terro shar = Until even stars fade" as an official translation. Report 1 already flagged this.
5. The script flagged 16 more Midnight records as all-scrambler. All were false positives: names and single words such as Ash'an, Aman, *alah* and *belore*. The scrambler borrows real words, so a real word can be on the list.

## Cross-checks

1. **Confirmed in the client's own tables** (wago.tools, build 12.1.7.70986, looked up by ID or name):
   1. [ItemSparse 249296](https://wago.tools/db2/ItemSparse?filter%5BID%5D=exact%3A249296): Alah'endal, the Dawnsong.
   2. [ItemSparse 249283](https://wago.tools/db2/ItemSparse?filter%5BID%5D=exact%3A249283): Belo'melorn, the Shattered Talon.
   3. [ItemSparse 280799](https://wago.tools/db2/ItemSparse?filter%5BID%5D=exact%3A280799): Lu'selama, Light's Justice.
   4. [Mount 2917](https://wago.tools/db2/Mount?filter%5BID%5D=exact%3A2917): Anu'shalla, Shadow's Guidance.
   5. [JournalEncounter 2827](https://wago.tools/db2/JournalEncounter?filter%5BName_lang%5D=Lu%27ashal): Lu'ashal.
   6. [JournalEncounter 2739](https://wago.tools/db2/JournalEncounter?filter%5BName_lang%5D=Belo%27ren): Belo'ren, Child of Al'ar.
2. **Not independently confirmed: the spoken and quest lines.** They are server-side text. The 12.1.7 client's BroadcastText holds 10,888 rows: the local zhCN, zhTW and koKR copies, and wago.tools for enUS. None of these lines is among them, and the koKR rows have no Hangul spelling of them either. Each greeting does appear on two or more wiki pages (an NPC page and a quest page), but those are separate edits to the same source. Vereesa's line is the exception: report 4 confirmed it through BroadcastText 309952.

## Limits

1. The wiki is fan-transcribed. Spellings drift (Sind'orei, Hal'hader), and lines go missing.
2. English is detected with the macOS word list plus a stemmer. The hand review of non-English words from elven speakers found no elvish word that the apostrophe and lexicon tiers had missed.
3. Speaker race comes from the speaker's Npcbox. Quest text has no speaker field, so the quest giver was read from the Questbox by hand.
4. On a page that already existed before Midnight, a line counts only inside a section the wiki marks as Midnight. Saltheril's on-click list has no such marker, so it was found by reading, using the page's 12.0.1 patch note.
5. Song lyrics, and the long texts of books and pacts, are named and linked, not copied.

## Candidates ([10-candidates.json](10-candidates.json))

| Action | Word | Confidence | What |
|---|---|---|---|
| fix evidence | anu belore dela'na | high | Five Midnight uses |
| fix notes | anu belore dela'na | medium | Also a toast and a parting wish |
| fix evidence | al diel shala | high | Two Midnight farewells |
| fix evidence | bal'a dash, malanore | high | Three Midnight gossip openers |
| fix evidence | sinu a'manore | high | Astalor's on-click greeting |
| fix evidence | shorel'aran | high | Aethas's sign-off and Astalor's farewell |
| fix evidence | anar'anel belore | medium | Knight-Lord Sunguard's cheer |
| fix evidence | lu | medium | Lu'ashal, the Light-infused world boss |
| fix evidence | lu'selama | high | ItemSparse 280799 |
| fix evidence | anu'shalla | medium | Mount 2917, name and description |
| add | alah'endal | medium | "the Dawnsong", an epithet |
| add | belo'melorn | medium | "the Shattered Talon", an epithet |
| note | quel'falan danas | low | Untranslated |
| note | belo'ren | low | A phoenix's name; the "sun + void" reading is a guess |

Every `old` value was copied from the current lexicon.json.

## Reproduce

From the repo root, with any cache folder outside the repo (about 30,000 requests at one a second for the first run; the cache makes later runs local):

```
python3 research/2026-11-revival/scripts/midnight_wiki.py enumerate CACHE
python3 research/2026-11-revival/scripts/midnight_wiki.py fetch CACHE
python3 research/2026-11-revival/scripts/midnight_wiki.py speakers CACHE
python3 research/2026-11-revival/scripts/midnight_wiki.py extract CACHE . CACHE/hits.json
python3 research/2026-11-revival/scripts/midnight_wiki.py check CACHE .
```
