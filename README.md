# Thalassian: A Sin'dorei Language Engine

[![GitHub Pages](https://img.shields.io/badge/Live_Demo-Play_Now-d4af37?style=for-the-badge&logo=github)](https://MikeKovetsky.github.io/thalassian/)
[![WoW Forever client data](https://img.shields.io/badge/WoW_Forever-1.60.1_client_data-8b0000?style=for-the-badge)](research/2026-11-revival/2-client-mining.md)
[![Built with Portal OS](https://img.shields.io/badge/Built_by-Portal_AI-black?style=for-the-badge)](https://portal.ai)

> *“Bal'a dash, malanore. Anu belore dela'na.”*

Welcome to **Thalassian**, a fan conlang engine for the Blood Elves (Sin'dorei), High Elves (Quel'dorei), Void Elves (Ren'dorei) and the Skyborne (Shen'dorei) of *World of Warcraft*.

The project follows a **Canon-First** methodology: every word says whether Blizzard stated its meaning (`canon: true`) and on what basis (`canon_basis`: attested, segment, epithet, name, inferred, generated or unverified). Canon comes from Blizzard's own glossed phrases in Thalassian, Darnassian and Shalassian, and since November 2026 from the [WoW Forever game client](research/2026-11-revival/2-client-mining.md). Words Blizzard never gave are filled in by inference or generation, and are marked as such.

**November 2026 revival.** A [canon audit](research/2026-11-revival/1-review-and-methods.md) corrected wrong meanings (for example *bash'a* is "taste", not "death"; *shal'na* is "aunt") and found that the March 2026 "Midnight datamine" never happened. The lexicon grew from 206 to 310 entries, including the [Skyborne words](research/2026-11-revival/3-new-elven-race.md) of WoW Forever (*shen'dorei*, "hidden people"). Every change and its evidence is in [the merge log](research/2026-11-revival/merge-log.md).

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

Our engine matches whole canon phrases first. Word by word, pronouns attach to verbs, most prepositions are dropped (but "by" is *anar'* and "and" is *rea*), and "X of the Y" becomes a modifier-first compound.

*   **English:** *"The sun guides us."*
    **Thalassian:** `Anu belore dela'na.` *(Canon match)*
*   **English:** *"Children of the void"*
    **Thalassian:** `Ren'dorei` *(Canon match; word by word it is also built as void + children)*
*   **English:** *"Rise, dead ones!"*
    **Thalassian:** `Aranal, ledel!` *(Extrapolated from Prince Keleseth)*
*   **English:** *"Justice for our people."*
    **Thalassian:** `Selama ashal'anore.` *(Canon match)*

### Poetic Translation (Song Adaptation)
Because Elves don't use modern words like "chains" or "confession", translating modern songs requires poetic adaptation of the roots. Here is a translation of a famous rock song (*Foo Fighters - Best of You*) using our LLM-Hybrid engine:

*   *"I've got another confession to make"* -> `Mith'o dalah'shola` (I speak my truth/business)
*   *"I'm your fool"* -> `On dal'thielin` (I am your little one)
*   *"Everyone's got their chains to break"* -> `Ethala shindu doren` (All break their bonds)
*   *"Holding you"* -> `Ari'a` (Hold'you)
*   *"Were you born to resist or be abused?"* -> `Dorei'a menta rea shindara?` (Born'you to oppose or fear?)

---

## 🏗️ Project Architecture

We treat conlanging as software engineering. The project is structured as a proper Python NLP framework:

- `src/thalassian/data/lexicon.json` - The single source of truth: 314 entries, each with `canon`, `canon_basis` and, for entries added since November 2026, `evidence` (exact quote and where it is).
- `src/thalassian/syntax/parser.py` - The NLP Grammar Compiler: whole canon phrases first, then word by word with the canon rules (*anar'*, modifier-first compounds, pronoun suffixes), in the input's word order. `spaCy`, when installed, supplies the lemmas. `web/translator.js` runs the same rules in the browser.
- `src/thalassian/phonetics/markov.py` - A character Markov-chain engine that generates new vocabulary from canon letter patterns. The November 2026 audit found its words easy to tell apart from canon and describes a better generator ([Method 7](research/2026-11-revival/1-review-and-methods.md#method-7-phonotactic-model)).
- `src/thalassian/morphology/` - Rules for agglutination and vocalic mutation (pluralization).

### Dive deeper into our methodology:
1. 📖 **[Lexicon Methodology (Canon-First)](docs/methodology/lexicon.md)**
2. 📜 **[Grammar Methodology (AST & Agglutination)](docs/methodology/grammar.md)**
3. 🖋️ **[Typography Methodology (Runic Visuals)](docs/methodology/typography.md)**
4. 📚 **[Bibliography & Sources (Citations)](docs/citations.md)**
5. 🤖 **[Architecting with Portal OS (How an AI built this)](docs/methodology/how-to-use-portal.md)**
6. 🔎 **[November 2026 revival: audit, client mining and the Skyborne](research/2026-11-revival/)**

---

## 🚀 Future Roadmap
- [x] **Lexicon Combiner**: Script to automatically merge roots into complex nouns.
- [x] **Grammar Compiler**: Syntax rules (SVO, pluralization, pronoun agglutination).
- [x] **Web Interface**: Multi-mode translator hosted on GitHub Pages.
- [x] **WoW Forever client mining**: Read the game client's tables, hotfixes and caches (`tools/wowf/`).
- [x] **Canon audit**: Every canon entry checked against its source; wrong meanings fixed (November 2026).
- [x] **Skyborne (Shen'dorei)**: Vocabulary of the new WoW Forever elven race.
- [x] **Localized text mining**: Blizzard's Chinese and Korean dialogue tables, mined for the elven lines the localizers translated ([report](research/2026-11-revival/4-localization-mining.md)).
- [ ] **Server-side localized lines**: the TBC Kael'thas lines whose Chinese glosses the wiki reports are not in the client's tables, so those glosses are still unverified.
- [x] **Phrasebook-first translator**: Match whole canon phrases first and build modifier-first compounds (`Sin'dorei`, not `Dorei sin`) ([scores](research/2026-11-revival/1-review-and-methods.md#method-8-translator-evaluation-on-canon-phrases)).
- [x] **Typography Engine**: Integrated Elvish Runic fonts for visual rendering in the web app.
- [x] **Reverse Translator**: Auto-detects Elvish and translates back to English.
- [x] **Syntax Tree Visualizer**: D3.js interactive parse trees for Elven grammar.
- [ ] **Audio Generation**: TTS integration that speaks Thalassian with a Silvermoon accent.

---
*World of Warcraft and Blizzard Entertainment are trademarks or registered trademarks of Blizzard Entertainment, Inc. in the U.S. and/or other countries.*
