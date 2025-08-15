"""
AI integration module for Context-AI.

Provides Claude API integration, chat interface functionality, and file-based prompt building.
"""

from .claude_client import ClaudeClient, ClaudeResponse, get_claude_client
from .prompt_builder import PromptBuilder, get_prompt_builder

__all__ = [
    "ClaudeClient",
    "ClaudeResponse",
    "get_claude_client",
    "PromptBuilder",
    "get_prompt_builder",
]
