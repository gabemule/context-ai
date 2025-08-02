"""
Languages Configuration Loader for Context-AI.

Handles loading, parsing, and copying of language configuration files.
Provides robust file operations with error handling and supports both
loading existing configurations and setting up default templates.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional, List, Protocol

from .models import LanguagesConfig, LanguageConfig, GlobalSettings, ChunkingPriority
from utils.file_operations import get_file_operations, FileSystemOperations as GenericFileSystemOperations
from utils.yaml_loader import get_yaml_loader
from utils.logging import get_logger

__all__ = [
    'YAMLConfigLoader', 
    'DefaultConfigGenerator',
    'ConfigurationError',
    'CopyResult',
    'FileOperations',
    'ConfigurationCopier',
    'LanguageConfigurationCopier',
    'load_languages_config',
    'ensure_default_config_exists',
]


class ConfigurationError(Exception):
    """Custom exception for configuration loading errors."""
    
    def __init__(self, message: str, file_path: Optional[Path] = None, cause: Optional[Exception] = None):
        self.file_path = file_path
        self.cause = cause
        super().__init__(message)


@dataclass(frozen=True)
class CopyResult:
    """Immutable result of a copy operation."""
    
    files_copied: int
    files_skipped: int
    errors: List[str]
    
    @property
    def total_files_processed(self) -> int:
        """Total number of files that were processed."""
        return self.files_copied + self.files_skipped
    
    @property
    def success(self) -> bool:
        """Whether the operation was successful."""
        return len(self.errors) == 0
    
    @property
    def has_changes(self) -> bool:
        """Whether any files were actually copied."""
        return self.files_copied > 0


class FileOperations(Protocol):
    """Protocol defining file operations interface (ISP)."""
    
    def copy_file(self, source: Path, target: Path) -> bool:
        """Copy a single file from source to target."""
        ...
    
    def list_files(self, directory: Path, pattern: str) -> List[Path]:
        """List files in directory matching pattern."""
        ...
    
    def ensure_directory_exists(self, directory: Path) -> None:
        """Ensure directory exists, creating if necessary."""
        ...


class FileSystemOperations:
    """Adapter for generic file operations (Adapter Pattern)."""
    
    def __init__(self, logger: Optional[Any] = None):
        self.logger = logger or get_logger(__name__)
        self.generic_ops = get_file_operations()
    
    def copy_file(self, source: Path, target: Path) -> bool:
        """Copy file using generic file operations."""
        if target.exists():
            self.logger.debug(f"Target file already exists, skipping: {target.name}")
            return False
        
        success = self.generic_ops.copy_file(source, target)
        if success:
            self.logger.info(f"Successfully copied: {source.name} -> {target}")
        return success
    
    def list_files(self, directory: Path, pattern: str) -> List[Path]:
        """List files using generic file operations."""
        return self.generic_ops.list_files(directory, pattern)
    
    def ensure_directory_exists(self, directory: Path) -> None:
        """Ensure directory exists using generic file operations."""
        success = self.generic_ops.ensure_directory_exists(directory)
        if not success:
            raise ConfigurationError(f"Could not create directory: {directory}")


class ConfigurationCopier(ABC):
    """Abstract base class for configuration copying (OCP + DIP)."""
    
    def __init__(self, file_ops: FileOperations):
        self.file_ops = file_ops
        self.logger = get_logger(self.__class__.__name__)
    
    @abstractmethod
    def get_files_to_copy(self) -> List[str]:
        """Get list of files that should be copied."""
        ...
    
    @abstractmethod
    def get_source_directory(self) -> Path:
        """Get the source directory containing templates."""
        ...
    
    def copy_configuration_files(self, target_directory: Path) -> CopyResult:
        """
        Copy configuration files to target directory.
        
        Template method implementing common copy logic (DRY).
        """
        try:
            self.file_ops.ensure_directory_exists(target_directory)
            
            source_directory = self.get_source_directory()
            files_to_copy = self.get_files_to_copy()
            
            files_copied = 0
            files_skipped = 0
            errors = []
            
            for filename in files_to_copy:
                source_file = source_directory / filename
                target_file = target_directory / filename
                
                if not source_file.exists():
                    error_msg = f"Template file not found: {filename}"
                    self.logger.warning(error_msg)
                    errors.append(error_msg)
                    continue
                
                if target_file.exists():
                    files_skipped += 1
                    continue
                
                if self.file_ops.copy_file(source_file, target_file):
                    files_copied += 1
                else:
                    error_msg = f"Failed to copy: {filename}"
                    errors.append(error_msg)
            
            result = CopyResult(
                files_copied=files_copied,
                files_skipped=files_skipped,
                errors=errors
            )
            
            self._log_copy_result(result)
            return result
            
        except Exception as e:
            error_msg = f"Configuration copy operation failed: {str(e)}"
            self.logger.error(error_msg)
            return CopyResult(
                files_copied=0,
                files_skipped=0,
                errors=[error_msg]
            )
    
    def _log_copy_result(self, result: CopyResult) -> None:
        """Log the results of copy operation."""
        if result.has_changes:
            self.logger.info(f"Copied {result.files_copied} configuration files")
        
        if result.files_skipped > 0:
            self.logger.debug(f"Skipped {result.files_skipped} existing files")
        
        if not result.success:
            self.logger.warning(f"Copy completed with {len(result.errors)} errors")


class LanguageConfigurationCopier(ConfigurationCopier):
    """
    Concrete implementation for copying language configuration files (SRP).
    
    Handles copying of languages.yaml and associated documentation.
    """
    
    def get_files_to_copy(self) -> List[str]:
        """
        Get list of language configuration files to copy.
        
        Returns:
            List of filenames that constitute the language configuration
        """
        return [
            "languages.yaml",         # Primary configuration file
            "languages-README.md"     # User documentation and guide
        ]
    
    def get_source_directory(self) -> Path:
        """Get the source directory containing language templates."""
        # Point to samples/ instead of current directory
        current_file = Path(__file__)
        config_dir = current_file.parent.parent  # Go up to src/config/
        return config_dir / "samples"


class YAMLConfigLoader:
    """YAML configuration loader using generic YAML utilities (Adapter Pattern)."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.generic_yaml = get_yaml_loader()
    
    def load(self, file_path: Path) -> Dict[str, Any]:
        """Load and parse YAML configuration file using generic loader."""
        if not file_path.exists():
            raise ConfigurationError(f"Configuration file not found: {file_path}", file_path=file_path)
        
        config_data = self.generic_yaml.load(file_path)
        
        if config_data is None:
            raise ConfigurationError(f"Failed to load YAML configuration", file_path=file_path)
        
        if not isinstance(config_data, dict):
            raise ConfigurationError(f"Configuration must be a YAML dictionary", file_path=file_path)
        
        self.logger.debug(f"Successfully loaded configuration from: {file_path}")
        return config_data


