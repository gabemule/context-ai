"""
Embedding Manager for Context-AI.

Provides centralized, consistent management of embedding operations throughout the system.
Handles the complete embedding lifecycle including creation, validation, deletion,
and metadata management with a clean, testable interface.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from utils.exceptions import ConfigurationError
from utils.logging import get_logger


class EmbeddingManager:
    """
    Centralized hub for all embedding operations in the system.
    
    Purpose: Provides a single, consistent interface for managing embeddings
    throughout the entire application. Handles the complete embedding lifecycle
    from creation to deletion.
    
    Benefits:
    - Single place to manage all embedding operations  
    - Consistent behavior across the entire system
    - Centralizes validation and error handling
    - Simplifies testing with dependency injection
    """
    
    def __init__(self, vector_store=None, metadata_dir: Optional[Path] = None):
        """Initialize embedding manager."""
        self.logger = get_logger(__name__)
        
        # Dependency injection for VectorStore
        if vector_store is not None:
            self.vector_store = vector_store
        else:
            from core.embeddings.vector_store import get_vector_store
            self.vector_store = get_vector_store()
        
        # Get metadata directory from StorageManager
        if metadata_dir is not None:
            self.metadata_dir = metadata_dir
        else:
            from .storage import get_storage_manager
            storage = get_storage_manager()
            self.metadata_dir = storage.path_manager.embeddings_dir
    
    def list_embeddings(self) -> List[str]:
        """List all available embedding names."""
        try:
            embeddings_info = self.vector_store.list_embeddings()
            return sorted([info["name"] for info in embeddings_info])
        except Exception as e:
            self.logger.warning("Error listing embeddings from vector store: %s", e)
            return []
    
    def embedding_exists(self, embedding_name: str) -> bool:
        """Check if embedding exists."""
        try:
            info = self.vector_store.get_embedding_info(embedding_name)
            return info is not None
        except Exception as e:
            self.logger.warning("Error checking embedding existence: %s", e)
            return False
    
    def get_embedding_info(self, embedding_name: str) -> Optional[Dict[str, Any]]:
        """Get embedding information from vector store."""
        try:
            return self.vector_store.get_embedding_info(embedding_name)
        except Exception as e:
            self.logger.warning("Error getting embedding info: %s", e)
            return None
    
    def delete_embedding(self, embedding_name: str) -> bool:
        """Delete embedding and its metadata."""
        try:
            # Delete actual data from vector store
            vector_deleted = self.vector_store.delete_embedding(embedding_name)
            
            # Delete metadata JSON file
            self.delete_embedding_metadata(embedding_name)
            
            if vector_deleted:
                self.logger.info("Deleted embedding '%s' and metadata", embedding_name)
            
            return vector_deleted
        except Exception as e:
            self.logger.error("Error deleting embedding '%s': %s", embedding_name, e)
            raise ConfigurationError(f"Failed to delete embedding '{embedding_name}': {e}")
    
    def validate_embeddings(self, embedding_names: List[str]) -> List[str]:
        """Validate that embeddings exist and return valid ones."""
        valid_embeddings = []
        for name in embedding_names:
            if self.embedding_exists(name):
                valid_embeddings.append(name)
            else:
                self.logger.warning("Embedding '%s' not found, skipping", name)
        return valid_embeddings
    
    def get_embeddings_analytics(self) -> Dict[str, Any]:
        """Get analytics about embeddings for storage info."""
        try:
            embeddings_info = self.vector_store.list_embeddings()
            
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
                "created_dates": created_dates,
            }
            
        except Exception as e:
            self.logger.warning("Error getting embeddings analytics: %s", e)
            return {"oldest": None, "newest": None, "sizes": {}, "created_dates": {}}
    
    # =============================================================================
    # METADATA OPERATIONS
    # =============================================================================
    
    def get_available_embeddings_metadata(self) -> List[Dict[str, Any]]:
        """Get list of available embeddings with metadata from JSON files."""
        try:
            embeddings = []
            
            if not self.metadata_dir.exists():
                return embeddings
            
            for embedding_file in self.metadata_dir.glob("*.json"):
                try:
                    with open(embedding_file, "r") as f:
                        data = json.load(f)
                        embeddings.append(data)
                except Exception as e:
                    self.logger.warning("Error reading embedding metadata %s: %s", embedding_file.name, e)
            
            # Sort by creation time, newest first
            return sorted(embeddings, key=lambda x: x.get("created_at", ""), reverse=True)
            
        except Exception as e:
            self.logger.warning("Error getting available embeddings metadata: %s", e)
            return []
    
    def save_embedding_metadata(self, embedding_info: Dict[str, Any]) -> None:
        """Save embedding metadata to JSON file."""
        try:
            self.metadata_dir.mkdir(parents=True, exist_ok=True)
            
            embedding_name = embedding_info["name"]
            metadata_file = self.metadata_dir / f"{embedding_name}.json"
            
            with open(metadata_file, "w") as f:
                json.dump(embedding_info, f, indent=2, default=str)
            self.logger.debug("Saved embedding metadata: %s", embedding_name)
            
        except Exception as e:
            raise ConfigurationError(f"Failed to save embedding metadata: {e}")
    
    def delete_embedding_metadata(self, embedding_name: str) -> None:
        """Delete embedding metadata file."""
        try:
            metadata_file = self.metadata_dir / f"{embedding_name}.json"
            
            if metadata_file.exists():
                metadata_file.unlink()
                self.logger.debug("Deleted embedding metadata: %s", embedding_name)
        except Exception as e:
            self.logger.warning("Failed to delete embedding metadata: %s", e)


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_embedding_manager: Optional[EmbeddingManager] = None


def get_embedding_manager() -> EmbeddingManager:
    """Get global embedding manager instance."""
    global _embedding_manager
    if _embedding_manager is None:
        _embedding_manager = EmbeddingManager()
    return _embedding_manager


def reset_embedding_manager() -> None:
    """Reset embedding manager instance (for testing)."""
    global _embedding_manager
    _embedding_manager = None
