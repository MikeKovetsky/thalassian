import sys, json, math, random, re, collections
sys.path.insert(0, sys.argv[1]); sys.path.insert(0, sys.argv[2])
from corpus import CORPUS
REPO = sys.argv[3]
lex = json.load(open(REPO + "/src/thalassian/data/lexicon.json"))
# canon morphemes from official corpus (all three languages), lowercase, apostrophes/hyphens split
def morphs(s):
    return [t for t in re.split(r"[\s'\-+,]+", s.lower()) if t and t.isalpha()]
canon = sorted({m for lang, ph, gl, typ, *_ in CORPUS if typ in ("official",) for m in morphs(ph) if len(m) >= 2 and m not in ("medivh",)})
# add attested untranslated Thalassian/Shalassian/Darnassian phrase words (wiki lists) as canon *forms* (form-only)
UNTR = """Anar'anel belore Andu fallah Anar'alash denal Anar'dalel Anar'sin arkhana Anar'endal belore Anu bala belore alon Aranal ledel Aseph-ah-balla nah Balamore shanal Bandal Belesa menoor Bin dorei am'ovel Diel fin'al Diel ma'ahn orindel'o Endala finel endal Endirina-dor Endo-enah Endorel aluminor Enshu-falah-nah dorini Felomin ashal Ishera-do Quel'falan danas Selama am'oronor Selama amor'anore Sha'amoor ara mashal Sha'amoor seabenal Thalas'din belore
Anar'amenos An'ah An'anora An'ratha ador adore an'tal-thandros Anath'ashar Aran'arcana Aran'ethil Arash-falas Ash'thoras denil E'rath omnas In'alah Ishnal toreth Ith'el kanesh Ith'nala kanesh Kal'theros maldin N'eth ana Nar'thalas vas manari Thala nar'valas Nor'bethos Rath-domaas Rath-anu'tanos Shal'asan torah Shanar daloras Tel'vasha Tel'velath Tenu'balah Tor'theras falar
Aludala Ana duna thera Anato retetour Anu'dora Anu Dorah Anu dorini ash'ka Anu dunah thalore Iseradune banthalos Anu therador mali Ash'al theradas Ashbalanol Ash rohk ilisar thandae Ashre thoraman Ash'thero danador Ash'therod nethanas Bathel'daelune Deronica Elun'falah shalar Elun'orin torel Enae elen'relos En'shu falah-nah Hinduli rethal Oshalan thara dormil Ishnu-talah Sael'ah Shal myrinan ishnu daldorah Thandae-alah Thara dormil dorah Tor falah-no dorah Zin-al-Elune"""
untr = sorted({m for m in morphs(UNTR) if len(m) >= 2})
canon_all = sorted(set(canon) | set(untr))
lex_canon_words = [e["word"] for e in lex if e.get("canon")]
lex_gen = [e["word"] for e in lex if e["source"] in ("generated", "generated_swadesh")]
lex_gen_m = sorted({m for w in lex_gen for m in morphs(w) if len(m) >= 2})
parser = """A N I O E D Da Lo An Ni Al Do Ri Su No Ano Dur Tal Nei Ash Dor Anu Fal Tur Ala Nor Osa Alah Andu Dath Mush Shar Thus Fulo Aman Diel Dieb Rini Anar Talah Adore Ishnu Bandu Balah Fandu Thera Turus Shari Shano Terro Eburi Dorini Shando Ethala Fallah Belore Do'rah Neph'o Asto're Man'ar Ishura U'phol T'as'e Anoduna Alah'ni Dor'Ano Al'shar Mush'al Aman'ni Shan're Mandalas Eraburis Dorithur Dal'dieb Thoribas D'ana'no Il'amare Neph'anis Dune'adah Banthalos Fala'andu Dath'anar Shari'fal Thori'dal Thero'shan Isera'duna Ash'therod Dorados'no Shar'adore U'phol'belore Fandu'talah Dor'ana'badu Thoribas'no'thera Turus'il'amare Shari'adune T'ase'mushal Shindu'fallah'na Ando'meth'derador Anu'dorannador Anu'dorinni'talah Esh'thero'mannash Asto're'dunadah"""
parser_m = sorted({m for m in morphs(parser) if len(m) >= 2})

# ---------- models ----------
# OLD: the repo's character bigram chain (cli generate-words / generate-roots)
def old_word_model(words, n, seed=1):
    random.seed(seed)
    trans = collections.defaultdict(list)
    for w in words:
        ch = ['^'] + list(w.lower()) + ['$']
        for i in range(len(ch) - 1): trans[ch[i]].append(ch[i + 1])
    out = set(); tries = 0
    while len(out) < n and tries < n * 200:
        tries += 1
        cur = '^'; wd = []
        while True:
            nx = random.choice(trans[cur])
            if nx == '$': break
            wd.append(nx); cur = nx
            if len(wd) > 12: break
        s = "".join(wd)
        if 3 <= len(s) <= 8: out.add(s)
    return sorted(out)
