"""
Storage management utilities for Context-AI.

Clean Architecture approach with separated responsibilities.
"""

import os
import shutil
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Protocol

from config.constants import DEFAULT_CONFIG_DIR
from utils.exceptions import StorageError
from utils.logging import get_logger


# =============================================================================
# CONSTANTS (DRY principle)
# =============================================================================

CLEANUP_METADATA_FILE = ".last_cleanup"
DEFAULT_TEMP_CLEANUP_HOURS = 24
DEFAULT_MODEL_UNUSED_DAYS = 30
DEFAULT_LOG_RETENTION_DAYS = 30

STORAGE_DIRECTORIES = [
    "embeddings",
    "models",
    "logs",
    "temp"
]

LOG_TYPE_PATTERNS = {
    "ask": "ask",
    "chat": "chat", 
    "query": "query",
    "general": ""
}


# =============================================================================
# PROTOCOLS (Interface Segregation Principle)
# =============================================================================

class StoragePathProvider(Protocol):
    """Protocol for storage path management."""
    
    def get_embedding_path(self, embedding_name: str) -> Path: ...
    def get_model_cache_path(self, model_name: str) -> Path: ...
    def get_log_file_path(self, log_name: str) -> Path: ...
    def get_temp_file_path(self, filename: str) -> Path: ...


class StorageAnalyticsProvider(Protocol):
    """Protocol for storage analytics."""
    
    def get_embeddings_analytics(self) -> Dict: ...
    def get_log_analytics(self) -> Dict: ...
    def get_models_analytics(self) -> Dict: ...


class StorageCleanerProvider(Protocol):
    """Protocol for storage cleaning operations."""
    
    def clean_by_age(self, older_than_days: int) -> int: ...
    def clean_all(self) -> int: ...


# =============================================================================
# PATH MANAGER (Single Responsibility Principle)
# =============================================================================

class StoragePathManager:
    """Manages storage paths and directory structure (SRP)."""
    
    def __init__(self, base_path: Optional[str] = None):
        self.logger = get_logger(__name__)
        self.base_path = self._resolve_base_path(base_path)
        self._setup_directory_paths()
    
    def _resolve_base_path(self, base_path: Optional[str]) -> Path:
        """Resolve base storage path."""
        if base_path:
            return Path(base_path).expanduser().resolve()
        return Path(DEFAULT_CONFIG_DIR).expanduser().resolve()
    
    def _setup_directory_paths(self) -> None:
        """Setup directory path attributes."""
        self.config_file = self.base_path / "config.json"
        self.active_file = self.base_path / "active.json"
        self.embeddings_dir = self.base_path / "embeddings"
        self.chromadb_dir = self.embeddings_dir / "chromadb"
        self.models_dir = self.base_path / "models"
        self.logs_dir = self.base_path / "logs"
        self.temp_dir = self.base_path / "temp"
    
    def ensure_storage_structure(self) -> None:
        """Ensure all storage directories exist."""
        try:
            directories = [
                self.base_path,
                self.embeddings_dir,
                self.chromadb_dir,
                self.models_dir,
                self.logs_dir,
                self.temp_dir,
            ]

            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                self.logger.debug("Ensured directory exists: %s", directory)

        except Exception as e:
            raise StorageError(f"Failed to create storage structure: {e}")
    
    def get_embedding_path(self, embedding_name: str) -> Path:
        """Get path for embedding data."""
        return self.chromadb_dir / f"{embedding_name}.db"

    def get_model_cache_path(self, model_name: str) -> Path:
        """Get path for cached model."""
        safe_name = model_name.replace("/", "_").replace(":", "_")
        return self.models_dir / safe_name

    def get_log_file_path(self, log_name: str = "context-ai.log") -> Path:
        """Get path for log file."""
        return self.logs_dir / log_name

    def get_temp_file_path(self, filename: str) -> Path:
        """Get path for temporary file."""
        return self.temp_dir / filename

    def get_directory_sizes(self) -> Dict[str, int]:
        """Get sizes of all storage directories."""
        dir_sizes = {}
        
        for dir_name in STORAGE_DIRECTORIES:
            dir_path = getattr(self, f"{dir_name}_dir")
            if dir_path.exists():
                size = sum(f.stat().st_size for f in dir_path.rglob("*") if f.is_file())
                dir_sizes[dir_name] = size
            else:
                dir_sizes[dir_name] = 0
        
        return dir_sizes


