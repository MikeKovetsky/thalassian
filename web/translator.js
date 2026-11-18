// The "Strict" engine of index.html, in both directions: pure functions over the lexicon, so node can
// test them (tests/web/run_translator.js runs them for tests/test_syntax/test_translator_canon.py).
// The forward rules mirror src/thalassian/syntax/parser.py and docs/methodology/grammar.md: whole canon
// phrases first, then "By X" opening a clause -> anar'X, then names "X of the Y" -> Y'X, then possessives,
// then "By" again before a possessive, then pronoun suffixes, and word lookup that prefers what Blizzard
// glossed. Nouns have no plural.
(function (root) {
    "use strict";

    // "and" is not dropped: canon rea. "by" is dropped except where it opens an oath or invocation, where it
    // is anar' ("By the light", Anar'alah); the "by" of a passive is not anar' ("Saved by magic").
    const DROP_WORDS = new Set(["для", "в", "до", "на", "з", "за", "від", "про", "але",
        "for", "to", "the", "a", "an", "of", "in", "on", "with", "by", "but"]);
    // Words that translate but never take a pronoun suffix: "and you" is not "rea'a".
    const FUNCTION_WORDS = new Set([...DROP_WORDS, "and", "і", "та"]);
    const ARTICLES = new Set(["the", "a", "an"]);
    // Pronouns (grammar section 5), the same tables as src/thalassian/morphology/agglutination.py. One form
    // serves every role: an object clitic after a verb (dela'na), a free word elsewhere (na "we"). 'na and 'o
    // are canon; 'a and 'dan are invented. anu is a wish particle, not "we".
    // Maps, not plain objects: a typed word such as "constructor" must not find Object.prototype.
    const PRONOUN_FORMS = new Map(Object.entries({
        "we": "na", "us": "na", "i": "o", "me": "o", "you": "a",
        "he": "dan", "she": "dan", "it": "dan", "they": "dan", "him": "dan", "her": "dan", "them": "dan",
        "ми": "na", "нас": "na", "нам": "na", "нами": "na", "я": "o", "мене": "o", "мені": "o", "мною": "o",
        "ти": "a", "тебе": "a", "тобі": "a", "тобою": "a", "ви": "a", "вас": "a", "вам": "a", "вами": "a",
        "він": "dan", "вона": "dan", "воно": "dan", "вони": "dan", "його": "dan", "її": "dan", "їх": "dan",
        "йому": "dan", "їй": "dan", "їм": "dan", "ним": "dan", "нею": "dan", "ними": "dan", "нього": "dan",
        "неї": "dan", "них": "dan", "ньому": "dan", "ній": "dan"
    }));
    // A subject is a free word before its verb, so these subject forms never join the word before them:
    // "then we guide them" is [then] na dela'dan, not [then]'na.
    const SUBJECTS = new Set(["i", "we", "he", "she", "they", "я", "ми", "ти", "ви", "він", "вона", "воно", "вони"]);
    // Possessives: [form, before the noun]. mal "your" comes first (canon: mal alann, "your heart"); na "our"
    // follows the noun; o "my" and dan "his, her, its, their" follow it by analogy (invented). "yours" and the
    // other independent forms take the same forms, and the Ukrainian ones are listed in every case.
    const POSSESSIVES = new Map([
        ...["your", "yours", "твій", "твого", "твоєму", "твоїм", "твоя", "твоєї", "твоїй", "твою", "твоєю", "твоє",
            "твої", "твоїх", "твоїми", "ваш", "вашого", "вашому", "вашим", "ваша", "вашої", "вашій", "вашу", "вашою",
            "ваше", "ваші", "ваших", "вашими"].map(w => [w, ["mal", true]]),
        ...["our", "ours", "наш", "нашого", "нашому", "нашим", "наша", "нашої", "нашій", "нашу", "нашою", "наше",
            "наші", "наших", "нашими"].map(w => [w, ["na", false]]),
        ...["my", "мій", "мого", "моєму", "моїм", "моя", "моєї", "моїй", "мою", "моєю", "моє", "мої", "моїх",
            "моїми"].map(w => [w, ["o", false]]),
        ...["his", "her", "hers", "its", "their", "theirs", "його", "її", "їхній", "їхнього", "їхньому", "їхнім",
            "їхня", "їхньої", "їхню", "їхньою", "їхнє", "їхні", "їхніх", "їхніми"].map(w => [w, ["dan", false]])
    ]);
    const PRONOUN_ENCLITICS = new Map(Object.entries({ "na": "us", "a": "you", "o": "me", "dan": "him/her/it/them" }));
    // Free pronouns and possessives the lexicon lacks (na "us/our" is an entry).
    const FREE_PRONOUNS = new Map(Object.entries({
        "o": "I/me/my", "a": "you", "dan": "he/she/it/they/his/her/its/their", "mal": "your"
    }));
    const BASIS_RANK = new Map(Object.entries({ attested: 0, segment: 1, name: 2, epithet: 2, inferred: 3, unverified: 4, generated: 5 }));
    const NOUN_POS = new Set(["noun", "proper noun"]);
    const CONTRACTIONS = [[/'re\b/gi, " are"], [/'m\b/gi, " am"], [/'ve\b/gi, " have"], [/'ll\b/gi, " will"]];
    const WORD = /[a-zа-яєіїґ']+/g;
    const PUNCT = /^[.,!?;]$/;

    // The gloss without commentary: parentheses go first, because they may hold a ';'
    // ("the Veiled One (title of ...; rebel battle cry)"), then everything after the first ';'.
    function glossProper(s) {
        return s.replace(/\([^)]*\)/g, " ").split(";")[0];
    }

    const glossSenses = s => glossProper(s).toLowerCase().split(/[\/,]/).map(x => x.trim()).filter(Boolean);

    // Words a gloss mentions, from its short senses only (at most three words, like "break through");
    // a longer sense is a description: "Valanaar: the Skyborne town..." must not translate "town".
    const mentionWords = (s, splitter) => glossSenses(s)
        .map(sense => sense.split(splitter).filter(Boolean))
        .filter(words => words.length <= 3).flat();

    // Whole phrases (e.g. anar'alah = "by the Light") are not used word by word.
    const isPhrase = e => e.pos === "phrase" || e.word.includes(" ");

    // Lookup prefers what Blizzard glossed over what was inferred or generated, then Thalassian over
    // the other dialects; ties keep lexicon order.
    function canonRank(e) {
        const basis = BASIS_RANK.has(e.canon_basis) ? BASIS_RANK.get(e.canon_basis) : BASIS_RANK.size;
        return [basis, e.source === "thalassian" ? 0 : 1];
    }

    function moreCanon(a, b) {
        const [x, y] = [canonRank(a), canonRank(b)];
        return x[0] < y[0] || (x[0] === y[0] && x[1] < y[1]);
    }

    const best = entries => entries.reduce((top, e) => top === null || moreCanon(e, top) ? e : top, null);

    const allowed = (e, canonOnly) => !(canonOnly && !e.canon);

    function expandContractions(text) {
        text = text.replace(/’/g, "'");
        for (const [contraction, full] of CONTRACTIONS) text = text.replace(contraction, full);
        return text;
    }

    // The words of a gloss sense or an input span, without punctuation or English articles.
    const phraseKey = text => (expandContractions(text).toLowerCase().match(WORD) || []).filter(w => !ARTICLES.has(w));

    // An entry whose sense is exactly the word, or its singular, wins over one that only mentions it
    // ("ones" is ore "one", not shal'nan "the Veiled One"); among equals the most canon entry wins
    // ("keeper" is dinoriel, not delar).
    function findWord(lexicon, lower, canonOnly) {
        const usable = lexicon.filter(e => allowed(e, canonOnly) && !isPhrase(e));
        const senses = e => [e.translation.en, e.translation.uk].flatMap(glossSenses);
        // The plural guess of parser.py: "is" and "us" are not plurals.
        const plural = (lower.length > 3 && lower.endsWith("s") && !lower.endsWith("ss")) ||
            (lower.length > 2 && lower.endsWith("и"));
        const singular = plural ? lower.slice(0, -1) : null;
        for (const form of [lower, singular]) {
            const exact = form ? usable.filter(e => senses(e).includes(form)) : [];
            if (exact.length) return best(exact);
        }
        return best(usable.filter(e => {
            const uk = mentionWords(e.translation.uk, /[^\wа-яєіїґ\']+/);
            const en = mentionWords(e.translation.en, /[^\w']+/);
            return uk.includes(lower) || en.includes(lower) ||
                (singular !== null && (uk.includes(singular) || en.includes(singular)));
        }));
    }

    // Every gloss sense of two or more words, mapped to its most canon entry. A phrase's gloss splits only
    // at '/', because its commas are inside the sense ("greetings, traveler"); a word's commas separate
    // senses ("father, papa").
    function buildPhrasebook(lexicon, canonOnly) {
        const book = new Map();
        for (const e of lexicon) {
            if (!allowed(e, canonOnly)) continue;
            for (const gloss of [e.translation.en, e.translation.uk]) {
                if (!gloss) continue;
                const senses = isPhrase(e) ? glossProper(gloss).split("/") : glossSenses(gloss);
                for (const sense of senses) {
                    const key = phraseKey(sense);
                    if (key.length < 2) continue;
                    const k = key.join(" ");
                    if (!book.has(k) || moreCanon(e, book.get(k))) book.set(k, e);
                }
            }
        }
        return book;
    }

    const BY = new Set(["by"]);
    const OF = new Set(["of"]);
    const isWord = item => item.kind === "token" && !item.punct;
    const isAny = (item, words) => isWord(item) && words.has(item.lower);
    const isPronoun = item => isWord(item) && (PRONOUN_FORMS.has(item.lower) || POSSESSIVES.has(item.lower));
    const isCapitalized = item => isWord(item) && /^\p{Lu}/u.test(item.text);
    // An item that translates to an elven word of its own: not punctuation, a function word or a pronoun.
    const isContent = item => item.kind !== "token" || (!item.punct && !FUNCTION_WORDS.has(item.lower) && !isPronoun(item));

    // Whether items[i] opens a clause: nothing but articles before it, back to the start or punctuation.
    function clauseStart(items, i) {
        let k = i - 1;
        while (k >= 0 && isAny(items[k], ARTICLES)) k--;
        return k < 0 || (items[k].kind === "token" && items[k].punct);
    }
    const clauseEnd = (items, j) => j + 1 >= items.length || (items[j + 1].kind === "token" && items[j + 1].punct);

    // The longest spans whose words equal a phrasebook sense. A span starts at a word that counts (not an
    // article) and may run over commas, but not over other punctuation. A whole phrase is a fixed formula
    // used whole, so it must fill its clause: "The light of the sun guides us" must not put the
    // clause-opening anu of anu belore dela'na in the middle.
    function applyPhrasebook(tokens, book) {
        let longest = 0;
        for (const k of book.keys()) longest = Math.max(longest, k.split(" ").length);
        const out = [];
        for (let i = 0; i < tokens.length;) {
            let found = null;
            if (!tokens[i].punct && phraseKey(tokens[i].text).length) {
                const key = [];
                for (let j = i; j < tokens.length && key.length < longest; j++) {
                    if (tokens[j].punct) {
                        if (tokens[j].text !== ",") break;
                        continue;
                    }
                    const words = phraseKey(tokens[j].text);
                    key.push(...words);
                    const entry = words.length ? book.get(key.join(" ")) : undefined;
                    if (entry && (!isPhrase(entry) || (clauseStart(tokens, i) && clauseEnd(tokens, j)))) {
                        found = { end: j, entry };
                    }
                }
            }
            if (found) {
                out.push({ kind: "fixed", text: found.entry.word });
                i = found.end + 1;
            } else {
                out.push(tokens[i]);
                i++;
            }
        }
        return out;
    }

    function skipArticles(items, k) {
        while (k < items.length && isAny(items[k], ARTICLES)) k++;
        return k;
    }

    // "By [the] X", opening a clause, -> anar'X, as in the oaths Anar'alah and Anar'endal dracon. Any other
    // "by" is dropped.
    function applyProclitics(items) {
        const out = [];
        for (let i = 0; i < items.length; i++) {
            if (isAny(items[i], BY) && clauseStart(items, i)) {
                const k = skipArticles(items, i + 1);
                if (k < items.length && isContent(items[k])) {
                    out.push({ kind: "proclitic", word: items[i], target: items[k] });
                    i = k;
                    continue;
                }
            }
            out.push(items[i]);
        }
        return out;
    }

    // A name, "X of [the] Y" with X and Y capitalized ("Light of the Forest"), -> Y'X, as in Thas'alah and
    // Sin'dorei. The word after Y, if it is a content word, is kept as `after`: render decides whether the
    // name goes on past Y. Any other "of" phrase is left as it is: "of" and "the" drop out and the head
    // comes first, as in canon alah belore, endal dracon and falor talah.
    function applyCompounds(items) {
        const out = [];
        const contentWord = item => isWord(item) && isContent(item);
        for (let i = 0; i < items.length; i++) {
            const head = out[out.length - 1];
            if (isAny(items[i], OF) && out.length && contentWord(head) && isCapitalized(head)) {
                const k = skipArticles(items, i + 1);
                if (k < items.length && contentWord(items[k]) && isCapitalized(items[k])) {
                    const after = k + 1 < items.length && isContent(items[k + 1]) ? items[k + 1] : null;
                    out[out.length - 1] = { kind: "compound", head: out[out.length - 1], modifier: items[k], after };
                    i = k;
                    continue;
                }
            }
            out.push(items[i]);
        }
        return out;
    }

    // A possessive before a noun phrase: mal goes before it, na, o and dan after it. The noun phrase is the
    // next content word, with any adjectives before it: "our noble heart" is quel alann na. Anywhere else a
    // possessive word is a pronoun ("guide her" -> dela'dan).
    function applyPossessives(items, isAdjective) {
        const out = [];
        for (let i = 0; i < items.length; i++) {
            const item = items[i];
            if (isWord(item) && POSSESSIVES.has(item.lower)) {
                let end = i + 1;
                while (end + 1 < items.length && isContent(items[end]) && isAdjective(items[end]) &&
                    isContent(items[end + 1])) end++;
                if (end < items.length && isContent(items[end])) {
                    const [form, before] = POSSESSIVES.get(item.lower);
                    out.push({ kind: "possessive", word: item, form, before, targets: items.slice(i + 1, end + 1) });
                    i = end;
                    continue;
                }
            }
            out.push(item);
        }
        return out;
    }

    // The free form of a pronoun or possessive standing on its own ("we" -> na, "you" -> a).
    const pronounForm = lower => PRONOUN_FORMS.has(lower) ? PRONOUN_FORMS.get(lower) :
        POSSESSIVES.has(lower) ? POSSESSIVES.get(lower)[0] : null;

    // A word followed by an object pronoun takes it as a suffix ("guide us" -> dela'na). A function word
    // does not ("justice for you" keeps its "you"), nor does a pronoun: "I guide you" is o dela'a, with the
    // subject a free word before the verb. For the same reason a subject form ("we", "ми") never joins the
    // word before it.
    function pairPronouns(items) {
        const out = [];
        for (let i = 0; i < items.length; i++) {
            const item = items[i];
            const next = items[i + 1];
            if (isWord(item) && !FUNCTION_WORDS.has(item.lower) && !isPronoun(item) && next !== undefined &&
                isPronoun(next) && !SUBJECTS.has(next.lower)) {
                out.push({ ...item, pronoun: next });
                i++;
                continue;
            }
            out.push(item);
        }
        return out;
    }

    const attach = (first, second) => first && second ? `${first}'${second}` : first || second;

    function strictTranslate(lexicon, text, options = {}) {
        const canonOnly = !!options.canonOnly;
        const tokens = (expandContractions(text).match(/[A-Za-zА-Яа-яЄєІіЇїҐґ\']+|[.,!?;]/g) || [])
            .map(t => ({ kind: "token", text: t, lower: t.toLowerCase(), punct: PUNCT.test(t) }));
        const book = options.phrasebook === false ? new Map() : buildPhrasebook(lexicon, canonOnly);
        // Whether a word is an adjective tells how far a possessive's noun phrase goes, whatever Canon Only
        // shows of the word itself.
        const isAdjective = item => {
            const found = isWord(item) ? findWord(lexicon, item.lower, false) : null;
            return !!found && found.pos === "adjective";
        };
        const steps = applyPossessives(applyCompounds(applyProclitics(applyPhrasebook(tokens, book))), isAdjective);
        // "By" again after the possessives, for "By our blood" (anar'sin na).
        const items = pairPronouns(applyProclitics(steps));

        // "" for a dropped word; [word] for one the lexicon lacks.
        const word = item => {
            if (DROP_WORDS.has(item.lower)) return "";
            const form = pronounForm(item.lower);
            if (form) return form;
            const found = findWord(lexicon, item.lower, canonOnly);
            return found ? found.word : `[${item.text}]`;
        };
        const by = findWord(lexicon, "by", canonOnly);
        const isNoun = item => {
            const found = item && item.kind === "token" ? findWord(lexicon, item.lower, canonOnly) : null;
            return !!found && NOUN_POS.has(found.pos);
        };
        const render = item => {
            if (item.kind === "fixed") return item.text;
            if (item.kind === "proclitic") return attach(by ? by.word : "", render(item.target));
            if (item.kind === "possessive") {
                const target = item.targets.map(render).filter(Boolean).join(" ");
                return (item.before ? [item.form, target] : [target, item.form]).filter(Boolean).join(" ");
            }
            if (item.kind === "compound") {
                // The name goes on past Y when Y is not a noun or a noun follows it; a verb after Y ends it
                // ("the Children of the Blood guide us").
                const goesOn = item.after !== null && (!isNoun(item.modifier) || isNoun(item.after));
                if (isNoun(item.head) && !goesOn) return attach(render(item.modifier), render(item.head));
                return [render(item.head), render(item.modifier)].filter(Boolean).join(" ");
            }
            const w = word(item);
            if (!item.pronoun) return w;
            // A dropped base must not take the pronoun with it.
            if (!w) return word(item.pronoun);
            return `${w}'${pronounForm(item.pronoun.lower)}`;
        };

        const translated = [];
        for (const item of items) {
            if (item.kind === "token" && item.punct) {
                if (translated.length > 0) translated[translated.length - 1] += item.text;
                continue;
            }
            let elven = render(item);
            if (!elven) continue;
            if (translated.length === 0 || /[.!?;]$/.test(translated[translated.length - 1])) {
                elven = elven.charAt(0).toUpperCase() + elven.slice(1);
            }
            translated.push(elven);
        }
        return translated.join(" ").replace(/ ([.,!?;])/g, "$1");
    }

    // Phones type ’ for the apostrophe ("Bal’a"), and a quote mark around a word is not part of it
    // ("'Bal'a'" is Bal'a).
    const plainApostrophes = text => text.replace(/[‘’ʼ]/g, "'");
    const unquoted = w => w.replace(/^'+|'+$/g, "") || w;

    // Thalassian -> English. Multi-word entries ("al diel shala") are matched first, then each whole word
    // ("bal'a", "anar'alah"); only a word the lexicon lacks is split at its apostrophes, with 'na, 'o and
    // the other enclitic pronouns read as pronouns.
    function reverseTranslate(lexicon, text, options = {}) {
        const canonOnly = !!options.canonOnly;
        const usable = lexicon.filter(e => allowed(e, canonOnly));
        const wordKey = s => (s.toLowerCase().match(/[a-z']+/g) || []).join(" ");
        const phrases = new Map();
        let longest = 1;
        for (const e of usable) {
            const k = wordKey(e.word);
            const n = k.split(" ").length;
            if (n < 2) continue;
            if (!phrases.has(k) || moreCanon(e, phrases.get(k))) phrases.set(k, e);
            longest = Math.max(longest, n);
        }
        // A phrase's gloss is shown by its first sense; a word's whole gloss proper is shown. Its closing
        // ? or ! is left to the input's own punctuation ("Doral ana'diel?" is "how fare you?", not "??").
        // An entry whose meaning is unknown (empty gloss proper) shows as [word], like a missing one.
        const gloss = (e, w, first) => {
            const t = (first ? glossProper(e.translation.en).split("/")[0] : glossProper(e.translation.en))
                .trim().replace(/\s*[.!?]+$/, "");
            return t || `[${w}]`;
        };
        // Nouns have no plural, so a word is looked up as it is; a free pronoun the lexicon lacks reads
        // from the pronoun table.
        const lookup = w => {
            const exact = usable.filter(e => e.word.toLowerCase() === w);
            if (exact.length) return gloss(best(exact), w, false);
            return FREE_PRONOUNS.has(w) ? FREE_PRONOUNS.get(w) : null;
        };

        const tokens = plainApostrophes(text).match(/[A-Za-z\']+|[.,!?;]/g) || [];
        const translated = [];
        for (let i = 0; i < tokens.length;) {
            const token = tokens[i];
            if (PUNCT.test(token)) {
                if (translated.length > 0) translated[translated.length - 1] += token;
                i++;
                continue;
            }
            let match = null;
            const key = [];
            for (let j = i; j < tokens.length && key.length < longest; j++) {
                if (PUNCT.test(tokens[j])) {
                    if (tokens[j] !== ",") break;
                    continue;
                }
                key.push(unquoted(tokens[j].toLowerCase()));
                const k = key.join(" ");
                if (key.length >= 2 && phrases.has(k)) match = { end: j, entry: phrases.get(k), text: k };
            }
            if (match) {
                translated.push(gloss(match.entry, match.text, true));
                i = match.end + 1;
                continue;
            }
            // The word as typed first: 'o (me) is an entry with its apostrophe.
            const typed = token.toLowerCase();
            const w = lookup(typed) !== null ? typed : unquoted(typed);
            const whole = lookup(w);
            if (whole !== null) {
                translated.push(whole);
            } else {
                w.split("'").filter(Boolean).forEach((part, n) => {
                    if (n > 0 && PRONOUN_ENCLITICS.has(part)) translated.push(PRONOUN_ENCLITICS.get(part));
                    else translated.push(lookup(part) || `[${part}]`);
                });
            }
            i++;
        }
        return translated.join(" ").replace(/ ([.,!?;])/g, "$1");
    }

    // The pronoun tables are exported so a test can check them against the Python ones.
    const Translator = {
        strictTranslate, reverseTranslate, findWord, buildPhrasebook, glossProper, canonRank,
        PRONOUN_FORMS, POSSESSIVES, SUBJECTS
    };
    if (typeof module !== "undefined" && module.exports) module.exports = Translator;
    else root.Translator = Translator;
})(this);
