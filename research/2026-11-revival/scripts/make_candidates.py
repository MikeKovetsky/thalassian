import json, os, sys
W = "https://warcraft.wiki.gg/wiki/"
TP = W + "Thalassian#Thalassian_primer_(official_translations)"
TU = W + "Thalassian#Untranslated_words_or_phrases"
TPARSER = W + "Thalassian#Thalassian_word_parser"
DP = W + "Darnassian#Darnassian_primer_(official_translations)"
DSPEC = W + "Darnassian#Speculation"
DU = W + "Darnassian#Untranslated_phrases"
SP = W + "Shalassian#Shalassian_primer_(official_translations)"
SU = W + "Shalassian#Untranslated_Shalassian_phrases"
ENC_T = W + "The_Warcraft_Encyclopedia/Thalassian"
ENC_D = W + "The_Warcraft_Encyclopedia/Darnassian"
TALK = W + "Talk:Thalassian#Making_a_wild_guess..."
CANT = W + "Canticle_of_Sacrifice#Lyrics"
WAGO = "https://wago.tools/db2/BroadcastText?filter%5BID%5D=exact%3A{id}&locale={loc}"
def ev(q, w): return {"quote": q, "where": w}
C = []
def add(word, en, uk, pos, canon, root, notes, source, evidence, method, conf):
    C.append({"action": "add", "word": word, "translation": {"en": en, "uk": uk}, "pos": pos, "canon": canon, "root": root,
              "notes": notes, "source": source, "evidence": evidence, "method": method, "confidence": conf})
def fix(word, field, old, new, evidence, conf, why=""):
    d = {"action": "fix", "word": word, "field": field, "old": old, "new": new, "evidence": evidence, "confidence": conf}
    if why: d["reason"] = why
    C.append(d)
def demote(word, reason, evidence, conf):
    C.append({"action": "demote", "word": word, "reason": reason, "evidence": evidence, "confidence": conf})
def remove(word, reason, evidence, conf):
    C.append({"action": "remove", "word": word, "reason": reason, "evidence": evidence, "confidence": conf})

E = {}  # reusable evidence
E["alar"] = [ev("Alar'annalas = Ranger Lord.", TP), ev("The Thalassian term for this rank is Alar'annalas.", W + "Farstriders")]
E["anaralah"] = [ev("Anar'alah = By the light.", TP), ev("Anar'alah belore. || By the light of the sun.", ENC_T), ev("Anar'endal dracon = By the breath of the dragon.", TP)]
E["thasalah"] = [ev("Thas'alah = Light of the Forest.", TP), ev("In Thalassian, \"alah\" translates \"light\" in Common", W + "Alah%27endal,_the_Dawnsong")]
E["selama"] = [ev("Selama ashal'anore. || Justice for our people. || Used as either a vow or a farewell.", ENC_T)]
E["bash"] = [ev("Bash'a no falor talah! || Taste the chill of true death! || Not a widespread expression or battle cry.", ENC_T),
             ev("Bash'a no falor talah! = Taste the chill of true death! Spoken by Sylvanas Windrunner in Warcraft III.", TP)]
E["shalna"] = [ev("Shal'na = Aunt.", TP), ev("Arator: Shal'na! Come back to us.", W + "What_Might_Come#Notes"),
               ev("阿姨！快醒醒啊。 (zhCN localization of BroadcastText 302349; 阿姨 = 'auntie')", WAGO.format(id=302349, loc="zhCN"))]
E["shindu"] = [ev("Shindu fallah na! || They're breaking through!", ENC_T), ev("Shindu fallah na = \"They are breaking through\" or \"Our enemies are breaking through\".", TP),
               ev("Shindu sin'dorei = Failing children of the blood.", TP)]
E["dela"] = [ev("Anu belore dela'na. || The sun guides us.", ENC_T)]
E["na_darn"] = [ev("Shu dalas na = Heavy are our hearts.", DP), ev("Tor ilisar'thera'nal = Let our enemies beware.", DP)]
E["tal"] = [ev("Tal anu'men no Sin'dorei = Death to all who oppose the children of the blood. Spoken by High Astromancer Solarian in Tempest Keep.", TP)]
E["vendel"] = [ev("Vendel'o eranu = Help me forget.", TP)]
E["zhtw"] = [ev("(p4, Taking matter into own hands) Balamore shanal = Prepare to die", TALK), ev("(p4 summon phonex) Anara'nel belore = For the sun (pretty obvious actually)", TALK), ev("(Flamestrike when Zombie mode at MgT) Felomin ashal! = Fire consumes!", TALK), ev("For example, playing in WoW-TW will see this: (薩拉斯語)準備道別吧!, which roughly translate to \"(Thalassian)Prepare to farewell!\".", TALK)]
E["parser"] = [ev("Five-letter words | Talah, Adore, Ishnu, Bandu, Balah, Fandu, Thera, Turus, Shari, Shano, Terro, Eburi", TPARSER),
               ev("Note: The language algorithm used by the in-game \"translator\" merely makes the words look like Thalassian. It does not actually translate words.", TPARSER)]

# ---------------- FIXES to existing entries ----------------
fix("alar", "translation", {"uk": "фенікс", "en": "phoenix"}, {"uk": "рейнджер", "en": "ranger"}, E["alar"], "medium",
    "No Blizzard source glosses 'alar' as phoenix; Al'ar is a proper name. The only gloss is Alar'annalas = Ranger Lord; Thalassian compounds are modifier-first (Quel'Thalas = High Home, Thas'alah = Light of the Forest), so alar = ranger, annalas = lord.")
fix("alar", "notes", "Name of Kael'thas' pet phoenix god, Al'ar.", "First element of Alar'annalas 'Ranger Lord' (Blood of the Highborne, ch. 2). Meaning from segmentation of an official compound. Al'ar (the phoenix) is a proper name with no official gloss.", E["alar"], "medium")
fix("anu", "translation", {"uk": "хай/привіт", "en": "hail/greetings"}, {"uk": "(частка звертання/побажання; точне значення невідоме)", "en": "(invocation/blessing particle; exact meaning unknown)"},
    E["dela"] + [ev("Anu'dorini Talah = Let my will be known.", DP), ev("Anu'shalla, Shadow's Guidance", W + "Anu%27shalla,_Shadow%27s_Guidance"), ev("Anu bala belore alon (or belore'alon) — Said by Nethermancer Sepethrea on death, and as a click quote by blood elf civilians in Midnight.", TU)], "high",
    "No gloss containing anu says hail or greetings. Anu occurs in blessings and wishes (Anu belore dela'na; Anu'dorini Talah = Let my will be known; Anu bala belore'alon). Best hypothesis: an optative 'may/let' particle; alternative from two mount epithets: 'guidance'.")
