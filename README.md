# Thalassian: A Sin'dorei Language Engine

[![GitHub Pages](https://img.shields.io/badge/Live_Demo-Play_Now-d4af37?style=for-the-badge&logo=github)](https://MikeKovetsky.github.io/thalassian/)
[![WoW Forever client data](https://img.shields.io/badge/WoW_Forever-1.60.1_client_data-8b0000?style=for-the-badge)](research/2026-11-revival/2-client-mining.md)
[![Built with Portal OS](https://img.shields.io/badge/Built_by-Portal_AI-black?style=for-the-badge)](https://portal.ai)

> *“Bal'a dash, malanore. Anu belore dela'na.”*

Welcome to **Thalassian**, a fan conlang engine for the Blood Elves (Sin'dorei), High Elves (Quel'dorei), Void Elves (Ren'dorei) and the Skyborne (Shen'dorei) of *World of Warcraft*.

The project follows a **Canon-First** methodology: every word says whether Blizzard stated its meaning (`canon: true`) and on what basis (`canon_basis`: attested, segment, epithet, name, inferred, generated or unverified). Canon comes from Blizzard's own glossed phrases in Thalassian, Darnassian and Shalassian, and since November 2026 from the [WoW Forever game client](research/2026-11-revival/2-client-mining.md). Words Blizzard never gave are filled in by inference or generation, and are marked as such.

**November 2026 revival.** A [canon audit](research/2026-11-revival/1-review-and-methods.md) corrected wrong meanings (for example *bash'a* is "taste", not "death"; *shal'na* is "aunt") and found that the March 2026 "Midnight datamine" never happened. The lexicon grew from 206 to 310 entries, including the [Skyborne words](research/2026-11-revival/3-new-elven-race.md) of WoW Forever (*shen'dorei*, "hidden people"). Every change and its evidence is in [the merge log](research/2026-11-revival/merge-log.md).

**Reconstruction audit.** [Report 8](research/2026-11-revival/8-reconstruction-audit.md) checked the grammar and the invented words against the canon. The grammar was rewritten with a label on every rule. In the lexicon, 12 flawed words were removed, 37 got new forms from a collision-checked generator, and 114 generated words filled every gap in the 207-word Swadesh list, which took the lexicon to 416 entries.

**Warcraft III and Midnight.** [Report 9](research/2026-11-revival/9-warcraft-iii.md) read Warcraft III: Reforged's own game files, [report 10](research/2026-11-revival/10-midnight-wiki.md) Midnight's text as the wiki quotes it, and [report 11](research/2026-11-revival/11-forsaken-kingdom-voice.md) the voice of Warcraft III's new campaign. They add the Darnassian titles *shan'do* "honored teacher" and *thero'shan* "honored student", the nightborne mana tree *Arcan'dor* and two Midnight item names, and new evidence to 14 entries. The lexicon now has 421 entries.

This project was conceived by **Mike Kovetsky** and architected by an autonomous agent powered by **Portal OS** ([Portal AI](https://portal.ai)).

---

## ⚡ Live Demo (Web Translator)
Try the language engine directly in your browser:
👉 **[Launch Thalassian Translator](https://MikeKovetsky.github.io/thalassian/)**

### Translation Modes:
1. **Strict Programmatic (Local):** Instantly translates known canon roots using our custom NLP grammar compiler. Missing words stay in English.
2. **Hybrid Gap-Fill (AI Powered):** Uses Elvish phonotactics to invent lore-friendly roots for missing words on the fly via LLM.
3. **Pure LLM Driven:** A creative mode where the LLM is fed our entire dictionary and grammar rules to roleplay a Silvermoon Magister.

---

## 📚 Examples of Elven Grammar at Work

Our engine matches whole canon phrases first. Word by word it follows the [grammar](docs/methodology/grammar.md):
- object pronouns join the verb (*dela'na*, "guides us"), and a subject pronoun is a free word before it (*na*, "we");
- *mal* "your" comes before its noun, *na* "our" after it, and nouns take no plural;
- "and" is *rea*, and a "By" that opens a clause, as an oath does, is *anar'*;
- an "of" phrase puts its head first (*alah belore*, "the light of the sun"). Only a capitalized name becomes a modifier-first compound (*Sin'dorei*, "Children of the Blood").

*   **English:** *"The sun guides us."*
    **Thalassian:** `Anu belore dela'na.` *(Canon match)*
*   **English:** *"Children of the Void"*
    **Thalassian:** `Ren'dorei` *(Canon match; word by word, the name is also built as void + children)*
*   **English:** *"Rise, dead ones!"*
    **Thalassian:** `Aranal, ledel!` *(Prince Keleseth's own line: only "aranal" (rise) is glossed, so the English is a guess)*
*   **English:** *"Justice for our people."*
    **Thalassian:** `Selama ashal'anore.` *(Canon match)*

### Poetic Translation (Song Adaptation)
The March 2026 README showed a rock song translated in the LLM-Hybrid mode. That example used words the audits removed (*mith*, *on*, *ethala*) and rules the canon contradicts, so it was taken out ([grammar findings, item 7](research/2026-11-revival/8-audit/grammar-findings.md#7-the-readme-song-translation-breaks-both-the-rules-and-the-lexicon)).

---

## 🏗️ Project Architecture

We treat conlanging as software engineering. The project is structured as a proper Python NLP framework:

- `src/thalassian/data/lexicon.json` - The single source of truth: 421 entries, each with `canon`, `canon_basis` and, for entries added since November 2026, `evidence` (exact quote and where it is).
- `src/thalassian/syntax/parser.py` - The NLP Grammar Compiler: whole canon phrases first, then word by word with the grammar's rules (*anar'* in oaths, compounds for names, head-first "of" phrases, possessives, pronoun suffixes), in the input's word order. `spaCy`, when installed, supplies the lemmas. `web/translator.js` runs the same rules in the browser.
- `src/thalassian/phonetics/markov.py` - A character Markov-chain engine that generates new vocabulary from canon letter patterns. The November 2026 audit found its words easy to tell apart from canon. New words now come from a Kneser-Ney generator with collision checks ([generate_words.py](research/2026-11-revival/scripts/generate_words.py), [report 8](research/2026-11-revival/8-reconstruction-audit.md#5-the-generator)).
- `src/thalassian/morphology/` - The pronoun and possessive tables (grammar section 5). Nouns have no plural, so there is no plural rule.

### Dive deeper into our methodology:
1. 📖 **[Lexicon Methodology (Canon-First)](docs/methodology/lexicon.md)**
2. 📜 **[Grammar Methodology (AST & Agglutination)](docs/methodology/grammar.md)**
3. 🖋️ **[Typography Methodology (Runic Visuals)](docs/methodology/typography.md)**
4. 📚 **[Bibliography & Sources (Citations)](docs/citations.md)**
5. 🤖 **[Architecting with Portal OS (How an AI built this)](docs/methodology/how-to-use-portal.md)**
6. 🔎 **[November 2026 revival: audit, client mining and the Skyborne](research/2026-11-revival/)**
7. 🧪 **[Reconstruction audit: grammar and invented words checked, basic vocabulary completed](research/2026-11-revival/8-reconstruction-audit.md)**

---

## 🚀 Future Roadmap
- [x] **Lexicon Combiner**: Script to automatically merge roots into complex nouns.
- [x] **Grammar Compiler**: Syntax rules (word order, compounds, pronoun agglutination; no plurals since the November 2026 grammar audit).
- [x] **Web Interface**: Multi-mode translator hosted on GitHub Pages.
- [x] **WoW Forever client mining**: Read the game client's tables, hotfixes and caches (`tools/wowf/`).
- [x] **Canon audit**: Every canon entry checked against its source; wrong meanings fixed (November 2026).
- [x] **Skyborne (Shen'dorei)**: Vocabulary of the new WoW Forever elven race.
- [x] **Reconstruction audit**: Grammar and invented words checked against the canon; the Swadesh-207 list is fully covered ([report 8](research/2026-11-revival/8-reconstruction-audit.md)).
- [x] **Localized text mining**: Blizzard's Chinese and Korean dialogue tables, mined for the elven lines the localizers translated ([report](research/2026-11-revival/4-localization-mining.md)).
- [ ] **Server-side localized lines**: the TBC Kael'thas lines whose Chinese glosses the wiki reports are not in the client's tables, so those glosses are still unverified.
- [x] **Phrasebook-first translator**: Match whole canon phrases first and build modifier-first compounds (`Sin'dorei`, not `Dorei sin`) ([scores](research/2026-11-revival/1-review-and-methods.md#method-8-translator-evaluation-on-canon-phrases)).
- [x] **Typography Engine**: Integrated Elvish Runic fonts for visual rendering in the web app.
- [x] **Reverse Translator**: Auto-detects Elvish and translates back to English.
- [x] **Syntax Tree Visualizer**: D3.js interactive parse trees for Elven grammar.
- [ ] **Audio Generation**: TTS integration that speaks Thalassian with a Silvermoon accent.

---
*World of Warcraft and Blizzard Entertainment are trademarks or registered trademarks of Blizzard Entertainment, Inc. in the U.S. and/or other countries.*
