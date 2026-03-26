import json
import random
import os

def load_lexicon():
    path = os.path.join(os.path.dirname(__file__), '../data/lexicon.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_roots_by_pos(lexicon, pos):
    return [entry for entry in lexicon if entry.get("pos") == pos and "root" in entry]

def combine_words(adj_root, noun_root):
    # Elvish combination rules often use apostrophes to combine two distinct concepts
    # e.g., Quel (High) + Dorei (Children) -> Quel'dorei
    # Felo (Fire) + Melorn (Strike) -> Felo'melorn
    
    # Sometimes they merge seamlessly:
    # Sindo (Blood) + dash (path) -> Sindash
    
    rule = random.choice(["apostrophe", "seamless"])
    
    if rule == "apostrophe":
        combined_word = f"{adj_root['word']}'{noun_root['word']}"
    else:
        combined_word = f"{adj_root['root']}{noun_root['word']}"
        
    translation_uk = f"{adj_root['translation']['uk']} {noun_root['translation']['uk']}"
    translation_en = f"{adj_root['translation']['en']} {noun_root['translation']['en']}"
    
    return {
        "word": combined_word.lower(),
        "translation": {
            "uk": translation_uk,
            "en": translation_en
        },
        "pos": "noun",
        "canon": False,
        "root": f"{adj_root['root']}{noun_root['root']}",
        "notes": f"Combined from {adj_root['word']} ({adj_root['translation']['en']}) and {noun_root['word']} ({noun_root['translation']['en']})",
        "source": "generated"
    }

if __name__ == "__main__":
    lexicon = load_lexicon()
    
    # Let's extract potential modifiers (adjectives/descriptive nouns) and base nouns
    adjectives = get_roots_by_pos(lexicon, "adjective")
    # We also use some nouns as modifiers (like Fire, Blood, Shadow, Sun)
    modifier_nouns = [w for w in lexicon if w["word"] in ["felo", "sin", "belore", "shal", "shalla", "ren"]]
    
    modifiers = adjectives + modifier_nouns
    nouns = get_roots_by_pos(lexicon, "noun")
    
    print("--- 10 Згенерованих Складних Слів (Lexicon Combiner) ---")
    generated = []
    
    for _ in range(10):
        mod = random.choice(modifiers)
        noun = random.choice(nouns)
        
        # Avoid combining a word with itself
        if mod["word"] == noun["word"]:
            continue
            
        combined = combine_words(mod, noun)
        generated.append(combined)
        
        print(f"- {combined['word'].capitalize()}: {combined['translation']['uk']} ({combined['translation']['en']})")
        print(f"  [Джерело: {mod['word']} + {noun['word']}]\n")
