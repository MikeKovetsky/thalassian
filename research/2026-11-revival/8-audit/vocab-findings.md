# Vocabulary audit of the invented layer

> **Appendix to [report 8](../8-reconstruction-audit.md).** A copy of `vocab-findings.md` from the local, gitignored audit folder `.wowf-extract/audit/`, as the audit wrote it on 2026-11-18. Only its links were changed: links into the repo now resolve from this folder, and the files that stay local are named without a link. What the audit proposed was applied through [8-candidates.json](../8-candidates.json); the [merge log](../merge-log.md#reconstruction-audit-8-candidatesjson) lists the result.

Date: 2026-11-18. Lexicon: `src/thalassian/data/lexicon.json` at commit 5cbb931 (314 entries). Nothing in the repo was changed.

Scope: the 107 entries with `canon_basis: "generated"` (58 from the Markov chain, 49 Swadesh words written by Claude 3 Opus), the 2 `extrapolated` entries and the 9 `unverified` ones, 118 in all. Where the root field or a gloss of a canon entry interacts with them, that entry is listed too.

Files in this folder:

| File | What it holds |
|---|---|
| `vocab-candidates.json` (local) | 98 proposed actions, one object per entry: 9 remove, 42 regenerate, 23 fix, 24 note. 27 reviewed entries have no entry-specific action. |
| `coverage.json` (local) | The Swadesh-207 table. |
| `vocab-checks.json` (local) | Raw machine checks: every collision hit, KN and classifier scores per morpheme, sense overlaps. |
| `audit_vocab.py` (local), `build_coverage.py` (local), `build_candidates.py` (local) | The scripts that make the three JSON files. Standard library only. |

## Summary

**The invented layer still has the flaws report 1 found in it, and more.** Report 1's fixes removed the worst cases (four scrambler words, six canon duplicates). Everything it held back is still in the lexicon: the five low-confidence removals, all eight duplicate-sense pairs, and the shared-root and generator bugs. Checking against the wider attested set (report 7's 419 forms, every scrambler list, the name generator) adds new collisions. The Swadesh layer also turns out to rest on an invented morphology that contradicts canon meanings in ten places.

Counts per finding type (entries affected; one entry can have several):

| # | Finding type | Entries |
|---|---|---|
| 1a | Generated word identical to an attested form of unknown meaning | 5 whole words (sira, thala, san, tora, era), plus 3 parts in 5 compounds (al, ro, anor) |
| 1b | Attested form of unknown meaning that still carries a guessed gloss | 7 (delar, aran, rath, kanesh, isera, alon, ledel) |
| 1c | Generated word one edit from an attested elven form | 26 of 107 |
| 1d | Scrambler words: whole-word / part / one edit from an elven list | 0 / 6 / 12 |
| 1e | Name-generator name, exact | 2 (dara, tala), plus the part rae |
| 2 | Canon morpheme inside with an unrelated or contradicted meaning | 26 |
| 3 | Phonotactic misfit (below the 10th percentile of canon by KN) | 9 of 96 morphemes; classifier AUC 0.72 against a 0.54 baseline |
| 4a | Two invented words for one meaning | 9 pairs |
| 4b | Invented word for a meaning canon or an inferred entry already covers | 8 |
| 4c | Gloss that joins two different senses | 11 |
| 5 | Ukrainian gloss that disagrees or is wrong / implausible part of speech | 6 / 9 |
| 6 | Root field or notes inventing a root, affix or shared etymology | 40 of 49 Swadesh entries, 4 Markov entries, 8 shared-root groups |
| 7 | Swadesh-207 meanings: canon / canon partial / inferred / invented only / unverified only / missing | 18 / 21 / 4 / 51 / 1 / 112 |
| 8 | Real word in a major language, or a confusable minimal pair | 17 / 10 clusters |

### Top 10 flaws, by impact

