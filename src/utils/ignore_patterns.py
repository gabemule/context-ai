"""
Ignore file pattern matching for Context-AI.

Supports .contextignore and .gitignore pattern syntax for filtering
files during embedding generation. Provides intelligent fallback
from .contextignore to .gitignore with sensible defaults.
"""

import fnmatch
from pathlib import Path
from typing import List, Optional, Tuple

from config.constants import (
    CONTEXTIGNORE_FILENAME,
    DEFAULT_IGNORE_PATTERNS,
    GITIGNORE_FILENAME,
    MAX_FILE_SIZE_BYTES,
    SAMPLE_CONTEXTIGNORE_CONTENT,
)
from config.languages.registry import get_languages_registry
from utils.logging import get_logger


class IgnorePatternMatcher:
    """
    Handles pattern matching for ignore files using gitignore-style syntax.

    Supports:
    - Glob patterns (*.log, node_modules/, etc.)
    - Directory patterns (dir/, **/cache/)
    - Negation patterns (!important.log)
    - Comments (# this is a comment)
    """

    def __init__(self, patterns: List[str], base_path: Path):
        """
        Initialize pattern matcher.

        Args:
            patterns: List of ignore patterns
            base_path: Base directory path for relative pattern matching
        """
        self.logger = get_logger(__name__)
        self.base_path = base_path.resolve()
        self.patterns = []
        self.negation_patterns = []

        self._parse_patterns(patterns)

    def _parse_patterns(self, raw_patterns: List[str]) -> None:
        """Parse and categorize patterns."""
        for pattern in raw_patterns:
            pattern = pattern.strip()

            # Skip empty lines and comments
            if not pattern or pattern.startswith("#"):
                continue

            # Handle negation patterns
            if pattern.startswith("!"):
                self.negation_patterns.append(self._normalize_pattern(pattern[1:]))
            else:
                self.patterns.append(self._normalize_pattern(pattern))

    def _normalize_pattern(self, pattern: str) -> str:
        """
        Normalize pattern for consistent matching.

        Args:
            pattern: Raw pattern string

        Returns:
            Normalized pattern
        """
        # Remove leading slash for relative matching
        if pattern.startswith("/"):
            pattern = pattern[1:]

        # Ensure directory patterns end with /
        if pattern.endswith("/"):
            pattern = pattern.rstrip("/") + "/**"

        # Handle ** patterns
        pattern = pattern.replace("**/", "*/")

        return pattern

    def should_ignore(self, file_path: Path) -> bool:
        """
        Check if a file should be ignored based on patterns.

        Args:
            file_path: Path to check (can be relative or absolute)

        Returns:
            True if file should be ignored
        """
        try:
            # Convert to relative path from base
            if file_path.is_absolute():
                try:
                    relative_path = file_path.relative_to(self.base_path)
                except ValueError:
                    # File is outside base path, don't ignore
                    return False
            else:
                relative_path = file_path

            path_str = str(relative_path).replace("\\", "/")

            # Check if any ignore patterns match
            is_ignored = False
            for pattern in self.patterns:
                if self._match_pattern(pattern, path_str, file_path):
                    is_ignored = True
                    break

            # Check negation patterns (override ignore)
            if is_ignored:
                for neg_pattern in self.negation_patterns:
                    if self._match_pattern(neg_pattern, path_str, file_path):
                        is_ignored = False
                        break

            return is_ignored

        except Exception as e:
            self.logger.warning(
                "Error checking ignore pattern for %s: %s", file_path, e
            )
            return False

    def _match_pattern(self, pattern: str, path_str: str, file_path: Path) -> bool:
        """
        Match a single pattern against a path.

        Args:
            pattern: Pattern to match
            path_str: String representation of path
            file_path: Path object for additional checks

        Returns:
            True if pattern matches
        """
        # Direct match
        if fnmatch.fnmatch(path_str, pattern):
            return True

        # Match any part of the path (for patterns like node_modules)
        path_parts = path_str.split("/")
        for i, part in enumerate(path_parts):
            if fnmatch.fnmatch(part, pattern):
                return True

            # Check if pattern matches from this part onwards
            remaining_path = "/".join(path_parts[i:])
            if fnmatch.fnmatch(remaining_path, pattern):
                return True

        # Directory pattern matching
        if file_path.is_dir() and pattern.endswith("/**"):
            dir_pattern = pattern[:-3]
            if fnmatch.fnmatch(path_str, dir_pattern) or path_str.endswith(
                "/" + dir_pattern
            ):
                return True

        return False


