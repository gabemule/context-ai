"""
LangChain adapter for text chunking in Context-AI.

This implements the ChunkerProtocol using langchain-text-splitters
for code-aware chunking across multiple programming languages.
"""

from pathlib import Path
from typing import List, Optional, Set

from langchain_text_splitters import (
    HTMLSemanticPreservingSplitter,
    JSFrameworkTextSplitter,
    MarkdownTextSplitter,
    PythonCodeTextSplitter,
    RecursiveCharacterTextSplitter,
)

from config.languages.manager import get_languages_manager
from utils.logging import get_logger

from .protocol import ChunkerProtocol, ChunkingMetadata, ChunkingStrategy, TextChunk


class LangChainChunker(ChunkerProtocol):
    """
    LangChain-based text chunker with language-aware splitting.

    Uses appropriate text splitters based on file type and language,
    providing better context preservation for code files.
    """

    def __init__(self, strategy: Optional[ChunkingStrategy] = None):
        """
        Initialize LangChain chunker.

        Args:
            strategy: Chunking configuration strategy
        """
        self.logger = get_logger(__name__)
        self.strategy = strategy or ChunkingStrategy()
        self.languages_manager = get_languages_manager()

    def chunk_text(self, text: str, file_path: str) -> List[TextChunk]:
        """
        Chunk text content using appropriate language-aware splitter.

        Args:
            text: The text content to chunk
            file_path: Path to the original file (for metadata)

        Returns:
            List of TextChunk objects
        """
        try:
            # Detect language from file extension
            file_ext = Path(file_path).suffix.lower()
            language = self.languages_manager.detect_language_from_extension(file_ext)

            # Get appropriate splitter
            splitter = self._get_splitter_for_language(language)

            # Split the text
            chunks = splitter.split_text(text)

            # Convert to TextChunk objects with metadata
            text_chunks = []
            for i, chunk_text in enumerate(chunks):
                # Skip chunks that are too small
                if len(chunk_text.strip()) < self.strategy.min_chunk_size:
                    continue

                metadata = ChunkingMetadata.create_base_metadata(
                    file_path=file_path,
                    chunk_index=i,
                    chunker_name=self.get_chunker_name(),
                    language=language or self._detect_language_from_content(chunk_text),
                )

                # Add additional metadata
                metadata.update(
                    {
                        ChunkingMetadata.CHUNK_TYPE: self._detect_chunk_type(
                            chunk_text, language
                        ),
                        ChunkingMetadata.TOKEN_COUNT: self._estimate_token_count(
                            chunk_text
                        ),
                        ChunkingMetadata.FILE_SIZE: len(text),
                    }
                )

                text_chunks.append(TextChunk(text=chunk_text, metadata=metadata))

            self.logger.debug(
                "Chunked %s into %d chunks (language: %s)",
                Path(file_path).name,
                len(text_chunks),
                language or "unknown",
            )

            return text_chunks

        except Exception as e:
            self.logger.error("Error chunking text from %s: %s", file_path, e)
            # Fallback to basic chunking
            return self._fallback_chunk(text, file_path)

    def chunk_file(self, file_path: Path) -> List[TextChunk]:
        """
        Chunk a file directly.

        Args:
            file_path: Path to the file to chunk

        Returns:
            List of TextChunk objects
        """
        try:
            # Read file content
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            return self.chunk_text(content, str(file_path))

        except Exception as e:
            self.logger.error("Error reading file %s: %s", file_path, e)
            return []

    def supports_extension(self, extension: str) -> bool:
        """
        Check if this chunker supports the given file extension.

        Args:
            extension: File extension (e.g., '.py', '.js')

        Returns:
            True if extension is supported
        """
        return extension.lower() in self.languages_manager.get_supported_extensions()

    def get_supported_extensions(self) -> Set[str]:
        """
        Get all supported file extensions.

        Returns:
            Set of supported extensions
        """
        return self.languages_manager.get_supported_extensions()

    def get_chunker_name(self) -> str:
        """
        Get the name of this chunker implementation.

        Returns:
            Chunker name
        """
        return "langchain"

    def _get_splitter_for_language(
        self, language: Optional[str]
    ) -> RecursiveCharacterTextSplitter:
        """
        Get appropriate text splitter for the given language.

        Args:
            language: Detected language

        Returns:
            Configured text splitter
        """
        chunk_size = self.strategy.chunk_size
        chunk_overlap = self.strategy.chunk_overlap

        try:
            # Use language-specific splitters when available
            if language == "python":
                return PythonCodeTextSplitter(
                    chunk_size=chunk_size, chunk_overlap=chunk_overlap
                )
            elif language == "javascript":
                return JSFrameworkTextSplitter(
                    chunk_size=chunk_size, chunk_overlap=chunk_overlap
                )
            elif language == "markdown":
                return MarkdownTextSplitter(
                    chunk_size=chunk_size, chunk_overlap=chunk_overlap
                )
            elif language == "html":
                return HTMLSemanticPreservingSplitter(
                    chunk_size=chunk_size, chunk_overlap=chunk_overlap
                )
            else:
                # Use recursive splitter with language-appropriate separators
                separators = self.languages_manager.get_language_separators(language or "default")
                return RecursiveCharacterTextSplitter(
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    separators=separators,
                    keep_separator=True,
                )

        except Exception as e:
            self.logger.error("Error creating language-specific splitter: %s", e)
            raise

    def _detect_language_from_content(self, content: str) -> str:
        """
        Detect programming language from content.

        Args:
            content: Text content to analyze

        Returns:
            Detected language string
        """
        # Simple heuristics for language detection
        content_lower = content.lower()

        if "def " in content or "import " in content or "class " in content:
            return "python"
        elif "function " in content or "const " in content or "let " in content:
            return "javascript"
        elif "interface " in content or "type " in content or ": string" in content:
            return "typescript"
        elif "<html" in content_lower or "<div" in content_lower:
            return "html"
        elif content.strip().startswith("#") or "##" in content:
            return "markdown"
        elif "{" in content and '"' in content:
            return "json"
        else:
            return "text"

    def _detect_chunk_type(self, chunk_text: str, language: Optional[str]) -> str:
        """
        Detect the type of code chunk.

        Args:
            chunk_text: The chunk content
            language: Programming language

        Returns:
            Chunk type (function, class, comment, etc.)
        """
        chunk_lower = chunk_text.lower().strip()

        # Code constructs
        if chunk_lower.startswith("class "):
            return "class"
        elif chunk_lower.startswith("def ") or chunk_lower.startswith("function "):
            return "function"
        elif chunk_lower.startswith("import ") or chunk_lower.startswith("from "):
            return "import"
        elif chunk_lower.startswith("interface ") or chunk_lower.startswith("type "):
            return "interface"
        elif (
            chunk_lower.startswith("#")
            or chunk_lower.startswith("//")
            or chunk_lower.startswith("/*")
        ):
            return "comment"
        elif chunk_lower.startswith("export "):
            return "export"
        else:
            return "code"

    def _estimate_token_count(self, text: str) -> int:
        """
        Estimate token count for text.

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        # Simple estimation: ~4 characters per token
        return len(text) // 4

    def _fallback_chunk(self, text: str, file_path: str) -> List[TextChunk]:
        """
        Fallback chunking method when language-specific chunking fails.

        Args:
            text: Text to chunk
            file_path: File path for metadata

        Returns:
            List of TextChunk objects
        """
        try:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.strategy.chunk_size,
                chunk_overlap=self.strategy.chunk_overlap,
            )

            chunks = splitter.split_text(text)
            text_chunks = []

            for i, chunk_text in enumerate(chunks):
                if len(chunk_text.strip()) >= self.strategy.min_chunk_size:
                    metadata = ChunkingMetadata.create_base_metadata(
                        file_path=file_path,
                        chunk_index=i,
                        chunker_name=self.get_chunker_name(),
                        language="unknown",
                    )

                    text_chunks.append(TextChunk(text=chunk_text, metadata=metadata))

            return text_chunks

        except Exception as e:
            self.logger.error("Fallback chunking failed for %s: %s", file_path, e)
            return []


def create_langchain_chunker(
    strategy: Optional[ChunkingStrategy] = None,
) -> LangChainChunker:
    """
    Factory function to create a LangChain chunker instance.

    Args:
        strategy: Optional chunking strategy configuration

    Returns:
        Configured LangChainChunker instance
    """
    return LangChainChunker(strategy)
