"""
Configuration module for Context-AI.

This module maintains backward compatibility while enabling modular imports
from the new organized structure.

Usage:
    # Backward compatible (still works):
    from config import DEFAULT_CHUNK_SIZE, ChunkingConfig, CLAUDE_MODELS
    
    # New modular approach (also works):
    from config.constants.chunking import DEFAULT_CHUNK_SIZE
    from config.models.chunking import ChunkingConfig  
    from config.providers.claude import CLAUDE_MODELS
"""

# Re-export everything from the new modular structure for backward compatibility
from .constants import *
from .models import *
from .providers import *
from .settings import *

# This maintains 100% backward compatibility:
# - All existing imports continue to work
# - New modular imports are also available
# - Zero breaking changes
