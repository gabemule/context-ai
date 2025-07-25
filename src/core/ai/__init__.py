"""
AI integration module for Context-AI.

Provides Claude API integration and chat interface functionality.
"""

from .claude_client import ClaudeClient, ClaudeResponse, get_claude_client

__all__ = ["ClaudeClient", "ClaudeResponse", "get_claude_client"]