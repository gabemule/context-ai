"""
Generate command implementation for Context-AI.

Provides embedding generation functionality from project directories.
"""

import argparse

from utils.error_handler import handle_command_errors
from utils.logging import get_logger


def add_generate_parser(subparsers) -> argparse.ArgumentParser:
    """Add generate command to CLI parser."""
    parser = subparsers.add_parser(
        "generate", help="Generate embeddings from a project directory"
    )

    parser.add_argument("path", help="Path to the project directory")
    parser.add_argument(
        "--name", "-n", required=True, help="Name for this embedding set"
    )
    parser.add_argument(
        "--ignore-file",
        "-i",
        help="Custom ignore file path (defaults to .contextignore then .gitignore)",
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable progress tracking and fancy output",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed processing information",
    )

    parser.set_defaults(func=execute_generate_command)
    return parser


@handle_command_errors
def execute_generate_command(args: argparse.Namespace) -> int:
    """Handle generate command."""
    logger = get_logger(__name__)
    logger.info("🚀 Initializing generate command...")

    from rich.console import Console

    from services.embedding_service import EmbeddingService

    console = Console()

    with console.status("[bold green]Loading embedding service...", spinner="dots"):
        service = EmbeddingService()

    show_progress = not args.no_progress
    service.generate_embedding(args.path, args.name, args.ignore_file, show_progress)

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
    add_generate_parser(subparsers)

    # Test with sample args
    test_args = parser.parse_args(
        ["generate", "./test-project", "--name", "test-v1", "--verbose"]
    )
    execute_generate_command(test_args)
