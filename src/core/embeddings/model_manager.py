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


# =============================================================================
# CORE ABSTRACTIONS (SOLID: Dependency Inversion Principle)
# =============================================================================

from abc import ABC, abstractmethod

class ModelCacheInterface(ABC):
    """Interface for model caching operations (ISP)."""
    
    @abstractmethod
    def is_cached(self, model_name: str) -> bool:
        """Check if model is cached."""
        pass
    
    @abstractmethod
    def get_cached_model(self, model_name: str) -> Optional[SentenceTransformer]:
        """Get cached model if available."""
        pass
    
    @abstractmethod
    def cache_model(self, model_name: str, model: SentenceTransformer) -> None:
        """Cache a loaded model."""
        pass


class ModelLoaderInterface(ABC):
    """Interface for model loading operations (ISP)."""
    
    @abstractmethod
    def load_model(self, model_name: str, show_progress: bool) -> SentenceTransformer:
        """Load a model."""
        pass


# =============================================================================
# SINGLE RESPONSIBILITY CLASSES (SOLID: SRP)
# =============================================================================

class ModelValidator:
    """Validates model operations (SRP)."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def validate_model_name(self, model_name: str) -> str:
        """Validate and normalize model name."""
        if model_name is None:
            return DEFAULT_MODEL_NAME
        
        if model_name not in AVAILABLE_MODELS:
            available = ", ".join(AVAILABLE_MODELS.keys())
            raise ConfigurationError(
                f"Model '{model_name}' not available. Available models: {available}"
            )
        
        return model_name
    
    def validate_texts(self, texts: List[str]) -> None:
        """Validate texts for embedding generation."""
        if not texts:
            raise ValueError("No texts provided for embedding generation")


class ModelCache(ModelCacheInterface):
    """Handles model caching operations (SRP)."""
    
    def __init__(self, cache_dir: Path):
        self.logger = get_logger(__name__)
        self.cache_dir = cache_dir
        self._memory_cache: Dict[str, SentenceTransformer] = {}
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def is_cached(self, model_name: str) -> bool:
        """Check if model is cached in memory or disk."""
        return self._is_memory_cached(model_name) or self._is_disk_cached(model_name)
    
    def get_cached_model(self, model_name: str) -> Optional[SentenceTransformer]:
        """Get cached model (memory first, then disk)."""
        if self._is_memory_cached(model_name):
            self.logger.debug("⚡ Using memory cached model: %s", model_name)
            return self._memory_cache[model_name]
        
        return None
    
    def cache_model(self, model_name: str, model: SentenceTransformer) -> None:
        """Cache model in memory."""
        self._memory_cache[model_name] = model
        self.logger.debug("💾 Cached model in memory: %s", model_name)
    
    def _is_memory_cached(self, model_name: str) -> bool:
        """Check if model is in memory cache."""
        return model_name in self._memory_cache
    
    def _is_disk_cached(self, model_name: str) -> bool:
        """Check if model is cached on disk."""
        cache_path = self._get_cache_path(model_name)
        return cache_path.exists() and cache_path.is_dir()
    
    def _get_cache_path(self, model_name: str) -> Path:
        """Get cache path for a model."""
        safe_name = model_name.replace("/", "_").replace(":", "_")
        return self.cache_dir / safe_name


class ModelLoader(ModelLoaderInterface):
    """Handles model loading operations (SRP)."""
    
    def __init__(self, cache_dir: Path):
        self.logger = get_logger(__name__)
        self.cache_dir = cache_dir
    
    def load_model(self, model_name: str, show_progress: bool) -> SentenceTransformer:
        """Load model with optimized performance."""
        is_cached = self._is_disk_cached(model_name)
        
        if not is_cached and show_progress:
            self._show_download_info(model_name)
        
        return self._load_sentence_transformer(model_name, is_cached)
    
    def _load_sentence_transformer(self, model_name: str, is_cached: bool) -> SentenceTransformer:
        """Load SentenceTransformer with minimal overhead."""
        self.logger.info("🤖 Loading embedding model: %s", model_name)
        
        if is_cached:
            # Fast path - direct loading
            return SentenceTransformer(model_name, cache_folder=str(self.cache_dir))
        else:
            # Show progress for downloads
            return self._load_with_progress(model_name)
    
    def _load_with_progress(self, model_name: str) -> SentenceTransformer:
        """Load model with progress indicator."""
        from rich.console import Console
        console = Console()
        
        with console.status(f"[bold green]Loading {model_name}...", spinner="dots"):
            return SentenceTransformer(model_name, cache_folder=str(self.cache_dir))
    
    def _is_disk_cached(self, model_name: str) -> bool:
        """Check if model is cached on disk."""
        cache_path = self._get_cache_path(model_name)
        return cache_path.exists() and cache_path.is_dir()
    
    def _get_cache_path(self, model_name: str) -> Path:
        """Get cache path for a model."""
        safe_name = model_name.replace("/", "_").replace(":", "_")
        return self.cache_dir / safe_name
    
    def _show_download_info(self, model_name: str) -> None:
        """Show download information for first-time downloads."""
        if model_name not in AVAILABLE_MODELS:
            return
        
        model_info = AVAILABLE_MODELS[model_name]
        self.logger.info("📥 Downloading model %s (~%.0f MB)...", model_name, model_info["size_mb"])


class EmbeddingGenerator:
    """Handles embedding generation (SRP)."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def generate_embeddings(
        self, 
        model: SentenceTransformer, 
        texts: List[str], 
        batch_size: int = DEFAULT_BATCH_SIZE,
        show_progress: bool = True
    ) -> List[List[float]]:
        """Generate embeddings using provided model."""
        self.logger.info("🔄 Generating embeddings for %d texts", len(texts))
        
        try:
            embeddings = self._encode_texts(model, texts, batch_size, show_progress)
            result = embeddings.tolist()
            
            self.logger.info("✅ Generated %d embeddings", len(result))
            return result
            
        except Exception as e:
            self.logger.error("Error generating embeddings: %s", e)
            raise ConfigurationError(f"Failed to generate embeddings: {e}") from e
    
    def _encode_texts(self, model: SentenceTransformer, texts: List[str], 
                     batch_size: int, show_progress: bool):
        """Encode texts with appropriate progress tracking."""
        if show_progress and len(texts) > LARGE_BATCH_THRESHOLD:
            return model.encode(
                texts, batch_size=batch_size, 
                show_progress_bar=True, convert_to_numpy=True
            )
        else:
            return model.encode(
                texts, batch_size=batch_size, 
                show_progress_bar=False, convert_to_numpy=True
            )


