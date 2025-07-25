"""
Custom exceptions for Context-AI.
"""


class ContextAIError(Exception):
    """Base exception for Context-AI."""
    pass


class ConfigurationError(ContextAIError):
    """Configuration related errors."""
    pass


class EmbeddingError(ContextAIError):
    """Embedding generation/query related errors."""
    pass


class StorageError(ContextAIError):
    """Storage/database related errors.""" 
    pass


class ValidationError(ContextAIError):
    """Input validation errors."""
    pass


class APIError(ContextAIError):
    """External API related errors."""
    pass