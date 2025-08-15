"""
Setup Manager for Context-AI.

Ensures the system has all necessary configuration files by copying templates when needed.
Provides "out of the box" functionality so users don't encounter missing file errors
when first using the system.
"""

from pathlib import Path
from typing import Optional

from utils.file_operations import get_file_operations
from utils.logging import get_logger


class SetupManager:
    """
    Ensures the system works "out of the box" by providing all needed config files.

    Purpose: Eliminates "file not found" errors when users first run the system.
    Automatically copies template files to user's config directory when they're missing.

    Benefits:
    - Zero-configuration startup experience for new users
    - Prevents crashes from missing configuration files
    - Maintains user customizations while filling in gaps
    - Handles complex directory structure setup automatically
    """

    def __init__(self):
        """Initialize setup manager."""
        self.logger = get_logger(__name__)
        self.file_ops = get_file_operations()

        # Use StorageManager for ALL path management
        from config.storage import get_storage_manager

        self.storage_manager = get_storage_manager()

    def ensure_all_configs_exist(self) -> None:
        """
        Central method for ensuring all config files exist.

        This coordinates the copying of all configuration types:
        languages, guidelines, and prompt templates.
        """
        try:
            self.logger.debug("🔧 Ensuring all configurations exist...")

            # Ensure config directory exists via StorageManager
            config_dir = self.storage_manager.path_manager.config_dir
            self.file_ops.ensure_directory_exists(config_dir)

            # Ensure each type of configuration
            self._ensure_languages_config()
            self._ensure_guidelines_config()
            self._ensure_prompts_config()

            self.logger.debug("✅ All configurations ensured")

        except Exception as e:
            self.logger.warning(f"Error ensuring configurations: {e}")
            # Don't raise - let the system continue with what's available

    def _ensure_languages_config(self) -> None:
        """Copy languages.yaml and documentation from samples/ if missing."""
        try:
            self.logger.debug("🌍 Ensuring languages configuration...")

            from config.languages.loader import DefaultConfigGenerator

            config_dir = self.storage_manager.path_manager.config_dir
            copy_result = DefaultConfigGenerator.copy_all_language_files(config_dir)
            if copy_result.has_changes:
                self.logger.info(
                    f"Initialized {copy_result.files_copied} language configuration files"
                )

        except Exception as e:
            self.logger.warning(f"Error ensuring languages config: {e}")

    def _ensure_guidelines_config(self) -> None:
        """Copy guidelines/*.md from samples/ if missing."""
        try:
            self.logger.debug("📝 Ensuring guidelines configuration...")

            # Use centralized path from StorageManager
            guidelines_dir = self.storage_manager.path_manager.guidelines_dir

            # Check if guidelines already exist
            if guidelines_dir.exists() and self.file_ops.list_files(
                guidelines_dir, "*.md"
            ):
                return  # Guidelines already exist

            # Copy guidelines from samples - use StorageManager template path
            samples_guidelines = (
                self.storage_manager.path_manager.template_guidelines_dir
            )

            if not self.file_ops.directory_exists(samples_guidelines):
                self.logger.warning(
                    f"Guidelines samples not found: {samples_guidelines}"
                )
                return

            # Ensure target directory exists
            self.file_ops.ensure_directory_exists(guidelines_dir)

            # Copy all .md files
            guideline_files = self.file_ops.list_files(samples_guidelines, "*.md")
            copied_count = 0

            for guideline_file in guideline_files:
                target_file = guidelines_dir / guideline_file.name
                if not self.file_ops.file_exists(target_file):
                    if self.file_ops.copy_file(guideline_file, target_file):
                        copied_count += 1
                        self.logger.debug(f"Copied guideline: {guideline_file.name}")

            if copied_count > 0:
                self.logger.info(f"Initialized {copied_count} guideline templates")

        except Exception as e:
            self.logger.warning(f"Error ensuring guidelines config: {e}")

    def _ensure_prompts_config(self) -> None:
        """Copy prompts/ structure from samples/ if missing."""
        try:
            self.logger.debug("🎯 Ensuring prompt configuration...")

            # Use centralized path from StorageManager
            prompts_dir = self.storage_manager.path_manager.prompts_dir

            # Check if prompts directory already exists
            if self.file_ops.directory_exists(prompts_dir):
                return  # Prompts already exist

            # Copy prompts from samples - use StorageManager template path
            samples_prompts = self.storage_manager.path_manager.template_prompts_dir

            if not self.file_ops.directory_exists(samples_prompts):
                self.logger.warning(f"Prompts samples not found: {samples_prompts}")
                return

            self.logger.info("Creating user prompt config by copying defaults...")
            self.logger.info(f"From: {samples_prompts}")
            self.logger.info(f"To: {prompts_dir}")

            # Copy entire directory structure
            if self.file_ops.copy_directory(samples_prompts, prompts_dir):
                self.logger.info("✅ User prompt configuration created successfully")
            else:
                self.logger.warning("Failed to copy prompt configuration")

        except Exception as e:
            self.logger.warning(f"Error ensuring prompts config: {e}")

    def get_config_directory(self) -> Path:
        """Get the configuration directory path via StorageManager."""
        return self.storage_manager.path_manager.config_dir

    def validate_setup(self) -> dict:
        """
        Validate that setup was completed successfully.

        Returns:
            Dictionary with validation results
        """
        # Use centralized paths from StorageManager
        config_dir = self.storage_manager.path_manager.config_dir
        guidelines_dir = self.storage_manager.path_manager.guidelines_dir
        prompts_dir = self.storage_manager.path_manager.prompts_dir

        results = {
            "config_dir_exists": self.file_ops.directory_exists(config_dir),
            "languages_exists": False,
            "guidelines_exists": False,
            "prompts_exists": False,
        }

        # Check languages config - use centralized path from StorageManager
        languages_file = self.storage_manager.path_manager.languages_file
        results["languages_exists"] = self.file_ops.file_exists(languages_file)

        # Check guidelines - use centralized path
        if self.file_ops.directory_exists(guidelines_dir):
            guideline_files = self.file_ops.list_files(guidelines_dir, "*.md")
            results["guidelines_exists"] = len(guideline_files) > 0

        # Check prompts - use centralized path
        results["prompts_exists"] = self.file_ops.directory_exists(prompts_dir)

        return results


# Global setup manager instance
_setup_manager: Optional[SetupManager] = None


def get_setup_manager() -> SetupManager:
    """
    Get global setup manager instance.

    Returns:
        Global SetupManager instance
    """
    global _setup_manager

    if _setup_manager is None:
        _setup_manager = SetupManager()

    return _setup_manager


def reset_setup_manager() -> None:
    """Reset the global setup manager instance (for testing)."""
    global _setup_manager
    _setup_manager = None
