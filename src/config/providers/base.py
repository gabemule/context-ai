"""
Provider Interfaces & Protocols for Context-AI.

This module contains base classes and protocols for AI provider implementations.
"""

from typing import Protocol, Dict, Any, List
from abc import ABC, abstractmethod

__all__ = [
    'AIProviderProtocol',
    'BaseProvider',
    'ProviderCapabilities',
]


class ProviderCapabilities:
    """Define capabilities for AI providers."""
    
    def __init__(
        self,
        supports_streaming: bool = False,
        supports_function_calling: bool = False,
        supports_vision: bool = False,
        max_context_window: int = 200000,
        max_output_tokens: int = 4000
    ):
        self.supports_streaming = supports_streaming
        self.supports_function_calling = supports_function_calling
        self.supports_vision = supports_vision
        self.max_context_window = max_context_window
        self.max_output_tokens = max_output_tokens


class AIProviderProtocol(Protocol):
    """Protocol defining the interface for AI providers."""
    
    @property
    def name(self) -> str:
        """Provider name."""
        ...
    
    @property
    def capabilities(self) -> ProviderCapabilities:
        """Provider capabilities."""
        ...
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        ...
    
    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        """Get configuration for a specific model."""
        ...


class BaseProvider(ABC):
    """Base class for AI provider implementations."""
    
    def __init__(self, provider_name: str):
        self._name = provider_name
        self._capabilities = ProviderCapabilities()
    
    @property
    def name(self) -> str:
        """Provider name."""
        return self._name
    
    @property
    def capabilities(self) -> ProviderCapabilities:
        """Provider capabilities."""
        return self._capabilities
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        pass
    
    @abstractmethod
    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        """Get configuration for a specific model."""
        pass
