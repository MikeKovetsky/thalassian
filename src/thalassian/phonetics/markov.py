import random
from collections import defaultdict
from typing import List, Dict

def build_markov_chain(words: List[str]) -> Dict[str, List[str]]:
    """Builds a character-level Markov chain from a list of words."""
    transitions = defaultdict(list)
    for word in words:
        chars = ['^'] + list(word.lower()) + ['$']
        for i in range(len(chars) - 1):
            transitions[chars[i]].append(chars[i+1])
    return transitions

def generate_word(transitions: Dict[str, List[str]], min_length: int = 3, max_length: int = 8) -> str:
    """Generates a word using the character-level Markov chain."""
    while True:
        word = []
        current = '^'
        while True:
            if current not in transitions or not transitions[current]:
                break
            next_char = random.choice(transitions[current])
            if next_char == '$':
                break
            word.append(next_char)
            current = next_char
        
        result = "".join(word)
        if min_length <= len(result) <= max_length:
            return result

def build_phonotactics(words: List[str]) -> Dict[str, List[str]]:
    """Builds a simple phonotactics transition model (bigrams) from roots."""
    transitions = defaultdict(list)
    for w in words:
        w = w.lower()
        for i in range(len(w)-1):
            transitions[w[i]].append(w[i+1])
    return transitions

def generate_root(transitions: Dict[str, List[str]], min_len: int = 3, max_len: int = 5) -> str:
    """Generates a brand new root based on Thalassian phonetics."""
    start_chars = [k for k in transitions.keys() if k.isalpha()]
    if not start_chars:
        return "shil"
        
    current = random.choice(start_chars)
    result = [current]
    
    while len(result) < max_len:
        if current in transitions and transitions[current]:
            next_char = random.choice(transitions[current])
            result.append(next_char)
            current = next_char
        else:
            break
            
        if len(result) >= min_len and random.random() < 0.3:
            break
            
    return "".join(result)