def old_root_model(roots, n, seed=2):
    random.seed(seed)
    trans = collections.defaultdict(list)
    for w in roots:
        w = w.lower()
        for i in range(len(w) - 1): trans[w[i]].append(w[i + 1])
    starts = [k for k in trans if k.isalpha()]
    out = []
    for _ in range(n):
        cur = random.choice(starts); res = [cur]
        while len(res) < 5:
            if trans[cur]:
                cur = random.choice(trans[cur]); res.append(cur)
            else: break
            if len(res) >= 3 and random.random() < 0.3: break
        out.append("".join(res))
    return out
# NEW: interpolated Kneser-Ney-ish (absolute discounting + backoff) character n-gram, order 4, with boundaries
class CharLM:
    def __init__(self, words, order=4, d=0.75):
        self.order = order; self.d = d
        self.counts = [collections.defaultdict(collections.Counter) for _ in range(order)]
        self.vocab = set("$")
        for w in words:
            s = "^" * (order - 1) + w + "$"
            for i in range(order - 1, len(s)):
                for k in range(order):
                    ctx = s[i - k:i] if k else ""
                    self.counts[k][ctx][s[i]] += 1
                self.vocab.add(s[i])
        self.V = len(self.vocab)
    def prob(self, ctx, ch, k=None):
        if k is None: k = self.order - 1
        ctx = ctx[-k:] if k else ""
        if k == 0:
            c = self.counts[0][""]; tot = sum(c.values())
            return (c[ch] + 1) / (tot + self.V)
        c = self.counts[k].get(ctx)
        lower = self.prob(ctx, ch, k - 1)
        if not c: return lower
        tot = sum(c.values()); types = len(c)
        return max(c[ch] - self.d, 0) / tot + (self.d * types / tot) * lower
    def logp(self, w):
        s = "^" * (self.order - 1) + w + "$"; lp = 0.0
        for i in range(self.order - 1, len(s)):
            lp += math.log(self.prob(s[:i], s[i]))
        return lp
    def sample(self, rng, maxlen=10):
        s = "^" * (self.order - 1)
        while True:
            ctx = s
            r = rng.random(); acc = 0.0
            chars = sorted(self.vocab)
            for ch in chars:
                acc += self.prob(ctx, ch)
                if r <= acc: break
            if ch == "$" or len(s) - (self.order - 1) >= maxlen: break
            s += ch
        return s[self.order - 1:]
VOW = set("aeiouy")
def syllables_ok(w):
    # elvish-like: no 3-consonant clusters except th/sh digraph combos, no double vowels other than ei/ai/ae/ia/io/ie, ends in vowel or l,r,n,s,h,th,sh,m,d,x
    w2 = w.replace("th", "θ").replace("sh", "ʃ")
    run = 0
    for c in w2:
        run = run + 1 if c not in VOW else 0
        if run >= 3: return False
    if re.search(r"(.)\1\1", w): return False
    if w2[-1] not in VOW and w2[-1] not in "lrnsθʃmdhx": return False
    return True
def edit(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]
def new_model(train, n, seed=3, mind=2):
    rng = random.Random(seed)
    lm = CharLM(train, 4)
    out = []; tries = 0
    banned = set(train) | set(parser_m)
    lens = collections.Counter(min(len(w), 9) for w in train if len(w) >= 3)
    quota = {L: round(n * c / sum(lens.values())) + 1 for L, c in lens.items()}
    have = collections.Counter()
    while len(out) < n and tries < n * 3000:
        tries += 1
        w = lm.sample(rng)
        if not (3 <= len(w) <= 9) or not syllables_ok(w): continue
        if have[min(len(w), 9)] >= quota.get(min(len(w), 9), 0): continue
        if min(edit(w, c) for c in banned) < mind: continue
        if w in out: continue
        out.append(w); have[min(len(w), 9)] += 1
    return out, lm
# ---------- discrimination test: can a classifier tell canon from generated? ----------
def ngrams(w, n=2):
    s = "^" + w + "$"
    g = [s[i:i + n] for i in range(len(s) - n + 1)]
    if n == 2: g.append("LEN%d" % min(len(w), 9)); g.append("LEN%d" % min(len(w), 9))
    return g