fix("ashal", "translation", {"uk": "великий/світлий", "en": "great/glorious"}, {"uk": "для (у 'ashal'anore' = 'для нашого народу')", "en": "for (in ashal'anore 'for our people')"},
    E["selama"] + [ev("[description; lyrics not reproduced] The Canticle of Sacrifice lyric table pairs the line made of ann'da + anore with an English line meaning father of our people (no 'for'), so anore = our people and ashal = for.", CANT)] + E["zhtw"], "medium",
    "The official gloss 'Justice for our people' has no 'great'. Alignment gives ashal = 'for'. A zhTW localization of 'Felomin ashal!' (Fire consumes!) suggests ashal is also a verb or a homonym, so the meaning is not settled.")
fix("dash", "translation", {"uk": "мир/шлях", "en": "peace/path"}, {"uk": "частина вітання 'bal'a dash' (вітаю)", "en": "part of the greeting bal'a dash ('greetings')"},
    [ev("Bal'a dash, malanore. || Greetings, traveler. || A greeting.", ENC_T)], "high", "The only gloss covers 'bal'a dash' as a unit ('Greetings'); 'peace' and 'path' have no source.")
fix("dela", "translation", {"uk": "вести/світити", "en": "guide/shine"}, {"uk": "вести", "en": "guide"}, E["dela"], "high", "'shine' has no source.")
fix("na", "translation", {"uk": "нас/ми", "en": "us/we"}, {"uk": "нас/наш (енклітика 1-ї особи множини)", "en": "us/our (1st person plural enclitic)"},
    E["dela"] + E["shindu"][1:2] + E["na_darn"], "high", "'na' is 'us' in dela'na and 'our' in the Lament gloss and in Darnassian 'Shu dalas na' (Heavy are our hearts); no source gives 'we'.")
fix("thalas", "translation", {"uk": "дім/королівство", "en": "home/kingdom"}, {"uk": "дім", "en": "home"},
    [ev("Quel'Thalas = High Home.", TP), ev("Quel'Thalas = \"High Kingdom\" or \"High Home\".", W + "Thalassian#In_the_RPG")], "high", "'Kingdom' comes only from the non-canon RPG (Lands of Conflict); the canon gloss is High Home (Chronicle Vol. 1 p.120).")
fix("melorn", "translation", {"uk": "удар/лють", "en": "strike/fury"}, {"uk": "удар", "en": "strike"}, [ev("Felo'melorn = Flamestrike.", TP)], "high", "'fury' has no source.")
fix("shindu", "translation", {"uk": "крах/приреченість", "en": "failing/doom"}, {"uk": "занепалий; у 'Shindu fallah na' = 'вони / наші вороги'", "en": "failing; in 'Shindu fallah na' it renders 'they / our enemies'"}, E["shindu"], "medium", "'doom' has no source; the two official glosses disagree, so both readings are kept.")
fix("fallah", "translation", {"uk": "прорив/атака", "en": "breakthrough/attack"}, {"uk": "проривати(ся)", "en": "break through"}, E["shindu"][:2], "high", "'attack' has no source.")
fix("bash'a", "translation", {"uk": "смерть/руйнування", "en": "death/destruction"}, {"uk": "скуштуй (наказовий спосіб)", "en": "taste (imperative)"}, E["bash"], "high",
    "'Death' is talah (cf. tal = death in Tal anu'men no Sin'dorei); the sentence-initial verb of 'Taste the chill of true death' is bash'a.")
fix("bash'a", "pos", "noun", "verb", E["bash"], "high")
fix("bash'a", "notes", "Bash'a no falor talah! (Kael'thas combat quote)", "Bash'a no falor talah! = Taste the chill of true death! Spoken by Sylvanas Windrunner in Warcraft III (Warcraft Encyclopedia, 2006).", E["bash"], "high")
fix("talah", "translation", {"uk": "вижити/витримати", "en": "survive/endure"}, {"uk": "(справжня) смерть", "en": "(true) death"}, E["bash"] + E["tal"], "high",
    "In 'Taste the chill of true death', taste = bash'a, chill = falor, so talah = (true) death; it shares the root tal 'death'.")
fix("talah", "pos", "verb", "noun", E["bash"], "high")
fix("anar", "translation", {"uk": "світло/через", "en": "light/by"}, {"uk": "через/клянусь (прийменник 'by')", "en": "by"}, E["anaralah"], "high",
    "Three official glosses start with 'By': Anar'alah, Anar'alah belore, Anar'endal dracon. 'Light' is alah (Thas'alah = Light of the Forest).")
fix("serrar", "source", "thalassian", "darnassian", [ev("Quel'Serrar = The High Blade.", DP), ev("It was forged by the combined effort of the five dragonflights and the night elves ... and was gifted to the kaldorei long ago.", W + "Quel%27Serrar")], "high")
fix("dracon", "source", "darnassian", "thalassian", [ev("Anar'endal dracon = By the breath of the dragon.", TP)], "high", "The phrase is listed in the Thalassian primer (Revelations comic; Through the Mirror Darkly).")
fix("shal'na", "translation", {"uk": "ні!/будь ласка (крик горя)", "en": "no! / please (cry of grief)"}, {"uk": "тітка", "en": "aunt"}, E["shalna"], "high",
    "Arator calls his aunt Vereesa 'Shal'na!' in the 11.2.7 quest What Might Come; Blizzard's zhCN localization renders it 阿姨 (auntie). Darnassian cognate: Shal'nar = Aunt.")
fix("shal'na", "pos", "interjection", "noun", E["shalna"], "high")
fix("shal'na", "notes", "Midnight (12.0) Alpha: Vereesa cries this seeing Rhonin's death", "Aunt. Said by Arator to Vereesa Windrunner in What Might Come (patch 11.2.7). Darnassian cognate Shal'nar 'Aunt' (Curse of the Worgen).", E["shalna"], "high")
fix("anu'shalla", "translation", {"uk": "вісник тіні", "en": "herald of shadow"}, {"uk": "Провід Тіні (епітет маунта)", "en": "Shadow's Guidance (mount epithet)"},
    [ev("Anu'shalla, Shadow's Guidance", W + "Anu%27shalla,_Shadow%27s_Guidance"), ev("A purple recolor of this mount, Anu'shalla, Shadow's Guidance, is an achievement reward from Insurmountable Collection, granted by collecting at least 600 mounts usable by a single character.", W + "Reins_of_Anu%27relos,_Flame%27s_Guidance")], "high",
    "It is a somnowl mount (reward for 600 mounts, added 12.0.0), a recolor of Anu'relos, Flame's Guidance from Amirdrassil; not a 'Void Owl' and not 'herald'.")
fix("anu'shalla", "source", "thalassian", "darnassian", [ev("Reins of Anu'relos, Flame's Guidance teach Anu'relos, Flame's Guidance, a fiery somnowl mount. This item drops from Fyrakk the Blazing in Mythic Amirdrassil, the Dream's Hope.", W + "Reins_of_Anu%27relos,_Flame%27s_Guidance")], "medium", "Emerald Dream / night elf context; the language is not stated, Darnassian is presumed.")
fix("lura", "source", "thalassian", "darnassian", [ev("Lura = Sea.", DP), ev("Hearthstone on Twitter, 2022-05-06 (Voyage to the Sunken City lyrics)", "https://twitter.com/PlayHearthstone/status/1522675071134879748")], "high",
    "The Voyage to the Sunken City song is Darnassian per the Hearthstone tweet. A Thalassian 'lura' is only a comparative-method prediction (identity).")
