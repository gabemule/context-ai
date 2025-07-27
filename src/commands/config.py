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

    # Config guidelines
    config_guidelines = config_subparsers.add_parser(
        "guidelines", help="Manage coding guidelines"
    )
    guidelines_subparsers = config_guidelines.add_subparsers(
        dest="guidelines_action", help="Guidelines actions"
    )

    # Guidelines list
    guidelines_list = guidelines_subparsers.add_parser(
        "list", help="List available guidelines"
    )

    # Guidelines show
    guidelines_show = guidelines_subparsers.add_parser(
        "show", help="Show content of a specific guideline"
    )
    guidelines_show.add_argument("language", help="Language to show (e.g., python, javascript)")

    # Guidelines edit
    guidelines_edit = guidelines_subparsers.add_parser(
        "edit", help="Edit a specific guideline in your default editor"
    )
    guidelines_edit.add_argument("language", help="Language to edit (e.g., python, javascript)")

    # Guidelines reset
    guidelines_reset = guidelines_subparsers.add_parser(
        "reset", help="Reset a guideline to default content"
    )
    guidelines_reset.add_argument("language", help="Language to reset (e.g., python, javascript)")

    # Guidelines path
    guidelines_path = guidelines_subparsers.add_parser(
        "path", help="Show file path for guidelines directory"
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

    elif args.config_action == "guidelines":
        from config.guidelines.manager import get_guidelines_manager
        
        guidelines_manager = get_guidelines_manager()
        
        if args.guidelines_action == "list":
            logger.info("📋 Available coding guidelines:")
            available = guidelines_manager.list_available_guidelines()
            
            if available:
                for language in available:
                    logger.info("  🔸 %s", language)
                logger.info("")
                logger.info("💡 Usage:")
                logger.info("  context-ai config guidelines show <language>")
                logger.info("  context-ai config guidelines edit <language>")
            else:
                logger.warning("⚠️  No guidelines found. They will be created on first use.")
            
        elif args.guidelines_action == "show":
            language = args.language.lower()
            content = guidelines_manager.get_guideline_content(language)
            
            if content:
                logger.info("📋 Guidelines for %s:", language)
                logger.info("=" * 50)
                print(content)  # Print directly for clean formatting
                logger.info("=" * 50)
            else:
                logger.error("❌ No guidelines found for language: %s", language)
                available = guidelines_manager.list_available_guidelines()
                if available:
                    logger.info("Available languages: %s", ", ".join(available))
                return 1
                
        elif args.guidelines_action == "edit":
            language = args.language.lower()
            file_path = guidelines_manager.get_guideline_file_path(language)
            
            # Create file with default content if it doesn't exist
            if not file_path.exists():
                logger.info("📝 Creating default guidelines for %s...", language)
                if not guidelines_manager.reset_guideline_to_default(language):
                    logger.error("❌ Failed to create default guidelines for %s", language)
                    return 1
            
            # Open in default editor
            import os
            import subprocess
            import platform
            
            try:
                logger.info("📝 Opening %s for editing...", file_path)
                
                # Use platform-appropriate editor
                if platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", str(file_path)])
                elif platform.system() == "Windows":
                    os.startfile(str(file_path))
                else:  # Linux
                    editor = os.environ.get("EDITOR", "nano")
                    subprocess.run([editor, str(file_path)])
                
                logger.info("✅ Guidelines will be reloaded automatically when you ask questions")
                
            except Exception as e:
                logger.error("❌ Failed to open editor: %s", e)
                logger.info("📁 You can manually edit: %s", file_path)
                return 1
                
        elif args.guidelines_action == "reset":
            language = args.language.lower()
            
            logger.info("🔄 Resetting %s guidelines to default...", language)
            if guidelines_manager.reset_guideline_to_default(language):
                logger.info("✅ Guidelines for %s reset successfully", language)
            else:
                logger.error("❌ Failed to reset guidelines for %s", language)
                return 1
                
        elif args.guidelines_action == "path":
            guidelines_dir = guidelines_manager._get_guidelines_directory()
            logger.info("📁 Guidelines directory: %s", guidelines_dir)
            
            # Show file listing
            if guidelines_dir.exists():
                files = list(guidelines_dir.glob("*.md"))
                if files:
                    logger.info("📋 Available files:")
                    for file_path in sorted(files):
                        logger.info("  📄 %s", file_path.name)
                else:
                    logger.info("📁 Directory exists but no guideline files found")
            else:
                logger.info("📁 Directory will be created on first use")
                
        else:
            logger.error("❌ Unknown guidelines action: %s", args.guidelines_action)
            return 1

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
