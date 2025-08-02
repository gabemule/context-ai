"""
Configuration module for Context-AI.

Central configuration management for the application.
"""

from .guidelines import get_guidelines_manager, GuidelinesManager
from .languages.manager import get_languages_manager, LanguagesManager
from .settings import get_settings_manager, SettingsManager
from .storage import get_storage_manager, StorageManager

__all__ = [
    'get_guidelines_manager',
    'GuidelinesManager',
    'get_languages_manager',
    'LanguagesManager',
    'get_settings_manager',
    'SettingsManager', 
    'get_storage_manager',
    'StorageManager',
]
