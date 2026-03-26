# Lexicon Methodology (Canon-First Approach)

This document outlines the strict "Canon-First" methodology used to construct and expand the Thalassian language.

## 1. The Problem with Legacy Projects
Most existing fan projects (e.g., the PBWorks wiki from 2008) relied heavily on inventing words from scratch due to a lack of available lore at the time. This resulted in legacy dictionaries that starkly contradict the official canon released by Blizzard (particularly by Loreology between 2014-2024).

**Our Goal:** Zero random inventions. We build the language based on etymology, linguistic drift, and verified existing roots.

## 2. Canon-First Approach (Root Gathering)
All words in `data/lexicon.json` are gathered exclusively from three official lore dialects:
1. **Thalassian (High Elves / Blood Elves / Void Elves):** The primary modern dialect.
2. **Darnassian (Night Elves):** The ancestral language. We extract base roots (e.g., `drassil` - crown, `kal` - stars) to understand word formation. We also study linguistic drift (e.g., Darnassian `Falo` -> Thalassian `Felo`).
3. **Shalassian (Nightborne / Suramar):** An archaic dialect preserved under the dome. It provides access to ancient Highborne roots.

Each gathered word is broken down into attributes: `word`, `root`, `translation` (EN/UK), `pos` (part of speech), `canon` (boolean flag), and `source` (dialect).

## 3. Lexicon Expansion (Extrapolation)
Because Blizzard did not provide a full Swadesh list (the basic 100-200 words needed for communication), we expand the language using two tools:

### A. Phonotactic Generator (New Roots)
For words that do not exist in the lore (e.g., "water", "stone", "run"), we do not invent them manually. A Markov-chain algorithm analyzes the frequency of letter combinations and syllables in our 75+ canon roots to generate entirely new roots that sound 100% lore-friendly (e.g., `Thela`, `Falol`). These words are marked with `canon: false`.

### B. Lexicon Combiner (Complex Words)
Using the database of canon and generated roots, we create complex words following Elvish compounding rules (reverse order or seamless merging). For example:
- `thas` (forest) + `aran` (city) = **Thas'aran** (Forest City)
- `sin` (blood) + `dash` (path) = **Sindash** (Blood Path)

## 4. Datamining (Midnight and Future Patches)
To keep the dictionary updated, we use `scraper_wowhead.py`. This tool parses text dumps of dialogues (e.g., from the *World of Warcraft: Midnight* expansion, which focuses on Quel'Thalas) and extracts new words based on linguistic patterns (apostrophes, specific endings), filtering out English text. These words are added to the database as new canon roots.
