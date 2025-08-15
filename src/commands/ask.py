"""
Ask command implementation for Context-AI.

Clean Architecture approach with separated responsibilities and comprehensive AI-powered question answering.
"""

import argparse
from contextlib import contextmanager
from typing import Any, NamedTuple, Optional

from utils.error_handler import handle_command_errors
from utils.logging import get_logger

# =============================================================================
# HELP CONSTANTS (Separated from implementation for DRY/SRP)
# =============================================================================

ASK_HELP = {
    "help": "Ask a question and get AI-powered answer",
    "description": "Ask Claude a question using context from your active embeddings. "
    "Leverages your embedded codebase knowledge to provide accurate, "
    "context-aware responses with examples and best practices.",
    "epilog": """
Examples:
  context-ai ask "How do I implement authentication?"
  context-ai ask "Show me error handling patterns" --format json
  context-ai ask "What validation helpers exist?" --copy --verbose
  context-ai ask "How to structure a new feature?" --output answer.md
  context-ai ask "Best practices for API design?" --prompt-mode comprehensive
    """,
    "arguments": {
        "question": "Question to ask (required)",
        "format": "Context format for AI processing: ai_friendly (optimized for Claude), "
        "plain (simple text), markdown (structured), json (data format), "
        "xml (structured data). Default: ai_friendly",
        "copy": "Copy the AI response to system clipboard for easy sharing",
        "output": "Save the AI response to specified file instead of displaying in console",
        "verbose": "Show detailed processing information including context loading, "
        "embeddings used, and AI service operations",
        "prompt_mode": "Set prompt processing mode: minimal (basic response), "
        "standard (balanced), comprehensive (detailed analysis), "
        "strict (enforced guidelines and validation)",
    },
}


# =============================================================================
# DATA STRUCTURES (Clean data modeling)
# =============================================================================


class ServiceContainer(NamedTuple):
    """Container for initialized services (Dependency Injection)."""

    ai_service: Any
    settings_manager: Any
    console: Any


class AskRequest(NamedTuple):
    """Structured ask request (Value Object)."""

    question: str
    format: str
    verbose: bool
    copy: bool
    output: Optional[str]
    prompt_mode: Optional[str]


# =============================================================================
# CONTEXT MANAGERS (Clean Resource Management)
# =============================================================================


@contextmanager
def session_context(request: AskRequest):
    """Manage session logging lifecycle (SRP)."""
    from utils.session_logger import end_command_session, start_command_session

    session_args = {
        "question": request.question,
        "format": request.format,
        "verbose": request.verbose,
        "copy": request.copy,
        "output": request.output,
        "prompt_mode": request.prompt_mode,
    }

    start_command_session("ask", session_args)
    try:
        yield
    finally:
        end_command_session()


@contextmanager
def prompt_mode_context(request: AskRequest, settings_manager, logger):
    """Manage prompt mode configuration lifecycle (SRP)."""
    original_mode = None

    if request.prompt_mode:
        original_mode = settings_manager.get_prompt_mode()
        settings_manager.set_prompt_mode(request.prompt_mode)
        if request.verbose:
            logger.info("🎯 Using prompt mode: %s", request.prompt_mode)

    try:
        yield
    finally:
        # Restore original mode
        if request.prompt_mode and original_mode:
            settings_manager.set_prompt_mode(original_mode)


# =============================================================================
# SERVICE INITIALIZATION (Dependency Injection)
# =============================================================================


def _initialize_services(logger) -> ServiceContainer:
    """Initialize required services with loading indicator (SRP)."""
    from rich.console import Console

    console = Console()

    # Load heavy imports with loading indicator
    with console.status("[bold green]Loading AI service...", spinner="dots"):
        from config.settings import get_settings_manager
        from services.ai_service import AIService

        ai_service = AIService()
        settings_manager = get_settings_manager()

        logger.debug("AI service and settings manager initialized")

    return ServiceContainer(
        ai_service=ai_service, settings_manager=settings_manager, console=console
    )


# =============================================================================
# REQUEST HANDLERS (Single Responsibility Principle)
# =============================================================================


def _create_ask_request(args: argparse.Namespace) -> AskRequest:
    """Create structured ask request from CLI arguments (SRP)."""
    return AskRequest(
        question=args.question,
        format=args.format,
        verbose=args.verbose,
        copy=args.copy,
        output=args.output,
        prompt_mode=getattr(args, "prompt_mode", None),
    )


def _execute_ask_request(
    request: AskRequest, services: ServiceContainer, logger
) -> None:
    """Execute the AI ask request (SRP)."""
    try:
        services.ai_service.ask_question(
            question=request.question,
            context_format=request.format,
            verbose=request.verbose,
            copy_to_clipboard=request.copy,
            output_file=request.output,
        )

        if request.verbose:
            logger.info("✅ Ask request completed successfully")

    except Exception as e:
        logger.error("❌ Ask request failed: %s", str(e))
        raise


# =============================================================================
# PARSER CONFIGURATION (DRY Principle)
# =============================================================================


def add_ask_parser(subparsers) -> argparse.ArgumentParser:
    """Add ask command to CLI parser with comprehensive help."""
    parser = subparsers.add_parser(
        "ask",
        help=ASK_HELP["help"],
        description=ASK_HELP["description"],
        epilog=ASK_HELP["epilog"],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Required arguments
    parser.add_argument("question", help=ASK_HELP["arguments"]["question"])

    # Optional arguments
    parser.add_argument(
        "--format",
        "-f",
        choices=["ai_friendly", "plain", "markdown", "json", "xml"],
        default="ai_friendly",
        help=ASK_HELP["arguments"]["format"],
    )

    parser.add_argument(
        "--copy", "-c", action="store_true", help=ASK_HELP["arguments"]["copy"]
    )

    parser.add_argument(
        "--output", "-o", type=str, help=ASK_HELP["arguments"]["output"]
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help=ASK_HELP["arguments"]["verbose"]
    )

    parser.add_argument(
        "--prompt-mode",
        "-pm",
        choices=["minimal", "standard", "comprehensive", "strict"],
        help=ASK_HELP["arguments"]["prompt_mode"],
    )

    parser.set_defaults(func=execute_ask_command)
    return parser


# =============================================================================
# MAIN COMMAND HANDLER (Orchestration)
# =============================================================================


@handle_command_errors
def execute_ask_command(args: argparse.Namespace) -> int:
    """
    Execute ask command with clean architecture approach.

    Acts as orchestrator, delegating specific responsibilities to specialized functions.
    """
    logger = get_logger(__name__)
    logger.info("🚀 Initializing ask command...")

    # Create structured request (Value Object)
    request = _create_ask_request(args)

    # Initialize services (Dependency Injection)
    services = _initialize_services(logger)

    # Execute with proper resource management
    with session_context(request):
        with prompt_mode_context(request, services.settings_manager, logger):
            _execute_ask_request(request, services, logger)

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
    add_ask_parser(subparsers)

    # Test with sample args
    test_args = parser.parse_args(["ask", "How to implement auth?", "--verbose"])
    execute_ask_command(test_args)