class DefaultConfigGenerator:
    """
    Legacy configuration generator for backward compatibility (OCP).
    
    Maintains existing API while delegating to new architecture.
    """
    
    @staticmethod
    def get_template_path() -> Path:
        """Get path to the default languages.yaml template."""
        return Path(__file__).parent / "languages.yaml"
    
    @classmethod
    def copy_default_config(cls, target_path: Path) -> None:
        """
        Copy default configuration to target location.
        
        Legacy method maintained for backward compatibility.
        """
        try:
            template_path = cls.get_template_path()
            if not template_path.exists():
                raise ConfigurationError(f"Default template not found: {template_path}")
            
            # Use generic file operations
            file_ops = get_file_operations()
            success = file_ops.copy_file(template_path, target_path)
            
            if not success:
                raise ConfigurationError(f"Failed to copy template file")
            
            logger = get_logger(__name__)
            logger.info(f"Copied default configuration from {template_path} to {target_path}")
            
        except Exception as e:
            raise ConfigurationError(f"Failed to copy default configuration: {str(e)}", file_path=target_path, cause=e)
    
    @classmethod
    def copy_all_language_files(cls, target_directory: Path) -> CopyResult:
        """
        Copy all language-related files to target directory.
        
        New method using SOLID architecture for comprehensive file copying.
        """
        file_operations = FileSystemOperations()
        configuration_copier = LanguageConfigurationCopier(file_operations)
        
        return configuration_copier.copy_configuration_files(target_directory)


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
    """
    Ensure default configuration file exists, create if missing.
    
    Legacy function maintained for backward compatibility.
    For new code, use DefaultConfigGenerator.copy_all_language_files()
    """
    if not file_path.exists():
        DefaultConfigGenerator.copy_default_config(file_path)
    return file_path
