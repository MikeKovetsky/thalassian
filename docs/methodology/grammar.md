# Thalassian Grammar

This is the grammar of the Thalassian conlang: the rules the canon supports, and the smallest set of conventions that make the language usable where the canon is silent. Every rule carries a label, so you can always tell Blizzard's language from the project's.

The canon is small. There are 39 official Thalassian glosses, 3 Chinese localizations, 6 lyric lines whose English has no cited source, and 1 epithet. Darnassian and Shalassian add about 60 more ([corpus](../../research/2026-11-revival/scripts/corpus.py)). Most rules below rest on one to three phrases, and their labels say so.

## 1. Labels

| Label | Meaning |
|---|---|
| **[canon, strong]** | Three or more independent Blizzard-glossed phrases, and no counterexample |
| **[canon, medium]** | Two glossed phrases, or one plus parallel unglossed forms |
| **[canon, weak]** | One phrase, or a segmentation that could be read another way |
| **[loan: Darnassian]**, **[loan: Shalassian]** | Attested in a related language, not in Thalassian. Blizzard's encyclopedia warns that Darnassian-specific words can offend high elves and blood elves ([Encyclopedia](https://warcraft.wiki.gg/wiki/The_Warcraft_Encyclopedia/Thalassian)), so loans are marked |
| **[convention]** | The project's choice. It fits the canon, but the canon does not show it |
| **[invented]** | The project's choice where the canon is silent. Section 10 lists all of them |

## 2. Sentence order

### 2.1 Imperatives come first [canon, strong]

A command opens with its verb, in its bare form, and the object follows:
- *Anaria shola* "Speak your business."
- *Bash'a no falor talah!* "Taste the chill of true death!"
- *Vendel'o eranu* "Help me forget."
- *Belono sil'aru, belore'dorei* "Shoulder your burdens well, child of the sun."
- *Aranal* "Rise."
- *Elor bindel felallan morin'aminor* "Sleep forever in quiet serenity."

Two Chinese localizations agree: *Band'or shorel'aran* "Prepare to say farewell" and *Balamore shanal* "Prepare to die". So do two Darnassian commands, *Ash karath* "Do it" and *Bandu thoribas* "Prepare to fight".

### 2.2 Statements: subject, verb, object

- **The verb comes before its object [canon, strong].** See the imperatives above, and *Tal anu'men no Sin'dorei* "Death to all who oppose the children of the blood".
- **The subject comes before the verb [canon, weak].** Only two glossed Thalassian statements have both: *Anu belore dela'na* "The sun guides us" and *Shindu fallah na* "They are breaking through". The basic order of a statement is therefore subject, verb, object **[convention, on weak evidence]**. The order is a default, not a strict rule.
- **Related languages differ.** Shalassian puts the verb before the subject: *Ru shanna shal'dorei* "The nightborne will survive". Darnassian can put a predicate first: *Shu dalas na* "Heavy are our hearts". Neither applies to Thalassian.

### 2.3 Question words come first [canon, medium]

- *Doral ana'diel?* "How fare you?"
- Darnassian *Fandu-dath-belore?* "Who goes there?"

### 2.4 The person addressed comes last, after a comma [canon, medium]

- *Bal'a dash, malanore* "Greetings, traveler."
- *Belono sil'aru, belore'dorei* "Shoulder your burdens well, child of the sun."
- *Selama ashal'anore, Blood Knight* (Vereesa, BroadcastText 309952).

### 2.5 Wishes and blessings may open with *anu* [canon, weak]

*Anu* opens the greeting *Anu belore dela'na*, in which "us" is already *'na*. It also opens the untranslated *Anu bala belore alon*. In Darnassian, wishes open the same way: *Anu'dorini Talah* "Let my will be known", *Andu-falah-dor* "Let balance be restored", *Ande'thoras-ethil* "May your troubles be diminished". The exact meaning of *anu* is unknown. Do not use it as a pronoun, and keep it at the start of its clause.

## 3. Nouns

### 3.1 No case [canon, medium]

A noun has the same form whatever its role:
- *belore* is a subject in *Anu belore dela'na*, an "of" phrase in *Anar'alah belore*, and a modifier in *Belore'dorei*;
- *Sin'dorei* is an object in *Tal anu'men no Sin'dorei*.

