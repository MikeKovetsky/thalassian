// The "Strict" engine of index.html, in both directions: pure functions over the lexicon, so node can
// test them (tests/web/translator.test.js). The forward rules mirror src/thalassian/syntax/parser.py:
// whole canon phrases first, then "by X" -> anar'X, then "X of the Y" -> Y'X, then pronoun suffixes,
// and word lookup that prefers what Blizzard glossed.
(function (root) {
    "use strict";

    // "and" and "by" are not dropped: canon has rea (and) and anar (by).
    const DROP_WORDS = new Set(["для", "в", "до", "на", "з", "за", "від", "про", "але",
        "for", "to", "the", "a", "an", "of", "in", "on", "with", "but"]);
    // Words that translate but never take a pronoun suffix: "and you" is not "rea'a".
    const FUNCTION_WORDS = new Set([...DROP_WORDS, "and", "by", "і", "та"]);
    const ARTICLES = new Set(["the", "a", "an"]);
    const PRONOUN_SUFFIXES = {
        "нас": "na", "ми": "anu", "нам": "na", "us": "na", "we": "anu",
        "ти": "a", "тобі": "a", "тебе": "a", "you": "a",
        "я": "o", "мені": "o", "мене": "o", "i": "o", "me": "o",
        "їх": "dan", "вони": "danu", "them": "dan", "they": "danu"
    };
    const PRONOUN_ENCLITICS = { "na": "us", "anu": "we", "a": "you", "o": "me", "dan": "them", "danu": "they" };
    const BASIS_RANK = { attested: 0, segment: 1, name: 2, epithet: 2, inferred: 3, unverified: 4, generated: 5 };
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
        const basis = e.canon_basis in BASIS_RANK ? BASIS_RANK[e.canon_basis] : Object.keys(BASIS_RANK).length;
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
    const isPronoun = item => isWord(item) && item.lower in PRONOUN_SUFFIXES;
    // An item that translates to an elven word of its own: not punctuation, a function word or a pronoun.
    const isContent = item => item.kind !== "token" || (!item.punct && !FUNCTION_WORDS.has(item.lower) && !isPronoun(item));

    // The longest spans whose words equal a phrasebook sense. A span starts at a word that counts (not an
    // article) and may run over commas, but not over other punctuation.
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
                    if (words.length && book.has(key.join(" "))) found = { end: j, entry: book.get(key.join(" ")) };
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

    // "by [the] X" -> anar'X, as in Anar'alah and Anar'endal.
    function applyProclitics(items) {
        const out = [];
        for (let i = 0; i < items.length; i++) {
            if (isAny(items[i], BY)) {
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

    // "X of [the] Y" -> Y'X when X and Y are single words, as in Sin'dorei and Thas'alah. "of" before a
    // longer phrase ("the chill of true death", falor talah) or after "by X" ("by the light of the sun",
    // anar'alah belore) stays a free genitive, head first, as in canon.
    function applyCompounds(items) {
        const out = [];
        const contentWord = item => isWord(item) && isContent(item);
        for (let i = 0; i < items.length; i++) {
            if (isAny(items[i], OF) && out.length && contentWord(out[out.length - 1])) {
                const k = skipArticles(items, i + 1);
                const single = k < items.length && contentWord(items[k]) &&
                    !(k + 1 < items.length && isContent(items[k + 1]));
                if (single) {
                    out[out.length - 1] = { kind: "compound", head: out[out.length - 1], modifier: items[k] };
                    i = k;
                    continue;
                }
            }
            out.push(items[i]);
        }
        return out;
    }

    // A word followed by an object pronoun takes it as a suffix ("guide us" -> dela'na). A function word
    // does not ("justice for you" keeps its "you").
    function pairPronouns(items) {
        const out = [];
        for (let i = 0; i < items.length; i++) {
            const item = items[i];
            if (isWord(item) && !FUNCTION_WORDS.has(item.lower) && i + 1 < items.length && isPronoun(items[i + 1])) {
                out.push({ ...item, suffix: "'" + PRONOUN_SUFFIXES[items[i + 1].lower] });
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
        const items = pairPronouns(applyCompounds(applyProclitics(applyPhrasebook(tokens, book))));

        // "" for a dropped word; [word] for one the lexicon lacks.
        const word = item => {
            if (DROP_WORDS.has(item.lower)) return "";
            const found = findWord(lexicon, item.lower, canonOnly);
            return found ? found.word : `[${item.text}]`;
        };
        const render = item => {
            if (item.kind === "fixed") return item.text;
            if (item.kind === "proclitic") return attach(word(item.word), render(item.target));
            if (item.kind === "compound") {
                const head = findWord(lexicon, item.head.lower, canonOnly);
                if (head && NOUN_POS.has(head.pos)) return attach(render(item.modifier), render(item.head));
                return [render(item.head), render(item.modifier)].filter(Boolean).join(" ");
            }
            const w = word(item);
            return w && w + (item.suffix || "");
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
        // A phrase's gloss is shown by its first sense; a word's whole gloss proper is shown.
        // An entry whose meaning is unknown (empty gloss proper) shows as [word], like a missing one.
        const gloss = (e, w, first) => {
            const t = (first ? glossProper(e.translation.en).split("/")[0] : glossProper(e.translation.en)).trim();
            return t || `[${w}]`;
        };
        const lookup = w => {
            const exact = usable.filter(e => e.word.toLowerCase() === w);
            if (exact.length) return gloss(best(exact), w, false);
            const plural = usable.filter(e => {
                const s = e.word.toLowerCase();
                return s + "i" === w || s.slice(0, -1) + "ei" === w;
            });
            const found = best(plural);
            if (!found) return null;
            const t = gloss(found, w, false);
            return found.pos === "noun" && !t.startsWith("[") ? t + "(s)" : t;
        };

        const tokens = text.match(/[A-Za-z\']+|[.,!?;]/g) || [];
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
                key.push(tokens[j].toLowerCase());
                const k = key.join(" ");
                if (key.length >= 2 && phrases.has(k)) match = { end: j, entry: phrases.get(k), text: k };
            }
            if (match) {
                translated.push(gloss(match.entry, match.text, true));
                i = match.end + 1;
                continue;
            }
            const w = token.toLowerCase();
            const whole = lookup(w);
            if (whole !== null) {
                translated.push(whole);
            } else {
                w.split("'").filter(Boolean).forEach((part, n) => {
                    if (n > 0 && PRONOUN_ENCLITICS[part]) translated.push(PRONOUN_ENCLITICS[part]);
                    else translated.push(lookup(part) || `[${part}]`);
                });
            }
            i++;
        }
        return translated.join(" ").replace(/ ([.,!?;])/g, "$1");
    }

    const Translator = { strictTranslate, reverseTranslate, findWord, buildPhrasebook, glossProper, canonRank };
    if (typeof module !== "undefined" && module.exports) module.exports = Translator;
    else root.Translator = Translator;
})(this);
