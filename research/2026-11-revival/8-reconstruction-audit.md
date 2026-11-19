# Report 8: Reconstruction audit

Date: 2026-11-18. The owner's request: "audit the existing reconstruction - it was built with an old model. So we need to find flaws first. Then extend the reconstruction".

## Findings

1. **The March grammar was mostly wrong or unlabelled.** Of its 46 checkable claims, 20 are contradicted by the canon and 11 are unlabelled conventions. Only 15 are supported, 6 of them weakly. The canon supports 18 rules it lacked. [grammar.md](../../docs/methodology/grammar.md) is now rewritten from the canon, with a label on every rule.
2. **The invented vocabulary still had the flaws report 1 found, and more.** The audit reviewed 118 entries: 107 generated words, 2 extrapolated and 9 unverified. It made 98 proposals: 9 removals, 42 new forms, 23 fixes and 24 notes.
3. **The fixes are applied.** 12 entries were removed, 27 fields fixed and 37 forms replaced. 4 notes changed nothing, and 28 low-confidence proposals are held back.
4. **The basic vocabulary is now complete.** 114 generated words were added. Before, 112 of the 207 Swadesh meanings had no entry; now none is missing.
5. **The lexicon grew from 314 to 416 entries.** 210 of them are generated. The 151 made in this pass record how: 149 name their generator and seed (147 drawn words with their score, and two compounds rebuilt on a drawn word), and the two object clitics cite grammar section 5.1.
6. **The translator scores a little higher.** On the 39 official Thalassian glosses, exact matches rose from 9 to 10 and the mean F1 from 0.716 to 0.729 (see [Translator score](#translator-score)).

The audit's own write-ups are the appendices: [vocabulary findings](8-audit/vocab-findings.md) and [grammar findings](8-audit/grammar-findings.md). Every action is in [8-candidates.json](8-candidates.json), and the [merge log](merge-log.md#reconstruction-audit-8-candidatesjson) lists what was applied.

## 1. The grammar audit

The audit checked every grammar claim in grammar.md, the morphology code, the web prompts and the README examples ([findings](8-audit/grammar-findings.md)).

| Verdict | Claims |
|---|---|
| Supported | 15 (6 only weakly) |
| Convention with no evidence and no label | 11 |
| Contradicted | 20 |
| Canon rules the grammar lacked | 18 (7 strong or medium) |

The worst flaws:
1. **The doc contradicted itself.** A November note said the main rules were unsupported, but the body still stated them.
2. **Plurals.** The canon marks no number: *dorei* is both "child" and "children". The March grammar had a plural in *-i*, and the code disagreed with the doc.
3. **Pronouns.** *anu* is not "we": it opens wishes. Invented forms such as *'a* "you" and *danu* "they" had no label.
4. **"Elves drop prepositions" is false.** The canon has *anar'* "by", *ashal'* "for" and *vala* "through". Only "of" is never a word.
5. **Tense.** The past suffix *-ash* has no evidence, and its claimed source *ashal* means "for".
6. **Missing rules.** Commands come first, compounds put the modifier first, and "of" phrases put the head first.

**What was fixed.** grammar.md was rewritten in the commit before this report. The engines (parser.py, morphology/, web/) are being rewritten in another session and were not touched.

## 2. The vocabulary audit

| Proposal | High | Medium | Low | All |
|---|---|---|---|---|
| Remove | 7 | 2 | 0 | 9 |
| Regenerate (new form, same meaning) | 11 | 27 | 4 | 42 |
| Fix a field | 7 | 11 | 5 | 23 |
| Note (no change proposed) | 0 | 6 | 18 | 24 |

The worst flaws ([findings](8-audit/vocab-findings.md#top-10-flaws-by-impact)):
1. **Seven attested words of unknown meaning carried guessed glosses**, for example *delar* "sword/keeper" and *ledel* "dead/servant". A lookup returned the guess, and *delar* "keeper" hid canon *dinoriel*.
2. **Five generated words were attested forms of unknown meaning:** *thala*, *tora*, *san*, *era* and *sira*.
3. **Ten Swadesh words gave a canon part a meaning the canon contradicts.** *thas'nor* "root" read "forest-heavens", and *lura'sin* "drink" read "sea-blood".
4. **Nine pairs of invented words shared a meaning**, such as *tala* and *dris'ael* "see".
5. **26 generated words were one letter from an attested form**, such as *talor* ~ *falor* "chill".
6. **The Swadesh words used an invented morphology:** a body-part suffix *-is* in 10 words and a verb suffix *-'ael* in 6.
7. **Some words were real words elsewhere:** *morn* and *mith* (Sindarin), *oris* (Latin), *sir* and *rashis* (Ukrainian readings).

## 3. What was decided

These decisions were taken before the work started:
1. High- and medium-confidence proposals are applied; low ones are held back and listed.
2. Pronouns follow grammar section 5. The generated subject pronouns *on*, *al'ore* and *il'ore* are removed, even where the audit proposed new forms. The object clitics *'a* "you" and *'dan* "him, her, it, them" are added as generated words.
3. Negation keeps *la* and drops *nath*. Grammar section 10, item 7 now says so.
4. *ore* "one" gets a new form, *akus*. Grammar section 10, item 14 now uses it.
5. A new form keeps the entry's meaning, part of speech and glosses, and records its method, confidence and evidence.
6. Every missing Swadesh meaning except "he" (covered by *'dan*) gets one generated word.

These were decided during the work:
1. **mal "your" is not added.** November held it back at low confidence, because its meaning comes from elimination within one phrase, *Elu'meniel mal alann* "May peace calm your heart". That still holds. The in-game line (report 4) confirms the form, not the meaning. The split is also not unique: Thalassian often leaves "your" unsaid (*Anaria shola* "Speak your business"), so *mal* could as well be "calm". It is listed as a held-back add.
2. **isera is removed, and "green" gets a generated word.** The audit proposed a new form for *isera*, but *isera* is an attested Darnassian form (Ysera's name, the scrambler word *Isera'duna*), not a generated word. So the proposal became a removal plus an add.
3. **Two compounds were rebuilt.** The audit's notes on *thas'ore* "tree" and *rashis'ael* "smell" say to rebuild them if their part gets a new form. Both parts did, so they are now *thas'akus* and *azsil'ael*.
4. **Six regenerated words keep one sense.** Their glosses joined two senses (vocabulary findings, section 4): *carth* "work/do" became "work", and likewise *ashad* "find", *iel* "love", *reom* "food", *isbab* "fortress" and *dara* "good".
5. **A fix does not copy the audit's evidence into the entry.** That evidence describes the old value (for example "delar = sword/keeper"), so it stays in 8-candidates.json.

## 4. What changed

| Action | Count | Examples |
|---|---|---|
| Removed | 12 | the 9 audit removals (*sira*, *thala*, *mith*, *doras*, *fa*, *tala*, *selorue*, *al'ore*, *nath*), plus *on*, *il'ore* and *isera* |
| Fixed | 27 fields | *delar*, *aran*, *rath*, *kanesh*, *alon* and *ledel* now say "(unknown; ...)"; five invented shared roots are gone; *la* is a particle; 7 two-sense glosses narrowed |
| New form | 37 | *ore* → *akus* "one", *rashis* → *azsil* "nose", *thas'nor* → *lel* "root", *lura'sin* → *surai* "drink" |
| Added | 114 | 111 Swadesh meanings, "green", *'a* and *'dan* |
| Noted, no change | 4 | *othina*, *aluta*, *thas'iel*, *ro'shin*: decisions nobody has taken yet |
| Held back | 28 | 18 low notes, 5 low fixes, 4 low new forms (*neal*, *tabe*, *oranuer*, *eralleb*) and *mal* |

Each new form's entry records why the old one went: "Replaced carth: a poor fit ('rth' is in no attested form), and an echo of Darnassian karath 'do it' (November 2026 audit)."

## 5. The generator

[scripts/generate_words.py](scripts/generate_words.py) drew every new form. It writes [8-candidates.json](8-candidates.json), and [scripts/apply_audit.py](scripts/apply_audit.py) applies that file.

**Model.** An order-4 interpolated Kneser-Ney character model with start and end symbols, as in [report 1, Method 7](1-review-and-methods.md#method-7-phonotactic-model). It learns from 380 parts of attested elven forms: the lexicon's Thalassian, Darnassian, Shalassian and Skyborne entries that are not generated or unverified, and the elven branches of [7-forms.json](7-forms.json). English surnames inside names (Feathermoon, Shadowsong ...) are left out of the training: with them, the model drew words like *moonel*.

**Seeds.** Each meaning seeds its own random generator, from the SHA-256 of the meaning. The method field names the seed: "seed 16773596909112 (SHA-256 of 'water')".

**Filters.** A sample is rejected if it:
1. uses a rare letter (q, x, c), ends in *-is* or *-ael*, has no vowel, or breaks report 1's phonotactic filter;
2. is an English word or name, a real word in another language (128 listed: 19 the audit flagged, 109 found by reading the output, such as *nos*, *rei* and *shinel*), or a name in the game's name generator;
3. equals an attested elven form or part, or is one letter from one (at four letters or more);
4. contains an attested part with a known meaning (such as *min* of *min'da* "mama"), or any attested part of four letters or more, or sits inside an attested form;
5. equals a scrambler word of any in-game language, or a Titan or Zandali form, or is one letter from one (at four letters or more);
6. equals a lexicon word or another new word, or is one letter from one, when either has four letters or more.

Filters 4 and 6 and the name check go further than the plan. Without them, the model drew pieces of names (*divh* from Medivh, *elunos* from Elune), minimal pairs such as *irar* "leg" and *rar*, and *lem*, a gnome name in the name generator (the audit's reason to drop *dara* and *tala*).

One rule is narrower than the plan. The plan rejected a word one letter from a scrambler word, a Titan or Zandali form, a lexicon word or another new word at any length. The generator counts one letter only from four letters up, as the audit's own checks do (vocabulary findings, section 1). Under the plan's wording, all 37 two- and three-letter words drawn here would fail. Of the model's samples, no two-letter one would pass, and only 9 of 916 three-letter ones would (such as *fyd* and *uvd*), so the plan's function words of 2 to 4 letters would almost all have four.

**Selection.** The length comes first, drawn from the lengths of attested words: 2 to 4 letters for function words (question words, conjunctions, numbers, demonstratives, the two prepositions), 3 to 7 for content words. Then the best-scoring of 10,000 samples of that length wins. Without the length draw, every content word came out at seven letters, because the score per letter rewards length.

**Fit.** The 147 drawn forms sit at a median percentile of 66 among the attested parts, scored leave-one-out (range 18 to 100). A naive-Bayes classifier with report 1's features tells them from the attested parts with an AUC of 0.68 (mean of 20 cross-validation seeds). On the same parts, the 92 older invented morphemes score 0.71, and two random halves of the attested parts 0.50. So the new words fit better, but they are still not indistinguishable.

**Inputs that stay local.** The scrambler lists, the name generator's names, the audit's own files and the system word list are not in git. That is why 8-candidates.json is committed: it is the reviewable input, and the recipe never runs the generator. Run on the lexicon that apply_voice.py leaves, the generator rebuilds 8-candidates.json byte for byte.

## 6. The extension

Swadesh-207 coverage, counted as in the audit's [coverage table](8-audit/vocab-findings.md#7-swadesh-207-coverage):

| Status | Before | After |
|---|---|---|
| Canon | 18 | 18 |
| Canon, partial (another part of speech, or inside an unsegmented phrase) | 21 | 21 |
| Inferred only | 4 | 4 |
| Invented only | 51 | 164 |
| Unverified only | 1 (*isera* "green") | 0 |
| Missing | 112 | 0 |

Some new words:

| Meaning | Word | Meaning | Word |
|---|---|---|---|
| water | *morlath* | one, three, four, five | *akus*, *aen*, *sarr*, *beir* |
| moon | *suramen* | what, where, when | *jaha*, *rin*, *zas* |
| rain | *nazel* | if, because | *enn*, *ae* |
| mountain | *medin* | in, at (proclitics: *elil'thalas*) | *elil'*, *ror'* |
| name | *ethrin* | you, him/her/it/them (clitics) | *'a*, *'dan* |
| year | *theldir* | green, yellow | *thelath*, *urei* |

Every new entry has an English and a Ukrainian gloss and a part of speech. Numbers are adjectives, like *elai* "two" before them.

## Reproduce

From commit 42eb9cf, five commands rebuild lexicon.json and merge-log.md byte for byte (checked on 2026-11-18):

```
git show 42eb9cf:src/thalassian/data/lexicon.json > src/thalassian/data/lexicon.json
python3 research/2026-11-revival/scripts/merge_candidates.py
python3 research/2026-11-revival/scripts/apply_localization.py
python3 research/2026-11-revival/scripts/apply_voice.py
python3 research/2026-11-revival/scripts/apply_audit.py
```

These five give this report's files, with 416 entries. Reports 9 to 11 add a sixth command, `python3 research/2026-11-revival/scripts/apply_wc3_midnight.py`; the docstring of [merge_candidates.py](scripts/merge_candidates.py) has the current recipe.

To redraw 8-candidates.json, run the first four, then `python3 research/2026-11-revival/scripts/generate_words.py`. It needs the local `.wowf-extract/` folder and takes about a minute.

## Translator score

`evalpy.py` translates the 39 official English glosses into Thalassian and compares the output with Blizzard's phrases:

| | Exact | Mean F1 | Lines with untranslated words |
|---|---|---|---|
| Before | 9 | 0.716 | 23% |
| After | 10 | 0.729 | 23% |

The gain comes from one fix. *delar*'s guessed "keeper" used to win the lookup, so "Gate keeper" came out as *Ban delar*. Now *delar* is "(unknown ...)", and the line comes out as *Ban dinoriel*, the canon.

Three probes changed, two for the worse, because the Python engine still uses the March pronoun tables:
- "I" is now left in English. The engine looks up a nominative "I", and *on* is gone; grammar section 5.3 uses *o*, which the engine does not know.
- "the dead rise" gives "[dead] aranal", since *ledel* no longer claims "dead".
- "you" gives *'a*, the new clitic, where it gave *Il'ore*.

The translator fixes merged later on 2026-11-18 use the section 5 forms in both engines: "I rise" is *O aranal*, "you" is *A*, and "the dead rise" is still *[dead] aranal*. Their scores are in [report 1, Method 8](1-review-and-methods.md#method-8-translator-evaluation-on-canon-phrases).

## Limits

1. **The real-word check is partial.** It covers the English word list and names, plus one reading of the output for the major European languages, Ukrainian, Russian, Latin, Greek and a few others. It is not a systematic multilingual check.
2. **The fit figures are optimistic.** The generator learned from the same attested parts the classifier and percentiles use. The best-of-10,000 choice also favours blends of canon pieces: *sharius* "work" is at the 100th percentile.
3. **Short words fit worse.** Most three-letter strings are already attested, English or scrambler words, so few remain to choose from. The 60 three- and four-letter words sit at a median percentile of 31, against 84 for six-letter words. Part of the gap is the measure, which favours longer words.
4. **The Ukrainian glosses were not reviewed by a native speaker.**
5. **59 older generated words keep their forms.** Five had a field fixed (*tana*, *nu*, *la*, *theli*, *lura'thiel*), and 27 carry audit proposals that are held back or undecided. None of them records a method, seed or evidence.
6. **The engines were not updated in this pass.** parser.py, morphology/ and web/ still used the March pronoun tables (*on*, *anu*, *danu*), plurals and dropped prepositions. The translator fixes merged the same day bring both engines to this grammar (see [Translator score](#translator-score)).
7. **Collisions are checked only against what the repo holds.** Server-side elven lines are not in the client, so a new word may still match one.
8. **The held-back items stay open:** *mal*, the four low new forms, the five low fixes and the 18 low notes. They are listed in the [merge log](merge-log.md#reconstruction-audit-8-candidatesjson).
9. **A change to the filters moves many words.** Each meaning takes the best form among its own samples, but the best forms recur from meaning to meaning, so barring one word passes forms down the draw order. Barring seven words late in the work (six that held a three-letter part with a known meaning, such as *min*, and the name *lem*) gave 25 entries a different form.
