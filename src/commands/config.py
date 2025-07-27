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
    config_set.add_argument("--provider", help="Set active AI provider (e.g., claude)")
    config_set.add_argument("--model", help="Set model for active provider (e.g., claude-3-5-haiku, claude-3-5-sonnet, claude-opus-4)")
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

    # Config models
    config_models = config_subparsers.add_parser(
        "models", help="List available models for providers"
    )
    config_models.add_argument(
        "--provider", help="Show models for specific provider (default: all)"
    )
    config_models.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed model information",
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
        any_option_set = False
        
        if args.claude_key:
            logger.info("🔑 Setting Claude API key...")
            settings_manager.set_claude_api_key(args.claude_key)
            logger.info("✅ Claude API key configured successfully")
            any_option_set = True
            
        if args.provider:
            logger.info("🔄 Setting active provider...")
            from config.providers import get_available_providers, get_available_models
            available_providers = get_available_providers()
            
            if args.provider not in available_providers:
                logger.error("❌ Invalid provider: %s", args.provider)
                logger.info("Available providers: %s", ", ".join(available_providers))
                return 1
                
            settings_manager.set_active_provider(args.provider)
            logger.info("✅ Active provider set to: %s", args.provider)
            
            # Se não especificou modelo, define o padrão do provider
            if not args.model:
                available_models = get_available_models(args.provider)
                if available_models:
                    default_model = available_models[0]  # Primeiro modelo = padrão
                    settings_manager.set_model(default_model)
                    logger.info("✅ Default model set to: %s", default_model)
            
            any_option_set = True
            
        if args.model:
            logger.info("🎯 Setting model...")
            config = settings_manager.get_config()
            active_provider = config.active_provider
            
            from config.providers import get_available_models
            available_models = get_available_models(active_provider)
            
            if args.model not in available_models:
                logger.error("❌ Invalid model for provider %s: %s", active_provider, args.model)
                logger.info("Available models: %s", ", ".join(available_models))
                return 1
                
            settings_manager.set_model(args.model)
            logger.info("✅ Model set to: %s", args.model)
            any_option_set = True
            
        if not any_option_set:
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

    elif args.config_action == "models":
        logger.info("🤖 Available AI models:")
        
        from config.providers import get_available_providers, get_available_models, CLAUDE_MODELS
        
        if args.provider:
            # Show models for specific provider
            if args.provider not in get_available_providers():
                logger.error("❌ Invalid provider: %s", args.provider)
                logger.info("Available providers: %s", ", ".join(get_available_providers()))
                return 1
                
            models = get_available_models(args.provider)
            logger.info("📋 %s models:", args.provider.title())
            
            for i, model in enumerate(models):
                prefix = "🔸" if i == 0 else "  "  # First model = default
                default_suffix = " (default)" if i == 0 else ""
                
                if args.verbose and args.provider == "claude":
                    # Show detailed info for Claude models
                    model_info = CLAUDE_MODELS.get(model, {})
                    speed = model_info.get("speed", "unknown")
                    description = model_info.get("description", "")
                    max_output = model_info.get("max_output_tokens", "unknown")
                    
                    logger.info("%s %s%s - %s (%s speed, %s max tokens)", 
                              prefix, model, default_suffix, description, speed, max_output)
                else:
                    logger.info("%s %s%s", prefix, model, default_suffix)
        else:
            # Show all providers and their models
            for provider in get_available_providers():
                models = get_available_models(provider)
                logger.info("📋 %s models:", provider.title())
                
                for i, model in enumerate(models):
                    prefix = "🔸" if i == 0 else "  "  # First model = default
                    default_suffix = " (default)" if i == 0 else ""
                    logger.info("%s %s%s", prefix, model, default_suffix)
                
                logger.info("")  # Empty line between providers

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