fix("lura", "translation", {"uk": "вода/море", "en": "water/sea"}, {"uk": "море", "en": "sea"}, [ev("Lura = Sea.", DP)], "high")
fix("ru", "translation", {"uk": "буде/виживати", "en": "will/survive"}, {"uk": "буде (частка майбутнього/модальності)", "en": "will (future/modal particle)"},
    [ev("Ru shanna shal'dorei or Ru-shanna shal'dorei = The nightborne will survive.", SP)], "medium", "'survive' is shanna; ru aligns with 'will'.")
fix("ashar", "translation", {"uk": "дуель/честь", "en": "duel/honor"}, {"uk": "дуель", "en": "duel"}, [ev("Tal'ashar = An honor duel.", SP)], "medium", "Modifier-first compound: tal'ashar = honor-duel, so ashar = duel; 'tal' here is a Shalassian homograph of Thalassian tal 'death'.")
fix("do", "translation", {"uk": "вчитель", "en": "teacher"}, {"uk": "вчитель; шанобливий суфікс -'do", "en": "teacher; honorific suffix -'do"},
    [ev("Shan'do = Honored Teacher.", DP), ev("Minn'do = Mother. Seems to be more formal than min'da, based on the suffix 'do which is shared with shan'do and nahlen'do.", DP), ev("Nahlen'do = Master of the Fang", DP)], "medium")
fix("minda", "word", "minda", "min'da", [ev("Min'da = Mama.", DP)], "high", "Attested spelling has an apostrophe; this entry is Darnassian. Thalassian is Minn'da (see add).")
fix("anda", "word", "anda", "an'da", [ev("An'da = Papa/Father.", DP)], "high", "Attested spelling has an apostrophe; this entry is Darnassian. Thalassian is Ann'da (see add).")
fix("bandor", "word", "bandor", "band'or", [ev("Band'or shorel'aran — (roughly) Prepare to say farewell. Spoken by Commander Sarannis, officially translated in the Chinese version of WoW.", TP)], "high")
fix("bandor", "notes", "Band'or shorel'aran", "From Band'or shorel'aran, '(roughly) Prepare to say farewell', a zhTW localization back-translated by a wiki user. Cognate of Darnassian bandu 'prepare' (Bandu thoribas = Prepare to fight).",
    [ev("Bandu Thoribas = Prepare to fight. (A challenge to an enemy.)", DP)], "medium")
fix("ban", "translation", {"uk": "брама/прохід", "en": "gate/passage"}, {"uk": "брама", "en": "gate"}, [ev("Ban'dinoriel = Gatekeeper.", TP)], "high", "'passage' has no source.")
fix("dinoriel", "translation", {"uk": "вартовий/охоронець", "en": "watcher/keeper"}, {"uk": "охоронець", "en": "keeper"}, [ev("Ban'dinoriel = Gatekeeper.", TP)], "high", "'watcher' has no source.")
fix("shala", "translation", {"uk": "подорож/шлях", "en": "travel/path"}, {"uk": "подорож/мандри", "en": "travels/journey"}, [ev("Al diel shala. || Safe travels. || A farewell.", ENC_T)], "high", "'path' has no source.")
fix("shola", "translation", {"uk": "справа/намір", "en": "business/intent"}, {"uk": "справа", "en": "business"}, [ev("Anaria shola. || Speak your business.", ENC_T)], "high", "'intent' has no source.")
fix("dris", "source", "generated_swadesh", "darnassian", [ev("Elun'dris = the Eye of Elune.", DP), ev("\"Dris\" = \"Eye\"", DSPEC)], "medium",
    "This 'generated' word coincides with the Darnassian morpheme dris 'eye' segmented from Elun'dris. Keep canon:false (segmentation), method 'segmentation of official compound'.")
fix("nu", "translation", {"uk": "білий/світлий", "en": "white/light"}, {"uk": "білий", "en": "white"}, [ev("Anar'alah = By the light.", TP), ev("Lu'selama = Light's Justice.", TP)], "medium",
    "Generated word whose 'light' sense shadows the canon alah and lu in the translator's first-match lookup.")

# ---------------- DEMOTIONS ----------------
demote("anu", "No Blizzard source gives 'hail/greetings'; meaning unknown (see fix).", [ev("Anu belore dela'na. || The sun guides us.", ENC_T)], "high")
demote("ashal", "The canon gloss is 'Justice for our people'; 'great/glorious' is unsupported and the replacement 'for' is inferred by alignment.", E["selama"], "high")
demote("dash", "No separate meaning is attested; only the unit 'bal'a dash' = 'Greetings'.", [ev("Bal'a dash, malanore. || Greetings, traveler.", ENC_T)], "high")
demote("delar", "No source glosses 'delar' as sword or keeper. The weapon's epithet is 'the Sister Blade', which does not decompose with quel = high.",
       [ev("Quel'Delar, the Sister Blade ... is one of the first Prismatic Blades.", W + "Quel%27Delar"), ev("\"Quel'Serrar\" means \"the High Blade\" and \"Quel'Delar\" means \"the Sister Blade\", which is odd because it is the \"Quel\" part that means \"high\".", W + "Talk:Thalassian#The_Twin_Blades")], "high")
demote("aran", "'Aran = Town' is listed only in the wiki's Speculation section, drawn from untranslated place names (Bashal'Aran, Ameth'Aran).", [ev("Based on the primer above, one can draw several conclusions as to the meanings of specific words ... \"Aran\" = \"Town\"", DSPEC)], "high")
demote("rath", "Untranslated; meaning guessed from the spell being cast.", [ev("Rath and Rath-domaas - Said by First Arcanist Thalyssra to fire arcane missiles at enemies.", SU), ev("E'rath omnas - Said by First Arcanist Thalyssra while casting an arcane shield bubble.", SU)], "high")
demote("kanesh", "Untranslated; meaning guessed from context (start/end of a recording).", [ev("Ith'el kanesh - Said by First Arcanist Thalyssra to start her magical recordings.", SU), ev("Ith'nala kanesh - Said by First Arcanist Thalyssra to end her magical recordings.", SU)], "high")
demote("anu'shalla", "Mount epithet, not a Blizzard translation statement; not Thalassian; previous gloss and 'Midnight datamine' provenance were wrong.", [ev("Anu'shalla, Shadow's Guidance", W + "Anu%27shalla,_Shadow%27s_Guidance")], "high")
demote("isera", "No source glosses 'isera' as green. Ysera's name is not glossed, and 'Isera'duna' is a word from the in-game language scrambler.", [ev("Ten-letter words | Thero'shan, Isera'duna, Ash'therod, Dorados'no, Shar'adore", TPARSER)], "high")

