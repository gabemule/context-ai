"""
Query preprocessing for Context-AI.

Handles basic query normalization, validation, and enhancement
to improve search quality and relevance.
"""

import re
from typing import List, Dict, Any, Set
from dataclasses import dataclass

from utils.logging import get_logger
from .dictionary import (
    get_synonyms, has_synonyms, should_remove_word, 
    is_programming_keyword, expand_query_terms
)


# Query preprocessing constants
MIN_QUERY_LENGTH = 2
MAX_QUERY_LENGTH = 500
# All dictionaries are now loaded from separate language files
# This keeps the code clean and makes it easy to extend with new languages


@dataclass
class ProcessedQuery:
    """Processed query with metadata."""
    original: str
    normalized: str
    cleaned: str
    expanded_terms: List[str]
    is_valid: bool
    issues: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/debugging."""
        return {
            "original": self.original,
            "normalized": self.normalized,
            "cleaned": self.cleaned,
            "expanded_terms": self.expanded_terms,
            "is_valid": self.is_valid,
            "issues": self.issues
        }


class QueryPreprocessor:
    """
    Handles basic query preprocessing for improved search quality.
    
    Features:
    - Text normalization and cleaning
    - Basic validation
    - Query expansion with programming synonyms
    - Stop word handling
    """
    
    def __init__(self, 
                 remove_stop_words: bool = False,
                 expand_synonyms: bool = True,
                 min_length: int = MIN_QUERY_LENGTH,
                 max_length: int = MAX_QUERY_LENGTH):
        """
        Initialize query preprocessor.
        
        Args:
            remove_stop_words: Whether to remove common stop words
            expand_synonyms: Whether to expand programming synonyms
            min_length: Minimum valid query length
            max_length: Maximum valid query length
        """
        self.logger = get_logger(__name__)
        self.remove_stop_words = remove_stop_words
        self.expand_synonyms = expand_synonyms
        self.min_length = min_length
        self.max_length = max_length
    
    def preprocess_query(self, query: str) -> ProcessedQuery:
        """
        Preprocess a query for improved search.
        
        Args:
            query: Raw query string
            
        Returns:
            ProcessedQuery object with processed query and metadata
        """
        if not query:
            return ProcessedQuery(
                original="",
                normalized="",
                cleaned="",
                expanded_terms=[],
                is_valid=False,
                issues=["Query is empty"]
            )
        
        original = query
        issues = []
        
        # Step 1: Basic normalization
        normalized = self._normalize_text(query)
        
        # Step 2: Validation
        if len(normalized.strip()) < self.min_length:
            issues.append(f"Query too short (minimum {self.min_length} characters)")
        
        if len(normalized) > self.max_length:
            issues.append(f"Query too long (maximum {self.max_length} characters)")
            normalized = normalized[:self.max_length].strip()
        
        # Step 3: Clean the query
        cleaned = self._clean_query(normalized)
        
        # Step 4: Handle stop words (optional)
        if self.remove_stop_words:
            cleaned = self._remove_stop_words(cleaned)
        
        # Step 5: Expand synonyms (optional)
        expanded_terms = []
        if self.expand_synonyms:
            expanded_terms = self._expand_synonyms(cleaned)
        
        # Final validation
        is_valid = len(issues) == 0 and len(cleaned.strip()) >= self.min_length
        
        result = ProcessedQuery(
            original=original,
            normalized=normalized,
            cleaned=cleaned,
            expanded_terms=expanded_terms,
            is_valid=is_valid,
            issues=issues
        )
        
        self.logger.debug("Preprocessed query: %s", result.to_dict())
        return result
    
    def get_search_terms(self, processed_query: ProcessedQuery) -> List[str]:
        """
        Get final search terms for vector search.
        
        Args:
            processed_query: Processed query object
            
        Returns:
            List of search terms (original + expanded)
        """
        if not processed_query.is_valid:
            return []
        
        # Start with cleaned query
        search_terms = [processed_query.cleaned]
        
        # Add expanded terms if available
        if processed_query.expanded_terms:
            search_terms.extend(processed_query.expanded_terms)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_terms = []
        for term in search_terms:
            if term and term not in seen:
                seen.add(term)
                unique_terms.append(term)
        
        return unique_terms
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for processing."""
        # Strip whitespace
        text = text.strip()
        
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep programming-relevant ones
        text = re.sub(r'[^\w\s\-\._/(){}[\]<>]', ' ', text)
        
        # Clean up spaces again
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _clean_query(self, query: str) -> str:
        """Clean normalized query."""
        # Convert to lowercase for matching (but preserve original case for display)
        cleaned = query.lower()
        
        # Remove extra punctuation
        cleaned = re.sub(r'[^\w\s\-\._]', ' ', cleaned)
        
        # Clean up spaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def _remove_stop_words(self, query: str) -> str:
        """
        Remove stop words but preserve programming-important terms.
        
        Uses the multi-language dictionary system with smart preservation logic.
        """
        words = query.split()
        filtered_words = []
        
        for word in words:
            # Use the dictionary system to determine if word should be removed
            if not should_remove_word(word):
                filtered_words.append(word)
            # Otherwise skip the stop word
        
        # If we removed too many words, keep the original
        if len(filtered_words) == 0:
            return query
        
        return ' '.join(filtered_words)
    
    def _expand_synonyms(self, query: str) -> List[str]:
        """Expand programming synonyms for better matching using multi-language support."""
        words = query.lower().split()
        expanded_queries = []
        
        for word in words:
            if has_synonyms(word):
                synonyms = get_synonyms(word)
                # Create alternative queries with synonyms
                for synonym in synonyms:
                    # Replace the word with synonym in the original query
                    expanded_query = query.replace(word, synonym)
                    if expanded_query != query:  # Avoid duplicates
                        expanded_queries.append(expanded_query)
        
        return expanded_queries
    
    def validate_query(self, query: str) -> tuple[bool, List[str]]:
        """
        Quick validation of query without full preprocessing.
        
        Args:
            query: Raw query string
            
        Returns:
            Tuple of (is_valid, issues)
        """
        issues = []
        
        if not query or not query.strip():
            issues.append("Query cannot be empty")
            return False, issues
        
        normalized = self._normalize_text(query)
        
        if len(normalized) < self.min_length:
            issues.append(f"Query too short (minimum {self.min_length} characters)")
        
        if len(normalized) > self.max_length:
            issues.append(f"Query too long (maximum {self.max_length} characters)")
        
        return len(issues) == 0, issues


# Global preprocessor instance  
_query_preprocessor: QueryPreprocessor = None


def get_query_preprocessor() -> QueryPreprocessor:
    """Get global query preprocessor instance."""
    global _query_preprocessor
    if _query_preprocessor is None:
        _query_preprocessor = QueryPreprocessor()
    return _query_preprocessor


def preprocess_query(query: str) -> ProcessedQuery:
    """Convenience function to preprocess a query."""
    preprocessor = get_query_preprocessor()
    return preprocessor.preprocess_query(query)