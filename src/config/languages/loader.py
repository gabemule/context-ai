"""
YAML Configuration Loader for Context-AI Languages.

Handles loading and parsing of language configuration files.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional

from .models import LanguagesConfig, LanguageConfig, GlobalSettings, ChunkingPriority
from utils.logging import get_logger

__all__ = [
    'YAMLConfigLoader', 
    'DefaultConfigGenerator',
    'ConfigurationError',
    'load_languages_config',
    'ensure_default_config_exists',
]


class ConfigurationError(Exception):
    """Custom exception for configuration loading errors."""
    
    def __init__(self, message: str, file_path: Optional[Path] = None, cause: Optional[Exception] = None):
        self.file_path = file_path
        self.cause = cause
        super().__init__(message)


class YAMLConfigLoader:
    """YAML configuration loader with error handling."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def load(self, file_path: Path) -> Dict[str, Any]:
        """Load and parse YAML configuration file."""
        try:
            if not file_path.exists():
                raise ConfigurationError(f"Configuration file not found: {file_path}", file_path=file_path)
            
            with file_path.open('r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            if config_data is None:
                self.logger.warning(f"Empty configuration file: {file_path}")
                return {}
            
            if not isinstance(config_data, dict):
                raise ConfigurationError(f"Configuration must be a YAML dictionary", file_path=file_path)
            
            self.logger.debug(f"Successfully loaded configuration from: {file_path}")
            return config_data
            
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML syntax: {str(e)}", file_path=file_path, cause=e)
        except (IOError, OSError) as e:
            raise ConfigurationError(f"Failed to read file: {str(e)}", file_path=file_path, cause=e)


class DefaultConfigGenerator:
    """Copy default language configuration from template."""
    
    @staticmethod
    def get_template_path() -> Path:
        """Get path to the default languages.yaml template."""
        return Path(__file__).parent / "languages.yaml"
    
    @classmethod
    def copy_default_config(cls, target_path: Path) -> None:
        """Copy default configuration to target location."""
        try:
            import shutil
            
            template_path = cls.get_template_path()
            if not template_path.exists():
                raise ConfigurationError(f"Default template not found: {template_path}")
            
            # Ensure target directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy template to target
            shutil.copy2(template_path, target_path)
            
            logger = get_logger(__name__)
            logger.info(f"Copied default configuration from {template_path} to {target_path}")
            
        except Exception as e:
            raise ConfigurationError(f"Failed to copy default configuration: {str(e)}", file_path=target_path, cause=e)


def load_languages_config(file_path: Path) -> LanguagesConfig:
    """Load and parse languages configuration from YAML file."""
    loader = YAMLConfigLoader()
    config_data = loader.load(file_path)
    
    try:
        # Convert to Pydantic model
        return LanguagesConfig(**config_data)
    except Exception as e:
        raise ConfigurationError(f"Invalid configuration structure: {str(e)}", file_path=file_path, cause=e)


def ensure_default_config_exists(file_path: Path) -> Path:
    """Ensure default configuration file exists, create if missing."""
    if not file_path.exists():
        DefaultConfigGenerator.copy_default_config(file_path)
    return file_path