# ---------------- REMOVALS ----------------
remove("el", "Fabricated by mis-segmenting 'diel' in 'Al diel shala' (Safe travels); there is no 'el' = peace. In Darnassian, Alor'el = Lover's Leaf, where el would be 'leaf'.", [ev("Al diel shala. || Safe travels. || A farewell.", ENC_T), ev("Alor'el = Lover's Leaf.", DP)], "high")
remove("rutaani", "Not a Thalassian word: the rutaani are a plant-like race native to Harandar in Midnight.", [ev("The rutaani are a race of plant-like humanoids native to Harandar.", W + "Rutaani")], "high")
remove("min", "Extrapolated from 'Felomin ashal!' on the false premise ashal = great. Blizzard's zhTW line reads 'Fire consumes!', which makes felomin the fire word, not min = blast.", E["zhtw"], "medium")
for w, why, conf in [
    ("elu'shin", "Generated 'sleep' that duplicates canon elor 'sleep' and reuses elu- from the canon phrase Elu'meniel with an invented meaning.", "medium"),
    ("ishala", "Generated 'heart' that duplicates canon alann 'heart'.", "medium"),
    ("suran", "Generated 'heart/soul' that duplicates canon alann and echoes Suramar.", "medium"),
    ("lubala", "Generated 'light' that duplicates the attested alah and lu 'light'.", "medium"),
    ("athar", "Generated 'gate' that duplicates canon ban 'gate' (Ban'dinoriel).", "medium"),
    ("thal", "Generated 'magic' that duplicates canon arkhana and reuses the root of thalas 'home'.", "medium"),
    ("thera", "Identical to a word in Blizzard's in-game Thalassian scrambler list; also an attested Darnassian form (Tor ilisar'thera'nal).", "medium"),
    ("ethala", "Identical to a word in Blizzard's in-game Thalassian scrambler list.", "medium"),
    ("shari", "Identical to a word in Blizzard's in-game Thalassian scrambler list.", "medium"),
    ("osa", "Identical to a word in Blizzard's in-game Thalassian scrambler list.", "medium"),
    ("an'dorei", "Etymology rests on an invented 'anu = self'; the form reads like a -dorei race name ('snow children', cf. an = snow in Andrassil).", "medium"),
    ("al'ore", "Etymology rests on an invented 'anu = self'; duplicates 'on' (I).", "low"),
    ("tala", "One edit from canon tal/talah 'death'; duplicates dris'ael 'see'.", "low"),
    ("thala", "Identical to the attested Shalassian form in 'Thala nar'valas' (untranslated); duplicates anor'ael 'live'.", "low"),
    ("sindor", "Reads as Sin'dor(ei) 'blood children'; misleading for 'gold'.", "low"),
    ("dorin", "One edit from attested 'dorini' (Enshu-falah-nah, dorini; scrambler list).", "low"),
]:
    remove(w, why + " Rename or drop.", E["parser"][:1] if w in ("thera", "ethala", "shari", "osa") else [ev("[analysis] Generated-word collision report: scripted edit-distance check against 273 attested elven forms.", "research/2026-11-revival/1-review-and-methods.md#13-generated-words-that-collide-with-or-shadow-canon")], conf)

# ---------------- ADDS: canon (Blizzard states the meaning) ----------------
def canon_t(word, en, uk, pos, root, notes, evid, conf="high", source="thalassian"):
    add(word, en, uk, pos, True, root, notes, source, evid, "official gloss", conf)
canon_t("alar'annalas", "ranger lord", "лорд-рейнджер", "noun", "alar + annalas", "Farstriders rank (Blood of the Highborne, ch. 2).", E["alar"])
canon_t("fora'nal", "ceremonial cloth draped on a newly appointed ranger lord", "церемоніальне полотно лорда-рейнджера", "noun", "fora'nal", "Blood of the Highborne: 'With this Fora'nal I appoint you Alar'annalas'.",
        [ev("The ranger-general drapes the new ranger lord in a Fora'nal cloth, symbolizing their progression", W + "Farstriders")], "medium")
