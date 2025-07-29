"""
Languages module for Context-AI.

This module provides dynamic language detection, configuration loading,
and management for programming languages, guidelines, and chunking separators.
"""

from .manager import LanguagesManager, get_languages_manager
from .models import LanguageConfig, LanguagesConfig

__all__ = [
    'LanguagesManager',
    'get_languages_manager',
    'LanguageConfig', 
    'LanguagesConfig',
]