# =============================================================================
# ANALYTICS PROVIDERS (Single Responsibility Principle)
# =============================================================================

class EmbeddingsAnalytics:
    """Handles embeddings analytics (SRP)."""
    
    def __init__(self, path_manager: StoragePathManager):
        self.path_manager = path_manager
        self.logger = get_logger(__name__)
    
    def get_analytics(self) -> Dict:
        """Get detailed embeddings analytics."""
        try:
            from core.embeddings.vector_store import get_vector_store

            vector_store = get_vector_store()
            embeddings_info = vector_store.list_embeddings()

            if not embeddings_info:
                return self._empty_analytics()

            return self._analyze_embeddings_info(embeddings_info)

        except Exception as e:
            self.logger.warning("Error getting embeddings analytics: %s", e)
            return self._empty_analytics()
    
    def _empty_analytics(self) -> Dict:
        """Return empty analytics structure."""
        return {"oldest": None, "newest": None, "sizes": {}}
    
    def _analyze_embeddings_info(self, embeddings_info: List[Dict]) -> Dict:
        """Analyze embeddings information."""
        # Sort by creation time (handle missing created field)
        def get_created_time(x):
            created = x.get("created_at")
            if created:
                try:
                    from datetime import datetime
                    return datetime.fromisoformat(created.replace('Z', '+00:00')).timestamp()
                except:
                    return 0
            return 0
        
        embeddings_by_time = sorted(embeddings_info, key=get_created_time)
        
        oldest = embeddings_by_time[0] if embeddings_by_time else None
        newest = embeddings_by_time[-1] if embeddings_by_time else None

        # Individual sizes (convert from bytes to MB)
        sizes = {}
        for info in embeddings_info:
            size_bytes = info.get("total_size_bytes", 0)
            size_mb = round(size_bytes / (1024 * 1024), 2) if size_bytes > 0 else 0
            sizes[info["name"]] = size_mb

        return {
            "oldest": oldest["name"] if oldest else None,
            "oldest_date": self._format_created_at(oldest.get("created_at")) if oldest else None,
            "newest": newest["name"] if newest else None,
            "newest_date": self._format_created_at(newest.get("created_at")) if newest else None,
            "sizes": sizes,
        }
    
    def _format_timestamp(self, timestamp: float) -> str:
        """Format timestamp to readable date."""
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
    
    def _format_created_at(self, created_at: str) -> str:
        """Format created_at string to readable date."""
        if not created_at:
            return "unknown"
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d")
        except:
            return "unknown"


