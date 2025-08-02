"""
Provider Models for Context-AI.

Defines data structures for AI provider capabilities and configurations.
Ensures type safety and validation for provider-specific settings,
making it easy to extend support for new providers.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any

__all__ = [
    'ProviderCapabilities',
]


class ProviderCapabilities(BaseModel):
    """
    Define capabilities for AI providers using Pydantic for validation.
    
    This model ensures type safety and validation for provider capabilities,
    making it easier to extend and maintain provider configurations.
    """
    
    supports_streaming: bool = Field(
        default=False,
        description="Whether the provider supports streaming responses"
    )
    
    supports_function_calling: bool = Field(
        default=False,
        description="Whether the provider supports function calling"
    )
    
    supports_vision: bool = Field(
        default=False,
        description="Whether the provider supports vision/image processing"
    )
    
    max_context_window: int = Field(
        default=200000,
        ge=1000,
        description="Maximum context window size in tokens"
    )
    
    max_output_tokens: int = Field(
        default=4000,
        ge=100,
        description="Maximum output tokens per response"
    )
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"  # Don't allow extra fields
        schema_extra = {
            "example": {
                "supports_streaming": True,
                "supports_function_calling": False,
                "supports_vision": True,
                "max_context_window": 200000,
                "max_output_tokens": 4000
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for compatibility."""
        return self.dict()
    
    def is_streaming_supported(self) -> bool:
        """Check if streaming is supported."""
        return self.supports_streaming
    
    def is_function_calling_supported(self) -> bool:
        """Check if function calling is supported."""
        return self.supports_function_calling
    
    def is_vision_supported(self) -> bool:
        """Check if vision processing is supported."""
        return self.supports_vision
    
    def get_context_limit(self) -> int:
        """Get maximum context window size."""
        return self.max_context_window
    
    def get_output_limit(self) -> int:
        """Get maximum output tokens."""
        return self.max_output_tokens