Word order and particles carry the roles.

### 3.2 No plural [canon, strong]

Number is not marked. Context, or a number word (section 10), shows it.
- *dorei* is "child" in *Belore'dorei* "Child of the Sun", which addresses one ranger lord. A Skyborne says "I am shen'dorei" ([report 3](../../research/2026-11-revival/3-new-elven-race.md)).
- *dorei* is "children" in *Sin'dorei* and *Quel'dorei*.
- English plurals in the glosses carry no ending: *sil'aru* "your burdens", *Shindu* "they / our enemies", Darnassian *thoras* "troubles", *ilisar* "enemies", *kal* "stars".

### 3.3 Compounds put the modifier first and the head last [canon, strong]

Two words joined by an apostrophe make a compound, and the modifier comes first. This holds in all 10 Thalassian compounds whose parts are known:
- *Quel'Thalas* "High Home";
- *Thas'alah* "Light of the Forest", *Thas'dorah* "Valor of the Forest";
- *Sin'dorei*, *Ren'dorei*, *Quel'dorei*, *Belore'dorei*;
- *Felo'melorn* "Flame Strike";
- *Ban'dinoriel* "Gatekeeper";
- *Lu'selama* "Light's Justice".

It holds in 13 Darnassian and Shalassian compounds too. The one exception is the Darnassian title *Thero'shan* "honored student".

