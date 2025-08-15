"""
Generic file system operations for Context-AI.

Provides reusable file operations without coupling to specific configurations.
Following Single Responsibility Principle (SRP).
"""

import shutil
from pathlib import Path
from typing import List, Optional

from utils.logging import get_logger


class FileSystemOperations:
    """
    Generic file system operations with error handling.

    Provides common file/directory operations that can be reused
    across different modules without coupling to specific use cases.
    """

    def __init__(self):
        self.logger = get_logger(__name__)

    def copy_file(
        self, source: Path, target: Path, preserve_metadata: bool = True
    ) -> bool:
        """
        Copy a single file from source to target.

        Args:
            source: Source file path
            target: Target file path
            preserve_metadata: Whether to preserve file metadata (timestamps, etc.)

        Returns:
            True if copy successful, False otherwise
        """
        if not source.exists():
            self.logger.error("Source file not found: %s", source)
            return False

        if not source.is_file():
            self.logger.error("Source is not a file: %s", source)
            return False

        try:
            # Ensure target directory exists
            target.parent.mkdir(parents=True, exist_ok=True)

            if preserve_metadata:
                shutil.copy2(source, target)
            else:
                shutil.copy(source, target)

            self.logger.debug("Copied file: %s → %s", source.name, target.name)
            return True

        except (OSError, IOError) as e:
            self.logger.error("Failed to copy file %s → %s: %s", source, target, e)
            return False
        except Exception as e:
            self.logger.error(
                "Unexpected error copying file %s → %s: %s", source, target, e
            )
            return False

    def copy_directory(
        self, source: Path, target: Path, ignore_patterns: Optional[List[str]] = None
    ) -> bool:
        """
        Copy entire directory tree from source to target.

        Args:
            source: Source directory path
            target: Target directory path
            ignore_patterns: List of patterns to ignore (glob-style)

        Returns:
            True if copy successful, False otherwise
        """
        if not source.exists():
            self.logger.error("Source directory not found: %s", source)
            return False

        if not source.is_dir():
            self.logger.error("Source is not a directory: %s", source)
            return False

        try:
            if ignore_patterns:

                def ignore_func(directory, contents):
                    ignored = []
                    for pattern in ignore_patterns:
                        for item in contents:
                            if Path(item).match(pattern):
                                ignored.append(item)
                    return ignored

                shutil.copytree(source, target, ignore=ignore_func, dirs_exist_ok=True)
            else:
                shutil.copytree(source, target, dirs_exist_ok=True)

            self.logger.debug("Copied directory: %s → %s", source.name, target.name)
            return True

        except (OSError, IOError) as e:
            self.logger.error("Failed to copy directory %s → %s: %s", source, target, e)
            return False
        except Exception as e:
            self.logger.error(
                "Unexpected error copying directory %s → %s: %s", source, target, e
            )
            return False

    def list_files(
        self, directory: Path, pattern: str = "*", recursive: bool = False
    ) -> List[Path]:
        """
        List files in directory matching pattern.

        Args:
            directory: Directory to search in
            pattern: Glob pattern to match (default: all files)
            recursive: Whether to search recursively

        Returns:
            List of matching file paths
        """
        if not directory.exists():
            self.logger.debug("Directory not found: %s", directory)
            return []

        if not directory.is_dir():
            self.logger.error("Path is not a directory: %s", directory)
            return []

        try:
            if recursive:
                files = list(directory.rglob(pattern))
            else:
                files = list(directory.glob(pattern))

            # Filter to only files (not directories)
            file_paths = [f for f in files if f.is_file()]

            self.logger.debug(
                "Found %d files matching '%s' in %s",
                len(file_paths),
                pattern,
                directory.name,
            )
            return file_paths

        except Exception as e:
            self.logger.error("Error listing files in %s: %s", directory, e)
            return []

    def list_directories(self, directory: Path, pattern: str = "*") -> List[Path]:
        """
        List subdirectories in directory matching pattern.

        Args:
            directory: Directory to search in
            pattern: Glob pattern to match (default: all directories)

        Returns:
            List of matching directory paths
        """
        if not directory.exists():
            self.logger.debug("Directory not found: %s", directory)
            return []

        if not directory.is_dir():
            self.logger.error("Path is not a directory: %s", directory)
            return []

        try:
            items = list(directory.glob(pattern))
            directories = [d for d in items if d.is_dir()]

            self.logger.debug(
                "Found %d directories matching '%s' in %s",
                len(directories),
                pattern,
                directory.name,
            )
            return directories

        except Exception as e:
            self.logger.error("Error listing directories in %s: %s", directory, e)
            return []

    def ensure_directory_exists(
        self, directory: Path, parents: bool = True, exist_ok: bool = True
    ) -> bool:
        """
        Ensure directory exists, creating it if necessary.

        Args:
            directory: Directory path to ensure exists
            parents: Whether to create parent directories
            exist_ok: Whether it's OK if directory already exists

        Returns:
            True if directory exists/created successfully, False otherwise
        """
        try:
            directory.mkdir(parents=parents, exist_ok=exist_ok)
            self.logger.debug("Ensured directory exists: %s", directory)
            return True

        except (OSError, IOError) as e:
            self.logger.error("Failed to create directory %s: %s", directory, e)
            return False
        except Exception as e:
            self.logger.error(
                "Unexpected error creating directory %s: %s", directory, e
            )
            return False

    def remove_file(self, file_path: Path) -> bool:
        """
        Remove a single file.

        Args:
            file_path: Path to file to remove

        Returns:
            True if removal successful, False otherwise
        """
        if not file_path.exists():
            self.logger.debug("File already doesn't exist: %s", file_path)
            return True

        if not file_path.is_file():
            self.logger.error("Path is not a file: %s", file_path)
            return False

        try:
            file_path.unlink()
            self.logger.debug("Removed file: %s", file_path.name)
            return True

        except (OSError, IOError) as e:
            self.logger.error("Failed to remove file %s: %s", file_path, e)
            return False
        except Exception as e:
            self.logger.error("Unexpected error removing file %s: %s", file_path, e)
            return False

    def remove_directory(self, directory: Path, recursive: bool = False) -> bool:
        """
        Remove directory.

        Args:
            directory: Directory path to remove
            recursive: Whether to remove non-empty directories

        Returns:
            True if removal successful, False otherwise
        """
        if not directory.exists():
            self.logger.debug("Directory already doesn't exist: %s", directory)
            return True

        if not directory.is_dir():
            self.logger.error("Path is not a directory: %s", directory)
            return False

        try:
            if recursive:
                shutil.rmtree(directory)
            else:
                directory.rmdir()  # Only works on empty directories

            self.logger.debug("Removed directory: %s", directory.name)
            return True

        except (OSError, IOError) as e:
            self.logger.error("Failed to remove directory %s: %s", directory, e)
            return False
        except Exception as e:
            self.logger.error(
                "Unexpected error removing directory %s: %s", directory, e
            )
            return False

    def file_exists(self, file_path: Path) -> bool:
        """Check if file exists and is a file."""
        return file_path.exists() and file_path.is_file()

    def directory_exists(self, directory: Path) -> bool:
        """Check if directory exists and is a directory."""
        return directory.exists() and directory.is_dir()

    def get_file_size(self, file_path: Path) -> Optional[int]:
        """
        Get file size in bytes.

        Args:
            file_path: Path to file

        Returns:
            File size in bytes, None if file doesn't exist or error
        """
        try:
            if self.file_exists(file_path):
                return file_path.stat().st_size
            return None
        except Exception as e:
            self.logger.error("Error getting file size for %s: %s", file_path, e)
            return None


# Global instance for convenience
_file_operations: Optional[FileSystemOperations] = None


def get_file_operations() -> FileSystemOperations:
    """Get global file operations instance."""
    global _file_operations
    if _file_operations is None:
        _file_operations = FileSystemOperations()
    return _file_operations
