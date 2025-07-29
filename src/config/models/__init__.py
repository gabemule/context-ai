"""
Models module for Context-AI.

This module re-exports all Pydantic models from domain-specific modules
to maintain backward compatibility while enabling modular imports.

Usage:
    # Backward compatible:
    from config.models import ChunkingConfig
    
    # New modular approach:
    from config.models.chunking import ChunkingConfig
"""

# Import all models from domain-specific modules
from .base import *
from .ai import *
from .chunking import *
from .storage import *

# Aggregate all __all__ lists for complete re-export
from .base import __all__ as base_all
from .ai import __all__ as ai_all
from .chunking import __all__ as chunking_all
from .storage import __all__ as storage_all

__all__ = (
    base_all +
    ai_all +
    chunking_all +
    storage_all
)