canon_t("al diel shala", "safe travels", "безпечної дороги", "phrase", "al + diel + shala", "A farewell.", [ev("Al diel shala. || Safe travels. || A farewell.", ENC_T)])
canon_t("ama noral'arkhana", "saved by magic", "врятовані магією", "phrase", "ama + noral + arkhana", "Loreology tweet 438752691678744576 (dead link).", [ev("Ama noral'arkhana = Saved by magic.", TP)])
canon_t("anar'alah", "by the Light", "клянусь Світлом", "phrase", "anar + alah", "Oath / battle cry.", E["anaralah"][:1])
canon_t("anar'alah belore", "by the light of the sun", "світлом сонця", "phrase", "anar + alah + belore", "Battle cry or vow.", [ev("Anar'alah belore. || By the light of the sun. || Used as either a battle cry or a vow.", ENC_T)])
canon_t("anaria shola", "speak your business", "кажи, з чим прийшов", "phrase", "anaria + shola", "Businesslike greeting.", [ev("Anaria shola. || Speak your business. || A greeting often used in a businesslike context.", ENC_T)])
canon_t("anar'endal dracon", "by the breath of the dragon", "диханням дракона", "phrase", "anar + endal + dracon", "Revelations (comic); Through the Mirror Darkly.", [ev("Anar'endal dracon = By the breath of the dragon.", TP)])
canon_t("ann'da", "father, papa", "тато, батько", "noun", "ann'da", "Thalassian form (Descent, p.16); Darnassian An'da.", [ev("Ann'da = Papa/Father.", TP)])
canon_t("minn'da", "mother, mama", "мама, мати", "noun", "minn'da", "Thalassian form (Descent, p.16); Darnassian Min'da.", [ev("Minn'da = Mama/Mother.", TP)])
canon_t("anu belore dela'na", "the sun guides us", "сонце веде нас", "phrase", "anu + belore + dela + na", "Greeting among blood and high elves.", [ev("Anu belore dela'na. || The sun guides us. || A greeting exchanged only with blood elves or high elves.", ENC_T)])
canon_t("bal'a dash, malanore", "greetings, traveler", "вітаю, мандрівнику", "phrase", "bal'a dash + malanore", "Greeting.", [ev("Bal'a dash, malanore. || Greetings, traveler. || A greeting.", ENC_T)])
canon_t("ban'dinoriel", "gatekeeper (Silvermoon's shield)", "брамник (щит Срібномісяця)", "noun", "ban + dinoriel", "Arthas: Rise of the Lich King p.227.", [ev("Ban'dinoriel = Gatekeeper.", TP)])
canon_t("bash'a no falor talah", "taste the chill of true death", "скуштуй холод справжньої смерті", "phrase", "bash'a + no + falor + talah", "Sylvanas, Warcraft III.", E["bash"][:1])
canon_t("belono sil'aru, belore'dorei", "shoulder your burdens well, child of the sun", "неси свій тягар гідно, дитя сонця", "phrase", "belono + sil'aru + belore'dorei", "Ends the ranger lord appointing ceremony (Blood of the Highborne, ch. 2).", [ev("Belono sil'aru, belore'dorei = Shoulder your burdens well, child of the sun.", TP)])
canon_t("belore'dorei", "child of the sun", "дитя сонця", "noun", "belore + dorei", "Sean Copeland tweet 979043020837285888 (dead link).", [ev("Belore'dorei = Child of the Sun.", TP)])
canon_t("doral ana'diel", "how fare you?", "як ся маєш?", "phrase", "doral + ana + diel", "Greeting.", [ev("Doral ana'diel? || How fare you? || A greeting.", ENC_T)])
canon_t("elor bindel felallan morin'aminor", "sleep forever in quiet serenity", "спи вічно в тихому спокої", "phrase", "elor + bindel + felallan + morin'aminor", "Loreology tweet 451393848195821568 (dead link).", [ev("Elor bindel felallan morin'aminor = Sleep forever in quiet serenity.", TP)])
canon_t("elu'meniel mal alann", "may peace calm your heart", "хай мир заспокоїть твоє серце", "phrase", "elu'meniel + mal + alann", "Loreology tweet 451393978949062656 (dead link).", [ev("Elu'meniel mal alann = May peace calm your heart.", TP)])
canon_t("felo'melorn", "Flamestrike (Sunstrider runeblade)", "Вогнеудар (рунічний меч Сонцеходів)", "noun", "felo + melorn", "Arthas pp.237, 293.", [ev("Felo'melorn = Flamestrike.", TP)])
canon_t("kim'jael", "little rat", "щуреня", "noun", "kim + jael", "Nickname given by blood elves to a goblin scout.", [ev("Kim'jael = Little rat.", TP), ev("It means \"little rat\" in Thalassian.", W + "Kim%27jael")])
canon_t("medivh", "keeper of secrets", "охоронець таємниць", "noun", "medivh", "Warcraft Encyclopedia (2006).", [ev("medivh || keeper of secrets || When used as a proper noun, Medivh refers to the last Guardian of Tirisfal.", ENC_T)])
canon_t("quel'dorei", "children of noble birth; high elves", "діти шляхетного роду; високі ельфи", "noun", "quel + dorei", "Also Darnassian.", [ev("Quel'dorei = Children of Noble Birth (Highborne, High-borne, high elves).", DP)])
canon_t("quel'thalas", "High Home", "Високий Дім", "noun", "quel + thalas", "Chronicle Vol. 1 p.120.", [ev("Quel'Thalas = High Home.", TP)])
canon_t("ren'dorei", "children of the Void", "діти Безодні", "noun", "ren + dorei", "Void elves.", [ev("Ren'dorei = Children of the Void.", TP)])
canon_t("sin'dorei", "children of the blood", "діти крові", "noun", "sin + dorei", "Blood elves.", [ev("sin'dorei || children of the blood || Can also be interpreted as \"people of the bloodline\".", ENC_T)])
canon_t("selama ashal'anore", "justice for our people", "справедливість для нашого народу", "phrase", "selama + ashal + anore", "Vow or farewell.", E["selama"])
canon_t("shindu fallah na", "they're breaking through! / our enemies are breaking through", "вони проривають! / наші вороги проривають", "phrase", "shindu + fallah + na", "Warning that defenses are breached.", E["shindu"][:2])
canon_t("shindu sin'dorei", "failing children of the blood", "занепалі діти крові", "phrase", "shindu + sin + dorei", "Lament of the Highborne (item).", E["shindu"][2:])
canon_t("shorel'aran", "farewell", "прощавай", "interjection", "shorel + aran", "zhTW localization of BroadcastText 321680 renders it 再會了 'farewell'.", [ev("Shorel'aran. || Farewell. || A farewell.", ENC_T), ev("再會了... (zhTW localization of BroadcastText 321680 'Shorel'aran...')", WAGO.format(id=321680, loc="zhTW"))])
canon_t("sinu a'manore", "well met", "радий зустрічі", "phrase", "sinu + a + manore", "Also used by Aethas Sunreaver in The World Awaits (Midnight 12.0.1).", [ev("Sinu a'manore. || Well met. || A greeting.", ENC_T), ev("Sinu a'manore, <class>.", W + "The_World_Awaits_(Midnight)#Description")])
canon_t("tal anu'men no sin'dorei", "death to all who oppose the children of the blood", "смерть усім, хто проти дітей крові", "phrase", "tal + anu'men + no + sin'dorei", "High Astromancer Solarian (Loreology tweet 377918675669770241, dead link).", E["tal"])
canon_t("thas'alah", "Light of the Forest", "Світло Лісу", "noun", "thas + alah", "Mother tree of Eversong.", E["thasalah"][:1])
canon_t("thas'dorah", "Valor of the Forest", "Звитяга Лісу", "noun", "thas + dorah", "Windrunner bow.", [ev("Thas'dorah = Valor of the Forest.", TP), ev("He named the weapon Thas'dorah, \"Valor of the Forest.\"", W + "Thas%27dorah,_Legacy_of_the_Windrunners")])
canon_t("vendel'o eranu", "help me forget", "допоможи мені забути", "phrase", "vendel + o + eranu", "Beyond the Dark Portal pp.204, 238.", E["vendel"])
canon_t("band'or shorel'aran", "(roughly) prepare to say farewell", "(приблизно) готуйся прощатися", "phrase", "band'or + shorel'aran", "Commander Sarannis; meaning from Blizzard's zhTW localization, English is a wiki back-translation.", [ev("Band'or shorel'aran — (roughly) Prepare to say farewell. Spoken by Commander Sarannis, officially translated in the Chinese version of WoW.", TP)], "medium")
# Shalassian
canon_t("shal'dorei", "Nightborne", "Нічнонароджені", "noun", "shal + dorei", "", [ev("Shal'dorei = Nightborne.", SP)], source="shalassian")
canon_t("tal'ashar", "an honor duel", "дуель честі", "noun", "tal + ashar", "", [ev("Tal'ashar = An honor duel.", SP)], source="shalassian")
canon_t("erana-dora isil", "a thousand thanks upon you", "тисяча дяк тобі", "phrase", "erana + dora + isil", "", [ev("Erana-dora isil = A thousand thanks upon you.", SP)], source="shalassian")
canon_t("quel'vala thonos", "nobility through tradition", "шляхетність через традицію", "phrase", "quel + vala + thonos", "", [ev("Quel'vala thonos = Nobility through tradition.", SP)], source="shalassian")
canon_t("ru shanna shal'dorei", "the Nightborne will survive", "нічнонароджені виживуть", "phrase", "ru + shanna + shal'dorei", "", [ev("Ru shanna shal'dorei or Ru-shanna shal'dorei = The nightborne will survive.", SP)], source="shalassian")
# Darnassian
D = [
 ("shaha lor'ma", "thank you", "дякую", "phrase", "shaha + lor'ma", "War Crimes ch. 6; Christie Golden confirmed on Twitter.", "Shaha lor'ma = Thank you."),
 ("elune-adore", "Elune be with you", "хай Елуна буде з тобою", "phrase", "elune + adore", "Greeting of the Sisters of Elune.", "Elune-Adore = Elune be with you. (A greeting.)"),
 ("ishnu-alah", "good fortune to you", "щастя тобі", "phrase", "ishnu + alah", "Common greeting; used by Kael'thas in Warcraft III.", "Ishnu-alah = Good fortune to you. (A greeting.)"),
 ("ishnu-dal-dieb", "good fortune to your family", "щастя твоїй родині", "phrase", "ishnu + dal + dieb", "Greeting.", "Ishnu-dal-dieb = Good fortune to your family. (A greeting.)"),
 ("andu-falah-dor", "let balance be restored", "хай рівновагу буде відновлено", "phrase", "andu + falah + dor", "War cry after the Sundering.", "Andu-falah-dor = Let balance be restored. (A war cry.)"),
 ("ande'thoras-ethil", "may your troubles be diminished", "хай поменшає твоїх турбот", "phrase", "ande + thoras + ethil", "A farewell.", "Ande'thoras-ethil = May your troubles be diminished. (A farewell.)"),
 ("bandu thoribas", "prepare to fight", "готуйся до бою", "phrase", "bandu + thoribas", "Challenge to battle.", "Bandu Thoribas = Prepare to fight. (A challenge to an enemy.)"),
 ("ash karath", "do it", "зроби це", "phrase", "ash + karath", "Generic command.", "Ash karath = Do it."),
 ("fandu-dath-belore", "who goes there?", "хто йде?", "phrase", "fandu + dath + belore", "Military challenge. Note: belore here does not mean 'sun'.", "Fandu-dath-belore? = Who goes there?"),
 ("tor ilisar'thera'nal", "let our enemies beware", "хай стережуться наші вороги", "phrase", "tor + ilisar + thera + nal", "Ancient war cry.", "Tor ilisar'thera'nal = Let our enemies beware. (A war cry used against enemies since ancient times.)"),
 ("anu'dorini talah", "let my will be known", "хай знають мою волю", "phrase", "anu + dorini + talah", "Malfurion's war cry; Loreology tweet 465903699592626176.", "Anu'dorini Talah = Let my will be known."),
 ("shu dalas na", "heavy are our hearts", "важкі наші серця", "phrase", "shu + dalas + na", "Hearthstone Voyage to the Sunken City song (Hearthstone tweet 2022-05-06).", "Shu dalas na = Heavy are our hearts."),
 ("aria", "we face", "ми зустрічаємо (лицем до лиця)", "verb", "aria", "Hearthstone song.", "Aria = We face."),
 ("bessae", "from the", "від (артикль+прийменник)", "preposition", "bessae", "Hearthstone song.", "Bessae = From the."),
 ("denalore", "oblivion, devastation", "забуття, спустошення", "noun", "denalore", "Hearthstone song.", "Denalore = Oblivion, devastation."),
 ("shal'nar", "aunt", "тітка", "noun", "shal'nar", "Curse of the Worgen. Thalassian cognate: shal'na.", "Shal'nar = Aunt."),
 ("minn'do", "mother (formal)", "мати (шанобливо)", "noun", "minn + do", "More formal than min'da.", "Minn'do = Mother."),
 ("shen'dorei", "hidden people (the Skyborne)", "приховані люди (Небонароджені)", "noun", "shen + dorei", "WoW Forever (2026); also the name of language ID 310 in the Forever client.", "Shen'dorei = hidden people."),
 ("shen'dralar", "those who remain hidden", "ті, що лишаються прихованими", "noun", "shen + dralar", "Chronicle Vol. 1 p.139.", "Shen'dralar = Those Who Remain Hidden."),
 ("xaxas", "elemental fury, chaos, catastrophe", "стихійна лють, хаос", "noun", "xaxas", "Also a name for Deathwing.", "Xaxas = A short title with many meanings, all dire. \"Chaos\", \"fury\", \"The embodiment of elemental rage, such as found in erupting volcanos or shattering earthquakes\", \"elemental fury\", \"catastrophe\"."),
 ("kaldorei", "children of the stars", "діти зірок", "noun", "kal + dorei", "Night elves.", "Kaldorei = Children of the stars, people of the stars."),
 ("tal'doren", "the wild home", "дикий дім", "noun", "tal + doren", "", "Tal'doren = The wild home."),
 ("elun'dris", "the Eye of Elune", "Око Елуни", "noun", "elun + dris", "Chronicle Vol. 1 p.94.", "Elun'dris = the Eye of Elune."),
 ("irana'ethil", "shield against the Shadow", "щит проти Тіні", "noun", "irana + ethil", "Scarab Wall (Exploring Azeroth: Kalimdor p.108).", "Irana'ethil = Shield against the Shadow."),
 ("jai'alator", "noble blade of Elune", "шляхетний клинок Елуни", "noun", "jai + alator", "Stormrage p.84.", "Jai'alator = Noble blade of Elune."),
 ("lathar'lazal", "Seat of the Sky", "Престол Неба", "noun", "lathar + lazal", "Chronicle Vol. 1 p.95.", "Lathar'Lazal = Seat of the Sky."),
 ("nar'valas", "View of Unending Stars", "Вид на безкінечні зорі", "noun", "nar + valas", "Exploring Azeroth: Kalimdor p.56.", "Nar'valas = View of Unending Stars."),
 ("shalla'tor", "Shadow Render", "Роздирач Тіней", "noun", "shalla + tor", "Flashback p.22.", "Shalla'tor = Shadow Render."),
 ("shal'nan", "the Veiled One", "Завуальований", "noun", "shal + nan", "Title of the Skyborne rebel leader.", "Shal'nan = The Veiled One."),
 ("ellemayne", "reaver", "спустошувач", "noun", "ellemayne", "Flashback p.22.", "Ellemayne = Reaver."),
 ("alor'el", "lover's leaf", "листок закоханих", "noun", "alor + el", "A plant (Seeds of Faith).", "Alor'el = Lover's Leaf."),
 ("al'anath", "Frostsoul", "Морозна душа", "noun", "al + anath", "", "Al'anath = Frostsoul."),
 ("alash'anir", "venom and storm", "отрута і буря", "noun", "alash + anir", "", "Alash'anir = Venom and storm."),
 ("alara'shinu", "finding beauty in imperfection", "бачити красу в недосконалості", "phrase", "alara + shinu", "", "Alara'shinu = Finding beauty in imperfection."),
 ("ama'shan", "Honor of the Goddess (a title)", "Честь Богині (титул)", "noun", "ama + shan", "", "Ama'shan = Honor of the Goddess. A title."),
 ("bel'ameth", "the arms of the Goddess", "обійми Богині", "noun", "bel + ameth", "", "Bel'ameth = The arms of the Goddess."),
 ("eluvi'ana", "the Night Dancer", "Нічна Танцівниця", "noun", "eluvi + ana", "", "Eluvi'ana = The Night Dancer"),
 ("t'lara", "(derogatory) a warrior armed only with words", "(зневажл.) воїн, озброєний лише словами", "noun", "t'lara", "", "T'lara = A derogatory term for \"a warrior armed only with words\"."),
 ("shanna melor'ne adala fal", "the truth is a guiding light", "правда — провідне світло", "phrase", "shanna + melor'ne + adala + fal", "Curse of the Worgen. Note: shanna here is not Shalassian shanna 'survive'.", "Shanna melor'ne adala fal = The truth is a guiding light."),
 ("ru shallora enudoril", "I anoint these caretakers of the wild", "я помазую цих доглядачів дикої природи", "phrase", "ru + shallora + enudoril", "Voice of Elune; Loreology tweet 465903699592626176.", "Ru shallora enudoril = I anoint these caretakers of the wild."),
 ("zin-azshari", "the glory of Azshara", "слава Азшари", "noun", "zin + azshari", "", "Zin-Azshari = The glory of Azshara."),
 ("nahlen'do", "Master of the Fang", "Володар Ікла", "noun", "nahlen + do", "Wielder of the Scythe of Elune.", "Nahlen'do = Master of the Fang"),
]
for word, en, uk, pos, root, notes, quote in D:
    where = ENC_D if "||" in quote else DP
    canon_t(word, en, uk, pos, root, notes, [ev(quote, where)], source="darnassian")

