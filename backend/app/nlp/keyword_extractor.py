import spacy
import yaml
from pathlib import Path
from typing import List, Dict, Set, Tuple
from collections import Counter
import logging

# Configure logger
logger = logging.getLogger(__name__)

class KeywordExtractor:
    """
    Extracts games industry related keywords from text using spaCy and a configuration file.
    """
    
    def __init__(self, config_path: str = "config/keywords.yaml"):
        """
        Initialize the extractor.
        
        Args:
            config_path: Path to the keywords configuration YAML file
        """
        self.config_path = config_path
        self.nlp = self._load_spacy_model()
        self.keywords_config = self._load_config()
        self.matcher = self._build_matcher()
        
    def _load_spacy_model(self):
        """Load spaCy model (en_core_web_sm)."""
        try:
            return spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("Spacy model 'en_core_web_sm' not found. Downloading...")
            from spacy.cli import download
            download("en_core_web_sm")
            return spacy.load("en_core_web_sm")

    def _load_config(self) -> Dict:
        """Load keywords from YAML configuration."""
        try:
            # Adjust path if running from different contexts
            path = Path(self.config_path)
            if not path.exists():
                # Try finding it relative to project root if not found
                # Assuming this runs from backend/ or scraper/
                possible_paths = [
                    Path("config/keywords.yaml"),
                    Path("../config/keywords.yaml"),
                    Path("../../config/keywords.yaml"),
                     Path("c:/Users/kabil/OneDrive/Desktop/Gaming_industry/config/keywords.yaml")
                ]
                for p in possible_paths:
                    if p.exists():
                        path = p
                        break
            
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load keywords config: {e}")
            return {"skills": [], "software": [], "experience": []}

    def _build_matcher(self):
        """Build spaCy PhraseMatcher for efficient keyword matching."""
        from spacy.matcher import PhraseMatcher
        matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        
        # Iterate through categories in config
        for category, items in self.keywords_config.items():
            if not items:
                continue
                
            # Create patterns for each keyword
            patterns = [self.nlp.make_doc(str(item)) for item in items if item]
            
            # Add to matcher with category as ID
            matcher.add(category, patterns)
            
        return matcher

    def extract(self, text: str) -> Dict[str, List[str]]:
        """
        Extract keywords from text.
        
        Args:
            text: Job description or text to analyze
            
        Returns:
            Dictionary with categories as keys and lists of found keywords as values
            Example: {'skills': ['C++', 'Python'], 'software': ['Unity']}
        """
        if not text:
            return {}
            
        doc = self.nlp(text)
        matches = self.matcher(doc)
        
        found_keywords = {
            "skills": set(),
            "software": set(),
            "experience": set()
        }
        
        # Process matches
        for match_id, start, end in matches:
            category = self.nlp.vocab.strings[match_id]
            span = doc[start:end]
            keyword = span.text
            
            # Add to appropriate category
            if category in found_keywords:
                # Store original casing from config is hard, for now store matches
                # We could map back to canonical form if needed
                found_keywords[category].add(keyword)
                
        # Convert sets to sorted lists
        return {k: sorted(list(v)) for k, v in found_keywords.items() if v}

    def extract_with_counts(self, text: str) -> Dict[str, Dict[str, int]]:
        """
        Extract keywords and their occurrence counts.
        """
        if not text:
            return {}
            
        doc = self.nlp(text)
        matches = self.matcher(doc)
        
        counts = {
            "skills": Counter(),
            "software": Counter(),
            "experience": Counter()
        }
        
        for match_id, start, end in matches:
            category = self.nlp.vocab.strings[match_id]
            span = doc[start:end]
            keyword = span.text
            
            if category in counts:
                counts[category][keyword] += 1
                
        return {k: dict(v) for k, v in counts.items() if v}

# Singleton instance for easy import
# extractor = KeywordExtractor()
