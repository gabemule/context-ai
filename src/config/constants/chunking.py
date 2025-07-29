"""
Text Processing & Chunking Constants for Context-AI.

This module contains constants related to text chunking configuration only.
Language-specific data is now handled by the LanguagesManager system.
"""

__all__ = [
    'DEFAULT_CHUNK_SIZE',
    'DEFAULT_CHUNK_OVERLAP',
    'DEFAULT_MIN_CHUNK_SIZE',
    'DEFAULT_MAX_CHUNKS',
    'DEFAULT_PRIORITIZE_CROSS_PROJECT',
    'DEFAULT_INCLUDE_METADATA',
]

# Chunking defaults
DEFAULT_CHUNK_SIZE = 2000
DEFAULT_CHUNK_OVERLAP = 200
DEFAULT_MIN_CHUNK_SIZE = 50

# Context assembly defaults
DEFAULT_MAX_CHUNKS = 8
DEFAULT_PRIORITIZE_CROSS_PROJECT = True
DEFAULT_INCLUDE_METADATA = True
