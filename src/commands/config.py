"""
Config command implementation for Context-AI.

Clean Architecture approach with separated responsibilities in a single file.
"""

import argparse
from typing import List

from utils.error_handler import handle_command_errors
from utils.logging import get_logger


# =============================================================================
# HELP CONSTANTS (Separated from implementation for DRY/SRP)
# =============================================================================

CONFIG_SET_HELP = {
    "help": "Configure Context-AI settings",
    "description": "Set configuration values for AI providers, API keys, and models. "
                  "This command allows you to configure your Context-AI installation with "
                  "the necessary credentials and preferences.",
    "epilog": """
Examples:
  context-ai config set --claude-key sk-ant-...                          # Set Claude API key
  context-ai config set --provider claude                                # Set active provider
  context-ai config set --provider claude --model claude-3-7-sonnet      # Set provider + model
  context-ai config set --model claude-sonnet-4                          # Change model only
  context-ai config set --claude-key sk-ant-... --verbose                # Verbose output
    """,
    "arguments": {
        "claude_key": "Set Claude API key (starts with 'sk-ant-'). Get your key from https://console.anthropic.com/",
        "provider": "Set active AI provider. Currently supported: claude. Setting a provider will automatically set its default model.",
        "model": "Set model for the active provider. Use 'context-ai config models' to see available models for each provider.",
        "verbose": "Show detailed information during configuration process"
    }
}

CONFIG_LIST_HELP = {
    "help": "Display current Context-AI configuration",
    "description": "Show organized view of all Context-AI settings including AI provider, "
                  "embeddings, prompt system, processing options, and storage configuration.",
    "epilog": """
Examples:
  context-ai config list                    # Show basic configuration overview
  context-ai config list --verbose         # Show detailed settings with file types
  context-ai config list -v                # Short form for verbose output
    """,
    "arguments": {
        "verbose": "Show detailed configuration including file types, storage stats, processing details, and extended settings information"
    }
}

CONFIG_TEST_HELP = {
    "help": "Test API key connectivity",
    "description": "Validate that your AI provider API key is working correctly by making "
                  "a test connection. This helps diagnose authentication issues and "
                  "ensures your configuration is ready for use.",
    "epilog": """
Examples:
  context-ai config test                    # Test active provider connection
  context-ai config test --verbose         # Test with detailed diagnostic info
  context-ai config test -v                # Short form for verbose testing
    """,
    "arguments": {
        "verbose": "Show detailed diagnostic information during connection testing, including API response details and error specifics"
    }
}

CONFIG_VALIDATE_HELP = {
    "help": "Validate configuration and diagnose issues",
    "description": "Comprehensive validation of your Context-AI configuration including "
                  "API keys, embeddings, storage, and all system components. "
                  "Identifies and reports configuration problems with suggestions for fixes.",
    "epilog": """
Examples:
  context-ai config validate               # Basic configuration validation
  context-ai config validate --verbose     # Detailed validation with diagnostic info
  context-ai config validate -v            # Short form for verbose validation
    """,
    "arguments": {
        "verbose": "Show detailed validation information including component-specific checks and diagnostic details"
    }
}

CONFIG_MODELS_HELP = {
    "help": "List available AI models for providers",
    "description": "Display all available AI models for each provider, including "
                  "model specifications, capabilities, and recommendations. "
                  "Use this to choose the best model for your use case.",
    "epilog": """
Examples:
  context-ai config models                 # List all models for all providers
  context-ai config models --provider claude    # List models for specific provider
  context-ai config models --verbose       # Show detailed model information
  context-ai config models --provider claude -v # Claude models with details
    """,
    "arguments": {
        "provider": "Show models for specific provider only (default: show all providers)",
        "verbose": "Show detailed model information including descriptions, speeds, token limits, and capabilities"
    }
}

CONFIG_GUIDELINES_HELP = {
    "help": "Manage coding guidelines",
    "description": "Manage Context-AI coding guidelines that influence AI responses. "
                  "Guidelines help ensure consistent code style and best practices "
                  "across your projects.",
    "arguments": {}
}

CONFIG_LANGUAGES_HELP = {
    "help": "Manage programming languages configuration",
    "description": "View and manage supported programming languages, their file extensions, "
                  "and chunking configurations. This allows you to see what languages "
                  "are supported and customize their behavior.",
    "arguments": {}
}

