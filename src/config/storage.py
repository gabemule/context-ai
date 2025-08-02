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
        
        # Storage directories
        self.embeddings_dir = self.base_path / "embeddings"
        self.chromadb_dir = self.embeddings_dir / "chromadb"
        self.models_dir = self.base_path / "models"
        self.logs_dir = self.base_path / "logs"
        self.temp_dir = self.base_path / "temp"
        
        # Config directories (centralized path management)
        self.config_dir = self.base_path / "config"
        self.guidelines_dir = self.config_dir / "guidelines"
        self.prompts_dir = self.config_dir / "prompts"
        
        # Config files (centralized file path management)
        self.languages_file = self.config_dir / "languages.yaml"
        self.languages_readme_file = self.config_dir / "languages-README.md"
    
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
# SIMPLIFIED CLEANUP OPERATIONS (Remove over-engineering)
# =============================================================================

def _clean_temp_files(base_path: Path, older_than_hours: int = DEFAULT_TEMP_CLEANUP_HOURS) -> int:
    """Simple temp files cleanup."""
    temp_dir = base_path / "temp"
    if not temp_dir.exists():
        return 0
    
    cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
    cleaned_count = 0
    
    for temp_file in temp_dir.rglob("*"):
        if temp_file.is_file():
            file_time = datetime.fromtimestamp(temp_file.stat().st_mtime)
            if file_time < cutoff_time:
                try:
                    temp_file.unlink()
                    cleaned_count += 1
                except Exception:
                    pass  # Ignore cleanup errors
    
    return cleaned_count


def _get_embeddings_analytics(embeddings_list: List[str]) -> Dict:
    """Get essential embeddings analytics for future sync feature."""
    try:
        from core.embeddings.vector_store import get_vector_store
        
        vector_store = get_vector_store()
        embeddings_info = vector_store.list_embeddings()
        
        if not embeddings_info:
            return {"oldest": None, "newest": None, "sizes": {}, "created_dates": {}}
        
        # Sort by creation time for sync decisions
        def get_created_time(x):
            created = x.get("created_at")
            if created:
                try:
                    return datetime.fromisoformat(created.replace('Z', '+00:00')).timestamp()
                except:
                    return 0
            return 0
        
        embeddings_by_time = sorted(embeddings_info, key=get_created_time)
        oldest = embeddings_by_time[0] if embeddings_by_time else None
        newest = embeddings_by_time[-1] if embeddings_by_time else None
        
        # Essential data for sync: sizes and creation dates
        sizes = {}
        created_dates = {}
        for info in embeddings_info:
            name = info["name"]
            size_bytes = info.get("total_size_bytes", 0)
            sizes[name] = round(size_bytes / (1024 * 1024), 2)  # MB
            created_dates[name] = info.get("created_at", "unknown")
        
        return {
            "oldest": oldest["name"] if oldest else None,
            "oldest_date": oldest.get("created_at") if oldest else None,
            "newest": newest["name"] if newest else None,
            "newest_date": newest.get("created_at") if newest else None,
            "sizes": sizes,
            "created_dates": created_dates,  # Critical for sync!
        }
        
    except Exception as e:
        return {"oldest": None, "newest": None, "sizes": {}, "created_dates": {}}


def _get_complete_analytics(embeddings_list: List[str], base_path: Path) -> Dict:
    """Get complete analytics including embeddings, logs, and models."""
    return {
        "embeddings_analytics": _get_embeddings_analytics(embeddings_list),
        "log_analytics": _get_log_analytics(base_path),
        "models_analytics": _get_models_analytics(base_path),
    }


def _get_log_analytics(base_path: Path) -> Dict:
    """Get log file analytics."""
    try:
        logs_dir = base_path / "logs"
        if not logs_dir.exists():
            return {"count": 0, "types": {}, "total_size_mb": 0}
        
        log_files = list(logs_dir.glob("*.log"))
        log_types = {}
        total_size = 0
        
        for log_file in log_files:
            try:
                size = log_file.stat().st_size
                total_size += size
                
                # Categorize by filename pattern
                for log_type, pattern in LOG_TYPE_PATTERNS.items():
                    if pattern and pattern in log_file.name:
                        log_types[log_type] = log_types.get(log_type, 0) + 1
                        break
                else:
                    log_types["general"] = log_types.get("general", 0) + 1
                    
            except Exception:
                continue
        
        return {
            "count": len(log_files),
            "types": log_types,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        }
        
    except Exception:
        return {"count": 0, "types": {}, "total_size_mb": 0}


def _get_models_analytics(base_path: Path) -> Dict:
    """Get cached models analytics."""
    try:
        models_dir = base_path / "models"
        if not models_dir.exists():
            return {"count": 0, "cached_models": [], "total_size_mb": 0}
        
        model_files = []
        total_size = 0
        
        for model_path in models_dir.iterdir():
            if model_path.is_dir():
                try:
                    size = sum(f.stat().st_size for f in model_path.rglob("*") if f.is_file())
                    total_size += size
                    model_files.append({
                        "name": model_path.name,
                        "size_mb": round(size / (1024 * 1024), 2),
                    })
                except Exception:
                    continue
        
        return {
            "count": len(model_files),
            "cached_models": sorted(model_files, key=lambda x: x["size_mb"], reverse=True),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        }
        
    except Exception:
        return {"count": 0, "cached_models": [], "total_size_mb": 0}


# =============================================================================
# STORAGE MANAGER (Composition + Facade Pattern)
# =============================================================================

class StorageManager:
    """
    Simplified storage manager focused on paths and basic operations.
    
    Removed over-engineered analytics and strategy patterns for simplicity.
    """

    def __init__(self, base_path: Optional[str] = None):
        self.logger = get_logger(__name__)
        self.path_manager = StoragePathManager(base_path)

    # Direct access to path manager - no facades
    @property
    def base_path(self) -> Path:
        """Get base storage path."""
        return self.path_manager.base_path

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
        """Get basic storage information."""
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
                **_get_complete_analytics(embeddings, self.path_manager.base_path),
                "last_cleanup": self._get_last_cleanup_time(),
            }

        except Exception as e:
            self.logger.error("Error getting storage info: %s", e)
            return {"error": str(e)}

    def cleanup_temp_files(self, older_than_hours: int = DEFAULT_TEMP_CLEANUP_HOURS) -> int:
        """Clean up temporary files."""
        cleaned_count = _clean_temp_files(self.path_manager.base_path, older_than_hours)
        self._update_cleanup_time()
        return cleaned_count

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