# ---------------- ADDS: inferred (canon:false) ----------------
def inf(word, en, uk, pos, root, notes, source, evid, method, conf):
    add(word, en, uk, pos, False, root, notes, source, evid, method, conf)
inf("alah", "light", "світло", "noun", "alah", "Thalassian 'alah' = light. Homograph of the existing Darnassian entry alah 'to you' (Ishnu-alah); the lexicon needs homograph support (word + source as key). Shalassian In'alah (said while lighting lamps) fits the same sense.", "thalassian",
    E["anaralah"][:2] + E["thasalah"] + [ev("In'alah - Said by First Arcanist Thalyssra while casting a spell that powers up lights all over the outer wall.", SU)], "segmentation of official compounds + cross-situational alignment (3 phrases)", "high")
inf("lu", "light", "світло", "noun", "lu", "From the item name Lu'selama, Light's Justice (12.1.5).", "thalassian",
    [ev("Lu'selama = Light's Justice.", TP), ev("\"Light's Justice\" is likely the literal translation of \"Lu'selama\".", W + "Lu%27selama,_Light%27s_Justice")], "item epithet + segmentation (selama = justice is established)", "medium")
inf("lu'selama", "Light's Justice", "Справедливість Світла", "noun", "lu + selama", "Item name with English epithet; the wiki lists it in the official primer.", "thalassian", [ev("Lu'selama = Light's Justice.", TP)], "item epithet", "medium")
inf("dorah", "valor", "звитяга", "noun", "dorah", "From Thas'dorah 'Valor of the Forest' with thas = forest.", "thalassian", [ev("Thas'dorah = Valor of the Forest.", TP)], "segmentation of official compound", "high")
inf("'o", "me (1st person singular object enclitic)", "мене (енклітика)", "pronoun", "o", "Vendel'o eranu = Help me forget. Confirms the parser's 'o suffix, which the lexicon lacked.", "thalassian", E["vendel"], "segmentation of official phrase", "high")
inf("vendel", "help (verb)", "допомагати", "verb", "vendel", "Vendel'o eranu = Help me forget: verb + 'o + verb.", "thalassian", E["vendel"], "segmentation of official phrase", "medium")
inf("eranu", "forget (verb)", "забувати", "verb", "eranu", "Vendel'o eranu = Help me forget.", "thalassian", E["vendel"], "segmentation of official phrase", "medium")
inf("morin'aminor", "(in) quiet serenity", "(у) тихому спокої", "noun", "morin + aminor", "Canticle of Sacrifice lyric table glosses the line made of this word alone as 'in quiet serenity'; matches the Loreology phrase.", "thalassian",
    [ev("Elor bindel felallan morin'aminor = Sleep forever in quiet serenity.", TP), ev("[description; lyrics not reproduced] The Canticle of Sacrifice lyric table glosses the line consisting only of Morin'aminor as quiet serenity; the wiki does not cite a source for the translation.", CANT)], "cross-situational alignment (tweet + lyric sheet)", "medium")