GUIDELINES_SUBCOMMANDS_HELP = {
    "list": {
        "help": "List available coding guidelines",
        "description": "Show all available coding guidelines that can be used to influence AI responses for different programming languages.",
        "epilog": """
Examples:
  context-ai config guidelines list        # Show all available guidelines
        """
    },
    "show": {
        "help": "Display content of a specific guideline",
        "description": "Show the full content of coding guidelines for a specific programming language.",
        "epilog": """
Examples:
  context-ai config guidelines show python     # Show Python guidelines
  context-ai config guidelines show javascript # Show JavaScript guidelines
        """,
        "arguments": {
            "language": "Programming language to show guidelines for (e.g., python, javascript, typescript)"
        }
    },
    "edit": {
        "help": "Edit a specific guideline in your default editor",
        "description": "Open coding guidelines for a specific language in your system's default editor. "
                      "If the guideline doesn't exist, it will be created with default content.",
        "epilog": """
Examples:
  context-ai config guidelines edit python     # Edit Python guidelines
  context-ai config guidelines edit javascript # Edit JavaScript guidelines
        """,
        "arguments": {
            "language": "Programming language to edit guidelines for (e.g., python, javascript, typescript)"
        }
    },
    "reset": {
        "help": "Reset a guideline to default content",
        "description": "Reset coding guidelines for a specific language back to the default template. "
                      "This will overwrite any custom changes you've made.",
        "epilog": """
Examples:
  context-ai config guidelines reset python     # Reset Python guidelines to default
  context-ai config guidelines reset javascript # Reset JavaScript guidelines to default
        """,
        "arguments": {
            "language": "Programming language to reset guidelines for (e.g., python, javascript, typescript)"
        }
    },
    "path": {
        "help": "Show file path for guidelines directory",
        "description": "Display the file system path where coding guidelines are stored, "
                      "along with a listing of available guideline files.",
        "epilog": """
Examples:
  context-ai config guidelines path        # Show guidelines directory and files
        """
    }
}

LANGUAGES_SUBCOMMANDS_HELP = {
    "list": {
        "help": "List all configured programming languages",
        "description": "Show all supported programming languages with their file extensions, chunking priorities, and guidelines status.",
        "epilog": """
Examples:
  context-ai config languages list         # Show all configured languages
        """
    },
    "show": {
        "help": "Show detailed configuration for a specific language",
        "description": "Display complete configuration for a language including extensions, separators, inheritance, and guidelines status.",
        "epilog": """
Examples:
  context-ai config languages show python      # Show Python language configuration
  context-ai config languages show vue         # Show Vue configuration (with inheritance)
        """,
        "arguments": {
            "language": "Programming language to show configuration for (e.g., python, javascript, vue, go)"
        }
    },
    "reset": {
        "help": "Reset a language configuration to default",
        "description": "Reset language configuration back to the default template. "
                      "This will overwrite any custom changes you've made to the language settings.",
        "epilog": """
Examples:
  context-ai config languages reset python     # Reset Python configuration to default
  context-ai config languages reset vue        # Reset Vue configuration to default
        """,
        "arguments": {
            "language": "Programming language to reset configuration for (e.g., python, javascript, vue)"
        }
    },
    "path": {
        "help": "Show path to languages configuration file",
        "description": "Display the file system path where language configurations are stored, "
                      "along with configuration statistics and validation status.",
        "epilog": """
Examples:
  context-ai config languages path         # Show languages configuration file and stats
        """
    }
}