class IgnoreFileResolver:
    """
    Resolves ignore files with intelligent fallback hierarchy:
    1. Custom ignore file (if specified)
    2. .contextignore (if exists)
    3. .gitignore (if exists) + context defaults
    4. Context defaults only
    """

    def __init__(self, project_path: Path):
        """
        Initialize ignore file resolver.

        Args:
            project_path: Path to the project directory
        """
        self.logger = get_logger(__name__)
        self.project_path = project_path.resolve()

    def resolve_ignore_patterns(
        self, custom_ignore_file: Optional[Path] = None
    ) -> IgnorePatternMatcher:
        """
        Resolve ignore patterns with intelligent fallback.

        Args:
            custom_ignore_file: Optional custom ignore file path

        Returns:
            Configured IgnorePatternMatcher
        """
        patterns = []
        source = "defaults"

        try:
            if custom_ignore_file and custom_ignore_file.exists():
                # Use custom ignore file
                patterns = self._load_ignore_file(custom_ignore_file)
                source = f"custom ({custom_ignore_file.name})"

            else:
                # Check for .contextignore
                contextignore = self.project_path / CONTEXTIGNORE_FILENAME
                if contextignore.exists():
                    patterns = self._load_ignore_file(contextignore)
                    source = ".contextignore"

                else:
                    # Fallback to .gitignore + defaults
                    gitignore = self.project_path / GITIGNORE_FILENAME
                    if gitignore.exists():
                        patterns = self._load_ignore_file(gitignore)
                        patterns.extend(DEFAULT_IGNORE_PATTERNS)
                        source = ".gitignore + defaults"
                    else:
                        # Use defaults only
                        patterns = list(DEFAULT_IGNORE_PATTERNS)
                        source = "defaults only"

            self.logger.debug(
                "Loaded %d ignore patterns from %s", len(patterns), source
            )
            return IgnorePatternMatcher(patterns, self.project_path)

        except Exception as e:
            self.logger.warning("Error loading ignore patterns, using defaults: %s", e)
            return IgnorePatternMatcher(
                list(DEFAULT_IGNORE_PATTERNS), self.project_path
            )

    def _load_ignore_file(self, ignore_file: Path) -> List[str]:
        """
        Load patterns from an ignore file.

        Args:
            ignore_file: Path to ignore file

        Returns:
            List of patterns
        """
        try:
            with open(ignore_file, "r", encoding="utf-8", errors="ignore") as f:
                patterns = [line.strip() for line in f.readlines()]

            self.logger.debug(
                "Loaded %d patterns from %s", len(patterns), ignore_file.name
            )
            return patterns

        except Exception as e:
            self.logger.error("Error reading ignore file %s: %s", ignore_file, e)
            return []

    def create_sample_contextignore(self) -> Path:
        """
        Create a sample .contextignore file in the project directory.

        Returns:
            Path to created file
        """
        contextignore_path = self.project_path / CONTEXTIGNORE_FILENAME

        try:
            with open(contextignore_path, "w", encoding="utf-8") as f:
                f.write(SAMPLE_CONTEXTIGNORE_CONTENT)

            self.logger.info("Created sample .contextignore at %s", contextignore_path)
            return contextignore_path

        except Exception as e:
            self.logger.error("Error creating .contextignore: %s", e)
            raise


class FileFilter:
    """
    High-level file filtering for embedding generation.

    Combines ignore patterns with extension filtering and provides
    a clean interface for the chunking system.
    """

    def __init__(self, project_path: Path, custom_ignore_file: Optional[Path] = None):
        """
        Initialize file filter.

        Args:
            project_path: Path to project directory
            custom_ignore_file: Optional custom ignore file
        """
        self.logger = get_logger(__name__)
        self.project_path = project_path.resolve()

        # Initialize ignore pattern matcher
        resolver = IgnoreFileResolver(project_path)
        self.ignore_matcher = resolver.resolve_ignore_patterns(custom_ignore_file)

        # Get supported extensions dynamically from LanguagesRegistry
        self.languages_registry = get_languages_registry()
        self.supported_extensions = self.languages_registry.get_supported_extensions()

        self.logger.debug("FileFilter initialized for %s", self.project_path)

    def should_process_file(self, file_path: Path) -> Tuple[bool, str]:
        """
        Determine if a file should be processed for embedding.

        Args:
            file_path: Path to check

        Returns:
            Tuple of (should_process, reason)
        """
        try:
            # Must be a file
            if not file_path.is_file():
                return False, "not a file"

            # Check ignore patterns
            if self.ignore_matcher.should_ignore(file_path):
                return False, "matches ignore pattern"

            # Check file extension
            extension = file_path.suffix.lower()
            if extension not in self.supported_extensions:
                return False, f"unsupported extension ({extension})"

            # Check file size (reasonable limit)
            try:
                file_size = file_path.stat().st_size
                if file_size > MAX_FILE_SIZE_BYTES:
                    return (
                        False,
                        f"file too large (>{MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB)",
                    )

                if file_size == 0:
                    return False, "empty file"

            except OSError:
                return False, "cannot access file"

            return True, "accepted"

        except Exception as e:
            self.logger.debug("Error checking file %s: %s", file_path, e)
            return False, f"error: {e}"

    def filter_files(self, file_paths: List[Path]) -> Tuple[List[Path], dict]:
        """
        Filter a list of files for processing.

        Args:
            file_paths: List of file paths to filter

        Returns:
            Tuple of (accepted_files, stats)
        """
        accepted = []
        stats = {
            "total": len(file_paths),
            "accepted": 0,
            "ignored": 0,
            "unsupported": 0,
            "too_large": 0,
            "empty": 0,
            "errors": 0,
        }

        for file_path in file_paths:
            should_process, reason = self.should_process_file(file_path)

            if should_process:
                accepted.append(file_path)
                stats["accepted"] += 1
            else:
                if "ignore" in reason:
                    stats["ignored"] += 1
                elif "unsupported" in reason:
                    stats["unsupported"] += 1
                elif "too large" in reason:
                    stats["too_large"] += 1
                elif "empty" in reason:
                    stats["empty"] += 1
                else:
                    stats["errors"] += 1

        self.logger.info(
            "Filtered %d files: %d accepted, %d ignored, %d unsupported",
            stats["total"],
            stats["accepted"],
            stats["ignored"],
            stats["unsupported"],
        )

        return accepted, stats


def create_file_filter(
    project_path: Path, custom_ignore_file: Optional[Path] = None
) -> FileFilter:
    """
    Factory function to create a FileFilter instance.

    Args:
        project_path: Path to project directory
        custom_ignore_file: Optional custom ignore file

    Returns:
        Configured FileFilter
    """
    return FileFilter(project_path, custom_ignore_file)
