"""
Guidelines Manager for Context-AI.

Provides fast access to coding guidelines for different programming languages.
Uses intelligent caching and lazy loading to optimize performance while ensuring
guidelines are always available when needed.
"""

import shutil
from pathlib import Path
from typing import Dict, List, Optional

from utils.logging import get_logger

__all__ = [
    "GuidelinesManager",
    "get_guidelines_manager",
]


class GuidelinesManager:
    """
    Fast access to coding guidelines with intelligent caching.

    Purpose: Provides instant access to language-specific coding guidelines
    without repeatedly reading files from disk. Automatically ensures
    guidelines are available when needed.

    Benefits:
    - Performance optimized with in-memory caching
    - Lazy loading - only loads guidelines when actually needed
    - Automatic template provisioning for missing guidelines
    - Supports multiple languages and combined guidelines
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        self._guidelines_copied = False
        self._cache: Dict[str, str] = {}

    def _get_user_guidelines_dir(self) -> Path:
        """Get user guidelines directory via StorageManager (centralized)."""
        from config.storage import get_storage_manager

        storage_manager = get_storage_manager()
        return storage_manager.path_manager.guidelines_dir

    def _get_template_guidelines_dir(self) -> Path:
        """Get template guidelines directory via StorageManager (centralized)."""
        from config.storage import get_storage_manager

        storage_manager = get_storage_manager()
        return storage_manager.path_manager.template_guidelines_dir

    def get_guideline(self, language: str) -> Optional[str]:
        """Get guideline content for a specific language."""
        # Ensure configs exist via SetupManager (no circular dependency!)
        user_guidelines_dir = self._get_user_guidelines_dir()
        if not user_guidelines_dir.exists() or not list(
            user_guidelines_dir.glob("*.md")
        ):
            self.logger.debug("Guidelines missing, ensuring via SetupManager...")
            from config.setup import get_setup_manager

            setup_manager = get_setup_manager()
            setup_manager.ensure_all_configs_exist()  # Direct setup, no circular dependency

        # Check cache first
        if language in self._cache:
            return self._cache[language]

        # Load from file using centralized path method
        guideline_file = self.get_guideline_file_path(language)

        if not guideline_file.exists():
            self.logger.debug(f"No guidelines found for language: {language}")
            return None

        try:
            content = guideline_file.read_text(encoding="utf-8").strip()
            self._cache[language] = content
            return content
        except Exception as e:
            self.logger.error(f"Failed to read guidelines for {language}: {e}")
            return None

    def get_available_languages(self) -> List[str]:
        """Get list of all available guideline languages."""
        # Ensure configs exist via SetupManager (no circular dependency!)
        user_dir = self._get_user_guidelines_dir()
        if not user_dir.exists():
            self.logger.debug(
                "Guidelines directory missing, ensuring via SetupManager..."
            )
            from config.setup import get_setup_manager

            setup_manager = get_setup_manager()
            setup_manager.ensure_all_configs_exist()  # Direct setup, no circular dependency

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

    def get_guideline_file_path(self, language: str) -> Path:
        """Get the file path for a specific language guideline."""
        return self._get_user_guidelines_dir() / f"{language}.md"

    def reset_to_default(self, language: str) -> bool:
        """Reset a language guideline to default template."""
        template_dir = self._get_template_guidelines_dir()
        template_file = template_dir / f"{language}.md"

        if not template_file.exists():
            self.logger.warning(f"No default template found for {language}")
            return False

        # Ensure user directory exists
        user_dir = self._get_user_guidelines_dir()
        if not user_dir.exists():
            from config.setup import get_setup_manager

            setup_manager = get_setup_manager()
            setup_manager.ensure_all_configs_exist()

        # Use centralized path method
        user_file = self.get_guideline_file_path(language)

        try:
            shutil.copy2(template_file, user_file)
            # Clear cache for this language
            self._cache.pop(language, None)
            self.logger.info(f"Reset {language} guidelines to default")
            return True
        except Exception as e:
            self.logger.error(f"Failed to reset {language} guidelines: {e}")
            return False

    def save_guideline(self, language: str, content: str) -> bool:
        """Save guideline content to file."""
        # Ensure configs exist via SetupManager
        user_guidelines_dir = self._get_user_guidelines_dir()
        if not user_guidelines_dir.exists():
            self.logger.debug(
                "Guidelines directory missing, ensuring via SetupManager..."
            )
            from config.setup import get_setup_manager

            setup_manager = get_setup_manager()
            setup_manager.ensure_all_configs_exist()

        # Use centralized path method
        guideline_file = self.get_guideline_file_path(language)

        try:
            guideline_file.write_text(content, encoding="utf-8")
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