def add_config_parser(subparsers) -> argparse.ArgumentParser:
    """Add config command to CLI parser."""
    parser = subparsers.add_parser("config", help="Manage configuration")

    config_subparsers = parser.add_subparsers(dest="config_action", help="Configuration actions")

    # Config set
    config_set = config_subparsers.add_parser(
        "set", 
        help=CONFIG_SET_HELP["help"],
        description=CONFIG_SET_HELP["description"],
        epilog=CONFIG_SET_HELP["epilog"]
    )
    config_set.add_argument("--claude-key", help=CONFIG_SET_HELP["arguments"]["claude_key"])
    config_set.add_argument("--provider", help=CONFIG_SET_HELP["arguments"]["provider"])
    config_set.add_argument("--model", help=CONFIG_SET_HELP["arguments"]["model"])
    config_set.add_argument("--verbose", "-v", action="store_true", help=CONFIG_SET_HELP["arguments"]["verbose"])

    # Config list
    config_list = config_subparsers.add_parser(
        "list", 
        help=CONFIG_LIST_HELP["help"],
        description=CONFIG_LIST_HELP["description"],
        epilog=CONFIG_LIST_HELP["epilog"]
    )
    config_list.add_argument("--verbose", "-v", action="store_true", help=CONFIG_LIST_HELP["arguments"]["verbose"])

    # Config test
    config_test = config_subparsers.add_parser(
        "test", 
        help=CONFIG_TEST_HELP["help"],
        description=CONFIG_TEST_HELP["description"],
        epilog=CONFIG_TEST_HELP["epilog"]
    )
    config_test.add_argument("--verbose", "-v", action="store_true", help=CONFIG_TEST_HELP["arguments"]["verbose"])

    # Config validate
    config_validate = config_subparsers.add_parser(
        "validate", 
        help=CONFIG_VALIDATE_HELP["help"],
        description=CONFIG_VALIDATE_HELP["description"],
        epilog=CONFIG_VALIDATE_HELP["epilog"]
    )
    config_validate.add_argument("--verbose", "-v", action="store_true", help=CONFIG_VALIDATE_HELP["arguments"]["verbose"])

    # Config models
    config_models = config_subparsers.add_parser(
        "models", 
        help=CONFIG_MODELS_HELP["help"],
        description=CONFIG_MODELS_HELP["description"],
        epilog=CONFIG_MODELS_HELP["epilog"]
    )
    config_models.add_argument("--provider", help=CONFIG_MODELS_HELP["arguments"]["provider"])
    config_models.add_argument("--verbose", "-v", action="store_true", help=CONFIG_MODELS_HELP["arguments"]["verbose"])

    # Config guidelines
    config_guidelines = config_subparsers.add_parser(
        "guidelines", 
        help=CONFIG_GUIDELINES_HELP["help"],
        description=CONFIG_GUIDELINES_HELP["description"]
    )
    guidelines_subparsers = config_guidelines.add_subparsers(dest="guidelines_action", help="Guidelines actions")
    
    # Guidelines subcommands
    guidelines_list = guidelines_subparsers.add_parser(
        "list", 
        help=GUIDELINES_SUBCOMMANDS_HELP["list"]["help"],
        description=GUIDELINES_SUBCOMMANDS_HELP["list"]["description"],
        epilog=GUIDELINES_SUBCOMMANDS_HELP["list"]["epilog"]
    )
    
    guidelines_show = guidelines_subparsers.add_parser(
        "show", 
        help=GUIDELINES_SUBCOMMANDS_HELP["show"]["help"],
        description=GUIDELINES_SUBCOMMANDS_HELP["show"]["description"],
        epilog=GUIDELINES_SUBCOMMANDS_HELP["show"]["epilog"]
    )
    guidelines_show.add_argument("language", help=GUIDELINES_SUBCOMMANDS_HELP["show"]["arguments"]["language"])
    
    guidelines_edit = guidelines_subparsers.add_parser(
        "edit", 
        help=GUIDELINES_SUBCOMMANDS_HELP["edit"]["help"],
        description=GUIDELINES_SUBCOMMANDS_HELP["edit"]["description"],
        epilog=GUIDELINES_SUBCOMMANDS_HELP["edit"]["epilog"]
    )
    guidelines_edit.add_argument("language", help=GUIDELINES_SUBCOMMANDS_HELP["edit"]["arguments"]["language"])
    
    guidelines_reset = guidelines_subparsers.add_parser(
        "reset", 
        help=GUIDELINES_SUBCOMMANDS_HELP["reset"]["help"],
        description=GUIDELINES_SUBCOMMANDS_HELP["reset"]["description"],
        epilog=GUIDELINES_SUBCOMMANDS_HELP["reset"]["epilog"]
    )
    guidelines_reset.add_argument("language", help=GUIDELINES_SUBCOMMANDS_HELP["reset"]["arguments"]["language"])
    
    guidelines_path = guidelines_subparsers.add_parser(
        "path", 
        help=GUIDELINES_SUBCOMMANDS_HELP["path"]["help"],
        description=GUIDELINES_SUBCOMMANDS_HELP["path"]["description"],
        epilog=GUIDELINES_SUBCOMMANDS_HELP["path"]["epilog"]
    )

    # Config languages
    config_languages = config_subparsers.add_parser(
        "languages", 
        help=CONFIG_LANGUAGES_HELP["help"],
        description=CONFIG_LANGUAGES_HELP["description"]
    )
    languages_subparsers = config_languages.add_subparsers(dest="languages_action", help="Languages actions")
    
    # Languages subcommands
    languages_list = languages_subparsers.add_parser(
        "list", 
        help=LANGUAGES_SUBCOMMANDS_HELP["list"]["help"],
        description=LANGUAGES_SUBCOMMANDS_HELP["list"]["description"],
        epilog=LANGUAGES_SUBCOMMANDS_HELP["list"]["epilog"]
    )
    
    languages_show = languages_subparsers.add_parser(
        "show", 
        help=LANGUAGES_SUBCOMMANDS_HELP["show"]["help"],
        description=LANGUAGES_SUBCOMMANDS_HELP["show"]["description"],
        epilog=LANGUAGES_SUBCOMMANDS_HELP["show"]["epilog"]
    )
    languages_show.add_argument("language", help=LANGUAGES_SUBCOMMANDS_HELP["show"]["arguments"]["language"])
    
    languages_reset = languages_subparsers.add_parser(
        "reset", 
        help=LANGUAGES_SUBCOMMANDS_HELP["reset"]["help"],
        description=LANGUAGES_SUBCOMMANDS_HELP["reset"]["description"],
        epilog=LANGUAGES_SUBCOMMANDS_HELP["reset"]["epilog"]
    )
    languages_reset.add_argument("language", help=LANGUAGES_SUBCOMMANDS_HELP["reset"]["arguments"]["language"])
    
    languages_path = languages_subparsers.add_parser(
        "path", 
        help=LANGUAGES_SUBCOMMANDS_HELP["path"]["help"],
        description=LANGUAGES_SUBCOMMANDS_HELP["path"]["description"],
        epilog=LANGUAGES_SUBCOMMANDS_HELP["path"]["epilog"]
    )

    parser.set_defaults(func=execute_config_command)
    return parser


