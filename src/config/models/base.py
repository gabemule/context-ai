"""
Base Models & Common Utilities for Context-AI.

This module contains base Pydantic models and common utilities
used across different domain-specific models.
"""

from datetime import datetime
from typing import Dict, Any

from pydantic import BaseModel

__all__ = [
    'TimestampedModel',
    'ConfigurableModel',
]


class TimestampedModel(BaseModel):
    """Base model with timestamp tracking."""
    
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    
    class Config:
        """Pydantic config for timestamped models."""
        json_encoders = {datetime: lambda v: v.isoformat()}


class ConfigurableModel(BaseModel):
    """Base model for configuration objects."""
    
    class Config:
        """Pydantic config for configuration models."""
        json_encoders = {datetime: lambda v: v.isoformat()}
        extra = "forbid"  # Prevent extra fields
        validate_assignment = True  # Validate on assignment
