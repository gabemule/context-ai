"""
AI/LLM Processing Constants for Context-AI.

This module contains all constants related to AI processing, token management,
chat history, and AI provider interactions.
"""

__all__ = [
    'DEFAULT_MAX_RETRIES',
    'DEFAULT_RETRY_DELAY',
    'DEFAULT_TIMEOUT',
    'CONTEXT_TOKEN_RATIO',
    'RESPONSE_TOKEN_RATIO',
    'MIN_RESPONSE_TOKENS',
    'CHAT_HISTORY_TOKEN_RATIO',
    'CHAT_MAX_HISTORY_TURNS',
    'CHAT_MIN_HISTORY_TURNS',
    'CHAT_SUMMARY_THRESHOLD',
    'STREAMING_THRESHOLD_TOKENS',
    'DEFAULT_SYSTEM_PROMPT_STRATEGY',
]

# Static AI constants (provider-agnostic)
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0  # seconds  
DEFAULT_TIMEOUT = 60.0  # seconds
CONTEXT_TOKEN_RATIO = 0.65  # Use 65% of total capacity for context
RESPONSE_TOKEN_RATIO = 0.8  # Use 80% of remaining capacity for response
MIN_RESPONSE_TOKENS = 4000  # Minimum response tokens

# Chat history management
CHAT_HISTORY_TOKEN_RATIO = 0.3  # Use 30% of context for chat history
CHAT_MAX_HISTORY_TURNS = 10  # Maximum conversation turns to keep
CHAT_MIN_HISTORY_TURNS = 1  # Minimum turns to preserve when truncating (include from 1st turn)
CHAT_SUMMARY_THRESHOLD = 5  # After N turns, start summarizing old history

# Streaming configuration
STREAMING_THRESHOLD_TOKENS = 50000  # Use streaming for contexts larger than this

# System prompt strategy
DEFAULT_SYSTEM_PROMPT_STRATEGY = "general_assistant_with_reusability_focus"
