"""
Validation Limits & Rules Constants for Context-AI.

This module contains all constants related to validation limits,
performance constraints, and caching configurations.
"""

__all__ = [
    "MIN_CHUNK_SIZE_LIMIT",
    "MAX_CHUNK_SIZE_LIMIT",
    "MAX_EMBEDDING_NAME_LENGTH",
    "MIN_CONTEXT_WINDOW_VALIDATION",
    "MIN_OUTPUT_TOKENS_VALIDATION",
    "QUERY_POOL_SIZE",
    "CONTEXT_DEFAULT_CHUNKS",
    "CONTEXT_PERFORMANCE_LIMIT",
    "ENABLE_TOKEN_CACHE",
    "TOKEN_CACHE_SIZE",
    "ENABLE_CONTEXT_CACHE",
    "CONTEXT_CACHE_TTL",
    "PROMPT_CONFIG_SUBDIR",
    "PROMPT_REQUIRED_FILES",
    "PROMPT_OPTIONAL_FILES",
    "PROMPT_GLOBAL_FILES",
]

# Validation constants
MIN_CHUNK_SIZE_LIMIT = 10
MAX_CHUNK_SIZE_LIMIT = 10000
MAX_EMBEDDING_NAME_LENGTH = 100

# Provider validation constants
MIN_CONTEXT_WINDOW_VALIDATION = 1000  # Minimum context window for model validation
MIN_OUTPUT_TOKENS_VALIDATION = 100  # Minimum output tokens for model validation

# Query and search defaults - clarified for specific purposes
QUERY_POOL_SIZE = 1000  # Wide search pool for vector queries (internal)
CONTEXT_DEFAULT_CHUNKS = 250  # Default chunks when user doesn't specify max_results
CONTEXT_PERFORMANCE_LIMIT = (
    500  # Performance protection limit to avoid excessive processing
)

# Performance optimization constants
ENABLE_TOKEN_CACHE = True  # Cache token calculations to avoid re-processing
TOKEN_CACHE_SIZE = 200  # Cache recent token calculations
ENABLE_CONTEXT_CACHE = True  # Cache context between chat turns
CONTEXT_CACHE_TTL = 300  # Context cache TTL in seconds

# File-based prompt system constants
PROMPT_CONFIG_SUBDIR = "config/prompt"  # Subdir in user config for prompt files
PROMPT_REQUIRED_FILES = ["mode.yaml", "core_instructions.md"]  # Required files per mode
PROMPT_OPTIONAL_FILES = [  # Optional files that may be loaded
    "cross_analysis.md",
    "final_instructions.md",
    "error_handling.md",
    "output_format.md",
    "validation_rules.md",
    "debug_info.md",
]
PROMPT_GLOBAL_FILES = ["global_instructions.md", "security_instructions.md"]
