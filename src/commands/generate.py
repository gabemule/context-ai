"""
Generate command implementation for Context-AI.

Clean Architecture approach with separated responsibilities and comprehensive embedding generation.
"""

import argparse
import re
from pathlib import Path
from typing import Any, Optional, NamedTuple
from contextlib import contextmanager

from utils.error_handler import handle_command_errors
from utils.logging import get_logger


# =============================================================================
# HELP CONSTANTS (Separated from implementation for DRY/SRP)
# =============================================================================

GENERATE_HELP = {
    "help": "Generate embeddings from a project directory",
    "description": "Create vector embeddings from your codebase for AI-powered context retrieval. "
                  "Analyzes source code, documentation, and project files to build a comprehensive "
                  "knowledge base that enables intelligent question answering and code assistance.",
    "epilog": """
Examples:
  context-ai generate ./my-project --name project-v1
  context-ai generate /path/to/codebase --name backend-api --verbose
  context-ai generate . --name current-project --ignore-file custom.ignore
  context-ai generate ./frontend --name ui-components --no-progress
    """,
    "arguments": {
        "path": "Path to the project directory to analyze (required). "
               "Can be absolute or relative path to any directory containing code or documentation",
        "name": "Unique name for this embedding set (required). "
               "Use descriptive names like 'project-v1', 'backend-api', 'frontend-components'. "
               "Only alphanumeric characters, hyphens, and underscores allowed",
        "ignore_file": "Custom ignore file path to control which files are processed. "
                      "Defaults to .contextignore if present, then .gitignore. "
                      "Supports standard gitignore patterns and syntax",
        "no_progress": "Disable progress tracking and fancy output for CI/automation environments. "
                      "Useful for scripts, containers, or when running in non-interactive mode",
        "verbose": "Show detailed processing information including file discovery, "
                  "chunking statistics, embedding progress, and performance metrics"
    }
}


# =============================================================================
# DATA STRUCTURES (Clean data modeling)
# =============================================================================

class ServiceContainer(NamedTuple):
    """Container for initialized services (Dependency Injection)."""
    embedding_service: Any
    console: Any


class GenerateRequest(NamedTuple):
    """Structured generate request (Value Object)."""
    path: str
    name: str
    ignore_file: Optional[str]
    show_progress: bool
    verbose: bool


# =============================================================================
# CONTEXT MANAGERS (Clean Resource Management)
# =============================================================================

@contextmanager
def generation_context(request: GenerateRequest, logger):
    """Manage embedding generation lifecycle with proper cleanup (SRP)."""
    logger.info("🔄 Starting embedding generation for '%s'", request.name)
    
    if request.verbose:
        logger.info("📁 Source path: %s", request.path)
        logger.info("🏷️  Embedding name: %s", request.name)
        logger.info("📋 Progress enabled: %s", request.show_progress)
        if request.ignore_file:
            logger.info("🚫 Ignore file: %s", request.ignore_file)
    
    start_time = None
    try:
        import time
        start_time = time.time()
        yield
        
        elapsed = time.time() - start_time if start_time else 0
        logger.info("✅ Embedding generation completed successfully in %.2fs", elapsed)
        
    except Exception as e:
        logger.error("❌ Embedding generation failed: %s", str(e))
        raise
    finally:
        if request.verbose and start_time:
            elapsed = time.time() - start_time
            logger.info("⏱️  Total processing time: %.2fs", elapsed)


# =============================================================================
# SERVICE INITIALIZATION (Dependency Injection)
# =============================================================================

def _initialize_services(logger) -> ServiceContainer:
    """Initialize required services with loading indicator (SRP)."""
    from rich.console import Console
    
    console = Console()
    
    # Load heavy imports with loading indicator
    with console.status("[bold green]Loading embedding service...", spinner="dots"):
        from services.embedding_service import EmbeddingService

        embedding_service = EmbeddingService()
        
        logger.debug("Embedding service initialized")

    return ServiceContainer(
        embedding_service=embedding_service,
        console=console
    )


# =============================================================================
# REQUEST HANDLERS (Single Responsibility Principle)
# =============================================================================

def _create_generate_request(args: argparse.Namespace) -> GenerateRequest:
    """Create structured generate request from CLI arguments (SRP)."""
    return GenerateRequest(
        path=args.path,
        name=args.name,
        ignore_file=args.ignore_file,
        show_progress=not args.no_progress,
        verbose=args.verbose
    )


