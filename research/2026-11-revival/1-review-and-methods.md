# Thalassian revival: review of the March 2026 build and new methods

Date: 2026-11-17. Scope: the code, lexicon, docs, tests and git history of this repo, plus new research.
Companion file: [1-candidates.json](1-candidates.json), with 179 proposed changes. Each one carries evidence quotes and a confidence level.

## Top findings

1. **Several "canon" meanings are wrong, and they reach the translator's output.** The current lexicon translates "death" as `bash'a`, "light" as `anar`, "no" as `shal'na`, "keeper" as `delar` and "you" as `alah`. The Blizzard sources say `bash'a` = *taste*, `anar` = *by*, `shal'na` = *aunt*. `delar` has no gloss at all, and `alah` is Darnassian *to you* (it means *light* in Thalassian).
   - "Bash'a no falor talah!" = "Taste the chill of true death!" ([Warcraft Encyclopedia](https://warcraft.wiki.gg/wiki/The_Warcraft_Encyclopedia/Thalassian)). It was spoken by Sylvanas in Warcraft III, not by Kael'thas.
   - "Shal'na = Aunt." Arator says it to Vereesa in the 11.2.7 quest [What Might Come](https://warcraft.wiki.gg/wiki/What_Might_Come#Notes). Blizzard's own zhCN localization of that line, [BroadcastText 302349](https://wago.tools/db2/BroadcastText?filter%5BID%5D=exact%3A302349&locale=zhCN), renders it 阿姨 ("auntie"). That second source is independent of the wiki.
2. **The "Midnight 12.0 datamine" never happened.** `scripts/scraper_wowhead.py` (commit bf6bf04) calls itself "a stub scraper" in its own comment. It fetched nothing, no dump was ever committed, and its built-in demo text has Lor'themar shouting a Darnassian war cry. All three "Midnight" words are mis-sourced:
   - `Shal'na` comes from an 11.2.7 quest.
   - `Anu'shalla` is the somnowl mount [Anu'shalla, Shadow's Guidance](https://warcraft.wiki.gg/wiki/Anu%27shalla,_Shadow%27s_Guidance). It is not a "Void Owl" and not a "herald".
   - `Rutaani` is [a plant-like race of Harandar](https://warcraft.wiki.gg/wiki/Rutaani), not a Thalassian word.
3. **Only 8 of the 84 `canon:true` entries are words that Blizzard glossed on their own.** 65 are segments cut out of glossed compounds, which is reasonable but is inference. 11 have no support or are wrong. One entry, `el` = peace, was invented by mis-splitting "diel" in "Al diel shala". 20 of the 65 segment entries also carry glosses that no source supports, such as *shine*, *fury*, *doom*, *kingdom* and *passage*.
4. **New methods add 112 entries.**
   - 83 phrases and compounds that Blizzard glossed, which the lexicon had missed. Examples: *Vendel'o eranu* (help me forget), *Ann'da* / *Minn'da* (father / mother), *Belore'dorei* (child of the sun), *Kim'jael* (little rat), *Medivh* (keeper of secrets), and the Darnassian *Shaha lor'ma* (thank you).
   - 29 inferred morphemes and decodings, all marked `canon:false`. Examples: *alah* (light), *dorah* (valor), *'o* (me), *shen* (hidden), and a full decoding of the ritual chant "Anar'sin arkhana! Anar'endal belore!" as "By blood (and) magic! By the breath of the sun!".
5. **The new generator is statistically indistinguishable from canon; the old one is not.**
   - A classifier separates the project's generated words (119 entries, 116 distinct morphemes) from canon with AUC 0.72 (0.5 would mean indistinguishable).
   - Of the 100 single-morpheme generated words, 6 are identical to attested elven forms: `thala`, `osa`, `thera`, `ethala`, `shari`, `dris`. 34 more are one edit away, though many of those are 2–3-letter words where one edit is hard to avoid.
   - Four of the identical ones (`thera`, `ethala`, `shari`, `osa`) are words from Blizzard's in-game language scrambler.
   - The new order-4 Kneser-Ney generator with phonotactic and collision filters scores AUC 0.52 against a 0.54 split-half baseline, with zero collisions.

Two smaller findings:

- **The wiki's "official" primer contains one artifact of the in-game scrambler.** "Ishnu alah terro shar = Until even stars fade" is what the language scrambler shows non-speakers. Each English word was swapped for a scrambler-list word of the same length (Until/Ishnu, even/alah, stars/terro, fade/shar); see [Bury Me Not](https://warcraft.wiki.gg/wiki/Bury_Me_Not#Notes) and the [scrambler list](https://warcraft.wiki.gg/wiki/Thalassian#Thalassian_word_parser). Do not import it.
- **The translator reproduces 4 of 39 canon phrases from their English gloss.** The Python and web engines both score this. Ordered recall is 0.44 to 0.45. Reverse translation scores a content-word F1 of 0.48.
   - Compounds come out in English order (`Dorei sin` instead of `Sin'dorei`).
   - "and" and "by" are on the drop list, so canon *rea* and *anar* can never be produced.
   - The reverse translator splits every word at the apostrophe, so `Bal'a` becomes "[bal] you".

## 1. Errors in the current lexicon, with fixes

### 1.1 Audit of all 84 `canon:true` entries

| Tier | Count | Entries | Verdict |
|---|---|---|---|
| A: Blizzard glossed the word itself | 8 | belore, rea, aranal, finel, minda→min'da, anda→an'da, lura (Darnassian), shal'na (after the fix) | Keep canon. |
| B: segment of a Blizzard-glossed phrase or compound, gloss OK | 45 | anore, bal'a, dorei, sin, quel, felo, malanore, selama, anaria, drassil, tel, nor, an, kal, ishnu, alah (Darn.), dieb, dal, shan, thero, zin, annalas, diel, arkhana, endal, shorel, falor, elor, bindel, alann, ren, sinu, tal, thas, shal, shanna, vala, thonos, erana, dora, isil, shalla, doral, ana, manore | The meaning is inferred from a glossed whole. **Decision for Mike:** a strict reading of "canon only when Blizzard states the meaning" makes these `canon:false`. I recommend keeping `canon:true` and adding a `canon_basis: "segment"` field. |
| B, gloss needs a fix | 20 | alar, dela, na, thalas, melorn, shindu, fallah, shola, bash'a, serrar, ban, dinoriel, talah, do, shala, anar, dracon, band'or, ru, ashar | Fix the meaning or the source (in the JSON). |
| C: no support, or wrong | 11 | anu, ashal, dash, delar, el, aran, rath, kanesh, anu'shalla, rutaani, isera | Demote 9; remove `el` and `rutaani`. |

### 1.2 Wrong meanings and wrong sources (highest impact first)

| Entry | Current | Should be | Evidence |
|---|---|---|---|
| bash'a | death/destruction (noun), "Kael'thas quote" | **taste** (imperative verb), Sylvanas, Warcraft III | "Bash'a no falor talah! \|\| Taste the chill of true death!" ([Encyclopedia](https://warcraft.wiki.gg/wiki/The_Warcraft_Encyclopedia/Thalassian)) |
| talah | survive/endure (verb) | **(true) death** (noun); shares the root of *tal* "death" | same phrase; "Tal anu'men no Sin'dorei = Death to all who oppose the children of the blood." ([primer](https://warcraft.wiki.gg/wiki/Thalassian#Thalassian_primer_(official_translations))) |
| shal'na | "no!/please", Vereesa at Rhonin's death, "Midnight alpha" | **aunt**: Arator to Vereesa, patch 11.2.7; Darnassian cognate *Shal'nar* | primer; [What Might Come](https://warcraft.wiki.gg/wiki/What_Might_Come#Notes); zhCN 阿姨 ([BroadcastText 302349](https://wago.tools/db2/BroadcastText?filter%5BID%5D=exact%3A302349&locale=zhCN)) |
| anar | light/by | **by** | three glosses start with "By": Anar'alah, Anar'alah belore, Anar'endal dracon |
| alar | phoenix | **ranger** (Alar'annalas = Ranger Lord). Al'ar is only a name. | primer; [Farstriders](https://warcraft.wiki.gg/wiki/Farstriders) |
| ashal | great/glorious | **for** (inferred, medium) | "Selama ashal'anore = Justice for our people." No "great" appears anywhere. |
| anu | hail/greetings | unknown; probably an optative "may/let" particle | no gloss has "hail". See Anu'dorini Talah = "Let my will be known" |
| dash | peace/path | only part of the greeting *bal'a dash* | "Bal'a dash, malanore = Greetings, traveler." |
| el | peace | **remove** (no such morpheme) | "Al diel shala = Safe travels"; Darnassian Alor'el = "Lover's Leaf" |
| delar | sword/keeper | unknown (Quel'Delar is "the Sister Blade") | [Quel'Delar](https://warcraft.wiki.gg/wiki/Quel%27Delar) |
| aran | town (canon, Darnassian) | speculation only | [Darnassian#Speculation](https://warcraft.wiki.gg/wiki/Darnassian#Speculation) |
| isera | green | no source; *Isera'duna* is a scrambler word | [scrambler list](https://warcraft.wiki.gg/wiki/Thalassian#Thalassian_word_parser) |
| anu'shalla | herald of shadow, "Void Owl", Thalassian | "Shadow's Guidance" (a mount epithet); presumably Darnassian | [mount page](https://warcraft.wiki.gg/wiki/Anu%27shalla,_Shadow%27s_Guidance) |
| rutaani | Thalassian, canon | a Harandar race name: **remove** | [Rutaani](https://warcraft.wiki.gg/wiki/Rutaani) |
| lura | water/sea, Thalassian | **sea, Darnassian** (Hearthstone song) | [Darnassian primer](https://warcraft.wiki.gg/wiki/Darnassian#Darnassian_primer_(official_translations)) |
| dracon | Darnassian | **Thalassian** (Revelations; Through the Mirror Darkly) | primer |
| serrar | Thalassian | **Darnassian** (Quel'Serrar is the night elves' blade) | [Quel'Serrar](https://warcraft.wiki.gg/wiki/Quel%27Serrar) |
| na | us/we | **us/our** (no source has "we") | dela'na "guides us"; Lament "Our enemies are breaking through"; Darnassian "Shu dalas na = Heavy are our hearts" |
| rath, kanesh | shield/missile, record/magic (canon) | context guesses: demote | [Shalassian untranslated](https://warcraft.wiki.gg/wiki/Shalassian#Untranslated_Shalassian_phrases) |
| thalas | home/kingdom | home ("kingdom" is from the non-canon RPG) | "Quel'Thalas = High Home." |
| ru | will/survive | will (*survive* is *shanna*) | "Ru shanna shal'dorei = The nightborne will survive." |
| minda, anda | no apostrophe | min'da, an'da (Darnassian); Thalassian is minn'da, ann'da | both primers |
| min (extrapolated) | blast | **remove**: built on "ashal = great" | Blizzard's zhTW line reads "Felomin ashal! = Fire consumes!" ([talk page](https://warcraft.wiki.gg/wiki/Talk:Thalassian#Making_a_wild_guess...)) |

Smaller gloss trims (in the JSON): dela (drop *shine*), melorn (drop *fury*), shindu (drop *doom*), fallah (drop *attack*), ban (drop *passage*), dinoriel (drop *watcher*), shala (drop *path*), shola (drop *intent*), ashar (*duel*), do (honorific suffix), band'or (spelling).

### 1.3 Generated words that collide with or shadow canon

The lookup is first-match over the list order (`parser.py:24-31`), so duplicate English senses decide the output silently.

| Problem | Words |
|---|---|
| Identical to Blizzard's in-game scrambler words, so in-game gibberish "translates" | thera (what), ethala (all), shari (many), osa (that) |
| Duplicates a canon meaning | elu'shin vs elor (sleep); ishala and suran vs alann (heart); lubala and nu vs alah/lu (light); athar vs ban (gate); thal vs arkhana (magic) |
| Equal to, or one edit from, an attested form | thala = Shalassian *Thala* (nar'valas); tala ~ tal/talah (death); dorin ~ dorini; sindor reads as Sin'dor(ei); an'dorei looks like a race name; talor ~ falor; ishala ~ shala; ethis ~ ethil |
| Invented etymology | al'ore, il'ore and an'dorei rest on "anu = self", which no source supports |
| Generated, but actually attested | dris (eye): Darnassian *Elun'dris* = "the Eye of Elune". Re-source it as an inferred Darnassian morpheme. |
| Duplicate senses among generated words | see (tala / dris'ael), hear (selorue / thelis'ael), day (sir / sira), I (on / al'ore), not (la / nath), live (thala / anor'ael), know (doras / ishari), feel (tana / ondore) |

The check behind this table is an edit-distance scan against 273 attested forms (Method 7). The removals it supports are in the JSON with `"action": "remove"`.

## 2. Code and data bugs

| # | Where | Bug | Effect |
|---|---|---|---|
| 1 | `src/thalassian/syntax/parser.py:21` and `web/index.html:660` | "and" and "by" are in the drop lists | Canon *rea* (and) and *anar* (by) can never be produced. |
| 2 | `src/thalassian/syntax/parser.py:24-31` | First match in list order wins; canon is not preferred | "keeper" becomes `delar`, "death" becomes `bash'a`, "you" becomes Darnassian `alah`, "no" becomes `shal'na`. |
| 3 | `src/thalassian/syntax/parser.py:92-95` with `:170-176` | The fallback pairs any word with a following pronoun; a dropped base returns "" | "Justice for you" becomes `Selama` (the pronoun is lost). |
| 4 | `src/thalassian/syntax/parser.py:124-154` | Output keeps English order; no modifier-first compounding | "children of the blood" becomes `Dorei sin` (canon: `Sin'dorei`); 3 of 5 two-part compounds come out reversed. |
| 5 | `src/thalassian/syntax/parser.py:163` | Plural guess is `endswith('s') and len>3` | "travels" becomes `shalei`; "this" is lemmatized to "thi". |
| 6 | `src/thalassian/syntax/parser.py:7-12` | spaCy is loaded inside a bare `except` | Tests run only the regex fallback here (spaCy is not installed); the spaCy path is untested. |
| 7 | `src/thalassian/morphology/agglutination.py:2-5` and `web/index.html:621,661-667` | `we→anu`, `they→danu`, `them→dan` are invented | Conflicts with canon `na` (us/our); `anu` is not "we". |
| 8 | `src/thalassian/morphology/pluralization.py:1-7` vs `docs/methodology/grammar.md` §4 | Code turns `shola` into `sholei`; the doc says `sholai`. `dorei` gets `doreii`. | No canon support for an -i/-ei plural: *dorei* is glossed both "child" and "children". |
| 9 | `src/thalassian/phonetics/markov.py:14-30` | `while True` with no attempt cap | Can hang if no word of length 3-8 is reachable. |
| 10 | `src/thalassian/phonetics/markov.py:41-61` | No word-start/end states; random start letter | Produces `ndr`, `qur`, `zis`, `qut`, plus canon duplicates `zin`, `kal`, `tal`, `nor`, `ban`. |
| 11 | `src/thalassian/cli/main.py:48` | Novelty is checked only against canon words | Collides with generated words and the scrambler list. |
| 12 | `web/index.html:635` | The reverse translator splits at apostrophes before lookup | `bal'a`, `bash'a`, `shal'na` and every apostrophe entry are unreachable; `Bal'a` becomes "[bal] you". |
| 13 | `web/index.html:645` | Plural heuristic `e.word+"i"` / `slice(0,-1)+"ei"` | False matches (e.g. any word ending in -ei). |
| 14 | `web/index.html:525` with `.github/workflows/static.yml:32` | Pages uploads only `./web`, so `../src/...lexicon.json` always 404s; `response.ok` is not checked | Production always loads `raw.githubusercontent.com/MikeKovetsky/thalassian/main`, never the deployed copy. |
| 15 | `web/CNAME:1` | Contains a comment, not a domain | Invalid CNAME; delete the file. |
| 16 | `src/thalassian/data/lexicon.json` | `root` values invent shared roots (`dela`/`delar` "del"; `thalas`/`thal`/`thala` "thal"; `malanore` "mal") | Misleading etymology. Line numbers of the flagged entries: alar 3, anu 27, ashal 39, dash 63, bash'a 255, delar 279, el 315, talah 327, anar 579, aran 759, shal'na 903, anu'shalla 915, rutaani 939, isera 1275. |
| 17 | `tests/test_syntax/test_parser.py:47,57-59` | Tests lock in bugs: `[bind]'o` and `Quel thalas` (canon is `Quel'Thalas`) | Fixing order or compounding will "break" tests. `tests/test_morphology/` and `tests/test_phonetics/` are empty, and `test_ast.py` duplicates `test_parser.py`. |
| 18 | `pyproject.toml:39,32,35` | Homepage is `github.com/Portal-OS/thalassian` (the repo is MikeKovetsky/thalassian); the spaCy model is pinned 3.7.1 while spaCy is unpinned; `mkdocs-material` is a runtime dependency | Install and version drift. |

## 3. Docs and claims that do not hold

- `README.md:1` says "The Official Sin'dorei Language Engine". Commit 51e9758 removed "Official" from the subtitles but not from the H1.
- `README.md:4,11,72` claim "Patch 12.0 Midnight datamines". No dumps were used (see Top finding 2).
- `README.md:11` says "Unlike older fan wikis that invented vocabulary from thin air". 119 of the 206 entries (58%) are invented.
- `README.md:36` translates "Justice for our great people". The canon gloss has no "great".
- `docs/methodology/lexicon.md:8,11` claim "Zero random inventions" and "gathered exclusively from three official lore dialects". Neither is true.
- `docs/methodology/lexicon.md:22` credits the Markov chain for new roots. The 57 Swadesh words came from an LLM ("Claude 3 Opus", per `how-to-use-portal.md` §3), not from the Markov chain.
- `docs/methodology/lexicon.md:30` describes `scraper_wowhead.py` as datamining. It was a stub, deleted in 063c6b8.
- `docs/citations.md:11-12,35` cite "leaked dialogue from Vereesa, Halduron, Lor'themar" and an "Anu'shalla Void Owl". Neither exists.
- `docs/methodology/grammar.md`:
  - §5 says "Elves generally drop prepositions". Canon has *anar* (by), *vala* (through, Shalassian) and *bessae* (from the, Darnassian).
  - §3 builds the past tense `-ash` from "ashal = complete/great" and the future `ru-` from Shalassian. There is no canon support for either; Darnassian *Ru shallora enudoril* = "I anoint…" is present tense.
  - §1 claims SVO. Shalassian *Ru shanna shal'dorei* = "The nightborne will survive" is verb-subject.

## 4. Missed canon

The 83 directly glossed items are in the JSON as `"canon": true`. In brief:

- **Thalassian phrases and compounds (36):** alar'annalas, fora'nal, al diel shala, ama noral'arkhana, anar'alah, anar'alah belore, anaria shola, anar'endal dracon, ann'da, minn'da, anu belore dela'na, bal'a dash malanore, ban'dinoriel, bash'a no falor talah, belono sil'aru belore'dorei, belore'dorei, doral ana'diel, elor bindel felallan morin'aminor, elu'meniel mal alann, felo'melorn, kim'jael, medivh, quel'dorei, quel'thalas, ren'dorei, sin'dorei, selama ashal'anore, shindu fallah na, shindu sin'dorei, shorel'aran, sinu a'manore, tal anu'men no sin'dorei, thas'alah, thas'dorah, vendel'o eranu, band'or shorel'aran.
- **Shalassian (5):** shal'dorei, tal'ashar, erana-dora isil, quel'vala thonos, ru shanna shal'dorei.
- **Darnassian (42):** shaha lor'ma (thank you), elune-adore, ishnu-alah, ishnu-dal-dieb, andu-falah-dor, ande'thoras-ethil, bandu thoribas, ash karath, fandu-dath-belore, tor ilisar'thera'nal, anu'dorini talah, shu dalas na, aria, bessae, denalore, shal'nar, minn'do, **shen'dorei** ("hidden people", the WoW Forever Skyborne, Sept 2026), shen'dralar, xaxas, kaldorei, tal'doren, elun'dris, irana'ethil, jai'alator, lathar'lazal, nar'valas, shalla'tor, shal'nan, ellemayne, alor'el, al'anath, alash'anir, alara'shinu, ama'shan, bel'ameth, eluvi'ana, t'lara, shanna melor'ne adala fal, ru shallora enudoril, zin-azshari, nahlen'do.
- **New since the March build:**
  - *Lu'selama, Light's Justice* (item, 12.1.5)
  - *Anu bala belore'alon* reused by Aethas in [The World Awaits](https://warcraft.wiki.gg/wiki/The_World_Awaits_(Midnight)#Completion) (12.0.1), still untranslated
  - *Shan'dorah* (K'aresh place name, untranslated)
  - the Forever-era Darnassian *Shen'dorei*
- **Not imported on purpose:**
  - *Ishnu alah terro shar*: a scrambler artifact (Top findings).
  - *Vereesa's Copper Coin* text: scrambler output, and the wiki says so.
  - The Canticle of Sacrifice lyric sheet: its translation has no cited source, so it is used only as corroboration and its lyrics are not reproduced.

## 5. Methods run: what each found and its limits

### Method 1: Rebuild the canon corpus

**What I did:** pulled the raw wikitext of the [Thalassian](https://warcraft.wiki.gg/wiki/Thalassian), [Darnassian](https://warcraft.wiki.gg/wiki/Darnassian) and [Shalassian](https://warcraft.wiki.gg/wiki/Shalassian) pages, the [Encyclopedia copies](https://warcraft.wiki.gg/wiki/The_Warcraft_Encyclopedia/Thalassian), and 40 linked item, quest and talk pages.

**Result:** 114 phrase–gloss pairs.

| Language | Pairs | Of which |
|---|---|---|
| Thalassian | 50 | 40 official, 3 zhTW localization, 6 lyric lines, 1 epithet |
| Darnassian | 59 | |
| Shalassian | 5 | |

Every wiki quote in the JSON was checked by script against the downloaded source: 236 of 236 found.

**Limits:**
- Tweets (Loreology / Llorewalker) are dead links. They are quoted via the wiki.
- Novels were not read directly; their page citations come from the wiki.

### Method 2: Cross-situational alignment over the corpus

**What I did:** ran IBM Model 1 (30 EM iterations, with a NULL token) and Dice co-occurrence, per language and pooled.

**Clear results (two or more independent phrases):**

| Morpheme | Meaning | Phrases |
|---|---|---|
| dorei | child/children | 7 |
| belore | sun | 6 |
| anar | by | 3 |
| alah | light | 3 |
| sin | blood | 3 |
| selama | justice | 2 |
| thas | forest | 2 |
| diel / shala | safe / travel(s) | 2 |
| shorel'aran | farewell (as a unit) | 2 |
| ann'da / minn'da | father / mother | 2 |
| anore | (our) people | 2 |
| na | us/our | 4, across Thalassian and Darnassian |
| drassil | crown (Darnassian) | 5 |
| shan | honor (Darnassian) | 3 |
| shen | hidden (Darnassian) | 2 |

**By elimination:** ashal = for, mal = your, 'o = me, vendel/eranu = help/forget, dorah = valor.

**Limits:**
- Most morphemes occur once, so alignment can only split a gloss by position.
- Pooling the three languages creates false friends:
  - *tal* is death (Thal.), honor (Shal. tal'ashar) and wild (Darn. tal'doren).
  - *alah* is light (Thal.) and to-you (Darn.).
  - *shanna* is survive (Shal.) and truth (Darn.).
- The model confused *no* with "death" until *talah* was merged with *tal*. It needs morphological normalization first.

### Method 3: Comparative method (Darnassian, Thalassian, Shalassian)

Cognate sets and the correspondences they suggest:

| Darnassian | Thalassian | Shalassian | Correspondence |
|---|---|---|---|
| An'da "father", Min'da "mother" | Ann'da, Minn'da | | Darn. n' → Thal. nn' before 'da (2 cases; Darn. *Minn'do* shows the same doubling, so this may be spelling, not a sound law) |
| Shal'nar "aunt" | Shal'na "aunt" | | Darn. final -r → Thal. ∅ (1 case). Note: a Thal. *shal'na* predicted from the Darnassian matches the later attestation. |
| Falla (scrambler) | Fallah (scrambler) | | Darn. -a → Thal. -ah (Blizzard's two scrambler lists differ only here) |
| | arkhana "magic" | arcana (Aran'arcana) | Thal. kh → Shal. c (1 case) |
| bandu "prepare" (Bandu thoribas) | band'or "prepare" (zhTW) | | shared root band- |
| quel, dorei, felo'melorn, ishnu-alah (Kael'thas uses it) | same | quel, dorei | identity |
| Belor'relos "the Suncaller" | belore "sun" | | belor ~ belore |
| Ande'thoras-ethil "may your troubles be diminished" | | Ash'thoras denil (a greeting) | shared *thoras* in greeting/farewell formulas |
| Elune-adore "Elune be with you" | | An'ratha adore (a farewell) | *adore* = be with you |

**Conclusion:** there are no regular sound correspondences with more than two supporting pairs. The data support only one prediction: shared vocabulary is mostly identical, with occasional final-consonant loss in Thalassian.

**Output:** a handful of predicted Thalassian forms, all `canon:false` and low confidence: *shaha lor'ma* (thank you), *lura* (sea), *dris* (eye), *shen* (hidden). Blizzard has not drawn the languages with sound laws, so claims beyond this would be invention.

### Method 4: Decoding untranslated phrases with the established morphemes plus context (`canon:false`)

| Phrase | Decoding | Basis | Confidence |
|---|---|---|---|
| "Anar'sin arkhana! Anar'endal belore!" | "By blood (and) magic! By the breath of the sun!" | Every word is already established; the context is a ritual | medium |
| "Endala finel endal!" | "Breathe your last breath!" | Said on killing a player; endal = breath, Darn. finel = the last | low |
| "Thalas'din belore" | "Defender of the home of the sun" | Flavor text of *Fal'inrush, Defender of Quel'thalas*; din- as in Ban'**din**oriel "gatekeeper" | low |
| "Anar'anel belore" | "For / by the power of the sun" | zhTW "For the sun"; Kael'thas alternates it with "By the power of the sun" for the same ability | medium |
| "Anar'alash denal!" | "By …!": an exasperated oath | [BroadcastText 69644](https://wago.tools/db2/BroadcastText?filter%5BID%5D=exact%3A69644&locale=zhCN), Lor'themar: "…Will someone tell me WHAT is going on in Dalaran?" No locale translates it. | low (not added) |
| Shalassian *In'alah* | alah = light | Said while lighting the city's lamps; matches Thal. alah | medium |

### Method 5 (new): Mining Blizzard's own localizations

Chinese localizers often translate elven lines instead of keeping them. I verified this on [wago.tools](https://wago.tools/db2/BroadcastText) (retail build 12.1.7.70892):

| Line | zhCN | zhTW | koKR, ruRU, deDE |
|---|---|---|---|
| "Shal'na! Come back to us." | 阿姨 (auntie) | keeps Shal'na | keep Shal'na |
| "Shorel'aran..." | keeps it | 再會了 (farewell) | keep it |
| "Anar'alash denal!" | keeps it | keeps it | keep it |

The wiki talk page reports zhTW glosses for three more Kael'thas lines: *Balamore shanal* (prepare to die), *Anar'anel belore* (for the sun), *Felomin ashal* (fire consumes). They are added as medium-confidence `canon:false` until they are re-verified.

**Limits:**
- wago's text search covers only part of the table: "Silvermoon" returns just 7 rows.
- Wowhead blocks scripted access (HTTP 403).
- Mining at scale needs the full localized BroadcastText export, which I did not download. See next steps.

### Method 6: WoW Forever client scan (`.wowf-extract/`, build 1.60.1.70938, read-only)

**What I did:** scanned 811,593 strings, plus `Languages.csv`, `LanguageWords.csv` and `BroadcastText.csv`.

**Findings:**
- There is a new language, **ID 310 "Shen'dorei"**.
- Its scrambler word list is the Darnassian list (the same 102 words, shuffled). In Blizzard's data it is a skin over Darnassian.
- No glossed elven text exists in the client. Quest and NPC speech are served by the server: BroadcastText has only 139 rows in the finished extract (12 shipped, 127 cached from play), none of them elven.
- Names only: Shen'dralas, Shen'dar, Shen'dramar, Ban'aethal, Urs'endris, Jai'vhanel, Nord'el, Al'Aketh.

**Limits:** the folder had no `README.md` when I checked, and it was still being filled during this run. The server-cached text (WDB) will grow as the client is played.

### Method 7: Phonotactic model

**Training set:** 273 attested elven forms (glossed and untranslated, all three languages).

**Discriminability test:** a naive-Bayes classifier on character 2- and 3-grams plus word length, scored with 5-fold cross-validation and AUC. 0.5 means indistinguishable from canon.

| Word set | n | AUC vs canon | Identical to attested or scrambler forms | One edit away |
|---|---|---|---|---|
| canon vs canon (split-half baseline) | 273 | 0.54 | n/a | n/a |
| Blizzard scrambler words | 94 | 0.60 | n/a | n/a |
| lexicon's generated words (116 distinct morphemes; collision counts are for the 100 single-morpheme words) | 116 | 0.72 | 6 | 34 |
| repo `generate-words` (order-1 chain) | 200 | 0.74 | 27 | 85 |
| repo `generate-roots` | 200 | 0.86 | 30 | 82 |
| **new: order-4 Kneser-Ney + phonotactic filter + edit distance ≥2 + length matching** | 200 | **0.52** | **0** | **0** |

Sample new words: mallann, aluel, nariath, shorah, enalora, ishana, thallan, bethalla, daelen, shoralas, therorin, andalorah, shindel, asharas, orindu, balarana, adorinas, ishnor, tenielas, silor.

**Limits:**
- Leave-one-out perplexity barely changes (8.12 for order 4 vs 8.14 for order 2). The gain comes from the filters, not from a better fit, because the data are too small.
- One output, `rthalah`, shows the filter should also ban word-initial clusters other than th, sh and dr.
- The new generator was trained on all 273 forms, including the classifier's test folds, which pulls its AUC toward 0.5. A strictly held-out test would retrain the generator inside each fold, so read 0.52 as a slightly optimistic figure.

### Method 8: Translator evaluation on canon phrases

Each engine was fed the 39 official Thalassian glosses.

| Engine | Exact | Ordered recall (LCS) | Notes |
|---|---|---|---|
| Python `compile_sentence_en` (regex fallback; spaCy not installed) | 4/39 | 0.44 | 49% of outputs contain [untranslated] words |
| Web `strictTranslate` | 4/39 | 0.45 | same with "Canon only" on |
| Web `reverseTranslate` (Thal. → EN) | n/a | content-word F1 0.48 | 15/39 lines contain [unknown] tokens |

Worst cases:
- "Tal anu'men no Sin'dorei" comes out as `Bash'a ethala theli [oppose] dorei sin`.
- "Shindu fallah na" comes out as `[They] [are] [breaking] vala` (Shalassian *vala* fills "through").

The cheapest large win is a phrasebook that matches whole canon phrases first.

## 6. Grammar findings from the canon

These replace parts of `grammar.md`.

1. **Apostrophe compounds put the modifier first and the head last.** This holds in all 10 Thalassian compounds whose parts are known independently: Quel'Thalas (High Home), Thas'alah (Light of the Forest), Thas'dorah, Felo'melorn, Ban'dinoriel, Lu'selama, Belore'dorei, Sin'dorei, Ren'dorei, Quel'dorei. It also holds in 13 Darnassian and Shalassian cases: Tel/Nor/An/Amir/Vor-drassil, Elun'dris, Kaldorei, Shen'dorei, Tal'doren, Shalla'tor, Shan'do, Nahlen'do, Shal'dorei. The one exception is Darnassian *Thero'shan* (honored student), where *shan* follows. Alar'annalas and Tal'ashar were segmented by this rule, so they are not counted as support.
2. **Free genitive phrases put the head first:** *falor talah* "chill of true death", *Ann'da anore* "father of our people".
3. **Enclitic pronouns:** *'na* = us/our and *'o* = me. *'a* = you has no support.
4. **Imperatives come first in the clause:** Anaria shola, Bash'a…, Vendel'o eranu, Belono sil'aru, Aranal; Darnassian Ash karath, Bandu thoribas. Shalassian *Ru shanna shal'dorei* is verb-subject, so strict SVO is not established.
5. **Prepositions exist** (anar, vala, bessae). Number is unmarked on *dorei* (child or children). There is no attested tense morphology.

## 7. Recommended next steps, ranked by value

1. **Apply the JSON in one reviewed change.** That means the fixes, demotions and removals, plus the 83 canon phrase and compound adds. Then add a phrasebook-first lookup and a `canon_basis` field (attested word / segment / localization / epithet / inferred) that drives the "Canon only" toggle. This removes the wrong output for death, light, you, no, keeper and great.
2. **Fix translator bugs 1–4 and 12** (drop lists, canon-first lookup, pronoun loss, modifier-first compounds, apostrophe lookup). Add regression tests that use the 39 canon phrases as gold, and retire the tests that lock in bugs.
3. **Localization mining at scale.**
   - **Mike's go is needed:** downloading the [wago.tools BroadcastText CSV](https://wago.tools/db2/BroadcastText) for zhTW, zhCN and koKR is a file download. The size is not advertised; it is likely tens of MB per locale.
   - Then filter for lines with elven tokens and back-translate the ones the localizers rendered. This is the only untried source of new official meanings, and two of three sampled lines confirmed it works.
4. **Correct the README, `lexicon.md`, `citations.md` and `grammar.md` claims** listed in section 3.
5. **Replace the Markov generator** with the KN-plus-filter generator. Regenerate the Swadesh list with collision checks, and record `method` on every generated entry.
6. **Data-integrity tests:**
   - no duplicate English senses;
   - no generated word within one edit of an attested form or a scrambler word;
   - every `canon:true` entry carries an evidence field.
7. **Re-scan `.wowf-extract/`** after the extraction agent finishes, especially WDB caches with server text, for new Shen'dorei/Darnassian lines.

## Appendix: reproducibility

- **Scripts.** The analysis scripts are in [scripts/](scripts/) and take their folders as command-line arguments. The ones that read the lexicon reproduce this report only against the pre-revival lexicon (commit 42eb9cf):
  - `corpus.py`: the corpus
  - `align.py`: alignment
  - `phono.py`: phonotactics
  - `evalpy.py` and `evaljs.js`: translator evaluation (`evaljs.js` holds a copy of the March web translator)
  - `make_candidates.py`: generates the JSON, against the pre-merge lexicon
- **No paid APIs were called.** Sources were warcraft.wiki.gg (raw wikitext), wago.tools pages and the local `.wowf-extract/` files.
- **Lyrics are described, not reproduced.**
