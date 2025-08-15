"""
Settings Manager for Context-AI.

High-level interface for user configuration operations. Coordinates complex
configuration changes that involve multiple managers while providing a
simple, consistent API for end users.
"""

import json
from datetime import datetime
from typing import List, Optional

from utils.exceptions import ConfigurationError
from utils.logging import get_logger

from .core import get_config_core
from .interfaces import PathProvider, get_default_path_provider
from .models import ActiveEmbeddings, ContextAIConfig, EmbeddingInfo


class SettingsManager:
    """
    User-facing interface for configuration management.

    Purpose: Provides a simple, consistent API for users to configure the system
    without needing to understand the underlying architecture. Coordinates
    complex operations across multiple managers.

    Benefits:
    - Single interface for all user configuration needs
    - Handles complex multi-step configuration changes automatically
    - Validates configuration changes before applying them
    - Abstracts away implementation details from users
    """

    def __init__(
        self,
        config_core=None,
        embedding_manager=None,
        path_provider: Optional[PathProvider] = None,
    ):
        """
        Initialize settings manager.

        Args:
            config_core: Optional ConfigCore instance for dependency injection
            embedding_manager: Optional EmbeddingManager instance for dependency injection
            path_provider: Optional path provider for dependency injection
        """
        self.logger = get_logger(__name__)

        # Use dependency injection for ConfigCore (eliminates circular dependencies)
        if config_core is not None:
            self.config_core = config_core
        else:
            self.config_core = get_config_core()

        # Use dependency injection for EmbeddingManager (eliminates SRP violations)
        if embedding_manager is not None:
            self.embedding_manager = embedding_manager
        else:
            from .embeddings import get_embedding_manager

            self.embedding_manager = get_embedding_manager()

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
        """Set active embeddings (validates via EmbeddingManager)."""
        # Use EmbeddingManager for validation (SRP compliance)
        valid_embeddings = self.embedding_manager.validate_embeddings(embedding_names)

        active = ActiveEmbeddings(
            selected=valid_embeddings, last_updated=datetime.now()
        )
        self.save_active_embeddings(active)
        self.logger.info("Active embeddings set: %s", ", ".join(valid_embeddings))

    def get_available_embeddings(self) -> List[EmbeddingInfo]:
        """Get list of available embeddings with metadata via EmbeddingManager."""
        # Use EmbeddingManager for metadata operations (SRP compliance)
        metadata_list = self.embedding_manager.get_available_embeddings_metadata()

        # Convert to EmbeddingInfo objects
        embeddings = []
        for data in metadata_list:
            try:
                embedding_info = EmbeddingInfo(**data)
                embeddings.append(embedding_info)
            except Exception as e:
                self.logger.warning("Error parsing embedding metadata: %s", e)

        return embeddings

    def save_embedding_metadata(self, embedding_info: EmbeddingInfo) -> None:
        """Save embedding metadata via EmbeddingManager."""
        # Use EmbeddingManager for metadata operations (SRP compliance)
        self.embedding_manager.save_embedding_metadata(embedding_info.dict())

    def delete_embedding_metadata(self, embedding_name: str) -> None:
        """Delete embedding metadata via EmbeddingManager."""
        # Use EmbeddingManager for metadata operations (SRP compliance)
        self.embedding_manager.delete_embedding_metadata(embedding_name)

    def delete_embedding(self, embedding_name: str) -> bool:
        """Delete embedding and its metadata via EmbeddingManager."""
        # Use EmbeddingManager for all embedding operations (SRP compliance)
        return self.embedding_manager.delete_embedding(embedding_name)

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
