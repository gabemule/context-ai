"""
Storage & Embedding Models for Context-AI.

This module contains Pydantic models related to storage configuration
and embedding information tracking.
"""

from datetime import datetime
from typing import List

from pydantic import Field

from .base import ConfigurableModel, TimestampedModel
from ..constants.storage import (
    DEFAULT_CONFIG_DIR,
    DEFAULT_MAX_EMBEDDINGS,
    DEFAULT_CLEANUP_AFTER_DAYS,
)

__all__ = [
    'StorageConfig',
    'EmbeddingInfo',
    'ActiveEmbeddings',
]


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
