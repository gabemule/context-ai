"""
Text chunking protocol interface for Context-AI.

This defines the common interface that all chunkers must implement,
whether using LangChain, Tree-sitter, or other approaches.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Set
from pathlib import Path

from config.constants import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP, DEFAULT_MIN_CHUNK_SIZE


class TextChunk:
    """Represents a single text chunk with metadata."""
    
    def __init__(self, text: str, metadata: Dict[str, Any]):
        """
        Initialize a text chunk.
        
        Args:
            text: The chunk content
            metadata: Metadata about the chunk
        """
        self.text = text
        self.metadata = metadata
    
    def __repr__(self) -> str:
        return f"TextChunk(text={self.text[:50]}..., metadata={self.metadata})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary."""
        return {
            "text": self.text,
            "metadata": self.metadata
        }


class ChunkerProtocol(ABC):
    """
    Abstract base class for all text chunkers.
    
    This defines the interface that all chunking implementations must follow,
    ensuring consistency between LangChain, Tree-sitter, and future approaches.
    """
    
    @abstractmethod
    def chunk_text(self, text: str, file_path: str) -> List[TextChunk]:
        """
        Chunk text content into smaller pieces.
        
        Args:
            text: The text content to chunk
            file_path: Path to the original file (for metadata)
            
        Returns:
            List of TextChunk objects
        """
        pass
    
    @abstractmethod
    def chunk_file(self, file_path: Path) -> List[TextChunk]:
        """
        Chunk a file directly.
        
        Args:
            file_path: Path to the file to chunk
            
        Returns:
            List of TextChunk objects
        """
        pass
    
    @abstractmethod
    def supports_extension(self, extension: str) -> bool:
        """
        Check if this chunker supports the given file extension.
        
        Args:
            extension: File extension (e.g., '.py', '.js')
            
        Returns:
            True if extension is supported
        """
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> Set[str]:
        """
        Get all supported file extensions.
        
        Returns:
            Set of supported extensions
        """
        pass
    
    @abstractmethod
    def get_chunker_name(self) -> str:
        """
        Get the name of this chunker implementation.
        
        Returns:
            Chunker name (e.g., 'langchain', 'treesitter')
        """
        pass
    
    def chunk_directory(self, directory_path: Path, 
                       custom_ignore_file: Path = None,
                       show_progress: bool = True) -> List[TextChunk]:
        """
        Chunk all supported files in a directory using intelligent file filtering.
        
        Args:
            directory_path: Path to the directory
            custom_ignore_file: Optional custom ignore file path
            show_progress: Whether to show progress tracking
            
        Returns:
            List of TextChunk objects from all files
        """
        from utils.ignore_patterns import create_file_filter
        from utils.progress_tracker import create_file_processing_tracker
        
        # Create file filter with ignore patterns
        file_filter = create_file_filter(directory_path, custom_ignore_file)
        
        # Get all files in directory
        all_files = [f for f in directory_path.rglob('*') if f.is_file()]
        
        # Filter files with progress tracking
        if show_progress:
            file_tracker = create_file_processing_tracker()
            
            with file_tracker.track_file_filtering(len(all_files)) as update_progress:
                files_to_process, stats = file_filter.filter_files(all_files)
                update_progress(len(all_files))
            
            file_tracker.show_filtering_results(stats)
        else:
            files_to_process, stats = file_filter.filter_files(all_files)
        
        # Process filtered files
        chunks = []
        for file_path in files_to_process:
            try:
                file_chunks = self.chunk_file(file_path)
                chunks.extend(file_chunks)
            except Exception as e:
                # Log error but continue processing other files
                from utils.logging import get_logger
                logger = get_logger(__name__)
                logger.warning("⚠️  Failed to chunk %s: %s", file_path, e)
                continue
        
        return chunks


class ChunkingStrategy:
    """Configuration for chunking behavior."""
    
    def __init__(self, 
                 chunk_size: int = DEFAULT_CHUNK_SIZE,
                 chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
                 preserve_structure: bool = True,
                 include_imports: bool = True,
                 min_chunk_size: int = DEFAULT_MIN_CHUNK_SIZE):
        """
        Initialize chunking strategy.
        
        Args:
            chunk_size: Target size for chunks in characters
            chunk_overlap: Overlap between consecutive chunks
            preserve_structure: Try to preserve code/document structure
            include_imports: Include import statements in chunks
            min_chunk_size: Minimum size for a chunk to be valid
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.preserve_structure = preserve_structure
        self.include_imports = include_imports
        self.min_chunk_size = min_chunk_size
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert strategy to dictionary."""
        return {
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "preserve_structure": self.preserve_structure,
            "include_imports": self.include_imports,
            "min_chunk_size": self.min_chunk_size
        }


class ChunkingMetadata:
    """Standard metadata fields for chunks."""
    
    # Required fields
    FILE_PATH = "file_path"
    CHUNK_INDEX = "chunk_index"
    CHUNKER_NAME = "chunker"
    LANGUAGE = "language"
    
    # Optional fields
    START_LINE = "start_line"
    END_LINE = "end_line"
    FUNCTION_NAME = "function_name"
    CLASS_NAME = "class_name"
    CHUNK_TYPE = "chunk_type"  # e.g., "function", "class", "comment", "import"
    TOKEN_COUNT = "token_count"
    
    # File metadata
    FILE_SIZE = "file_size"
    FILE_MODIFIED = "file_modified"
    
    @classmethod
    def create_base_metadata(cls, file_path: str, chunk_index: int, 
                           chunker_name: str, language: str = None) -> Dict[str, Any]:
        """
        Create base metadata dictionary with required fields.
        
        Args:
            file_path: Path to the source file
            chunk_index: Index of this chunk in the file
            chunker_name: Name of the chunker that created this chunk
            language: Programming language (auto-detected if None)
            
        Returns:
            Dictionary with base metadata
        """
        metadata = {
            cls.FILE_PATH: file_path,
            cls.CHUNK_INDEX: chunk_index,
            cls.CHUNKER_NAME: chunker_name,
        }
        
        if language:
            metadata[cls.LANGUAGE] = language
        
        return metadata