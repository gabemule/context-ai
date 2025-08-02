"""
Guidelines Manager for Context-AI.

Handles loading, caching and serving of language-specific coding guidelines with lazy copy.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Protocol
import shutil

from utils.logging import get_logger

__all__ = [
    'GuidelinesManager',
    'get_guidelines_manager',
]


class GuidelinesManager:
    """Central coordinator for guideline operations with lazy copy."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self._guidelines_copied = False
        self._cache: Dict[str, str] = {}
    
    def _get_user_guidelines_dir(self) -> Path:
        """Get user guidelines directory."""
        from config.constants.storage import DEFAULT_CONFIG_DIR
        return Path(DEFAULT_CONFIG_DIR).expanduser() / "config" / "guidelines"
    
    def _get_template_guidelines_dir(self) -> Path:
        """Get template guidelines directory."""
        # Point to samples/guidelines/
        current_file = Path(__file__)
        config_dir = current_file.parent.parent  # Go up to src/config/
        return config_dir / "samples" / "guidelines"
    
    def get_guideline(self, language: str) -> Optional[str]:
        """Get guideline content for a specific language."""
        # Ensure configs exist via centralized copy (SettingsManager)
        user_guidelines_dir = self._get_user_guidelines_dir()
        if not user_guidelines_dir.exists() or not list(user_guidelines_dir.glob("*.md")):
            self.logger.debug("Guidelines missing, ensuring via SettingsManager...")
            from config.settings import get_settings_manager
            get_settings_manager()  # This copies languages + guidelines + prompts
        
        # Check cache first
        if language in self._cache:
            return self._cache[language]
        
        # Load from file
        guideline_file = self._get_user_guidelines_dir() / f"{language}.md"
        
        if not guideline_file.exists():
            self.logger.debug(f"No guidelines found for language: {language}")
            return None
        
        try:
            content = guideline_file.read_text(encoding='utf-8').strip()
            self._cache[language] = content
            return content
        except Exception as e:
            self.logger.error(f"Failed to read guidelines for {language}: {e}")
            return None
    
    def get_available_languages(self) -> List[str]:
        """Get list of all available guideline languages."""
        # Ensure configs exist via centralized copy (SettingsManager)
        user_dir = self._get_user_guidelines_dir()
        if not user_dir.exists():
            self.logger.debug("Guidelines directory missing, ensuring via SettingsManager...")
            from config.settings import get_settings_manager
            get_settings_manager()  # This copies languages + guidelines + prompts
        
        user_dir = self._get_user_guidelines_dir()
        if not user_dir.exists():
            return []
        
        guideline_files = list(user_dir.glob("*.md"))
        return sorted([f.stem for f in guideline_files if f.stem != "README"])
    
    def get_guidelines_for_languages(self, languages: List[str]) -> Optional[str]:
        """Get combined guidelines for multiple languages."""
        if not languages:
            return None
        
        unique_guidelines = []
        seen_content = set()
        
        for language in languages:
            content = self.get_guideline(language)
            if content and content not in seen_content:
                unique_guidelines.append(content)
                seen_content.add(content)
        
        if not unique_guidelines:
            return None
        
        if len(unique_guidelines) == 1:
            return unique_guidelines[0]
        
        return self._combine_multiple_guidelines(unique_guidelines)
    
    def _combine_multiple_guidelines(self, guidelines: List[str]) -> str:
        """Combine multiple guidelines with proper formatting."""
        header = "## 📋 Coding Guidelines for Multiple Languages\n\n"
        separator = "\n\n---\n\n"
        return header + separator.join(guidelines)
    
    def save_guideline(self, language: str, content: str) -> bool:
        """Save guideline content to file."""
        # Ensure configs exist via centralized copy (SettingsManager)
        user_guidelines_dir = self._get_user_guidelines_dir()
        if not user_guidelines_dir.exists():
            self.logger.debug("Guidelines directory missing, ensuring via SettingsManager...")
            from config.settings import get_settings_manager
            get_settings_manager()  # This copies languages + guidelines + prompts
        
        guideline_file = self._get_user_guidelines_dir() / f"{language}.md"
        
        try:
            guideline_file.write_text(content, encoding='utf-8')
            # Clear cache for this language
            self._cache.pop(language, None)
            self.logger.info(f"Updated guidelines: {language}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save guidelines for {language}: {e}")
            return False
    
    def reload(self) -> None:
        """Reload all guidelines from disk."""
        self._cache.clear()
        self.logger.info("Guidelines cache reloaded")


# Global instance management
_guidelines_manager: Optional[GuidelinesManager] = None


def get_guidelines_manager() -> GuidelinesManager:
    """Get global GuidelinesManager instance."""
    global _guidelines_manager
    
    if _guidelines_manager is None:
        _guidelines_manager = GuidelinesManager()
    
    return _guidelines_manager


def reset_guidelines_manager() -> None:
    """Reset global instance (for testing)."""
    global _guidelines_manager
    _guidelines_manager = None
