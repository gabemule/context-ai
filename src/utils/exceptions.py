"""
Custom exceptions for Context-AI.
"""


class ContextAIError(Exception):
    """Base exception for Context-AI."""


class ConfigurationError(ContextAIError):
    """Configuration related errors."""


class EmbeddingError(ContextAIError):
    """Embedding generation/query related errors."""


class StorageError(ContextAIError):
    """Storage/database related errors."""


class ValidationError(ContextAIError):
    """Input validation errors."""


class APIError(ContextAIError):
    """External API related errors."""
