"""
Chat command implementation for Context-AI.

Provides interactive AI chat sessions with context from active embeddings.
"""

import argparse

from utils.error_handler import handle_command_errors
from utils.logging import get_logger


def add_chat_parser(subparsers) -> argparse.ArgumentParser:
    """Add chat command to CLI parser."""
    parser = subparsers.add_parser("chat", help="Start interactive chat session")

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed processing information",
    )
    parser.add_argument(
        "--prompt-mode",
        "-pm",
        choices=["minimal", "standard", "comprehensive", "strict"],
        help="Set prompt mode: minimal (basic), standard (default), "
        "comprehensive (full analysis), strict (enforced guidelines)",
    )

    parser.set_defaults(func=execute_chat_command)
    return parser


@handle_command_errors
def execute_chat_command(args: argparse.Namespace) -> int:
    """Handle chat command."""
    logger = get_logger(__name__)
    logger.info("🚀 Initializing chat command...")

    from rich.console import Console
    from utils.session_logger import start_command_session, end_command_session

    # Start session logging
    session_args = {
        "verbose": args.verbose,
        "prompt_mode": getattr(args, 'prompt_mode', None)
    }
    start_command_session("chat", session_args)

    console = Console()

    # Load heavy imports with loading indicator
    with console.status("[bold green]Loading chat service...", spinner="dots"):
        from services.ai_service import AIService
        from config.settings import get_settings_manager

        service = AIService()
        settings_manager = get_settings_manager()

    # Set prompt mode if specified
    original_mode = None
    if args.prompt_mode:
        original_mode = settings_manager.get_prompt_mode()
        settings_manager.set_prompt_mode(args.prompt_mode)
        if args.verbose:
            logger.info("🎯 Using prompt mode: %s", args.prompt_mode)

    try:
        service.start_chat(verbose=args.verbose)
    finally:
        # Restore original mode
        if args.prompt_mode and original_mode:
            settings_manager.set_prompt_mode(original_mode)
        
        # End session logging
        end_command_session()

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
    add_chat_parser(subparsers)

    # Test with sample args
    test_args = parser.parse_args(["chat", "--verbose"])
    execute_chat_command(test_args)
