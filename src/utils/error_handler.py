"""
Error handling utilities for Context-AI.

Provides decorators and utilities to eliminate error handling duplication
and ensure consistent error responses across the application.
"""

import functools
from typing import Callable, Any
from utils.logging import get_logger
from utils.exceptions import ValidationError, ConfigurationError, StorageError
from config.constants import MAX_EMBEDDING_NAME_LENGTH, EXIT_SUCCESS, EXIT_ERROR, EXIT_INTERRUPTED


def handle_command_errors(func: Callable[..., int]) -> Callable[..., int]:
    """
    Decorator to handle common command errors consistently.
    
    Args:
        func: Command handler function that returns exit code
        
    Returns:
        Wrapped function with error handling
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> int:
        logger = get_logger(func.__module__)
        
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            logger.info("\n👋 Operation cancelled by user")
            return EXIT_INTERRUPTED
        except ValidationError as e:
            logger.error("❌ Validation error: %s", e)
            return EXIT_ERROR
        except ConfigurationError as e:
            logger.error("❌ Configuration error: %s", e)
            return EXIT_ERROR
        except StorageError as e:
            logger.error("❌ Storage error: %s", e)
            return EXIT_ERROR
        except Exception as e:
            logger.error("❌ Unexpected error: %s", e)
            # Check if verbose mode is available in args
            if hasattr(args[0], 'verbose') and args[0].verbose:
                logger.exception("Full traceback:")
            else:
                logger.info("Use --verbose for full traceback")
            return EXIT_ERROR
    
    return wrapper


def validate_file_path(path: str, must_exist: bool = True, must_be_dir: bool = False) -> None:
    """
    Validate file path with consistent error messages.
    
    Args:
        path: File path to validate
        must_exist: Whether path must exist
        must_be_dir: Whether path must be a directory
        
    Raises:
        ValidationError: If validation fails
    """
    import os
    from pathlib import Path
    
    if not path or not path.strip():
        raise ValidationError("Path cannot be empty")
    
    path_obj = Path(path)
    
    if must_exist and not path_obj.exists():
        raise ValidationError(f"Path does not exist: {path}")
    
    if must_exist and must_be_dir and not path_obj.is_dir():
        raise ValidationError(f"Path is not a directory: {path}")
    
    if must_exist and not must_be_dir and path_obj.is_dir():
        raise ValidationError(f"Path is a directory, expected file: {path}")


def validate_embedding_name(name: str) -> None:
    """
    Validate embedding name with consistent rules.
    
    Args:
        name: Embedding name to validate
        
    Raises:
        ValidationError: If name is invalid
    """
    if not name or not name.strip():
        raise ValidationError("Embedding name cannot be empty")
    
    # Invalid characters for file systems
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    if any(char in name for char in invalid_chars):
        raise ValidationError(f"Embedding name contains invalid characters: {name}")
    
    # Reasonable length limit
    if len(name) > MAX_EMBEDDING_NAME_LENGTH:
        raise ValidationError(f"Embedding name too long (max {MAX_EMBEDDING_NAME_LENGTH} characters)")


def safe_import(module_name: str, package: str = None) -> Any:
    """
    Safely import a module with helpful error message.
    
    Args:
        module_name: Name of module to import
        package: Package name for relative imports
        
    Returns:
        Imported module
        
    Raises:
        ConfigurationError: If import fails
    """
    try:
        if package:
            return __import__(module_name, fromlist=[package])
        else:
            return __import__(module_name)
    except ImportError as e:
        raise ConfigurationError(f"Required module '{module_name}' not installed. "
                               f"Install with: pip install {module_name}") from e