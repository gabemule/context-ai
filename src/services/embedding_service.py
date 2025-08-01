"""
Embedding management service for Context-AI.

Handles business logic for embedding operations including
generation, selection, and management.
"""

from typing import Any, Dict, List, Optional

from config.constants import QUERY_POOL_SIZE, CONTEXT_DEFAULT_CHUNKS, CONTEXT_PERFORMANCE_LIMIT
from config.settings import get_settings_manager
from utils.error_handler import validate_embedding_name, validate_file_path
from utils.exceptions import ValidationError
from utils.logging import get_logger


class EmbeddingService:
    """Service for embedding-related operations."""

    def __init__(self):
        import time
        init_start_time = time.time()
        
        self.logger = get_logger(__name__)
        verbose = self.logger.isEnabledFor(10)  # DEBUG level = 10
        
        # Settings Manager
        self.settings_manager = get_settings_manager()
        
        # Model Manager (LAZY IMPORT - can be slow)
        if verbose:
            t2 = time.time()
        from core.embeddings.model_manager import get_model_manager
        self.model_manager = get_model_manager()
        if verbose:
            self.logger.info("⏱️  Model Manager: %.3fs", time.time() - t2)
        
        # Vector Store (LAZY IMPORT - ChromaDB connection)
        if verbose:
            t3 = time.time()
        from core.embeddings.vector_store import get_vector_store
        self.vector_store = get_vector_store()
        if verbose:
            self.logger.info("⏱️  Vector Store: %.3fs", time.time() - t3)
        
        # Chunker (LAZY IMPORT)
        from core.chunking import get_chunker
        self.chunker = get_chunker()
        
        if verbose:
            total_time = time.time() - init_start_time
            self.logger.info("✅ EmbeddingService ready in %.3fs", total_time)

    def generate_embedding(
        self, path: str, name: str, ignore_file: str = None, show_progress: bool = True
    ) -> Dict[str, Any]:
        """
        Generate embeddings for a project directory.

        Args:
            path: Path to the project directory
            name: Name for the embedding set
            ignore_file: Optional custom ignore file path
            show_progress: Whether to show progress tracking

        Returns:
            Dictionary with generation statistics

        Raises:
            ValidationError: If inputs are invalid
        """
        from pathlib import Path

        from utils.ignore_patterns import create_file_filter
        from utils.progress_tracker import create_embedding_progress_tracker

        # Validate inputs
        validate_file_path(path, must_exist=True, must_be_dir=True)
        validate_embedding_name(name)

        if ignore_file:
            validate_file_path(ignore_file, must_exist=True, must_be_dir=False)

        # Check if embedding already exists
        if self._embedding_exists(name):
            raise ValidationError(f"Embedding '{name}' already exists")

        project_path = Path(path)
        custom_ignore_path = Path(ignore_file) if ignore_file else None

        # Log operation start
        self.logger.info("🚀 Generating embeddings for: %s", path)
        self.logger.info("📛 Embedding name: %s", name)

        if ignore_file:
            self.logger.info("📋 Using custom ignore file: %s", ignore_file)
        else:
            self.logger.info(
                "📋 Using intelligent ignore file detection "
                "(.contextignore → .gitignore → defaults)"
            )

        # Get and filter files
        file_filter = create_file_filter(project_path, custom_ignore_path)
        all_files = [f for f in project_path.rglob("*") if f.is_file()]
        files_to_process, filter_stats = file_filter.filter_files(all_files)

        if not files_to_process:
            raise ValidationError("No supported files found to process")

        # Initialize progress tracking
        if show_progress:
            progress_tracker = create_embedding_progress_tracker(show_details=True)
            progress_tracker.start_embedding_generation(files_to_process, name)

        total_chunks = 0
        all_documents = []
        all_metadatas = []

        try:
            # Process files with actual chunking and embedding generation
            for file_path in files_to_process:
                try:
                    # Chunk the file
                    chunks = self.chunker.chunk_file(file_path)

                    if not chunks:
                        continue

                    # Extract texts and metadatas for embedding
                    for chunk in chunks:
                        all_documents.append(chunk.text)
                        all_metadatas.append(chunk.metadata)
                        total_chunks += 1

                    if show_progress:
                        progress_tracker.update_file_progress(file_path, len(chunks))

                except Exception as e:
                    if show_progress:
                        progress_tracker.update_error(file_path, str(e))
                    self.logger.error("Error processing %s: %s", file_path, e)
                    continue

            # Generate embeddings for all documents
            if all_documents:
                self.logger.info(
                    "🔄 Generating embeddings for %d chunks...", len(all_documents)
                )
                embeddings = self.model_manager.generate_embeddings(
                    all_documents, show_progress=show_progress
                )

                # Store in vector database
                self.logger.info("💾 Storing embeddings in vector database...")
                self.vector_store.store_embeddings(
                    embedding_name=name,
                    documents=all_documents,
                    embeddings=embeddings,
                    metadatas=all_metadatas,
                )

        finally:
            if show_progress:
                final_stats = progress_tracker.finish()
            else:
                final_stats = {
                    "files_processed": len(files_to_process),
                    "chunks_created": total_chunks,
                    "errors_count": 0,
                }

        self.logger.info(
            "✅ Embedding generation completed: %d chunks from %d files",
            final_stats.get("chunks_created", 0),
            final_stats.get("files_processed", 0),
        )

        return {
            **final_stats,
            "embedding_name": name,
            "source_path": path,
            "filter_stats": filter_stats,
        }

    def select_embeddings(self) -> List[str]:
        """
        Interactive selection of active embeddings.

        Returns:
            List of selected embedding names

        Raises:
            ValidationError: If no embeddings available or selection fails
        """
        from rich.console import Console

        console = Console()

        # Get available embeddings with loading
        with console.status(
            "[bold green]Loading available embeddings...", spinner="dots"
        ):
            available_embeddings_info = self.vector_store.list_embeddings()

        if not available_embeddings_info:
            raise ValidationError(
                "No embeddings found. Generate some first with 'context-ai generate'"
            )

        # Convert to display format
        available_embeddings = []
        for embedding in available_embeddings_info:
            name = embedding["name"]
            chunks = embedding["total_chunks"]
            files = embedding["unique_files"]
            created_at = embedding.get("created_at", "Unknown date")
            if created_at != "Unknown date":
                from datetime import datetime

                try:
                    date_obj = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    date_str = date_obj.strftime("%d %b %Y")
                except (ValueError, TypeError):
                    date_str = "Unknown date"
            else:
                date_str = created_at

            info = f"{chunks} chunks, {files} files, {date_str}"
            available_embeddings.append((name, info))

        # Get currently active embeddings for pre-selection
        current_active = self.settings_manager.get_active_embeddings()
        currently_selected = current_active.selected if current_active else []

        # Use inquirer for interactive selection
        try:
            import inquirer

            questions = [
                inquirer.Checkbox(
                    "selected_embeddings",
                    message=(
                        f"Select embeddings to query (currently active: "
                        f"{len(currently_selected)}) - Space: select/deselect, "
                        f"Enter: confirm"
                    ),
                    choices=[
                        (f"{name} ({info})", name)
                        for name, info in available_embeddings
                    ],
                    # Pre-select currently active embeddings
                    default=currently_selected,
                ),
            ]

            answers = inquirer.prompt(questions)

            if not answers or not answers["selected_embeddings"]:
                raise ValidationError("No embeddings selected")

            selected = answers["selected_embeddings"]

            # Save selection
            self.settings_manager.set_active_embeddings(selected)
            self.logger.info("✅ Selected embeddings: %s", ", ".join(selected))

            return selected

        except ImportError:
            raise ValidationError(
                "inquirer not installed. Install with: pip install inquirer"
            )

    def list_embeddings(self) -> List[str]:
        """
        Get list of available embeddings.

        Returns:
            List of embedding names
        """
        embeddings_info = self.vector_store.list_embeddings()
        return [embedding["name"] for embedding in embeddings_info]

    def delete_embedding(self, name: str) -> None:
        """
        Delete a specific embedding.

        Args:
            name: Name of embedding to delete

        Raises:
            ValidationError: If embedding doesn't exist
        """
        if not self._embedding_exists(name):
            raise ValidationError(f"Embedding '{name}' does not exist")

        success = self.vector_store.delete_embedding(name)
        if success:
            self.logger.info("✅ Embedding '%s' deleted successfully", name)
        else:
            raise ValidationError(f"Failed to delete embedding '{name}'")

    def _embedding_exists(self, name: str) -> bool:
        """Check if embedding exists."""
        info = self.vector_store.get_embedding_info(name)
        return info is not None


