# Thalassian: The Official Sin'dorei Language Engine

[![GitHub Pages](https://img.shields.io/badge/Live_Demo-Play_Now-d4af37?style=for-the-badge&logo=github)](https://MikeKovetsky.github.io/thalassian/)
[![World of Warcraft: Midnight](https://img.shields.io/badge/Patch-12.0_Midnight-8b0000?style=for-the-badge)](https://MikeKovetsky.github.io/thalassian/)
[![Built with Portal OS](https://img.shields.io/badge/Built_by-Portal_AI-black?style=for-the-badge)](https://portal.ai)

> *“Bal'a dash, malanore. Anu belore dela'na.”*

Welcome to **Thalassian**, the most comprehensive and scientifically reconstructed conlang engine for the Blood Elves (Sin'dorei), High Elves (Quel'dorei), and Void Elves (Ren'dorei) of *World of Warcraft*. 

Unlike older fan wikis that invented vocabulary from thin air, this project strictly adheres to a **Canon-First** methodology. We reverse-engineered the actual phrases datamined from the game (including Darnassian roots, Shalassian archaic forms, and brand new **Patch 12.0 Midnight** datamines) to build a working, speakable Elven language.

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

Our engine understands agglutinative grammar (pronouns attach to verbs, prepositions are dropped, adjectives precede nouns).

*   **English:** *"The sun guides us."*
    **Thalassian:** `Belore dela'na.` *(Canon match)*
*   **English:** *"Rise, dead ones!"*
    **Thalassian:** `Aranal, ledel!` *(Extrapolated from Prince Keleseth)*
*   **English:** *"Justice for our great people."*
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

- `src/thalassian/data/lexicon.json` - The Single Source of Truth database for 200+ canon and phonotactically generated roots.
- `src/thalassian/syntax/parser.py` - The NLP Grammar Compiler (using AST and `spaCy` to parse English and compile SVO Elven grammar).
- `src/thalassian/phonetics/markov.py` - A Phonotactic Markov-chain engine to generate new vocabulary that sounds 100% lore-friendly.
- `src/thalassian/morphology/` - Rules for agglutination and vocalic mutation (pluralization).

### Dive deeper into our methodology:
1. 📖 **[Lexicon Methodology (Canon-First)](docs/methodology/lexicon.md)**
2. 📜 **[Grammar Methodology (AST & Agglutination)](docs/methodology/grammar.md)**
3. 🖋️ **[Typography Methodology (Runic Visuals)](docs/methodology/typography.md)**
4. 📚 **[Bibliography & Sources (Citations)](docs/citations.md)**
5. 🤖 **[Architecting with Portal OS (How an AI built this)](docs/methodology/how-to-use-portal.md)**

---

## 🚀 Future Roadmap
- [x] **Lexicon Combiner**: Script to automatically merge roots into complex nouns.
- [x] **Grammar Compiler**: Syntax rules (SVO, pluralization, pronoun agglutination).
- [x] **Web Interface**: Multi-mode translator hosted on GitHub Pages.
- [x] **Midnight (12.0) Datamining**: Integrate the newest canonical words (`Shal'na`, `Anu'shalla`).
- [x] **Typography Engine**: Integrated Elvish Runic fonts for visual rendering in the web app.
- [x] **Reverse Translator**: Auto-detects Elvish and translates back to English.
- [x] **Syntax Tree Visualizer**: D3.js interactive parse trees for Elven grammar.
- [ ] **Audio Generation**: TTS integration that speaks Thalassian with a Silvermoon accent.

---
*World of Warcraft and Blizzard Entertainment are trademarks or registered trademarks of Blizzard Entertainment, Inc. in the U.S. and/or other countries.*
