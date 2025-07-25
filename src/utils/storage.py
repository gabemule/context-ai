"""
Storage path management utilities for Context-AI.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta

from config.constants import DEFAULT_CONFIG_DIR
from utils.logging import get_logger
from utils.exceptions import StorageError


class StorageManager:
    """Manages storage paths and operations for Context-AI."""
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize storage manager.
        
        Args:
            base_path: Optional custom base path
        """
        self.logger = get_logger(__name__)
        
        # Resolve base storage path
        if base_path:
            self.base_path = Path(base_path).expanduser().resolve()
        else:
            self.base_path = Path(DEFAULT_CONFIG_DIR).expanduser().resolve()
        
        # Define storage structure
        self.config_file = self.base_path / "config.json"
        self.active_file = self.base_path / "active.json"
        self.embeddings_dir = self.base_path / "embeddings"
        self.chroma_dir = self.base_path / "chroma"
        self.models_dir = self.base_path / "models"
        self.logs_dir = self.base_path / "logs"
        self.temp_dir = self.base_path / "temp"
    
    def ensure_storage_structure(self) -> None:
        """Ensure all storage directories exist."""
        try:
            directories = [
                self.base_path,
                self.embeddings_dir,
                self.chroma_dir,
                self.models_dir,
                self.logs_dir,
                self.temp_dir
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                self.logger.debug("Ensured directory exists: %s", directory)
                
        except Exception as e:
            raise StorageError(f"Failed to create storage structure: {e}")
    
    def get_embedding_path(self, embedding_name: str) -> Path:
        """Get path for embedding data."""
        return self.chroma_dir / f"{embedding_name}.db"
    
    def get_embedding_metadata_path(self, embedding_name: str) -> Path:
        """Get path for embedding metadata."""
        return self.embeddings_dir / f"{embedding_name}.json"
    
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
    
    def list_embeddings(self) -> List[str]:
        """List all available embedding names from ChromaDB."""
        try:
            # Import here to avoid circular imports
            from core.embeddings.vector_store import get_vector_store
            
            vector_store = get_vector_store()
            embeddings_info = vector_store.list_embeddings()
            
            return sorted([info["name"] for info in embeddings_info])
            
        except Exception as e:
            self.logger.warning("Error listing embeddings from vector store: %s", e)
            # Fallback to JSON files if vector store fails
            try:
                if not self.embeddings_dir.exists():
                    return []
                
                embeddings = []
                for metadata_file in self.embeddings_dir.glob("*.json"):
                    embedding_name = metadata_file.stem
                    embeddings.append(embedding_name)
                
                return sorted(embeddings)
            except Exception as fallback_e:
                self.logger.warning("Fallback to JSON files also failed: %s", fallback_e)
                return []
    
    def embedding_exists(self, embedding_name: str) -> bool:
        """Check if embedding exists in ChromaDB."""
        try:
            from core.embeddings.vector_store import get_vector_store
            
            vector_store = get_vector_store()
            info = vector_store.get_embedding_info(embedding_name)
            return info is not None
            
        except Exception as e:
            self.logger.warning("Error checking embedding existence: %s", e)
            # Fallback to JSON file check
            return self.get_embedding_metadata_path(embedding_name).exists()
    
    def get_storage_size(self) -> int:
        """Get total storage size in bytes."""
        try:
            total_size = 0
            for root, dirs, files in os.walk(self.base_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                    except (OSError, FileNotFoundError):
                        # Skip files that can't be accessed
                        continue
            return total_size
            
        except Exception as e:
            self.logger.warning("Error calculating storage size: %s", e)
            return 0
    
    def get_storage_info(self) -> dict:
        """Get comprehensive storage information."""
        try:
            embeddings = self.list_embeddings()
            total_size = self.get_storage_size()
            
            # Check directory sizes
            dir_sizes = {}
            for dir_name, dir_path in [
                ("embeddings", self.embeddings_dir),
                ("chroma", self.chroma_dir),
                ("models", self.models_dir),
                ("logs", self.logs_dir),
                ("temp", self.temp_dir)
            ]:
                if dir_path.exists():
                    size = sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file())
                    dir_sizes[dir_name] = size
                else:
                    dir_sizes[dir_name] = 0
            
            return {
                "base_path": str(self.base_path),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "embeddings_count": len(embeddings),
                "embeddings": embeddings,
                "directory_sizes": dir_sizes,
                "created": self.base_path.stat().st_ctime,
                "last_modified": self.base_path.stat().st_mtime
            }
            
        except Exception as e:
            self.logger.error("Error getting storage info: %s", e)
            return {"error": str(e)}
    
    def cleanup_temp_files(self, older_than_hours: int = 24) -> int:
        """
        Clean up temporary files older than specified hours.
        
        Args:
            older_than_hours: Remove files older than this many hours
            
        Returns:
            Number of files cleaned up
        """
        if not self.temp_dir.exists():
            return 0
        
        try:
            cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
            cleaned_count = 0
            
            for temp_file in self.temp_dir.rglob('*'):
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
    
    def reset_storage(self, confirm: bool = False) -> bool:
        """
        Reset all storage (DELETE EVERYTHING).
        
        Args:
            confirm: Must be True to actually perform reset
            
        Returns:
            True if reset was performed
        """
        if not confirm:
            self.logger.warning("Reset storage called without confirmation")
            return False
        
        try:
            if self.base_path.exists():
                shutil.rmtree(self.base_path)
                self.logger.info("Storage reset: deleted %s", self.base_path)
            
            # Recreate basic structure
            self.ensure_storage_structure()
            self.logger.info("Storage reset complete")
            return True
            
        except Exception as e:
            raise StorageError(f"Failed to reset storage: {e}")
    
    def delete_embedding(self, embedding_name: str) -> bool:
        """
        Delete a specific embedding and its metadata.
        
        Args:
            embedding_name: Name of embedding to delete
            
        Returns:
            True if deletion was successful
        """
        try:
            deleted_files = 0
            
            # Delete metadata file
            metadata_path = self.get_embedding_metadata_path(embedding_name)
            if metadata_path.exists():
                metadata_path.unlink()
                deleted_files += 1
                self.logger.debug("Deleted metadata: %s", metadata_path)
            
            # Delete embedding data
            embedding_path = self.get_embedding_path(embedding_name)
            if embedding_path.exists():
                if embedding_path.is_dir():
                    shutil.rmtree(embedding_path)
                else:
                    embedding_path.unlink()
                deleted_files += 1
                self.logger.debug("Deleted embedding data: %s", embedding_path)
            
            if deleted_files > 0:
                self.logger.info("Deleted embedding '%s' (%d files)", embedding_name, deleted_files)
                return True
            else:
                self.logger.warning("Embedding '%s' not found", embedding_name)
                return False
                
        except Exception as e:
            self.logger.error("Error deleting embedding '%s': %s", embedding_name, e)
            raise StorageError(f"Failed to delete embedding '{embedding_name}': {e}")


# Global storage manager instance
_storage_manager: Optional[StorageManager] = None


def get_storage_manager() -> StorageManager:
    """Get global storage manager instance."""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = StorageManager()
        _storage_manager.ensure_storage_structure()
    return _storage_manager