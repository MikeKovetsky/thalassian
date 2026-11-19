# 10. Elvish in Midnight's server-side text, from the wiki

Date: 2026-11-18. Input: [warcraft.wiki.gg](https://warcraft.wiki.gg/wiki/World_of_Warcraft:_Midnight), read through its public API, for every page of patches 11.2.5 to 12.1.7. Output: [10-candidates.json](10-candidates.json), 17 candidates: 12 fixes, 3 additions and 2 notes (table at the end). Script: [midnight_wiki.py](scripts/midnight_wiki.py).

## Top findings

1. **In Midnight text, three characters explain an elvish word in English, and only one of them translates it.**
   1. Vereesa Windrunner's "Selama ashal'anore, Blood Knight. Justice for our people." ([A Favor for Kinduru](https://warcraft.wiki.gg/wiki/A_Favor_for_Kinduru#Notes), 12.0.7) is the only translation. [Report 4](4-localization-mining.md) already added it.
   2. Lorewalker Cho says what *sin'dorei* names and why: "The blood elves, or sin'dorei, will never forget that loss." and "The blood elves took their name in remembrance of their fallen kin" ([Lorewalking: Children of the Blood](https://warcraft.wiki.gg/wiki/Lorewalking:_Children_of_the_Blood#Description), 11.2.7).
   3. First Arcanist Thalyssra says what the nightborne word *Arcan'dor* names: "a mana tree we call the Arcan'dor" ([In Times of Need](https://warcraft.wiki.gg/wiki/In_Times_of_Need#Notes), 12.0.1). It is not in the lexicon, and the candidates add it.
2. **No elvish phrase or word in Midnight text is new to both the lexicon and the wiki.** Of the 15 on Midnight lines, 12 are in the lexicon, 3 are on the wiki's language pages only, and none is new to both.
3. **Known phrases get new uses.**
   1. *Anu belore dela'na* is a toast for Lord Saltheril and a parting wish for Lor'themar Theron.
   2. *Al diel shala* and *Shorel'aran* close Aethas Sunreaver's weekly quests, and *Sinu a'manore* and *Shorel'aran* are Magister Astalor Bloodsworn's on-click greeting and farewell.
   3. The wiki's biography of Lady Liadrin says Lor'themar bids her farewell with a final *shorel'aran* when she dies (12.1.5).
   4. *Anar'anel belore* is a cheer at good news.
   5. *Minn'da* "mother" names the 11.2.7 chapter in which Arator looks for his mother, Alleria Windrunner.

   Each one fits its gloss, and the candidates add them as evidence.
4. **Two phrases stay untranslated:** *Quel'falan danas!*, the last line of the Silversun Compact (12.0.1), and *Anu bala belore'alon*, the last line of [The World Awaits](https://warcraft.wiki.gg/wiki/The_World_Awaits_(Midnight)#Completion) (12.0.1). No character, quest text or item explains either one.
5. **Two item names carry English epithets that are not translations:** *Alah'endal, the Dawnsong* (an axe) and *Belo'melorn, the Shattered Talon* (a dagger). The client's own item table confirms both names. The wiki's readings "Lightbreath" and "Sunstrike" are editors' guesses. The world boss *Lu'ashal*, a dragonhawk grown huge on Holy energy, is a second Midnight name where *lu-* goes with the Light.
6. **One line is scrambler output.** Knight Anais's "[Thalassian] Ishnu alah terro shar..." ([Bury Me Not](https://warcraft.wiki.gg/wiki/Bury_Me_Not#Notes), 12.0.1) is what non-speakers see for "Until even stars fade...". [Report 1](1-review-and-methods.md) found this first. The wiki's primer still lists it as an official translation.

## Method

1. **Enumerate.** The script collected every page the wiki ties to patches 11.2.5 to 12.1.7, one request a second, with a generic User-Agent. It used five sources:
   1. the "Added in patch X" categories;
   2. pages that use a `{{Patch X}}` template of the range;
   3. pages that use the wiki's Midnight markers `{{Mn-section}}` and `{{Mn-inline}}` (`{{Expac|Midnight}}` uses the latter);
   4. a walk four levels down from 48 Midnight zone, faction and storyline categories;
   5. CirrusSearch `insource:` queries for Midnight level templates.
2. **Fetch.** It read the raw wikitext of every page, 50 titles per request, the pages of the speakers the corpus quotes (for their race), and the wiki's Thalassian, Darnassian and Shalassian pages. A page that the API leaves out of a full batch is asked for again.
3. **Find the Midnight text.** A line counts as Midnight text in two cases.
   1. The wiki marks the line, or the part of the page it sits in, as Midnight (`{{Mn-section}}`, `{{Mn-inline}}` or `{{Expac|Midnight}}`). A section marker covers its section up to the next marker, heading or `;` sub-heading. Markers that come before any text of a section cover its sub-sections too. An inline marker covers only its own line, and the innermost marker wins.
   2. The line has no era marker, and its page was added in the range, or its page is filed under a Midnight category or level and has no patch note older than 11.2.5.

   Text that the wiki marks as removed from the beta, alpha or PTR, and text under a Beta, Alpha or PTR heading, never counts, because it was not released. Of the fetched pages, 228 say so in their lead (`{{Removedfrombeta}}` and the like), and 710 lines sit in a section marked that way (`{{Rfb-section}}` and the like) or under such a heading. Quoted speech comes from `{{Text|say|Speaker|...}}`, `{{Dialogue}}` and quote templates, and quest text from the Description, Progress, Completion and Notes sections.
4. **Find elvish.** A phrase is a run of words with an elvish apostrophe (not a contraction or possessive), or lexicon and language-page words that are not English. In speech, any word that is not in the macOS word list also counts.
5. **Read.** The script's 20,974 Midnight records were reviewed by hand. The review covered the 197 phrases that are not names, the non-English words of elven speakers, every line with a language tag, and every in-game line where an elvish word sits next to a gloss cue ("means", "in Thalassian", "translate", "we call", "known as", or an aside such as "the blood elves, or sin'dorei") or next to a word of its lexicon gloss.
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

1. All 26,699 pages were fetched, with the speaker pages: 27,384 pages in all. Of those, 18,236 have Midnight text (214,091 lines or fields, headings included).
2. **First check: the wiki's own lists.** The wiki's [Thalassian page](https://warcraft.wiki.gg/wiki/Thalassian#Proper_nouns) lists 35 proper nouns. 24 of them occur on Midnight lines, and none of the 35 is a lexicon entry. The page also cites six Midnight pages for its phrases: Bury Me Not, Lu'selama and What Might Come in the primer, and Sunfire to the Blade, The World Awaits and the Silversun Compact among the untranslated ones. The script found all of them.
3. **Second check: a search of the whole wiki.** The `check` step searched the whole wiki for 195 elvish forms: every lexicon form of four or more letters, and the wiki's untranslated phrases. That gave 14,826 page hits. For the 170 rarer forms (60 hits or fewer), it fetched and read all 547 hit pages outside the set. Only 3 of them carry a Midnight marker:
   1. [Skyborne](https://warcraft.wiki.gg/wiki/Skyborne) and [Zephras Isle](https://warcraft.wiki.gg/wiki/Zephras_Isle) are WoW Forever pages that mention a Midnight housing dye.
   2. The other is the [Thalassian page](https://warcraft.wiki.gg/wiki/Thalassian) itself.

   So the enumeration missed no Midnight page that uses a rarer known form. The 25 common forms (Quel'Thalas, kaldorei, sin'dorei and the like) were not checked this way.
4. **What it cannot see.** Text that the wiki does not transcribe is out of reach. Many NPCs' on-click and gossip lines are missing from the wiki. For example, the wiki says *Anu bala belore alon* is "a click quote by blood elf civilians in Midnight", but no NPC page among the 27,384 quotes it. The wiki's only Midnight source for it is The World Awaits.

## Counts

1. **Script level.** On Midnight lines the script found 1,101 distinct phrases of the apostrophe or lexicon tier. The script writes the lists below to the `review` part of its output.
   1. 904 are names only (places, NPCs, items).
   2. The other 197 sort into 23 in the lexicon, 10 on the wiki's language pages only, and 164 in neither.
   3. The 23 in the lexicon are 12 elvish phrases and words, 5 race names (*sin'dorei*, *quel'dorei*, *kaldorei*, *ren'dorei*, *shal'dorei*), 3 single words that wiki notes quote (*alah*, *endal*, *belore*), the fragment *Quel* of a split "Quel 'Danas", and 2 false matches. The false matches are the English "Gah!", which matches the generated word *gah* "ice", and the Silver Hand's old motto, "Esarus thar no'Darador—By Blood and Honor We Serve". The motto comes with its English, but it is older lore (the page cites *Of Blood and Honor*) quoted on a page filed under a Midnight category, and the lexicon already has it.
   4. The 10 on the wiki only are 2 elvish words or phrases (*Quel'falan danas*, *Arcan'dor*), the scrambler line *Ishnu alah terro shar*, 2 plant and drink names from the wiki's proper-noun list (*Belanise*, *Sintalia*), 3 race and language names (*fal'dorei*, *san'layn*, Darnassian), and 2 fragments of names split by a stray space ("Zul' Aman", "Dath 'Remar").
   5. Reading the 164 found one elvish phrase that the script's exact match missed: *Anu bala belore'alon*, which the wiki's Thalassian page spells without the apostrophe. The rest hold no new elvish:
      1. troll (*hash'ura*, *hash'ey*, *Tokobo'ne na Amani'Zar*), Haranir, ethereal, draenei, tauren and Shath'Yar words and names;
      2. spellings and pieces of known elvish: *Arc'andor* (an in-game spelling of Arcan'dor), *ashal'anore*, *selama'* and *elu'meniel* (parts of lexicon phrases), and race names with endings or typos (*non-sin'dorei*, *sin'dorel*, *fal'dorie*);
      3. Legion names that came back with Legion Remix in 11.2.5 (*Elun'eth*, *Ly'elth*, *Del'thanar*);
      4. wiki file names and run-together link text (*Quel'DanasIsle*), English contractions (*s'posed*, *won'tcha*), and typos (*Dan'khan* for Dar'Khan, *Shand'orah* for Shan'dorah).
2. **After reading: 15 elvish phrases and words on Midnight lines.** Race names and the scrambler line are counted apart.
   1. (a) In the lexicon: 12.
   2. (b) On the wiki's language pages, not in the lexicon: 3 (*Anu bala belore'alon*, *Quel'falan danas* and *Arcan'dor*).
   3. (c) New to both: 0.
3. **Words and names with an in-game English meaning: 7.**
   1. One is a spoken translation: Vereesa's *Selama ashal'anore*, already in the lexicon.
   2. Two are spoken explanations of what a word names: Cho's *sin'dorei* "the blood elves" and Thalyssra's *Arcan'dor* "a mana tree".
   3. Four are item or mount names with an English epithet: *Lu'selama, Light's Justice* and *Anu'shalla, Shadow's Guidance* (both in the lexicon), and *Alah'endal, the Dawnsong* and *Belo'melorn, the Shattered Talon* (new to the lexicon). Only the first two read as translations.
   4. Every other phrase gets its function from context only: a greeting, a farewell, a toast, a cheer or a chapter name.
4. **Scrambler output: 1 line.** See the scrambler check below.

## Findings: elvish in Midnight text

| Phrase | Class | Where (patch) | Speaker | Context | English pairing |
|---|---|---|---|---|---|
| Selama ashal'anore | a | [A Favor for Kinduru](https://warcraft.wiki.gg/wiki/A_Favor_for_Kinduru#Notes) (12.0.7) | Vereesa Windrunner | "...Blood Knight. Justice for our people." | Yes, the speaker glosses it |
| Sin'dorei (a race name) | a | [Lorewalking: Children of the Blood](https://warcraft.wiki.gg/wiki/Lorewalking:_Children_of_the_Blood#Description) (11.2.7) | Lorewalker Cho | "The blood elves, or sin'dorei, will never forget that loss."; "The blood elves took their name in remembrance of their fallen kin" | Yes, what it names and why, not a translation |
| Arcan'dor | b | [In Times of Need](https://warcraft.wiki.gg/wiki/In_Times_of_Need#Notes) (12.0.1) | First Arcanist Thalyssra | "...a mana tree we call the Arcan'dor."; "The fruit of the Arcan'dor can cleanse all manner of magic." | Yes, what it names, not a translation |
| Anu belore dela'na | a | [Fortify the Runestones: Magisters](https://warcraft.wiki.gg/wiki/Fortify_the_Runestones:_Magisters#Notes) and [Shades of the Row](https://warcraft.wiki.gg/wiki/Fortify_the_Runestones:_Shades_of_the_Row#Notes) (12.0.1) | Lord Saltheril | Ends a toast, "A toast to the Magisters..." | No |
| Anu belore dela'na | a | [No Fear of the Dark](https://warcraft.wiki.gg/wiki/No_Fear_of_the_Dark#Notes), [Fractured](https://warcraft.wiki.gg/wiki/Fractured#Completion) (12.0.1) | Lor'themar Theron | Before a mission; "I hope you find him soon. Anu belore dela'na, <Name>." | No |
| Anu belore dela'na; Al diel shala | a | [Lord Saltheril](https://warcraft.wiki.gg/wiki/Lord_Saltheril#On-click) (12.0.1 on-clicks) | Lord Saltheril | On-click greeting; on-click farewell | No (the English on-click lines beside them are separate voice lines) |
| Al diel shala | a | [An Original Path Through Time](https://warcraft.wiki.gg/wiki/An_Original_Path_Through_Time_(Midnight)#Completion) (12.0.7) | Aethas Sunreaver | "Al diel shala, <name>." closes the quest | No |
| Bal'a dash, malanore | a | [Enchanted Naga Scroll](https://warcraft.wiki.gg/wiki/Enchanted_Naga_Scroll_(quest)#Notes) (12.0.5), [Paved in Ash](https://warcraft.wiki.gg/wiki/Paved_in_Ash_(Horde)#Notes) (12.0.1) | Aethas; Magistrix Nizara | Opens gossip; Aethas adds "Welcome to Silvermoon." | Context only |
| Sinu a'manore | a | [The World Awaits](https://warcraft.wiki.gg/wiki/The_World_Awaits_(Midnight)#Description) (12.0.1), [Magister Astalor Bloodsworn](https://warcraft.wiki.gg/wiki/Magister_Astalor_Bloodsworn#On-click) | Aethas; Astalor | Opens a quest; on-click greeting | No |
| Shorel'aran | a | [Emissary of War](https://warcraft.wiki.gg/wiki/Emissary_of_War_(Midnight)#Description) (12.0.1), [Magister Astalor Bloodsworn](https://warcraft.wiki.gg/wiki/Magister_Astalor_Bloodsworn#On-click) | Aethas; Astalor | Last word of a quest; on-click farewell | No |
| Shorel'aran | a | [Lady Liadrin](https://warcraft.wiki.gg/wiki/Lady_Liadrin#The_Promise_of_Tomorrow) (12.1.5), the wiki's biography | Lor'themar Theron | The biography says Lor'themar "bid farewell to his old friend with a final *shorel'aran*". The quest pages do not transcribe the line. | Context only (a farewell at her death) |
| Anar'anel belore | a | [Sunfire to the Blade](https://warcraft.wiki.gg/wiki/Sunfire_to_the_Blade#Completion) (12.0.1) | Knight-Lord Sunguard | "Anar'anel belore! You love to hear it." | Context only (a cheer) |
| Anar'alah belore | a | [Ever Painting](https://warcraft.wiki.gg/wiki/Ever_Painting) (12.0.0) | (none) | Title of a painter's easel in Eversong | No |
| Minn'da | a | [Visions of a Shadowed Sun](https://warcraft.wiki.gg/wiki/Visions_of_a_Shadowed_Sun#A_Meeting_with_Minn%27da) (11.2.7) | (none) | The chapter "A Meeting with Minn'da", in which Arator looks for his mother, Alleria ([Lore Book](https://warcraft.wiki.gg/wiki/Lore_Book_(The_War_Within)#A_Meeting_with_Minn%27da)) | Context only (fits "mother") |
| Shal'na | a | [What Might Come](https://warcraft.wiki.gg/wiki/What_Might_Come#Notes) (11.2.7) | Arator | "Shal'na! Come back to us." | Already handled (aunt) |
| Three sung fragments of the Lament of the Highborne (*Vendel'o eranu*, *Elu'meniel mal alann*, and part of *selama ashal'anore*) | a | [Repent of the Highborne](https://warcraft.wiki.gg/wiki/Repent_of_the_Highborne) (11.2.7) | Sylvanas Windrunner | Sung in a cinematic | Not quoted here, because they are song lyrics. All are in the lexicon. |
| Anu bala belore'alon | b | [The World Awaits](https://warcraft.wiki.gg/wiki/The_World_Awaits_(Midnight)#Completion) (12.0.1) | Aethas Sunreaver | "Your efforts are known and appreciated. Anu bala belore'alon." | No, already handled |
| Quel'falan danas | b | [The Silversun Compact (object)](https://warcraft.wiki.gg/wiki/The_Silversun_Compact_(object)#Content) (12.0.1) | Signed by Vereesa and Aethas | "In memory of Theramore, Dalaran, and the Sunwell. Quel'falan danas!" | No |
| Ishnu alah terro shar | b | [Bury Me Not](https://warcraft.wiki.gg/wiki/Bury_Me_Not#Notes) (12.0.1) | Knight Anais | Scrambler output for "Until even stars fade..." | Not elvish |

A fourth use of *Bal'a dash, malanore*, Bloodguard Nelric's gossip, is left out: the wiki files it under `{{Rfb-section}}`, removed from the beta ([Bloodguard Nelric](https://warcraft.wiki.gg/wiki/Bloodguard_Nelric#Quotes)).

## Names in Midnight text

None of these has a spoken gloss. They are listed for completeness.

1. **Names with an English epithet.**
   1. [Alah'endal, the Dawnsong](https://warcraft.wiki.gg/wiki/Alah%27endal,_the_Dawnsong#Speculation) (item 249296, 12.0.1) is new to the lexicon. Its parts read *alah* "light" (inferred) and *endal* "breath" (segment). The wiki's "Lightbreath" is marked as speculation.
   2. [Belo'melorn, the Shattered Talon](https://warcraft.wiki.gg/wiki/Belo%27melorn,_the_Shattered_Talon#Trivia) (item 249283, 12.0.1) is new to the lexicon. In beta it was Belo'ren's Mystic Talon, so *belo-* probably comes from the phoenix [Belo'ren, Child of Al'ar](https://warcraft.wiki.gg/wiki/Belo%27ren,_Child_of_Al%27ar). The wiki's "Sunstrike" is an editor's guess.
   3. *Lu'selama, Light's Justice* (12.1.5) and *Anu'shalla, Shadow's Guidance* (12.0.0) are already in the lexicon. The client's Mount table describes Anu'shalla's wings as cutting the sky "like shadows on a moonlit night", which fits *shalla* "shadow".
2. **Names on the wiki's list but not in the lexicon.** 24 of the list's 35 names occur on Midnight lines. Besides Alah'endal, Belo'melorn and Belo'ren, they are:
   1. Ath'Ran and Lash'Ra (Lightbloom areas), Shan'dor and Falithas (runestones), Scintilas Falls, Shan'dorah, Belanise, Sinara, Sintalia, and Sin'gria (the wiki says it is a pun on sangria);
   2. older names, most of them only in the wiki's own prose: Quel'Danas, Quel'Danil, Quel'Lithien, Elrendar, Falthrien, Shalandis, An'daroth, An'owyn, An'telas, Lu'minellia and San'layn.
3. **Names in neither:**
   1. [Lu'ashal](https://warcraft.wiki.gg/wiki/Lu%27ashal#Adventure_Guide) is a world boss in Eversong, a dragonhawk the Adventure Guide says grew huge "from the surging Holy energy". That fits *lu* "light".
   2. The rest have no gloss: the arcane golems Construct V'anore, E'nui and Ali'a; the food Kale'thas Sunsalad; the NPC Fel'orei Moonstrider; the Kal'delar armor set.
4. **Legion Remix.** Patch 11.2.5 brought back Legion's story as Legion Remix, so the range also holds Legion's Suramar names (Elun'eth, Ly'elth, Shal'Aran, the fal'dorei). They are older nightborne names, not new Midnight elvish.
5. **Out of scope.** The Haranir villages carry English epithets, such as *Har'mara, Village of Balance*, but Haranir is not elvish. The troll (Zandali), draenei and Shath'Yar lines were skipped.

## Untranslated: nobody explains these

1. *Quel'falan danas!* ends the [Silversun Compact](https://warcraft.wiki.gg/wiki/The_Silversun_Compact_(object)#Content), a pact for mages to work together against world-ending threats, signed by Vereesa Windrunner and Aethas Sunreaver. Only *quel* "high" is known. Candidate: a low-confidence note.
2. *Anu bala belore'alon* is Aethas's sign-off in The World Awaits. Reports [1](1-review-and-methods.md) and [8](8-reconstruction-audit.md) already handled it, and the wiki adds nothing new.
3. *Anar'anel belore* has no gloss either. The lexicon's "For the sun!" is inferred, and Knight-Lord Sunguard's cheer fits it.
4. *Minn'da* only names a chapter. No line says what it means, but the chapter is Arator's search for his mother, which fits the lexicon's "mother".
5. *Arcan'dor* is explained by what it names, a mana tree. No line explains its parts.
6. Item names *Alah'endal* and *Belo'melorn* have epithets but no literal translation.

## Scrambler check

1. Only one Midnight line has every word in the scrambler list: Knight Anais's "[Thalassian] Ishnu alah terro shar..." in [Bury Me Not](https://warcraft.wiki.gg/wiki/Bury_Me_Not#Notes).
2. All four words are in the Thalassian scrambler list (language 10, 102 words, in the local WoW Forever LanguageWords table). The Darnassian (2) and Shen'dorei (310) lists are the same as each other, and differ from it only in two spellings: *Falla* and *Shindu'falla'na* for *Fallah* and *Shindu'fallah'na*.
3. The same page also has the understood line, "[Thalassian] Until even stars fade...". Its word lengths, 5-4-5-4, match the scrambled words one for one.
4. The wiki's [Thalassian primer](https://warcraft.wiki.gg/wiki/Thalassian#Thalassian_primer_(official_translations)) still lists "Ishnu alah terro shar = Until even stars fade" as an official translation. Report 1 already flagged this.
5. The script flagged 15 more Midnight records, on 14 lines, as all-scrambler. All were false positives: names and single words such as Ash'an, Aman, N'ala, *alah* and *belore*, and the painting title *Anar'alah Belore*. The scrambler borrows real words, so a real word can be on the list.

## Cross-checks

1. **Confirmed in the client's own tables** (wago.tools, build 12.1.7.70986, looked up by ID or name):
   1. [ItemSparse 249296](https://wago.tools/db2/ItemSparse?filter%5BID%5D=exact%3A249296): Alah'endal, the Dawnsong.
   2. [ItemSparse 249283](https://wago.tools/db2/ItemSparse?filter%5BID%5D=exact%3A249283): Belo'melorn, the Shattered Talon.
   3. [ItemSparse 280799](https://wago.tools/db2/ItemSparse?filter%5BID%5D=exact%3A280799): Lu'selama, Light's Justice.
   4. [Mount 2917](https://wago.tools/db2/Mount?filter%5BID%5D=exact%3A2917): Anu'shalla, Shadow's Guidance.
   5. [JournalEncounter 2827](https://wago.tools/db2/JournalEncounter?filter%5BName_lang%5D=Lu%27ashal): Lu'ashal.
   6. [JournalEncounter 2739](https://wago.tools/db2/JournalEncounter?filter%5BName_lang%5D=Belo%27ren): Belo'ren, Child of Al'ar.
   7. [CriteriaTree 211364](https://wago.tools/db2/CriteriaTree?filter%5BID%5D=exact%3A211364): "A Meeting with Minn'da", a criterion under tree 211359, which is the tree of [Achievement 42299](https://wago.tools/db2/Achievement?filter%5BID%5D=exact%3A42299), Visions of a Shadowed Sun. The client confirms the chapter name. That the chapter is about Arator's mother comes from the in-game Lore Book text as the wiki transcribes it.
   8. [BroadcastText 118587](https://wago.tools/db2/BroadcastText?filter%5BID%5D=exact%3A118587): "Now the power of the arcan'dor is mine!", an older line. It confirms the word, not Thalyssra's explanation.
2. **Not independently confirmed: the spoken and quest lines.** They are server-side text. The 12.1.7 client's BroadcastText holds 10,888 rows: the local zhCN, zhTW and koKR copies, and wago.tools for enUS. None of these lines is among them: a text search on wago.tools finds neither Thalyssra's nor Cho's lines, and the koKR rows have no Hangul spelling of the greetings either. Each greeting does appear on two or more wiki pages (an NPC page and a quest page), but those are separate edits to the same source. Vereesa's line is the exception: report 4 confirmed it through BroadcastText 309952.

## Limits

1. The wiki is fan-transcribed. Spellings drift (Sind'orei, Hal'hader), and lines go missing.
2. English is detected with the macOS word list plus a stemmer. The hand review of non-English words from elven speakers found no elvish word that the apostrophe and lexicon tiers had missed.
3. Speaker race comes from the speaker's Npcbox. Quest text has no speaker field, so the quest giver was read from the Questbox by hand.
4. The era model reads the wiki's markers, which editors place unevenly.
   1. A page added in the range counts whole wherever it has no marker, so it can hold older text that counts: the history sections of a zone page rebuilt for Midnight, or the Silver Hand's old motto. The reading set those apart (see Counts).
   2. A page that existed before Midnight counts only inside its marked sections. Saltheril's on-click list has no marker, so it was found by reading, using the page's 12.0.1 patch note.
5. Song lyrics, and the long texts of books and pacts, are named and linked, not copied.

## Candidates ([10-candidates.json](10-candidates.json))

| Action | Word | Confidence | What |
|---|---|---|---|
| fix evidence | anu belore dela'na | high | Five Midnight uses |
| fix notes | anu belore dela'na | medium | Also a toast and a parting wish |
| fix evidence | al diel shala | high | Two Midnight farewells |
| fix evidence | bal'a dash, malanore | high | Two Midnight gossip openers |
| fix evidence | sinu a'manore | high | Astalor's on-click greeting |
| fix evidence | shorel'aran | high | Aethas's sign-off, Astalor's farewell and Lor'themar's farewell to Liadrin |
| fix evidence | anar'anel belore | medium | Knight-Lord Sunguard's cheer |
| fix evidence | minn'da | medium | The chapter "A Meeting with Minn'da" (CriteriaTree 211364) |
| fix evidence | sin'dorei | high | Lorewalker Cho: "The blood elves, or sin'dorei" |
| fix evidence | lu | medium | Lu'ashal, the Light-infused world boss |
| fix evidence | lu'selama | high | ItemSparse 280799 |
| fix evidence | anu'shalla | medium | Mount 2917, name and description |
| add | alah'endal | medium | "the Dawnsong", an epithet |
| add | belo'melorn | medium | "the Shattered Talon", an epithet |
| add | arcan'dor | medium | Thalyssra: "a mana tree we call the Arcan'dor" |
| note | quel'falan danas | low | Untranslated |
| note | belo'ren | low | A phoenix's name; the "sun + void" reading is a guess |

Every `old` value except the *sin'dorei* fix's was copied from lexicon.json as it stood before reports 9 to 11 were applied. [Report 9](9-warcraft-iii.md) also proposes an evidence fix for *sin'dorei*, in [9-candidates.json](9-candidates.json); the two merge.

Four candidates were corrected before [scripts/apply_wc3_midnight.py](scripts/apply_wc3_midnight.py) applied them, on 2026-11-18 and 2026-11-19:
1. The *sin'dorei* evidence fix now starts from report 9's result, because report 9's fix is applied first and would otherwise leave this one stale.
2. *Alah'endal* and *Belo'melorn* are now proper nouns glossed as "an axe" and "a dagger" whose epithets are "the Dawnsong" and "the Shattered Talon", because both translators read a gloss of three words or fewer as a translation and turned "talon" into *Belo'melorn*.
3. *Arcan'dor*'s gloss gives its fruit after a semicolon, not a comma, because a comma splits a gloss into senses and both translators turned "whose fruit cleanses magic" into *Arcan'dor*.

## Reproduce

From the repo root, with any cache folder outside the repo. A first run makes about 1,400 requests at one a second, so it takes about 25 minutes; this cache holds 1,440 answers. Later runs read the cache. A first run reads the live wiki, which keeps changing, so its counts will drift from these.

```
python3 research/2026-11-revival/scripts/midnight_wiki.py enumerate CACHE
python3 research/2026-11-revival/scripts/midnight_wiki.py fetch CACHE
python3 research/2026-11-revival/scripts/midnight_wiki.py speakers CACHE
python3 research/2026-11-revival/scripts/midnight_wiki.py extract CACHE . CACHE/hits.json
python3 research/2026-11-revival/scripts/midnight_wiki.py check CACHE .
```

The script's tests run offline, on a small cache they build: [test_midnight_wiki.py](../../tests/test_tools/test_midnight_wiki.py).
