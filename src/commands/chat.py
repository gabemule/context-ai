"""
Chat command implementation for Context-AI.

Clean Architecture approach with separated responsibilities and comprehensive interactive AI chat sessions.
"""

import argparse
from typing import Any, Optional, NamedTuple
from contextlib import contextmanager

from utils.error_handler import handle_command_errors
from utils.logging import get_logger


# =============================================================================
# HELP CONSTANTS (Separated from implementation for DRY/SRP)
# =============================================================================

CHAT_HELP = {
    "help": "Start interactive chat session",
    "description": "Start an interactive AI chat session with context from your active embeddings. "
                  "Engage in natural conversations with AI that has access to your codebase knowledge, "
                  "allowing for contextual discussions, code reviews, and technical guidance.",
    "epilog": """
Examples:
  context-ai chat                              # Start basic interactive chat
  context-ai chat --verbose                   # Chat with detailed processing info
  context-ai chat --prompt-mode comprehensive # Use comprehensive analysis mode
  context-ai chat --prompt-mode strict        # Use strict guidelines enforcement
    """,
    "arguments": {
        "verbose": "Show detailed processing information including context loading, "
                  "embeddings used, AI service operations, and conversation statistics",
        "prompt_mode": "Set prompt processing mode for chat responses: "
                      "minimal (basic responses), standard (balanced), "
                      "comprehensive (detailed analysis), strict (enforced guidelines). "
                      "Mode persists only for this chat session"
    }
}


# =============================================================================
# DATA STRUCTURES (Clean data modeling)
# =============================================================================

class ServiceContainer(NamedTuple):
    """Container for initialized services (Dependency Injection)."""
    ai_service: Any
    settings_manager: Any
    console: Any


class ChatRequest(NamedTuple):
    """Structured chat request (Value Object)."""
    verbose: bool
    prompt_mode: Optional[str]


# =============================================================================
# CONTEXT MANAGERS (Clean Resource Management)
# =============================================================================

@contextmanager
def chat_session_context(request: ChatRequest, logger):
    """Manage chat session lifecycle with proper cleanup (SRP)."""
    from utils.session_logger import start_command_session, end_command_session
    
    # Prepare session arguments
    session_args = {
        "verbose": request.verbose,
        "prompt_mode": request.prompt_mode
    }
    
    start_command_session("chat", session_args)
    
    try:
        logger.info("💬 Starting interactive chat session...")
        
        if request.verbose:
            logger.info("📋 Chat mode: Interactive")
            if request.prompt_mode:
                logger.info("🎯 Prompt mode: %s", request.prompt_mode)
        
        yield
        
        logger.info("✅ Chat session completed successfully")
        
    except KeyboardInterrupt:
        logger.info("👋 Chat session ended by user")
    except Exception as e:
        logger.error("❌ Chat session failed: %s", str(e))
        raise
    finally:
        end_command_session()


@contextmanager
def prompt_mode_context(request: ChatRequest, settings_manager, logger):
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
            if request.verbose:
                logger.info("🔄 Restored original prompt mode: %s", original_mode)


# =============================================================================
# SERVICE INITIALIZATION (Dependency Injection)
# =============================================================================

def _initialize_services(logger) -> ServiceContainer:
    """Initialize required services with loading indicator (SRP)."""
    from rich.console import Console
    
    console = Console()
    
    # Load heavy imports with loading indicator
    with console.status("[bold green]Loading chat service...", spinner="dots"):
        from services.ai_service import AIService
        from config.settings import get_settings_manager

        ai_service = AIService()
        settings_manager = get_settings_manager()
        
        logger.debug("AI service and settings manager initialized")

    return ServiceContainer(
        ai_service=ai_service,
        settings_manager=settings_manager,
        console=console
    )


# =============================================================================
# REQUEST HANDLERS (Single Responsibility Principle)
# =============================================================================

def _create_chat_request(args: argparse.Namespace) -> ChatRequest:
    """Create structured chat request from CLI arguments (SRP)."""
    return ChatRequest(
        verbose=args.verbose,
        prompt_mode=getattr(args, 'prompt_mode', None)
    )


def _validate_chat_prerequisites(services: ServiceContainer, logger) -> bool:
    """Validate chat prerequisites (SRP)."""
    try:
        # Check if AI service is properly configured
        # This would typically check API keys, settings, etc.
        if not hasattr(services.ai_service, 'start_chat'):
            logger.error("❌ AI service does not support chat functionality")
            return False
        
        # Check if embeddings are available (for context)
        try:
            current_active = services.settings_manager.get_active_embeddings()
            if not current_active.selected:
                logger.warning("⚠️  No active embeddings selected")
                logger.info("💡 Chat will work without context. Use 'context-ai select' to add context")
            else:
                logger.info("📋 Active embeddings: %s", ", ".join(current_active.selected))
        except Exception:
            logger.warning("⚠️  Could not check active embeddings")
        
        return True
        
    except Exception as e:
        logger.error("❌ Chat prerequisites validation failed: %s", str(e))
        return False


def _execute_chat_session(request: ChatRequest, services: ServiceContainer, logger) -> None:
    """Execute the interactive chat session (SRP)."""
    try:
        # Validate prerequisites
        if not _validate_chat_prerequisites(services, logger):
            logger.error("❌ Chat session cannot start due to validation failures")
            raise ValueError("Chat prerequisites not met")
        
        # Start the interactive chat session
        services.ai_service.start_chat(verbose=request.verbose)
        
        if request.verbose:
            logger.info("✅ Chat session executed successfully")
            
    except KeyboardInterrupt:
        # User interrupted - this is normal
        logger.info("👋 Chat session interrupted by user")
    except Exception as e:
        logger.error("❌ Chat session execution failed: %s", str(e))
        raise


# =============================================================================
# PARSER CONFIGURATION (DRY Principle)
# =============================================================================

def add_chat_parser(subparsers) -> argparse.ArgumentParser:
    """Add chat command to CLI parser with comprehensive help."""
    parser = subparsers.add_parser(
        "chat",
        help=CHAT_HELP["help"],
        description=CHAT_HELP["description"],
        epilog=CHAT_HELP["epilog"],
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Optional arguments
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help=CHAT_HELP["arguments"]["verbose"]
    )
    
    parser.add_argument(
        "--prompt-mode", "-pm",
        choices=["minimal", "standard", "comprehensive", "strict"],
        help=CHAT_HELP["arguments"]["prompt_mode"]
    )

    parser.set_defaults(func=execute_chat_command)
    return parser


# =============================================================================
# MAIN COMMAND HANDLER (Orchestration)
# =============================================================================

@handle_command_errors
def execute_chat_command(args: argparse.Namespace) -> int:
    """
    Execute chat command with clean architecture approach.
    
    Acts as orchestrator, delegating specific responsibilities to specialized functions.
    """
    logger = get_logger(__name__)
    logger.info("🚀 Initializing chat command...")

    # Create structured request (Value Object)
    request = _create_chat_request(args)
    
    # Initialize services (Dependency Injection)
    services = _initialize_services(logger)

    # Execute with proper resource management
    with chat_session_context(request, logger):
        with prompt_mode_context(request, services.settings_manager, logger):
            _execute_chat_session(request, services, logger)

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
    add_chat_parser(subparsers)

    # Test with sample args
    test_args = parser.parse_args(["chat", "--verbose"])
    execute_chat_command(test_args)
