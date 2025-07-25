"""
Text chunking module for Context-AI.

Provides text chunking functionality with multiple implementation strategies.
"""

from typing import Optional
from .protocol import ChunkerProtocol, TextChunk, ChunkingStrategy, ChunkingMetadata
from .langchain_adapter import LangChainChunker


# Global chunker instance
_chunker_instance: Optional[ChunkerProtocol] = None


def get_chunker() -> ChunkerProtocol:
    """Get global chunker instance."""
    global _chunker_instance
    if _chunker_instance is None:
        _chunker_instance = LangChainChunker()
    return _chunker_instance


def set_chunker(chunker: ChunkerProtocol) -> None:
    """Set global chunker instance."""
    global _chunker_instance
    _chunker_instance = chunker


__all__ = [
    'ChunkerProtocol',
    'TextChunk', 
    'ChunkingStrategy',
    'ChunkingMetadata',
    'LangChainChunker',
    'get_chunker',
    'set_chunker'
]