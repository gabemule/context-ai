"""
Logging configuration for Context-AI.
"""

import logging
import sys
from typing import Optional


def setup_logging(verbose: bool = False, log_file: Optional[str] = None) -> None:
    """
    Setup logging configuration with appropriate levels and formatting.
    
    Args:
        verbose: Enable verbose (DEBUG) logging
        log_file: Optional file path to write logs to
    """
    # Determine log level
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Always debug level for files
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set levels for external libraries to reduce noise
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('anthropic').setLevel(logging.WARNING)
    logging.getLogger('chromadb').setLevel(logging.WARNING)
    logging.getLogger('sentence_transformers').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Convenience functions for different log levels
def log_info(message: str, logger_name: str = "context-ai") -> None:
    """Log info message."""
    logger = get_logger(logger_name)
    logger.info(message)


def log_debug(message: str, logger_name: str = "context-ai") -> None:
    """Log debug message."""
    logger = get_logger(logger_name)
    logger.debug(message)


def log_warning(message: str, logger_name: str = "context-ai") -> None:
    """Log warning message."""
    logger = get_logger(logger_name)
    logger.warning(message)


def log_error(message: str, logger_name: str = "context-ai") -> None:
    """Log error message."""
    logger = get_logger(logger_name)
    logger.error(message)


def log_exception(message: str, logger_name: str = "context-ai") -> None:
    """Log exception with traceback."""
    logger = get_logger(logger_name)
    logger.exception(message)