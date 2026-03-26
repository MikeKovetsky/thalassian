# Thalassian (Sin'dorei Language Engine)

Engineering a fully functional spoken language based on Thalassian (Blood Elves, World of Warcraft). 
This repository contains the phonotactic engine, the single-source-of-truth lexicon, and eventually the grammar compiler.

## Architecture
- `data/lexicon.json` - Single Source of Truth for canon and generated words.
- `scripts/analyzer.py` - Phonotactic Markov-chain engine to generate new lore-friendly vocabulary based on canon words.
- `scripts/generator.py` - Root generation script.
- `scripts/scraper_wowhead.py` - Datamine scanner for extracting Elvish words from text dumps.

## Methodology
- [Lexicon Methodology](docs/methodology/lexicon.md) - Our "Canon-First" approach.
- [Typography Methodology](docs/methodology/typography.md) - Runic alphabet integration.

## Usage
Run the analyzer to generate new words:
```bash
python3 scripts/analyzer.py
```

## TODO
- [ ] **Lexicon Combiner**: Створити скрипт для автоматичного об'єднання коренів у нові складні слова.
- [ ] **Grammar Compiler**: Написати правила синтаксису (побудова простих речень).
- [ ] **Web Interface**: Створити фронтенд для перекладача.
- [ ] **Typography / Runes**: Інтегрувати ельфійські рунічні шрифти (TTF/WOFF) для візуального рендерингу перекладеного тексту (деталі в `docs/methodology/typography.md`).
