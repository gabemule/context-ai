"""
Configuration constants for Context-AI.
"""

# Claude API Configuration
CLAUDE_DEFAULT_MODEL = "claude-4"
CLAUDE_MAX_TOKENS = 200000

# Default file extensions supported
DEFAULT_SUPPORTED_EXTENSIONS = [
    ".py", ".js", ".ts", ".md", ".tsx", ".jsx", 
    ".css", ".json", ".yaml", ".yml", ".html",
    ".scss", ".sass", ".less", ".vue", ".svelte"
]

# Chunking defaults
DEFAULT_CHUNK_SIZE = 2000
DEFAULT_CHUNK_OVERLAP = 200

# Context assembly defaults
DEFAULT_MAX_CHUNKS = 8
DEFAULT_PRIORITIZE_CROSS_PROJECT = True
DEFAULT_INCLUDE_METADATA = True

# Storage defaults
DEFAULT_CONFIG_DIR = "~/.context-ai"
DEFAULT_MAX_EMBEDDINGS = 50
DEFAULT_CLEANUP_AFTER_DAYS = 30

# System prompt strategy
DEFAULT_SYSTEM_PROMPT_STRATEGY = "general_assistant_with_reusability_focus"