@handle_command_errors
def execute_config_command(args: argparse.Namespace) -> int:
    """Execute the config command using clean handlers."""
    logger = get_logger(__name__)
    
    from config.settings import get_settings_manager
    settings_manager = get_settings_manager()
    
    # Route to appropriate handler (Strategy Pattern)
    handlers = {
        "set": _handle_config_set,
        "list": _handle_config_list,
        "test": _handle_config_test,
        "validate": _handle_config_validate,
        "models": _handle_config_models,
        "guidelines": _handle_config_guidelines,
        "languages": _handle_config_languages
    }
    
    handler = handlers.get(args.config_action)
    if handler:
        return handler(args, settings_manager, logger)
    else:
        logger.error("❌ Unknown config action")
        return 1


# =============================================================================
# CONFIG HANDLERS (Clean separation of concerns)
# =============================================================================

def _handle_config_set(args, settings_manager, logger) -> int:
    """Handle configuration setting (SRP)."""
    any_option_set = False
    
    if args.claude_key:
        logger.info("🔑 Setting Claude API key...")
        settings_manager.set_claude_api_key(args.claude_key)
        logger.info("✅ Claude API key configured successfully")
        any_option_set = True
        
    if args.provider:
        if not _set_provider(args.provider, args.model, settings_manager, logger):
            return 1
        any_option_set = True
        
    if args.model:
        if not _set_model(args.model, settings_manager, logger):
            return 1
        any_option_set = True
        
    if not any_option_set:
        logger.error("❌ No configuration option provided")
        return 1
        
    return 0


def _handle_config_list(args, settings_manager, logger) -> int:
    """Handle configuration display (SRP)."""
    _display_configuration(settings_manager, logger, args.verbose)
    return 0


def _handle_config_test(args, settings_manager, logger) -> int:
    """Handle API connectivity testing (OCP - extensible for any provider)."""
    logger.info("🔍 Testing API key connectivity...")
    config = settings_manager.get_config()
    
    active_provider = config.active_provider
    if not active_provider:
        logger.error("❌ No active AI provider configured")
        return 1
    
    provider_config = config.ai.get(active_provider)
    if not provider_config or not provider_config.api_key:
        logger.error("❌ No %s API key configured", active_provider.title())
        logger.info("Set your API key with: context-ai config set --%s-key YOUR_KEY", active_provider)
        return 1

    # Provider-specific testing (extensible)
    try:
        if active_provider == "claude":
            from core.ai.claude_client import get_claude_client
            client = get_claude_client(provider_config.api_key, provider_config.default_model)
            if client.validate_connection():
                logger.info("✅ %s API key is valid and working", active_provider.title())
                return 0
            else:
                logger.error("❌ %s API key validation failed", active_provider.title())
                return 1
        # Future providers can be added here
        # elif active_provider == "openai":
        #     from core.ai.openai_client import get_openai_client
        #     client = get_openai_client(provider_config.api_key, provider_config.default_model)
        #     ...
        else:
            logger.error("❌ API testing not implemented for provider: %s", active_provider)
            return 1
            
    except Exception as e:
        logger.error("❌ Error testing %s connection: %s", active_provider.title(), e)
        return 1


def _handle_config_validate(args, settings_manager, logger) -> int:
    """Handle configuration validation (SRP)."""
    logger.info("🔧 Validating configuration...")
    config = settings_manager.get_config()
    issues = []

    # Validate active provider configuration
    _validate_active_provider_config(config, issues, logger)
    
    # Validate embeddings
    _validate_embeddings(settings_manager, issues, logger)
    
    # Validate storage
    _validate_storage(issues, logger)

    # Report results
    if issues:
        logger.warning("Configuration issues found:")
        for issue in issues:
            logger.warning("  %s", issue)
        return 1
    else:
        logger.info("✅ Configuration is valid and ready to use!")
        return 0


def _handle_config_models(args, settings_manager, logger) -> int:
    """Handle models listing (SRP)."""
    logger.info("🤖 Available AI models:")
    
    from config.providers.registry import get_provider_function
    get_available_providers = get_provider_function("get_available_providers")
    get_available_models = get_provider_function("get_available_models")
    from config.providers.claude import CLAUDE_MODELS
    
    if args.provider:
        return _show_provider_models(args.provider, args.verbose, logger)
    else:
        return _show_all_models(args.verbose, logger)


