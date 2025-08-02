"""
Settings management for Context-AI.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from utils.exceptions import ConfigurationError
from utils.logging import get_logger

from .providers import DEFAULT_MODEL, get_max_tokens
from .models import ActiveEmbeddings, AIProviderConfig, ContextAIConfig, EmbeddingInfo


class SettingsManager:
    """Manages Context-AI configuration and settings."""

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize settings manager.

        Args:
            config_dir: Optional custom config directory path
        """
        self.logger = get_logger(__name__)

        # Determine config directory
        if config_dir:
            self.config_dir = Path(config_dir).expanduser()
        else:
            self.config_dir = Path("~/.context-ai").expanduser()

        # Config file paths
        self.config_file = self.config_dir / "config.json"
        self.active_file = self.config_dir / "active.json"
        self.embeddings_dir = self.config_dir / "embeddings"

        # In-memory config cache
        self._config: Optional[ContextAIConfig] = None
        self._active: Optional[ActiveEmbeddings] = None

    def initialize(self) -> None:
        """Initialize configuration directory and files."""
        try:
            # Create config directory
            self.config_dir.mkdir(parents=True, exist_ok=True)
            self.embeddings_dir.mkdir(parents=True, exist_ok=True)

            # Create default config if doesn't exist
            if not self.config_file.exists():
                self.logger.info("Creating default configuration file")
                default_config = ContextAIConfig()
                self._save_config(default_config)

            # Create default active embeddings if doesn't exist
            if not self.active_file.exists():
                self.logger.info("Creating default active embeddings file")
                default_active = ActiveEmbeddings()
                self._save_active(default_active)

            self.logger.debug("Configuration initialized at: %s", self.config_dir)

        except Exception as e:
            raise ConfigurationError(f"Failed to initialize configuration: {e}")

    def get_config(self) -> ContextAIConfig:
        """Get current configuration."""
        if self._config is None:
            self._load_config()
        return self._config

    def save_config(self, config: ContextAIConfig) -> None:
        """Save configuration to file."""
        self._save_config(config)
        self._config = config

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
        """Set Claude API key."""
        config = self.get_config()

        # Create or update Claude provider config
        config.ai["claude"] = AIProviderConfig(
            api_key=api_key,
            default_model=DEFAULT_MODEL,
            max_tokens=get_max_tokens(),
        )

        # Set as active provider
        config.active_provider = "claude"

        self.save_config(config)
        self.logger.info("Claude API key configured successfully")

    def get_claude_api_key(self) -> Optional[str]:
        """Get Claude API key."""
        config = self.get_config()
        claude_config = config.ai.get("claude")
        return claude_config.api_key if claude_config else None

    def set_active_provider(self, provider: str) -> None:
        """Set active AI provider."""
        config = self.get_config()
        config.active_provider = provider
        self.save_config(config)
        self.logger.info("Active provider set to: %s", provider)

    def set_model(self, model: str) -> None:
        """Set model for the active provider."""
        config = self.get_config()
        active_provider = config.active_provider
        
        if active_provider == "claude":
            # Update Claude config with new model
            if "claude" not in config.ai:
                # Create default Claude config if doesn't exist
                from .providers import get_max_tokens
                config.ai["claude"] = AIProviderConfig(
                    api_key="",  # Will need to be set separately
                    default_model=model,
                    max_tokens=get_max_tokens(),
                )
            else:
                # Update existing config
                config.ai["claude"].default_model = model
                
        # Future: add support for other providers
        # elif active_provider == "openai":
        #     config.ai["openai"].default_model = model
        
        self.save_config(config)
        self.logger.info("Model for %s set to: %s", active_provider, model)

    def get_prompt_mode(self) -> str:
        """Get the current prompt mode."""
        config = self.get_config()
        return config.prompt_mode

    def set_prompt_mode(self, mode: str) -> None:
        """Set the prompt mode."""
        config = self.get_config()
        config.prompt_mode = mode
        self.save_config(config)
        self.logger.info("Prompt mode set to: %s", mode)

    def set_active_embeddings(self, embedding_names: List[str]) -> None:
        """Set active embeddings."""
        active = ActiveEmbeddings(selected=embedding_names, last_updated=datetime.now())
        self.save_active_embeddings(active)
        self.logger.info("Active embeddings set: %s", ", ".join(embedding_names))

    def get_available_embeddings(self) -> List[EmbeddingInfo]:
        """Get list of available embeddings."""
        embeddings = []

        if not self.embeddings_dir.exists():
            return embeddings

        try:
            for embedding_file in self.embeddings_dir.glob("*.json"):
                with open(embedding_file, "r") as f:
                    data = json.load(f)
                    embedding_info = EmbeddingInfo(**data)
                    embeddings.append(embedding_info)
        except Exception as e:
            self.logger.warning("Error reading embeddings metadata: %s", e)

        return sorted(embeddings, key=lambda x: x.created_at, reverse=True)

    def save_embedding_metadata(self, embedding_info: EmbeddingInfo) -> None:
        """Save embedding metadata."""
        metadata_file = self.embeddings_dir / f"{embedding_info.name}.json"

        try:
            with open(metadata_file, "w") as f:
                json.dump(embedding_info.dict(), f, indent=2, default=str)
            self.logger.debug("Saved embedding metadata: %s", embedding_info.name)
        except Exception as e:
            raise ConfigurationError(f"Failed to save embedding metadata: {e}")

    def delete_embedding_metadata(self, embedding_name: str) -> None:
        """Delete embedding metadata."""
        metadata_file = self.embeddings_dir / f"{embedding_name}.json"

        try:
            if metadata_file.exists():
                metadata_file.unlink()
                self.logger.debug("Deleted embedding metadata: %s", embedding_name)
        except Exception as e:
            self.logger.warning("Failed to delete embedding metadata: %s", e)

    def _load_config(self) -> None:
        """Load configuration from file."""
        try:
            if not self.config_file.exists():
                self.initialize()

            with open(self.config_file, "r") as f:
                data = json.load(f)
                self._config = ContextAIConfig(**data)

        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")

    def _save_config(self, config: ContextAIConfig) -> None:
        """Save configuration to file."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, "w") as f:
                json.dump(config.dict(), f, indent=2, default=str)

        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration: {e}")

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

    def _ensure_all_configs_exist(self) -> None:
        """Ensure all configuration files exist (centralized lazy copy)."""
        try:
            import shutil
            
            config_dir = self.config_dir / "config"
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # 1. Ensure Languages configuration exists
            self.logger.debug("🌍 Ensuring languages configuration...")
            from config.languages.loader import DefaultConfigGenerator
            
            copy_result = DefaultConfigGenerator.copy_all_language_files(config_dir)
            if copy_result.has_changes:
                self.logger.info(f"Initialized {copy_result.files_copied} language configuration files")
            
            # 2. Ensure Guidelines exist - Direct copy
            self.logger.debug("📝 Ensuring guidelines configuration...")
            guidelines_dir = config_dir / "guidelines"
            if not guidelines_dir.exists() or not list(guidelines_dir.glob("*.md")):
                # Copy guidelines from samples
                current_file = Path(__file__)
                project_root = current_file.parent.parent.parent  # Go up to project root 
                samples_guidelines = project_root / "src" / "config" / "samples" / "guidelines"
                
                if samples_guidelines.exists():
                    guidelines_dir.mkdir(parents=True, exist_ok=True)
                    
                    copied_count = 0
                    for guideline_file in samples_guidelines.glob("*.md"):
                        target_file = guidelines_dir / guideline_file.name
                        if not target_file.exists():
                            shutil.copy2(guideline_file, target_file)
                            copied_count += 1
                            self.logger.debug(f"Copied guideline: {guideline_file.name}")
                    
                    if copied_count > 0:
                        self.logger.info(f"Initialized {copied_count} guideline templates")
            
            # 3. Ensure Prompt templates exist - Direct copy  
            self.logger.debug("🎯 Ensuring prompt configuration...")
            prompts_dir = config_dir / "prompts"
            if not prompts_dir.exists():
                # Copy prompts from samples
                current_file = Path(__file__)
                project_root = current_file.parent.parent.parent  # Go up to project root
                samples_prompts = project_root / "src" / "config" / "samples" / "prompts"
                
                if samples_prompts.exists():
                    self.logger.info("Creating user prompt config by copying defaults...")
                    self.logger.info(f"From: {samples_prompts}")
                    self.logger.info(f"To: {prompts_dir}")
                    
                    shutil.copytree(samples_prompts, prompts_dir)
                    self.logger.info("✅ User prompt configuration created successfully")
            
            self.logger.debug("✅ All configurations ensured")
            
        except Exception as e:
            self.logger.warning(f"Error ensuring configurations: {e}")
            # Don't raise - let the system continue with what's available


# Global settings manager instance
_settings_manager: Optional[SettingsManager] = None


def get_settings_manager() -> SettingsManager:
    """Get global settings manager instance."""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
        _settings_manager._ensure_all_configs_exist()
        _settings_manager.initialize()
    return _settings_manager
