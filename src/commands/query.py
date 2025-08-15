"""
Query command implementation for Context-AI.

Clean Architecture approach with separated responsibilities and comprehensive context search functionality.
"""

import argparse
from contextlib import contextmanager
from typing import Any, NamedTuple, Optional

from utils.error_handler import handle_command_errors
from utils.exceptions import ValidationError
from utils.logging import get_logger

# =============================================================================
# CONSTANTS (Configuration)
# =============================================================================

DEFAULT_OUTPUT_FORMAT = "ai_friendly"
SUPPORTED_FORMATS = ["ai_friendly", "plain", "markdown", "json", "xml"]


# =============================================================================
# HELP CONSTANTS (Separated from implementation for DRY/SRP)
# =============================================================================

QUERY_HELP = {
    "help": "Search embeddings for relevant context",
    "description": "Query active embeddings to find relevant code and documentation context. "
    "Uses advanced semantic search to retrieve the most relevant chunks based on "
    "your question, with support for multiple output formats and flexible result handling.",
    "epilog": """
Examples:
  context-ai query "How do I implement authentication?"
  context-ai query "Show me error handling patterns" --format json
  context-ai query "What validation helpers exist?" --copy --verbose
  context-ai query "API design best practices" --output results.md --max-results 10
  context-ai query "Database connection setup" --debug --format markdown
    """,
    "arguments": {
        "question": "Question or search query to find relevant context (required). "
        "Use natural language to describe what you're looking for",
        "format": f"Output format for results. Options: {', '.join(SUPPORTED_FORMATS)}. "
        f"Default: {DEFAULT_OUTPUT_FORMAT}. Choose based on your intended use",
        "max_results": "Maximum number of results to display. Uses configuration default if not specified. "
        "Higher numbers provide more context but may be overwhelming",
        "verbose": "Show detailed search information and statistics including embeddings used, "
        "result scores, and performance metrics",
        "debug": "Show debug information including query preprocessing details, "
        "search terms expansion, and internal processing steps",
        "copy": "Copy results to clipboard for easy sharing. Requires pyperclip package",
        "output": "Save results to specified file instead of printing to console. "
        "File extension should match the chosen format",
    },
}


# =============================================================================
# DATA STRUCTURES (Clean data modeling)
# =============================================================================


class ServiceContainer(NamedTuple):
    """Container for initialized services (Dependency Injection)."""

    query_service: Any
    console: Any


class QueryRequest(NamedTuple):
    """Structured query request (Value Object)."""

    question: str
    format: str
    max_results: Optional[int]
    verbose: bool
    debug: bool
    copy: bool
    output: Optional[str]


# =============================================================================
# CONTEXT MANAGERS (Clean Resource Management)
# =============================================================================


@contextmanager
def query_context(request: QueryRequest, logger):
    """Manage query lifecycle with session logging (SRP)."""
    from utils.session_logger import end_command_session, start_command_session

    # Prepare session arguments
    session_args = {
        "question": request.question,
        "format": request.format,
        "max_results": request.max_results,
        "verbose": request.verbose,
        "debug": request.debug,
        "copy": request.copy,
        "output": request.output,
    }

    start_command_session("query", session_args)

    try:
        logger.info("🔍 Searching for: %s", request.question)

        if request.verbose:
            logger.info("📊 Query format: %s", request.format)
            if request.max_results:
                logger.info("📊 Max results: %d", request.max_results)

        yield

        if request.verbose:
            logger.info("✅ Query completed successfully")

    except Exception as e:
        logger.error("❌ Query failed: %s", str(e))
        raise
    finally:
        end_command_session()


@contextmanager
def debug_context(request: QueryRequest, logger):
    """Manage debug mode configuration (SRP)."""
    original_level = None

    if request.debug:
        original_level = logger.level
        logger.setLevel("DEBUG")
        logger.debug("Debug mode enabled")
        logger.debug("Query arguments: %s", request._asdict())

    try:
        yield
    finally:
        if request.debug and original_level is not None:
            logger.setLevel(original_level)


# =============================================================================
# SERVICE INITIALIZATION (Dependency Injection)
# =============================================================================


def _initialize_services(logger) -> ServiceContainer:
    """Initialize required services with loading indicator (SRP)."""
    from rich.console import Console

    console = Console()

    # Load heavy imports with loading indicator
    with console.status("[bold green]Loading query service...", spinner="dots"):
        from services.embedding_service import QueryService

        query_service = QueryService()

        logger.debug("Query service initialized")

    return ServiceContainer(query_service=query_service, console=console)


# =============================================================================
# REQUEST HANDLERS (Single Responsibility Principle)
# =============================================================================


def _create_query_request(args: argparse.Namespace) -> QueryRequest:
    """Create structured query request from CLI arguments (SRP)."""
    return QueryRequest(
        question=args.question,
        format=args.format,
        max_results=args.max_results,
        verbose=args.verbose,
        debug=args.debug,
        copy=args.copy,
        output=args.output,
    )


def _validate_query_request(request: QueryRequest, logger) -> bool:
    """Validate query request parameters (SRP)."""
    # Validate question
    if not request.question.strip():
        logger.error("❌ Query cannot be empty")
        return False

    # Validate format
    if request.format not in SUPPORTED_FORMATS:
        logger.error("❌ Invalid format: %s", request.format)
        logger.error("💡 Supported formats: %s", ", ".join(SUPPORTED_FORMATS))
        return False

    # Validate max_results
    if request.max_results is not None and request.max_results <= 0:
        logger.error("❌ Max results must be a positive number")
        return False

    # Validate output file path if specified
    if request.output:
        from pathlib import Path

        try:
            output_path = Path(request.output)
            # Test if we can create the parent directory
            # Ensure output directory exists via file operations
            from utils.file_operations import get_file_operations

            file_ops = get_file_operations()
            file_ops.ensure_directory_exists(output_path.parent)
        except Exception as e:
            logger.error("❌ Invalid output path: %s", str(e))
            return False

    if request.verbose:
        logger.info("✅ Request validation passed")

    return True


