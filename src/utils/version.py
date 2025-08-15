"""
Version utilities for Context-AI.

ALWAYS reads version from pyproject.toml - the single source of truth.
"""

import re
from pathlib import Path


def get_version() -> str:
    """
    Get the version from pyproject.toml.

    ALWAYS reads from pyproject.toml, whether running locally or installed.

    Returns:
        str: Version string from pyproject.toml or "development" if not found
    """
    try:
        # Find pyproject.toml starting from current file location
        current_dir = Path(__file__).resolve().parent

        # Walk up directories to find pyproject.toml
        while current_dir != current_dir.parent:
            pyproject_path = current_dir / "pyproject.toml"
            if pyproject_path.exists():
                content = pyproject_path.read_text(encoding="utf-8")
                # Look for version = "x.x.x" pattern
                match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
                break
            current_dir = current_dir.parent
    except Exception:
        pass

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
