"""
Guidelines manager for Context-AI.

Handles loading and applying language-specific coding guidelines to prompts.
"""

from pathlib import Path
from typing import Dict, List, Optional

from utils.logging import get_logger


class GuidelinesManager:
    """Manages coding guidelines for different languages."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self._guidelines_cache = {}
        self._guidelines_dir = None
        self._load_guidelines()

    def _get_guidelines_directory(self) -> Path:
        """Get or create the guidelines directory in ~/.context-ai/"""
        if self._guidelines_dir is None:
            from config.constants import DEFAULT_CONFIG_DIR
            
            config_dir = Path(DEFAULT_CONFIG_DIR).expanduser()
            self._guidelines_dir = config_dir / "guidelines"
            
            # Create directory if it doesn't exist
            self._guidelines_dir.mkdir(parents=True, exist_ok=True)
        
        return self._guidelines_dir

    def _ensure_default_guidelines_exist(self) -> None:
        """Ensure default guideline files exist, create them if missing."""
        guidelines_dir = self._get_guidelines_directory()
        
        # Default guidelines content
        defaults = self._get_default_guidelines()
        
        for language, content in defaults.items():
            guideline_file = guidelines_dir / f"{language}.md"
            
            if not guideline_file.exists():
                self.logger.debug(f"Creating default guidelines: {guideline_file}")
                try:
                    with open(guideline_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                except Exception as e:
                    self.logger.warning(f"Failed to create {guideline_file}: {e}")

    def _get_default_guidelines(self) -> Dict[str, str]:
        """Get default guidelines content from code modules."""
        defaults = {}
        
        try:
            from .javascript import JAVASCRIPT_GUIDELINES, TYPESCRIPT_EXTENSIONS
            from .python import PYTHON_GUIDELINES
            
            defaults["python"] = PYTHON_GUIDELINES
            defaults["javascript"] = JAVASCRIPT_GUIDELINES
            defaults["typescript"] = JAVASCRIPT_GUIDELINES + TYPESCRIPT_EXTENSIONS
            
        except Exception as e:
            self.logger.error("Failed to load default guidelines from code: %s", e)
        
        return defaults

    def _load_guidelines_from_files(self) -> Dict[str, str]:
        """Load guidelines from .md files in ~/.context-ai/guidelines/"""
        guidelines = {}
        guidelines_dir = self._get_guidelines_directory()
        
        # Supported languages
        language_files = {
            "python": ["python.md", "py.md"],
            "javascript": ["javascript.md", "js.md"],
            "typescript": ["typescript.md", "ts.md"],
        }
        
        for language, possible_files in language_files.items():
            content = None
            
            # Try each possible filename
            for filename in possible_files:
                file_path = guidelines_dir / filename
                if file_path.exists():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                        self.logger.debug(f"Loaded guidelines from: {file_path}")
                        break
                    except Exception as e:
                        self.logger.warning(f"Failed to read {file_path}: {e}")
            
            if content:
                guidelines[language] = content
        
        return guidelines

    def _load_guidelines(self) -> None:
        """Load all available guidelines from files or create defaults."""
        try:
            # Ensure default files exist
            self._ensure_default_guidelines_exist()
            
            # Load from files
            file_guidelines = self._load_guidelines_from_files()
            
            # Build cache with all language mappings
            self._guidelines_cache = {}
            
            for language, content in file_guidelines.items():
                # Primary language key
                self._guidelines_cache[language] = content
                
                # Add common aliases
                if language == "python":
                    self._guidelines_cache["py"] = content
                elif language == "javascript":
                    self._guidelines_cache["js"] = content
                    self._guidelines_cache["jsx"] = content
                elif language == "typescript":
                    self._guidelines_cache["ts"] = content
                    self._guidelines_cache["tsx"] = content

            self.logger.debug(
                "Loaded guidelines for languages: %s",
                ", ".join(self._guidelines_cache.keys()),
            )

        except Exception as e:
            self.logger.error("Failed to load guidelines: %s", e)
            self._guidelines_cache = {}

    def get_guidelines_for_languages(self, languages: List[str]) -> Optional[str]:
        """
        Get combined guidelines for the given languages.

        Args:
            languages: List of detected languages in the context

        Returns:
            Combined guidelines string or None if no guidelines available
        """
        if not languages:
            return None

        applicable_guidelines = []
        seen_guidelines = set()

        for language in languages:
            lang_key = language.lower()
            if lang_key in self._guidelines_cache:
                guideline = self._guidelines_cache[lang_key]
                # Avoid duplicates
                if guideline not in seen_guidelines:
                    applicable_guidelines.append(guideline)
                    seen_guidelines.add(guideline)

        if not applicable_guidelines:
            return None

        # Combine guidelines with a header
        if len(applicable_guidelines) == 1:
            return applicable_guidelines[0]
        else:
            combined = "## 📋 Coding Guidelines for Multiple Languages\n\n"
            combined += "\n\n---\n\n".join(applicable_guidelines)
            return combined

    def detect_languages_in_context(self, context: str) -> List[str]:
        """
        Detect programming languages mentioned in the context.

        Args:
            context: The context string to analyze

        Returns:
            List of detected language names
        """
        # Simple detection based on keywords and file extensions
        languages = []
        context_lower = context.lower()

        # Python detection
        python_keywords = ["python", "py", "pip", "poetry", "django", "flask", "fastapi", "pytest", "pandas", "numpy"]
        
        # JavaScript/TypeScript detection
        js_keywords = ["javascript", "js", "jsx", "react", "node.js", "npm", "yarn"]
        ts_keywords = ["typescript", "ts", "tsx", "interface", "type"]

        # Check for Python keywords
        if any(keyword in context_lower for keyword in python_keywords):
            languages.append("python")
        
        # Check for JS/TS keywords
        if any(keyword in context_lower for keyword in ts_keywords):
            languages.append("typescript")
        elif any(keyword in context_lower for keyword in js_keywords):
            languages.append("javascript")

        # File extension detection
        import re

        # Look for code blocks with language hints
        code_block_pattern = r"```(\w+)"
        matches = re.findall(code_block_pattern, context_lower)
        for match in matches:
            if match in self._guidelines_cache:
                if match not in languages:
                    languages.append(match)

        # Look for file extensions in file paths
        file_ext_pattern = r"\.(\w+)(?:\s|$|,|;|\))"
        ext_matches = re.findall(file_ext_pattern, context_lower)
        for ext in ext_matches:
            if ext == "py":
                if "python" not in languages:
                    languages.append("python")
            elif ext in ["js", "jsx", "ts", "tsx"]:
                lang = "typescript" if ext in ["ts", "tsx"] else "javascript"
                if lang not in languages:
                    languages.append(lang)

        return languages

    def should_apply_guidelines(self, context: str, question: str) -> bool:
        """
        Determine if guidelines should be applied based on context and question.

        Args:
            context: The retrieved context
            question: The user's question

        Returns:
            True if guidelines should be applied
        """
        # Apply guidelines if:
        # 1. Code-related keywords in question
        # 2. Programming languages detected in context
        # 3. Implementation/development related queries

        question_lower = question.lower()
        code_keywords = [
            "implement",
            "code",
            "function",
            "class",
            "component",
            "method",
            "refactor",
            "optimize",
            "create",
            "build",
            "develop",
            "write",
            "how to",
            "example",
            "pattern",
            "architecture",
            "design",
        ]

        has_code_intent = any(keyword in question_lower for keyword in code_keywords)
        has_languages = len(self.detect_languages_in_context(context)) > 0

        return has_code_intent or has_languages

    def get_applicable_guidelines(self, context: str, question: str) -> Optional[str]:
        """
        Get guidelines that should be applied to the current prompt.

        Args:
            context: The retrieved context
            question: The user's question

        Returns:
            Guidelines string or None if not applicable
        """
        if not self.should_apply_guidelines(context, question):
            return None

        languages = self.detect_languages_in_context(context)
        if not languages:
            # If no specific language detected but code intent exists,
            # provide general guidelines
            return None

        guidelines = self.get_guidelines_for_languages(languages)

        if guidelines:
            self.logger.debug(
                "Applying guidelines for languages: %s", ", ".join(languages)
            )

        return guidelines

    def list_available_guidelines(self) -> List[str]:
        """List all available guideline languages."""
        guidelines_dir = self._get_guidelines_directory()
        
        # Find all .md files in guidelines directory
        available = []
        for file_path in guidelines_dir.glob("*.md"):
            language = file_path.stem
            available.append(language)
        
        return sorted(available)

    def get_guideline_content(self, language: str) -> Optional[str]:
        """Get the content of a specific guideline."""
        guidelines_dir = self._get_guidelines_directory()
        guideline_file = guidelines_dir / f"{language}.md"
        
        if not guideline_file.exists():
            return None
        
        try:
            with open(guideline_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Failed to read {guideline_file}: {e}")
            return None

    def save_guideline(self, language: str, content: str) -> bool:
        """Save content to a guideline file."""
        guidelines_dir = self._get_guidelines_directory()
        guideline_file = guidelines_dir / f"{language}.md"
        
        try:
            with open(guideline_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Reload guidelines cache
            self._load_guidelines()
            
            self.logger.info(f"Updated guidelines for {language}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save {guideline_file}: {e}")
            return False

    def reset_guideline_to_default(self, language: str) -> bool:
        """Reset a guideline to its default content."""
        defaults = self._get_default_guidelines()
        
        if language not in defaults:
            self.logger.error(f"No default guidelines available for {language}")
            return False
        
        return self.save_guideline(language, defaults[language])

    def get_guideline_file_path(self, language: str) -> Path:
        """Get the file path for a specific guideline."""
        guidelines_dir = self._get_guidelines_directory()
        return guidelines_dir / f"{language}.md"


# Global instance
_guidelines_manager = None


def get_guidelines_manager() -> GuidelinesManager:
    """Get the global guidelines manager instance."""
    global _guidelines_manager
    if _guidelines_manager is None:
        _guidelines_manager = GuidelinesManager()
    return _guidelines_manager
