"""Score both translators on the 39 official Thalassian phrases of corpus.py, with the phrasebook on and off.

With the phrasebook on, a phrase whose gloss is in the lexicon is reproduced by lookup, so that score checks
the lookup, not the rules. The phrasebook-off score is the word-by-word engine on its own.
From the repo root (the web engine needs node):
  python3 research/2026-11-revival/scripts/evaltranslator.py
"""
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "src"))
from corpus import CORPUS  # noqa: E402
from thalassian.core.lexicon import load_lexicon  # noqa: E402
from thalassian.syntax.parser import compile_sentence_en  # noqa: E402

NODE = shutil.which("node")
RUNNER = os.path.join(REPO, "tests", "web", "run_translator.js")

GOLD = [(phrase, gloss) for lang, phrase, gloss, typ, _, _ in CORPUS if lang == "thal" and typ == "official"]


def words(text):
    """Lower-case words, split at spaces, apostrophes, hyphens and punctuation (as evalpy.py does)."""
    return [t for t in re.split(r"[\s'\-,.!?]+", text.lower()) if t]


def f1(ref, hyp):
    common = sum(min(ref.count(x), hyp.count(x)) for x in set(ref))
    p, r = (common / len(hyp) if hyp else 0), (common / len(ref) if ref else 0)
    return 2 * p * r / (p + r) if p + r else 0


def score(pairs):
    """pairs: (reference, output). Exact matches and mean F1 over words, untranslated [words] left out of F1."""
    exact = sum(words(ref) == words(out) for ref, out in pairs)
    mean = sum(f1(words(ref), words(re.sub(r"\[[^\]]*\]", "", out))) for ref, out in pairs) / len(pairs)
    return exact, round(mean, 3)


def python_translate(inputs, phrasebook=True):
    lexicon = load_lexicon()
    return [compile_sentence_en(s, lexicon, phrasebook=phrasebook) for s in inputs]


def web_translate(inputs, direction="forward", **options):
    """Run web/translator.js under node. Raises if node is missing."""
    if not NODE:
        raise RuntimeError("node is not installed")
    request = json.dumps({"direction": direction, "inputs": inputs, "options": options})
    done = subprocess.run([NODE, RUNNER], input=request, capture_output=True, text=True, check=True)
    return json.loads(done.stdout)


def main():
    phrases, glosses = [p for p, _ in GOLD], [g for _, g in GOLD]
    print(f"{len(GOLD)} official Thalassian phrases; exact matches and mean word F1")
    engines = [("python", lambda pb: python_translate(glosses, pb))]
    if NODE:
        engines.append(("web", lambda pb: web_translate(glosses, phrasebook=pb)))
    for name, run in engines:
        for phrasebook in (True, False):
            exact, mean = score(list(zip(phrases, run(phrasebook))))
            print(f"  {name:6} English -> Thalassian, phrasebook {'on ' if phrasebook else 'off'}: exact {exact}, F1 {mean}")
    if NODE:
        exact, mean = score(list(zip(glosses, web_translate(phrases, "reverse"))))
        print(f"  web    Thalassian -> English: exact {exact}, F1 {mean}")
    else:
        print("  web engine skipped: node is not installed")


if __name__ == "__main__":
    main()
