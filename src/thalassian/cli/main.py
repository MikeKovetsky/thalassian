import argparse
import sys
from ..core.lexicon import load_lexicon
from ..syntax.parser import compile_sentence_en, compile_sentence_uk
from ..phonetics.markov import build_markov_chain, generate_word, build_phonotactics, generate_root

def main():
    parser = argparse.ArgumentParser(description="Thalassian Language Tools")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Translate
    trans_parser = subparsers.add_parser("translate", help="Translate a sentence to Thalassian")
    trans_parser.add_argument("sentence", type=str, help="Sentence to translate")
    trans_parser.add_argument("--lang", type=str, choices=["en", "uk"], default="en", help="Source language")
    
    # Generate Words
    gen_word_parser = subparsers.add_parser("generate-words", help="Generate new Thalassian-sounding words")
    gen_word_parser.add_argument("-n", type=int, default=10, help="Number of words to generate")
    
    # Generate Roots
    gen_root_parser = subparsers.add_parser("generate-roots", help="Generate new Thalassian roots")
    gen_root_parser.add_argument("-n", type=int, default=10, help="Number of roots to generate")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
        
    lexicon = load_lexicon()
    
    if args.command == "translate":
        if args.lang == "en":
            result = compile_sentence_en(args.sentence, lexicon)
        else:
            result = compile_sentence_uk(args.sentence, lexicon)
        print(result)
        
    elif args.command == "generate-words":
        canon_words = [entry["word"] for entry in lexicon if entry.get("canon")]
        transitions = build_markov_chain(canon_words)
        
        generated = set()
        attempts = 0
        while len(generated) < args.n and attempts < args.n * 100:
            attempts += 1
            new_word = generate_word(transitions)
            if new_word not in canon_words:
                generated.add(new_word)
                
        for word in generated:
            print(f"- {word.capitalize()}")
            
    elif args.command == "generate-roots":
        canon_roots = [entry["root"] for entry in lexicon if entry.get("canon") and "root" in entry]
        transitions = build_phonotactics(canon_roots)
        
        for _ in range(args.n):
            new_root = generate_root(transitions)
            print(f"- {new_root.capitalize()}")

if __name__ == "__main__":
    main()
