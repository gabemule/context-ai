"""
Provider Protocols for Context-AI.

Protocol definitions for AI provider implementations.
Following Interface Segregation Principle (ISP).
"""

from typing import Protocol, Dict, Any, List
from .models import ProviderCapabilities

__all__ = [
    'AIProviderProtocol',
]


class AIProviderProtocol(Protocol):
    """
    Protocol defining the interface for AI providers.
    
    This protocol ensures that all AI provider implementations
    follow a consistent interface without requiring inheritance.
    """
    
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
