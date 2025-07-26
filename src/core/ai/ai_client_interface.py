"""
AI Client Interface for Context-AI.

Defines the common interface that all AI providers must implement,
enabling seamless switching between different AI services (Claude, OpenAI, etc.).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class AIResponse:
    """
    Standardized response from any AI provider.

    This abstracts away provider-specific response formats, allowing
    the rest of the system to work with any AI service consistently.
    """

    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: Optional[str] = None
    provider: str = "unknown"

    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary for serialization."""
        return {
            "content": self.content,
            "model": self.model,
            "usage": self.usage,
            "finish_reason": self.finish_reason,
            "provider": self.provider,
        }


class AIClientInterface(ABC):
    """
    Abstract base class for all AI clients.

    This interface ensures all AI providers implement the same methods,
    making them interchangeable throughout the application.
    """

    @abstractmethod
    def __init__(self, api_key: str, default_model: str, **kwargs):
        """
        Initialize the AI client.

        Args:
            api_key: API key for the AI service
            default_model: Default model to use
            **kwargs: Provider-specific configuration options
        """

    @abstractmethod
    def validate_connection(self) -> bool:
        """
        Test API key validity and connection.

        Returns:
            True if connection is valid, False otherwise
        """

    @abstractmethod
    def ask(
        self,
        question: str,
        context: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        **provider_kwargs,
    ) -> AIResponse:
        """
        Ask the AI a question with optional context.

        Args:
            question: User question
            context: Optional context to include
            model: Override default model
            max_tokens: Maximum tokens to generate
            **provider_kwargs: Provider-specific parameters

        Returns:
            Standardized AIResponse object
        """

    @abstractmethod
    def get_available_models(self) -> list[str]:
        """
        Get list of available models for this provider.

        Returns:
            List of model names/IDs
        """

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of this AI provider.

        Returns:
            Provider name (e.g., "claude", "openai", "ollama")
        """

    def get_model_info(self, model: str) -> Dict[str, any]:
        """
        Get information about a specific model.

        Args:
            model: Model name/ID

        Returns:
            Dictionary with model information (optional to implement)
        """
        return {
            "name": model,
            "provider": self.get_provider_name(),
            "details": "No additional information available",
        }

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text (optional to implement).

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        # Simple fallback estimation
        return len(text.split()) * 1.3  # Rough approximation


class AIClientFactory:
    """
    Factory for creating AI clients based on provider name.

    This allows the application to switch between AI providers
    dynamically based on configuration.
    """

    _registry = {}  # Registry of available providers

    @classmethod
    def register_provider(cls, name: str, client_class: type):
        """
        Register an AI client provider.

        Args:
            name: Provider name (e.g., "claude", "openai")
            client_class: Class implementing AIClientInterface
        """
        if not issubclass(client_class, AIClientInterface):
            raise TypeError(f"Client class must implement AIClientInterface")

        cls._registry[name.lower()] = client_class

    @classmethod
    def create_client(
        self, provider: str, api_key: str, default_model: str = None, **kwargs
    ) -> AIClientInterface:
        """
        Create an AI client for the specified provider.

        Args:
            provider: Provider name (e.g., "claude", "openai")
            api_key: API key for the provider
            default_model: Default model to use
            **kwargs: Provider-specific configuration

        Returns:
            Configured AI client instance

        Raises:
            ValueError: If provider is not registered
        """
        provider_lower = provider.lower()

        if provider_lower not in cls._registry:
            available = ", ".join(cls._registry.keys())
            raise ValueError(
                f"Unknown AI provider: {provider}. " f"Available providers: {available}"
            )

        client_class = cls._registry[provider_lower]
        return client_class(api_key=api_key, default_model=default_model, **kwargs)

    @classmethod
    def get_available_providers(cls) -> list[str]:
        """
        Get list of registered AI providers.

        Returns:
            List of provider names
        """
        return list(cls._registry.keys())

    @classmethod
    def is_provider_available(cls, provider: str) -> bool:
        """
        Check if a provider is registered and available.

        Args:
            provider: Provider name to check

        Returns:
            True if provider is available
        """
        return provider.lower() in cls._registry