def _handle_config_guidelines(args, settings_manager, logger) -> int:
    """Handle guidelines management (SRP)."""
    from config.guidelines import get_guidelines_manager
    guidelines_manager = get_guidelines_manager()
    
    action_handlers = {
        "list": lambda: _guidelines_list(guidelines_manager, logger),
        "show": lambda: _guidelines_show(args.language, guidelines_manager, logger),
        "edit": lambda: _guidelines_edit(args.language, guidelines_manager, logger),
        "reset": lambda: _guidelines_reset(args.language, guidelines_manager, logger),
        "path": lambda: _guidelines_path(guidelines_manager, logger)
    }
    
    handler = action_handlers.get(args.guidelines_action)
    if handler:
        return handler()
    else:
        logger.error("❌ Unknown guidelines action: %s", args.guidelines_action)
        return 1


# =============================================================================
# HELPER FUNCTIONS (DRY principle)
# =============================================================================

def _set_provider(provider: str, model: str, settings_manager, logger) -> bool:
    """Set active provider with validation."""
    logger.info("🔄 Setting active provider...")
    
    from config.providers.registry import get_provider_function
    get_available_providers = get_provider_function("get_available_providers")
    get_available_models = get_provider_function("get_available_models")
    available_providers = get_available_providers()
    
    if provider not in available_providers:
        logger.error("❌ Invalid provider: %s", provider)
        logger.info("Available providers: %s", ", ".join(available_providers))
        return False
        
    settings_manager.set_active_provider(provider)
    logger.info("✅ Active provider set to: %s", provider)
    
    # Set default model if not specified
    if not model:
        available_models = get_available_models(provider)
        if available_models:
            default_model = available_models[0]
            settings_manager.set_model(default_model)
            logger.info("✅ Default model set to: %s", default_model)
    
    return True


def _set_model(model: str, settings_manager, logger) -> bool:
    """Set model with validation."""
    logger.info("🎯 Setting model...")
    config = settings_manager.get_config()
    active_provider = config.active_provider
    
    from config.providers.registry import get_provider_function
    get_available_models = get_provider_function("get_available_models")
    available_models = get_available_models(active_provider)
    
    if model not in available_models:
        logger.error("❌ Invalid model for provider %s: %s", active_provider, model)
        logger.info("Available models: %s", ", ".join(available_models))
        return False
        
    settings_manager.set_model(model)
    logger.info("✅ Model set to: %s", model)
    return True


def _validate_active_provider_config(config, issues: List[str], logger) -> None:
    """Validate active provider configuration (OCP - extensible for any provider)."""
    active_provider = config.active_provider
    
    if not active_provider:
        issues.append("❌ No active AI provider configured")
        return
    
    provider_config = config.ai.get(active_provider)
    if not provider_config:
        issues.append(f"❌ {active_provider.title()} configuration missing")
        return
    
    # Generic API key validation
    if not provider_config.api_key:
        issues.append(f"❌ {active_provider.title()} API key not set")
        return
    
    # Provider-specific validation (extensible)
    if active_provider == "claude":
        if not provider_config.api_key.startswith("sk-ant-"):
            issues.append("❌ Claude API key format invalid (should start with 'sk-ant-')")
            return
    # Future providers can be added here without breaking existing code
    # elif active_provider == "openai":
    #     if not provider_config.api_key.startswith("sk-"):
    #         issues.append("❌ OpenAI API key format invalid (should start with 'sk-')")
    #         return
    
    logger.info("✅ %s API key configured", active_provider.title())


def _validate_embeddings(settings_manager, issues: List[str], logger) -> None:
    """Validate embeddings configuration."""
    active = settings_manager.get_active_embeddings()
    if not active.selected:
        issues.append("⚠️  No active embeddings selected")
    else:
        logger.info("✅ Active embeddings: %s", ", ".join(active.selected))


def _validate_storage(issues: List[str], logger) -> None:
    """Validate storage configuration."""
    try:
        from config.storage import get_storage_manager
        storage_manager = get_storage_manager()
        storage_info = storage_manager.get_storage_info()

        if storage_info.get("embeddings_count", 0) == 0:
            issues.append("⚠️  No embeddings generated yet")
        else:
            logger.info("✅ Storage: %d embeddings available", storage_info["embeddings_count"])
    except Exception as e:
        issues.append(f"❌ Storage validation failed: {e}")