class LogAnalytics:
    """Handles log analytics (SRP)."""
    
    def __init__(self, path_manager: StoragePathManager):
        self.path_manager = path_manager
        self.logger = get_logger(__name__)
    
    def get_analytics(self) -> Dict:
        """Get detailed log analytics."""
        try:
            if not self.path_manager.logs_dir.exists():
                return self._empty_analytics()

            # Session logs are stored in directories, not .log files
            session_dirs = [d for d in self.path_manager.logs_dir.iterdir() if d.is_dir()]
            if not session_dirs:
                return self._empty_analytics()

            return self._analyze_session_dirs(session_dirs)

        except Exception as e:
            self.logger.warning("Error getting log analytics: %s", e)
            return self._empty_analytics()
    
    def _empty_analytics(self) -> Dict:
        """Return empty analytics structure."""
        return {"count": 0, "oldest": None, "types": {}}
    
    def _analyze_session_dirs(self, session_dirs: List[Path]) -> Dict:
        """Analyze session directories."""
        # Sort by modification time
        sessions_by_time = sorted(session_dirs, key=lambda x: x.stat().st_mtime)
        oldest_session = sessions_by_time[0] if sessions_by_time else None

        # Count by type based on directory names
        types = self._count_session_types(session_dirs)

        return {
            "count": len(session_dirs),
            "oldest": oldest_session.name if oldest_session else None,
            "oldest_date": self._format_file_time(oldest_session) if oldest_session else None,
            "types": types,
            "recent_sessions": [d.name for d in sessions_by_time[-5:]] if sessions_by_time else [],
        }
    
    def _count_session_types(self, session_dirs: List[Path]) -> Dict[str, int]:
        """Count sessions by type based on directory name patterns."""
        types = {log_type: 0 for log_type in LOG_TYPE_PATTERNS.keys()}
        
        for session_dir in session_dirs:
            name = session_dir.name.lower()
            categorized = False
            
            for log_type, pattern in LOG_TYPE_PATTERNS.items():
                if pattern and pattern in name:
                    types[log_type] += 1
                    categorized = True
                    break
            
            if not categorized:
                types["general"] += 1
        
        return types
    
    def _count_log_types(self, log_files: List[Path]) -> Dict[str, int]:
        """Count logs by type based on filename patterns."""
        types = {log_type: 0 for log_type in LOG_TYPE_PATTERNS.keys()}
        
        for log_file in log_files:
            name = log_file.name.lower()
            categorized = False
            
            for log_type, pattern in LOG_TYPE_PATTERNS.items():
                if pattern and pattern in name:
                    types[log_type] += 1
                    categorized = True
                    break
            
            if not categorized:
                types["general"] += 1
        
        return types
    
    def _format_file_time(self, file_path: Path) -> str:
        """Format file modification time."""
        return datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d")


class ModelsAnalytics:
    """Handles model cache analytics (SRP)."""
    
    def __init__(self, path_manager: StoragePathManager):
        self.path_manager = path_manager
        self.logger = get_logger(__name__)
    
    def get_analytics(self) -> Dict:
        """Get detailed models analytics."""
        try:
            if not self.path_manager.models_dir.exists():
                return self._empty_analytics()

            model_dirs = [d for d in self.path_manager.models_dir.iterdir() if d.is_dir()]
            if not model_dirs:
                return self._empty_analytics()

            return self._analyze_model_dirs(model_dirs)

        except Exception as e:
            self.logger.warning("Error getting models analytics: %s", e)
            return self._empty_analytics()
    
    def _empty_analytics(self) -> Dict:
        """Return empty analytics structure."""
        return {"count": 0, "last_used": None, "cached_models": []}
    
    def _analyze_model_dirs(self, model_dirs: List[Path]) -> Dict:
        """Analyze model directories."""
        # Find most recently accessed
        most_recent = max(model_dirs, key=lambda x: x.stat().st_atime)
        last_used_time = datetime.fromtimestamp(most_recent.stat().st_atime)

        # List cached models (convert back from safe names)
        cached_models = [d.name.replace("_", "/") for d in model_dirs]

        return {
            "count": len(model_dirs),
            "last_used": last_used_time.strftime("%Y-%m-%d %H:%M"),
            "cached_models": cached_models[:5],  # Show first 5
            "total_cached": len(cached_models),
        }


# =============================================================================
# CLEANUP STRATEGIES (Strategy Pattern + SRP)
# =============================================================================

class BaseCleanupStrategy(ABC):
    """Base cleanup strategy (OCP)."""
    
    def __init__(self, path_manager: StoragePathManager):
        self.path_manager = path_manager
        self.logger = get_logger(__name__)
    
    @abstractmethod
    def clean_by_age(self, older_than_days: int) -> int:
        """Clean items older than specified days."""
        pass
    
    @abstractmethod
    def clean_all(self) -> int:
        """Clean all items."""
        pass


