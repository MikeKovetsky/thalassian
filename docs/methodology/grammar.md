# Thalassian Grammar

This document describes the structural rules (syntax and morphology) of the language, reconstructed from canonical World of Warcraft phrases and extrapolated for the conlang.

> **November 2026 audit: what the canon actually supports.** The rules below are the engine's conventions; several go beyond the canon. From all Blizzard-glossed phrases ([full analysis](../../research/2026-11-revival/1-review-and-methods.md#6-grammar-findings-from-the-canon)):
> 1. Apostrophe compounds put the modifier first and the head last (*Quel'Thalas* "High Home", *Thas'alah* "Light of the Forest", *Sin'dorei*), in 10 of 10 Thalassian cases.
> 2. Free genitive phrases put the head first (*falor talah*, "chill of true death").
> 3. The enclitic pronouns *'na* (us/our) and *'o* (me) are attested; *'a* (you) is not.
> 4. Imperatives come first in the clause. Strict SVO is not established: Shalassian *Ru shanna shal'dorei* ("The nightborne will survive") is verb-subject.
> 5. Prepositions exist (*anar* "by", Shalassian *vala* "through", Darnassian *bessae* "from the"). Number is unmarked on *dorei* (child or children). No tense morphology is attested, so the `-ash` and `ru-` tense markers below are inventions.

## 1. Word Order
We use standard analytical word order: **Subject — Verb — Object (SVO)**.
This is the most natural order for the majority of global languages and is observable in most of Blizzard's translated phrases.
- *Example:* The sun guides us -> SVO.

## 2. Cases
Elven language does not utilize complex noun cases (unlike Slavic languages). It relies on a strict word order and agglutination, similar to English or Esperanto.

## 3. Verb Tenses
To keep the language "lore-friendly" and avoid overloading it with conjugation tables, tense markers (particles/affixes) are used:
- **Present Tense:** Base verb root (e.g., *dela* - guide).
- **Past Tense:** Suffix `-ash` (derived from *ashal* - complete/great). E.g., *dela'ash* (guided).
- **Future Tense:** Prefix `ru-` (derived from *ru shanna* - will survive). E.g., *ru'dela* (will guide).

## 4. Plurals
From the canon, we know plurals are often formed by adding the suffix `-i` or changing the final vowel to the diphthong `-ei` (dore -> dorei).
- **Rule 1:** If the word ends with a consonant, add `-i` (e.g., *alar* -> *alari* - rangers).
- **Rule 2:** If the word ends with a vowel, add `-i` to form a diphthong, or extend the vowel (e.g., *sindo* -> *sindorei*, *shola* -> *sholai*).

## 5. Agglutination (Pronouns & Prepositions)
This is the core feature of Thalassian grammar:
- **Pronouns:** Pronouns are not standalone subjects/objects when a verb is present. They attach to the end of verbs using an apostrophe.
  - `o` = me/I
  - `a` = you
  - `na` = us/we
  - *Example:* `dela'na` (guides us).
- **Prepositions:** The translator drops "for", "to", "in", "on", "with", "of" and "but", and the articles. Any other preposition is looked up like any word: "by" gives *anar'*, "from" gives Darnassian *bessae*, and one the lexicon lacks stays in brackets ("[at]"). The canon has prepositions (*anar* "by", *ashal* "for" as the audit reads it), so dropping is the engine's convention, not a rule of the language.
  - "by" is the proclitic *anar'*: "by the light" is *Anar'alah*, and "by the breath of the dragon" is *Anar'endal dracon*.
  - "and" is *rea*.
  - *Example:* `Selama ashal'anore` (Justice for our people). The audit reads *ashal* as "for", so this example does keep a preposition.

## 6. Adjectives
Adjectives can precede the noun when they merge into a term (e.g., *Quel'dorei* - High elves), or follow the noun in poetic contexts.
For the conlang, the base rule for compound words is: **Adjective + Noun**.

"X of [the] Y" becomes the compound **Y'X**, modifier first and head last, when X is a noun and the "of" phrase ends at Y: "children of the blood" is *Sin'dorei*, and "light of the forest" is *Thas'alah*. A verb after Y ends the phrase, so "the children of the blood guide us" is *Sin'dorei dela'na*. Two cases stay free, with the head first and no apostrophe: a longer "of" phrase, where Y is not a noun or a noun follows it ("the chill of true death", *falor talah*; "father of our people", canon *Ann'da anore*), and "of" after "by X" ("by the light of the sun", *Anar'alah belore*).
