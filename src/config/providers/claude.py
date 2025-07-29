"""
Claude-Specific Provider Configuration for Context-AI.

This module contains all Claude (Anthropic) provider configurations,
models, and capabilities.
"""

from typing import Dict, List, Any
from .base import BaseProvider, ProviderCapabilities

__all__ = [
    'CLAUDE_MODELS',
    'ClaudeProvider',
    'get_claude_model_config',
    'get_claude_available_models',
]


# Claude Provider Models - First item in each dict is the default
CLAUDE_MODELS = {
    # DEFAULT: Claude 4 Sonnet - High-performance reasoning
    "claude-sonnet-4": {
        "api_name": "claude-sonnet-4-20250514",
        "max_output_tokens": 64000,
        "speed": "fast",
        "description": "High-performance with exceptional reasoning",
        "context_window": 200000,
        "pricing_input": 3.0,
        "pricing_output": 15.0,
    },
    
    # Claude 3.5 models (2024) - Fast and reliable
    "claude-3-5-haiku": {
        "api_name": "claude-3-5-haiku-20241022",
        "max_output_tokens": 8192,
        "speed": "fastest",
        "description": "Blazing fast responses",
        "context_window": 200000,
        "pricing_input": 0.8,
        "pricing_output": 4.0,
    },
    "claude-3-5-sonnet": {
        "api_name": "claude-3-5-sonnet-20241022", 
        "max_output_tokens": 8192,
        "speed": "fast",
        "description": "Intelligent and capable",
        "context_window": 200000,
        "pricing_input": 3.0,
        "pricing_output": 15.0,
    },
    
    # Claude 3.7 models (2025) - Extended capabilities
    "claude-3-7-sonnet": {
        "api_name": "claude-3-7-sonnet-20250219",
        "max_output_tokens": 64000,
        "speed": "fast",
        "description": "Fast with extended thinking capability",
        "context_window": 200000,
        "pricing_input": 3.0,
        "pricing_output": 15.0,
    },
    
    # Claude 4 Opus - Most capable
    "claude-opus-4": {
        "api_name": "claude-opus-4-20250514",
        "max_output_tokens": 32000,
        "speed": "moderately_fast", 
        "description": "Most capable, highest intelligence",
        "context_window": 200000,
        "pricing_input": 15.0,  # $/MTok
        "pricing_output": 75.0,  # $/MTok
    },
}


class ClaudeProvider(BaseProvider):
    """Claude provider implementation."""
    
    def __init__(self):
        super().__init__("claude")
        self._capabilities = ProviderCapabilities(
            supports_streaming=True,
            supports_function_calling=True,
            supports_vision=True,
            max_context_window=200000,
            max_output_tokens=64000
        )
    
    def get_available_models(self) -> List[str]:
        """Get list of available Claude models."""
        return list(CLAUDE_MODELS.keys())
    
    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        """Get configuration for a specific Claude model."""
        return CLAUDE_MODELS.get(model_name, {})


# Convenience functions for backward compatibility
def get_claude_model_config(model_key: str) -> Dict[str, Any]:
    """Get configuration for a specific Claude model."""
    return CLAUDE_MODELS.get(model_key, {})


def get_claude_available_models() -> List[str]:
    """Get list of available Claude models."""
    return list(CLAUDE_MODELS.keys())
