"""
Chunking & Context Models for Context-AI.

This module contains Pydantic models related to text chunking
and context assembly configuration.
"""

from typing import List

from pydantic import Field

from .base import ConfigurableModel
from ..constants.chunking import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_MIN_CHUNK_SIZE,
    DEFAULT_MAX_CHUNKS,
    DEFAULT_PRIORITIZE_CROSS_PROJECT,
    DEFAULT_INCLUDE_METADATA,
    SUPPORTED_EXTENSIONS,
)

__all__ = [
    'ChunkingConfig',
    'ContextAssemblyConfig',
]


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
        default=list(SUPPORTED_EXTENSIONS), description="Supported file extensions"
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