1. **Seven attested words of unknown meaning still carry guessed glosses.** `delar` "sword/keeper", `aran` "town/settlement", `rath` "shield/missile", `kanesh` "record/magic", `isera` "green", `alon` "eternal/eternity" and `ledel` "dead/servant" are demoted to `canon:false`, but the guesses are still in `translation.en`, so any gloss lookup returns them. They pre-empt the real meanings. `delar`'s own notes say no source supports its gloss. `kanesh` "magic" duplicates canon `arkhana`, `alon` "eternal" duplicates canon `bindel` "forever". `alon` and `ledel` are still `canon_basis: "inferred"`.
2. **Five generated words are identical to attested forms whose meaning is unknown.** `thala` (live) = Shalassian *Thala* in [Thala nar'valas](https://warcraft.wiki.gg/wiki/Shalassian#Untranslated_Shalassian_phrases), and part of the retail Shalassian scrambler word *Nar'thala*. `tora` (protect) and `san` (red) = both words of Valtrois's [Shal'san Tora](https://warcraft.wiki.gg/wiki/Arcanist_Valtrois#On-click), also spelled *Shal'asan torah*. `era` (this) = the Nazja attack line [Era'sazjar!](https://warcraft.wiki.gg/wiki/Quotes_of_Warcraft_III/Neutral_Heroes#Naga_Sea_Witch). `sira` (today/day) = the naga group [Sira'kess](https://warcraft.wiki.gg/wiki/Sira'kess). Each blocks a later gloss of that word.
3. **Ten Swadesh entries give a canon morpheme a meaning the canon contradicts or lacks.** `thas'nor` "root" uses *nor* = "beneath/deep", but canon *nor* is "heavens" (Nordrassil, "Crown of the Heavens"), so by the modifier-first rule it reads "forest-heavens". `lura'thiel` and `lura'sin` call *lura* "water"; canon Darnassian *lura* is "sea". `shalis` "leg" uses *shal-* = "stride" (canon: night/shadow/veil). `talor` "foot" uses *tal-* = "path/walk" (canon: death). `ish'thero` uses *thero* = "study" (canon: student), and by the modifier-first rule it reads as a noun. `al'ore` rests on *anu* = "self". `elara` rests on *el* "light", the morpheme report 1 removed as a mis-segmentation. `thalis` gives *thalas* "hearth". `dorin` adds a singular *-in* to *dorei*, which canon leaves unmarked for number.
4. **All eight duplicate-sense pairs from report 1 are still there, plus a ninth.** The pairs: see (`tala`/`dris'ael`), hear (`selorue`/`thelis'ael`), day (`sir`/`sira`), I (`on`/`al'ore`), not (`la`/`nath`), live (`thala`/`anor'ael`), know (`doras`/`ishari`) and feel (`tana`/`ondore`). The ninth is tree (`fa`/`thas'ore`). Invented words also duplicate canon: `mith` "speak/say" duplicates canon `anaria` "speak/say", and README.md:44 shows it.
5. **26 generated words are one edit from an attested elven form, and they are the most canon-like by the model because they are near-copies.** The worst cases:
   - `doras` is one edit from four forms: *dora* "thanks", *dorah* "valor", *doral* "how" and Shalassian *toras*.
   - `tala` is one edit from six: *tal*, *talah*, *thala*, *vala*, *bala* and *nala*.
   - `dorin` is one edit from *dorini* (Anu'dorini talah, and a scrambler word in all three elven lists).
   - `talor` is one edit from *falor* "chill", and `ethis` from *ethil*, a tier-1 core part.
   - `onar` is one edit from *anar* "by", and `al'ore` from *adore* and *anore*.
   - `ishari` contains the scrambler word *Shari* whole; the lexicon removed `shari` for exactly that reason.

   `dorin`, `doras` and `anor` are the three highest-scoring invented morphemes (93rd–96th percentile of canon), and `tala` and `talor` are at the 83rd.
6. **Canon parts inside invented words read as other words under the modifier-first rule.**
   - `sindor` "gold" is *sin* "blood" + *dor* "land": it reads as "blood-land", or as *Sin'dor(ei)*.
   - `felash` "silver" reads as fel + ash.
   - `tala`, `talu` and `talor` start with *tal* "death".
   - `lelora` "life" and `selorue` "hear" contain *elor* "sleep".
   - `ore` "one" is the ending of six canon words (belore, anore, malanore, manore, denalore, adore).
   - `iel` "love" is also the Swadesh layer's "small/piece" suffix, so `thas'iel` "leaf" parses as "forest-love".
7. **The Swadesh layer runs on an invented morphology that is the main statistical tell.** 40 of its 49 entries give meanings to roots or affixes no source has. 10 body-part words end in a made-up suffix *-is*: 10.4% of invented morphemes end in *-is*, against 1 of 273 attested forms (*dris*). Six verbs use a made-up *-ael* "action" suffix, five of them after an apostrophe; canon apostrophe compounds are nouns. These patterns also create minimal pairs for basic words: `ethis`/`nethis`/`rethis` (hand/tooth/skin), `lashis`/`rashis` (tongue/nose), `shalis`/`thalis`/`thelis` (leg/belly/ear).
8. **The phonotactic fit has not improved since November.** A naive-Bayes classifier still separates the 96 invented morphemes from canon with AUC 0.72 (mean of 20 cross-validation seeds; split-half canon baseline 0.54). 68 of 96 fall below the canon median by the order-4 KN model. The worst are `nubu`, `carth`, `isbab`, `ururann`, `reom`, `lanelot`, `ubelala`, `tabe`, `nu` and `misi`.
9. **Real words and borrowings:**
   - `morn` "black/dark" is Sindarin (Tolkien) for the same sense, and English for "morning".
   - `oris` "mouth" is Latin for "of the mouth". `ossira` "bone" is built on Latin *os, ossis*.
   - `mith` is Sindarin for "grey".
   - `on`, `sir`, `era` and `ore` are common English words, and `lanelot` is one letter from "Lancelot".
   - For the Ukrainian translation: `sir` reads as сир "cheese", `sira` as сіра "grey", and `rashis` as рашист, a wartime pejorative.
   - `dara` is a name from the client's night elf and Skyborne name generator.
10. **The root field invents shared roots, and report 1's bug 16 is still open.** `thala`/`thalas` share the root "thal", `delar`/`dela` share "del", and `malanore` has "mal". New: `aranal` "rise" and `aran` "town" share "aran", `an'da` "papa" and `an` "snow" share "an", `anaria` "speak" and `anar` "by" share "anar", and `shala` "travels" shares "shal" with *shal* "night" and *shal'na* "aunt".

Two systemic problems make the next extension repeat these flaws:
- The repo's generator still has no attempt cap, no start or end states and no novelty check beyond canon words (report 1 bugs 9–11). See [markov.py:16](../../../src/thalassian/phonetics/markov.py), [markov.py:47](../../../src/thalassian/phonetics/markov.py) and [cli/main.py:62](../../../src/thalassian/cli/main.py).
- [test_lexicon_integrity.py](../../../tests/test_lexicon_integrity.py) has no test for duplicate senses or for collisions (report 1, next step 6).

## Report 1's findings: what is fixed and what is open

| Report 1 finding (invented layer) | Now |
|---|---|
| Scrambler-identical words `thera`, `ethala`, `shari`, `osa` | **Fixed:** removed. No generated word is now a whole scrambler word. |
| Canon-duplicating words `elu'shin`, `ishala`, `suran`, `lubala`, `athar`, `thal`; `nu` glossed "white/light" | **Fixed:** removed; `nu` narrowed to "white". `nu` still carries the old "light" evidence (see section 5). |
| `an'dorei` (anu = self, looks like a race name) | **Fixed:** removed. |
| `dris` generated but attested (Elun'dris) | **Fixed:** re-sourced as inferred Darnassian. |
| `el` "peace", `min` "blast", `rutaani` | **Fixed:** removed. |
| 9 unsupported canon entries | **Partly fixed:** demoted to `unverified`, but 5 still show the old guessed gloss (delar, aran, rath, kanesh, isera). |
| Held-back removals `al'ore`, `tala`, `thala`, `sindor`, `dorin` (low) | **Open.** This audit adds evidence and proposes them at high confidence (remove, or regenerate for sindor and dorin). |
| 8 duplicate-sense pairs among generated words | **Open:** all 8. |
| `talor` ~ `falor`, `ethis` ~ `ethil`, `ishala` ~ `shala` | **Open** for talor and ethis; ishala was removed. |
| Classifier AUC 0.72 for the generated words | **Open:** 0.72 again on the 96 remaining morphemes. Removals targeted collisions, not fit. |
| Bug 7: `we→anu`, `they→danu`, `them→dan` | **Open:** [agglutination.py:2-5](../../../src/thalassian/morphology/agglutination.py) (the web copy at HEAD too; web/ was not otherwise read, see Limits). |
| Bug 8: `-i`/`-ei` plural | **Open:** [pluralization.py:1](../../../src/thalassian/morphology/pluralization.py). |
| Bugs 9–11: Markov `while True`, random start, novelty only against canon | **Open:** markov.py:16, markov.py:47, cli/main.py:62. |
| Bug 16: invented shared roots | **Open,** and wider than listed (section 6). |
| Next steps 5–6: regenerate the Swadesh list with collision checks, record `method`, add integrity tests | **Open:** no generated entry has `method`, `confidence` or `evidence`. |

## 1. Collisions

The checks compare each invented word, whole and per part (split at apostrophes, spaces and hyphens), with:
- 780 attested keys from the lexicon's non-invented entries, `corpus.py`, phono.py's list of untranslated phrases and the elven branches of `7-forms.json`;
- the 183 parts of `7-core.json`;
- 1,146 scrambler keys: all 15 WoW Forever lists, the retail Shalassian and Titan lists, and the wiki's Thalassian word parser;
- 1,928 name-generator names, 691 reserved names and 20,333 client tokens;
- Titan and Zandali as controls.

One edit was tested only for keys of four letters or more.

### 1a. Identical to an attested form of unknown meaning

| Invented | Meaning given | Attested form | Source |
|---|---|---|---|
| thala | live/exist | *Thala* nar'valas; *Nar'thala* vas manari (Thalyssra); retail Shalassian scrambler *Nar'thala* | [Shalassian, untranslated](https://warcraft.wiki.gg/wiki/Shalassian#Untranslated_Shalassian_phrases); `.wowf-extract/origins/scramblers.json` |
| tora | protect | Shal'san *Tora* (Valtrois, on-click); *torah* in Shal'asan torah (greeting) | [Arcanist Valtrois](https://warcraft.wiki.gg/wiki/Arcanist_Valtrois#On-click) |
| san | red | Shal'*san* Tora | same |
| era | this | *Era*'sazjar! (Nazja, naga sea witch) | [Quotes of Warcraft III](https://warcraft.wiki.gg/wiki/Quotes_of_Warcraft_III/Neutral_Heroes#Naga_Sea_Witch) |
| sira | today/day | *Sira*'kess (naga group) | [Sira'kess](https://warcraft.wiki.gg/wiki/Sira'kess) |
| al (in al'ore, dris'al) | "the/of", "self" | *Al* diel shala (unglossed part), Al'anath, Al'Aketh | lexicon |
| anor (in anor'ael) | "people" | Tel'*anor* (Suramar place) | [Tel'anor](https://warcraft.wiki.gg/wiki/Tel'anor) |
| ro (in ro'ael, ro'shin) | "air/sky" | *Ro*'minate (ancient name) | 7-forms.json |

### 1b. Attested words that carry a guessed gloss

| Entry | Gloss shown | What the sources show |
|---|---|---|
| delar | sword/keeper | Only the name Quel'Delar, "the Sister Blade". The entry's notes say no source glosses it. |
| aran | town/settlement | From the wiki's Speculation section. Aran also ends *Shorel'aran* "farewell" and Shalassian *Aran'arcana*; it is a tier-1 core part with no gloss. |
| rath | shield/missile (uk щит/ракета) | Thalyssra's spell lines; a retail Shalassian scrambler word. ракета means "rocket". |
| kanesh | record/magic | Thalyssra's recordings; a retail Shalassian scrambler word. "magic" duplicates `arkhana`. |
| isera | green | Ysera's name. Elsewhere only in the scrambler word *Isera'duna* (Thalassian, Darnassian, Shen'dorei lists) and the untranslated *Iseradune banthalos*; one edit from the untranslated *Ishera-do*. |
| alon | eternal/eternity | The untranslated *Anu bala belore alon*, reused untranslated by Aethas in 12.0.1. The notes call the gloss an old fan reading. |
| ledel | dead/servant | The untranslated *Aranal, ledel!*. "servant" has no basis; README.md:37 shows it. |

`anu`, `ashal`, `dash` and `anu'shalla` carry honest glosses. `ashal` "for" does not fit the lexicon's own inferred *Felomin ashal* "Fire consumes!", and its notes do not say so.

### 1c. One edit from an attested elven form (26 generated words)

Canon parts reused on purpose with their canon meaning (thas, lura, sin) are not counted.

| Word | Neighbours (meaning where glossed) |
|---|---|
| doras | dora "thanks", dorah "valor", doral "how", toras (Ash'toras denil) |
| tala | tal "death", talah "true death", thala, vala "through", bala, nala |
| dorin | dorini (Anu'dorini talah "let my will be known"), doren (Tal'doren "the wild home"), morin, orin |
| al'ore | adore "be with you", anore "people", alor (Alor'el), ralore |
| anor'ael | anar "by", anore "people", anora (An'anora), ador, alor, amor, anir, nor |
| tora | torah, toras, tor, dora "thanks", fora, mora |
| thala | thalas "home", shala "travels", thal, thara |
| talor | falor "chill", malor (Zin-Malor), talos, alor |
| ethis | ethil (tier-1 core: Ande'thoras-ethil, Irana'ethil) |
| onar | anar "by", nar (tier-1 core) |
| nath | anath (Al'anath "Frostsoul"), dath, rath, nah, bath |
| dara | dora "thanks", lara/t'lara, dar (Shen'dar), ara, fara |
| elara | alara (Alara'shinu), lara, t'lara |
| thalis | thalas "home", talis (Aru-Talis) |
| ashad | ashal, ashar "duel" |
| fanah | falah (Andu-falah-dor), anah (An'ah) |
| morn | morin (morin'aminor "quiet serenity"), mora |
| talu | tal "death", tanu (Tanu'balah) |
| tana | ana "fare", tanu |
| sorin | morin, orin |
| oris | dris "eye", orin |
| ro'shin (shin) | shan "honored", shen "hidden", shinu, sin "blood" |
| thas'ore (whole) | thalore (Anu dunah thalore) |
| elai | elan (Vashj'elan) |
| neal | nal (tier-1 core) |
| mith | ith (Ith'el kanesh) |

**Calibration:** 16 of the 107 generated entries are also identical to, or within one edit of, a Titan or Zandali form, which unrelated words match by chance. So a single one-edit match on a four-letter word is weak evidence on its own. The candidates weight words with several elven neighbours, or with a meaning clash.

### 1d. Scrambler lists

- **Whole words:** none. Report 1's four were removed.
- **Parts:**
  - *thala* (retail Shalassian *Nar'thala*);
  - *nath* (Orcish *Gul'nath*);
  - *il* (*Il'amare*, Thalassian/Darnassian/Shen'dorei);
  - *ro* (Orcish *Ro'th*), *ish* (Taurahe), *shin* (Kalimag).
- **One edit from an elven list:**
  - `ishari` contains *Shari*; `dorin` ~ *Dorini*; `al'ore` ~ *Adore*; `onar` ~ *Anar*; `astor` ~ *Asto're*.
  - `tala` ~ *Tal*, *Talah*, *Fala*; `talu` ~ *Tal*; `thala` ~ *Ethala*.
  - `nath` ~ *Dath*; `anor'ael` ~ *Anar*, *Ano*; `mith` ~ *Ith*; `tana` ~ *Ana*.

In this client, the Thalassian (10), Darnassian (2) and Shen'dorei (310) lists hold the same words.

### 1e. Names

`dara` is a night elf and Windshaper Skyborne name in NameGen. `tala` is a Tauren name, and `rae` (in `sin'rae`) a night elf name. One edit from an elf or Skyborne name: `llarana` ~ Larana, `alalan` ~ Alaan, `ethis` ~ Ecthis, `dorin` ~ Dorian. `dorin` is also an NPC name in the client's creature cache. No invented word matches a reserved name. No invented word matches any of Blizzard's 267 NamesProfanity patterns.

## 2. Canon morphemes inside invented words

Read with the modifier-first rule: the first part modifies, the last part is the head.

| Word (meaning) | Canon part | Canon meaning | Reads as |
|---|---|---|---|
| sindor (gold) | sin + dor | blood + land, home | "blood-land", Sin'dor(ei) |
| felash (silver) | fel(o) + ash | fire | "fel-ash" |
| tala (see), talu (city), talor (foot) | tal- | death | "death-…" |
| lelora (life), selorue (hear) | elor | sleep | |
| ubelala (darkness), abelu (queen) | bel(ore) | sun | |
| doras (know) | dora, dor | thanks; land | |
| anortha (old), anor'ael (live) | anor(e), nor | people; heavens | |
| thas'nor (root) | nor | heavens | "forest-heavens" |
| shalis (leg) | shal | night/shadow/veil | "night-…" |
| ish'thero (think) | thero | student | "(inner) student", a noun |
| lura'sin (drink) | lura + sin | sea + blood | "sea-blood", a noun |
| lura'thiel (fish) | lura | sea (notes: "water") | |
| ore (one), with al'ore, il'ore, thas'ore | -ore | end of belore, anore, malanore, manore, denalore, adore | false parses such as bel-ore |
| iel (love), with thas'iel, roval'iel | -iel | end of dinoriel "keeper", elu'meniel | thas'iel = "forest-love" |
| orene (remember), silaren (hair) | ren | void | |

## 3. Phonotactic fit

Model: phono.py's order-4 Kneser-Ney character model and naive-Bayes classifier, trained on the same 273 attested forms as report 1. The 96 invented morphemes are those not themselves attested.

| Measure | Value |
|---|---|
| Classifier AUC, invented vs canon (mean of 20 CV seeds) | 0.722 (report 1: 0.72) |
| Split-half canon baseline | 0.538 |
| AUC, Markov words (57) / Swadesh words (40) | 0.729 / 0.740 |
| Canon leave-one-out KN log-prob per character: median / 10th percentile | −1.97 / −3.14 |
| Invented morphemes below the canon median / below the 10th percentile | 68 of 96 (71%) / 9 of 96 |

Worst fit, with the KN nats per character, the KN percentile among canon and the classifier percentile among canon:

| Word | KN | KN pct | NB pct | Why |
|---|---|---|---|---|
| nubu | −4.71 | 1.5 | 3.3 | u…u, Orcish-scrambler-like; 0.4th percentile on the wider 489-form set |
| carth | −4.60 | 1.5 | 6.2 | *rth* |
| isbab | −4.08 | 2.6 | 3.3 | final -b (1/273), *bab* (0) |
| ururann | −3.92 | 3.7 | 4.0 | *uru* (0) |
| reom | −3.53 | 5.9 | 16.1 | hiatus *eo* (0) |
| lanelot | −3.47 | 5.9 | 1.1 | |
| ubelala | −3.46 | 5.9 | 1.8 | initial u- (0), *lala* (0) |
| tabe | −3.25 | 8.4 | 5.5 | |
| nu | −3.23 | 8.4 | 29.3 | |
| misi | −3.13 | 10.3 | 4.4 | |

By classifier alone, the least canon-like are the Swadesh *-is* words: `nethira`, `nethis` and `lashis` are at the 0.0th percentile, `rashis` at 0.4, `rethis` and `rovalin` at 0.7, and `ethis`, `othina`, `rashiel` and `lanelot` at 1.1.

Pattern counts, invented morphemes against the 273 canon forms:
- final *-is*: 10/96 vs 1/273;
- final *-iel*: 5/96 vs 3/273;
- initial *ro-*: 3/96 vs 1/273;
- reduplicated *lala/alal*: 3/96 vs 0;
- initial *u-*: 2/96 vs 0;
- initial *ll-*: 1/96 vs 0.

The most canon-like invented morphemes are the near-copies of section 1c: `dorin` (96th percentile), `doras` (96), `anor` (93), `tala` (83), `talor` (83) and `tora` (77). A filter on fit alone would keep exactly the words that collide.

Robustness: on a wider training set (489 attested parts, adding Nazja, Shalassian and pre-Sundering names), all of the bottom 10 stay in the bottom 20. `ururann` and `ubelala` improve the most.

## 4. Sense problems

**Two invented words for one meaning (9 pairs):**
- see: tala / dris'ael
- hear: selorue / thelis'ael
- day: sir / sira
- I: on / al'ore
- not: la / nath
- live: thala / anor'ael
- know: doras / ishari
- feel: tana / ondore
- tree: fa / thas'ore

The candidates resolve each pair:
- remove tala and keep dris'ael;
- remove selorue and keep thelis'ael;
- remove sira and regenerate sir;
- remove al'ore and regenerate on;
- remove nath and keep la;
- remove thala and regenerate anor'ael;
- remove doras and regenerate ishari;
- narrow tana to "touch" and keep ondore;
- remove fa and keep thas'ore.

**Invented word for a meaning canon or an inferred entry covers (8):**
- `mith` duplicates `anaria` "speak/say".
- `kanesh` "magic" duplicates `arkhana`.
- `delar` "keeper" duplicates `dinoriel`.
- `alon` "eternal" duplicates `bindel` "forever".
- `othina` "wind" duplicates the inferred `banu` and `zephar`.
- `aran` "settlement" duplicates the inferred `naar`.
- `fa`'s Ukrainian "ліс" means forest, which is `thas`.
- `ro'shin` "breathe" ignores canon `endal` "breath".

**Overlaps:**
- `ubelala` "darkness" with `morn` "black/dark" and canon `shal`/`shalla` "shadow".
- `mishar` "power" with `astor` "strong/powerful".
- `tabe` "defender" with `tora` "protect" and canon `dinoriel`.
- `aluta` "enemy" with canon *shindu* ("our enemies") and *ilisar* (held back).
- `onar` "brave" with inferred `dorah` "valor".
- `elandi` "beautiful" with Darnassian *alara* (Alara'shinu).

**Glosses that join two senses (11):** carth "work/do", sira "today/day", isbab "fortress/house", reom "food/bread", fa "tree/wood", iel "love/desire", doras "understand/know", tana "touch/feel", ashad "find/seek", dara "good/pleasant", and mith "speak/say (simple)", whose register note has no canon basis.

## 5. Gloss and part-of-speech quality

**Ukrainian glosses:**
- `rath` uses ракета ("rocket") for "missile".
- `fa` uses ліс ("forest") for "wood".
- `mith` renders "(simple)" as "(просто)", which reads "simply".
- `dara` drops "pleasant" (приємний).
- In canon entries: `vala` "through" has the Ukrainian "через/шлях", which adds "path"; `diel` is an adjective "safe/well" in English but the nouns "безпека/добро" in Ukrainian.

**Part of speech:**
- `anu` is an interjection, but it is always bound in a phrase.
- `dash` is a noun, but it is only part of the greeting *bal'a dash*.
- `la` is an adverb and `nath` a particle, though both negate.
- `fanah` "yes" is an adverb.
- `ore`/`elai` are adjectives while canon `erana` "thousand" is a noun.
- `sira` "today" is a noun.
- `alon` is an adjective glossed "eternal/eternity".
- `ledel` is a noun glossed "dead/servant".
- Eight invented verbs are apostrophe compounds (lura'sin, dris'ael, thelis'ael, rashis'ael, ro'ael, ro'shin, anor'ael, ish'thero). Canon apostrophe compounds are nouns, and canon verbs carry apostrophes only before enclitics (dela'na, vendel'o) or in bash'a and band'or.

**Notes that state false facts:**
- `theli`: "th- onset common in Thalassian question words". The only canon question words are doral and Fandu-dath-belore.
- `loriel`: "-iel common in Thalassian adjectives". Only diel is one.
- `elai`: "-ai marks duality".
- `lura'thiel`: "lura (water)".

**Stale evidence:** `nu` "white" still carries the evidence quotes Anar'alah and Lu'selama, left over from the removed sense "light".

## 6. Root field and etymologies

- **Shared roots with no source** (the root field links entries that no source relates):
  - thalas/thala "thal", dela/delar "del" and malanore "mal" (report 1 bug 16);
  - aranal/aran "aran", an/an'da "an", anar/anaria "anar" and shala/shal/shal'na "shal" (new);
  - sir/sira "sir".
- **Swadesh layer:** 40 of 49 entries give meanings to roots or affixes no source has:
  - *-is* "body part" in 10 words, and *-'ael* "action" in 6;
  - *-iel* "small/piece", *-in* "one who" or singular, *il-* "second person", *ro-* "air", *neth-* "tooth", *ish-* "inner", *rae* "substance", *al* "the/of", *-ara* "state", *-aren*, *-val*, *-ira*, *lur-*, *thel-*, *rash-*, *or-*, *lash-* and *eth-*;
  - 10 of them change a canon meaning (top flaw 3).
- **Markov layer:** four notes claim relations no source makes: `thala` "From Thalas (home)", `san` "related to sin/blood", `on` derived from *'o*, and `mith` "contrast with anaria".

## 7. Swadesh-207 coverage

Full table in `coverage.json` (local).

| Status | Meanings |
|---|---|
| canon | 18: how, child, mother, father, forest, blood, heart, sleep, say, sun, star, sea, earth, sky, snow, fire, night, and |
| canon partial (other part of speech or case, or only inside an unsegmented phrase) | 21 |
| inferred only | 4: I ('o, object only), eye (dris), wind (banu, zephar), with (adore) |
| invented only | 51 |
| unverified only | 1: green (isera) |
| missing | 112 |

- **Where the invented words fall:** 63 meanings have at least one invented word. The Swadesh batch stopped at item 108, "live". Items 1–108 are 40 invented-only and 44 missing; items 109–207 are 11 invented-only and 68 missing.
- **Basic gaps:** *water* is missing, although two Swadesh entries call *lura* "water". So are *he*, *that*, *what*, the numerals three to five, *big*, *moon*, *name* and most verbs of motion and handling.
- **Invented duplicates:** three meanings have an invented word on top of canon or inferred coverage: I, say and wind.

## 8. Other findings

- **Real words:** 17 entries are tagged in the candidates. Top flaw 9 has the strongest; also `neal` (English given name), `astor` (surname), `doras` (Irish "door"), `aluta` (Portuguese "a luta", "the struggle"), `tabe` (Belarusian "to you"), `on` (Russian and Polish "he"), `tora` (Torah), `elara` and `sorin` (given names) and `san` (Ukrainian сан "rank").
- **Minimal pairs among basic words (10 clusters):**
  - tala/talu/tana (see/city/touch), with thala;
  - ethis/nethis/rethis;
  - lashis/rashis;
  - shalis/thalis/thelis;
  - theli/thelis (who/ear);
  - loriel/luriel (long/egg);
  - dorin/sorin (person/seed);
  - dris'al/dris'ael (head/see);
  - ashad/ashal;
  - nath/rath.
- **Docs that showcase invented words:**
  - [README.md:37](../../../README.md) shows *Aranal, ledel!*, README.md:44 shows *Mith'o* and README.md:48 shows *shindara*;
  - [how-to-use-portal.md:23](../../../docs/methodology/how-to-use-portal.md) presents `lura'sin` as the method's example;
  - web/tree.html shows `roval` and `rovalin`.
- **Data labels:** `.wowf-extract/origins/scramblers.json` labels the WoW Forever Shen'dorei list (language 310) as branch "shalassian". 7-forms.json has 419 forms, not 420.

## Limits: what I could not check

1. **Attested coverage is wiki-bound.** Server-side speech is not in the client (BroadcastText has 139 rows), so an invented word may still collide with an elven line that only the server sends. No new pages were fetched (no downloads).
2. **The real-word check is partial.** It covers English (`/usr/share/dict/web2`), Blizzard's 267 NamesProfanity patterns and my own knowledge of Ukrainian, Russian, Latin, Sindarin and a few others. It is not a systematic multilingual dictionary check.
3. **The Ukrainian glosses were checked for meaning, not style.** A native speaker has not reviewed them.
4. **The translator's output was not measured.** parser.py and web/ are being rewritten in another session; I only grepped web/index.html at HEAD for bug 7. The impact of a duplicate gloss on output depends on the new lookup.
5. **No replacement forms were generated.** "regenerate" means: keep the meaning, and draw a new form from the KN generator with the collision checks in audit_vocab.py.

## Reproduce

From the repo root, standard library only, about 2 seconds:

```
python3 -I .wowf-extract/audit/audit_vocab.py
python3 -I .wowf-extract/audit/build_coverage.py
python3 -I .wowf-extract/audit/build_candidates.py
```
