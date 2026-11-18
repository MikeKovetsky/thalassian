# Bibliography & Sources (Thalassian Conlang)

This document lists the primary canonical sources, community resources, and datamining archives used to reconstruct the Thalassian, Shalassian, and Darnassian lexicons. 

## 1. Official Blizzard Lore & In-Game Texts
- **World of Warcraft (2004 - Present)**
  - *Eversong Woods & Silvermoon City (The Burning Crusade)*: In-game dialogue, NPC greetings, and interactable environmental objects (e.g., "Anar'alah Belore" shrines).
  - *Suramar (Legion)*: Shalassian dialogue, spellcasting quotes, and Ancient Nightborne Tomes. Quotes from First Arcanist Thalyssra, Chief Telemancer Oculeth, and Arcanist Valtrois.
  - *Tempest Keep & Magister's Terrace (The Burning Crusade)*: Boss combat dialogue (Kael'thas Sunstrider, High Astromancer Solarian, Nethermancer Sepethrea).
- **World of Warcraft: The War Within and Midnight (patches 11.2.7 to 12.1.7)**
  - *Shal'na* ("aunt"): Arator to Vereesa in the quest [What Might Come](https://warcraft.wiki.gg/wiki/What_Might_Come#Notes) (11.2.7). Blizzard's zhCN localization renders it 阿姨, "auntie".
  - *Selama ashal'anore* ("Justice for our people"): Vereesa says it and glosses it herself in the quest [A Favor for Kinduru](https://warcraft.wiki.gg/wiki/A_Favor_for_Kinduru) (12.0.7), a second Blizzard source after the 2006 Warcraft Encyclopedia.
  - *Vendel'o eranu* and *Elu'meniel mal alann*: sung by Sylvanas in the quest [Repent of the Highborne](https://warcraft.wiki.gg/wiki/Repent_of_the_Highborne) (11.2.7).
  - *Blizzard's localizations*: the zhCN, zhTW and koKR dialogue tables ([BroadcastText](https://wago.tools/db2/BroadcastText), retail 12.1.7.70892), mined for the elven lines the localizers translated. See the [localization mining report](../research/2026-11-revival/4-localization-mining.md).
  - *Anu'shalla*: the mount [Anu'shalla, Shadow's Guidance](https://warcraft.wiki.gg/wiki/Anu%27shalla,_Shadow%27s_Guidance), an epithet rather than a translation.
  - *Correction (November 2026):* earlier versions of this page cited "leaked Midnight broadcast text" from Vereesa, Halduron and Lor'themar, and an "Anu'shalla Void Owl". Neither existed; the scraper that was meant to collect them was a stub. See the [canon audit](../research/2026-11-revival/1-review-and-methods.md).
- **World of Warcraft: Forever (client 1.60.1.70938, November 2026)**
  - *Game client tables, hotfixes and caches*, read with [tools/wowf](../tools/wowf/): race names (ChrRaces 95 and 96, lore name Shen'dorei), the Shen'dorei language (Languages 310), item, spell, place and name-generator data, and the letter MailTemplate 652. See the [client mining report](../research/2026-11-revival/2-client-mining.md).
  - *Skyborne voice lines*: 196 voice files from the client, all transcribed by Whisper and the 32 that mattered most also by two or three other speech-to-text models. Both NPC voice sets say the farewell *aeesha'el banu zephrali*, and *banu* is in all four of their elvish formulas. See the [voice transcription report](../research/2026-11-revival/5-voice-transcription.md).
  - *Skyborne (Shen'dorei)*: Blizzard's [BlizzCon 2026 panel recap](https://worldofwarcraft.blizzard.com/en-us/news/24304071) gives *shen'dorei* = "hidden people". See the [Skyborne report](../research/2026-11-revival/3-new-elven-race.md).
- **Warcraft Novels & Comics**
  - *Arthas: Rise of the Lich King* by Christie Golden (e.g., Felo'melorn translations).
  - *Stormrage* by Richard A. Knaak.
  - *Day of the Dragon* by Richard A. Knaak.
  - *Blood of the Highborne* (World of Warcraft: Paragons) by Micky Neilson.
  - *Curse of the Worgen* (Comic series).
- **Official Soundtracks & Media**
  - *Lament of the Highborne* (In-game song lyrics).
  - *Voyage to the Sunken City* (Hearthstone Cinematic Trailer song - source for `lura` / sea).

## 2. Developer Statements (Twitter/X & Forums)
- **Sean Copeland (Loreology)**: Lead Historian at Blizzard Entertainment (2014-2018). Numerous tweets confirming exact translations of Elvish phrases (e.g., "Al diel shala", "Ama noral'arkhana", "Anaria shola").
- **Don Adams**: WoW Quest Designer. Confirmed Shalassian as an offshoot of Darnassian and its relation to Thalassian.
- **Christie Golden**: WoW Narrative Director. Confirmed phrases like "Shaha lor'ma" (Thank you).

## 3. Community Wikis & Archives
- **Warcraft Wiki (wiki.gg)**
  - *Thalassian Page*: [warcraft.wiki.gg/wiki/Thalassian](https://warcraft.wiki.gg/wiki/Thalassian)
  - *Darnassian Page*: [warcraft.wiki.gg/wiki/Darnassian](https://warcraft.wiki.gg/wiki/Darnassian)
  - *Shalassian Page*: [warcraft.wiki.gg/wiki/Shalassian](https://warcraft.wiki.gg/wiki/Shalassian)
- **Wowhead Database (wowhead.com)**
  - *Sounds Database*: Extracted NPC Greeting sound files for Blood Elves and Nightborne.
  - *Broadcast Text / Spells*: no Midnight (12.0.1) strings were datamined; earlier versions of this page said so in error (see the correction in section 1).
- **MMO-Champion Forums**
  - Lore discussions regarding the linguistic drift from Darnassian to Thalassian and the translation of boss quotes.

## 4. Fan Linguistics & Conlang Precedents
While this project is strictly **Canon-First**, we acknowledge the foundational work done by the community to map the language over the last 15+ years.
- **Thalassian Redux (Lost Eventide Studios)**: One of the most prominent modern attempts to reverse-engineer Thalassian grammar based on actual phrases. We adapted their observations on agglutination (pronoun suffixes) and SVO structure.
- **Thalassian Language Institute (PBWorks)**: A 2008 project by Fiona Jallings (dreamingfifi) and Ryan "Vintago" Chaddock. While mostly non-canon by modern standards, it pioneered the concept of a full Thalassian dictionary.
- **Feyawen's Warcraft Fonts**: A community project that mapped in-game runic textures (from Silvermoon and Darnassus) into usable TrueType/OpenType fonts, inspiring the Typography Engine of this project.
