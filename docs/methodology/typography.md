# Typography Methodology

This document outlines the approach to visually rendering the Thalassian language using in-game runes.

## 1. Analysis of In-Game Inscriptions
In World of Warcraft, there are numerous objects with Elven inscriptions (signposts in Eversong Woods, the portal in Darnassus, magical books in Dalaran/Suramar, glowing runes on weapons like Felo'melorn).
However, analysis reveals that Blizzard artists mostly used these inscriptions as decorative patterns (an Elven equivalent of *Lorem Ipsum*), which cannot be directly cryptographically translated into an alphabet.

## 2. Visualization Approach (Runic Integration)
Since the original textures do not contain ciphered text, we do not attempt to translate them. Instead, we use a reverse approach:
- We integrate fan-compiled runic alphabets (e.g., from the *Feyawen's Warcraft Fonts* project), which are based on real textures from the game.
- These alphabets allow us to create a fully custom font (TTF/WOFF) for our web interface.

## 3. Practical Application
When a user inputs text for translation (e.g., *"Glory to the elves"*):
1. The **Grammar Compiler** translates it into Thalassian (e.g., *"Zin'dorei"*).
2. The **Typography Engine** automatically renders this result on the screen using authentic golden runes.
3. The user can take a screenshot of the result (perfect for tattoos, avatars, or RP profiles).

This adds maximum authenticity and visual appeal for the World of Warcraft community.