class EmbeddingsCleanupStrategy(BaseCleanupStrategy):
    """Handles embeddings cleanup (SRP)."""
    
    def clean_by_age(self, older_than_days: int) -> int:
        """Clean embeddings older than specified days."""
        try:
            from core.embeddings.vector_store import get_vector_store

            vector_store = get_vector_store()
            embeddings_info = vector_store.list_embeddings()
            
            cutoff_time = datetime.now() - timedelta(days=older_than_days)
            cleaned_count = 0

            for embedding_info in embeddings_info:
                embedding_name = embedding_info["name"]
                created_time = datetime.fromtimestamp(embedding_info.get("created", 0))
                
                if created_time < cutoff_time:
                    if self._delete_embedding(embedding_name):
                        cleaned_count += 1
                        self.logger.info("Cleaned old embedding: %s (created %s)", 
                                       embedding_name, created_time.strftime("%Y-%m-%d"))

            return cleaned_count

        except Exception as e:
            self.logger.error("Error cleaning embeddings by age: %s", e)
            return 0
    
    def clean_all(self) -> int:
        """Clean all embeddings."""
        try:
            from core.embeddings.vector_store import get_vector_store

            vector_store = get_vector_store()
            embeddings_info = vector_store.list_embeddings()
            cleaned_count = 0

            for embedding_info in embeddings_info:
                embedding_name = embedding_info["name"]
                if self._delete_embedding(embedding_name):
                    cleaned_count += 1

            return cleaned_count

        except Exception as e:
            self.logger.error("Error cleaning all embeddings: %s", e)
            return 0
    
    def _delete_embedding(self, embedding_name: str) -> bool:
        """Delete a specific embedding."""
        try:
            from core.embeddings.vector_store import get_vector_store

            vector_store = get_vector_store()
            success = vector_store.delete_embedding(embedding_name)

            if success:
                self.logger.info("Deleted embedding '%s'", embedding_name)
                return True
            else:
                self.logger.warning("Embedding '%s' not found", embedding_name)
                return False

        except Exception as e:
            self.logger.error("Error deleting embedding '%s': %s", embedding_name, e)
            return False


class LogsCleanupStrategy(BaseCleanupStrategy):
    """Handles logs cleanup (SRP)."""
    
    def clean_by_age(self, older_than_days: int) -> int:
        """Clean log files older than specified days."""
        if not self.path_manager.logs_dir.exists():
            return 0

        try:
            cutoff_time = datetime.now() - timedelta(days=older_than_days)
            cleaned_count = 0

            for log_file in self.path_manager.logs_dir.rglob("*.log"):
                if log_file.is_file():
                    file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if file_time < cutoff_time:
                        try:
                            log_file.unlink()
                            cleaned_count += 1
                            self.logger.info("Cleaned old log: %s", log_file.name)
                        except Exception as e:
                            self.logger.warning("Failed to delete log %s: %s", log_file, e)

            return cleaned_count

        except Exception as e:
            self.logger.error("Error cleaning logs by age: %s", e)
            return 0
    
    def clean_all(self) -> int:
        """Clean all log files."""
        return self.clean_by_age(0)  # Clean all regardless of age


class ModelsCleanupStrategy(BaseCleanupStrategy):
    """Handles model cache cleanup (SRP)."""
    
    def clean_by_age(self, older_than_days: int = DEFAULT_MODEL_UNUSED_DAYS) -> int:
        """Clean unused model cache files."""
        if not self.path_manager.models_dir.exists():
            return 0

        try:
            cutoff_time = datetime.now() - timedelta(days=older_than_days)
            cleaned_count = 0

            for model_path in self.path_manager.models_dir.iterdir():
                if model_path.is_dir():
                    try:
                        access_time = datetime.fromtimestamp(model_path.stat().st_atime)
                        if access_time < cutoff_time:
                            shutil.rmtree(model_path)
                            cleaned_count += 1
                            self.logger.info("Cleaned unused model cache: %s", model_path.name)
                    except Exception as e:
                        self.logger.warning("Failed to clean model cache %s: %s", model_path, e)

            return cleaned_count

        except Exception as e:
            self.logger.error("Error cleaning unused models: %s", e)
            return 0
    
    def clean_all(self) -> int:
        """Clean all model cache files."""
        if not self.path_manager.models_dir.exists():
            return 0

        try:
            cleaned_count = 0
            for model_path in self.path_manager.models_dir.iterdir():
                if model_path.is_dir():
                    try:
                        shutil.rmtree(model_path)
                        cleaned_count += 1
                        self.logger.info("Cleaned model cache: %s", model_path.name)
                    except Exception as e:
                        self.logger.warning("Failed to clean model cache %s: %s", model_path, e)

            return cleaned_count

        except Exception as e:
            self.logger.error("Error cleaning all models: %s", e)
            return 0


