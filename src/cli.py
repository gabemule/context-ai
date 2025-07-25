#!/usr/bin/env python3
"""
Context-AI CLI entry point.
Cross-project code intelligence assistant.
"""

import argparse
import os
import sys
from typing import List, Optional

from utils.logging import get_logger, setup_logging

# Silence HuggingFace tokenizers warning about forking
os.environ["TOKENIZERS_PARALLELISM"] = "false"


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        prog="context-ai",
        description="Cross-project code intelligence assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
💡 Quick Start Examples:

  📁 Generate embeddings:
    context-ai generate ./my-project --name "project-v1"
    context-ai generate ./docs --name "documentation"

  🎯 Select active embeddings:
    context-ai select                    # Interactive selection
    context-ai select project-v1 docs   # Direct selection

  🔍 Query for context:
    context-ai query "authentication patterns" --format markdown
    context-ai query "error handling" --copy --output results.txt

  🤖 AI-powered assistance:
    context-ai ask "How do I implement authentication?"
    context-ai ask "Show me validation patterns" --format json --copy
    context-ai chat                      # Interactive chat session

  ⚙️  Configuration:
    context-ai config set --claude-key sk-ant-xxxxx
    context-ai config list              # Show current settings
    context-ai config test              # Test API connectivity

  🗄️  Storage management:
    context-ai storage info             # Show storage stats
    context-ai storage cleanup          # Clean temporary files
    context-ai storage delete old-embedding

💡 Pro Tips:
  - Use --verbose with any command for detailed output
  - Combine --copy and --output for maximum productivity
  - JSON/XML formats are great for tool integration
        """,
    )

    parser.add_argument("--version", action="version", version="context-ai 0.1.0")

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    # Create subparsers for commands
    subparsers = parser.add_subparsers(
        dest="command", help="Available commands", metavar="COMMAND"
    )

    # Import command modules and add their parsers
    from commands.ask import add_ask_parser
    from commands.chat import add_chat_parser
    from commands.config import add_config_parser
    from commands.generate import add_generate_parser
    from commands.query import add_query_parser
    from commands.select import add_select_parser
    from commands.storage import add_storage_parser

    # Add all command parsers
    add_generate_parser(subparsers)
    add_select_parser(subparsers)
    add_query_parser(subparsers)
    add_ask_parser(subparsers)
    add_chat_parser(subparsers)
    add_config_parser(subparsers)
    add_storage_parser(subparsers)

    return parser


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

    # Use the function dispatcher pattern established by command modules
    if hasattr(args, "func"):
        return args.func(args)
    else:
        logger.error("❌ Unknown command: %s", args.command)
        return 1


if __name__ == "__main__":
    sys.exit(main())