def _execute_query_request(
    request: QueryRequest, services: ServiceContainer, logger
) -> str:
    """Execute the query request (SRP)."""
    try:
        # Get context from query service
        if request.format == "json":
            context_result = services.query_service.query_context_json(
                request.question, max_results=request.max_results
            )
        else:
            context_result = services.query_service.query_context(
                request.question,
                format_type=request.format,
                max_results=request.max_results,
                verbose=request.verbose,
            )

        # Log query result to session
        _log_query_result(context_result, request, logger)

        return context_result

    except Exception as e:
        logger.error("❌ Query execution failed: %s", str(e))
        raise


def _log_query_result(context_result: str, request: QueryRequest, logger) -> None:
    """Log query result to session (SRP)."""
    try:
        from utils.session_logger import get_current_session

        session = get_current_session()
        if session:
            # Estimate results count from context_result length
            results_count = (
                len(context_result.split("\n---")) if "---" in context_result else 1
            )
            session.log_query_result(
                context_result, request.question, request.format, results_count
            )

    except Exception as e:
        logger.warning("Could not log query result to session: %s", e)


def _handle_output(content: str, request: QueryRequest, logger) -> None:
    """Handle output (display, save, copy) (SRP)."""
    # Handle file output
    if request.output:
        _save_to_file(content, request.output, logger)
    else:
        # Display to console
        _display_query_result(content, request.format)

    # Handle clipboard
    if request.copy:
        _copy_to_clipboard(content, logger)


# =============================================================================
# OUTPUT HANDLERS (Single Responsibility Principle)
# =============================================================================


def _save_to_file(content: str, file_path: str, logger) -> None:
    """Save content to file (SRP)."""
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
    """Copy content to clipboard (SRP)."""
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
    """Display query result with appropriate formatting (SRP)."""
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.syntax import Syntax

    console = Console()

    try:
        if format_type == "json":
            # Pretty print JSON with syntax highlighting
            syntax = Syntax(content, "json", theme="monokai", line_numbers=False)
            panel = Panel(
                syntax,
                title="🔍 Query Results (JSON)",
                border_style="cyan",
                padding=(1, 2),
            )
            console.print(panel)
        elif format_type == "xml":
            # Pretty print XML with syntax highlighting
            syntax = Syntax(content, "xml", theme="monokai", line_numbers=False)
            panel = Panel(
                syntax,
                title="🔍 Query Results (XML)",
                border_style="cyan",
                padding=(1, 2),
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

    except Exception:
        # Fallback to simple print if rich formatting fails
        console.print(f"🔍 Query Results ({format_type}):")
        console.print(content)


# =============================================================================
# PARSER CONFIGURATION (DRY Principle)
# =============================================================================


def add_query_parser(subparsers) -> argparse.ArgumentParser:
    """Add query command to CLI parser with comprehensive help."""
    parser = subparsers.add_parser(
        "query",
        help=QUERY_HELP["help"],
        description=QUERY_HELP["description"],
        epilog=QUERY_HELP["epilog"],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Required arguments
    parser.add_argument("question", help=QUERY_HELP["arguments"]["question"])

    # Optional arguments
    parser.add_argument(
        "--format",
        "-f",
        choices=SUPPORTED_FORMATS,
        default=DEFAULT_OUTPUT_FORMAT,
        help=QUERY_HELP["arguments"]["format"],
    )

    parser.add_argument(
        "--max-results",
        "-n",
        type=int,
        default=None,
        help=QUERY_HELP["arguments"]["max_results"],
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help=QUERY_HELP["arguments"]["verbose"]
    )

    parser.add_argument(
        "--debug", action="store_true", help=QUERY_HELP["arguments"]["debug"]
    )

    parser.add_argument(
        "--copy", "-c", action="store_true", help=QUERY_HELP["arguments"]["copy"]
    )

    parser.add_argument(
        "--output", "-o", type=str, help=QUERY_HELP["arguments"]["output"]
    )

    parser.set_defaults(func=execute_query_command)
    return parser


# =============================================================================
# MAIN COMMAND HANDLER (Orchestration)
# =============================================================================


@handle_command_errors
def execute_query_command(args: argparse.Namespace) -> int:
    """
    Execute query command with clean architecture approach.

    Acts as orchestrator, delegating specific responsibilities to specialized functions.
    """
    logger = get_logger(__name__)
    logger.info("🚀 Initializing query command...")

    # Create structured request (Value Object)
    request = _create_query_request(args)

    # Validate request parameters
    if not _validate_query_request(request, logger):
        from config.constants import EXIT_FAILURE

        return EXIT_FAILURE

    # Initialize services (Dependency Injection)
    services = _initialize_services(logger)

    # Execute with proper resource management
    with query_context(request, logger):
        with debug_context(request, logger):
            # Execute query
            context_result = _execute_query_request(request, services, logger)

            # Handle output
            _handle_output(context_result, request, logger)

    from config.constants import EXIT_SUCCESS

    return EXIT_SUCCESS


# =============================================================================
# TESTING SUPPORT (Development convenience)
# =============================================================================

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