def _show_provider_models(provider: str, verbose: bool, logger) -> int:
    """Show models for specific provider."""
    from config.providers.registry import get_provider_registry
    from config.providers.claude import CLAUDE_MODELS
    registry = get_provider_registry()
    get_available_providers = registry.get_available_providers
    get_available_models = registry.get_available_models
    
    if provider not in get_available_providers():
        logger.error("❌ Invalid provider: %s", provider)
        logger.info("Available providers: %s", ", ".join(get_available_providers()))
        return 1
        
    models = get_available_models(provider)
    logger.info("📋 %s models:", provider.title())
    
    for i, model in enumerate(models):
        prefix = "🔸" if i == 0 else "  "
        default_suffix = " (default)" if i == 0 else ""
        
        if verbose and provider == "claude":
            model_info = CLAUDE_MODELS.get(model, {})
            speed = model_info.get("speed", "unknown")
            description = model_info.get("description", "")
            max_output = model_info.get("max_output_tokens", "unknown")
            
            logger.info("%s %s%s - %s (%s speed, %s max tokens)", 
                      prefix, model, default_suffix, description, speed, max_output)
        else:
            logger.info("%s %s%s", prefix, model, default_suffix)
    
    return 0


def _show_all_models(verbose: bool, logger) -> int:
    """Show all available models."""
    from config.providers.registry import get_provider_function
    get_available_providers = get_provider_function("get_available_providers")
    get_available_models = get_provider_function("get_available_models")
    
    for provider in get_available_providers():
        models = get_available_models(provider)
        logger.info("📋 %s models:", provider.title())
        
        for i, model in enumerate(models):
            prefix = "🔸" if i == 0 else "  "
            default_suffix = " (default)" if i == 0 else ""
            logger.info("%s %s%s", prefix, model, default_suffix)
        
        logger.info("")
    
    return 0


# =============================================================================
# CONFIGURATION DISPLAY (Clean, organized sections)
# =============================================================================

def _display_configuration(settings_manager, logger, verbose: bool = False) -> None:
    """Display configuration in organized sections."""
    config = settings_manager.get_config()
    
    logger.info("📋 Context-AI Configuration")
    logger.info("")
    
    _display_ai_provider(config, logger)
    _display_embeddings(config, settings_manager, logger, verbose)
    _display_prompt_system(config, logger)
    _display_processing(config, logger, verbose)
    _display_storage(config, logger, verbose)
    
    if not verbose:
        logger.info("💡 Use --verbose for detailed settings and file type support")


def _display_ai_provider(config, logger) -> None:
    """Display AI provider section (OCP - works with any provider)."""
    logger.info("🤖 AI Provider:")
    
    active_provider = config.active_provider
    if not active_provider:
        logger.info("   ❌ No AI provider configured")
        logger.info("")
        return
    
    provider_config = config.ai.get(active_provider)
    if provider_config:
        max_tokens_k = provider_config.max_tokens // 1000
        logger.info("   Active: %s", active_provider)
        logger.info("   Model: %s (%dK tokens)", provider_config.default_model, max_tokens_k)
        logger.info("   API Key: %s", "***configured***" if provider_config.api_key else "❌ not set")
    else:
        logger.info("   ❌ %s configuration missing", active_provider.title())
    
    logger.info("")


def _display_embeddings(config, settings_manager, logger, verbose: bool) -> None:
    """Display embeddings section."""
    active = settings_manager.get_active_embeddings()
    logger.info("📊 Embeddings:")
    if active.selected:
        logger.info("   Active: %s (%d selected)", ", ".join(active.selected), len(active.selected))
    else:
        logger.info("   ❌ None selected")
    
    storage_config = config.storage
    logger.info("   Storage: %d max, cleanup after %d days", 
              storage_config.max_embeddings, storage_config.cleanup_after_days)
    
    if verbose:
        _display_storage_stats(logger)
    logger.info("")


def _display_storage_stats(logger) -> None:
    """Display storage statistics."""
    try:
        from config.storage import get_storage_manager
        storage_manager = get_storage_manager()
        storage_info = storage_manager.get_storage_info()
        embeddings_count = storage_info.get("embeddings_count", 0)
        logger.info("   Generated: %d embeddings available", embeddings_count)
    except Exception:
        logger.info("   Generated: unable to retrieve stats")


def _display_prompt_system(config, logger) -> None:
    """Display prompt system section."""
    logger.info("🎯 Prompt System:")
    logger.info("   Mode: %s", config.prompt_mode)
    logger.info("   Strategy: %s", config.system_prompt_strategy)
    logger.info("")


def _display_processing(config, logger, verbose: bool) -> None:
    """Display processing section."""
    chunking_config = config.chunking
    context_config = config.context_assembly
    
    logger.info("⚙️ Processing:")
    logger.info("   Chunk size: %d tokens (overlap: %d)", 
              chunking_config.chunk_size, chunking_config.chunk_overlap)
    logger.info("   Max chunks: %d per query", context_config.max_chunks)
    logger.info("   Cross-project priority: %s", 
              "enabled" if context_config.prioritize_cross_project else "disabled")
    
    if verbose:
        logger.info("   Min chunk size: %d tokens", chunking_config.min_chunk_size)
        logger.info("   Include metadata: %s", 
                  "enabled" if context_config.include_metadata else "disabled")
    logger.info("")


