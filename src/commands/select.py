"""
Select command implementation for Context-AI.

Clean Architecture approach with separated responsibilities and comprehensive embedding selection.
"""

import argparse
from typing import Any, List, NamedTuple
from contextlib import contextmanager

from utils.error_handler import handle_command_errors
from utils.logging import get_logger


# =============================================================================
# HELP CONSTANTS (Separated from implementation for DRY/SRP)
# =============================================================================

SELECT_HELP = {
    "help": "Select active embeddings for queries",
    "description": "Choose which embeddings to use for AI-powered queries and context retrieval. "
                  "You can either specify embedding names directly via command line arguments "
                  "for automation, or use the interactive interface for manual selection.",
    "epilog": """
Examples:
  context-ai select                           # Interactive selection interface
  context-ai select project-v1               # Select single embedding directly
  context-ai select backend-api frontend-ui  # Select multiple embeddings directly
  context-ai select project-v1 --verbose     # Direct selection with detailed output
    """,
    "arguments": {
        "embeddings": "Embedding names to select directly (optional). "
                     "If not provided, opens interactive selection interface. "
                     "Use space-separated names for multiple embeddings",
        "verbose": "Show detailed processing information including current selections, "
                  "available embeddings, and selection confirmation details"
    }
}


# =============================================================================
# DATA STRUCTURES (Clean data modeling)
# =============================================================================

class ServiceContainer(NamedTuple):
    """Container for initialized services (Dependency Injection)."""
    embedding_service: Any
    settings_manager: Any
    console: Any


class SelectRequest(NamedTuple):
    """Structured select request (Value Object)."""
    embeddings: List[str]
    is_interactive: bool
    verbose: bool


# =============================================================================
# CONTEXT MANAGERS (Clean Resource Management)
# =============================================================================

@contextmanager
def selection_context(request: SelectRequest, logger):
    """Manage selection lifecycle with proper logging (SRP)."""
    if request.is_interactive:
        logger.info("🎯 Starting interactive embedding selection...")
    else:
        logger.info("🎯 Setting active embeddings: %s", ", ".join(request.embeddings))
    
    if request.verbose:
        logger.info("📋 Selection mode: %s", "Interactive" if request.is_interactive else "Direct")
        if not request.is_interactive:
            logger.info("📝 Embeddings to select: %s", ", ".join(request.embeddings))
    
    try:
        yield
        
        if request.is_interactive:
            logger.info("✅ Interactive selection completed successfully")
        else:
            logger.info("✅ Direct selection completed successfully")
            
    except Exception as e:
        logger.error("❌ Selection failed: %s", str(e))
        raise


# =============================================================================
# SERVICE INITIALIZATION (Dependency Injection)
# =============================================================================

def _initialize_services(logger) -> ServiceContainer:
    """Initialize required services with loading indicator (SRP)."""
    from rich.console import Console
    
    console = Console()
    
    # Load heavy imports with loading indicator
    with console.status("[bold green]Loading embedding service...", spinner="dots"):
        from config.settings import get_settings_manager
        from services.embedding_service import EmbeddingService

        embedding_service = EmbeddingService()
        settings_manager = get_settings_manager()
        
        logger.debug("Embedding service and settings manager initialized")

    return ServiceContainer(
        embedding_service=embedding_service,
        settings_manager=settings_manager,
        console=console
    )


# =============================================================================
# REQUEST HANDLERS (Single Responsibility Principle)
# =============================================================================

def _create_select_request(args: argparse.Namespace) -> SelectRequest:
    """Create structured select request from CLI arguments (SRP)."""
    embeddings = args.embeddings if args.embeddings else []
    is_interactive = len(embeddings) == 0
    
    return SelectRequest(
        embeddings=embeddings,
        is_interactive=is_interactive,
        verbose=args.verbose
    )


def _validate_embeddings(embeddings: List[str], available: List[str], logger) -> bool:
    """Validate that embeddings exist (SRP)."""
    if not embeddings:
        return True  # No validation needed for empty list
    
    invalid = [name for name in embeddings if name not in available]
    
    if invalid:
        logger.error("❌ Invalid embedding names: %s", ", ".join(invalid))
        
        if available:
            logger.info("💡 Available embeddings: %s", ", ".join(available))
        else:
            logger.info("💡 No embeddings found. Generate some first with: context-ai generate")
        
        return False
    
    return True


