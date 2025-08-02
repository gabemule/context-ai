"""
Provider Registry & Management for Context-AI.

This module provides a centralized registry for managing AI providers
following the same class-based pattern as other managers.
"""

from typing import Dict, List, Optional
from .claude import CLAUDE_MODELS

__all__ = [
    'ProviderRegistry',
    'get_provider_registry',
]


class ProviderRegistry:
    """
    Centralized provider registry following the same pattern as other managers.
    
    Manages all AI provider configurations, models, and capabilities
    in a single, consistent interface. Uses ConfigCore to avoid circular dependencies.
    """
    
    def __init__(self, config_core=None):
        """Initialize the provider registry."""
        # Dependency injection for ConfigCore (eliminates circular dependency)
        if config_core is not None:
            self.config_core = config_core
        else:
            from config.core import get_config_core
            self.config_core = get_config_core()
        
        # Smart default selection - automatically picks first model from active provider
        self.providers = {
            "claude": CLAUDE_MODELS,
            # Future providers can be added here
            # "openai": OPENAI_MODELS,  # Future
            # "gemini": GEMINI_MODELS,  # Future
        }
        
        # Map provider keys to human-readable names
        self.provider_names = {
            "claude": "Anthropic Claude",
            # "openai": "OpenAI GPT",  # Future
            # "gemini": "Google Gemini"  # Future
        }
        
        # Dynamic defaults - always use first items (YAGNI approach)
        self.default_provider = self._get_first_item(self.providers)
        self.default_model = self._get_first_item(self.providers[self.default_provider]) if self.default_provider else ""
    
    def _get_first_item(self, obj: dict) -> str:
        """Get the first key from any dictionary."""
        return next(iter(obj)) if obj else ""
    
    def _get_current_provider_and_model(self) -> tuple[str, str]:
        """Get current provider and model from user configuration via ConfigCore."""
        try:
            # Use ConfigCore to get current config (no circular dependency!)
            active_provider = self.config_core.get_active_provider()
            active_model = self.config_core.get_provider_model(active_provider)
            return active_provider, active_model
            
        except Exception:
            # Fallback to defaults if config unavailable
            return self.default_provider, self.default_model
    
    def get_model_config(self, model_key: str, provider: str = None) -> dict:
        """Get configuration for a specific model (no hardcoding!)."""
        provider = provider or self.default_provider
        
        # Use centralized providers dict (eliminates hardcoded ifs)
        provider_models = self.providers.get(provider, {})
        return provider_models.get(model_key, {})
    
    def get_current_model_config(self) -> dict:
        """Get config for currently active model from user config."""
        provider, model = self._get_current_provider_and_model()
        return self.get_model_config(model, provider)
    
    def get_max_tokens(self) -> int:
        """Get context window size for current active model from user config."""
        provider, model = self._get_current_provider_and_model()
        model_config = self.get_model_config(model, provider)
        return model_config.get("context_window", 200000)
    
    def get_max_output_tokens(self) -> int:
        """Get max output tokens for current active model from user config."""
        provider, model = self._get_current_provider_and_model()
        model_config = self.get_model_config(model, provider)
        return model_config.get("max_output_tokens", 12000)
    
    def get_api_name(self) -> str:
        """Get API name for current active model from user config."""
        provider, model = self._get_current_provider_and_model()
        model_config = self.get_model_config(model, provider)
        return model_config.get("api_name", model)
    
    def get_available_models(self, provider: str = None) -> List[str]:
        """Get available models for a provider."""
        provider = provider or self.default_provider
        return list(self.providers.get(provider, {}).keys())
    
    def get_available_providers(self) -> List[str]:
        """Get list of available AI providers."""
        return list(self.providers.keys())
    
    def get_provider_display_name(self, provider: str = None) -> str:
        """Get human-readable display name for a provider."""
        provider = provider or self.default_provider
        return self.provider_names.get(provider, f"{provider.title()} AI")


# Global provider registry instance
_provider_registry: Optional[ProviderRegistry] = None


def get_provider_registry() -> ProviderRegistry:
    """Get global provider registry instance."""
    global _provider_registry
    if _provider_registry is None:
        _provider_registry = ProviderRegistry()
    return _provider_registry
