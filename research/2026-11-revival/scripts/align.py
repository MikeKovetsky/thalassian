import re, sys, json, math, collections
sys.path.insert(0, sys.argv[1])
from corpus import CORPUS
LEMMA = {"children":"child","guides":"guide","travels":"travel","burdens":"burden","stars":"star","enemies":"enemy","hearts":"heart",
 "troubles":"trouble","caretakers":"caretaker","arms":"arm","heavens":"heaven","greetings":"greeting","breaking":"break","failing":"fail",
 "diminished":"diminish","restored":"restore","known":"know","saved":"save","light's":"light","lover's":"lover","shadow's":"shadow",
 "flame's":"flame","are":"be","is":"be","gatekeeper":"gate keeper","frostsoul":"frost soul","suncaller":"sun caller","flamestrike":"flame strike",
 "starlight":"star light","nightborne":"night borne","honored":"honor","guiding":"guide","unending":"unend","finding":"find","fare":"fare",
 "oppose":"oppose","caller":"call","journey":"travel","travels":"travel","papa":"father","mama":"mother","renderer":"render"}
STOP = set("the a an of to by for be in with you your our us we my me i they them it there all who these upon from and may let".split())
def etoks(s):
    out = []
    for w in re.findall(r"[a-z']+", s.lower()):
        w = w.strip("'")
        w = LEMMA.get(w, w)
        out.extend(w.split())
    return out
def ftoks(s):
    return [t for t in re.split(r"[\s'\-+,]+", s.lower()) if t]
def run(langs, types, content_only):
    data = []
    for lang, ph, gl, typ, src, where in CORPUS:
        if lang not in langs or typ not in types: continue
        f = ftoks(ph); e = etoks(gl)
        if content_only: e = [w for w in e if w not in STOP]
        data.append((f, e, ph, gl, lang, typ))
    # IBM model 1: t(e|f) with NULL
    fvocab = sorted({x for d in data for x in d[0]}); evocab = sorted({x for d in data for x in d[1]})
    t = collections.defaultdict(lambda: 1.0/len(evocab))
    for it in range(30):
        cnt = collections.defaultdict(float); tot = collections.defaultdict(float)
        for f, e, *_ in data:
            fs = f + ["<NULL>"]
            for ew in e:
                z = sum(t[(ew, fw)] for fw in fs)
                for fw in fs:
                    p = t[(ew, fw)] / z
                    cnt[(ew, fw)] += p; tot[fw] += p
        t = collections.defaultdict(float, {k: v / tot[k[1]] for k, v in cnt.items()})
    # co-occurrence
    nf = collections.Counter(); ne = collections.Counter(); c = collections.Counter()
    for f, e, *_ in data:
        for fw in set(f): nf[fw] += 1
        for ew in set(e): ne[ew] += 1
        for fw in set(f):
            for ew in set(e): c[(fw, ew)] += 1
    res = {}
    for fw in fvocab:
        cands = []
        for ew in evocab:
            if c[(fw, ew)] == 0: continue
            dice = 2 * c[(fw, ew)] / (nf[fw] + ne[ew])
            cands.append((round(t[(ew, fw)], 3), round(dice, 2), c[(fw, ew)], ew))
        cands.sort(reverse=True)
        phr = [d[2] for d in data if fw in d[0]]
        res[fw] = {"n": nf[fw], "cands": cands[:4], "phrases": phr}
    return res, data
if __name__ == "__main__":
    langs = set(sys.argv[2].split(","))
    types = set(sys.argv[3].split(","))
    content_only = sys.argv[4] == "content"
    res, data = run(langs, types, content_only)
    print("phrases:", len(data), "morpheme types:", len(res))
    for fw, r in sorted(res.items(), key=lambda kv: (-kv[1]["n"], kv[0])):
        print(f"{fw:14s} n={r['n']}  " + "; ".join(f"{e}(t={tp},dice={d},c={cc})" for tp, d, cc, e in r["cands"]) + "  <- " + " | ".join(r["phrases"][:5]))
