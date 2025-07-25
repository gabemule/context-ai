"""
Multi-language synonym and stop word system for Context-AI query expansion.

Always loads both English and Portuguese dictionaries since real codebases
are often mixed language.
"""

from typing import List, Set

from .en import ENGLISH_PROGRAMMING_KEYWORDS, ENGLISH_STOP_WORDS, ENGLISH_SYNONYMS
from .pt_br import (
    PORTUGUESE_PROGRAMMING_KEYWORDS,
    PORTUGUESE_STOP_WORDS,
    PORTUGUESE_SYNONYMS,
)

# Combine all dictionaries - no language selection needed
ALL_SYNONYMS = {}
ALL_SYNONYMS.update(ENGLISH_SYNONYMS)
ALL_SYNONYMS.update(PORTUGUESE_SYNONYMS)

ALL_STOP_WORDS = set()
ALL_STOP_WORDS.update(ENGLISH_STOP_WORDS)
ALL_STOP_WORDS.update(PORTUGUESE_STOP_WORDS)

ALL_PROGRAMMING_KEYWORDS = set()
ALL_PROGRAMMING_KEYWORDS.update(ENGLISH_PROGRAMMING_KEYWORDS)
ALL_PROGRAMMING_KEYWORDS.update(PORTUGUESE_PROGRAMMING_KEYWORDS)


def get_synonyms(word: str) -> List[str]:
    """Get synonyms for a word (from all languages)."""
    return ALL_SYNONYMS.get(word.lower(), [])


def has_synonyms(word: str) -> bool:
    """Check if word has synonyms."""
    return word.lower() in ALL_SYNONYMS


def is_stop_word(word: str) -> bool:
    """Check if word is a stop word."""
    return word.lower() in ALL_STOP_WORDS


def is_programming_keyword(word: str) -> bool:
    """Check if word is a programming keyword that should be preserved."""
    return word.lower() in ALL_PROGRAMMING_KEYWORDS


def should_remove_word(word: str) -> bool:
    """
    Check if word should be removed as stop word.

    Returns True if word is stop word AND not a programming keyword.
    """
    word_lower = word.lower()
    return word_lower in ALL_STOP_WORDS and word_lower not in ALL_PROGRAMMING_KEYWORDS


def get_stop_words() -> Set[str]:
    """Get all stop words (for debugging/info)."""
    return ALL_STOP_WORDS.copy()


def get_programming_keywords() -> Set[str]:
    """Get all programming keywords (for debugging/info)."""
    return ALL_PROGRAMMING_KEYWORDS.copy()


def expand_query_terms(query_words: List[str]) -> List[str]:
    """Expand a list of query words with synonyms."""
    expanded = []

    for word in query_words:
        word_lower = word.lower()
        if word_lower in ALL_SYNONYMS:
            # Add original word
            expanded.append(word)
            # Add synonyms
            expanded.extend(ALL_SYNONYMS[word_lower])
        else:
            expanded.append(word)

    # Remove duplicates while preserving order
    seen = set()
    unique_expanded = []
    for term in expanded:
        if term not in seen:
            seen.add(term)
            unique_expanded.append(term)

    return unique_expanded