class QueryService:
    """Service for query operations."""

    def __init__(self):
        import time
        init_start_time = time.time()
        
        self.logger = get_logger(__name__)
        verbose = self.logger.isEnabledFor(10)  # DEBUG level = 10
        
        # Settings Manager
        self.settings_manager = get_settings_manager()
        
        # Vector Store (LAZY IMPORT - ChromaDB connection can be slow)
        if verbose:
            t2 = time.time()
        from core.embeddings.vector_store import get_vector_store
        self.vector_store = get_vector_store()
        if verbose:
            self.logger.info("⏱️  Vector Store: %.3fs", time.time() - t2)
        
        # Result Merger, Query Preprocessor, Context Formatter (LAZY IMPORTS)
        from core.query.result_merger import get_result_merger
        from core.query.preprocessor import get_query_preprocessor
        from core.formatting.context_formatter import get_context_formatter
        
        self.result_merger = get_result_merger()
        self.query_preprocessor = get_query_preprocessor()
        self.context_formatter = get_context_formatter()
        
        if verbose:
            total_time = time.time() - init_start_time
            self.logger.info("✅ QueryService ready in %.3fs", total_time)

    def query_context(
        self,
        question: str,
        format_type: str = "ai_friendly",
        max_results: Optional[int] = None,
        verbose: bool = False,
        max_context_tokens: Optional[int] = None,
    ) -> str:
        """
        Query embeddings for context.

        Args:
            question: Question to search for
            format_type: Output format ("ai_friendly", "plain", "markdown")
            max_results: Maximum number of results (uses default if None)
            verbose: Whether to show verbose logging
            max_context_tokens: Maximum tokens for context (uses default if None)

        Returns:
            Formatted context information

        Raises:
            ValidationError: If no active embeddings
        """
        # Preprocess query
        processed_query = self.query_preprocessor.preprocess_query(question)

        if not processed_query.is_valid:
            issues_str = "; ".join(processed_query.issues)
            raise ValidationError(f"Invalid query: {issues_str}")

        # Check active embeddings
        active = self.settings_manager.get_active_embeddings()
        if not active.selected:
            raise ValidationError(
                "No active embeddings selected. Use 'context-ai select' first"
            )

        # Verbose logging
        if verbose:
            self.logger.info("🔍 Original query: %s", processed_query.original)
            self.logger.info("🔧 Processed query: %s", processed_query.cleaned)
            if processed_query.expanded_terms:
                self.logger.info(
                    "📝 Expanded terms: %s", ", ".join(processed_query.expanded_terms)
                )
            self.logger.info("📊 Active embeddings: %s", ", ".join(active.selected))
            self.logger.info("🎯 Query strategy: Wide search (%d candidates) → Best selection", QUERY_POOL_SIZE)

        # Query vector database with preprocessed terms
        try:
            # Get search terms (original + expanded)
            search_terms = self.query_preprocessor.get_search_terms(processed_query)

            # Use the primary cleaned query for vector search
            # (we could also try multiple terms but that's more complex)
            query_text = search_terms[0] if search_terms else processed_query.cleaned

            # Query with wide search pool for better score normalization
            raw_results = self.vector_store.query_embeddings(
                query_texts=[query_text],
                embedding_names=active.selected,
                n_results=QUERY_POOL_SIZE,  # Get 1000 candidates for selection
            )

            # Use result merger for cross-embedding normalization
            normalized_results = self.result_merger.merge_multi_embedding_results(
                raw_results
            )

            if not normalized_results:
                return "No relevant context found."

            # Format results using the new context formatter
            display_results = (
                max_results if max_results is not None else CONTEXT_DEFAULT_CHUNKS
            )
            
            # Apply performance protection limit
            if display_results > CONTEXT_PERFORMANCE_LIMIT:
                display_results = CONTEXT_PERFORMANCE_LIMIT
                self.logger.warning(
                    "⚠️  Limited to %d chunks for performance (requested: %d)",
                    CONTEXT_PERFORMANCE_LIMIT,
                    max_results if max_results is not None else CONTEXT_DEFAULT_CHUNKS
                )
            formatted_context = self.context_formatter.format_context(
                normalized_results,
                query=processed_query.original,
                format_type=format_type,
                max_results=display_results,
                max_tokens=max_context_tokens,
            )

            # Add context statistics for debugging/verbose mode
            if verbose:
                stats = self.context_formatter.get_context_stats(formatted_context)
                stats_info = "\n## Context Statistics\n"
                stats_info += (
                    f"- Token count: {stats['token_count']} "
                    f"({stats['token_percentage']:.1f}% of limit)\n"
                )
                stats_info += (
                    f"- Chunks: {stats['chunk_count']} from "
                    f"{stats['source_count']} sources\n"
                )
                stats_info += f"- Sources: {', '.join(stats['sources'])}\n"
                if stats["truncated"]:
                    stats_info += "- ⚠️ Context was truncated due to token limit\n"

                return formatted_context.content + stats_info
            else:
                return formatted_context.content

        except Exception as e:
            self.logger.error("Query failed: %s", e)
            return f"Query failed: {e}"

    def query_context_json(
        self, question: str, max_results: Optional[int] = None
    ) -> str:
        """
        Query embeddings and return results in JSON format.

        Args:
            question: Question to search for
            max_results: Maximum number of results (uses default if None)

        Returns:
            JSON string with query results and metadata

        Raises:
            ValidationError: If no active embeddings
        """
        import json

        # Preprocess query
        processed_query = self.query_preprocessor.preprocess_query(question)

        if not processed_query.is_valid:
            issues_str = "; ".join(processed_query.issues)
            raise ValidationError(f"Invalid query: {issues_str}")

        # Check active embeddings
        active = self.settings_manager.get_active_embeddings()
        if not active.selected:
            raise ValidationError(
                "No active embeddings selected. Use 'context-ai select' first"
            )

        try:
            # Get search terms and query
            search_terms = self.query_preprocessor.get_search_terms(processed_query)
            query_text = search_terms[0] if search_terms else processed_query.cleaned

            # Query with wide search pool for better score normalization
            raw_results = self.vector_store.query_embeddings(
                query_texts=[query_text],
                embedding_names=active.selected,
                n_results=QUERY_POOL_SIZE,  # Get 1000 candidates for selection
            )

            # Use result merger for cross-embedding normalization
            normalized_results = self.result_merger.merge_multi_embedding_results(
                raw_results
            )

            if not normalized_results:
                return json.dumps(
                    {
                        "query": processed_query.original,
                        "results": [],
                        "metadata": {
                            "total_results": 0,
                            "active_embeddings": active.selected,
                            "processed_query": processed_query.cleaned,
                        },
                    },
                    indent=2,
                )

            # Limit results
            display_results = (
                max_results if max_results is not None else CONTEXT_DEFAULT_CHUNKS
            )
            
            # Apply performance protection limit
            if display_results > CONTEXT_PERFORMANCE_LIMIT:
                display_results = CONTEXT_PERFORMANCE_LIMIT
            limited_results = normalized_results[:display_results]

            # Convert to JSON-serializable format
            json_results = []
            for result in limited_results:
                json_results.append(
                    {
                        "text": result.text,
                        "score": result.final_score,
                        "similarity": result.normalized_score,
                        "source_embedding": result.source_embedding,
                        "metadata": result.metadata,
                    }
                )

            return json.dumps(
                {
                    "query": processed_query.original,
                    "results": json_results,
                    "metadata": {
                        "total_results": len(json_results),
                        "active_embeddings": active.selected,
                        "processed_query": processed_query.cleaned,
                        "expanded_terms": processed_query.expanded_terms,
                    },
                },
                indent=2,
            )

        except Exception as e:
            self.logger.error("JSON query failed: %s", e)
            return json.dumps(
                {"error": str(e), "query": processed_query.original}, indent=2
            )