class EmbeddingModelManager:
    """
    Orchestrates embedding model operations (Clean Architecture).
    
    Follows SOLID principles with dependency injection and single responsibilities.
    """

    def __init__(self):
        """Initialize manager with dependency injection."""
        self.logger = get_logger(__name__)
        self.storage_manager = get_storage_manager()
        self._model_cache_dir = self.storage_manager.path_manager.models_dir
        
        # Dependency Injection (SOLID: DIP)
        self.validator = ModelValidator()
        self.cache = ModelCache(self._model_cache_dir)
        self.loader = ModelLoader(self._model_cache_dir)
        self.generator = EmbeddingGenerator()

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
        # ✅ SOLID: Delegate to cache (SRP)
        return self.cache.is_cached(model_name)

    def load_model(
        self, model_name: str = None, show_progress: bool = True
    ) -> SentenceTransformer:
        """
        Load an embedding model with SOLID architecture (Performance Optimized).

        Args:
            model_name: Name of model to load (defaults to DEFAULT_MODEL_NAME)
            show_progress: Whether to show download progress

        Returns:
            Loaded SentenceTransformer model

        Raises:
            ConfigurationError: If model loading fails
        """
        # ✅ SOLID: Use validator to validate and normalize model name
        model_name = self.validator.validate_model_name(model_name)

        # ✅ SOLID: Check cache first (SRP)
        cached_model = self.cache.get_cached_model(model_name)
        if cached_model is not None:
            return cached_model

        # ✅ SOLID: Use loader to load model (SRP)
        model = self.loader.load_model(model_name, show_progress)
        
        # ✅ SOLID: Cache the loaded model (SRP)
        self.cache.cache_model(model_name, model)
        
        # ✅ Log success
        model_info = AVAILABLE_MODELS[model_name]
        self.logger.info("✅ Model loaded successfully: %s (%d dimensions)", 
                        model_name, model_info["dimensions"])
        
        return model

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
        # ✅ SOLID: Validate inputs (SRP)
        self.validator.validate_texts(texts)
        if batch_size is None:
            batch_size = DEFAULT_BATCH_SIZE

        # ✅ SOLID: Load model (SRP)
        model = self.load_model(model_name, show_progress=show_progress)

        # ✅ SOLID: Generate embeddings (SRP)
        return self.generator.generate_embeddings(model, texts, batch_size, show_progress)

    def get_model_memory_usage(self, model_name: str) -> Optional[float]:
        """
        Get memory usage of a loaded model in MB.

        Args:
            model_name: Name of the model

        Returns:
            Memory usage in MB, or None if model not loaded
        """
        # ✅ SOLID: Delegate to cache (SRP)
        model = self.cache.get_cached_model(model_name)
        if model is None:
            return None

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

    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cached models."""
        cache_info = {
            "cache_directory": str(self._model_cache_dir),
            "loaded_models": list(self.cache._memory_cache.keys()),
            "cached_models": [],
            "total_cache_size_mb": 0.0,
        }

        # Check disk cache for each available model
        for model_name in AVAILABLE_MODELS:
            if self.cache._is_disk_cached(model_name):
                cache_path = self.cache._get_cache_path(model_name)
                try:
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