inf("felallan", "(unglossed; possibly 'in' or an intensifier)", "(без перекладу)", "unknown", "felallan", "Present in the Loreology phrase but absent from the Canticle line with the same English, so it carries no visible meaning.", "thalassian",
    [ev("Elor bindel felallan morin'aminor = Sleep forever in quiet serenity.", TP)], "cross-situational alignment (negative evidence)", "low")
inf("mal", "your (possessive, before noun)", "твій", "pronoun", "mal", "Elu'meniel mal alann = May peace calm your heart; alann = heart, so mal = your by elimination.", "thalassian",
    [ev("Elu'meniel mal alann = May peace calm your heart.", TP)], "cross-situational alignment (elimination)", "low")
inf("anu'men", "all who oppose", "усі, хто протистоїть", "noun", "anu + men", "Tal anu'men no Sin'dorei: tal = death, Sin'dorei = children of the blood, no = the/to.", "thalassian", E["tal"], "segmentation of official phrase", "low")
inf("no", "the / of (linking particle before a noun phrase)", "(сполучна частка 'the/of')", "particle", "no", "Occurs only in the two 'death' phrases, before falor and Sin'dorei; aligns with English 'the'. Do not map English 'no' to anything else.", "thalassian",
    E["bash"][:1] + E["tal"], "cross-situational alignment", "low")
inf("anar'sin arkhana! anar'endal belore!", "by blood (and) magic! by the breath of the sun!", "кров'ю і магією! диханням сонця!", "phrase", "anar + sin + arkhana; anar + endal + belore", "Untranslated ritual chant (Talandra Dawnsprite, Flowers for Amalthea) decoded word by word with established morphemes.", "thalassian",
    [ev("Anar'sin arkhana! Anar'endal belore! — Said by Talandra Dawnsprite as part of a necromantic ritual during Flowers for Amalthea.", TU)], "compositional decoding with established morphemes", "medium")
inf("endala finel endal", "breathe your last breath!", "зроби останній подих!", "phrase", "endala + finel + endal", "Said by Nethermancer Sepethrea when killing a player; endal = breath (official), finel = the last (Darnassian, Elegy p.87).", "thalassian",
    [ev("Endala finel endal! — Said by Nethermancer Sepethrea when killing a player.", TU), ev("Finel = The last.", DP)], "compositional decoding + context", "low")
inf("din", "keep, defend", "охороняти", "verb", "din", "Ban'dinoriel = Gatekeeper; flavor text 'Thalas'din belore' on Fal'inrush, Defender of Quel'thalas.", "thalassian",
    [ev("Ban'dinoriel = Gatekeeper.", TP), ev("Thalas'din belore — From the flavor text on Fal'inrush, Defender of Quel'thalas#Heroic.", TU)], "segmentation + item-name context", "low")
