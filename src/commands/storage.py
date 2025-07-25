"""
Storage command implementation for Context-AI.

Provides storage management and cleanup functionality.
"""

import argparse

from utils.error_handler import handle_command_errors
from utils.logging import get_logger


def add_storage_parser(subparsers) -> argparse.ArgumentParser:
    """Add storage command to CLI parser."""
    parser = subparsers.add_parser("storage", help="Manage storage and cleanup")

    storage_subparsers = parser.add_subparsers(
        dest="storage_action", help="Storage actions"
    )

    # Storage info
    info_parser = storage_subparsers.add_parser("info", help="Show storage information")
    info_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed processing information",
    )

    # Storage cleanup
    cleanup_parser = storage_subparsers.add_parser(
        "cleanup", help="Clean up temporary files"
    )
    cleanup_parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Remove temp files older than N hours (default: 24)",
    )
    cleanup_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed processing information",
    )

    # Storage reset
    reset_parser = storage_subparsers.add_parser(
        "reset", help="Reset all storage (DELETE EVERYTHING)"
    )
    reset_parser.add_argument(
        "--confirm", action="store_true", help="Confirm the reset operation"
    )
    reset_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed processing information",
    )

    # Storage delete
    delete_parser = storage_subparsers.add_parser(
        "delete", help="Delete a specific embedding"
    )
    delete_parser.add_argument("embedding_name", help="Name of embedding to delete")
    delete_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed processing information",
    )

    parser.set_defaults(func=execute_storage_command)
    return parser


@handle_command_errors
def execute_storage_command(args: argparse.Namespace) -> int:
    """Handle storage command."""
    logger = get_logger(__name__)
    logger.info("🚀 Initializing storage command...")

    from rich.console import Console

    from utils.storage import get_storage_manager

    console = Console()

    with console.status("[bold yellow]Loading storage info...", spinner="dots"):
        storage_manager = get_storage_manager()

    if args.storage_action == "info":
        logger.info("📊 Storage Information:")
        storage_info = storage_manager.get_storage_info()

        if "error" in storage_info:
            logger.error("❌ Error getting storage info: %s", storage_info["error"])
            return 1

        logger.info("Base path: %s", storage_info["base_path"])
        logger.info("Total size: %s MB", storage_info["total_size_mb"])
        logger.info("Embeddings count: %d", storage_info["embeddings_count"])

        if storage_info["embeddings"]:
            logger.info(
                "Available embeddings: %s", ", ".join(storage_info["embeddings"])
            )
        else:
            logger.info("Available embeddings: none")

        # Show directory sizes
        logger.info("Directory breakdown:")
        for dir_name, size_bytes in storage_info["directory_sizes"].items():
            size_mb = round(size_bytes / (1024 * 1024), 2)
            logger.info("  %s: %s MB", dir_name, size_mb)

    elif args.storage_action == "cleanup":
        logger.info("🧹 Cleaning up temporary files older than %d hours...", args.hours)
        cleaned_count = storage_manager.cleanup_temp_files(args.hours)
        logger.info("✅ Cleaned up %d temporary files", cleaned_count)

    elif args.storage_action == "reset":
        if not args.confirm:
            logger.error("❌ Reset requires --confirm flag")
            logger.error(
                "⚠️  This will DELETE ALL embeddings, configuration, and data!"
            )  # noqa: E501
            logger.error("Usage: context-ai storage reset --confirm")
            return 1

        logger.warning("🚨 RESETTING ALL STORAGE - This will delete everything!")
        success = storage_manager.reset_storage(confirm=True)
        if success:
            logger.info("✅ Storage reset complete")
        else:
            logger.error("❌ Storage reset failed")
            return 1

    elif args.storage_action == "delete":
        embedding_name = args.embedding_name
        logger.info("🗑️  Deleting embedding: %s", embedding_name)

        if not storage_manager.embedding_exists(embedding_name):
            logger.error("❌ Embedding '%s' does not exist", embedding_name)
            return 1

        success = storage_manager.delete_embedding(embedding_name)
        if success:
            logger.info("✅ Embedding '%s' deleted successfully", embedding_name)
        else:
            logger.error("❌ Failed to delete embedding '%s'", embedding_name)
            return 1

    else:
        logger.error("❌ Unknown storage action: %s", args.storage_action)
        return 1

    return 0


# For testing and direct execution
if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Add src to path for testing
    src_path = Path(__file__).parent.parent
    sys.path.insert(0, str(src_path))

    # Create a test parser
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    add_storage_parser(subparsers)

    # Test with sample args
    test_args = parser.parse_args(["storage", "info", "--verbose"])
    execute_storage_command(test_args)
