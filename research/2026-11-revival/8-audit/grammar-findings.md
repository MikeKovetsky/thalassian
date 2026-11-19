# Grammar audit: the March 2026 Thalassian grammar against the canon

> **Appendix to [report 8](../8-reconstruction-audit.md).** A copy of `grammar-findings.md` from the local, gitignored audit folder `.wowf-extract/audit/`, as the audit wrote it on 2026-11-18. Only its links were changed, and the English of one lyric line was dropped: links into the repo now resolve from this folder, and the files that stay local are named without a link. What the audit proposed was applied through [8-candidates.json](../8-candidates.json); the [merge log](../merge-log.md#reconstruction-audit-8-candidatesjson) lists the result.

Date: 2026-11-18. Read-only audit: nothing in the repo was changed. The proposed rewrite is `grammar-draft.md` (local); it became [docs/methodology/grammar.md](../../../docs/methodology/grammar.md).

**What was audited.** Every grammar claim in:
- `docs/methodology/grammar.md` (main, 43 lines);
- `src/thalassian/morphology/agglutination.py` and `src/thalassian/morphology/pluralization.py`;
- the Pure LLM and Hybrid prompts in `web/index.html:769-807`, with the pronoun tables at `web/index.html:627` and `:668-673`;
- the worked examples in `README.md:32-48`, including the song translation.

Also noted, because they repeat or add grammar: `web/tree.html` and the lexicon's notes on generated words.

**Canon used.** The Blizzard-glossed phrases in `research/2026-11-revival/scripts/corpus.py`, the Shalassian, Nazja and pre-Sundering forms in `research/2026-11-revival/7-forms.json`, report 7's shared core, the lexicon's `canon_basis`, and reports 3 and 5 (Skyborne). The glosses were re-checked on 2026-11-18 against the raw wiki pages ([Thalassian primer](https://warcraft.wiki.gg/wiki/Thalassian#Thalassian_primer_(official_translations)), [Encyclopedia: Thalassian](https://warcraft.wiki.gg/wiki/The_Warcraft_Encyclopedia/Thalassian), [Darnassian primer](https://warcraft.wiki.gg/wiki/Darnassian#Darnassian_primer_(official_translations)), [Shalassian primer](https://warcraft.wiki.gg/wiki/Shalassian#Shalassian_primer_(official_translations))). Every gloss quoted below matched.

**Translator branch.** The rules that `translator-fixes` encodes were checked by running its `web/translator.js` and `parser.py` on test sentences, from copies in the scratchpad. The branch was not checked out.

**Strength scale.**
- **Strong:** 3 or more independent glossed attestations and no counterexample.
- **Medium:** 2 glossed attestations, or 1 glossed plus parallel unglossed forms.
- **Weak:** 1 attestation, or an ambiguous segmentation.

## Verdicts in numbers

The built grammar makes **46 checkable claims** (the inventory below):

| Verdict | Count | Meaning |
|---|---|---|
| Supported | 15 | The canon backs it (6 of the 15 only weakly) |
| Convention, no evidence | 11 | Fine for a conlang, but none is labelled a convention |
| Contradicted | 20 | Canon counterexamples, a factual error, or an example that breaks the rules or the lexicon |

The canon also supports **18 rules the built grammar lacks** (see "Missing rules"). Seven of them are strong or medium.

## Findings, ranked by impact

### 1. The doc contradicts itself: the November note says the main rules are unsupported, but the body still states them

`grammar.md:5-10` (added in November) says strict SVO is not established, prepositions exist, number is unmarked and the tense markers are inventions. The body below it (`grammar.md:12-43`) still states each of these as a rule: SVO (§1), strict word order (§2), `-ash`/`ru-` (§3), `-i`/`-ei` plurals (§4) and dropped prepositions (§5). The same rules are repeated as plain fact in:
- the Pure LLM prompt ("SVO word order, drop prepositions", `web/index.html:780`);
- the README (`README.md:32`, `:57`, `:59`, `:73`);
- `web/tree.html:121` and `:137`.

A reader, or the LLM, gets the unsupported rules and none of the supported ones: the prompt says nothing about imperatives, compounds, genitives or *anar'*. Report 1 found these problems; they were added as a note, and the rules themselves were left in place. **Status:** open on `main`. `translator-fixes` rewrites only the prepositions paragraph of §5 and adds a compounds paragraph to §6.

### 2. Plurals: the canon marks no number, and the code and the doc disagree with each other

Built grammar (`grammar.md:26-29`): plural `-i` or `-ei` ("dore -> dorei"), with *alar -> alari* and *sindo -> sindorei*, *shola -> sholai*.

**Canon (strong): number is unmarked.**
- *dorei* is singular in *Belore'dorei* "Child of the Sun", which also addresses one new ranger lord in *Belono sil'aru, belore'dorei*. In Skyborne text it is singular too: "I am shen'dorei" (report 3, line 257).
- *dorei* is plural in *Sin'dorei* "children of the blood" and *Quel'dorei* "children of noble birth".
- No form *dore* "child" is attested.
- Glossed English plurals carry no `-i`: *sil'aru* "your burdens", Darnassian *thoras* "troubles" (*Ande'thoras-ethil*), *ilisar* "enemies" (*Tor ilisar'thera'nal*), *kal* "stars" (*Kaldorei*).

**The examples are wrong on their own terms.**
- *sindo* is not a word: *Sin'dorei* is *sin* "blood" + *dorei*.
- *sindo -> sindorei* does not follow Rule 2.

**The code disagrees with the doc** (`pluralization.py`, verified by running it):

| Input | Doc | Code |
|---|---|---|
| *shola* | sholai | sholei |
| *sindo* | sindorei | sindei |
| *dorei* | (not given) | doreii |

**The plural creates canon words.**
- *dora* "thanks" becomes *dorei* "children".
- *dorin* "person" becomes *dorini*, which is attested in *Anu'dorini Talah*.

**`-i` is attested, but on names, with the sense "of X" or "from X":**
- *Zin-Azshari* "the glory of Azshara";
- *Suramari* "Suramarian" (`7-forms.json`);
- Skyborne *Rohashi* "of Rohash" and *zephrali* "of Zephras" (reports 3 and 5).

**Effect on output.** The Python engine still pluralizes, on `main` and on the branch: "The rangers guide us" gives *Alari dela'na*, "travels" gives *Shalei*, "Our hearts" gives *Na alanni*. The branch's web engine does not pluralize: it gives *Alar dela'na*.

**Fix.** Number is unmarked, as a canon rule. Delete the plural rule, or keep it only as a labelled invention that collides with nothing. **Status:** report 1's bug 8 is still open.

### 3. Pronouns: one canon form is misused, and four invented forms are unlabelled

Built grammar:
- `grammar.md:33-37`: *o* = me/I, *a* = you, *na* = us/we, and pronouns are never standalone when a verb is present.
- `agglutination.py:1-9` and `web/index.html:627,668-673`: also we = *anu*, they = *danu*, them = *dan*.

| Claim | Verdict | Evidence |
|---|---|---|
| *'na* = us | Supported | *Anu belore dela'na* "The sun guides us" |
| *'o* = me | Supported (weak) | *Vendel'o eranu* "Help me forget" |
| *'o* = I (a subject) | No evidence | No subject pronoun is attached to a verb anywhere in the canon |
| *'a* = you | No evidence | See the second-person forms below |
| *na* = we | No evidence | *na* is only ever glossed "us" or "our" |
| *anu* = we | Contradicted | See below |
| *danu* = they, *dan* = them | No evidence | "They're breaking through" is *Shindu fallah na*, with no *danu* |
| Pronouns are never standalone | Contradicted | See below |

**The canon's second-person forms** are all other words:
- Thalassian *mal* "your" (*Elu'meniel mal alann* "May peace calm your heart"; inferred by elimination);
- Darnassian *alah* "to you" and *dal* "your" (*Ishnu-alah*, *Ishnu-dal-dieb*);
- Shalassian *isil* "upon you";
- *adore* "be with you".

*Bash'a* "taste" and *Bal'a* "greetings" end in *'a*, but their glosses do not split off a "you".

**Why *anu* = we is contradicted.**
- *anu* opens *Anu belore dela'na*, where "us" is already *'na* and the gloss has no "we".
- In Darnassian it opens jussives: *Anu'dorini Talah* "Let my will be known", and the untranslated *Anu'dora!*, *Anu dorini ash'ka*.
- The only "we" reading is a Canticle of Sacrifice lyric line whose English has no cited source.

**Why "never standalone" is contradicted.**
- *na* stands free after the verb in *Shindu fallah na*. Blizzard's garble list writes it *Shindu'fallah'na*, so the spelling varies.
- *isil* (*Erana-dora isil*) and *mal* (*Elu'meniel mal alann*) are free words.

**The two pronoun tables are inconsistent.**
- Ukrainian *ми* "we" maps to *na*, but English "we" maps to *anu*.
- Ukrainian *вони* "they" maps to *dan*, but English "they" maps to *danu*.

**Effect on output.** Both engines produce *Aria dela'dan* for "We guide them": *aria* is Darnassian "we face". They produce *On dela'a* for "I guide you".

**Status:** report 1's bug 7 is open on `main` and on `translator-fixes`.

### 4. "Elves generally drop prepositions" is contradicted; only "of" is really absent

Built grammar: `grammar.md:38`, the Pure LLM prompt ("drop prepositions") and `README.md:32`.

**Canon has prepositions:**
- *anar'* "by", in 3 glosses;
- *ashal'* "for" (*Selama ashal'anore*; inferred);
- Shalassian *vala* "through";
- Darnassian *bessae* "from the";
- an agentive "by" in *Ama noral'arkhana* "Saved by magic".

**What holds is narrower.** No glossed phrase has a word for "of", and "of" phrases are built by juxtaposition or compounding in about 15 glosses (strong). "for" is not dropped. For "to" there is no evidence either way.

The doc's own example, *Selama ashal'anore*, keeps "for"; the November line under it admits this.

**Status:** open on `main`. `translator-fixes` rewrites the paragraph: dropping is labelled the engine's convention, *anar'* is "by" and *rea* is "and".

### 5. Tense: `-ash` has no evidence, its etymology is wrong, and it clashes with canon *ash*; `ru-` is a Shalassian loan

**`-ash` past** (`grammar.md:23`, *dela'ash*): no glossed form has a past marker.
- The one past participle in the canon, *ama* "saved" (*Ama noral'arkhana*), has no `-ash`.
- The stated source is wrong: *ashal* "complete/great" is unsupported. The canon reads *ashal* as "for" (*Selama ashal'anore*), and the zhTW gloss of *Felomin ashal* is "Fire consumes".
- *ash* is attested clause-initially, in commands and war cries: Darnassian *Ash karath* "Do it", *Ash'al theradas*, *Ash'thero danador*; Shalassian *Ash'thoras denil*; Nazja *Ash'thero sanguine*.

**`ru-` future** (`grammar.md:24`, *ru'dela*): weak support, from Shalassian only.
- For it: *Ru shanna shal'dorei* "The nightborne will survive". The wiki also lists the spelling *Ru-shanna*, which fits a bound pre-verbal marker.
- Against it: Darnassian *Ru shallora enudoril* is a present tense, "I anoint these caretakers of the wild".
- No Thalassian form is attested, and no source spells it with an apostrophe.

Neither marker is implemented by any engine (checked in `parser.py` and `web/index.html` on `main`, and in `parser.py` and `web/translator.js` on `translator-fixes`), so they exist only in the doc. The November note calls both "inventions". That is right for `-ash`; `ru` is better described as a weakly attested Shalassian loan.

### 6. Missing genitive rule: compounds for names, head-first free genitives in speech

`grammar.md` has no rule for "X of Y". The canon has two patterns.

**Compounds put the modifier first and the head last** (strong; 10 of 10 Thalassian). They are names, titles and fixed epithets: *Sin'dorei*, *Thas'alah* (a bow), *Quel'Thalas* (a land), *Ban'dinoriel* (a shield), *Lu'selama*.

**Free genitives put the head first, with no "of"** (medium). They occur in running speech:
- *Anar'alah belore* "by the light of the sun": *alah* light + *belore* sun;
- *Anar'endal dracon* "by the breath of the dragon";
- *Bash'a no falor talah* "taste the chill of true death";
- the lyric *ann'da* + *anore* "father of our people".

Report 1 cited only *falor talah*, plus the lyric line; *alah belore* and *endal dracon* are two more official examples. The same head noun takes both patterns: "light" is *Thas'alah* as the name of a bow, but *alah belore* in an oath.

**Branch conflict.** `translator-fixes` makes every two-noun "X of the Y" a compound:
- "The light of the sun" gives *Belore'alah* (canon *alah belore*);
- "The breath of the dragon" gives *Dracon'endal* (canon *endal dracon*);
- "The chill of death" gives *Talah'falor* (canon *falor talah*).

It reaches the canon outputs only through a special case after "by".

### 7. The README song translation breaks both the rules and the lexicon

`README.md:44-48`. The English lyric lines are not repeated here; each line is named by its Thalassian.

| README line | Problems |
|---|---|
| *Mith'o dalah'shola* | *dalah* is not in the lexicon. *mith* is generated. *'o* is used as the subject "I", which is unattested. |
| *On dal'thielin* | *thielin* is not in the lexicon. *dal* is Darnassian "to your", while the Thalassian canon has *mal* "your". *dal'* as a proclitic is unattested. The back-gloss, "little one", is not the English line's word. |
| *Ethala shindu doren* | *ethala* is no longer in the lexicon: it was a generated word identical to a Blizzard scrambler word (report 1). *shindu* means "failing"; "break through" is *fallah*. *doren* is not in the lexicon and is a part of Darnassian *Tal'doren* "the wild home". |
| *Ari'a* | *ari* is not in the lexicon, and *'a* = you is unattested. It is one apostrophe away from Darnassian *Aria* "We face". |
| *Dorei'a menta rea shindara?* | *dorei* is a noun ("children") used as the verb "born". *menta* is not in the lexicon. *rea* means "and" but is used for "or". *shindara* is generated ("fear"), and fear is not what the English line says. |

None of the five lines round-trips through the branch's reverse translator. For example, *Ari'a* gives "[ari] you".

### 8. The flagship example drops the canon's first word

`grammar.md:15` and `README.md:35` give "The sun guides us" as *Belore dela'na*, and the README labels it "(Canon match)". Blizzard's line is ***Anu** belore dela'na* ([Encyclopedia](https://warcraft.wiki.gg/wiki/The_Warcraft_Encyclopedia/Thalassian)). SVO does not account for *anu*, which is why the example drops it. `web/tree.html:137-156` draws the same three-word tree.

**Status:** fixed in the README on `translator-fixes`; `grammar.md` §1 and `tree.html` are unchanged on both branches.

### 9. Clause order is over-claimed, and four supported ordering rules are missing

Built grammar: "standard SVO ... observable in most of Blizzard's translated phrases" (`grammar.md:13-14`) and "strict word order" (`:18`).

**Canon.**
- Only 2 of the 39 official Thalassian glosses have both an overt subject and a finite verb: *Anu belore dela'na* and *Shindu fallah na*. Both are subject before verb, which is weak support for SV.
- Verb before object is strong: *Anaria shola*, *Bash'a no falor talah*, *Belono sil'aru*, *Vendel'o eranu*, *Tal anu'men no Sin'dorei*.
- Shalassian *Ru shanna shal'dorei* is verb before subject.
- Darnassian *Shu dalas na* "Heavy are our hearts" puts the predicate first.

**Missing from the grammar, all supported** (see "Missing rules"):
- imperatives first, with a bare verb (strong);
- question words first (medium);
- the vocative last (medium);
- clause-initial *anu* in wishes (weak).

### 10. Possessives are missing, and the engines use the wrong dialect for "your"

The grammar says nothing about possessives.

**Canon.**
- Thalassian *mal* "your" comes before the noun: *mal alann* "your heart".
- Darnassian *dal* "your" also comes before: *Ishnu-dal-dieb*.
- "our" is *na* after the noun: Darnassian *Shu dalas na* "Heavy are our hearts"; Thalassian *Shindu fallah na*, in its Lament gloss "Our enemies are breaking through".

**The lexicon lacks *mal*.** It was held back in the November merge (`merge-log.md:261`).

**Effect on output.**
- "Your heart" gives Darnassian *Dal alann* on both branches, though the canon Thalassian is *mal alann*.
- "Our hearts" gives *Na alann(i)*: *na* before the noun, the opposite of the canon.

### 11. "by" is not always *anar'*

`translator-fixes` turns every "by X" into *anar'X* (its `grammar.md` §5). In the canon, *anar'* is the "by" of oaths and invocations: 3 glosses, plus 6 untranslated exclamations of the same shape (*Anar'anel belore*, *Anar'alash denal*, *Anar'dalel*, *Anar'sin arkhana*, *Anar'endal belore*, Shalassian *Anar'amenos*).

The agent of a passive is not *anar'*: *Ama noral'arkhana* is "Saved by magic". Word by word, the branch gives *[Saved] anar'arkhana*. The unattributed motto *Esarus thar no'darador* "By blood and honor we serve" (lexicon, from the WoW Forever client) has no *anar'* either.

### 12. *no* before a definite object is dropped by the engines

*no* occurs in both Thalassian phrases where a verb takes a noun object with "the":
- *Bash'a **no** falor talah* "Taste **the** chill of true death";
- *Tal anu'men **no** Sin'dorei* "Death to all who oppose **the** children of the blood".

It is absent before possessed objects (*Anaria shola* "Speak your business", *Belono sil'aru* "Shoulder your burdens"). The evidence is weak (2 cases), but it is consistent. Report 1 proposed *no* as a particle and held it back (`merge-log.md:263`). Report 6 says "no article on record".

Both engines drop "the", so word by word they lose the canon *no*. The branch's test `test_translator_canon.py:72-73` locks in *Bash'a falor [true] talah*.

### 13. Smaller errors and unlabelled inventions in the doc

1. **The Esperanto comparison is false.** `grammar.md:18` says elvish has no cases, "similar to English or Esperanto". Esperanto has an accusative case (*-n*), and English is not agglutinative.
2. **"Agglutination" is not the core feature.** `grammar.md:32`, `README.md:32` and `tree.html:121` say so. The canon shows clitics joined by apostrophes, plus compounds; no attested word stacks two grammatical affixes whose meanings are known. As a typological label, it is a convention.
3. **"Adjectives follow the noun in poetic contexts"** (`grammar.md:42`) has no evidence. The only head-first compound is Darnassian *Thero'shan* "honored student", a title, not poetry.
4. **The "Rise, dead ones!" example is mislabelled.** `README.md:37` calls *Aranal, ledel!* "Extrapolated from Prince Keleseth". It is Keleseth's own untranslated line ([wiki](https://warcraft.wiki.gg/wiki/Thalassian#Untranslated_words_or_phrases)); only the English is the project's guess (*ledel* is `inferred`). The branch README turns it into *Aranal, ledel ore!*, adding the generated *ore* to Blizzard's line.
5. **The Hybrid prompt's sound rule overstates the softness.** "lots of vowels, soft consonants l, r, s, sh, th" (`web/index.html:799`) holds as a tendency: *l*, *r*, *s* are 19.1% of letters in Blizzard's elvish garble lists (report 6). But the canon also has *kh*, *k*, *d*, *b*, *m* (*arkhana*, *karath*, *dorei*, *belore*, *minn'da*).

### 14. Grammar hidden outside the grammar doc

These rules are not in `grammar.md`, so the audit would miss them if it read only the doc:
- **The lexicon's generated words carry their own morphology.** *dorin* "person" uses a singular `-in`, while the grammar has a plural `-i`. *rovalin* uses `-in` "one who". *il'ore* has an *il-* second-person prefix. *shindara* has an `-ara` state suffix. *al'ore* rests on "anu = self", an invented etymology already flagged by report 1.
- **One lexicon note is contradicted by the canon.** *theli* "who" says "th- onset common in Thalassian question words". The attested question words are *doral* "how" and Darnassian *fandu* "who".
- **`web/tree.html` adds more.** It splits *bash'a* into *bash* + *'a* "Agglutinated Subject: you", which the gloss "Taste" does not support. It leaves out the canon *no* and shows a "[dropped] of" that the phrase does not contain.

### 15. Darnassian forms leak into Thalassian output unlabelled

Blizzard's encyclopedia warns that addressing a high elf or blood elf with a Darnassian-specific word or phrase can be offensive ([Encyclopedia: Thalassian](https://warcraft.wiki.gg/wiki/The_Warcraft_Encyclopedia/Thalassian)). The engines nevertheless output, with no dialect label:
- *dal* "your";
- *aria* for "we";
- *bessae* for "from" (on the branch);
- *adore*, *alah* "to you".

The draft labels each such form as a loan.

## Rule-by-rule inventory (46 claims)

Sources: G = `grammar.md` (main), A = `agglutination.py`, P = `pluralization.py`, W = `web/index.html` prompts and tables, R = `README.md`.

| # | Claim | Where | Verdict | Evidence |
|---|---|---|---|---|
| R01 | The verb precedes its object | G§1, W, R | Supported (strong) | *Anaria shola*; *Bash'a no falor talah*; *Belono sil'aru*; *Vendel'o eranu*; *Tal anu'men no Sin'dorei*; Darnassian *Ash karath* |
| R02 | The subject precedes the verb | G§1, W | Supported (weak, Thalassian only) | *Anu belore dela'na*; *Shindu fallah na*. Against it: Shalassian *Ru shanna shal'dorei* (verb-subject) |
| R03 | SVO is "observable in most of Blizzard's translated phrases" | G:14 | Contradicted | 2 of 39 official Thalassian glosses have a subject and a verb; at least 6 are imperatives |
| R04 | Example "The sun guides us -> SVO" (*Belore dela'na*) | G:15 | Contradicted | The canon is *Anu belore dela'na* |
| R05 | "Relies on a strict word order" | G:18 | Contradicted | Shalassian verb-subject; Darnassian predicate-first; vocatives at the end |
| R06 | No noun cases | G§2 | Supported (medium) | *belore* is unchanged as subject (*Anu belore dela'na*), genitive (*alah belore*) and compound modifier (*Belore'dorei*); *Sin'dorei* is unchanged as an object |
| R07 | "Similar to English or Esperanto" | G:18 | Contradicted (factual) | Esperanto has an accusative *-n* |
| R08 | Agglutination is "the core feature" | G:32, R:32 | Convention | The canon shows clitics and compounds, with no stacked affixes |
| R09 | No conjugation tables (no agreement) | G:21 | Supported (weak) | *dela* "guides" (3rd singular) and *fallah* "are breaking" (3rd plural) carry no person marking |
| R10 | Present tense = bare root | G:22 | Supported (weak) | *dela'na* "guides us"; *Shindu fallah na* |
| R11 | Past tense = suffix `-ash` (*dela'ash*) | G:23 | Convention | No attestation; *ama* "saved" has none; clashes with clause-initial *ash* |
| R12 | `-ash` comes from *ashal* "complete/great" | G:23 | Contradicted | *ashal* = "for" (*Selama ashal'anore*); zhTW *Felomin ashal* "Fire consumes" |
| R13 | Future = prefix `ru-` (*ru'dela*) | G:24 | Convention (Shalassian loan, weak) | For: Shalassian *Ru shanna* / *Ru-shanna*. Against: Darnassian *Ru shallora* (present). No Thalassian form |
| R14 | Plurals take `-i` or `-ei` (*dore -> dorei*) | G:27 | Contradicted | *dorei* is child and children; no *dore* |
| R15 | Rule 1: a consonant takes `-i` (*alar -> alari*) | G:28 | Contradicted | No plural marking is attested: *sil'aru*, *thoras*, *ilisar*, *kal* |
| R16 | Rule 2: a vowel takes `-i` or lengthens (*sindo -> sindorei*, *shola -> sholai*) | G:29 | Contradicted | *sindo* is not a word; the example breaks the rule |
| R17 | `apply_plural`: `-e` +i; `-a/-o/-u` -> `-ei`; else +i | P | Contradicted | Disagrees with R16 (*sholei*, *sindei*, *doreii*); makes *dora* -> *dorei* |
| R18 | Pronouns are never standalone when a verb is present | G:33 | Contradicted | *Shindu fallah na*; *Erana-dora isil*; *mal alann* |
| R19 | Object pronouns follow the verb | G:33 | Supported (medium) | *dela'na*; *Vendel'o* |
| R20 | ...attached with an apostrophe | G:33, W:780 | Supported (weak; spelling varies) | *dela'na*, *Vendel'o*; but *fallah na* (written *Shindu'fallah'na* in Blizzard's garble list) |
| R21 | *'o* = me | G:34, A, W | Supported (weak) | *Vendel'o eranu* |
| R22 | *'o* = I (subject) | G:34, A, W:780 | Convention | No subject clitic is attested |
| R23 | *'a* = you | G:35, A, W | Convention | Canon second person: *mal*, *alah*, *dal*, *isil*, *adore* |
| R24 | *'na* = us | G:36, A, W | Supported | *dela'na* |
| R25 | *na* = we | G:36 | Convention | *na* is only glossed "us" or "our" |
| R26 | we = *anu* | A, W:627,669 | Contradicted | *Anu belore dela'na* (no "we"); Darnassian *Anu'dorini Talah* "Let my will be known" |
| R27 | they = *danu* | A, W | Convention | "They're breaking through" = *Shindu fallah na* |
| R28 | them = *dan* | A, W | Convention | No attestation |
| R29 | Example *dela'na* "guides us" | G:37 | Supported | Encyclopedia |
| R30 | Elves generally drop prepositions | G:38, W:780, R:32 | Contradicted | *anar'*, *ashal'*, *vala*, *bessae*, *noral'* |
| R31 | "of" is not a word (juxtaposition or compounding) | G:38 | Supported (strong) | About 15 glossed genitives have no "of" word |
| R32 | "for" is dropped | G:38 | Contradicted | *ashal'anore* |
| R33 | "to" is dropped | G:38 | Convention | No clear case either way |
| R34 | *Selama ashal'anore* given as an example of dropping | G:39 | Contradicted | It keeps *ashal* "for" |
| R35 | Adjective before noun | G§6, W, R:32 | Supported (medium) | *Al diel shala*; *Shindu sin'dorei*; *Quel'Thalas* |
| R36 | Adjective after noun "in poetic contexts" | G:42 | Convention | No case; *Thero'shan* is a title |
| R37 | Compounds are Adjective + Noun | G:43 | Supported (too narrow) | Noun modifiers also come first: *Sin'dorei*, *Thas'alah* |
| R38 | Hybrid prompt: many vowels and soft *l r s sh th* | W:799 | Supported as a tendency (weak) | *l r s* are 19.1% of letters in the garble lists; but *arkhana*, *karath* |
| R39 | README: *Belore dela'na* "(Canon match)" | R:35 | Contradicted | The canon is *Anu belore dela'na* |
| R40 | README: *Aranal, ledel!* "Extrapolated" | R:37 | Convention, mislabelled | Blizzard's line; the English is the project's guess |
| R41 | README: *Selama ashal'anore* "(Canon match)" | R:39 | Supported | Encyclopedia; BroadcastText 309952 |
| R42 | Song line 1: *Mith'o dalah'shola* | R:44 | Contradicted | *dalah* missing; subject *'o* |
| R43 | Song line 2: *On dal'thielin* | R:45 | Contradicted | *thielin* missing; Darnassian *dal* |
| R44 | Song line 3: *Ethala shindu doren* | R:46 | Contradicted | *ethala* removed; *shindu* is not "break"; *doren* missing |
| R45 | Song line 4: *Ari'a* | R:47 | Contradicted | *ari* missing; *'a* unattested |
| R46 | Song line 5: *Dorei'a menta rea shindara?* | R:48 | Contradicted | *dorei* is a noun; *menta* missing; *rea* is "and" |

## Missing rules the canon supports

| # | Rule | Evidence | Strength | In the built grammar? |
|---|---|---|---|---|
| M01 | Apostrophe compounds put the modifier first and the head last | 10 of 10 Thalassian (*Quel'Thalas*, *Thas'alah*, *Sin'dorei*, *Ren'dorei*, *Belore'dorei*, *Felo'melorn*, *Ban'dinoriel*, *Lu'selama*...); 13 Darnassian and Shalassian; one exception, Darnassian *Thero'shan* | Strong | Only in the note; §6 says "Adjective + Noun" |
| M02 | Free genitives put the head first; compounds are for names, titles and epithets | *alah belore*, *endal dracon*, *falor talah* (official); *ann'da* + *anore* (lyric); Darnassian *Zin-Azshari* is head first | Medium | The note gives one example; no rule |
| M03 | *anar'* is the proclitic "by" of oaths and invocations | *Anar'alah*, *Anar'alah belore*, *Anar'endal dracon* (glossed); 6 untranslated exclamations of the same shape. Not the agent of a passive: *Ama noral'arkhana* | Strong (oaths) | Only the note's "prepositions exist" |
| M04 | *ashal'* is a proclitic "for" | *Selama ashal'anore*, by elimination; the Canticle pairing (unsourced) agrees | Weak | No (§3 misuses it) |
| M05 | Imperatives come first, as a bare verb | *Anaria shola*, *Bash'a...*, *Vendel'o eranu*, *Belono sil'aru*, *Aranal*, *Elor bindel...*; zhTW *Band'or shorel'aran*, *Balamore shanal*; Darnassian *Ash karath*, *Bandu thoribas* | Strong | Only the note |
| M06 | Object enclitics *'na* (us) and *'o* (me) | *dela'na*; *Vendel'o* | Medium | Yes, mixed with invented forms |
| M07 | Possessives: *mal* "your" before the noun; *na* "our" after it | *mal alann*; Darnassian *dal-dieb*, *dalas na*; Lament *Shindu fallah na* | Weak | No |
| M08 | Number is unmarked | *dorei* singular and plural; Skyborne "I am shen'dorei"; *sil'aru*, *thoras*, *ilisar*, *kal* | Strong | Only the note; §4 says the opposite |
| M09 | Shalassian puts the verb before the subject | *Ru shanna shal'dorei* (also spelled *Ru-shanna*) | Weak (1 phrase) | Only the note |
| M10 | Blessing formulas: X-*adore* "X be with you" and X-*alah* "X to you" (Darnassian family) | *Elune-adore*, *Ishnu-alah* (glossed); Shalassian *An'ratha adore*, Nazja *Zin-Azshari adore*, Skyborne *banu adora* and *banu alah* (unglossed, same slots) | Medium for Darnassian; none in Thalassian | No |
| M11 | Question words come first | *Doral ana'diel?* "How fare you?"; Darnassian *Fandu-dath-belore?* "Who goes there?" | Medium | No |
| M12 | The vocative comes last, after a comma | *Bal'a dash, malanore*; *Belono sil'aru, belore'dorei*; *Selama ashal'anore, Blood Knight* (BroadcastText 309952) | Medium | No |
| M13 | Wishes and blessings open with a particle; *anu* is the Thalassian candidate | *Anu belore dela'na*; *Elu'meniel mal alann* "May peace..."; untranslated *Anu bala belore alon*. Darnassian *Anu'dorini Talah* "Let...", *Andu-falah-dor* "Let...", *Ande'thoras-ethil* "May..." | Weak (Thalassian), medium (Darnassian) | No (A uses *anu* as "we") |
| M14 | *no* before a definite noun object | *Bash'a no falor talah*; *Tal anu'men no Sin'dorei*; absent before "your" objects | Weak | No |
| M15 | Kinship *'da*; Darnassian honorific *'do* | *Ann'da*, *Minn'da*; Darnassian *An'da*, *Min'da*; *Shan'do*, *Nahlen'do*, *Minn'do* | Medium | No |
| M16 | *-i* on a name means "of X" or "from X" | *Zin-Azshari* "the glory of Azshara"; *Suramari*; Skyborne *Rohashi*, *zephrali* | Weak to medium | No (the plural rule uses *-i* for something else) |
| M17 | No copula | Darnassian *Shu dalas na* "Heavy are our hearts"; no Thalassian copular gloss | Weak | No |
| M18 | *rea* "and" joins words or clauses of the same kind | "Rea = And" (Loreology tweet; the wiki adds the usage note) | Medium | No on `main`; added on the branch |

## Report 1: what is still open

| Report 1 item | Status on `main` | Status on `translator-fixes` |
|---|---|---|
| Bug 5: plural guess ("travels" -> *shalei*; "this" -> *thi*) | "this" fixed (now *Era*). "travels" -> *Shalei* still open; "Safe travels" -> *Diel shalei* | The phrasebook gives *Al diel shala*. A lone "travels" is still *Shalei* in Python |
| Bug 7: we -> *anu*, they -> *danu*, them -> *dan* | Open | Open (both engines keep the tables) |
| Bug 8: plural doc vs code; *doreii* | Open | Open |
| Bug 17: tests lock in bugs | Open (`[bind]'o`, `Quel thalas`) | Fixed (*vendel'o*, *quel'thalas*). New tests lock in *dela'a* and *Bash'a falor [true] talah*. `tests/test_morphology/` is still empty |
| §3: README "Official" H1, "Midnight datamine", "invented from thin air", "great people" | Fixed | Fixed |
| §3: lexicon.md "zero random inventions", Markov credit, scraper | Fixed | Fixed |
| §3: citations.md leaked dialogue, Void Owl | Fixed (correction note) | Fixed |
| §3: grammar.md §5 "drop prepositions" | Open (a note was added) | Rewritten as the engine's convention |
| §3: grammar.md §3 `-ash` / `ru-` | Open (a note was added) | Open |
| §3: grammar.md §1 SVO | Open (a note was added) | Open |
| §6: findings 1 to 5 | Added as a note only; the body still contradicts them | Compounds and *anar'* implemented; *'a* and the Python plural kept, against findings 3 and 5 |

## Conflicts with `translator-fixes`

Checked by running the branch's engines (copies in the scratchpad).

1. **Compounds.** "The light of the sun" gives *Belore'alah*, "The breath of the dragon" gives *Dracon'endal* and "The chill of death" gives *Talah'falor*. The canon has *alah belore*, *endal dracon* and *falor talah* (finding 6).
2. **Agentive "by".** Word by word, "Saved by magic" gives *[Saved] anar'arkhana*; the canon is *Ama noral'arkhana* (finding 11).
3. **Pronoun tables.** The branch keeps we = *anu*, they = *danu*, them = *dan*, you = *'a* and I = *'o*, and attaches a pronoun to any preceding content word. The outputs include *Aria dela'dan* and *On dela'a*. The test `test_parser.py` "guide you" -> *dela'a* locks in the invented *'a* (finding 3).
4. **Plurals.** The Python engine pluralizes (*Alari*, *alanni*, *Shalei*) and the web engine does not, so they disagree. The canon marks no number (finding 2).
5. **Articles.** Dropping "the" loses the canon *no*. The test locks in *Bash'a falor [true] talah* (finding 12).
6. **Possessives.** "Your heart" gives Darnassian *Dal alann*, not Thalassian *mal alann*. "Our hearts" gives *Na alann*, with *na* on the wrong side of the noun (finding 10).
7. **Phrase splicing.** "The light of the sun guides us" gives *Alah anu belore dela'na*: the phrasebook puts the clause-initial *anu* in the middle of a sentence (finding 9, M13).
8. **README.** The branch's "Rise, dead ones!" -> *Aranal, ledel ore!* adds a generated word to Blizzard's own line (finding 13, item 4).
9. **`grammar.md` on the branch** still states SVO, `-ash`/`ru-` and the plural rules. It adds "from" -> *bessae* (Darnassian, unlabelled; finding 15).

The branch agrees with the canon on modifier-first compounds, *anar'* in oaths, *rea*, and keeping the input's word order. It does not apply the doc's `-ash` and `ru-`.

## Limits

1. The Thalassian corpus is small: 39 official glosses, 3 zhTW localizations, 6 lyric lines with unsourced English, and 1 epithet. Most rules rest on one to three phrases, and the strength labels say so.
2. Segmentation is inference. A word's meaning taken from a glossed phrase (*mal*, *ashal*, *no*, *noral'*) is the project's reading, not Blizzard's.
3. Darnassian and Shalassian evidence is used for the family's patterns. Blizzard calls them related but distinct, so each such rule is labelled with its dialect.
4. The translator branch was probed with about 40 sentences, not audited as code.
