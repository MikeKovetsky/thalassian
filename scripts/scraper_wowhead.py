import re
import argparse
from typing import List

# This is a stub scraper. In a real-world scenario with API access, 
# it would query Wowhead's XML/JSON endpoints for NPC Quotes / Dialogues from Patch 12.0+
# For now, it accepts a raw text file (e.g., dumped from game files or wiki pages) 
# and extracts potential Thalassian words based on their linguistic patterns.

def extract_thalassian_candidates(text: str) -> List[str]:
    """
    Extracts potential Thalassian/Darnassian/Shalassian words from a block of text.
    Pattern characteristics:
    - Often contain apostrophes (e.g., Sin'dorei, Felo'melorn)
    - Often end in specific vowels (e, a, o, i)
    - Can be capitalized (if at the start of a sentence or a proper noun)
    """
    # Regex for words with an apostrophe (the most obvious Elvish marker)
    apostrophe_pattern = re.compile(r'\b[A-Za-z]+(?:\'[A-Za-z]+)+\b', re.IGNORECASE)
    
    # Extract candidates
    candidates = apostrophe_pattern.findall(text)
    
    # Filter out common English contractions (don't, can't, I'm, etc.)
    english_contractions = {"don't", "can't", "won't", "i'm", "it's", "that's", "he's", "she's", "we're", "they're", "you're", "isn't", "aren't", "didn't", "hasn't", "haven't", "hadn't", "doesn't", "wasn't", "weren't", "shouldn't", "wouldn't", "couldn't", "mightn't", "mustn't", "let's", "who's", "what's", "where's", "when's", "why's", "how's", "i've", "you've", "we've", "they've", "i'd", "you'd", "he'd", "she'd", "we'd", "they'd", "i'll", "you'll", "he'll", "she'll", "we'll", "they'll"}
    
    valid_candidates = []
    for word in candidates:
        if word.lower() not in english_contractions:
            valid_candidates.append(word)
            
    return list(set(valid_candidates))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract Thalassian word candidates from WoW text dumps (e.g., Midnight patch data).")
    parser.add_argument("--file", type=str, help="Path to the text file containing WoW dialogues/quotes.", required=False)
    
    args = parser.parse_args()
    
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text_content = f.read()
            candidates = extract_thalassian_candidates(text_content)
            
            output_file = "../data/midnight_candidates.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                for c in sorted(candidates):
                    f.write(f"{c}\n")
            print(f"Found {len(candidates)} potential Elvish words. Saved to {output_file}")
            
        except Exception as e:
            print(f"Error reading file: {e}")
    else:
        print("No file provided. Running in demo mode with sample Midnight text...")
        sample_text = "The Devouring Host is attacking! Xal'atath approaches the Sunwell. Lor'themar shouts: 'Anu'dorini Talah! Defend the Quel'dorei legacy! The Fal'inrush will not break. We cannot let them take the Arcan'dor! Don't yield!'"
        print(f"\nSample Text:\n{sample_text}\n")
        
        extracted = extract_thalassian_candidates(sample_text)
        print("Extracted Elvish Candidates:")
        for word in sorted(extracted):
            print(f"- {word}")
