"""
Languages module for Context-AI.

This module provides dynamic language detection, configuration loading,
and management for programming languages, guidelines, and chunking separators.
"""

from .registry import LanguagesRegistry, get_languages_registry
from .models import LanguageConfig, LanguagesConfig

__all__ = [
    'LanguagesRegistry',
    'get_languages_registry',
    'LanguageConfig', 
    'LanguagesConfig',
]