def _display_storage(config, logger, verbose: bool) -> None:
    """Display storage section."""
    storage_config = config.storage
    logger.info("📁 Storage:")
    logger.info("   Base path: %s", storage_config.base_path)
    
    if verbose:
        _display_file_types(config.chunking.supported_extensions, logger)
    logger.info("")


def _display_file_types(extensions: List[str], logger) -> None:
    """Display supported file types by category."""
    logger.info("   File types: %d supported", len(extensions))
    
    # Group extensions by category
    categories = {
        'JavaScript/TS': ['.js', '.ts', '.jsx', '.tsx', '.vue', '.svelte'],
        'Web/Styles': ['.html', '.css', '.scss', '.sass', '.less'],
        'Config': ['.json', '.yaml', '.yml'],
    }
    
    for category, category_exts in categories.items():
        matching = [ext for ext in extensions if ext in category_exts]
        if matching:
            logger.info("     %s: %s", category, ", ".join(matching))
    
    # Show other extensions
    all_categorized = [ext for exts in categories.values() for ext in exts]
    other_exts = [ext for ext in extensions if ext not in all_categorized]
    if other_exts:
        logger.info("     Other: %s", ", ".join(other_exts))


# =============================================================================
# GUIDELINES HANDLERS (Clean separation)
# =============================================================================

def _guidelines_list(guidelines_manager, logger) -> int:
    """List available guidelines."""
    logger.info("📋 Available coding guidelines:")
    available = guidelines_manager.get_available_languages()
    
    if available:
        for language in available:
            logger.info("  🔸 %s", language)
        logger.info("")
        logger.info("💡 Usage:")
        logger.info("  context-ai config guidelines show <language>")
        logger.info("  context-ai config guidelines edit <language>")
    else:
        logger.warning("⚠️  No guidelines found. They will be created on first use.")
    
    return 0


def _guidelines_show(language: str, guidelines_manager, logger) -> int:
    """Show guideline content."""
    language = language.lower()
    content = guidelines_manager.get_guideline(language)
    
    if content:
        logger.info("📋 Guidelines for %s:", language)
        logger.info("=" * 50)
        print(content)
        logger.info("=" * 50)
        return 0
    else:
        logger.error("❌ No guidelines found for language: %s", language)
        available = guidelines_manager.get_available_languages()
        if available:
            logger.info("Available languages: %s", ", ".join(available))
        return 1


def _guidelines_edit(language: str, guidelines_manager, logger) -> int:
    """Edit guideline in default editor."""
    language = language.lower()
    file_path = guidelines_manager.get_guideline_file_path(language)
    
    # Create file with default content if it doesn't exist
    if not file_path.exists():
        logger.info("📝 Creating default guidelines for %s...", language)
        if not guidelines_manager.reset_to_default(language):
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
        return 0
        
    except Exception as e:
        logger.error("❌ Failed to open editor: %s", e)
        logger.info("📁 You can manually edit: %s", file_path)
        return 1


def _guidelines_reset(language: str, guidelines_manager, logger) -> int:
    """Reset guideline to default."""
    language = language.lower()
    
    logger.info("🔄 Resetting %s guidelines to default...", language)
    if guidelines_manager.reset_to_default(language):
        logger.info("✅ Guidelines for %s reset successfully", language)
        return 0
    else:
        logger.error("❌ Failed to reset guidelines for %s", language)
        return 1


def _guidelines_path(guidelines_manager, logger) -> int:
    """Show guidelines directory path."""
    # Use the guidelines manager method instead of PathResolver
    guidelines_dir = guidelines_manager._get_user_guidelines_dir()
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
    
    return 0


def _handle_config_languages(args, settings_manager, logger) -> int:
    """Handle languages management (SRP)."""
    from config.languages.registry import get_languages_registry
    languages_registry = get_languages_registry()
    
    action_handlers = {
        "list": lambda: _languages_list(languages_registry, logger),
        "show": lambda: _languages_show(args.language, languages_registry, logger),
        "reset": lambda: _languages_reset(args.language, languages_registry, logger),
        "path": lambda: _languages_path(languages_registry, logger)
    }
    
    handler = action_handlers.get(args.languages_action)
    if handler:
        return handler()
    else:
        logger.error("❌ Unknown languages action: %s", args.languages_action)
        return 1


# =============================================================================
# LANGUAGES HANDLERS (Clean separation)
# =============================================================================

