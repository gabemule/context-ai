"""
Version utilities for Context-AI.

Professional version management using importlib.metadata - industry standard approach.
Used by Click, Django, and other major Python libraries.
"""

from importlib.metadata import version, PackageNotFoundError


def get_version() -> str:
    """
    Get the version using importlib.metadata - the professional standard.
    
    This approach:
    - Works reliably in all installed environments (pipx, pip, etc)
    - Is the industry standard used by Click, Django, and other major libs
    - Reads from package metadata, not files that may not exist
    - Follows Python packaging best practices
    
    Returns:
        str: Version string from package metadata or "development" if not installed
    """
    try:
        # Try both possible package names (alpha and production)
        try:
            return version("context-ai-alpha")
        except PackageNotFoundError:
            return version("context-ai")
    except PackageNotFoundError:
        return "development"


def get_version_info() -> tuple[str, bool]:
    """
    Get version info with development flag.

    Returns:
        tuple: (version_string, is_development)
    """
    version_str = get_version()
    is_dev = version_str == "development"
    return version_str, is_dev


def format_version_display(include_name: bool = True) -> str:
    """
    Format version for display purposes.

    Args:
        include_name: Whether to include "context-ai" prefix

    Returns:
        str: Formatted version string
    """
    version_str = get_version()
    if include_name:
        return f"context-ai {version_str}"
    return version_str