def _get_current_selection_info(settings_manager, logger, verbose: bool) -> None:
    """Display current selection information (SRP)."""
    try:
        current_active = settings_manager.get_active_embeddings()
        current_selected = current_active.selected if current_active else []
        
        if current_selected:
            logger.info("📋 Currently active embeddings: %s", ", ".join(current_selected))
        else:
            logger.info("📋 No embeddings currently selected")
            
        if verbose and current_selected:
            logger.info("📊 Active embedding count: %d", len(current_selected))
            
    except Exception as e:
        logger.warning("Could not retrieve current selection: %s", e)


def _execute_direct_selection(request: SelectRequest, services: ServiceContainer, logger) -> None:
    """Execute direct embedding selection (SRP)."""
    try:
        # Get available embeddings for validation
        available = services.embedding_service.list_embeddings()
        
        if not available:
            logger.error("❌ No embeddings found")
            logger.info("💡 Generate embeddings first with: context-ai generate")
            raise ValueError("No embeddings available")
        
        # Validate requested embeddings
        if not _validate_embeddings(request.embeddings, available, logger):
            raise ValueError("Invalid embedding names")
        
        # Show current selection if verbose
        if request.verbose:
            _get_current_selection_info(services.settings_manager, logger, request.verbose)
        
        # Set active embeddings directly
        services.settings_manager.set_active_embeddings(request.embeddings)
        
        logger.info("✅ Selected embeddings: %s", ", ".join(request.embeddings))
        
        if request.verbose:
            logger.info("🎯 Selection saved and ready for queries")
            
    except Exception as e:
        logger.error("❌ Direct selection failed: %s", str(e))
        raise


def _execute_interactive_selection(request: SelectRequest, services: ServiceContainer, logger) -> None:
    """Execute interactive embedding selection (SRP)."""
    try:
        # Show current selection if verbose
        if request.verbose:
            _get_current_selection_info(services.settings_manager, logger, request.verbose)
        
        logger.info("🎯 Select active embeddings for queries\n")
        
        # Use the embedding service's interactive selection
        selected_embeddings = services.embedding_service.select_embeddings()
        
        if selected_embeddings and request.verbose:
            logger.info("🎯 Interactive selection completed")
            logger.info("✅ Final selection: %s", ", ".join(selected_embeddings))
            
    except Exception as e:
        logger.error("❌ Interactive selection failed: %s", str(e))
        raise


# =============================================================================
# PARSER CONFIGURATION (DRY Principle)
# =============================================================================

def add_select_parser(subparsers) -> argparse.ArgumentParser:
    """Add select command to CLI parser with comprehensive help."""
    parser = subparsers.add_parser(
        "select",
        help=SELECT_HELP["help"],
        description=SELECT_HELP["description"],
        epilog=SELECT_HELP["epilog"],
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Optional arguments
    parser.add_argument(
        "embeddings",
        nargs="*",
        help=SELECT_HELP["arguments"]["embeddings"]
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help=SELECT_HELP["arguments"]["verbose"]
    )

    parser.set_defaults(func=execute_select_command)
    return parser


# =============================================================================
# MAIN COMMAND HANDLER (Orchestration)
# =============================================================================

@handle_command_errors
def execute_select_command(args: argparse.Namespace) -> int:
    """
    Execute select command with clean architecture approach.
    
    Acts as orchestrator, delegating specific responsibilities to specialized functions.
    """
    logger = get_logger(__name__)
    logger.info("🚀 Initializing select command...")

    # Create structured request (Value Object)
    request = _create_select_request(args)
    
    # Initialize services (Dependency Injection)
    services = _initialize_services(logger)

    # Execute with proper resource management
    with selection_context(request, logger):
        if request.is_interactive:
            _execute_interactive_selection(request, services, logger)
        else:
            _execute_direct_selection(request, services, logger)

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
    add_select_parser(subparsers)

    # Test with sample args
    test_args = parser.parse_args(["select", "embedding1", "embedding2", "--verbose"])
    execute_select_command(test_args)
