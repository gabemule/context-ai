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
    in a single, consistent interface.
    """
    
    def __init__(self):
        """Initialize the provider registry."""
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
    
    def get_model_config(self, model_key: str, provider: str = None) -> dict:
        """Get configuration for a specific model."""
        provider = provider or self.default_provider
        
        if provider == "claude" and model_key in CLAUDE_MODELS:
            return CLAUDE_MODELS[model_key]
        # Future: elif provider == "openai" and model_key in OPENAI_MODELS:
        #     return OPENAI_MODELS[model_key]
        return {}
    
    def get_current_model_config(self) -> dict:
        """Get config for currently selected default model."""
        return self.get_model_config(self.default_model, self.default_provider)
    
    def get_max_tokens(self) -> int:
        """Get context window size for current model."""
        return self.get_current_model_config().get("context_window", 200000)
    
    def get_max_output_tokens(self) -> int:
        """Get max output tokens for current model."""
        return self.get_current_model_config().get("max_output_tokens", 12000)
    
    def get_api_name(self) -> str:
        """Get API name for current model."""
        return self.get_current_model_config().get("api_name", self.default_model)
    
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
