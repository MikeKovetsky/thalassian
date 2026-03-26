# Thalassian (Sin'dorei Language Engine)

Engineering a fully functional spoken language based on Thalassian (Blood Elves, World of Warcraft). 
This repository contains the phonotactic engine, the single-source-of-truth lexicon, and eventually the grammar compiler.

## Architecture
- `data/lexicon.json` - Single Source of Truth for canon and generated words.
- `scripts/analyzer.py` - Phonotactic Markov-chain engine to generate new lore-friendly vocabulary based on canon words.

## Usage
Run the analyzer to generate new words:
```bash
python3 scripts/analyzer.py
```