"""
Settings management for Context-AI.

Business logic layer for configuration management using ConfigCore.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from utils.exceptions import ConfigurationError
from utils.logging import get_logger

from .core import get_config_core
from .models import ActiveEmbeddings, AIProviderConfig, ContextAIConfig, EmbeddingInfo
from .interfaces import PathProvider, get_default_path_provider


class SettingsManager:
    """
    Manages Context-AI configuration and settings using ConfigCore.
    
    This is the business logic layer that uses ConfigCore for data operations
    and provides higher-level configuration management.
    """

    def __init__(self, config_core=None, path_provider: Optional[PathProvider] = None):
        """
        Initialize settings manager.

        Args:
            config_core: Optional ConfigCore instance for dependency injection
            path_provider: Optional path provider for dependency injection
        """
        self.logger = get_logger(__name__)

        # Use dependency injection for ConfigCore (eliminates circular dependencies)
        if config_core is not None:
            self.config_core = config_core
        else:
            self.config_core = get_config_core()

        # Use dependency injection for paths (eliminates hardcoding)
        if path_provider is not None:
            self.path_provider = path_provider
        else:
            self.path_provider = get_default_path_provider()

        # Config file paths
        self.config_dir = self.path_provider.get_base_path()
        self.active_file = self.path_provider.get_config_file_path("active.json")

        # In-memory active embeddings cache (config.json handled by ConfigCore)
        self._active: Optional[ActiveEmbeddings] = None

    def initialize(self) -> None:
        """Initialize configuration directory and files."""
        try:
            # Create config directory
            self.config_dir.mkdir(parents=True, exist_ok=True)

            # ConfigCore handles config.json initialization automatically
            # We only need to handle active.json here
            if not self.active_file.exists():
                self.logger.info("Creating default active embeddings file")
                default_active = ActiveEmbeddings()
                self._save_active(default_active)

            self.logger.debug("Configuration initialized at: %s", self.config_dir)

        except Exception as e:
            raise ConfigurationError(f"Failed to initialize configuration: {e}")

    def get_config(self) -> ContextAIConfig:
        """Get current configuration via ConfigCore."""
        # Use ConfigCore instead of direct file operations
        config_data = self.config_core.get_config_data()
        return ContextAIConfig(**config_data)

    def save_config(self, config: ContextAIConfig) -> None:
        """Save configuration via ConfigCore."""
        # Use ConfigCore instead of direct file operations
        self.config_core.save_config_data(config.dict())

    def get_active_embeddings(self) -> ActiveEmbeddings:
        """Get active embeddings configuration."""
        if self._active is None:
            self._load_active()
        return self._active

    def save_active_embeddings(self, active: ActiveEmbeddings) -> None:
        """Save active embeddings configuration."""
        self._save_active(active)
        self._active = active

    def set_claude_api_key(self, api_key: str) -> None:
        """Set Claude API key via ConfigCore."""
        # Use ConfigCore directly - cleaner and simpler
        self.config_core.set_provider_api_key("claude", api_key)
        self.config_core.set_active_provider("claude")
        
        # Set default model and max_tokens via ProviderRegistry
        from .providers.registry import get_provider_registry
        registry = get_provider_registry()
        default_model = registry.default_model
        max_tokens = registry.get_max_tokens()
        
        self.config_core.set_provider_model("claude", default_model)
        self.config_core.set_provider_max_tokens("claude", max_tokens)
        
        self.logger.info("Claude API key configured successfully")

    def get_claude_api_key(self) -> Optional[str]:
        """Get Claude API key via ConfigCore."""
        return self.config_core.get_provider_api_key("claude")

    def set_active_provider(self, provider: str) -> None:
        """Set active AI provider via ConfigCore."""
        self.config_core.set_active_provider(provider)
        self.logger.info("Active provider set to: %s", provider)

    def set_model(self, model: str) -> None:
        """Set model for the active provider via ConfigCore."""
        active_provider = self.config_core.get_active_provider()
        self.config_core.set_provider_model(active_provider, model)
        self.logger.info("Model for %s set to: %s", active_provider, model)

    def get_prompt_mode(self) -> str:
        """Get the current prompt mode via ConfigCore."""
        return self.config_core.get_prompt_mode()

    def set_prompt_mode(self, mode: str) -> None:
        """Set the prompt mode via ConfigCore."""
        self.config_core.set_prompt_mode(mode)
        self.logger.info("Prompt mode set to: %s", mode)

    def set_active_embeddings(self, embedding_names: List[str]) -> None:
        """Set active embeddings (validates via vector store)."""
        # Validate that all embeddings exist via vector store directly
        from core.embeddings.vector_store import get_vector_store
        vector_store = get_vector_store()
        
        valid_embeddings = []
        for name in embedding_names:
            if vector_store.get_embedding_info(name) is not None:
                valid_embeddings.append(name)
            else:
                self.logger.warning("Embedding '%s' not found, skipping", name)
        
        active = ActiveEmbeddings(selected=valid_embeddings, last_updated=datetime.now())
        self.save_active_embeddings(active)
        self.logger.info("Active embeddings set: %s", ", ".join(valid_embeddings))

    def get_available_embeddings(self) -> List[EmbeddingInfo]:
        """Get list of available embeddings with metadata."""
        try:
            embeddings = []
            embeddings_dir = self.path_provider.get_embeddings_metadata_dir()

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

    def save_embedding_metadata(self, embedding_info: EmbeddingInfo) -> None:
        """Save embedding metadata."""
        try:
            embeddings_dir = self.path_provider.get_embeddings_metadata_dir()
            embeddings_dir.mkdir(parents=True, exist_ok=True)
            
            metadata_file = embeddings_dir / f"{embedding_info.name}.json"

            with open(metadata_file, "w") as f:
                json.dump(embedding_info.dict(), f, indent=2, default=str)
            self.logger.debug("Saved embedding metadata: %s", embedding_info.name)
            
        except Exception as e:
            raise ConfigurationError(f"Failed to save embedding metadata: {e}")

    def delete_embedding_metadata(self, embedding_name: str) -> None:
        """Delete embedding metadata."""
        try:
            embeddings_dir = self.path_provider.get_embeddings_metadata_dir()
            metadata_file = embeddings_dir / f"{embedding_name}.json"

            if metadata_file.exists():
                metadata_file.unlink()
                self.logger.debug("Deleted embedding metadata: %s", embedding_name)
        except Exception as e:
            self.logger.warning("Failed to delete embedding metadata: %s", e)

    def delete_embedding(self, embedding_name: str) -> bool:
        """Delete embedding and its metadata (coordinated operation)."""
        try:
            # Delete actual data from vector store
            from core.embeddings.vector_store import get_vector_store
            vector_store = get_vector_store()
            vector_deleted = vector_store.delete_embedding(embedding_name)
            
            # Delete metadata JSON (Settings responsibility)
            self.delete_embedding_metadata(embedding_name)
            
            if vector_deleted:
                self.logger.info("Deleted embedding '%s' and metadata", embedding_name)
            
            return vector_deleted
        except Exception as e:
            self.logger.error("Error deleting embedding '%s': %s", embedding_name, e)
            raise ConfigurationError(f"Failed to delete embedding '{embedding_name}': {e}")


    def _load_active(self) -> None:
        """Load active embeddings from file."""
        try:
            if not self.active_file.exists():
                self._active = ActiveEmbeddings()
                return

            with open(self.active_file, "r") as f:
                data = json.load(f)
                self._active = ActiveEmbeddings(**data)

        except Exception as e:
            self.logger.warning(
                "Failed to load active embeddings, using defaults: %s", e
            )
            self._active = ActiveEmbeddings()

    def _save_active(self, active: ActiveEmbeddings) -> None:
        """Save active embeddings to file."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)

            with open(self.active_file, "w") as f:
                json.dump(active.dict(), f, indent=2, default=str)

        except Exception as e:
            raise ConfigurationError(f"Failed to save active embeddings: {e}")



# Global settings manager instance
_settings_manager: Optional[SettingsManager] = None


def get_settings_manager() -> SettingsManager:
    """Get global settings manager instance."""
    global _settings_manager
    if _settings_manager is None:
        # Ensure setup is complete first using dedicated SetupManager
        from config.setup import get_setup_manager
        setup_manager = get_setup_manager()
        setup_manager.ensure_all_configs_exist()
        
        _settings_manager = SettingsManager()
        _settings_manager.initialize()  # Only handles config.json/active.json
    return _settings_manager
