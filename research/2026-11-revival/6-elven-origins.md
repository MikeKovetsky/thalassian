# Elven origins: what the lore says, and what could rebuild ancient elvish

Date: 2026-11-18. Sources: the raw wikitext of the warcraft.wiki.gg pages linked below, including its copies of Blizzard's Warcraft Encyclopedia, and the local, gitignored `Languages.csv` and `LanguageWords.csv` from the WoW Forever client (1.60.1.70938). No paid APIs, no downloads. The lore claims rest on the wiki and the sources it cites; the books themselves were not opened.

## Findings

1. **Darnassian is the parent in Blizzard's wording, but strictly a cousin.** Blizzard's encyclopedia says Thalassian and Nazja derive from Darnassian, and in another entry calls them its cousin languages. Their common ancestor is the Darnassian spoken before the Sundering, about 10,000 years ago. Blizzard never documents it, and modern Darnassian has changed over the same 10,000 years.
2. **Trolls are the elves' ancestors, not elves, and their language shares nothing traceable with elvish.** Night elves descend from dark trolls changed by the Well of Eternity. Zandali and the elven languages share no word, and their sound is designed differently. The one shared trait is a pronoun suffixed to the verb.
3. **Five branches of elvish can be compared, and the repo uses four.** They are Darnassian, Thalassian, Shalassian, Skyborne and Nazja, the naga language. Nazja is missing from the repo.
4. **Ancient elvish can be rebuilt only as a shared core, not as proto-forms.** Report 1 found no sound correspondence with more than two supporting pairs. What the sources can support is a list of the morphemes that several branches share, plus the names coined before the Sundering. *dorei* "children, people" is in all five branches.

## 1. Is Darnassian the ancestor?

