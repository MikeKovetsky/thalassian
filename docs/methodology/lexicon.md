# Lexicon Methodology (Canon-First Approach)

This document describes how the Thalassian lexicon (`src/thalassian/data/lexicon.json`) is built and how each entry records how much of it is canon.

## 1. The problem with legacy projects
Most older fan projects (for example the PBWorks Thalassian Language Institute from 2008) invented much of their vocabulary because little lore was available. Many of those words contradict what Blizzard later published.

**Our goal:** never present an invention as canon. Invented and inferred words are allowed, because a usable language needs them, but every entry says what it rests on.

## 2. Canon sources
Canon meanings come only from Blizzard: in-game text that gives an English gloss, Blizzard developer statements (for example Loreology), official books, and Blizzard's own localizations of elven lines. The lexicon draws on four lore dialects:
1. **Thalassian** (High Elves, Blood Elves, Void Elves): the main modern dialect.
2. **Darnassian** (Night Elves): the ancestral language and the source of many shared roots.
3. **Shalassian** (Nightborne of Suramar): an archaic Highborne dialect.
4. **Skyborne** (Shen'dorei of WoW Forever, added November 2026): a Darnassian dialect; players of the race learn "Language: Darnassian". See [the Skyborne report](../../research/2026-11-revival/3-new-elven-race.md).

## 3. Entry fields
Each entry has `word`, `translation` (`en`, `uk`), `pos`, `canon`, `root`, `notes` and `source` (the dialect, or `generated` / `generated_swadesh` / `extrapolated` for invented words).

Since November 2026 every entry also has `canon_basis`:

| canon_basis | canon | Meaning |
|---|---|---|
| `attested` | true | Blizzard glossed this word or phrase itself. |
| `segment` | true | A piece cut out of a Blizzard-glossed phrase or compound; the meaning is inferred from the glossed whole. |
| `epithet` | true | A name Blizzard pairs with an English epithet (for example *Eluvi'ana, the Night Dancer*); the epithet may not be a literal translation. |
| `name` | true or false | A name whose referent Blizzard states (a place, a race, a faction), without a word-for-word meaning. |
| `inferred` | false | Meaning inferred by alignment, segmentation, comparison or context. |
| `generated` | false | Invented for this project (see section 4). |
| `unverified` | false | Formerly marked canon, but no Blizzard source supports the meaning (demoted in the November 2026 audit). |

Entries added since November 2026 also carry `confidence` (high or medium), `method` and `evidence` (the exact quote and where it is: a URL, or a client table and row ID). Low-confidence candidates are kept out of the lexicon and stay in the `research/2026-11-revival/*-candidates.json` files.

## 4. Filling the gaps
Blizzard never provided a full basic vocabulary, so the lexicon fills gaps in two ways, always with `canon: false`:

### A. Generated words
- **March 2026:** 62 roots from the Markov-chain generator in `src/thalassian/phonetics/markov.py`, and 57 Swadesh-list words written by an LLM (see [how-to-use-portal.md](how-to-use-portal.md)), marked `generated_swadesh`.
- **November 2026 audit:** a classifier tells these generated words apart from canon fairly easily, and six of them were identical to attested forms or to words from Blizzard's in-game language scrambler. Those collisions and the generated words that duplicated a canon meaning were removed. A better generator (an order-4 Kneser-Ney model with phonotactic and collision filters) is described in [the audit](../../research/2026-11-revival/1-review-and-methods.md#method-7-phonotactic-model) and is not yet wired in.

### B. Inferred words and compounds
Meanings are inferred by aligning glossed phrases word by word, by segmenting glossed compounds, and from context. Elvish compounds put the modifier first and the head last: `thas` (forest) + `alah` (light) = **Thas'alah**, "Light of the Forest"; `sin` (blood) + `dorei` (children) = **Sin'dorei**.

## 5. Datamining
- **March 2026:** the project cited a "Midnight 12.0 datamine", but the scraper (`scripts/scraper_wowhead.py`, since deleted) was a stub and collected nothing. The three words it was credited with came from other sources; see the [canon audit](../../research/2026-11-revival/1-review-and-methods.md).
- **November 2026:** `tools/wowf/` reads the WoW Forever game client directly (its CASC storage, DB2 tables, hotfix cache and quest caches). The raw extract stays local in the gitignored `.wowf-extract/` folder. See the [client mining report](../../research/2026-11-revival/2-client-mining.md).
