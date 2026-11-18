import sys, json, re
sys.path.insert(0, sys.argv[1]); sys.path.insert(0, sys.argv[2] + "/src")
from corpus import CORPUS
from thalassian.core.lexicon import load_lexicon
from thalassian.syntax import parser as P
print("spaCy available:", P.USE_EN_NLP)
lex = load_lexicon()
def m(s): return [t for t in re.split(r"[\s'\-,.!?]+", s.lower()) if t]
rows = []
for lang, ph, gl, typ, src, where in CORPUS:
    if lang != "thal" or typ != "official": continue
    out = P.compile_sentence_en(gl, lex)
    ref = m(ph); hyp = m(re.sub(r"\[[^\]]*\]", "", out))
    common = sum(min(ref.count(x), hyp.count(x)) for x in set(ref))
    p = common / len(hyp) if hyp else 0; r = common / len(ref) if ref else 0
    f = 2 * p * r / (p + r) if p + r else 0
    exact = " ".join(ref) == " ".join(m(out))
    rows.append((ph, gl, out, round(f, 2), exact))
for r in rows: print(r)
n = len(rows)
print("N", n, "exact", sum(r[4] for r in rows), "meanF1", round(sum(r[3] for r in rows) / n, 3), "untranslated-bracket rate", round(sum('[' in r[2] for r in rows) / n, 2))
# probe specific bugs
for s in ["Justice for you", "I love you", "no", "light", "and", "by the light", "you", "great", "magic", "heart", "I sleep", "phoenix", "we", "the dead rise", "travelers", "children"]:
    print(repr(s), "->", P.compile_sentence_en(s, lex))
