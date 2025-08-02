"""
Consolidated Models for Context-AI Configuration.

This module contains all Pydantic models used for configuration management,
consolidating base models, AI configuration, storage configuration, and chunking configuration.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional

from pydantic import BaseModel, Field, validator

from .constants.ai import DEFAULT_SYSTEM_PROMPT_STRATEGY
from .constants.storage import (
    DEFAULT_CONFIG_DIR,
    DEFAULT_MAX_EMBEDDINGS,
    DEFAULT_CLEANUP_AFTER_DAYS,
)
from .constants.chunking import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_INCLUDE_METADATA,
    DEFAULT_MAX_CHUNKS,
    DEFAULT_MIN_CHUNK_SIZE,
    DEFAULT_PRIORITIZE_CROSS_PROJECT,
)

__all__ = [
    # Base Models
    'TimestampedModel',
    'ConfigurableModel',
    # AI Models
    'AIProviderConfig',
    'ContextAIConfig',
    # Storage Models
    'StorageConfig',
    'EmbeddingInfo',
    'ActiveEmbeddings',
    # Chunking Models
    'ChunkingConfig',
    'ContextAssemblyConfig',
]


# =============================================================================
# BASE MODELS
# =============================================================================

class TimestampedModel(BaseModel):
    """Base model with timestamp tracking."""
    
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    
    class Config:
        """Pydantic config for timestamped models."""
        json_encoders = {datetime: lambda v: v.isoformat()}


class ConfigurableModel(BaseModel):
    """Base model for configuration objects."""
    
    class Config:
        """Pydantic config for configuration models."""
        json_encoders = {datetime: lambda v: v.isoformat()}
        extra = "forbid"  # Prevent extra fields
        validate_assignment = True  # Validate on assignment


# =============================================================================
# AI MODELS
# =============================================================================

class AIProviderConfig(ConfigurableModel):
    """Configuration for AI providers."""

    api_key: str = Field(..., description="API key for the provider")
    default_model: str = Field(..., description="Default model to use")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens per request (resolved by business logic)")


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


# =============================================================================
# STORAGE MODELS
# =============================================================================

class StorageConfig(ConfigurableModel):
    """Configuration for storage."""

    base_path: str = Field(DEFAULT_CONFIG_DIR, description="Base storage directory")
    max_embeddings: int = Field(
        DEFAULT_MAX_EMBEDDINGS, description="Maximum number of embeddings to keep"
    )
    cleanup_after_days: int = Field(
        DEFAULT_CLEANUP_AFTER_DAYS, description="Clean up embeddings after N days"
    )


class EmbeddingInfo(TimestampedModel):
    """Information about an embedding."""

    name: str = Field(..., description="Embedding name")
    path: str = Field(..., description="Original path that was embedded")
    chunk_count: int = Field(..., description="Number of chunks")
    token_count: int = Field(..., description="Approximate token count")
    chunker: str = Field("langchain", description="Chunker used (langchain/treesitter)")


class ActiveEmbeddings(TimestampedModel):
    """Model for active embeddings tracking."""

    selected: List[str] = Field(
        default_factory=list, description="Selected embedding names"
    )
    last_updated: datetime = Field(
        default_factory=datetime.now, description="Last update timestamp"
    )


# =============================================================================
# CHUNKING MODELS
# =============================================================================

def _get_supported_extensions() -> set:
    """Get supported extensions dynamically from LanguagesManager."""
    from .languages.manager import get_languages_manager
    return get_languages_manager().get_supported_extensions()


class ChunkingConfig(ConfigurableModel):
    """Configuration for text chunking."""

    chunk_size: int = Field(
        DEFAULT_CHUNK_SIZE, description="Maximum chunk size in characters"
    )
    chunk_overlap: int = Field(
        DEFAULT_CHUNK_OVERLAP, description="Overlap between chunks"
    )
    min_chunk_size: int = Field(
        DEFAULT_MIN_CHUNK_SIZE, description="Minimum chunk size"
    )
    supported_extensions: List[str] = Field(
        default_factory=lambda: list(_get_supported_extensions()), 
        description="Supported file extensions"
    )


class ContextAssemblyConfig(ConfigurableModel):
    """Configuration for context assembly."""

    max_chunks: int = Field(
        DEFAULT_MAX_CHUNKS, description="Maximum chunks to include in context"
    )
    prioritize_cross_project: bool = Field(
        DEFAULT_PRIORITIZE_CROSS_PROJECT, description="Prioritize cross-project results"
    )
    include_metadata: bool = Field(
        DEFAULT_INCLUDE_METADATA, description="Include metadata in context"
    )
