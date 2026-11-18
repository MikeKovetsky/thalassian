# The new elven race in WoW: Forever: the Skyborne (shen'dorei)

**Race:** the **Skyborne**, who call themselves the **shen'dorei**, "hidden people". They are the only new playable race in *World of Warcraft: Forever* (product `wowf`, client 1.60.1). Blizzard announced it at BlizzCon on 2026-09-12 ([Game Informer, 2026-09-12](https://gameinformer.com/blizzcon-2026/2026/09/12/blizzard-announces-world-of-warcraft-forever-expanding-vanilla-wow-with)) and it went live with patch 1.60.1 on 2026-11-04.

**Language:** guides and the wiki say Darnassian for both factions, the same language as the night elves ([Warcraft Tavern race guide](https://www.warcrafttavern.com/forever/guides/skyborne/), [Skyborne (playable) on warcraft.wiki.gg](https://warcraft.wiki.gg/wiki/Skyborne_%28playable%29)). The client confirms this: both Skyborne races learn "Language: Darnassian" (`SkillRaceClassInfo` row 42). The client also defines a language row of its own, `Languages` 310, **"Shen'dorei"**, whose garble words are identical to Darnassian's, but no player skill uses it (details in the client-check section below). The Skyborne speak an isolated variety of it: their ancestors left Eldre'Thalas (Dire Maul) and lived for thousands of years in Skywall, the Elemental Plane of Air. Their names show distinct sound patterns (see the sound-change notes below).

**New words:** this research proposes 20 additions and 2 corrections in [3-candidates.json](3-candidates.json). Six additions came from the Zephras follow-up (see "Zephras and zepharaalis" below) and one from the client check (`zaalanarr`). Every entry now carries its client location, or the note "not found" after a search of the dump.

| Confidence | Additions | Corrections |
|---|---|---|
| High | 7: `shen'dorei`, `shen`, `shal'nan`, `al'aketh`, `shen'dralar`, `zephras`, `zephrali` | `dorei` gains "people" |
| Medium | 10: `eluvi'ana`, `urs`, `ursera`, `naar`, `dralar`, `zephar`, `zepharaalis`, `as`, `aeesha'el banu zepharaalis`, `zaalanarr` | `shal` gains "veil" |
| Low | 3: `nan`, `aeesha'el`, `banu` | none |

Five additions are canon (`canon: true`) because a Blizzard source states their meaning or referent: `shen'dorei`, `shal'nan`, `al'aketh`, `shen'dralar` and `zephras`. Every other addition is inferred, and its `method` field names how.

**Why the source value is `skyborne`.** Players speak Darnassian, and the client's own "Shen'dorei" language row (310) reuses Darnassian's garble words, so this is a dialect of Darnassian, not a new language. It counts as a distinct dialect for this project for four reasons:

1. The client gives it its own language row, even though no player skill uses it.
2. Lore separates its speakers from the night elves for about 7,000 to 10,000 years. Blizzard's own texts give both figures.
3. Its names follow their own sound patterns: doubled vowels, Darnassian `fal-` and the `zephar-` stem.
4. Its words come from a separate product.

Tagging them `skyborne` keeps them filterable. If the main session prefers one `darnassian` tag, it only needs to change the field, because each `notes` field already says "Darnassian (Skyborne dialect)". Three entries are tagged `darnassian` because they are older or shared Darnassian: `shen'dralar`, `dralar` and `naar`. `naar` was changed to `darnassian` to match 2-candidates.json.

**Status:** phase 1 (web) and phase 2 (client dump, `.wowf-extract/` per its README, build 1.60.1.70938) are both done. Two things remain open. The voice files need transcription, which needs the user's go for a speech-to-text model. Zephras Isle quest and book text is server-side, so it needs a Skyborne character to play the zone and fill the cache.

## Client check (phase 2)

### What the client settles

1. **Players speak Darnassian.** `SkillRaceClassInfo` row 42 ("Language: Darnassian", Availability 1) has the race mask Night Elf + High Order Skyborne + Windshaper Skyborne (PlayableRaceBit 3, 32, 33). Row 40 gives Common to High Order, and row 48 gives Orcish to Windshapers.
2. **The "Shen'dorei" language row has no skill.** `Languages` 310 "Shen'dorei" exists, and its 102 `LanguageWords` are identical to Darnassian's (ID 2), but no `SkillLine` teaches it. It is probably reserved for NPC speech; no cached `BroadcastText` line carries LanguageID 310.
3. **Every *-dorei* race name is a lore name in `ChrRaces`:** Kaldorei (4), Sin'dorei (10), Shal'dorei (27), Ren'dorei (29) and Shen'dorei (95, 96). This supports the `dorei` "people" correction.
4. **Spellings settled by the client:**
   1. **Valanaar**, not "Valinaar" (`AreaTable` 16638).
   2. **Al'Aketh** with a capital A in all 74 strings. The wiki's lower-case "Al'aketh" is not in the client.
   3. **Rohashi Spires** in `AreaTable` 16630, but **Rohaashi Spires** in `SpellName` 1259410 ("Portal to Rohaashi Spires") and in `UiWidgetStringSource` 21041. The Skyborne doubled vowel is optional in spelling (see the sound-change notes).
5. **Not in the client:** *Shal'nan*, *shan'dorei*, *Talaanis/Talanis*, *Ayessa*, *Rorian*, *Saeyleenan*, *Ur'endra*, *Den'dralass*, *Tel'daeor*, *New Eldre'naar*, *Eldranaar*, *Eldre'narr*, *Shen'dramar*, *Siroccas* and *Anvilas*. All are quest, book or NPC text sent by the server. No Zephras Isle quest is cached (README, "Known gaps" 2).

### Each candidate, checked against the dump

| Entry | Client location | Result |
|---|---|---|
| `shen'dorei` | ChrRaces 95, 96 (Lore_name); Languages 310; Faction 2748; Faction 2778 description; MailTemplate 652; SpellName 1253151; Creature 273554; ItemSparse 271722 onward (33 items) and 280740; TransmogSetGroup 393 | Confirmed |
| `shen` | AreaTable 16623, 16624 (Shen'dar), 16651 (Shen'dralas); Faction 809 (Shen'dralar) | Confirmed as a stem; its gloss comes from the web |
| `shal'nan`, `nan` | None | Not in client |
| `al'aketh` | Faction 2749; ItemSparse 255658, 258771, 271756 and others; 24 common items 277056 to 277079 | Confirmed |
| `eluvi'ana` | ItemSparse 276188 (hotfix 17053404, Description "The Night Dancer."); Spell 1314923 | Confirmed |
| `urs` | ItemSparse 252665 "Head of Urs'anah", 263435 "Mark of Urs'endris" | Confirmed |
| `ursera` | ItemSparse 251918, 251925 ("Tattered Ursera Feather"), 263183, 263184 | Confirmed; the gloss now says "feathered" |
| `naar` | AreaTable 16638, 16628, 186, 415, 489; ItemSparse 277136 (Vord'anaar), 252023 (Zaalanarr) | Confirmed |
| `zephras`, `zephrali`, `zephar`, `zepharaalis`, `as` | AreaTable 16593, Map 2991, UiMap 2521, Faction 2757; ItemSparse 277080 to 277111; NameGen 25277, 25363, 25449, 25535; AreaTable 16651 | Confirmed |
| `aeesha'el banu zepharaalis`, `aeesha'el`, `banu` | MailTemplate 652 only | Found once; no other occurrence |
| `shen'dralar`, `dralar` | Faction 809; hotfix BroadcastText 313613, 302214; ItemSparse 260627, 277559 | Confirmed |
| Correction `dorei` | ChrRaces 4, 10, 27, 29, 95, 96 | Supported |
| Correction `shal` | None for "veil" | The web gloss stands alone |

### New from the client

1. **`zaalanarr` (new, medium).** "Zaalanarr Sharp" (`ItemSparse` 252023) sits among the Zephras Isle items. It has exactly the stats and price of the night elf starter cheese Darnassian Bleu (item 2070: item level 5, required level 1, buy price 25, sell price 1). It is named like "Dalaran Sharp" (item 414), which takes its name from Dalaran, so Zaalanarr is presumably a Skyborne place. It has the *-narr* ending of Eldre'narr. It appears nowhere on the web.
2. **Elvish Skyborne names in `NameGen`.** Of 86 family names, only two are not English compounds: **Zephraalis** and **Siroccaa** (see "Zephras and zepharaalis"). Of 149 given names, most are elvish-looking, but they carry no meaning in the client, so none are proposed. A few come from outside Warcraft: Beren, Imrahil, Dagda, Ciaran. Several echo place stems: Zepha, Sirocaas, Siroca, Valaan, Cyclaas. Many show the doubled vowel: Aae, Aaem, Aashri, Alaan, Algaan, Ariaa, Beliaa, Elransiaal, Emaa, Lokaa, Raan, Raani, Rowenvaa, Tevaan, Valaan, Vraal, Zhaal, Zriaal.
3. **Camp Gev'rek** (`AreaTable` 17223, parent 215 Mulgore) is the Windshapers' camp. Its name looks Taur-ahe or Orcish rather than elvish, so it is not proposed.
4. **No new elvish titles, mounts, achievements or currencies.** `CharTitles`, `Mount`, `Achievement` and `CurrencyTypes` have nothing Skyborne beyond English names (Galestrider and similar) and "Explore Shen'dralas" (`Achievement` 63684).

### Where this file disagrees with 2-candidates.json

| Entry | 2-candidates.json | This file | Why |
|---|---|---|---|
| `shen` | medium | high | Two independent Blizzard glosses: shen'dorei "hidden people" and Shen'dralar "Those Who Remain Hidden" |
| `eluvi'ana` | "an ancient Shen'dorei spirit", canon | "the Night Dancer (a sword)", not canon | ItemSparse 276188 is a one-hand sword. Spell 1314956 binds an unnamed "ancient Shen'dorei spirit" using the hilt of Eluvi'tor; it does not name the spirit Eluvi'ana. |
| `zephras` | low | high | The referent is stated by Blizzard (area, map and race intro text) |
| `aeesha'el banu zepharaalis` | low, "not translated" | medium, a gloss offered | Matched with the surname Zephraalis, plus the letter's closing slot |
| `naar` | source `darnassian` | changed to `darnassian` | Now agrees |

Same words in both files, with this file's client evidence added: `shen'dorei`, `shen'dralar`, `ursera` (which gains "feathered" from their drops) and the `dorei` correction. Their proper-noun entries (valanaar, shen'dar, thendal, falaath, ban'aethal, eluvi'tor, eldre'thalas, shen'dralas) are not duplicated here.

### The 10 voice files most worth transcribing

All are in `.wowf-extract/skyborne_vo/sound/`. The meaning of each comes from the emote or NPC slot that plays it. The blood elf lines in the same slots are elvish, for example /hello "Bal'a dash, malanore" ("Greetings, traveler").

| # | File | Slot | What it should say |
|---|---|---|---|
| 1 | `character/skyborne_elf_male/vo_skyborne_elf_male_hello_7744494.ogg` (kit 341062, the longest male /hello) | /hello | A greeting, perhaps the elvish form of "Gale's greetings" |
| 2 | `character/skyborne_elf_female/vo_skyborne_elf_female_hello_7744900.ogg` (kit 341194) | /hello | A greeting |
| 3 | `character/skyborne_elf_male/vo_skyborne_elf_male_bye_7744488.ogg` (kit 341056) | /bye | A farewell, perhaps "Aeesha'el banu zepharaalis" or "Winds be with you" |
| 4 | `character/skyborne_elf_female/vo_skyborne_elf_female_bye_7744894.ogg` (kit 341188, the longest /bye) | /bye | A farewell, the best chance of a full formula |
| 5 | `character/skyborne_elf_male/vo_skyborne_elf_male_thank_7744512.ogg` (kit 341080) | /thank | "Thank you" (the Darnassian is *Shaha lor'ma*) |
| 6 | `character/skyborne_elf_female/vo_skyborne_elf_female_thank_7744920.ogg` (kit 341215) | /thank | "Thank you" |
| 7 | `character/skyborne_elf_male/vo_skyborne_elf_male_charge_7744475.ogg` (kit 341043) | /charge | A battle cry, perhaps "Shal'nan!", which the books call the rebels' cry |
| 8 | `character/skyborne_elf_female/vo_skyborne_elf_female_yw_7997896.ogg` (kit 355489) | /yw | "You're welcome" |
| 9 | `creature/7478487/7478487_greetings_7744809.ogg` (NPCSounds 3775, the longest NPC greeting) | Skyborne NPC greeting | What a Skyborne NPC says when clicked |
| 10 | `creature/7478487/7478487_farewell_7744803.ogg` (NPCSounds 3775, the longest NPC farewell) | Skyborne NPC farewell | What a Skyborne NPC says when you leave, perhaps the letter's farewell blessing |

No speech-to-text model is installed, and none was downloaded. A person can also listen to these ten files (228 KB in all) and write down what they hear.

## Sources used

1. Blizzard, [World of Warcraft: Forever Found Photos Panel Recap](https://worldofwarcraft.blizzard.com/en-us/news/24304071) (2026-09-13). It states the meaning of shen'dorei: "the Skyborne, also known as the shen'dorei or hidden people".
2. Blizzard, [WoW: Forever Meet the New Skyborne](https://news.blizzard.com/en-us/article/24302071/wow-forever-meet-the-new-skyborne). It covers the Windshapers, the High Order and Eldre'Thalas, and calls them "shen'dorei high elves".
3. Blizzard, [Create the Hero You Want to Be in World of Warcraft: Forever](https://news.blizzard.com/en-us/article/24304075/create-the-hero-you-want-to-be-in-world-of-warcraft-forever). It covers the race and its class combinations.
4. In-game texts, as transcribed by warcraft.wiki.gg with object, quest, item and NPC IDs. Page links are in the tables below. The lore summary is the [Skyborne](https://warcraft.wiki.gg/wiki/Skyborne) article, with its [Language section](https://warcraft.wiki.gg/wiki/Skyborne#Language).
5. warcraft.wiki.gg [Darnassian](https://warcraft.wiki.gg/wiki/Darnassian) and [Shen'dralar](https://warcraft.wiki.gg/wiki/Shen%27dralar), for older canon glosses.
6. Warcraft Tavern [Zephras Isle walkthrough](https://www.warcrafttavern.com/forever/guides/zephras-isle-walkthrough/), for the full list of quest, NPC and item names.

Several sources could not be used. Wowhead has no Skyborne vocabulary datamining post that search could find. Icy Veins' lore article returned HTTP 403. MMO-Champion turned up nothing. The BlizzCon "Found Photographs" panel video was not watched. The wiki cites it, but only the Blizzard recap above was read.

## Phrase table

### A. Meanings stated by Blizzard

| Phrase | Meaning | Source | Segmentation |
|---|---|---|---|
| **shen'dorei** | "hidden people": the Skyborne's own name, used for one person or for the people | [Blizzard recap](https://worldofwarcraft.blizzard.com/en-us/news/24304071); in game: "I am no "quel'dorei"... I am shen'dorei." ([Lumina Windsinger, quest 91862](https://warcraft.wiki.gg/wiki/Lumina_Windsinger_%28quest%29)) | **shen** "hidden" (NEW) + **dorei** "children, people" (lexicon, canon). Lumina contrasts it with quel'dorei, which shows that `shen` fills the modifier slot that `quel` "high" fills. |
| **Shal'nan** | "The Veiled One": the masked leader of the Eldre'Thalas rebellion. His name "became a battle cry synonymous with rebellion." | Audio crystal [The Rebellion in Eldre'Thalas, Part 3](https://warcraft.wiki.gg/wiki/The_Rebellion_In_Eldre%27Thalas,_Part_3) (object 658840); also [On the Shal'nan](https://warcraft.wiki.gg/wiki/On_the_Shal%27nan) (658836). warcraft.wiki.gg lists it among the Blizzard-confirmed [Darnassian](https://warcraft.wiki.gg/wiki/Darnassian) translations. | **shal** "night, shadow" (lexicon), here "veil, concealment", + **nan** "one (who is)" (NEW, low). |
| **Shen'dralar** | "Those Who Remain Hidden": the Highborne house of Eldre'Thalas that the Skyborne came from. This gloss predates Forever. | *World of Warcraft: Chronicle Volume 1*. The wiki cites p. 133 on its [Shen'dralar](https://warcraft.wiki.gg/wiki/Shen%27dralar) page and p. 139 on its [Darnassian](https://warcraft.wiki.gg/wiki/Darnassian) page. | **shen** "hidden" + **dralar** "those who remain". This is an independent check on `shen`. |
| **Al'Aketh** | The cult of Al'Akir the Windlord on Zephras Isle | [Blizzard recap](https://worldofwarcraft.blizzard.com/en-us/news/24304071) (named as one of three factions); BlizzCon panel, cited on the [Skyborne](https://warcraft.wiki.gg/wiki/Skyborne) page | **Al'** + **Aketh**, built on Al'Akir. `Al'` comes off: "Shrine of Akir", "Mark of Akir". Literal meaning unknown; perhaps "those of Akir" (low). |

### B. A name with an English epithet but no stated translation

| Phrase | Epithet or role | Source | Segmentation |
|---|---|---|---|
| **Eluvi'ana** | Item flavor text "The Night Dancer.": Luminarian's sword. Spell 1314923's aura text reads "Raising Eluvi'ana, the Night Dancer." | [Eluvi'ana](https://warcraft.wiki.gg/wiki/Eluvi%27ana) (item 276188, confirmed in client `ItemSparse`); [quest 97029](https://warcraft.wiki.gg/wiki/Eluvi%27ana_%28quest%29) | **eluvi**, probably from Elune (moon, night; compare Elun'dris "Eye of Elune"), + **ana**. If the epithet is a translation, then *ana* means "dancer". That would clash with the lexicon's `ana` "fare, status" (see the contradictions section). |
| **Eluvi'tor** | Twin of Eluvi'ana (Ancient Hilt) | [Ancient Hilt](https://warcraft.wiki.gg/wiki/Ancient_Hilt) (items 272313, 282315) | **eluvi** + **tor**. Compare *Shalla'tor* "Shadow Render" (canon) and *Jai'alator*. Perhaps "Night Render" (speculative; not proposed). |
| **Urs'endris** | "The Great Windborne Bear Spirit": he teaches Bear Form | [Urs'endris](https://warcraft.wiki.gg/wiki/Urs%27endris) (NPC 255853) | **urs** "bear" (NEW, medium) + **endris** |
| **Urs'anah** | "The Den Mother" (an ursera) | [Urs'anah](https://warcraft.wiki.gg/wiki/Urs%27anah) (NPC 251115) | **urs** + **anah** |
| **Ur'endra** | "Mate of Urs'endris" (a female ursera) | [Ur'endra](https://warcraft.wiki.gg/wiki/Ur%27endra) (NPC 258443) | **ur(s)** + **endra**. The pair *endris* (male) and *endra* (female) hints at gender endings `-is` and `-a` (low; not proposed). |
| **Ur'seris** | The creature the player helps in Shadowgale Forest | [Skyborne#Language](https://warcraft.wiki.gg/wiki/Skyborne#Language) | Perhaps *urs + seris* with the double s simplified (see the sound-change notes) |
| **Den'dralass** | "The Great Mother" (a rare ursera) | [Den'dralass](https://warcraft.wiki.gg/wiki/Den%27dralass) (NPC 250936) | **den** + **dralass**, which echoes *Shen'dralas* and *Shen'dralar* |
| **Saeyleenan** | "The Great Windborne Cat Spirit": it teaches Cat Form | [Skyborne](https://warcraft.wiki.gg/wiki/Skyborne) (Druidism section) | Cannot be analysed |
| **ursera** | Bear-like beast family native to Zephras | [Urs'endris](https://warcraft.wiki.gg/wiki/Urs%27endris), [Den'dralass](https://warcraft.wiki.gg/wiki/Den%27dralass) | **urs** + **-era** (collective or kind). Compare Ursoc and Ursol. |
| **Tel'daeor the Stormspeaker** | An Al'Aketh rare | [Tel'daeor the Stormspeaker](https://warcraft.wiki.gg/wiki/Tel%27daeor_the_Stormspeaker) (NPC 259385) | **tel** "earth" (lexicon) + **daeor**. This fits poorly with "Stormspeaker", so it is not proposed. |

### C. The one untranslated Skyborne sentence

| Phrase | Context | Source | Segmentation |
|---|---|---|---|
| **Aeesha'el banu zepharaalis** | It is the closing salutation of Lotheluum Starbreeze's letter thanking the player for helping Ur'seris and protecting Shadowgale Forest. It stands right before the signature and right after "I am unsure where the winds will lead you". The wiki gives its meaning as unknown. | Client `MailTemplate` 652 (Body); [Skyborne#Language](https://warcraft.wiki.gg/wiki/Skyborne#Language) | **aeesha'el** (perhaps *aeesha* + **el** "peace", lexicon; low) · **banu** (perhaps **ban** "gate, passage" + *-u*; low) · **zepharaalis** = **Zephra(s) + -alis** "of Zephras", the same word as the client surname *Zephraalis* (medium-high). The whole phrase is a farewell blessing naming the homeland (medium). Details are in "Zephras and zepharaalis" below. |

### D. Place names (in-game; no meaning stated)

| Name | What it is | Segmentation and notes |
|---|---|---|
| **Zephras Isle** | The starting island in Skywall ([Zephras Isle](https://warcraft.wiki.gg/wiki/Zephras_Isle), area 16593) | **zephr** "zephyr" + **-as** "place". Derived forms: *Zephrali* and *Zephraalis* (see "Zephras and zepharaalis" below). Spells: "Blessing of Zephras"; items: "Zephyrseeds", "Enchanted Gyrozephyr". |
| **Valanaar** | The capital | **vala** + **naar** "settlement" (NEW, medium). Compare *Dolanaar* and *Astranaar*. One wiki page spells it "Valinaar"; the client confirms **Valanaar** (`AreaTable` 16638). |
| **New Eldre'naar** / "Eldranaar" | A Skyborne town on another island | Named after the port **Eldre'narr** in Feralas, where the exiles set sail. A Zephras Citizen says "Eldranaar" ([Zephras Citizen](https://warcraft.wiki.gg/wiki/Zephras_Citizen)). See the sound-change notes. |
| **Shen'dramar** | A Skyborne town on another island | **shen** "hidden" + *dramar*. Compare Shen'dralar and Suramar. |
| **Shen'dar Village**, **Shen'dar Highlands** | A highland settlement | **shen** "hidden" + *dar* |
| **Thendal Village**, **Thendal Grove**, **Thendal Cave**, **Thendal Standing Stones** | The starting village | Unknown; perhaps *th-* + **endal** "breath" (lexicon). Speculative, not proposed. |
| **Falaath Village** | A village | **fal** (Darnassian vowel, not Thalassian *fel*) + *aath* |
| **Ruins of Ban'aethal** | A ruined magesmith town | **ban** "gate, passage" (lexicon) + *aethal* (compare "aether": *Aetheen of the Gales*, *Anathamaas Aetherwind*) |
| **Rohashi Spires** (client also "Rohaashi") | Named after Rohash, Lord of the East Wind | **Rohash** + **-i**, an adjectival or genitive ending ("of Rohash"). `AreaTable` 16630 has "Rohashi"; `SpellName` 1259410 and `UiWidgetStringSource` 21041 have "Rohaashi". |
| **Zaalanarr** (client only) | A place, known only from the starter cheese "Zaalanarr Sharp" (`ItemSparse` 252023) | *zaala* + **-narr**, a variant of **-naar** "settlement" (compare Eldre'narr). NEW, medium. |
| **Shrine of Akir** (formerly Shrine of the Four Winds) | The Al'Aketh temple | Akir without **Al'** |
| **Anvilas**, **Siroccas** | Other Skyborne islands | Built on English or Latin roots (anvil, sirocco) plus Darnassian-looking *-as*. Not proposed. |
| **Shen'dralas** | A new Forever zone south-east of Desolace: Highborne ruins, not Skyborne ([Shen'dralas](https://warcraft.wiki.gg/wiki/Shen%27dralas), area 16651) | **shen** + **dralas**. Compare Shen'dralar. |

### E. Item, faction and spell names with elvish parts

Item names that use the ethnonym as an adjective: Shen'dorei Signet, Shen'dorei Tabard, Shen'dorei Standard, Shen'dorei Windwell, Handmade Shen'dorei Pillow, and the "Ensemble: Shen'dorei Skyseer's / Magister's / Peacekeeper's Garb" sets. These show that **shen'dorei** also works as an adjective. The wiki spells the armor sold by Brother Zendraas with a lower-case *a*, "Al'aketh", but the client has **Al'Aketh** in all 74 strings. That includes 24 common items, 277056 to 277079, which sit right before the 32 Zephrali items. The Elunar Longstaff drops from Den'dralass. Factions, spells and mounts all have English names: High Order, Windshapers, Nightclaw Druids, Peacekeepers, Empyrean Blades, Walk on Air, Wind Blessed, Elemental Insight, Read Leyline, Skysight, Galestrider.

### F. Spoken formulas (English only; no elvish form attested)

| Formula | Use | Source |
|---|---|---|
| "Gale's greetings" | Greeting | [Coming of Age, quest 92460](https://warcraft.wiki.gg/wiki/Coming_of_Age_%28Forever%29) |
| "Winds be with you" | Farewell | [What Comes Next (Horde), quest 93090](https://warcraft.wiki.gg/wiki/What_Comes_Next_%28Horde%29) |
| "May the winds guide you" / "...guide your path" | Farewell, blessing | [The Next Step, quest 92472](https://warcraft.wiki.gg/wiki/The_Next_Step_%28Skyborne%29) |
| "I'm your shen'dorei" | Pun on "I'm your man", with singular use | [Halavuul Cragwind](https://warcraft.wiki.gg/wiki/Halavuul_Cragwind) |
| "shed shen'dorei blood" | Adjectival use | [Agitators, quest 92465](https://warcraft.wiki.gg/wiki/Agitators) |

These suggest calques for the project, such as a wind-based greeting, but they are not attested in elvish, so the JSON proposes none.

**Count:** 32 elvish items in sections A to E: 4 glossed by Blizzard, 10 names with epithets or roles, 1 sentence, 14 place-name rows (one of them, Zaalanarr, client-only) and 3 item-name forms (Shen'dorei as an adjective, Al'Aketh, Elunar). Section F adds 5 English formulas. The client adds Zephrali, Zephraalis and Siroccaa (see "Zephras and zepharaalis").

## Zephras and zepharaalis

The question was whether the last word of the letter, *zepharaalis*, comes from Zephras Isle. **Yes: the client supports it at medium-high confidence.** The client turns the island name into a demonym, a family name and this word, the same way it turns the island Siroccas into a family name.

### The letter, read in context

`MailTemplate` 652, from the client:

> Greetings $n, / I hope this letter finds you well. I wanted to thank you for speaking to Ur'seris and taking on his request. Through your deeds the forest has now become much safer for both wildlife and shen'dorei. / I am unsure where the winds will lead you, but I believe you will go on to do great things. I hope you are able to find further druidic instruction on your adventures. / Aeesha'el banu zepharaalis, / Lotheluum Starbreeze

1. **Sender.** Lotheluum Starbreeze, the Druid Trainer in Valanaar ([Zephras Isle NPCs](https://warcraft.wiki.gg/wiki/Zephras_Isle_NPCs)). He starts the druid quest "The Great Ursera Spirit", which leads to the bear spirit Urs'endris.
2. **Recipient.** The player ($n), a young Skyborne druid who has just finished the Shadowgale Forest bear-spirit quests and is leaving Zephras ("I hope you are able to find further druidic instruction on your adventures"). *Ur'seris* appears nowhere else in the client or on the wiki. It may be another name for Urs'endris, or for a spirit whose quest text is server-side.
3. **Function.** The phrase sits exactly where other letters in the same table put their closing line: "Regards," (MailTemplate 612 to 615 and 623) and "Light be with you." (624). So it is a farewell blessing for certain.
4. **The closest English parallel** is the coming-of-age blessing in quest 92460: "know that the winds of home will be with you wherever you travel" ([Coming of Age](https://warcraft.wiki.gg/wiki/Coming_of_Age_%28Forever%29)). The spoken farewells are "Winds be with you" and "May the winds guide you".

### Zephr- words in the client

| Form | Where | What it is |
|---|---|---|
| **Zephras** Isle | `AreaTable` 16593, `Map` 2991, `UiMap` 2521, `GlobalStrings` RACE_INFO_SKYBORNE; atlas name `skyborne-zephras-isles` | The island |
| **Zephrali** Chainmail, Greatstaff, Bow and others | `ItemSparse` 277080 to 277111 (32 common-quality items, item level 14; [Zephrali Greatstaff](https://warcraft.wiki.gg/wiki/Zephrali_Greatstaff)) | The demonym "Zephran", used the way English item names use "Darnassian" |
| **Zephraalis** | `NameGen` 25277, 25363, 25449 and 25535: NameType 1 (family name), both Skyborne races (95, 96), both sexes | A Skyborne family name |
| **zepharaalis** | `MailTemplate` 652 | The letter's last word |
| **Zepha** | `NameGen`, male given name | A personal name on the same stem |
| **Siroccaa**, **Sirocaas**, **Siroca** | `NameGen`: family name, male given name, female given name | The same pattern on the island **Siroccas** |
| *zephyr* (English) | Zephyrgale and Zephyrgaze (NameGen family names), Zephyrseeds, Enchanted Gyrozephyr | English, not elvish, kept apart |

The client's 86 Skyborne family names are almost all English wind compounds, such as Windsong, Starbreeze and Evengale. Only two are elvish, Zephraalis and Siroccaa, and both are built on island names. No other client text has *zephar*, *aeesha*, *banu* or *aalis* except the letter, and the last only as the surname *Zephraalis*. The search covered every text field in `corpus.jsonl` and `wdb_strings.jsonl`.

### Segmentations tested

| # | Parse | For | Against | Verdict |
|---|---|---|---|---|
| 1 | **Zephra(s) + -alis**: the place loses its -s, and the stem's *a* plus the suffix's *a* are written as the Skyborne long *aa* | It matches the client surname Zephraalis exactly. It runs parallel to Siroccas > Siroccaa (island loses -s and takes a vowel) and to Zephras > Zephra-li (demonym). | The letter has an extra *a*: zeph**a**r-, against Zephr- everywhere else. That may be an epenthetic vowel or a variant spelling; compare Eldre'narr and "Eldranaar". | **Best** (medium-high) |
| 2 | zephar + **aalis** | *-aal* and *-is* are both common Skyborne name endings: Myriaal, Sriaal, Zriaal, Vraal, Elransiaal; Talaanis, Denaaris, Urs'endris. | It is the same word as parse 1 cut differently, and the client stem is *zephr-*, never *zephar-*. | Compatible with 1 |
| 3 | **zephara + alis** | Identical to parse 1 if the stem's full form is *zephara-*. | Only the letter spells it that way. | Same as 1 |
| 4 | zephar + Darnassian **-alah** "to you" (as in *Ishnu-alah*, "good fortune to you") | It would fit a blessing. | *-alis* is not *-alah*: both the vowel and the final consonant differ, and no *alah*/*alis* alternation is known. | Rejected |
| 5 | A *-thalas* "home, kingdom" compound (as in Quel'Thalas, Eldre'Thalas) | "Winds of home" would fit the meaning. | There is no *th*; the island is *Zephr-as*, not *\*Zeph'thalas*. | Rejected |
| 6 | Darnassian *-aran* or *-naar* "town" | None | Neither form matches. | Rejected |

**The place ending `-as`.** Every Skyborne island name is a weather word plus *-as*: Zephr-as (zephyr), Sirocc-as (sirocco) and Anvil-as (anvil cloud). The new Forever zone *Shen'dral-as* sits beside the house name *Shen'dral-ar*, which pairs *-as* "place" with *-ar* "people, house". The JSON adds `as` as a medium-confidence entry. The lexicon's `thalas` "home, kingdom" may contain the same ending.

### Best reading of the whole phrase

| Word | Gloss | Confidence | Basis |
|---|---|---|---|
| **zepharaalis** | "of Zephras, a Zephran" | **Medium-high** | The client surname, the demonym and the Siroccaa parallel |
| **aeesha'el** | Perhaps "peace be (with you)": *aeesha* + **el** "peace" (lexicon, canon) | Low | One attestation only |
| **banu** | Perhaps "way, passage": **ban** "gate, passage" (lexicon, canon) + *-u*, echoing "May the winds guide your path" | Low | One attestation only |
| **Whole phrase** | A farewell blessing naming the homeland, roughly "may peace and the winds of Zephras go with you", the elvish counterpart of "the winds of home will be with you" | **Medium** | Function: certain. Zephras link: medium-high. Exact words: low. |

### Still unknown

1. What *aeesha* means, and whether *banu* is a noun ("path") or a verb ("go, guide").
2. Whether *zepharaalis* refers to the recipient ("Zephran!") or modifies the blessing ("...of Zephras").
3. Who *Ur'seris* is.
4. **The best remaining source is the Skyborne voice files.** The dump has `skyborne_vo/`: 196 files extracted, out of 588 listed in `skyborne_vo_files.csv`. They include /hello, /bye and /thank recordings for both sexes. A forum post on the [Skyborne backstory thread](https://us.forums.blizzard.com/en/wow/t/2353964) says some Skyborne voice lines are in an elvish language its author could not identify as Darnassian. If /bye or /thank says "Aeesha'el" or "banu", that would settle these words. The 10 files most worth hearing are listed in the client-check section. They have not been transcribed, because that needs the user's go for a speech-to-text model.

## Sound-change notes compared with Thalassian, Darnassian and Shalassian

1. **The Darnassian vowel `fal-` is kept.** Skyborne names have *Fal-* and never *Fel-*: Falaath Village, Falfaan Halfwind, Faladiel, Falorne Fallwind. Lore has the ancestors leave Eldre'Thalas, a Darnassian-speaking city, separately from the Quel'Thalas exiles, so they should lack the Thalassian *a > e* shift (Darnassian *falo* > Thalassian *felo*). This is consistent, but rests on names only.
2. **Doubled vowels mark the dialect.** 54 of 116 Skyborne given names checked (47%) contain *aa, ee, ii* or *uu*. Examples: Talaanis, Elaadrin, Belathaan, Haalien, Ealaane, Dorii, Uualia, Lotheluum, Halavuul, Xy'aaria, Ventaari. The place names Valanaar, Falaath and Eldre'naar and the phrase *zephar**aa**lis* show it too. Darnassian has it only in a few place names (Dolanaar, Astranaar), and Thalassian hardly at all. The [wiki's Names section](https://warcraft.wiki.gg/wiki/Skyborne#Names) points out the same pattern. No comparison count was computed for night elf names. The client shows that the doubling is optional in spelling: **Rohashi** Spires (`AreaTable` 16630) and **Rohaashi** Spires (`SpellName` 1259410) name the same place. The client's name generator uses it heavily too: Aae, Aashri, Ariaa, Elransiaal, Valaan, Zhaal, Zriaal, Zephraalis and Siroccaa.
3. **A double consonant may become a long vowel: `rr` > `aa`.** The old port *Eldre'narr* became the colony *New Eldre'naar*, and colloquially *Eldranaar*, which also drops the apostrophe and the *e*. The client has none of these three forms, since they are quest text, but it does have **Zaalanarr** with *-narr* beside **Valanaar** with *-naar*. So *-narr* and *-naar* are two forms of one ending, and the `rr`/`aa` swap is real, even if its direction is not proven.
4. **A double s may simplify: `urs + s-` > `ur's-`.** *Ur'seris* fits *Urs'seris*, against *Urs'endris* and *Urs'anah*. *Ur'endra* is not explained by this (low).
5. **The ending `-l-` may change to `-m-`, or the name may blend with Suramar.** *Shen'dralar* (Highborne) sits beside *Shen'dramar* (a Skyborne town) and *Shen'dralas* (a Highborne zone). This is weak; it may simply echo Suramar.
6. **`shen` may vary with `shan`.** One NPC yell has "shan'dorei": Rorian the Dayseeker in [Falling With Style, quest 92474](https://warcraft.wiki.gg/wiki/Falling_With_Style_%28Skyborne%29). It is probably a typo for *shen'dorei*, since *shan* means "honored" in Darnassian *Shan'do*. To check in BroadcastText.
7. **`Al'` is a separable prefix.** *Al'Akir* sits beside *Shrine of Akir* and *Mark of Akir*, so in Skyborne usage *Al'* is a detachable title or prefix. *Al'Aketh* may be *Akir* plus a collective *-eth*, replacing *-ir*. Low.
8. **Shalassian contrast.** No Shalassian-only roots appear. The Skyborne words line up with Darnassian, in *dorei*, *shal* and *tel*, more than with Shalassian.

## Contradictions with the current lexicon

None of the new data contradicts a canon entry outright. Six points are worth noting:

1. **`dorei` "children/born of" lacks "people".** Blizzard glosses shen'dorei as "hidden **people**", and the Warcraft Encyclopedia glosses Kaldorei as "people of the stars". The JSON has a correction (high).
2. **`shal` "night/shadow" lacks "veil".** Shal'nan means "The Veiled One". The JSON has a correction (medium). Keep the Thalassian entry `shal'na` "no! / please" apart: it has a similar shape but an unrelated meaning.
3. **[grammar.md](../../docs/methodology/grammar.md) (the plurals section, lines 20-22) treats *dorei* as the plural of *dore*.** Skyborne texts use **shen'dorei** for one person: "I am shen'dorei"; "a shen'dorei of intense presence" ([On the Shal'nan](https://warcraft.wiki.gg/wiki/On_the_Shal%27nan)); "I'm your shen'dorei". The grammar note should say that *-dorei* ethnonyms work as both singular and collective.
4. **`ana` "fare/status" (Thalassian, canon) may clash.** If *Eluvi'ana* "The Night Dancer" is a literal gloss, then *ana* would mean "dancer". Not proposed as a correction: the epithet is not stated to be a translation.
5. **`othina` "wind" (generated, non-canon)** now has an attested rival stem, **zephr-** "zephyr" (medium). It shows up in Zephras, Zephrali and Zephraalis, but only as the island's name, never as a free noun for "wind". Keep `othina` for the general word, and use `zephr-` for the gentle or west wind and for anything "of Zephras".
6. **`aran` "town/settlement" (Darnassian, canon) and the new `naar` "settlement (place-name ending)"** can coexist: one is a free noun (Ameth'Aran) and the other a bound ending (Dolanaar, Valanaar).

## Lookups still open

Phase 2 ran every lookup that the dump can answer; the results are in "Client check (phase 2)" above. Four lookups need data the dump does not have:

1. **Transcribe the 10 voice files** listed in the client-check section. This needs the user's go to install a speech-to-text model, or a person to listen.
2. **Zephras Isle quest and book text.** This needs a Skyborne character to play the zone so the quest and page caches fill. Then search `wdb_strings.jsonl` for:
   1. *Shal'nan* and the four "Rebellion in Eldre'Thalas" crystals.
   2. Rorian's line in quest 92474, to settle *shan'dorei* against *shen'dorei*.
   3. *New Eldre'naar*, *Eldranaar*, *Eldre'narr*, *Shen'dramar*, *Siroccas* and *Anvilas*.
   4. *Ur'seris*.
   5. Any Skyborne line tagged LanguageID 310.
3. **NPC speech tagged Shen'dorei (310).** `BroadcastText` lines arrive from the server only when an NPC speaks in play. A Skyborne play session would show whether any NPC speaks Languages 310.
4. **The three non-public TACT keys** hide 61 DB2 sections (README, "Known gaps" 1). Re-run the extraction if Blizzard pushes those keys.

## What could not be found

1. **A translation of "Aeesha'el banu zepharaalis".** Neither the web nor the client translates it. The client has the letter (`MailTemplate` 652) and the matching surname Zephraalis, but nothing for *aeesha'el* or *banu*.
2. **Skyborne voice-line transcripts and battle cries.** None are online. The client has 196 voice files, but they are audio and have not been transcribed (see the voice-file list).
3. **Meanings for place names and given names.** Blizzard gives none: not for Valanaar, Thendal, Shen'dar, Ban'aethal, Falaath, Zephras, Eluvi'tor, Saeyleenan or Ur'seris.
4. **The BlizzCon "Found Photographs" panel video.** It was not watched; the Blizzard written recap was used.
5. **Wowhead and MMO-Champion.** Neither had a datamining post on Skyborne vocabulary. The Icy Veins lore article returned HTTP 403.
