"""
Ask command implementation for Context-AI.

Provides AI-powered question answering using context from active embeddings.
"""

import argparse

from utils.error_handler import handle_command_errors
from utils.logging import get_logger


def add_ask_parser(subparsers) -> argparse.ArgumentParser:
    """Add ask command to CLI parser."""
    parser = subparsers.add_parser(
        "ask",
        help="Ask a question and get AI-powered answer",
        description="Ask Claude a question using context from your active embeddings",
        epilog="""
Examples:
  context-ai ask "How do I implement authentication?"
  context-ai ask "Show me error handling patterns" --format json
  context-ai ask "What validation helpers exist?" --copy --verbose
  context-ai ask "How to structure a new feature?" --output answer.md
        """,
    )

    parser.add_argument("question", help="Question to ask")
    parser.add_argument(
        "--format",
        "-f",
        choices=["ai_friendly", "plain", "markdown", "json", "xml"],
        default="ai_friendly",
        help="Context format for AI processing (default: ai_friendly)",
    )
    parser.add_argument(
        "--copy", "-c", action="store_true", help="Copy response to clipboard"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Save response to file instead of printing to console",
    )
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

    parser.set_defaults(func=execute_ask_command)
    return parser


@handle_command_errors
def execute_ask_command(args: argparse.Namespace) -> int:
    """Handle ask command."""
    logger = get_logger(__name__)
    logger.info("🚀 Initializing ask command...")

    from rich.console import Console

    console = Console()

    # Set prompt mode if specified
    if args.prompt_mode:
        import config.constants

        original_mode = config.constants.PROMPT_MODE
        config.constants.PROMPT_MODE = args.prompt_mode
        if args.verbose:
            logger.info("🎯 Using prompt mode: %s", args.prompt_mode)

    # Load heavy imports with loading indicator
    with console.status("[bold green]Loading AI service...", spinner="dots"):
        from services.ai_service import get_ai_service
        service = get_ai_service()

    try:
        service.ask_question(
            question=args.question,
            context_format=args.format,
            verbose=args.verbose,
            copy_to_clipboard=args.copy,
            output_file=args.output,
        )
    finally:
        # Restore original mode
        if args.prompt_mode:
            config.constants.PROMPT_MODE = original_mode

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
    add_ask_parser(subparsers)

    # Test with sample args
    test_args = parser.parse_args(["ask", "How to implement auth?", "--verbose"])
    execute_ask_command(test_args)
