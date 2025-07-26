"""
Select command implementation for Context-AI.

Provides embedding selection functionality for queries.
"""

import argparse

from utils.error_handler import handle_command_errors
from utils.logging import get_logger


def add_select_parser(subparsers) -> argparse.ArgumentParser:
    """Add select command to CLI parser."""
    parser = subparsers.add_parser(
        "select", help="Select active embeddings for queries"
    )

    parser.add_argument(
        "embeddings",
        nargs="*",
        help="Embedding names to select (if not provided, shows interactive interface)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed processing information",
    )

    parser.set_defaults(func=execute_select_command)
    return parser


@handle_command_errors
def execute_select_command(args: argparse.Namespace) -> int:
    """Handle select command with optional direct embedding selection."""
    logger = get_logger(__name__)
    logger.info("🚀 Initializing select command...")

    from rich.console import Console

    console = Console()

    # Load heavy imports with loading indicator
    with console.status("[bold green]Loading embedding service...", spinner="dots"):
        from config.settings import get_settings_manager
        from services.embedding_service import EmbeddingService

        service = EmbeddingService()

    if args.embeddings:
        # Direct selection via CLI arguments
        embedding_names = args.embeddings
        logger.info("🎯 Setting active embeddings: %s", ", ".join(embedding_names))

        # Validate that embeddings exist
        available = service.list_embeddings()
        invalid = [name for name in embedding_names if name not in available]

        if invalid:
            logger.error("❌ Invalid embedding names: %s", ", ".join(invalid))
            logger.info("Available embeddings: %s", ", ".join(available))
            from config.constants import EXIT_ERROR

            return EXIT_ERROR

        # Set active embeddings directly
        settings_manager = get_settings_manager()
        settings_manager.set_active_embeddings(embedding_names)
        logger.info("✅ Selected embeddings: %s", ", ".join(embedding_names))
    else:
        # Interactive selection
        logger.info("🎯 Select active embeddings for queries\n")
        service.select_embeddings()

    from config.constants import EXIT_SUCCESS

    return EXIT_SUCCESS


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
    add_select_parser(subparsers)

    # Test with sample args
    test_args = parser.parse_args(["select", "embedding1", "embedding2", "--verbose"])
    execute_select_command(test_args)
