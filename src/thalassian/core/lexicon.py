import json
import os
from typing import List, Dict, Optional

def get_lexicon_path() -> str:
    return os.path.join(os.path.dirname(__file__), '..', 'data', 'lexicon.json')

def load_lexicon() -> List[Dict]:
    path = get_lexicon_path()
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)
