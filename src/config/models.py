"""
Configuration data models for Context-AI.
"""

from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel, Field

from .constants import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CLEANUP_AFTER_DAYS,
    DEFAULT_CONFIG_DIR,
    DEFAULT_INCLUDE_METADATA,
    DEFAULT_MAX_CHUNKS,
    DEFAULT_MAX_EMBEDDINGS,
    DEFAULT_MIN_CHUNK_SIZE,
    DEFAULT_PRIORITIZE_CROSS_PROJECT,
    DEFAULT_SYSTEM_PROMPT_STRATEGY,
    SUPPORTED_EXTENSIONS,
)
from .providers import get_max_tokens


class AIProviderConfig(BaseModel):
    """Configuration for AI providers."""

    api_key: str = Field(..., description="API key for the provider")
    default_model: str = Field(..., description="Default model to use")
    max_tokens: int = Field(get_max_tokens(), description="Maximum tokens per request")


class ChunkingConfig(BaseModel):
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
        default=list(SUPPORTED_EXTENSIONS), description="Supported file extensions"
    )


class ContextAssemblyConfig(BaseModel):
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


class StorageConfig(BaseModel):
    """Configuration for storage."""

    base_path: str = Field(DEFAULT_CONFIG_DIR, description="Base storage directory")
    max_embeddings: int = Field(
        DEFAULT_MAX_EMBEDDINGS, description="Maximum number of embeddings to keep"
    )
    cleanup_after_days: int = Field(
        DEFAULT_CLEANUP_AFTER_DAYS, description="Clean up embeddings after N days"
    )


class EmbeddingInfo(BaseModel):
    """Information about an embedding."""

    name: str = Field(..., description="Embedding name")
    path: str = Field(..., description="Original path that was embedded")
    created_at: datetime = Field(..., description="Creation timestamp")
    chunk_count: int = Field(..., description="Number of chunks")
    token_count: int = Field(..., description="Approximate token count")
    chunker: str = Field("langchain", description="Chunker used (langchain/treesitter)")


class ContextAIConfig(BaseModel):
    """Main configuration model."""

    storage: StorageConfig = Field(default_factory=StorageConfig)
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    context_assembly: ContextAssemblyConfig = Field(
        default_factory=ContextAssemblyConfig
    )
    ai: Dict[str, AIProviderConfig] = Field(default_factory=dict)
    active_provider: str = Field("claude", description="Active AI provider")
    active_embeddings: List[str] = Field(
        default_factory=list, description="Active embedding names"
    )
    system_prompt_strategy: str = Field(
        DEFAULT_SYSTEM_PROMPT_STRATEGY, description="System prompt strategy to use"
    )
    prompt_mode: str = Field("standard", description="Active prompt mode")

    class Config:
        """Pydantic config."""

        json_encoders = {datetime: lambda v: v.isoformat()}


class ActiveEmbeddings(BaseModel):
    """Model for active embeddings tracking."""

    selected: List[str] = Field(
        default_factory=list, description="Selected embedding names"
    )
    last_updated: datetime = Field(
        default_factory=datetime.now, description="Last update timestamp"
    )

    class Config:
        """Pydantic config."""

        json_encoders = {datetime: lambda v: v.isoformat()}
