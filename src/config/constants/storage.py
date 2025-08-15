"""
Storage & File Handling Constants for Context-AI.

This module contains all constants related to storage, file management,
ignore patterns, and file system operations.
"""

from .system import BYTES_PER_MB

__all__ = [
    "DEFAULT_CONFIG_DIR",
    "DEFAULT_MAX_EMBEDDINGS",
    "DEFAULT_CLEANUP_AFTER_DAYS",
    "MAX_FILE_SIZE_MB",
    "MAX_FILE_SIZE_BYTES",
    "DEFAULT_IGNORE_PATTERNS",
    "CONTEXTIGNORE_FILENAME",
    "GITIGNORE_FILENAME",
    "SAMPLE_CONTEXTIGNORE_CONTENT",
]

# Storage defaults
DEFAULT_CONFIG_DIR = "~/.context-ai"
DEFAULT_MAX_EMBEDDINGS = 50
DEFAULT_CLEANUP_AFTER_DAYS = 30

# File size constants
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * BYTES_PER_MB

# Ignore file names
CONTEXTIGNORE_FILENAME = ".contextignore"
GITIGNORE_FILENAME = ".gitignore"

# Default ignore patterns for Context-AI
DEFAULT_IGNORE_PATTERNS = [
    # Version control
    ".git/",
    ".svn/",
    ".hg/",
    # Dependencies
    "node_modules/",
    "__pycache__/",
    ".venv/",
    "venv/",
    "env/",
    ".env/",
    "vendor/",
    # Build artifacts
    "dist/",
    "build/",
    "target/",
    "out/",
    ".next/",
    ".nuxt/",
    "coverage/",
    # IDE and editors
    ".vscode/",
    ".idea/",
    "*.swp",
    "*.swo",
    "*~",
    ".DS_Store",
    "Thumbs.db",
    # Logs and temporary files
    "*.log",
    "*.tmp",
    "*.temp",
    ".cache/",
    "tmp/",
    "temp/",
    # Compiled and minified files
    "*.min.js",
    "*.min.css",
    "*.bundle.js",
    "*.bundle.css",
    "*.map",
    # Environment and config
    ".env*",
    "*.key",
    "*.pem",
    "*.crt",
    # Large binary files
    "*.zip",
    "*.tar",
    "*.tar.gz",
    "*.rar",
    "*.7z",
    "*.exe",
    "*.dll",
    "*.so",
    "*.dylib",
    "*.bin",
    "*.img",
    "*.iso",
]

# Sample .contextignore content
SAMPLE_CONTEXTIGNORE_CONTENT = """
# Context-AI ignore patterns
# This file follows .gitignore syntax
# Lines starting with # are comments
# Use ! to negate patterns

# Dependencies and modules
node_modules/
__pycache__/
.venv/
vendor/

# Build artifacts
dist/
build/
target/
*.min.js
*.bundle.*

# IDE and editor files
.vscode/
.idea/
*.swp
.DS_Store

# Logs and temporary files
*.log
.cache/
tmp/

# Environment files (may contain secrets)
.env*
*.key
*.pem

# Large binary files
*.zip
*.tar.gz
*.exe
*.dll
*.so

# Include important config files
!important-config.json
!docs/*.md
"""