def _validate_generate_request(request: GenerateRequest, logger) -> bool:
    """Validate generate request parameters (SRP)."""
    # Validate path exists
    path_obj = Path(request.path)
    if not path_obj.exists():
        logger.error("❌ Path does not exist: %s", request.path)
        return False
    
    if not path_obj.is_dir():
        logger.error("❌ Path is not a directory: %s", request.path)
        return False
    
    # Validate embedding name format
    if not _is_valid_embedding_name(request.name):
        logger.error("❌ Invalid embedding name: '%s'", request.name)
        logger.error("💡 Use only alphanumeric characters, hyphens, and underscores")
        logger.error("💡 Examples: 'project-v1', 'backend_api', 'frontend-components'")
        return False
    
    # Check if embedding already exists
    if _embedding_exists(request.name, logger):
        logger.error("❌ Embedding '%s' already exists", request.name)
        logger.error("💡 Use a different name or delete the existing embedding first")
        logger.error("💡 Run: context-ai storage delete %s", request.name)
        return False
    
    # Validate ignore file if specified
    if request.ignore_file:
        ignore_path = Path(request.ignore_file)
        if not ignore_path.exists():
            logger.error("❌ Ignore file does not exist: %s", request.ignore_file)
            return False
        
        if not ignore_path.is_file():
            logger.error("❌ Ignore file path is not a file: %s", request.ignore_file)
            return False
    
    if request.verbose:
        logger.info("✅ Request validation passed")
    
    return True


def _is_valid_embedding_name(name: str) -> bool:
    """Check if embedding name follows naming conventions (SRP)."""
    # Allow alphanumeric, hyphens, and underscores
    # Must start with alphanumeric, length 1-50
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9_-]{0,49}$'
    return bool(re.match(pattern, name))


def _embedding_exists(name: str, logger) -> bool:
    """Check if embedding already exists (SRP)."""
    try:
        from utils.storage import get_storage_manager
        
        storage_manager = get_storage_manager()
        return storage_manager.embedding_exists(name)
        
    except Exception as e:
        logger.warning("Could not check existing embeddings: %s", e)
        return False


def _execute_generate_request(request: GenerateRequest, services: ServiceContainer, logger) -> None:
    """Execute the embedding generation request (SRP)."""
    try:
        services.embedding_service.generate_embedding(
            path=request.path,
            name=request.name,
            ignore_file=request.ignore_file,
            show_progress=request.show_progress
        )
        
        # Auto-select the newly created embedding for immediate use
        _auto_select_new_embedding(request.name, logger)
        
        if request.verbose:
            logger.info("✅ Embedding generation request completed successfully")
            
    except Exception as e:
        logger.error("❌ Embedding generation request failed: %s", str(e))
        raise


def _auto_select_new_embedding(embedding_name: str, logger) -> None:
    """Auto-select the newly created embedding for immediate use (SRP)."""
    try:
        from config.settings import get_settings_manager
        
        settings_manager = get_settings_manager()
        
        # Get current active embeddings
        current_active = settings_manager.get_active_embeddings()
        current_selected = current_active.selected if current_active else []
        
        # Add the new embedding to active selection if not already there
        if embedding_name not in current_selected:
            new_selection = current_selected + [embedding_name]
            settings_manager.set_active_embeddings(new_selection)
            logger.info("🎯 Auto-selected embedding '%s' for immediate use", embedding_name)
            
            if len(new_selection) > 1:
                logger.info("📋 Active embeddings: %s", ", ".join(new_selection))
        else:
            logger.debug("Embedding '%s' already in active selection", embedding_name)
            
    except Exception as e:
        logger.warning("Could not auto-select embedding: %s", e)
        logger.info("💡 You can manually select it with: context-ai select")


# =============================================================================
# PARSER CONFIGURATION (DRY Principle)
# =============================================================================

def add_generate_parser(subparsers) -> argparse.ArgumentParser:
    """Add generate command to CLI parser with comprehensive help."""
    parser = subparsers.add_parser(
        "generate",
        help=GENERATE_HELP["help"],
        description=GENERATE_HELP["description"],
        epilog=GENERATE_HELP["epilog"],
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Required arguments
    parser.add_argument(
        "path", 
        help=GENERATE_HELP["arguments"]["path"]
    )
    
    parser.add_argument(
        "--name", "-n",
        required=True,
        help=GENERATE_HELP["arguments"]["name"]
    )
    
    # Optional arguments
    parser.add_argument(
        "--ignore-file", "-i",
        help=GENERATE_HELP["arguments"]["ignore_file"]
    )
    
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help=GENERATE_HELP["arguments"]["no_progress"]
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help=GENERATE_HELP["arguments"]["verbose"]
    )

    parser.set_defaults(func=execute_generate_command)
    return parser


# =============================================================================
# MAIN COMMAND HANDLER (Orchestration)
# =============================================================================

@handle_command_errors
def execute_generate_command(args: argparse.Namespace) -> int:
    """
    Execute generate command with clean architecture approach.
    
    Acts as orchestrator, delegating specific responsibilities to specialized functions.
    """
    logger = get_logger(__name__)
    logger.info("🚀 Initializing generate command...")

    # Create structured request (Value Object)
    request = _create_generate_request(args)
    
    # Validate request parameters
    if not _validate_generate_request(request, logger):
        from config.constants import EXIT_FAILURE
        return EXIT_FAILURE
    
    # Initialize services (Dependency Injection)
    services = _initialize_services(logger)

    # Execute with proper resource management
    with generation_context(request, logger):
        _execute_generate_request(request, services, logger)

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
    add_generate_parser(subparsers)

    # Test with sample args
    test_args = parser.parse_args(
        ["generate", "./test-project", "--name", "test-v1", "--verbose"]
    )
    execute_generate_command(test_args)
