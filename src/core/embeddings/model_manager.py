"""
Embedding model management for Context-AI.

Handles loading, caching, and management of sentence-transformer models
with intelligent caching and progress tracking for model downloads.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch
from sentence_transformers import SentenceTransformer

from utils.exceptions import ConfigurationError
from utils.logging import get_logger
from config.storage import get_storage_manager

# Model specifications
AVAILABLE_MODELS = {
    "all-MiniLM-L6-v2": {
        "name": "all-MiniLM-L6-v2",
        "dimensions": 384,
        "max_seq_length": 256,
        "size_mb": 90.0,
        "description": "Fast and efficient model, good for most use cases",
    },
    "all-mpnet-base-v2": {
        "name": "all-mpnet-base-v2",
        "dimensions": 768,
        "max_seq_length": 384,
        "size_mb": 420.0,
        "description": "Higher quality embeddings, slower processing",
    },
    "all-MiniLM-L12-v2": {
        "name": "all-MiniLM-L12-v2",
        "dimensions": 384,
        "max_seq_length": 256,
        "size_mb": 130.0,
        "description": "Balance between speed and quality",
    },
}

# Default model for MVP
DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"

# Default batch size for embedding generation
DEFAULT_BATCH_SIZE = 32

# Memory thresholds
LARGE_BATCH_THRESHOLD = 100


class ModelInfo:
    """Information about an embedding model."""

    def __init__(
        self,
        name: str,
        dimensions: int,
        max_seq_length: int,
        size_mb: float,
        description: str = "",
    ):
        self.name = name
        self.dimensions = dimensions
        self.max_seq_length = max_seq_length
        self.size_mb = size_mb
        self.description = description
        self.loaded_at: Optional[datetime] = None
        self.cache_path: Optional[Path] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "dimensions": self.dimensions,
            "max_seq_length": self.max_seq_length,
            "size_mb": self.size_mb,
            "description": self.description,
            "loaded_at": self.loaded_at.isoformat() if self.loaded_at else None,
            "cache_path": str(self.cache_path) if self.cache_path else None,
        }


class EmbeddingModelManager:
    """
    Manages embedding models with caching and automatic downloading.

    Provides model loading, caching, and batch processing capabilities
    for generating embeddings from text chunks.
    """

    def __init__(self):
        """Initialize model manager."""
        self.logger = get_logger(__name__)
        self.storage_manager = get_storage_manager()
        self._loaded_models: Dict[str, SentenceTransformer] = {}
        self._model_cache_dir = self.storage_manager.path_manager.models_dir

        # Ensure cache directory exists
        self._model_cache_dir.mkdir(parents=True, exist_ok=True)

    def get_available_models(self) -> Dict[str, ModelInfo]:
        """Get dictionary of available models."""
        models = {}
        for name, spec in AVAILABLE_MODELS.items():
            models[name] = ModelInfo(**spec)
        return models

    def get_model_info(self, model_name: str) -> ModelInfo:
        """
        Get information about a specific model.

        Args:
            model_name: Name of the model

        Returns:
            ModelInfo object

        Raises:
            ConfigurationError: If model is not available
        """
        if model_name not in AVAILABLE_MODELS:
            available = ", ".join(AVAILABLE_MODELS.keys())
            raise ConfigurationError(
                f"Model '{model_name}' not available. Available models: {available}"
            )

        return ModelInfo(**AVAILABLE_MODELS[model_name])

    def is_model_cached(self, model_name: str) -> bool:
        """
        Check if a model is cached locally.

        Args:
            model_name: Name of the model

        Returns:
            True if model is cached
        """
        cache_path = self._get_model_cache_path(model_name)
        return cache_path.exists() and cache_path.is_dir()

    def load_model(
        self, model_name: str = None, show_progress: bool = True
    ) -> SentenceTransformer:
        """
        Load an embedding model with caching.

        Args:
            model_name: Name of model to load (defaults to DEFAULT_MODEL_NAME)
            show_progress: Whether to show download progress

        Returns:
            Loaded SentenceTransformer model

        Raises:
            ConfigurationError: If model loading fails
        """
        import time
        load_start_time = time.time()
        
        if model_name is None:
            model_name = DEFAULT_MODEL_NAME

        verbose = self.logger.isEnabledFor(10)  # DEBUG level = 10
        
        # Check if model is already loaded
        if model_name in self._loaded_models:
            if verbose:
                self.logger.info("⚡ Using cached model: %s", model_name)
            else:
                self.logger.debug("Using already loaded model: %s", model_name)
            return self._loaded_models[model_name]

        # Get model info
        model_info = self.get_model_info(model_name)
        cache_path = self._get_model_cache_path(model_name)

        self.logger.info("🤖 Loading embedding model: %s", model_name)

        try:
            # Check if we need to download
            is_cached = self.is_model_cached(model_name)
            
            if not is_cached:
                if show_progress:
                    self._show_download_info(model_info)

                self.logger.info(
                    "📥 Downloading model (this may take a few minutes)..."
                )

            # Load model with visual loading indicator
            from rich.console import Console

            console = Console()

            if verbose:
                st_start_time = time.time()

            with console.status(
                f"[bold green]Loading model {model_name}...", spinner="dots"
            ):
                model = SentenceTransformer(
                    model_name, cache_folder=str(self._model_cache_dir)
                )

            if verbose:
                st_load_time = time.time() - st_start_time
                self.logger.info("⏱️  Model loading: %.3fs", st_load_time)

            # Cache the loaded model
            self._loaded_models[model_name] = model

            # Update model info
            model_info.loaded_at = datetime.now()
            model_info.cache_path = cache_path

            # Save model metadata
            self._save_model_metadata(model_name, model_info)

            total_load_time = time.time() - load_start_time
            if verbose:
                self.logger.info("✅ Model ready: %s (%d dimensions) in %.3fs", model_name, model_info.dimensions, total_load_time)
            else:
                self.logger.info("✅ Model loaded successfully: %s (%d dimensions)", model_name, model_info.dimensions)

            return model

        except Exception as e:
            total_load_time = time.time() - load_start_time
            if verbose:
                self.logger.error("❌ Model loading failed after %.3fs: %s", total_load_time, e)
            raise ConfigurationError(f"Failed to load model '{model_name}': {e}") from e

    def generate_embeddings(
        self,
        texts: List[str],
        model_name: str = None,
        batch_size: int = None,
        show_progress: bool = True,
    ) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of texts to embed
            model_name: Model to use (defaults to DEFAULT_MODEL_NAME)
            batch_size: Batch size for processing (defaults to DEFAULT_BATCH_SIZE)
            show_progress: Whether to show progress

        Returns:
            List of embedding vectors
        """
        if batch_size is None:
            batch_size = DEFAULT_BATCH_SIZE
        if not texts:
            return []

        # Load model
        model = self.load_model(model_name, show_progress=show_progress)

        self.logger.info("🔄 Generating embeddings for %d texts", len(texts))

        try:
            # Generate embeddings with progress tracking
            if show_progress and len(texts) > LARGE_BATCH_THRESHOLD:
                # For large batches, show progress
                embeddings = model.encode(
                    texts,
                    batch_size=batch_size,
                    show_progress_bar=True,
                    convert_to_numpy=True,
                )
            else:
                embeddings = model.encode(
                    texts,
                    batch_size=batch_size,
                    show_progress_bar=False,
                    convert_to_numpy=True,
                )

            # Convert to list of lists for JSON serialization
            result = embeddings.tolist()

            self.logger.info("✅ Generated %d embeddings", len(result))
            return result

        except Exception as e:
            self.logger.error("Error generating embeddings: %s", e)
            raise ConfigurationError(f"Failed to generate embeddings: {e}") from e

    def get_model_memory_usage(self, model_name: str) -> Optional[float]:
        """
        Get memory usage of a loaded model in MB.

        Args:
            model_name: Name of the model

        Returns:
            Memory usage in MB, or None if model not loaded
        """
        if model_name not in self._loaded_models:
            return None

        model = self._loaded_models[model_name]

        try:
            # Calculate model parameter size
            param_size = 0
            for param in model.parameters():
                param_size += param.nelement() * param.element_size()

            # Convert to MB
            return param_size / (1024 * 1024)

        except Exception as e:
            self.logger.warning("Could not calculate memory usage: %s", e)
            return None

    def unload_model(self, model_name: str) -> bool:
        """
        Unload a model from memory.

        Args:
            model_name: Name of model to unload

        Returns:
            True if model was unloaded
        """
        if model_name in self._loaded_models:
            del self._loaded_models[model_name]

            # Force garbage collection
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            self.logger.info("🗑️  Unloaded model: %s", model_name)
            return True

        return False

    def clear_cache(self, model_name: str = None) -> bool:
        """
        Clear model cache.

        Args:
            model_name: Specific model to clear, or None for all

        Returns:
            True if cache was cleared
        """
        try:
            if model_name:
                # Clear specific model
                cache_path = self._get_model_cache_path(model_name)
                if cache_path.exists():
                    import shutil

                    shutil.rmtree(cache_path)
                    self.logger.info("🧹 Cleared cache for model: %s", model_name)

                # Unload from memory if loaded
                self.unload_model(model_name)
                return True
            else:
                # Clear all models
                if self._model_cache_dir.exists():
                    import shutil

                    shutil.rmtree(self._model_cache_dir)
                    self._model_cache_dir.mkdir(parents=True, exist_ok=True)
                    self.logger.info("🧹 Cleared all model caches")

                # Unload all from memory
                self._loaded_models.clear()
                return True

        except Exception as e:
            self.logger.error("Error clearing cache: %s", e)
            return False

    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about cached models.

        Returns:
            Dictionary with cache information
        """
        cache_info = {
            "cache_directory": str(self._model_cache_dir),
            "loaded_models": list(self._loaded_models.keys()),
            "cached_models": [],
            "total_cache_size_mb": 0.0,
        }

        # Check cached models
        for model_name in AVAILABLE_MODELS:
            cache_path = self._get_model_cache_path(model_name)
            if cache_path.exists():
                try:
                    # Calculate cache size
                    size = sum(
                        f.stat().st_size for f in cache_path.rglob("*") if f.is_file()
                    )
                    size_mb = size / (1024 * 1024)

                    cache_info["cached_models"].append(
                        {
                            "name": model_name,
                            "path": str(cache_path),
                            "size_mb": round(size_mb, 1),
                        }
                    )

                    cache_info["total_cache_size_mb"] += size_mb

                except Exception as e:
                    self.logger.warning(
                        "Error calculating cache size for %s: %s", model_name, e
                    )

        cache_info["total_cache_size_mb"] = round(cache_info["total_cache_size_mb"], 1)
        return cache_info

    def _get_model_cache_path(self, model_name: str) -> Path:
        """Get cache path for a model."""
        safe_name = model_name.replace("/", "_").replace(":", "_")
        return self._model_cache_dir / safe_name

    def _show_download_info(self, model_info: ModelInfo) -> None:
        """Show information about model download."""
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table

        console = Console()

        table = Table(title=f"📥 Downloading Model: {model_info.name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="bold white")

        table.add_row("Model Size", f"~{model_info.size_mb:.0f} MB")
        table.add_row("Dimensions", str(model_info.dimensions))
        table.add_row("Max Sequence", str(model_info.max_seq_length))
        table.add_row("Description", model_info.description)
        table.add_row(
            "Cache Location", str(self._get_model_cache_path(model_info.name))
        )

        console.print(Panel(table, expand=False))
        console.print(
            "⏳ This is a one-time download. Future uses will be much faster!"
        )
        console.print()

    def _save_model_metadata(self, model_name: str, model_info: ModelInfo) -> None:
        """Save model metadata to cache."""
        try:
            metadata_file = self._get_model_cache_path(model_name) / "model_info.json"
            metadata_file.parent.mkdir(parents=True, exist_ok=True)

            with open(metadata_file, "w") as f:
                json.dump(model_info.to_dict(), f, indent=2)

        except Exception as e:
            self.logger.warning("Could not save model metadata: %s", e)


# Global model manager instance
_model_manager: Optional[EmbeddingModelManager] = None


def get_model_manager() -> EmbeddingModelManager:
    """Get global model manager instance."""
    global _model_manager
    if _model_manager is None:
        import time
        from utils.logging import get_logger
        
        logger = get_logger(__name__)
        verbose = logger.isEnabledFor(10)  # DEBUG level = 10
        
        if verbose:
            start_time = time.time()
            logger.info("🤖 Creating EmbeddingModelManager...")
        
        _model_manager = EmbeddingModelManager()
        
        if verbose:
            creation_time = time.time() - start_time
            logger.info("⏱️  EmbeddingModelManager creation: %.3fs", creation_time)
    
    return _model_manager


def create_embeddings(
    texts: List[str],
    model_name: str = None,
    batch_size: int = None,
    show_progress: bool = True,
) -> List[List[float]]:
    """
    Convenience function to create embeddings.

    Args:
        texts: List of texts to embed
        model_name: Model to use (defaults to DEFAULT_MODEL_NAME)
        batch_size: Batch size for processing (defaults to DEFAULT_BATCH_SIZE)
        show_progress: Whether to show progress

    Returns:
        List of embedding vectors
    """
    if batch_size is None:
        batch_size = DEFAULT_BATCH_SIZE
    manager = get_model_manager()
    return manager.generate_embeddings(texts, model_name, batch_size, show_progress)
