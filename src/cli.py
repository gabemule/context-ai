#!/usr/bin/env python3
"""
Context-AI CLI entry point.
Cross-project code intelligence assistant.
"""

import argparse
import sys
from typing import List, Optional

from utils.logging import setup_logging, get_logger
from utils.error_handler import handle_command_errors
from config.constants import EXIT_SUCCESS, EXIT_ERROR


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        prog="context-ai",
        description="Cross-project code intelligence assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  context-ai generate ./my-project --name "project-v1"
  context-ai select    # Interactive checkbox selection
  context-ai ask "How do I implement authentication?"
  context-ai chat
  context-ai storage info    # Show storage information
  context-ai storage cleanup # Clean temporary files
        """,
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version="context-ai 0.1.0"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        metavar="COMMAND"
    )
    
    # Generate command
    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate embeddings from a project directory"
    )
    generate_parser.add_argument(
        "path",
        help="Path to the project directory"
    )
    generate_parser.add_argument(
        "--name", "-n",
        required=True,
        help="Name for this embedding set"
    )
    generate_parser.add_argument(
        "--ignore-file", "-i",
        help="Custom ignore file path (defaults to .contextignore then .gitignore)"
    )
    generate_parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable progress tracking and fancy output"
    )
    
    # Select command
    select_parser = subparsers.add_parser(
        "select",
        help="Select active embeddings for queries"
    )
    select_parser.add_argument(
        "embeddings",
        nargs="*",
        help="Embedding names to select (if not provided, shows interactive interface)"
    )
    
    # Query command - defined inline to avoid heavy imports during parser creation
    query_parser = subparsers.add_parser(
        'query',
        help='Search embeddings for relevant context',
        description='Query active embeddings to find relevant code and documentation context'
    )
    query_parser.add_argument(
        'question',
        help='Question or search query to find relevant context'
    )
    query_parser.add_argument(
        '--format', '-f',
        choices=["ai_friendly", "plain", "markdown", "json"],
        default="ai_friendly",
        help='Output format (default: ai_friendly)'
    )
    query_parser.add_argument(
        '--max-results', '-n',
        type=int,
        default=None,
        help='Maximum number of results to display (uses config default if not specified)'
    )
    query_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed search information and statistics'
    )
    query_parser.add_argument(
        '--debug',
        action='store_true',
        help='Show debug information including query preprocessing details'
    )
    query_parser.add_argument(
        '--copy', '-c',
        action='store_true',
        help='Copy results to clipboard (requires pyperclip)'
    )
    query_parser.add_argument(
        '--output', '-o',
        type=str,
        help='Save results to file instead of printing to console'
    )
    
    # Ask command
    ask_parser = subparsers.add_parser(
        "ask",
        help="Ask a question and get AI-powered answer"
    )
    ask_parser.add_argument(
        "question",
        help="Question to ask"
    )
    
    # Chat command
    chat_parser = subparsers.add_parser(
        "chat",
        help="Start interactive chat session"
    )
    
    # Config command
    config_parser = subparsers.add_parser(
        "config",
        help="Manage configuration"
    )
    config_subparsers = config_parser.add_subparsers(
        dest="config_action",
        help="Configuration actions"
    )
    
    # Config set
    config_set = config_subparsers.add_parser(
        "set",
        help="Set configuration value"
    )
    config_set.add_argument(
        "--claude-key",
        help="Set Claude API key"
    )
    
    # Config list
    config_subparsers.add_parser(
        "list",
        help="List current configuration"
    )
    
    # Storage command
    storage_parser = subparsers.add_parser(
        "storage",
        help="Manage storage and cleanup"
    )
    storage_subparsers = storage_parser.add_subparsers(
        dest="storage_action",
        help="Storage actions"
    )
    
    # Storage info
    storage_subparsers.add_parser(
        "info",
        help="Show storage information"
    )
    
    # Storage cleanup
    cleanup_parser = storage_subparsers.add_parser(
        "cleanup",
        help="Clean up temporary files"
    )
    cleanup_parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Remove temp files older than N hours (default: 24)"
    )
    
    # Storage reset
    reset_parser = storage_subparsers.add_parser(
        "reset",
        help="Reset all storage (DELETE EVERYTHING)"
    )
    reset_parser.add_argument(
        "--confirm",
        action="store_true",
        help="Confirm the reset operation"
    )
    
    # Storage delete
    delete_parser = storage_subparsers.add_parser(
        "delete",
        help="Delete a specific embedding"
    )
    delete_parser.add_argument(
        "embedding_name",
        help="Name of embedding to delete"
    )
    
    return parser


@handle_command_errors
def handle_generate(args) -> int:
    """Handle generate command."""
    from services.embedding_service import EmbeddingService
    
    service = EmbeddingService()
    show_progress = not args.no_progress
    service.generate_embedding(args.path, args.name, args.ignore_file, show_progress)
    return EXIT_SUCCESS


@handle_command_errors
def handle_query(args) -> int:
    """Handle query command."""
    from commands.query import execute_query_command
    
    execute_query_command(args)
    return EXIT_SUCCESS


@handle_command_errors
def handle_select(args) -> int:
    """Handle select command with optional direct embedding selection."""
    from services.embedding_service import EmbeddingService
    from config.settings import get_settings_manager
    
    logger = get_logger(__name__)
    service = EmbeddingService()
    
    if args.embeddings:
        # Direct selection via CLI arguments
        embedding_names = args.embeddings
        logger.info("🎯 Setting active embeddings: %s", ', '.join(embedding_names))
        
        # Validate that embeddings exist
        available = service.list_embeddings()
        invalid = [name for name in embedding_names if name not in available]
        
        if invalid:
            logger.error("❌ Invalid embedding names: %s", ', '.join(invalid))
            logger.info("Available embeddings: %s", ', '.join(available))
            return EXIT_ERROR
        
        # Set active embeddings directly
        settings_manager = get_settings_manager()
        settings_manager.set_active_embeddings(embedding_names)
        logger.info("✅ Selected embeddings: %s", ', '.join(embedding_names))
    else:
        # Interactive selection
        logger.info("🎯 Select active embeddings for queries\n")
        service.select_embeddings()
    
    return EXIT_SUCCESS




@handle_command_errors
def handle_ask(args) -> int:
    """Handle ask command."""
    from services.embedding_service import AIService
    
    service = AIService()
    service.ask_question(args.question)
    return EXIT_SUCCESS


@handle_command_errors
def handle_chat(args) -> int:
    """Handle chat command."""
    from services.embedding_service import AIService
    
    service = AIService()
    service.start_chat()
    return EXIT_SUCCESS


@handle_command_errors
def handle_config(args) -> int:
    """Handle config command."""
    from config.settings import get_settings_manager
    
    logger = get_logger(__name__)
    settings_manager = get_settings_manager()
    
    if args.config_action == "set":
        if args.claude_key:
            logger.info("🔑 Setting Claude API key...")
            settings_manager.set_claude_api_key(args.claude_key)
            logger.info("✅ Claude API key configured successfully")
        else:
            logger.error("❌ No configuration option provided")
            return 1
    elif args.config_action == "list":
        logger.info("📋 Current configuration:")
        config = settings_manager.get_config()
        
        # Show general config
        logger.info("Storage path: %s", config.storage.base_path)
        logger.info("Active provider: %s", config.active_provider)
        logger.info("System prompt strategy: %s", config.system_prompt_strategy)
        
        # Show Claude config if available
        claude_config = config.ai.get("claude")
        if claude_config:
            logger.info("Claude model: %s", claude_config.default_model)
            logger.info("Claude max tokens: %s", claude_config.max_tokens)
            logger.info("Claude API key: %s", "***configured***" if claude_config.api_key else "not set")
        else:
            logger.info("Claude: not configured")
        
        # Show active embeddings
        active = settings_manager.get_active_embeddings()
        if active.selected:
            logger.info("Active embeddings: %s", ", ".join(active.selected))
        else:
            logger.info("Active embeddings: none selected")
            
    else:
        logger.error("❌ Unknown config action")
        return 1
        
    return 0


@handle_command_errors
def handle_storage(args) -> int:
    """Handle storage command."""
    from utils.storage import get_storage_manager
    
    logger = get_logger(__name__)
    storage_manager = get_storage_manager()
    
    if args.storage_action == "info":
        logger.info("📊 Storage Information:")
        storage_info = storage_manager.get_storage_info()
        
        if "error" in storage_info:
            logger.error("❌ Error getting storage info: %s", storage_info["error"])
            return 1
        
        logger.info("Base path: %s", storage_info["base_path"])
        logger.info("Total size: %s MB", storage_info["total_size_mb"])
        logger.info("Embeddings count: %d", storage_info["embeddings_count"])
        
        if storage_info["embeddings"]:
            logger.info("Available embeddings: %s", ", ".join(storage_info["embeddings"]))
        else:
            logger.info("Available embeddings: none")
        
        # Show directory sizes
        logger.info("Directory breakdown:")
        for dir_name, size_bytes in storage_info["directory_sizes"].items():
            size_mb = round(size_bytes / (1024 * 1024), 2)
            logger.info("  %s: %s MB", dir_name, size_mb)
            
    elif args.storage_action == "cleanup":
        logger.info("🧹 Cleaning up temporary files older than %d hours...", args.hours)
        cleaned_count = storage_manager.cleanup_temp_files(args.hours)
        logger.info("✅ Cleaned up %d temporary files", cleaned_count)
        
    elif args.storage_action == "reset":
        if not args.confirm:
            logger.error("❌ Reset requires --confirm flag")
            logger.error("⚠️  This will DELETE ALL embeddings, configuration, and data!")
            logger.error("Usage: context-ai storage reset --confirm")
            return 1
        
        logger.warning("🚨 RESETTING ALL STORAGE - This will delete everything!")
        success = storage_manager.reset_storage(confirm=True)
        if success:
            logger.info("✅ Storage reset complete")
        else:
            logger.error("❌ Storage reset failed")
            return 1
            
    elif args.storage_action == "delete":
        embedding_name = args.embedding_name
        logger.info("🗑️  Deleting embedding: %s", embedding_name)
        
        if not storage_manager.embedding_exists(embedding_name):
            logger.error("❌ Embedding '%s' does not exist", embedding_name)
            return 1
        
        success = storage_manager.delete_embedding(embedding_name)
        if success:
            logger.info("✅ Embedding '%s' deleted successfully", embedding_name)
        else:
            logger.error("❌ Failed to delete embedding '%s'", embedding_name)
            return 1
            
    else:
        logger.error("❌ Unknown storage action: %s", args.storage_action)
        return 1
        
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)
    
    # Handle no command provided
    if not args.command:
        parser.print_help()
        return 1
    
    # Setup logging
    setup_logging(verbose=args.verbose)
    logger = get_logger(__name__)
    
    if args.verbose:
        logger.info("🔧 Verbose mode enabled")
        logger.debug("CLI arguments: %s", vars(args))
    
    # Route to command handlers
    if args.command == "generate":
        return handle_generate(args)
    elif args.command == "select":
        return handle_select(args)
    elif args.command == "query":
        return handle_query(args)
    elif args.command == "ask":
        return handle_ask(args)
    elif args.command == "chat":
        return handle_chat(args)
    elif args.command == "config":
        return handle_config(args)
    elif args.command == "storage":
        return handle_storage(args)
    else:
        print(f"❌ Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())