inf("thalas'din belore", "defender of the home of the sun", "оборонець дому сонця", "phrase", "thalas + din + belore", "Flavor text of the crossbow Fal'inrush, Defender of Quel'thalas.", "thalassian",
    [ev("Thalas'din belore. (item flavor text of Fal'inrush, Defender of Quel'thalas)", W + "Fal%27inrush,_Defender_of_Quel%27thalas")], "compositional decoding + item-name context", "low")
inf("felomin ashal", "fire consumes!", "вогонь пожирає!", "phrase", "felomin + ashal", "Kael'thas (Magisters' Terrace) casting Flamestrike. Meaning from a zhTW client line reported on the wiki talk page; not independently verified.", "thalassian", E["zhtw"], "Blizzard zhTW localization (reported)", "medium")
inf("balamore shanal", "prepare to die!", "готуйся до смерті!", "phrase", "balamore + shanal", "Kael'thas (The Eye). zhTW localization as reported on the wiki talk page; not independently verified.", "thalassian", E["zhtw"], "Blizzard zhTW localization (reported)", "medium")
inf("anar'anel belore", "for the sun! / by the power of the sun", "заради сонця! / силою сонця", "phrase", "anar + anel + belore", "Kael'thas summoning a phoenix. zhTW 'For the sun' (reported); in English he alternates it with 'By the power of the sun' for the same ability, so anel may mean 'power'.", "thalassian",
    E["zhtw"] + [ev("Anar'anel belore — ... May translate to \"By the power of the sun,\" another line Kael'thas says for the same ability.", TU)], "Blizzard zhTW localization (reported) + context", "medium")
inf("quel'zaram", "High Blade (Lothar's sword)", "Високий Клинок", "noun", "quel + zaram", "Retail item 'Quel'Zaram, High Blade of the Lion' (10.1.5); the gloss originates in the non-canon RPG Shadows & Light p.172.", "thalassian",
    [ev("The sword impressed Medivh and he dubbed it Quel'Zaram - Thalassian for \"high blade\". (In the RPG section; source Shadows & Light p.172)", W + "Quel%27Zaram,_High_Blade_of_the_Lion#In_the_RPG")], "item epithet + RPG", "low")
inf("dor", "land, home", "земля, дім", "noun", "dor", "Kalimdor 'land of eternal starlight', Tal'doren 'the wild home', and the Canticle lyric gloss 'watch our land' for Ash'thero'dalah'dor.", "darnassian",
    [ev("Kalimdor ... (Titan and Darnassian for land of eternal starlight)", W + "Kalimdor"), ev("Tal'doren = The wild home.", DP), ev("[description; lyrics not reproduced] The Canticle of Sacrifice lyric table glosses the line Ash'thero'dalah'dor with an English line about watching over our land.", CANT)], "cross-situational alignment across Darnassian and Thalassian", "medium")
inf("shen", "hidden", "прихований", "adjective", "shen", "Shen'dorei = hidden people; Shen'dralar = those who remain hidden.", "darnassian",
    [ev("Shen'dorei = hidden people.", DP), ev("Shen'dralar = Those Who Remain Hidden.", DP)], "segmentation of two official compounds", "high")
inf("amir", "harmony", "гармонія", "noun", "amir", "Amirdrassil = Crown of Harmony.", "darnassian", [ev("Amirdrassil = Crown of Harmony.", DP)], "segmentation of official compound (drassil = crown)", "high")
inf("vor", "broken", "зламаний", "adjective", "vor", "Vordrassil = Broken Crown.", "darnassian", [ev("Vordrassil = Broken Crown.", DP)], "segmentation of official compound (drassil = crown)", "high")
inf("adore", "be with you (blessing)", "будь з тобою", "phrase", "adore", "Elune-adore = Elune be with you; Shalassian farewell An'ratha adore uses the same word.", "darnassian",
    [ev("Elune-Adore = Elune be with you. (A greeting.)", DP), ev("An'ratha ador and An'ratha adore - Said by Silgryn and First Arcanist Thalyssra as a farewell.", SU)], "segmentation + Shalassian usage context", "medium")
inf("relos", "flame", "полум'я", "noun", "relos", "Anu'relos, Flame's Guidance vs Anu'shalla, Shadow's Guidance (shalla = shadow); also Belor'relos, the Suncaller.", "darnassian",
    [ev("Reins of Anu'relos, Flame's Guidance", W + "Reins_of_Anu%27relos,_Flame%27s_Guidance"), ev("Anu'shalla, Shadow's Guidance", W + "Anu%27shalla,_Shadow%27s_Guidance")], "contrastive item epithets", "low")
inf("ilisar", "enemies", "вороги", "noun", "ilisar", "Tor ilisar'thera'nal = Let our enemies beware: nal = our (cf. na), so ilisar is the best candidate for 'enemies'.", "darnassian",
    [ev("Tor ilisar'thera'nal = Let our enemies beware.", DP)], "cross-situational alignment (elimination)", "low")
inf("arcana", "magic (Shalassian cognate of Thalassian arkhana)", "магія", "noun", "arcana", "Aran'arcana is a nightborne greeting and farewell; Thalassian arkhana = magic (Ama noral'arkhana).", "shalassian",
    [ev("Aran'arcana = Said as a greeting by First Arcanist Thalyssra and Silgryn, and as a farewell by Valtrois.", SU), ev("Ama noral'arkhana = Saved by magic.", TP)], "comparative method (kh ~ c correspondence, 1 pair)", "low")
inf("shaha lor'ma", "thank you (predicted Thalassian form)", "дякую (передбачена талассійська форма)", "phrase", "shaha + lor'ma", "Darnassian 'thank you'. Shared Darnassian/Thalassian vocabulary is mostly identical (quel, dorei, felo'melorn, ishnu'alah used by Kael'thas), so the predicted Thalassian form is unchanged. Intentional homograph of the Darnassian add with the same spelling.", "thalassian",
    [ev("Shaha lor'ma = Thank you.", DP), ev("Darnassian, Thalassian, and Najza seem to have many common phrases, as is evidenced by Prince Kael'thas' use of \"Ishnu'alah\"", W + "Darnassian#Related_languages")], "comparative method (identity prediction)", "low")

# Fills each fix's "old" value from the lexicon, so it has to run against the pre-merge lexicon (commit 42eb9cf).
LEX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "src", "thalassian", "data", "lexicon.json")
LEX = {e["word"]: e for e in json.load(open(LEX_PATH, encoding="utf-8"))}
for c in C:
    if c["action"] == "fix":
        c["old"] = LEX[c["word"]][c["field"]]
json.dump(C, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
import collections
cnt = collections.Counter((c["action"], c.get("confidence")) for c in C)
print(len(C), sorted(cnt.items()))
print("adds canon:", sum(1 for c in C if c["action"]=="add" and c["canon"]), "adds inferred:", sum(1 for c in C if c["action"]=="add" and not c["canon"]))