The modifier can be an adjective (*Quel'*) or a noun (*Sin'*, *Thas'*). Compounds name things: peoples, places, weapons, titles and fixed epithets.

### 3.4 In ordinary speech, "of" phrases put the head first, with no "of" [canon, medium]

- *Anar'alah belore* "By the light of the sun": *alah* "light", then *belore* "sun".
- *Anar'endal dracon* "By the breath of the dragon".
- *Bash'a no falor talah* "Taste the chill of true death".
- The Canticle of Sacrifice pairs *ann'da* + *anore* with "father of our people" (lyric sheet; the translation is unsourced).

The same noun can take either pattern. "Light" is *Thas'alah* when it names a bow, but *alah belore* in an oath.

**Rule of thumb [convention]:** use a compound (modifier'head) for a name, a title or a fixed epithet. Use a free phrase (head, then modifier) everywhere else.

### 3.5 *-i* on a name means "of" or "from" that place or person [canon, weak to medium]

- *Zin-Azshari* "the glory of Azshara" **[loan: Darnassian]**;
- *Suramari* "Suramarian" **[loan: Shalassian]**;
- Skyborne *Rohashi* "of Rohash" and *zephrali* "of Zephras" **[loan: Darnassian, Skyborne dialect]**.

This *-i* is not a plural (section 3.2).

### 3.6 Kinship and honorific endings

- ***'da* marks parents [canon, medium]:** *Ann'da* "father", *Minn'da* "mother"; Darnassian *An'da*, *Min'da*.
- ***'do* marks respect [loan: Darnassian, medium]:** *Shan'do* "honored teacher", *Nahlen'do* "Master of the Fang", *Minn'do* "mother" (formal).

### 3.7 *no* before a definite object [canon, weak]

*no* stands where English has "the" before a noun object:
- *Bash'a **no** falor talah* "Taste **the** chill of true death";
- *Tal anu'men **no** Sin'dorei* "Death to all who oppose **the** children of the blood".

It is absent before objects with "your": *Anaria shola*, *Belono sil'aru*.

Keep *no* in canon phrases. Using it in new sentences is optional **[convention]**.

## 4. Adjectives and adverbs

- **An adjective comes before its noun [canon, medium]:** *Al diel shala* "Safe travels", *Shindu sin'dorei* "Failing children of the blood", *Quel'Thalas* "High Home".
- **Adverbs:** the canon has both orders. *Sinu a'manore* "Well met" puts the adverb first; *Elor bindel* "Sleep forever" puts it last. Put an adverb after the verb **[convention]**.

## 5. Pronouns

### 5.1 Object pronouns follow the verb [canon, medium]

| Form | Meaning | Label | Evidence |
|---|---|---|---|
| *'na* | us | [canon, medium] | *Anu belore dela'na* "The sun guides us" |
| *'o* | me | [canon, weak] | *Vendel'o eranu* "Help me forget" |
| *'a* | you | [invented] | No Thalassian form for "you" is attested. *Bash'a* and *Bal'a* are not "you" in their glosses |
| *'dan* | him, her, it, them | [invented] | No third-person form is attested |

**Spelling [convention].** Write an object pronoun joined to its verb by an apostrophe (*dela'na*). The canon writes it both ways: joined in *dela'na* and *Vendel'o*, free in *Shindu fallah na*.

### 5.2 Possessives [canon, weak]

| Form | Meaning | Position | Label | Evidence |
|---|---|---|---|---|
| *mal* | your | before the noun | [canon, weak] | *Elu'meniel mal alann* "May peace calm your heart" |
| *na* | our | after the noun | [canon, weak] | Darnassian *Shu dalas na* "Heavy are our hearts"; Lament gloss of *Shindu fallah na*, "Our enemies are breaking through" |
| *o* | my | after the noun | [invented] | By analogy with *na* |
| *dan* | his, her, its, their | after the noun | [invented] | By analogy with *na* |

Thalassian *mal* is preferred to Darnassian *dal* (*Ishnu-dal-dieb*) **[loan: Darnassian]**. The lexicon does not list *mal*: its meaning rests on elimination within this one phrase, so it stays held back ([report 8](../../research/2026-11-revival/8-reconstruction-audit.md)).

### 5.3 Subject pronouns [invented]

The canon has no Thalassian subject pronoun.
1. Leave a subject pronoun out when the context makes it clear, as in *Shindu fallah na* "They are breaking through".
2. When one is needed, use the object form as a free word before the verb: *na* "we", *o* "I", *a* "you", *dan* "he, she, it, they". Like nouns, pronouns then have one form for every role (section 3.1).

The generated *on*, *al'ore* and *il'ore* were therefore removed in the [November 2026 audit](../../research/2026-11-revival/8-reconstruction-audit.md).

**Not pronouns:**
- *anu* is the wish particle (section 2.5), not "we".
- *danu* "they" is dropped: one third-person form is enough.
- *aria* is Darnassian "we face", not "we".

## 6. Verbs

### 6.1 One bare form, with no agreement [canon, weak]

*dela* "guides" (one subject) and *fallah* "are breaking" (several) carry no person or number ending. The imperative is the same bare form (section 2.1).

### 6.2 Tense

- **Present and past: no marker [canon].** No glossed phrase marks tense on a Thalassian verb. The one past participle, *Ama* "Saved" in *Ama noral'arkhana*, has no ending. Show the past with a time word when it matters **[invented]**.
- **Future: *ru* before the verb [loan: Shalassian, weak].** *Ru shanna shal'dorei* "The nightborne will survive", also spelled *Ru-shanna*. Write it as a separate word: *ru dela* "will guide". The evidence is mixed: Darnassian *Ru shallora enudoril* "I anoint these caretakers of the wild" is present tense.
- **Removed:** the past suffix *-ash* (*dela'ash*). Nothing attests it. Its claimed source, *ashal* "complete/great", is unsupported: *ashal* is "for" (section 7.3). And *ash* already opens commands and war cries in Darnassian and Shalassian (*Ash karath* "Do it", *Ash'thoras denil*).

## 7. Prepositions and particles

### 7.1 "of" is never a word [canon, strong]

About 15 glossed "of" phrases use a compound (section 3.3) or a head-first phrase (section 3.4), never a separate word.

### 7.2 *anar'* "by", in oaths and invocations [canon, strong]

*anar'* is joined by an apostrophe to the noun after it:
- *Anar'alah* "By the light";
- *Anar'alah belore* "By the light of the sun";
- *Anar'endal dracon* "By the breath of the dragon".

Six untranslated exclamations have the same shape: *Anar'anel belore*, *Anar'alash denal*, *Anar'dalel*, *Anar'sin arkhana*, *Anar'endal belore*, and Shalassian *Anar'amenos*.

*anar'* is not the "by" of a passive. "Saved by magic" is *Ama noral'arkhana*, and the meaning of *noral'* is not settled (section 10).

### 7.3 *ashal'* "for" [canon, weak]

*Selama ashal'anore* "Justice for our people". The meaning is inferred by elimination. It is joined by an apostrophe, like *anar'*.

### 7.4 *rea* "and" [canon, medium]

*Rea* = "And" (Loreology). It joins words, phrases or clauses of the same kind. It never means "or".

### 7.5 Other prepositions

- "through": Shalassian *vala* (*Quel'vala thonos* "Nobility through tradition") **[loan: Shalassian, weak]**.
- "from the": Darnassian *bessae* **[loan: Darnassian]**.
- "to", "in", "with", "from" and the rest have no Thalassian form. Leave them out when the meaning stays clear **[convention]**, or see section 10.

## 8. Formulas

Thalassian greetings and farewells are fixed phrases; use them whole [canon].

| Formula | Meaning | Use |
|---|---|---|
| *Bal'a dash, malanore* | Greetings, traveler | Greeting |
| *Sinu a'manore* | Well met | Greeting |
| *Anaria shola* | Speak your business | Businesslike greeting |
| *Anu belore dela'na* | The sun guides us | Greeting, among blood elves and high elves only |
| *Doral ana'diel?* | How fare you? | Greeting |
| *Al diel shala* | Safe travels | Farewell |
| *Shorel'aran* | Farewell | Farewell |
| *Selama ashal'anore* | Justice for our people | Vow or farewell |
| *Anar'alah belore* | By the light of the sun | Battle cry or vow |

**Darnassian blessings [loan: Darnassian, medium].** X-*adore* "X be with you" (*Elune-adore*), and X-*alah* "X to you" (*Ishnu-alah* "Good fortune to you"). The same shapes appear unglossed:
- Shalassian *An'ratha adore* (a farewell);
- Nazja *Zin-Azshari adore*;
- Skyborne *banu adora* and *banu alah*.

They are not Thalassian. In Thalassian, *alah* means "light", so *X-alah* reads as "X light". Use these blessings only for night elves, nightborne or Skyborne speakers.

## 9. Spelling: apostrophes and hyphens [convention, drawn from the canon]

- **An apostrophe joins:**
  - a compound (*Sin'dorei*);
  - a proclitic preposition (*anar'alah*, *ashal'anore*);
  - an object pronoun (*dela'na*);
  - a kinship ending (*Ann'da*).
- **A hyphen joins** the parts of a Darnassian fixed phrase (*Ishnu-alah*, *Andu-falah-dor*, *Zin-Azshari*). Thalassian glosses do not use hyphens.
- **Capitals:** capitalize the start of a sentence and proper names (*Quel'Thalas*, *Sin'dorei* as a people's name).

## 10. Open questions: the smallest conventions [all invented]

The canon is silent on the points below. Each convention is the smallest one that makes the language usable; change any of them freely, because none is Blizzard's.

1. **Subject pronouns** take the object form as a free word before the verb, and are dropped when clear (section 5.3).
2. **"You"** is *'a* after a verb and *a* before it. "Your" is the canon *mal* (section 5.2).
3. **Third person** is *dan* for every gender, number and role.
4. **"My", "his", "their"** are *o* and *dan* after the noun, like *na* "our".
5. **Plural, when it matters:** add a number or a word such as *aeess* "many" before the noun. Those words are not attested; they come from the [Method 7 generator](../../research/2026-11-revival/1-review-and-methods.md#method-7-phonotactic-model) (report 8). Never add *-i*.
6. **Past tense, when it matters:** add a time word. There is no verb ending.
7. **Negation:** one particle before the verb, the generated *la*. The [November 2026 audit](../../research/2026-11-revival/8-reconstruction-audit.md) removed the second negator, *nath*: it is one letter from Darnassian *anath* and part of an Orcish scrambler word.
8. **Yes/no questions** keep statement order and end in "?". Question words come first (section 2.3).
9. **"X is Y"** has no verb "to be": write *X Y*, with the predicate first for emphasis, following Darnassian *Shu dalas na* "Heavy are our hearts".
10. **Relative clauses** follow the noun, with no word for "who" or "which".
11. **"Or"** has no attested form; generate one. Never use *rea*, which means "and".
12. **The agent of a passive** ("by magic"): rephrase as an active sentence. Keep *noral'* for the canon phrase *Ama noral'arkhana* only, until its meaning is settled.
13. **Prepositions other than *anar'* and *ashal'*:** leave them out when the meaning stays clear, or use a generated proclitic joined by an apostrophe, as with *anar'*. "In" is *elil'* and "at" is *ror'* (report 8).
14. **Numbers:** not attested in Thalassian. Generate them; the generated *akus* "one" is one example. It replaced *ore*, which ends six canon words (*belore*, *anore* ...) and so invited false parses.

## 11. Worked examples

**Canon, analyzed:**

| Phrase | Gloss | Analysis |
|---|---|---|
| *Anu belore dela'na* | The sun guides us | wish particle *anu* (2.5), subject *belore*, verb *dela* + object *'na* (5.1) |
| *Bash'a no falor talah!* | Taste the chill of true death! | imperative first (2.1), *no* before the object (3.7), head-first "of" phrase *falor talah* (3.4) |
| *Anar'alah belore* | By the light of the sun | *anar'* + *alah* (7.2), then *belore* as a head-first "of" phrase (3.4) |
| *Selama ashal'anore, Blood Knight* | Justice for our people, Blood Knight | noun, *ashal'* + *anore* (7.3), vocative last (2.4) |
| *Doral ana'diel?* | How fare you? | question word first (2.3) |
| *Sin'dorei*, *Thas'alah* | Children of the blood, Light of the Forest | compounds, modifier first (3.3) |
| *Ann'da*, *Minn'da* | Father, Mother | kinship *'da* (3.6) |

**Built with the conventions (not canon):**

| English | Thalassian | Rules used |
|---|---|---|
| The children of the blood guide us | *Sin'dorei dela'na* | compound name (3.3), subject, verb, object (2.2) |
| Guide me, child of the sun | *Dela'o, belore'dorei* | imperative first (2.1), *'o* (5.1), vocative last (2.4) |
| The sun will guide us | *Belore ru dela'na* | *ru* [loan: Shalassian] (6.2) |
| Your heart | *Mal alann* | *mal* before the noun (5.2) |
| By the breath of the sun | *Anar'endal belore* | an attested untranslated line, built from *anar'* (7.2) and a head-first "of" phrase (3.4) |

## 12. What changed from the March 2026 grammar

| March rule | Now | Why |
|---|---|---|
| Strict SVO, "observable in most of Blizzard's phrases" | Imperatives first; statements default to subject, verb, object | 2 of 39 official glosses are statements with a subject; at least 6 are commands |
| "Relies on a strict word order"; "similar to English or Esperanto" | Removed | Shalassian is verb-subject; Esperanto has an accusative case |
| Past suffix *-ash*, from *ashal* "complete/great" | Removed; no tense marker | No attestation; *ashal* is "for"; *ash* opens commands |
| Future prefix *ru-* (*ru'dela*) | *ru* before the verb, as a Shalassian loan | One Shalassian phrase; never spelled with an apostrophe |
| Plurals in *-i* / *-ei* (*alari*, *sindorei*, *sholai*) | No plural | *dorei* is both child and children; *-i* on names means "of" |
| *o* = me/I, *a* = you, *na* = us/we; pronouns never standalone | Object clitics *'na* and *'o* (canon); *'a* and subject forms invented | *na* is "us/our" only; *na*, *isil* and *mal* stand free in the canon |
| we = *anu*, they = *danu*, them = *dan* (code) | *anu* is a wish particle; *dan* is the invented third person; *danu* is dropped | *Anu belore dela'na* already has *'na* "us" |
| "Elves generally drop prepositions" | "of" is never a word; *anar'*, *ashal'* and *rea* are kept | Canon *anar'*, *ashal'*, *vala*, *bessae* |
| Adjective after the noun "in poetic contexts" | Removed | No case in the canon |
| Adjective + Noun compounds | Kept and widened to modifier + head, with head-first "of" phrases in speech | 10 of 10 compounds; *alah belore*, *endal dracon*, *falor talah* |

## For the engines

To match this grammar:
1. `pluralization.py` should stop changing nouns.
2. `agglutination.py` and the tables in `web/index.html` should use the forms in section 5. That means dropping *anu* and *danu*, and making the English and Ukrainian tables agree.
3. The Pure LLM prompt should state sections 2 to 7 in place of "SVO word order, drop prepositions".
4. The translator's "X of the Y" rule should build a compound only for names, titles and epithets, and a head-first phrase otherwise.
