# Localization mining: BroadcastText zhCN / zhTW / koKR (retail 12.1.7.70892)

Date: 2026-11-17. Input: the three shipped-row tables in this folder (10,888 rows each). English originals came from [wago.tools BroadcastText](https://wago.tools/db2/BroadcastText) page lookups by ID. Candidates: [4-candidates.json](4-candidates.json), with 14 actions.

## What the localizations confirm or add

1. **14 rows carry elven text** (plus one stage direction). The lines are in Thalassian or Darnassian. Across the 42 locale renderings (14 rows × 3 locales):
   - **2 translate the elven text.** Both are Chinese, and both match the existing canon gloss.
   - **40 keep it.** Chinese keeps the Latin text; Korean always transliterates into Hangul and never translates.
   - **No localization adds a new elven meaning.** Mike's canon list is unchanged by this pass. It gets independent confirmation instead.
2. **Shal'na = aunt is confirmed.** zhCN renders [row 302349](https://wago.tools/db2/BroadcastText?filter%5BID%5D=exact%3A302349&locale=zhCN) "Shal'na! Come back to us." as 阿姨！快醒醒啊。 ("Auntie! Wake up!"). zhTW keeps "Shal'na", and koKR transliterates it as 샬나.
3. **Shorel'aran = farewell is confirmed.** zhTW renders [row 321680](https://wago.tools/db2/BroadcastText?filter%5BID%5D=exact%3A321680&locale=zhTW) "Shorel'aran..." as 再會了... ("Farewell..."). zhCN keeps it, and koKR transliterates it as 쇼렐러란.
4. **The strongest finding is a second, independent Blizzard gloss for *Selama ashal'anore*.** In [row 309952](https://wago.tools/db2/BroadcastText?filter%5BID%5D=exact%3A309952) Vereesa Windrunner glosses the phrase herself: "Selama ashal'anore, Blood Knight. Justice for our people." This is the 12.0.7 quest [A Favor for Kinduru](https://warcraft.wiki.gg/wiki/A_Favor_for_Kinduru).
   - The only earlier source for this gloss was the 2006 Warcraft Encyclopedia.
   - zhTW renders the gloss sentence as 為族人伸張正義 ("uphold justice for our kinsfolk"), and koKR as 우리 동족에게 정의를 ("justice for our kin").
   - So Blizzard's translators read *anore* as "our people / kin". There is no "great" and no "nation". That supports the earlier fixes to *ashal* and *anore*.
5. **Two canon phrases are now attested in-game.** Before, they came only from a novel and tweets:
   - *Vendel'o eranu* (rows 302497–302498)
   - *Elu'meniel mal alann* (row 302501)

   Both are sung by Sylvanas in [Repent of the Highborne](https://warcraft.wiki.gg/wiki/Repent_of_the_Highborne) (11.2.7). Row 302496 marks the passage "(singing in Thalassian)"; zhCN calls it 萨拉斯语 "Thalassian", and koKR calls it 하이엘프어 "High Elf language". No locale translates any sung line, so this confirms the forms, not the meanings. The lyrics are not reproduced here.
6. **Darnassian *Andu-falah-dor* is used as a parting blessing as well as a war cry.** One line reads "Andu-falah-dor, old friend. Watch her well." (row 215394), and it also appears alone (row 215215). All locales keep it.
7. **Calibration: the method is reliable.** zhTW translated 16 Orcish rows in this table, covering 5 distinct phrases. Every phrase rendering matches Blizzard's official English gloss on the [Orcish page](https://warcraft.wiki.gg/wiki/Orcish_(language)):
   - Lok'tar ogar → 不勝即亡 / 勝利或死亡 ("victory or death")
   - Throm-Ka → 你好 ("well met")
   - Lok-Narash → 備好武器 / 拿起武器 ("to arms")
   - Lok-Regar → 準備聽令 ("ready for orders")
   - Aka'Magosh → 祝福你與你的同伴 ("a blessing on you and yours")

   Chinese renderings are therefore trustworthy at the phrase level. They are loose for lone words: zhTW renders bare "Lok'tar!" as 部落！ ("Horde!"). zhTW even supplies a gloss where English has none: Zandali "Taz'dingo!" → "Taz'dingo! (勝利！)" ("Victory!", row 86300). That row is out of scope here.

## Table

The English column comes from wago.tools (enUS). The zhCN, zhTW and koKR columns come from the local CSVs. "keeps" means the text stays in Latin script (zh) or is transliterated into Hangul (ko).

| Row | English | zhCN | zhTW | koKR | What it means for which word | Confidence |
|---|---|---|---|---|---|---|
| 302349 | Shal'na! Come back to us. | 阿姨！快醒醒啊。 (**translates**: "Auntie!") | keeps "Shal'na" | 샬나 (transliterates) | *shal'na* = aunt is confirmed by Blizzard zhCN | high |
| 321680 | Shorel'aran... | keeps | 再會了... (**translates**: "farewell") | 쇼렐러란 | *shorel'aran* = farewell is confirmed by Blizzard zhTW | high |
| 309952 | Selama ashal'anore, Blood Knight. Justice for our people. | keeps phrase; gloss → 我只求正义得以昭雪 (looser) | keeps phrase; gloss → 為族人伸張正義 | 셀라마 아샬라노레 …; gloss → 우리 동족에게 정의를 | *selama ashal'anore* = justice for our people (second Blizzard source, 12.0.7); *anore* = our people/kin | high |
| 302496 | (singing in Thalassian) | （用萨拉斯语吟唱） | （用薩拉斯語歌唱） | (하이엘프어 노래) | stage direction; koKR names Thalassian "High Elf language" | n/a |
| 302497–302502 | sung passage made of the canon phrases *Vendel'o eranu*, *ashal'anore*, *Sin'dorei*, *Elu'meniel mal alann* | keeps | keeps | transliterates (벤델로 에라누, 아샬라노레, 신도레이, 엘루메니엘 말 알란) | in-game attestation of *vendel'o eranu* and *elu'meniel mal alann*; no new meaning | high (form) |
| 69644 | Anar'alash denal! Will someone tell me WHAT is going on in Dalaran? | keeps | keeps | 아날라쉬 데날 | still untranslated; an exasperated "By …!" oath (anar = by) | low |
| 158529 | Sylvanas! Your foul deeds desecrate this sacred place! Andu-falah-dor! | keeps | keeps | 안두 팔라 도르 | no new meaning | n/a |
| 215215 | Andu-falah-dor. | keeps | keeps | 안두 팔라 도르 | no new meaning | n/a |
| 215394 | Andu-falah-dor, old friend. Watch her well. | keeps | keeps | 안두 팔라 도르 | usage as a parting blessing | medium |
| 249126 | Elune-adore. | keeps | keeps | 엘룬 아도레 | no new meaning | n/a |
| 74417 and others (Orcish, calibration) | Lok'tar ogar! | keeps | 不勝即亡！ | 록타르 오가르 | calibration: zhTW = official gloss "victory or death" | n/a |
| 77148 (calibration) | Throm-Ka, Commander Vorka. … | keeps | 你好，… | 트롬카 | calibration: "well met" | n/a |
| 77168 (calibration) | Lok-Regar. What orders? | keeps | 準備聽令。… | 록레가르 | calibration: "ready for orders" | n/a |
| 79500, 79626 (calibration) | Lok-Narash! | keeps | 備好武器 / 拿起武器 | 로크 나라쉬 | calibration: "to arms" | n/a |
| 81674 (calibration) | … Aka'Magosh. | keeps | 祝福你與你的同伴。 | 아카마고쉬 | calibration: "a blessing on you and yours" | n/a |

## Candidates (4-candidates.json)

All 14 actions were checked against the current 310-entry lexicon, and every `old` value matches.

| Action | Confidence | Words |
|---|---|---|
| Fix | high (11) | selama ashal'anore (evidence, notes); anore (notes); selama (notes); ashal (notes); vendel'o eranu (evidence, notes); elu'meniel mal alann (evidence, notes); shal'na (evidence); shorel'aran (evidence) |
| Fix | medium (2) | anore translation, "people/nation" → "people, kin (our people)"; andu-falah-dor notes (parting blessing) |
| Add | low (1) | *anar'alash denal* (attested, untranslated), canon:false |

Several fixes remove stale notes that still quote the old wrong gloss "Justice for our great people". These notes were on *anore*, *selama* and *ashal*.

No new `canon:true` entries: the two words Blizzard's localizations translate (shal'na, shorel'aran) are already canon.

## Limits

- **Subset only.** The tables hold only the 10,888 rows shipped in the 12.1.7 client. The TBC boss lines are not in it: Kael'thas's *Felomin ashal*, *Balamore shanal* and *Anar'anel belore*, Sarannis's *Band'or shorel'aran*, and Zerevor's lines. So the zhTW glosses reported on the wiki talk page are still not re-verified.
- **No language-tagged speech.** No row in the subset uses LanguageID 10 (Thalassian) or 2 (Darnassian): 10,861 rows are language 0.
- **How rows were found.** Elven rows were found through Latin text that survives in at least one locale, plus Hangul matches against known elven words. A line translated in all three locales, with no English to compare, would be missed. I found none of these among the Hangul matches.
- **What it can and cannot show.** The method can confirm meanings, not invent them. Korean always transliterates. Chinese translates only about 1 in 20 elven renderings (2 of 42).
- **English text not stored locally.** It came from wago.tools page lookups for 31 IDs, and no further files were downloaded.