What the sources say:
- Blizzard's encyclopedia says Thalassian is derived from Darnassian, like Nazja ([Thalassian entry](https://warcraft.wiki.gg/wiki/The_Warcraft_Encyclopedia/Thalassian)). Its [Darnassian entry](https://warcraft.wiki.gg/wiki/The_Warcraft_Encyclopedia/Darnassian) calls Nazja and Thalassian Darnassian's two cousin languages, spoken by peoples descended from night elves.
- In 2016 a Blizzard developer, Don Adams, called Shalassian an offshoot of Darnassian like Thalassian, and also a unique dialect of ancient elvish ([tweets cited on the wiki](https://warcraft.wiki.gg/wiki/Shalassian#Notes)).
- In the novel *Day of the Dragon*, high elves call Darnassian an elder tongue they have almost forgotten ([Darnassian](https://warcraft.wiki.gg/wiki/Darnassian)).
- The novel *Cycle of Hatred* speaks of four elven dialects, without naming them.

What it means here:
- The branches split at the Sundering or after it. The exiled Highborne left for Quel'Thalas, the nightborne were sealed in Suramar, the naga sank with Zin-Azshari, and the Shen'dralar stayed in Eldre'Thalas.
- Night elf Darnassian kept changing over the same 10,000 years, so it is the closest living relative of the ancient tongue, not the ancient tongue itself.
- Darnassian's own origin is unknown. The wiki's idea that it grew out of Zandali is marked [speculation](https://warcraft.wiki.gg/wiki/Darnassian#Speculation), with no Blizzard source.
- The only outside influence Blizzard names is the Titan language. The early night elves learned *Kalimdor* and other Titan words through Elune and from titan-forged artifacts, and that shaped their name for themselves, *kaldorei* ([Dark troll](https://warcraft.wiki.gg/wiki/Dark_troll), citing *Chronicle* Vol. 1 and the *Warcraft III* manual). Titan *Kalimdor* is glossed "land of eternal starlight", and *kaldorei* "children of the stars".

## 2. Trolls and Zandali

**Lore.** About 15,000 years ago a tribe of dark trolls settled by the Well of Eternity, and its power slowly changed them into the first night elves ([Dark troll](https://warcraft.wiki.gg/wiki/Dark_troll)). In-world the origin is disputed, and night elves resent it. Haranir murals in Harandar offer another account, in which trolls and elves both descend from haranir kin.

**Language.** Three comparisons:

| Aspect | Zandali (troll) | Elvish | Verdict |
|---|---|---|---|
| Sound (the client's scrambler word lists) | 79 words built on Jamaican Patois (*ackee*, *obeah*, *mek*, *fi*, *deh*); 6 with an apostrophe; *z k j w b g* are 9.6% of letters | Darnassian and Thalassian share 100 of 102 words, and Shen'dorei uses Darnassian's list; 39 with an apostrophe; *z k j w b g* are 1.9%, *l r s* 19.1% | No shared word except the single letters *a*, *e*, *n* and *o*. By letter pairs, the troll list is as far from elvish (cosine 0.54) as from Taurahe (0.54) or Common (0.53). |
| Vocabulary ([about 45 glossed Zandali words](https://warcraft.wiki.gg/wiki/Zandali#Zandali_primer_(official_translations))) | *ban* "will", *na* "in", *ni* "and", *roa* "heart", *kele* "rise", *Fa'da* / *Ma'da* "father / mother" | *ban* "gate", *'na* "us", *rea* "and", *alann* "heart", *aranal* "rise", *An'da* / *Min'da* | No match in meaning. *Fa'da* / *Ma'da* share the *'da* ending with the elven parent words, but *Fa-* and *Ma-* look modelled on English "father" and "mama". |
| Grammar | Object pronoun suffixed to the verb: *Weta-den* "cleanse him", *Watha-nekan* "cleanse us"; an article, *de* "the" | Object pronoun suffixed to the verb: *dela'na* "guide us", *Vendel'o* "help me"; no article on record | One shared trait, with different pronouns. |

The scrambler lists are sound design, not vocabulary: they are what players see when they don't know a language (report 1 found one scrambler line in the wiki's own primer). They show how Blizzard wants each language to sound, nothing more.

## 3. Sources for ancient elvish, ranked

| # | Source | What it gives | In the repo | What it takes |
|---|---|---|---|---|
| 1 | **Nazja**, the naga language ([wiki](https://warcraft.wiki.gg/wiki/Nazja)) | A fifth branch, split at the Sundering. 12 untranslated phrases and 11 proper nouns, none glossed, so it can confirm forms but not meanings: *Ba'anthalso-dorei!* has *dorei*, and *Zin-Azshari adore* has *adore* ("be with you", as in Darnassian *Elune-adore*). | No | Free: the wiki page, plus naga lines in retail speech (Serpentshrine Cavern, Nazjatar, the Eternal Palace). |
| 2 | **Shalassian at full size** | The nightborne were sealed in Suramar from the Sundering until *Legion*, so they are the branch most cut off from the others. The corpus has only 5 glossed phrases; retail's Shalassian scrambler list has 141 words, 39 of them its own ([report 2](2-client-mining.md)), and the [wiki](https://warcraft.wiki.gg/wiki/Shalassian#Untranslated_Shalassian_phrases) lists 27 untranslated phrases. | 5 phrases | Free: wago.tools serves the list as CSV (LanguageID 181). |
| 3 | **Names from before the Sundering** | The only direct record of the ancient language: places, people and artifacts named in that era. Some are glossed and already in the lexicon (*Zin-Azshari* "the glory of Azshara", *Elun'dris* "the Eye of Elune", *Kaldorei*); the rest (*Eldarath*, *Nar'thalas*, *Suramar*, *Sharas'dal*, *Varo'then*, *Dath'Remar*) can be split with known morphemes. | A few | Free: a sweep of the wiki's pages on the War of the Ancients era. |
| 4 | **Retail server-side speech and its localizations** | NPC lines from content set in or just after that era: the Well of Eternity dungeon (set 10,000 years ago), Azsuna's Highborne ghosts of Nar'thalas, Suramar and Nazjatar. Chinese and Korean localizers sometimes translate an elven line instead of keeping it, which is how report 4 confirmed *shal'na* and *shorel'aran*. Whether these zones' lines hold elvish is not checked yet. | Only the 10,888 rows shipped in the client (report 4) | A download, which needs Mike's go: the full BroadcastText from wago.tools for enUS, zhCN, zhTW and koKR. Size not advertised. |
| 5 | **Titan loans** | A layer to separate from inherited words: lore says the early night elves took Titan words, and *kal-* "star" in *kaldorei* may be one, given *Kalimdor* "land of eternal starlight". | Titan is not | Free: the wiki's Titan primer. |
| 6 | **Skyborne** (Shen'dralar of Eldre'Thalas) | A branch cut off since the Sundering, with eight sound-change notes and four voice formulas. | Yes ([report 3](3-new-elven-race.md), [report 5](5-voice-transcription.md)) | Done. |

Not useful:
- Zandali: no shared vocabulary (section 2).
- The old tabletop RPG's "Elven" language and its "ancient dialect of Darnassian written in runes" ([wiki](https://warcraft.wiki.gg/wiki/Darnassian#In_the_RPG)): the RPG is no longer canon, and neither gives words.
- Scrambler lists as vocabulary: they are sound only.

## 4. What a reconstruction can claim

A shared-core list is supported. Each item is a morpheme attested in at least three of the five branches, or in a name from before the Sundering. Each would be marked `inferred`, never canon. Two examples:
- *dorei* "children, people": Darnassian *kaldorei*, Thalassian *sin'dorei*, Shalassian *shal'dorei*, Nazja *Ba'anthalso-dorei*, Skyborne *shen'dorei*. All five branches.
- *adore* "be with you": Darnassian *Elune-adore*, Shalassian *An'ratha adore*, Nazja *Zin-Azshari adore*. Three branches.

Proto-forms with sound laws are not supported. Report 1's comparative method found no correspondence with more than two pairs, so Blizzard has not built these languages with regular sound change, and any proto-form would be invention.

## Reproducing the sound comparison

From the repo root, with the client extract in `.wowf-extract/`:

```python
import csv, collections, math
names = {r["ID"]: r["Name_lang"] for r in csv.DictReader(open(".wowf-extract/Languages.csv"))}
words = collections.defaultdict(set)
for r in csv.DictReader(open(".wowf-extract/LanguageWords.csv")):
    words[names.get(r["LanguageID"])].add(r["Word"].lower())
def bigrams(ws):
    c = collections.Counter()
    for w in ws:
        w = "^" + w + "$"
        c.update(w[i:i + 2] for i in range(len(w) - 1))
    return c
def cosine(a, b):
    return sum(a[k] * b[k] for k in a) / math.sqrt(sum(v * v for v in a.values()) * sum(v * v for v in b.values()))
troll = bigrams(words["Troll"])
for lang in ("Darnassian", "Thalassian", "Shen'dorei", "Taurahe", "Common", "Titan", "Orcish"):
    print(lang, round(cosine(troll, bigrams(words[lang])), 2))
print(sorted(words["Troll"] & words["Darnassian"]))
```
