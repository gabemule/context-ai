"""
Guidelines manager for Context-AI.

Handles loading and applying language-specific coding guidelines to prompts.
"""

from typing import List, Optional

from utils.logging import get_logger


class GuidelinesManager:
    """Manages coding guidelines for different languages."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self._guidelines_cache = {}
        self._load_guidelines()

    def _load_guidelines(self) -> None:
        """Load all available guidelines."""
        try:
            from .javascript import JAVASCRIPT_GUIDELINES, TYPESCRIPT_EXTENSIONS

            self._guidelines_cache = {
                "javascript": JAVASCRIPT_GUIDELINES,
                "typescript": JAVASCRIPT_GUIDELINES + TYPESCRIPT_EXTENSIONS,
                "js": JAVASCRIPT_GUIDELINES,
                "ts": JAVASCRIPT_GUIDELINES + TYPESCRIPT_EXTENSIONS,
                "jsx": JAVASCRIPT_GUIDELINES,
                "tsx": JAVASCRIPT_GUIDELINES + TYPESCRIPT_EXTENSIONS,
            }

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

        # JavaScript/TypeScript detection
        js_keywords = ["javascript", "js", "jsx", "react", "node.js", "npm", "yarn"]
        ts_keywords = ["typescript", "ts", "tsx", "interface", "type"]

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
            if ext in ["js", "jsx", "ts", "tsx"]:
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


# Global instance
_guidelines_manager = None


def get_guidelines_manager() -> GuidelinesManager:
    """Get the global guidelines manager instance."""
    global _guidelines_manager
    if _guidelines_manager is None:
        _guidelines_manager = GuidelinesManager()
    return _guidelines_manager