class AIService:
    """Service for AI-powered operations."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.settings_manager = get_settings_manager()

    def ask_question(self, question: str) -> str:
        """
        Ask AI a question with context.

        Args:
            question: Question to ask

        Returns:
            AI response

        Raises:
            ValidationError: If configuration invalid
        """
        if not question.strip():
            raise ValidationError("Question cannot be empty")

        # Check AI configuration
        config = self.settings_manager.get_config()
        if not config.ai or config.active_provider not in config.ai:
            raise ValidationError(
                "AI provider not configured. Use "
                "'context-ai config set --claude-key YOUR_KEY'"
            )

        self.logger.info("❓ Asking: %s", question)

        # TODO: Implement actual AI integration
        self.logger.warning("⚠️  Ask command not yet implemented")
        return "AI response placeholder"

    def start_chat(self) -> None:
        """
        Start interactive chat session.

        Raises:
            ValidationError: If configuration invalid
        """
        # Check AI configuration
        config = self.settings_manager.get_config()
        if not config.ai or config.active_provider not in config.ai:
            raise ValidationError(
                "AI provider not configured. Use "
                "'context-ai config set --claude-key YOUR_KEY'"
            )

        self.logger.info("💬 Starting chat session...")

        # TODO: Implement actual chat
        self.logger.warning("⚠️  Chat command not yet implemented")
