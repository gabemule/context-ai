"""
Config command implementation for Context-AI.

Provides configuration management functionality.
"""

import argparse

from utils.error_handler import handle_command_errors
from utils.logging import get_logger


def add_config_parser(subparsers) -> argparse.ArgumentParser:
    """Add config command to CLI parser."""
    parser = subparsers.add_parser("config", help="Manage configuration")

    config_subparsers = parser.add_subparsers(
        dest="config_action", help="Configuration actions"
    )

    # Config set
    config_set = config_subparsers.add_parser("set", help="Set configuration value")
    config_set.add_argument("--claude-key", help="Set Claude API key")
    config_set.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed processing information",
    )

    # Config list
    config_list = config_subparsers.add_parser(
        "list", help="List current configuration"
    )
    config_list.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed processing information",
    )

    # Config test
    config_test = config_subparsers.add_parser("test", help="Test API key connectivity")
    config_test.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed processing information",
    )

    # Config validate
    config_validate = config_subparsers.add_parser(
        "validate", help="Validate configuration and diagnose issues"
    )
    config_validate.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed processing information",
    )

    parser.set_defaults(func=execute_config_command)
    return parser


@handle_command_errors
def execute_config_command(args: argparse.Namespace) -> int:
    """
    Execute the config command.

    Args:
        args: Parsed command line arguments
    """
    logger = get_logger(__name__)

    from config.settings import get_settings_manager

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
            logger.info(
                "Claude API key: %s",
                "***configured***" if claude_config.api_key else "not set",
            )
        else:
            logger.info("Claude: not configured")

        # Show active embeddings
        active = settings_manager.get_active_embeddings()
        if active.selected:
            logger.info("Active embeddings: %s", ", ".join(active.selected))
        else:
            logger.info("Active embeddings: none selected")

    elif args.config_action == "test":
        logger.info("🔍 Testing API key connectivity...")
        config = settings_manager.get_config()
        claude_config = config.ai.get("claude")

        if not claude_config or not claude_config.api_key:
            logger.error("❌ No Claude API key configured")
            logger.info(
                "Set your API key with: context-ai config set --claude-key YOUR_KEY"
            )
            return 1

        from core.ai.claude_client import get_claude_client

        try:
            client = get_claude_client(
                claude_config.api_key, claude_config.default_model
            )
            if client.validate_connection():
                logger.info("✅ Claude API key is valid and working")
                return 0
            else:
                logger.error("❌ Claude API key validation failed")
                return 1
        except Exception as e:
            logger.error("❌ Error testing connection: %s", e)
            return 1

    elif args.config_action == "validate":
        logger.info("🔧 Validating configuration...")
        config = settings_manager.get_config()
        issues = []

        # Check Claude configuration
        claude_config = config.ai.get("claude")
        if not claude_config:
            issues.append("❌ Claude configuration missing")
        elif not claude_config.api_key:
            issues.append("❌ Claude API key not set")
        elif not claude_config.api_key.startswith("sk-ant-"):
            issues.append("❌ Claude API key format invalid")
        else:
            logger.info("✅ Claude API key configured")

        # Check active embeddings
        active = settings_manager.get_active_embeddings()
        if not active.selected:
            issues.append("⚠️  No active embeddings selected")
        else:
            logger.info("✅ Active embeddings: %s", ", ".join(active.selected))

        # Check storage
        from utils.storage import get_storage_manager

        storage_manager = get_storage_manager()
        storage_info = storage_manager.get_storage_info()

        if storage_info.get("embeddings_count", 0) == 0:
            issues.append("⚠️  No embeddings generated yet")
        else:
            logger.info(
                "✅ Storage: %d embeddings available", storage_info["embeddings_count"]
            )

        # Report results
        if issues:
            logger.warning("Configuration issues found:")
            for issue in issues:
                logger.warning("  %s", issue)
            return 1
        else:
            logger.info("✅ Configuration is valid and ready to use!")
            return 0

    else:
        logger.error("❌ Unknown config action")
        return 1

    return 0


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
    add_config_parser(subparsers)

    # Test with sample args
    test_args = parser.parse_args(["config", "list", "--verbose"])
    execute_config_command(test_args)
