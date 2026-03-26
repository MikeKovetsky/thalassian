import json
import random
import sys
from collections import defaultdict

def load_lexicon(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        sys.exit(1)

def build_markov_chain(words):
    transitions = defaultdict(list)
    for word in words:
        chars = ['^'] + list(word.lower()) + ['$']
        for i in range(len(chars) - 1):
            transitions[chars[i]].append(chars[i+1])
    return transitions

def generate_word(transitions, min_length=3, max_length=8):
    while True:
        word = []
        current = '^'
        while True:
            # If a character has no outgoing transitions, force end of word
            if current not in transitions:
                break
            next_char = random.choice(transitions[current])
            if next_char == '$':
                break
            word.append(next_char)
            current = next_char
        
        result = "".join(word)
        if min_length <= len(result) <= max_length:
            return result

if __name__ == "__main__":
    lexicon_path = "data/lexicon.json"
    print(f"Loading canon lexicon from {lexicon_path}...")
    lexicon = load_lexicon(lexicon_path)
    
    canon_words = [entry["word"] for entry in lexicon if entry.get("canon")]
    print(f"Canon words loaded ({len(canon_words)}): {', '.join(canon_words)}")
    
    # We build a simple char-level Markov chain for demonstration
    transitions = build_markov_chain(canon_words)
    
    print("\n--- Generating 10 new Thalassian-sounding roots ---")
    generated_words = set()
    attempts = 0
    while len(generated_words) < 10 and attempts < 1000:
        attempts += 1
        new_word = generate_word(transitions)
        if new_word not in canon_words:
            generated_words.add(new_word)
            
    for word in generated_words:
        print(f"- {word.capitalize()}")
