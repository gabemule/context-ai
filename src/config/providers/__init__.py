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
from .protocols import *
from .models import *
from .claude import *
from .registry import *

# Aggregate all __all__ lists for complete re-export
from .protocols import __all__ as protocols_all
from .models import __all__ as models_all
from .claude import __all__ as claude_all
from .registry import __all__ as registry_all

__all__ = (
    protocols_all +
    models_all +
    claude_all +
    registry_all
)