def nb_auc(pos, neg, folds=5, seed=7):
    rng = random.Random(seed)
    data = [(w, 1) for w in pos] + [(w, 0) for w in neg]
    rng.shuffle(data)
    scores = []
    for f in range(folds):
        test = data[f::folds]; train = [d for i, d in enumerate(data) if i % folds != f]
        cnt = {0: collections.Counter(), 1: collections.Counter()}; tot = {0: 0, 1: 0}
        for w, y in train:
            for g in ngrams(w) + ngrams(w, 3): cnt[y][g] += 1; tot[y] += 1
        V = len(set(cnt[0]) | set(cnt[1])) + 1
        for w, y in test:
            s = 0.0
            for g in ngrams(w) + ngrams(w, 3):
                s += math.log((cnt[1][g] + 1) / (tot[1] + V)) - math.log((cnt[0][g] + 1) / (tot[0] + V))
            scores.append((s, y))
    P = [s for s, y in scores if y == 1]; N = [s for s, y in scores if y == 0]
    wins = sum((p > q) + 0.5 * (p == q) for p in P for q in N)
    return wins / (len(P) * len(N))
def loo_ppl(train_words, model="new"):
    # leave-one-out per-character perplexity of canon words under the model
    tot_lp = 0.0; tot_ch = 0
    for i, w in enumerate(train_words):
        rest = train_words[:i] + train_words[i + 1:]
        if model == "new":
            lm = CharLM(rest, 4); lp = lm.logp(w)
        else:
            # repo bigram chain with add-one smoothing
            big = collections.defaultdict(collections.Counter); V = set("$")
            for x in rest:
                s = "^" + x + "$"
                for a, b in zip(s, s[1:]): big[a][b] += 1; V.add(b)
            s = "^" + w + "$"; lp = 0.0
            for a, b in zip(s, s[1:]):
                lp += math.log((big[a][b] + 1) / (sum(big[a].values()) + len(V) + 1))
        tot_lp += lp; tot_ch += len(w) + 1
    return math.exp(-tot_lp / tot_ch)
if __name__ == "__main__":
    print("canon morphemes (official glossed):", len(canon), "plus untranslated attested forms:", len(untr), "=> train", len(canon_all))
    old_w = old_word_model(lex_canon_words, 200)
    old_r = old_root_model([e["root"] for e in lex if e.get("canon")], 200)
    new_w, lm = new_model(canon_all, 200)
    def coll(ws):
        exact = [w for w in ws if w in set(canon_all) | set(parser_m)]
        near = [w for w in ws if w not in exact and min(edit(w, c) for c in canon_all) <= 1]
        return len(exact), len(near)
    def stats(name, ws):
        L = [len(w) for w in ws]; e, n_ = coll(ws)
        vr = sum(c in VOW for w in ws for c in w) / max(1, sum(L))
        ok = sum(syllables_ok(w) for w in ws) / len(ws)
        print(f"{name:34s} n={len(ws):3d} meanlen={sum(L)/len(L):.2f} vowel_ratio={vr:.2f} phonotactic_ok={ok:.2f} exact_canon_or_parser={e} edit1_to_canon={n_} AUC_vs_canon={nb_auc(canon_all, ws):.3f}")
    rr = random.Random(11); sh = canon_all[:]; rr.shuffle(sh)
    print("canon split-half AUC (should be ~0.5):", round(nb_auc(sh[:len(sh)//2], sh[len(sh)//2:]), 3))
    stats("repo generated lexicon words", lex_gen_m)
    stats("repo generate-words (old chain)", old_w)
    stats("repo generate-roots (old chain)", old_r)
    stats("Blizzard in-game parser words", parser_m)
    stats("NEW 4-gram KN + phonotactic filter", new_w)
    print("LOO per-char perplexity on canon: order-4 KN =", round(loo_ppl(canon_all, "new"), 2), " order-2 (repo-like) =", round(loo_ppl(canon_all, "old"), 2))
    print("sample old generate-words:", old_w[:25])
    print("sample old generate-roots:", old_r[:25])
    print("sample NEW:", new_w[:40])
    # which repo generated words collide with canon / parser / near-canon
    rows = []
    for e in lex:
        if e["source"] not in ("generated", "generated_swadesh"): continue
        for m in morphs(e["word"]):
            if len(m) < 2: continue
            hits = [c for c in canon_all if edit(m, c) <= (0 if len(m) <= 3 else 1)]
            p = [c for c in parser_m if c == m]
            if hits or p: rows.append((e["word"], e["translation"]["en"], m, hits[:4], p))
    print("\nGenerated lexicon words that equal / are 1 edit from attested canon forms or parser words:")
    for r in rows: print("  ", r)
    json.dump({"canon_all": canon_all, "new": new_w, "old_words": old_w, "old_roots": old_r}, open("phono_out.json", "w"))
