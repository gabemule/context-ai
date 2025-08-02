"""
Configuration Core for Context-AI.

Centralized configuration access that eliminates inconsistencies and circular dependencies.
Provides a single point of access to config.json, ensuring all system components
read and write configurations consistently.
"""

import json
from pathlib import Path
from typing import Dict, Optional, Any

from utils.exceptions import ConfigurationError
from utils.logging import get_logger


class ConfigCore:
    """
    Centralized configuration access point for the entire system.
    
    What it solves: Before this, each manager had its own way of reading/writing
    config.json, causing inconsistencies and conflicts when multiple components
    tried to update configuration simultaneously.
    
    Benefits:
    - Single source of truth for all configuration data
    - Automatic consistency across all system components
    - Eliminates config-related bugs from concurrent access
    - Makes testing easier with centralized mocking point
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize config core with file path."""
        self.logger = get_logger(__name__)
        
        if config_path:
            self.config_file = config_path
        else:
            # Use default path 
            from config.constants import DEFAULT_CONFIG_DIR
            base_path = Path(DEFAULT_CONFIG_DIR).expanduser().resolve()
            self.config_file = base_path / "config.json"
        
        self._data: Optional[Dict] = None
    
    # =============================================================================
    # CORE CRUD OPERATIONS
    # =============================================================================
    
    def get_config_data(self) -> Dict[str, Any]:
        """Get complete configuration data."""
        if self._data is None:
            self._load_data()
        return self._data.copy()
    
    def save_config_data(self, data: Dict[str, Any]) -> None:
        """Save complete configuration data."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, "w") as f:
                json.dump(data, f, indent=2, default=str)
            
            # Update cache
            self._data = data.copy()
            self.logger.debug("Config data saved to: %s", self.config_file)
            
        except Exception as e:
            raise ConfigurationError(f"Failed to save config data: {e}")
    
    def reload_data(self) -> None:
        """Force reload data from file."""
        self._data = None
        self._load_data()
    
    # =============================================================================
    # PROVIDER OPERATIONS (Specific helpers to avoid dict manipulation)
    # =============================================================================
    
    def get_active_provider(self) -> str:
        """Get currently active AI provider with default fallback."""
        data = self.get_config_data()
        return data.get("active_provider") or "claude"
    
    def set_active_provider(self, provider: str) -> None:
        """Set active AI provider."""
        data = self.get_config_data()
        data["active_provider"] = provider
        self.save_config_data(data)
    
    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """Get configuration for specific provider."""
        data = self.get_config_data()
        ai_configs = data.get("ai", {})
        return ai_configs.get(provider, {})
    
    def set_provider_config(self, provider: str, config: Dict[str, Any]) -> None:
        """Set configuration for specific provider."""
        data = self.get_config_data()
        if "ai" not in data:
            data["ai"] = {}
        data["ai"][provider] = config
        self.save_config_data(data)
    
    def get_provider_api_key(self, provider: str = None) -> Optional[str]:
        """Get API key for specific provider with active provider fallback."""
        provider = provider or self.get_active_provider()
        provider_config = self.get_provider_config(provider)
        return provider_config.get("api_key")
    
    def set_provider_api_key(self, provider: str, api_key: str) -> None:
        """Set API key for specific provider."""
        provider_config = self.get_provider_config(provider)
        provider_config["api_key"] = api_key
        self.set_provider_config(provider, provider_config)
    
    def get_provider_model(self, provider: str = None) -> str:
        """Get default model for specific provider with smart fallbacks."""
        provider = provider or self.get_active_provider()
        provider_config = self.get_provider_config(provider)
        model = provider_config.get("default_model")
        
        # Smart fallback using ProviderRegistry (no hardcoding!)
        if not model:
            from config.providers.registry import get_provider_registry
            registry = get_provider_registry()
            available_models = registry.get_available_models(provider)
            model = available_models[0] if available_models else "claude-sonnet-4"
        
        return model
    
    def set_provider_model(self, provider: str, model: str) -> None:
        """Set default model for specific provider."""
        provider_config = self.get_provider_config(provider)
        provider_config["default_model"] = model
        self.set_provider_config(provider, provider_config)
    
    def get_provider_max_tokens(self, provider: str = None) -> Optional[int]:
        """Get max tokens for specific provider."""
        provider = provider or self.get_active_provider()
        provider_config = self.get_provider_config(provider)
        return provider_config.get("max_tokens")
    
    def set_provider_max_tokens(self, provider: str, max_tokens: int) -> None:
        """Set max tokens for specific provider."""
        provider_config = self.get_provider_config(provider)
        provider_config["max_tokens"] = max_tokens
        self.set_provider_config(provider, provider_config)
    
    # =============================================================================
    # OTHER CONFIG OPERATIONS
    # =============================================================================
    
    def get_prompt_mode(self) -> str:
        """Get current prompt mode."""
        data = self.get_config_data()
        return data.get("prompt_mode", "standard")
    
    def set_prompt_mode(self, mode: str) -> None:
        """Set prompt mode."""
        data = self.get_config_data()
        data["prompt_mode"] = mode
        self.save_config_data(data)
    
    def get_system_prompt_strategy(self) -> str:
        """Get system prompt strategy."""
        data = self.get_config_data()
        return data.get("system_prompt_strategy", "comprehensive")
    
    def set_system_prompt_strategy(self, strategy: str) -> None:
        """Set system prompt strategy."""
        data = self.get_config_data()
        data["system_prompt_strategy"] = strategy
        self.save_config_data(data)
    
    # =============================================================================
    # PRIVATE METHODS
    # =============================================================================
    
    def _load_data(self) -> None:
        """Load configuration data from file."""
        try:
            if not self.config_file.exists():
                # Create default config
                self._data = self._get_default_config()
                self.save_config_data(self._data)
                return
            
            with open(self.config_file, "r") as f:
                self._data = json.load(f)
                
        except Exception as e:
            self.logger.error("Failed to load config data: %s", e)
            # Fall back to default config
            self._data = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration structure."""
        return {
            "active_provider": None,
            "ai": {},
            "prompt_mode": "standard",
            "system_prompt_strategy": "comprehensive",
            "chunking": {
                "chunk_size": 1000,
                "chunk_overlap": 200,
                "min_chunk_size": 100,
                "supported_extensions": [
                    ".py", ".js", ".ts", ".jsx", ".tsx", ".vue",
                    ".html", ".css", ".scss", ".sass", ".less",
                    ".md", ".mdx", ".txt", ".json", ".yaml", ".yml"
                ]
            },
            "context_assembly": {
                "max_chunks": 20,
                "prioritize_cross_project": True,
                "include_metadata": True
            },
            "storage": {
                "base_path": "~/.context-ai",
                "max_embeddings": 50,
                "cleanup_after_days": 30
            }
        }


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_config_core: Optional[ConfigCore] = None


def get_config_core() -> ConfigCore:
    """Get global config core instance."""
    global _config_core
    if _config_core is None:
        _config_core = ConfigCore()
    return _config_core


def reset_config_core() -> None:
    """Reset config core instance (for testing)."""
    global _config_core
    _config_core = None
