"""
Language detection system for Context-AI.
Follows Single Responsibility Principle and Clean Architecture.
"""

import re
import hashlib
from typing import Set, List, Optional
from pathlib import Path

from utils.logging import get_logger


class ExtensionExtractor:
    """Single responsibility: extract file extensions from text (SRP)."""
    
    # Regex patterns (DRY principle)
    PATTERNS = [
        (r'\b\w+\.([a-zA-Z0-9]+)\b', 'filename.ext'),
        (r'\.([a-zA-Z0-9]+)\s+files?', '.ext files'),
        (r'\.([a-zA-Z0-9]+)\s+code', '.ext code'),
        (r'\.([a-zA-Z0-9]+)\s+scripts?', '.ext scripts'),
        (r'(`[^`]*\.([a-zA-Z0-9]+)`)', 'backtick filenames'),
    ]
    
    MAX_EXTENSION_LENGTH = 5
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self._cache = {}  # Simple instance cache
    
    def extract_from_text(self, text: str, valid_extensions: Set[str]) -> Set[str]:
        """Extract valid file extensions from text."""
        # Simple cache to avoid duplicate work
        text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        if text_hash in self._cache:
            return self._cache[text_hash]
        
        raw_extensions = set()
        
        for pattern, _ in self.PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                extensions = self._extract_extensions_from_match(match)
                raw_extensions.update(extensions)
        
        # Filter by valid extensions only
        valid_found = {ext for ext in raw_extensions if ext in valid_extensions}
        
        # Cache and return
        self._cache[text_hash] = valid_found
        return valid_found
    
    def _extract_extensions_from_match(self, match) -> Set[str]:
        """Extract extensions from regex match (handle tuples and strings)."""
        extensions = set()
        
        if isinstance(match, tuple):
            for group in match:
                if group and len(group) <= self.MAX_EXTENSION_LENGTH:
                    extensions.add(f".{group.lower()}")
        else:
            if match and len(match) <= self.MAX_EXTENSION_LENGTH:
                extensions.add(f".{match.lower()}")
        
        return extensions


class LanguageDetector:
    """Single responsibility: detect programming languages from context (SRP)."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.extractor = ExtensionExtractor()
    
    def detect_languages_from_context(self, context: str, question: str) -> List[str]:
        """Detect programming languages from context and question."""
        try:
            # Get managers (Dependency Injection principle)
            languages_manager = self._get_languages_manager()
            guidelines_manager = self._get_guidelines_manager()
            
            if not languages_manager or not guidelines_manager:
                return []
            
            # Extract extensions
            valid_extensions = languages_manager.get_supported_extensions()
            found_extensions = self.extractor.extract_from_text(
                context + " " + question, 
                valid_extensions
            )
            
            if not found_extensions:
                return []
            
            # Map to languages and filter by guidelines availability
            available_guidelines = set(guidelines_manager.get_available_languages())
            detected_languages = []
            
            for extension in found_extensions:
                language = languages_manager.detect_language_from_extension(extension)
                if language and language not in detected_languages and language in available_guidelines:
                    detected_languages.append(language)
            
            # Prioritize by importance
            return self._prioritize_languages(detected_languages, languages_manager)
            
        except Exception as e:
            self.logger.error("Failed to detect languages: %s", e)
            return []
    
    def _get_languages_manager(self):
        """Get languages manager (dependency injection point)."""
        try:
            from config.languages.manager import get_languages_manager
            return get_languages_manager()
        except ImportError:
            return None
    
    def _get_guidelines_manager(self):
        """Get guidelines manager (dependency injection point)."""
        try:
            from config.guidelines.manager import get_guidelines_manager
            return get_guidelines_manager()
        except ImportError:
            return None
    
    def _prioritize_languages(self, languages: List[str], languages_manager) -> List[str]:
        """Prioritize languages by importance (high priority first)."""
        if not languages:
            return []
        
        try:
            high_priority = languages_manager.get_high_priority_languages()
            prioritized = []
            
            # Add high priority first
            for lang in languages:
                if lang in high_priority:
                    prioritized.append(lang)
            
            # Add remaining
            for lang in languages:
                if lang not in prioritized:
                    prioritized.append(lang)
            
            return prioritized
        except:
            return languages


# Factory function (DRY principle)
def get_language_detector() -> LanguageDetector:
    """Get language detector instance."""
    return LanguageDetector()
