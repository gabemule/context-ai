"""
System-Wide Constants for Context-AI.

This module contains all constants related to system configuration,
exit codes, logging, and application-wide settings.
"""

__all__ = [
    "EXIT_SUCCESS",
    "EXIT_ERROR",
    "EXIT_INTERRUPTED",
    "BYTES_PER_MB",
    "CHARS_PER_TOKEN",
    "LOGGING_ENABLED",
    "LOG_LEVEL",
    "LOG_RETENTION_DAYS",
    "LOG_MAX_SIZE_MB",
    "SESSION_LOGGING_FORMAT",
    "AUTO_CLASSIFY_SESSIONS",
    "SAVE_RAW_PROMPT",
    "SAVE_RAW_RESPONSE",
]

# Exit codes
EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_INTERRUPTED = 130

# System constants
BYTES_PER_MB = 1024 * 1024
CHARS_PER_TOKEN = 4

# Session logging configuration
LOGGING_ENABLED = True
LOG_LEVEL = "complete"  # basic, complete, debug
LOG_RETENTION_DAYS = 30
LOG_MAX_SIZE_MB = 100

# Classification settings
AUTO_CLASSIFY_SESSIONS = True
SAVE_RAW_PROMPT = True
SAVE_RAW_RESPONSE = True
SESSION_LOGGING_FORMAT = "4_files"  # 4_files: session.json, prompt_sent.txt, response_received.txt, metadata.json
