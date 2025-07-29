"""
Query command implementation for Context-AI.

Provides context search functionality to retrieve relevant code and documentation
chunks from selected embeddings based on user queries.
"""

import argparse

from utils.exceptions import ValidationError
from utils.logging import get_logger

DEFAULT_OUTPUT_FORMAT = "ai_friendly"
SUPPORTED_FORMATS = ["ai_friendly", "plain", "markdown", "json"]


def add_query_parser(subparsers) -> argparse.ArgumentParser:
    """Add query command to CLI parser."""
    parser = subparsers.add_parser(
        "query",
        help="Search embeddings for relevant context",
        description="Query active embeddings to find relevant code and "
        "documentation context",
    )

    parser.add_argument(
        "question", help="Question or search query to find relevant context"
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=SUPPORTED_FORMATS,
        default=DEFAULT_OUTPUT_FORMAT,
        help=f"Output format (default: {DEFAULT_OUTPUT_FORMAT})",
    )

    parser.add_argument(
        "--max-results",
        "-n",
        type=int,
        default=None,
        help="Maximum number of results to display "
        "(uses config default if not specified)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed search information and statistics",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show debug information including query preprocessing details",
    )

    parser.add_argument(
        "--copy",
        "-c",
        action="store_true",
        help="Copy results to clipboard (requires pyperclip)",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Save results to file instead of printing to console",
    )

    parser.set_defaults(func=execute_query_command)
    return parser


def execute_query_command(args: argparse.Namespace) -> None:
    """
    Execute the query command.

    Args:
        args: Parsed command line arguments
    """
    logger = get_logger(__name__)
    logger.info("🚀 Initializing query command...")

    from rich.console import Console
    from utils.session_logger import start_command_session, end_command_session

    # Start session logging
    session_args = {
        "question": args.question,
        "format": args.format,
        "max_results": args.max_results,
        "verbose": args.verbose,
        "debug": args.debug,
        "copy": args.copy,
        "output": args.output
    }
    start_command_session("query", session_args)

    try:
        console = Console()

        # Initialize query service with loading
        with console.status("[bold green]Loading query service...", spinner="dots"):
            from services.embedding_service import QueryService

            query_service = QueryService()

        # Set debug mode if requested
        if args.debug:
            logger.setLevel("DEBUG")
            logger.debug("Debug mode enabled")
            logger.debug("Query arguments: %s", vars(args))

        # Validate query
        if not args.question.strip():
            raise ValidationError("Query cannot be empty")

        # Execute query
        logger.info("🔍 Searching for: %s", args.question)

        if args.verbose:
            logger.info("📊 Query format: %s", args.format)
            if args.max_results:
                logger.info("📊 Max results: %d", args.max_results)

        # Get context from query service
        if args.format == "json":
            context_result = query_service.query_context_json(
                args.question, max_results=args.max_results
            )
        else:
            context_result = query_service.query_context(
                args.question,
                format_type=args.format,
                max_results=args.max_results,
                verbose=args.verbose,
            )

        # Log query result to session
        from utils.session_logger import get_current_session
        session = get_current_session()
        if session:
            # Estimate results count from context_result length
            results_count = len(context_result.split('\n---')) if '---' in context_result else 1
            session.log_query_result(context_result, args.question, args.format, results_count)

        # Handle output
        if args.output:
            _save_to_file(context_result, args.output, logger)
        else:
            # Use rich formatting for better display
            _display_query_result(context_result, args.format)

        if args.copy:
            _copy_to_clipboard(context_result, logger)

        if args.verbose:
            logger.info("✅ Query completed successfully")

    except ValidationError as e:
        logger.error("❌ Validation error: %s", e)
        exit(1)
    except Exception as e:
        logger.error("❌ Query failed: %s", e)
        if args.debug:
            import traceback

            logger.debug("Full traceback: %s", traceback.format_exc())
        exit(1)
    finally:
        # End session logging
        end_command_session()


def _save_to_file(content: str, file_path: str, logger) -> None:
    """Save content to file."""
    try:
        from pathlib import Path

        output_file = Path(file_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info("💾 Results saved to: %s", file_path)

    except Exception as e:
        raise ValidationError(f"Failed to save to file: {e}")


def _copy_to_clipboard(content: str, logger) -> None:
    """Copy content to clipboard."""
    try:
        import pyperclip

        pyperclip.copy(content)
        logger.info("📋 Results copied to clipboard")

    except ImportError:
        logger.warning(
            "⚠️  pyperclip not installed. Install with: pip install pyperclip"
        )
    except Exception as e:
        logger.warning("⚠️  Failed to copy to clipboard: %s", e)


def _display_query_result(content: str, format_type: str) -> None:
    """Display query result with appropriate formatting."""
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.syntax import Syntax

    console = Console()

    if format_type == "json":
        # Pretty print JSON with syntax highlighting
        syntax = Syntax(content, "json", theme="monokai", line_numbers=False)
        panel = Panel(
            syntax, title="🔍 Query Results (JSON)", border_style="cyan", padding=(1, 2)
        )
        console.print(panel)
    elif format_type == "xml":
        # Pretty print XML with syntax highlighting
        syntax = Syntax(content, "xml", theme="monokai", line_numbers=False)
        panel = Panel(
            syntax, title="🔍 Query Results (XML)", border_style="cyan", padding=(1, 2)
        )
        console.print(panel)
    elif format_type == "markdown":
        # Render markdown
        markdown_content = Markdown(content)
        panel = Panel(
            markdown_content,
            title="🔍 Query Results (Markdown)",
            border_style="cyan",
            padding=(1, 2),
        )
        console.print(panel)
    else:
        # Plain text or ai_friendly - use simple panel
        panel = Panel(
            content,
            title=f"🔍 Query Results ({format_type})",
            border_style="cyan",
            padding=(1, 2),
        )
        console.print(panel)


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
    add_query_parser(subparsers)

    # Test with sample args
    test_args = parser.parse_args(["query", "how to use buttons", "--verbose"])
    execute_query_command(test_args)