def _languages_list(languages_manager, logger) -> int:
    """List all configured languages."""
    logger.info("📋 Configured languages:")
    
    all_languages = languages_manager.get_all_languages()
    guidelines_languages = set(languages_manager.get_guidelines_languages())
    
    if not all_languages:
        logger.warning("⚠️  No languages configured")
        return 1
    
    # Sort by priority then name
    priority_order = {"high": 0, "medium": 1, "low": 2}
    sorted_languages = sorted(
        all_languages.items(),
        key=lambda x: (priority_order.get(x[1].chunking_priority, 3), x[0])
    )
    
    for name, config in sorted_languages:
        # Format extensions
        extensions_str = ", ".join(config.extensions)
        
        # Show inheritance
        inheritance_info = ""
        if hasattr(config, 'extends') and config.extends:
            inheritance_info = f" extends {config.extends}"
        
        # Show guidelines status
        guidelines_status = "✅" if name in guidelines_languages else "📝"
        
        logger.info("  🔸 %s (%s)%s - %s priority %s", 
                   name, extensions_str, inheritance_info, 
                   config.chunking_priority, guidelines_status)
    
    logger.info("")
    logger.info("📊 Total: %d languages, %d extensions", 
               len(all_languages), len(languages_manager.get_supported_extensions()))
    logger.info("📋 Legend: ✅ = guidelines available, 📝 = no guidelines")
    logger.info("")
    logger.info("💡 Usage:")
    logger.info("  context-ai config languages show <language>")
    logger.info("  context-ai config guidelines edit <language>  # Create guidelines")
    
    return 0


def _languages_show(language: str, languages_manager, logger) -> int:
    """Show detailed configuration for a specific language."""
    language = language.lower()
    config = languages_manager.get_language_config(language)
    
    if not config:
        logger.error("❌ Language '%s' not found", language)
        available = languages_manager.get_language_names()
        if available:
            logger.info("Available languages: %s", ", ".join(available[:10]))
            if len(available) > 10:
                logger.info("... and %d more", len(available) - 10)
        return 1
    
    logger.info("📋 Language configuration for '%s':", language)
    logger.info("=" * 50)
    logger.info("Name: %s", config.name)
    logger.info("Extensions: %s", ", ".join(config.extensions))
    
    # Show inheritance info
    if hasattr(config, 'extends') and config.extends:
        logger.info("Extends: %s", config.extends)
        base_separators = len(languages_manager.get_language_separators(config.extends))
        additional = len(config.separators) - base_separators
        logger.info("Separators: %d total (%d inherited + %d additional)", 
                   len(config.separators), base_separators, additional)
    else:
        logger.info("Separators: %d total", len(config.separators))
    
    logger.info("Chunking priority: %s", config.chunking_priority)
    
    # Show guidelines status
    guidelines_languages = languages_manager.get_guidelines_languages()
    if language in guidelines_languages:
        logger.info("Guidelines: ✅ available")
    else:
        logger.info("Guidelines: 📝 not available (create with: context-ai config guidelines edit %s)", language)
    
    # Show some separators
    separators = config.separators[:8]  # Show first 8
    logger.info("")
    logger.info("🔸 Separators preview:")
    for i, sep in enumerate(separators):
        display_sep = repr(sep) if len(sep) <= 10 else f"{repr(sep[:10])}..."
        logger.info("  %d. %s", i + 1, display_sep)
    
    if len(config.separators) > 8:
        logger.info("  ... and %d more", len(config.separators) - 8)
    
    logger.info("=" * 50)
    return 0


def _languages_reset(language: str, languages_manager, logger) -> int:
    """Reset language configuration to default."""
    language = language.lower()
    
    # Check if language exists
    if not languages_manager.has_language(language):
        logger.error("❌ Language '%s' not found", language)
        available = languages_manager.get_language_names()
        if available:
            logger.info("Available languages: %s", ", ".join(available[:10]))
        return 1
    
    logger.info("🔄 Resetting %s language configuration to default...", language)
    if languages_manager.reset_language_to_default(language):
        logger.info("✅ Language configuration for %s reset successfully", language)
        return 0
    else:
        logger.error("❌ Failed to reset language configuration for %s", language)
        return 1


def _languages_path(languages_manager, logger) -> int:
    """Show languages configuration file path and statistics."""
    config_file = languages_manager.get_config_file_path()
    config_info = languages_manager.get_config_info()
    
    logger.info("📁 Languages configuration: %s", config_file)
    
    # File status
    if config_file.exists():
        file_size = config_file.stat().st_size
        logger.info("📊 File size: %s bytes", f"{file_size:,}")
        logger.info("📊 Status: ✅ valid")
    else:
        logger.info("📊 Status: ❌ file not found")
        return 1
    
    # Configuration statistics
    logger.info("")
    logger.info("📊 Configuration statistics:")
    logger.info("  Languages: %d configured", config_info["total_languages"])
    logger.info("  Extensions: %d supported", config_info["extensions_count"])
    logger.info("  Guidelines: %d available", config_info["guidelines_available"])
    
    # Show guidelines status
    total_languages = config_info["total_languages"]
    guidelines_available = config_info["guidelines_available"]
    guidelines_missing = total_languages - guidelines_available
    
    if guidelines_missing > 0:
        logger.info("  📝 %d languages can have guidelines created", guidelines_missing)
        logger.info("")
        logger.info("💡 Create guidelines with: context-ai config guidelines edit <language>")
    
    return 0
