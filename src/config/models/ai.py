"""
AI-Related Models for Context-AI.

This module contains Pydantic models related to AI provider configuration
and main application configuration.
"""

from datetime import datetime
from typing import Dict, List, Any

from pydantic import BaseModel, Field, validator

from .base import ConfigurableModel
from ..constants.ai import DEFAULT_SYSTEM_PROMPT_STRATEGY
from ..providers import get_max_tokens

__all__ = [
    'AIProviderConfig',
    'ContextAIConfig',
]


class AIProviderConfig(ConfigurableModel):
    """Configuration for AI providers."""

    api_key: str = Field(..., description="API key for the provider")
    default_model: str = Field(..., description="Default model to use")
    max_tokens: int = Field(get_max_tokens(), description="Maximum tokens per request")


class ContextAIConfig(BaseModel):
    """Main configuration model."""

    # Use Any but create proper objects at runtime
    storage: Any = Field(default_factory=dict, description="Storage configuration")
    chunking: Any = Field(default_factory=dict, description="Chunking configuration")  
    context_assembly: Any = Field(default_factory=dict, description="Context assembly configuration")
    ai: Dict[str, AIProviderConfig] = Field(default_factory=dict)
    active_provider: str = Field("claude", description="Active AI provider")
    active_embeddings: List[str] = Field(
        default_factory=list, description="Active embedding names"
    )
    system_prompt_strategy: str = Field(
        DEFAULT_SYSTEM_PROMPT_STRATEGY, description="System prompt strategy to use"
    )
    prompt_mode: str = Field("standard", description="Active prompt mode")

    def __init__(self, **kwargs):
        """Initialize with proper config objects."""
        # Import here to avoid circular dependencies
        from .storage import StorageConfig
        from .chunking import ChunkingConfig, ContextAssemblyConfig
        
        # Convert dicts to proper config objects if needed
        if 'storage' in kwargs and isinstance(kwargs['storage'], dict):
            kwargs['storage'] = StorageConfig(**kwargs['storage'])
        elif 'storage' not in kwargs:
            kwargs['storage'] = StorageConfig()
            
        if 'chunking' in kwargs and isinstance(kwargs['chunking'], dict):
            kwargs['chunking'] = ChunkingConfig(**kwargs['chunking'])
        elif 'chunking' not in kwargs:
            kwargs['chunking'] = ChunkingConfig()
            
        if 'context_assembly' in kwargs and isinstance(kwargs['context_assembly'], dict):
            kwargs['context_assembly'] = ContextAssemblyConfig(**kwargs['context_assembly'])
        elif 'context_assembly' not in kwargs:
            kwargs['context_assembly'] = ContextAssemblyConfig()
            
        super().__init__(**kwargs)

    class Config:
        """Pydantic config."""
        json_encoders = {datetime: lambda v: v.isoformat()}
        extra = "allow"  # Allow extra fields for backward compatibility
        arbitrary_types_allowed = True  # Allow custom types
