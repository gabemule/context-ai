"""
Languages Manager for Context-AI.

Central manager for language configurations, providing dynamic language detection
and configuration management with caching and hot reload capabilities.
"""

from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from functools import lru_cache

from .models import LanguagesConfig, ResolvedLanguageConfig, ChunkingPriority
from .loader import load_languages_config, ensure_default_config_exists, ConfigurationError
from utils.logging import get_logger

__all__ = [
    'LanguagesManager',
    'get_languages_manager',
]


class LanguagesManager:
    """
    Central manager for language configurations.
    
    Provides dynamic language detection, configuration loading, caching,
    and APIs for accessing language-specific data.
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize Languages Manager.
        
        Args:
            config_dir: Directory containing configuration files (defaults to ~/.context-ai/config)
        """
        self.logger = get_logger(__name__)
        
        # Set up configuration paths
        if config_dir is None:
            from config.constants.storage import DEFAULT_CONFIG_DIR
            config_dir = Path(DEFAULT_CONFIG_DIR).expanduser() / "config"
        
        self.config_dir = Path(config_dir)
        self.languages_file = self.config_dir / "languages.yaml"
        
        # Internal state
        self._config: Optional[LanguagesConfig] = None
        self._resolved_languages: Optional[Dict[str, ResolvedLanguageConfig]] = None
        self._cache_valid = False
        
        # Initialize configuration
        self._ensure_config_exists()
    
    def _ensure_config_exists(self) -> None:
        """Ensure configuration files exist, create defaults if missing."""
        try:
            # Use new SOLID architecture for comprehensive file copying
            from .loader import DefaultConfigGenerator
            
            # Ensure the directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy all language-related files (languages.yaml + README.md)
            copy_result = DefaultConfigGenerator.copy_all_language_files(self.config_dir)
            
            if copy_result.has_changes:
                self.logger.info(
                    f"Initialized {copy_result.files_copied} language configuration files: "
                    f"languages.yaml, README.md"
                )
            
            if not copy_result.success and copy_result.errors:
                error_details = "; ".join(copy_result.errors)
                self.logger.warning(f"Configuration initialization completed with warnings: {error_details}")
            
            # Verify that at least the main configuration file exists
            if not self.languages_file.exists():
                raise ConfigurationError(f"Languages configuration file was not created: {self.languages_file}")
                
        except ConfigurationError as e:
            self.logger.error(f"Failed to ensure configuration exists: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during configuration initialization: {e}")
            raise ConfigurationError(f"Configuration initialization failed: {str(e)}")
    
    def _load_config(self, force_reload: bool = False) -> LanguagesConfig:
        """Load configuration from file with caching."""
        if self._config is None or force_reload or not self._cache_valid:
            try:
                self.logger.debug(f"Loading languages configuration from: {self.languages_file}")
                self._config = load_languages_config(self.languages_file)
                self._resolved_languages = None  # Clear resolved cache
                self._cache_valid = True
                self.logger.debug(f"Loaded {len(self._config.languages)} languages")
            except ConfigurationError as e:
                self.logger.error(f"Failed to load configuration: {e}")
                raise
        
        return self._config
    
    def _get_resolved_languages(self, force_reload: bool = False) -> Dict[str, ResolvedLanguageConfig]:
        """Get resolved language configurations with inheritance."""
        if self._resolved_languages is None or force_reload:
            config = self._load_config(force_reload)
            try:
                self._resolved_languages = config.resolve_inheritance()
                self.logger.debug(f"Resolved {len(self._resolved_languages)} language configurations")
            except Exception as e:
                self.logger.error(f"Failed to resolve inheritance: {e}")
                raise ConfigurationError(f"Inheritance resolution failed: {str(e)}")
        
        return self._resolved_languages
    
    def reload_config(self) -> None:
        """Reload configuration from disk."""
        self.logger.info("Reloading languages configuration")
        self._load_config(force_reload=True)
        self._get_resolved_languages(force_reload=True)
    
    # Public API Methods
    
    def get_supported_extensions(self) -> Set[str]:
        """Get all supported file extensions across all languages."""
        resolved = self._get_resolved_languages()
        extensions = set()
        
        for lang_config in resolved.values():
            extensions.update(lang_config.extensions)
        
        return extensions
    
    def get_extension_to_language(self) -> Dict[str, str]:
        """Get mapping from file extension to language name."""
        resolved = self._get_resolved_languages()
        mapping = {}
        
        for lang_name, lang_config in resolved.items():
            for ext in lang_config.extensions:
                mapping[ext] = lang_name
        
        return mapping
    
    def get_language_separators(self, language: str) -> List[str]:
        """Get text separators for a specific language."""
        resolved = self._get_resolved_languages()
        
        if language not in resolved:
            self.logger.warning(f"Language '{language}' not found, using default separators")
            return ["\n\n", "\n", " ", ""]
        
        return resolved[language].separators
    
    def get_all_separators(self) -> Dict[str, List[str]]:
        """Get all language separators as a dictionary."""
        resolved = self._get_resolved_languages()
        return {name: config.separators for name, config in resolved.items()}
    
    def get_guidelines_languages(self) -> List[str]:
        """Get list of languages that have guidelines available."""
        # Use the GuidelinesManager to get available guidelines
        # This will trigger the copy process if needed
        try:
            from config.guidelines.manager import get_guidelines_manager
            guidelines_manager = get_guidelines_manager()
            return guidelines_manager.get_available_languages()
        except Exception as e:
            self.logger.warning(f"Failed to get guidelines languages: {e}")
            return []
    
    def get_language_config(self, language: str) -> Optional[ResolvedLanguageConfig]:
        """Get resolved configuration for a specific language."""
        resolved = self._get_resolved_languages()
        return resolved.get(language)
    
    def get_all_languages(self) -> Dict[str, ResolvedLanguageConfig]:
        """Get all resolved language configurations."""
        return self._get_resolved_languages().copy()
    
    def get_language_names(self) -> List[str]:
        """Get list of all available language names."""
        resolved = self._get_resolved_languages()
        return sorted(resolved.keys())
    
    def has_language(self, language: str) -> bool:
        """Check if a language is supported."""
        resolved = self._get_resolved_languages()
        return language in resolved
    
    def detect_language_from_extension(self, extension: str) -> Optional[str]:
        """Detect language from file extension."""
        if not extension.startswith('.'):
            extension = f'.{extension}'
        
        mapping = self.get_extension_to_language()
        return mapping.get(extension.lower())
    
    def get_languages_by_priority(self, priority: str) -> List[str]:
        """Get languages filtered by chunking priority."""
        resolved = self._get_resolved_languages()
        
        return [
            name for name, config in resolved.items()
            if config.chunking_priority == priority.lower()
        ]
    
    def get_high_priority_languages(self) -> List[str]:
        """Get languages with high chunking priority."""
        return self.get_languages_by_priority(ChunkingPriority.HIGH)
    
    def get_config_file_path(self) -> Path:
        """Get path to the configuration file."""
        return self.languages_file
    
    def get_config_info(self) -> Dict[str, Any]:
        """Get information about the current configuration."""
        config = self._load_config()
        resolved = self._get_resolved_languages()
        
        return {
            "config_file": str(self.languages_file),
            "total_languages": len(config.languages),
            "resolved_languages": len(resolved),
            "settings": config.settings.dict(),
            "extensions_count": len(self.get_supported_extensions()),
            "guidelines_available": len(self.get_guidelines_languages()),
        }
    
    def reset_language_to_default(self, language: str) -> bool:
        """Reset specific language configuration to default template."""
        try:
            # Get the source template file
            template_file = Path(__file__).parent / "languages.yaml"
            
            if not template_file.exists():
                self.logger.error(f"Template file not found: {template_file}")
                return False
            
            # Load current config and template
            current_config = self._load_config()
            template_config = load_languages_config(template_file)
            
            # Check if language exists in template
            if language not in template_config.languages:
                self.logger.error(f"Language '{language}' not found in template")
                return False
            
            # Replace the language in current config with template version
            current_config.languages[language] = template_config.languages[language]
            
            # Save updated config
            import yaml
            with open(self.languages_file, 'w', encoding='utf-8') as f:
                # Convert to dict for YAML serialization
                config_dict = {
                    "languages": {name: lang.dict(exclude_unset=True) for name, lang in current_config.languages.items()},
                    "settings": current_config.settings.dict()
                }
                yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
            
            # Reload config
            self.reload_config()
            
            self.logger.info(f"Reset language '{language}' to default configuration")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reset language '{language}': {e}")
            return False


# Global instance management
_languages_manager: Optional[LanguagesManager] = None


def get_languages_manager(config_dir: Optional[Path] = None) -> LanguagesManager:
    """
    Get the global LanguagesManager instance.
    
    Args:
        config_dir: Optional config directory (only used on first call)
        
    Returns:
        Global LanguagesManager instance
    """
    global _languages_manager
    
    if _languages_manager is None:
        _languages_manager = LanguagesManager(config_dir=config_dir)
    
    return _languages_manager


def reset_languages_manager() -> None:
    """Reset the global LanguagesManager instance (for testing)."""
    global _languages_manager
    _languages_manager = None
