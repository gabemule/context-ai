"""
Constants module for Context-AI.

This module re-exports all constants from domain-specific modules
to maintain backward compatibility while enabling modular imports.

Usage:
    # Backward compatible:
    from config.constants import DEFAULT_CHUNK_SIZE

    # New modular approach:
    from config.constants.chunking import DEFAULT_CHUNK_SIZE
"""

# Import all constants from domain-specific modules

# Aggregate all __all__ lists for complete re-export
from .ai import __all__ as ai_all
from .chunking import __all__ as chunking_all
from .storage import __all__ as storage_all
from .system import __all__ as system_all
from .validation import __all__ as validation_all

__all__ = ai_all + chunking_all + storage_all + system_all + validation_all
