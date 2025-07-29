"""
Provider Registry & Management for Context-AI.

This module provides a simple registry for managing AI providers
following YAGNI principles - minimal but functional.
"""

from typing import Dict, List, Any
from .claude import CLAUDE_MODELS, ClaudeProvider

__all__ = [
    'ALL_PROVIDERS',
    'PROVIDER_NAMES',
    'DEFAULT_AI_PROVIDER',
    'DEFAULT_MODEL',
    'get_first_item',
    'get_model_config',
    'get_current_model_config',
    'get_max_tokens',
    'get_max_output_tokens',
    'get_api_name',
    'get_available_models',
    'get_available_providers',
    'get_provider_display_name',
]


def get_first_item(obj: dict) -> str:
    """Get the first key from any dictionary."""
    return next(iter(obj)) if obj else ""


# Smart default selection - automatically picks first model from active provider
ALL_PROVIDERS = {
    "claude": CLAUDE_MODELS,
    # Future providers can be added here
    # "openai": OPENAI_MODELS,  # Future
    # "gemini": GEMINI_MODELS,  # Future
}

# Map provider keys to human-readable names
PROVIDER_NAMES = {
    "claude": "Anthropic Claude",
    # "openai": "OpenAI GPT",  # Future
    # "gemini": "Google Gemini"  # Future
}

# Dynamic defaults - always use first items (YAGNI approach)
DEFAULT_AI_PROVIDER = get_first_item(ALL_PROVIDERS)
DEFAULT_MODEL = get_first_item(ALL_PROVIDERS[DEFAULT_AI_PROVIDER]) if DEFAULT_AI_PROVIDER else ""


# Model configuration functions
def get_model_config(model_key: str, provider: str = None) -> dict:
    """Get configuration for a specific model."""
    provider = provider or DEFAULT_AI_PROVIDER
    
    if provider == "claude" and model_key in CLAUDE_MODELS:
        return CLAUDE_MODELS[model_key]
    # Future: elif provider == "openai" and model_key in OPENAI_MODELS:
    #     return OPENAI_MODELS[model_key]
    return {}


def get_current_model_config() -> dict:
    """Get config for currently selected default model."""
    return get_model_config(DEFAULT_MODEL, DEFAULT_AI_PROVIDER)


# Dynamic constants based on selected model
def get_max_tokens() -> int:
    """Get context window size for current model."""
    return get_current_model_config().get("context_window", 200000)


def get_max_output_tokens() -> int:
    """Get max output tokens for current model."""
    return get_current_model_config().get("max_output_tokens", 12000)


def get_api_name() -> str:
    """Get API name for current model."""
    return get_current_model_config().get("api_name", DEFAULT_MODEL)


def get_available_models(provider: str = None) -> list[str]:
    """Get available models for a provider."""
    provider = provider or DEFAULT_AI_PROVIDER
    return list(ALL_PROVIDERS.get(provider, {}).keys())


def get_available_providers() -> list[str]:
    """Get list of available AI providers."""
    return list(ALL_PROVIDERS.keys())


def get_provider_display_name(provider: str = None) -> str:
    """Get human-readable display name for a provider."""
    provider = provider or DEFAULT_AI_PROVIDER
    return PROVIDER_NAMES.get(provider, f"{provider.title()} AI")
