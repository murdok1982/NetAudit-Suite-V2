import yaml
import os
import re
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0

class Scorer:
    def __init__(self, rules_dir: str):
        self.rules_dir = rules_dir
        self.rules = {}
        self._load_rules()

    def _load_rules(self):
        for filename in os.listdir(self.rules_dir):
            if filename.endswith(".yaml"):
                lang = filename.split(".")[0]
                with open(os.path.join(self.rules_dir, filename), 'r', encoding='utf-8') as f:
                    self.rules[lang] = yaml.safe_load(f)

    def detect_language(self, text: str) -> str:
        try:
            return detect(text)
        except:
            return "unknown"

    def calculate_score(self, text: str, lang: str = None) -> float:
        if not lang or lang not in self.rules:
            lang = self.detect_language(text)
            if lang not in self.rules:
                lang = "en" # Default to English rules if not found

        rules = self.rules.get(lang, {})
        score = 0.0
        
        # Phrases (High Risk)
        for phrase in rules.get("phrases_high_risk", []):
            if phrase.lower() in text.lower():
                score += 40.0
        
        # Keywords (Medium Risk)
        for keyword in rules.get("keywords_medium_risk", []):
            if keyword.lower() in text.lower():
                score += 15.0
        
        # Regex (Indicators)
        for pattern in rules.get("regex_indicators", []):
            if re.search(pattern, text):
                score += 25.0
                
        # Context Negation
        for neg in rules.get("context_negation", []):
            if neg.lower() in text.lower():
                score -= 20.0

        return min(max(score, 0), 100)
