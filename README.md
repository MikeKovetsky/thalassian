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
*   **English:** *"I work on a new project today."* (Modern conversational)
    **Thalassian:** `Carth'o neal shola sira.` *(Generated via phonotactic engine)*

---

## 🏗️ Project Architecture

We treat conlanging as software engineering. 

- `data/lexicon.json` - The Single Source of Truth database for 100+ canon and phonotactically generated roots.
- `src/thalassian/grammar_en.py` - The NLP Grammar Compiler (using `spaCy` to stem English and compile SVO Elven grammar).
- `src/thalassian/analyzer.py` - A Phonotactic Markov-chain engine to generate new vocabulary that sounds 100% lore-friendly.
- `src/thalassian/scraper_wowhead.py` - A datamine scanner built to extract Elvish apostrophized words from raw WoW text dumps (e.g., Midnight expansion files).

### Dive deeper into our methodology:
1. 📖 **[Lexicon Methodology (Canon-First)](docs/methodology/lexicon.md)**
2. 🖋️ **[Typography Methodology (Runic Visuals)](docs/methodology/typography.md)**

---

## 🚀 TODO & Future Roadmap
- [x] **Lexicon Combiner**: Script to automatically merge roots into complex nouns (e.g., `felo` + `alar` = `Felo'alar` / Fire Phoenix).
- [x] **Grammar Compiler**: Syntax rules (SVO, pluralization, pronoun agglutination).
- [x] **Web Interface**: Multi-mode translator hosted on GitHub Pages.
- [x] **Midnight (12.0) Datamining**: Integrate the newest canonical words (`Shal'na`, `Anu'shalla`).
- [ ] **Typography Engine**: Integrate custom TTF/WOFF Elvish Runic fonts for visual rendering in the web app.
- [ ] **Reverse Translator**: Convert Thalassian back to English.
- [ ] **Audio Generation**: TTS integration that speaks Thalassian with a Silvermoon accent.

---
*World of Warcraft and Blizzard Entertainment are trademarks or registered trademarks of Blizzard Entertainment, Inc. in the U.S. and/or other countries.*
