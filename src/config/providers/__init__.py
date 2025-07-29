"""
Providers module for Context-AI.

This module re-exports all AI provider configurations from domain-specific modules
to maintain backward compatibility while enabling modular imports.

Usage:
    # Backward compatible:
    from config.providers import CLAUDE_MODELS
    
    # New modular approach:
    from config.providers.claude import CLAUDE_MODELS
"""

# Import all providers from domain-specific modules
from .base import *
from .claude import *
from .registry import *

# Aggregate all __all__ lists for complete re-export
from .base import __all__ as base_all
from .claude import __all__ as claude_all
from .registry import __all__ as registry_all

__all__ = (
    base_all +
    claude_all +
    registry_all
)