class TempCleanupStrategy(BaseCleanupStrategy):
    """Handles temporary files cleanup (SRP)."""
    
    def clean_by_age(self, older_than_hours: int = DEFAULT_TEMP_CLEANUP_HOURS) -> int:
        """Clean temp files older than specified hours."""
        if not self.path_manager.temp_dir.exists():
            return 0

        try:
            cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
            cleaned_count = 0

            for temp_file in self.path_manager.temp_dir.rglob("*"):
                if temp_file.is_file():
                    file_time = datetime.fromtimestamp(temp_file.stat().st_mtime)
                    if file_time < cutoff_time:
                        try:
                            temp_file.unlink()
                            cleaned_count += 1
                            self.logger.debug("Cleaned temp file: %s", temp_file.name)
                        except Exception as e:
                            self.logger.warning("Failed to delete temp file %s: %s", temp_file, e)

            return cleaned_count

        except Exception as e:
            self.logger.error("Error during temp cleanup: %s", e)
            return 0
    
    def clean_all(self) -> int:
        """Clean all temporary files."""
        return self.clean_by_age(0)  # Clean all regardless of age


# =============================================================================
# STORAGE MANAGER (Composition + Facade Pattern)
# =============================================================================

class StorageManager:
    """
    Main storage manager using composition pattern (Clean Architecture).
    
    Acts as a facade for different storage operations while maintaining
    single responsibility principle through composition.
    """

    def __init__(self, base_path: Optional[str] = None):
        self.logger = get_logger(__name__)
        
        # Composition: Inject dependencies (Dependency Inversion Principle)
        self.path_manager = StoragePathManager(base_path)
        self.embeddings_analytics = EmbeddingsAnalytics(self.path_manager)
        self.log_analytics = LogAnalytics(self.path_manager)
        self.models_analytics = ModelsAnalytics(self.path_manager)
        
        # Cleanup strategies (Strategy Pattern)
        self.cleanup_strategies = {
            "embeddings": EmbeddingsCleanupStrategy(self.path_manager),
            "logs": LogsCleanupStrategy(self.path_manager),
            "models": ModelsCleanupStrategy(self.path_manager),
            "temp": TempCleanupStrategy(self.path_manager),
        }

    # =============================================================================
    # PUBLIC API (Facade Pattern - Backward Compatibility)
    # =============================================================================
    
    @property
    def base_path(self) -> Path:
        """Get base storage path."""
        return self.path_manager.base_path
    
    def ensure_storage_structure(self) -> None:
        """Ensure all storage directories exist."""
        self.path_manager.ensure_storage_structure()
    
    def get_embedding_path(self, embedding_name: str) -> Path:
        """Get path for embedding data."""
        return self.path_manager.get_embedding_path(embedding_name)

    def get_model_cache_path(self, model_name: str) -> Path:
        """Get path for cached model."""
        return self.path_manager.get_model_cache_path(model_name)

    def get_log_file_path(self, log_name: str = "context-ai.log") -> Path:
        """Get path for log file."""
        return self.path_manager.get_log_file_path(log_name)

    def get_temp_file_path(self, filename: str) -> Path:
        """Get path for temporary file."""
        return self.path_manager.get_temp_file_path(filename)

    def list_embeddings(self) -> List[str]:
        """List all available embedding names."""
        try:
            from core.embeddings.vector_store import get_vector_store

            vector_store = get_vector_store()
            embeddings_info = vector_store.list_embeddings()
            return sorted([info["name"] for info in embeddings_info])

        except Exception as e:
            self.logger.warning("Error listing embeddings from vector store: %s", e)
            return []

    def embedding_exists(self, embedding_name: str) -> bool:
        """Check if embedding exists."""
        try:
            from core.embeddings.vector_store import get_vector_store

            vector_store = get_vector_store()
            info = vector_store.get_embedding_info(embedding_name)
            return info is not None

        except Exception as e:
            self.logger.warning("Error checking embedding existence: %s", e)
            return False

    def get_storage_size(self) -> int:
        """Get total storage size in bytes."""
        try:
            total_size = 0
            for root, dirs, files in os.walk(self.path_manager.base_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                    except (OSError, FileNotFoundError):
                        continue
            return total_size

        except Exception as e:
            self.logger.warning("Error calculating storage size: %s", e)
            return 0

    def get_storage_info(self) -> Dict:
        """Get comprehensive storage information."""
        try:
            embeddings = self.list_embeddings()
            total_size = self.get_storage_size()
            dir_sizes = self.path_manager.get_directory_sizes()

            return {
                "base_path": str(self.path_manager.base_path),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "embeddings_count": len(embeddings),
                "embeddings": embeddings,
                "directory_sizes": dir_sizes,
                "created": self.path_manager.base_path.stat().st_ctime,
                "last_modified": self.path_manager.base_path.stat().st_mtime,
                "embeddings_analytics": self.embeddings_analytics.get_analytics(),
                "log_analytics": self.log_analytics.get_analytics(),
                "models_analytics": self.models_analytics.get_analytics(),
                "last_cleanup": self._get_last_cleanup_time(),
            }

        except Exception as e:
            self.logger.error("Error getting storage info: %s", e)
            return {"error": str(e)}

    # =============================================================================
    # CLEANUP OPERATIONS (Strategy Pattern)
    # =============================================================================
    
    def cleanup_temp_files(self, older_than_hours: int = DEFAULT_TEMP_CLEANUP_HOURS) -> int:
        """Clean up temporary files (backward compatibility)."""
        cleaned_count = self.cleanup_strategies["temp"].clean_by_age(older_than_hours)
        self._update_cleanup_time()
        return cleaned_count

    def clean_embeddings_by_age(self, older_than_days: int) -> int:
        """Clean embeddings older than specified days."""
        cleaned_count = self.cleanup_strategies["embeddings"].clean_by_age(older_than_days)
        self._update_cleanup_time()
        return cleaned_count

    def clean_all_embeddings(self) -> int:
        """Clean all embeddings data."""
        cleaned_count = self.cleanup_strategies["embeddings"].clean_all()
        self._update_cleanup_time()
        return cleaned_count

    def clean_logs_by_age(self, older_than_days: int) -> int:
        """Clean log files older than specified days."""
        cleaned_count = self.cleanup_strategies["logs"].clean_by_age(older_than_days)
        self._update_cleanup_time()
        return cleaned_count

    def clean_unused_models(self) -> int:
        """Clean unused model cache files."""
        cleaned_count = self.cleanup_strategies["models"].clean_by_age()
        self._update_cleanup_time()
        return cleaned_count

    def clean_all_models(self) -> int:
        """Clean all model cache files."""
        cleaned_count = self.cleanup_strategies["models"].clean_all()
        self._update_cleanup_time()
        return cleaned_count

    def delete_embedding(self, embedding_name: str) -> bool:
        """Delete a specific embedding and its metadata."""
        try:
            # Delete from vector store
            embeddings_strategy = self.cleanup_strategies["embeddings"]
            vector_deleted = embeddings_strategy._delete_embedding(embedding_name)
            
            # Delete metadata file
            self.delete_embedding_metadata(embedding_name)
            
            return vector_deleted
        except Exception as e:
            self.logger.error("Error deleting embedding '%s': %s", embedding_name, e)
            raise StorageError(f"Failed to delete embedding '{embedding_name}': {e}")

    def get_available_embeddings(self) -> List:
        """Get list of available embeddings with metadata."""
        try:
            import json
            from config.models import EmbeddingInfo
            
            embeddings = []
            embeddings_dir = self.path_manager.base_path / "embeddings"

            if not embeddings_dir.exists():
                return embeddings

            for embedding_file in embeddings_dir.glob("*.json"):
                try:
                    with open(embedding_file, "r") as f:
                        data = json.load(f)
                        embedding_info = EmbeddingInfo(**data)
                        embeddings.append(embedding_info)
                except Exception as e:
                    self.logger.warning("Error reading embedding metadata %s: %s", embedding_file.name, e)

            return sorted(embeddings, key=lambda x: x.created_at, reverse=True)

        except Exception as e:
            self.logger.warning("Error getting available embeddings: %s", e)
            return []

    def save_embedding_metadata(self, embedding_info) -> None:
        """Save embedding metadata."""
        try:
            import json
            
            embeddings_dir = self.path_manager.base_path / "embeddings"
            embeddings_dir.mkdir(parents=True, exist_ok=True)
            
            metadata_file = embeddings_dir / f"{embedding_info.name}.json"

            with open(metadata_file, "w") as f:
                json.dump(embedding_info.dict(), f, indent=2, default=str)
            self.logger.debug("Saved embedding metadata: %s", embedding_info.name)
            
        except Exception as e:
            raise StorageError(f"Failed to save embedding metadata: {e}")

    def delete_embedding_metadata(self, embedding_name: str) -> None:
        """Delete embedding metadata."""
        try:
            embeddings_dir = self.path_manager.base_path / "embeddings"
            metadata_file = embeddings_dir / f"{embedding_name}.json"

            if metadata_file.exists():
                metadata_file.unlink()
                self.logger.debug("Deleted embedding metadata: %s", embedding_name)
        except Exception as e:
            self.logger.warning("Failed to delete embedding metadata: %s", e)

    def reset_storage(self, confirm: bool = False) -> bool:
        """Reset all storage (DELETE EVERYTHING)."""
        if not confirm:
            self.logger.warning("Reset storage called without confirmation")
            return False

        try:
            if self.path_manager.base_path.exists():
                shutil.rmtree(self.path_manager.base_path)
                self.logger.info("Storage reset: deleted %s", self.path_manager.base_path)

            # Recreate basic structure
            self.path_manager.ensure_storage_structure()
            self.logger.info("Storage reset complete")
            return True

        except Exception as e:
            raise StorageError(f"Failed to reset storage: {e}")

    # =============================================================================
    # PRIVATE HELPERS (DRY principle)
    # =============================================================================
    
    def _get_last_cleanup_time(self) -> str:
        """Get last cleanup time from metadata file."""
        try:
            cleanup_file = self.path_manager.base_path / CLEANUP_METADATA_FILE
            if cleanup_file.exists():
                timestamp = float(cleanup_file.read_text().strip())
                last_cleanup = datetime.fromtimestamp(timestamp)
                return last_cleanup.strftime("%Y-%m-%d %H:%M")
            else:
                return "Never"

        except Exception as e:
            self.logger.warning("Error getting last cleanup time: %s", e)
            return "Unknown"

    def _update_cleanup_time(self) -> None:
        """Update last cleanup time."""
        try:
            cleanup_file = self.path_manager.base_path / CLEANUP_METADATA_FILE
            cleanup_file.write_text(str(datetime.now().timestamp()))
        except Exception as e:
            self.logger.warning("Error updating cleanup time: %s", e)


# =============================================================================
# GLOBAL INSTANCE (Singleton Pattern)
# =============================================================================

_storage_manager: Optional[StorageManager] = None


def get_storage_manager() -> StorageManager:
    """Get global storage manager instance."""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = StorageManager()
        _storage_manager.ensure_storage_structure()
    return _storage_manager
