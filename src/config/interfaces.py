"""
Configuration Interfaces for Context-AI.

Defines protocols and adapters that enable dependency injection throughout the system.
These interfaces allow components to depend on abstractions rather than concrete
implementations, making the system more testable and flexible.
"""

from pathlib import Path
from typing import Protocol

__all__ = [
    "PathProvider",
    "StoragePathProvider",
]


class PathProvider(Protocol):
    """
    Protocol for providing configuration paths.

    This interface allows SettingsManager to get paths without
    directly depending on StorageManager (Dependency Inversion).
    """

    def get_base_path(self) -> Path:
        """Get base configuration directory path."""
        ...

    def get_config_file_path(self, filename: str) -> Path:
        """Get path for configuration file."""
        ...

    def get_embeddings_metadata_dir(self) -> Path:
        """Get directory for embeddings metadata JSONs."""
        ...


class StoragePathProvider:
    """
    Adapter implementing PathProvider using StorageManager.

    This adapter allows SettingsManager to get paths from StorageManager
    without tight coupling (Adapter Pattern).
    """

    def __init__(self):
        # Import here to avoid circular dependency
        from config.storage import get_storage_manager

        self._storage_manager = get_storage_manager()

    def get_base_path(self) -> Path:
        """Get base configuration directory path from StorageManager."""
        return self._storage_manager.path_manager.base_path

    def get_config_file_path(self, filename: str) -> Path:
        """Get path for configuration file."""
        return self._storage_manager.path_manager.base_path / filename

    def get_embeddings_metadata_dir(self) -> Path:
        """Get directory for embeddings metadata JSONs."""
        return self._storage_manager.path_manager.embeddings_dir


# Global path provider instance
_default_path_provider = None


def get_default_path_provider() -> PathProvider:
    """Get default path provider instance."""
    global _default_path_provider
    if _default_path_provider is None:
        _default_path_provider = StoragePathProvider()
    return _default_path_provider
