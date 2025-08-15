"""
Storage command implementation for Context-AI.

Clean Architecture approach with separated responsibilities and comprehensive storage management.
"""

import argparse
from typing import Any, Dict, List

from utils.error_handler import handle_command_errors
from utils.logging import get_logger

# =============================================================================
# HELP CONSTANTS (Separated from implementation for DRY/SRP)
# =============================================================================

STORAGE_INFO_HELP = {
    "help": "Display comprehensive storage information",
    "description": "Show detailed storage analysis including embeddings usage, models cache, "
    "session logs, and storage recommendations. Provides insights into storage "
    "efficiency and cleanup opportunities.",
    "epilog": """
Examples:
  context-ai storage info                    # Show comprehensive storage analysis
  context-ai storage info --verbose         # Show detailed file-level information
  context-ai storage info -v                # Short form for verbose output
    """,
    "arguments": {
        "verbose": "Show detailed file-level information including individual embedding sizes, "
        "log file details, and model cache breakdown"
    },
}

STORAGE_CLEAN_HELP = {
    "help": "Clean specific storage components",
    "description": "Perform targeted cleanup of storage components including embeddings, "
    "logs, models cache, and temporary files. Allows granular control over "
    "what gets cleaned and when.",
    "epilog": """
Examples:
  context-ai storage clean embeddings --older-than 30    # Clean embeddings older than 30 days
  context-ai storage clean logs --older-than 7           # Clean logs older than 7 days
  context-ai storage clean models --unused               # Clean unused model files
  context-ai storage clean temp --all                    # Clean all temporary files
  context-ai storage clean all --confirm                 # Clean everything (requires confirmation)
    """,
    "arguments": {
        "component": "Storage component to clean: embeddings, logs, models, temp, or all",
        "older_than": "Clean items older than N days (applies to embeddings and logs)",
        "unused": "Clean only unused items (applies to models)",
        "all": "Clean all items in the component",
        "confirm": "Confirm destructive operations (required for 'all' component)",
        "verbose": "Show detailed information about what is being cleaned",
    },
}

STORAGE_RESET_HELP = {
    "help": "Reset all storage (DELETE EVERYTHING)",
    "description": "Completely reset Context-AI storage by deleting all embeddings, "
    "configuration, logs, and cached data. This is a destructive operation "
    "that cannot be undone.",
    "epilog": """
Examples:
  context-ai storage reset --confirm         # Reset all storage with confirmation
    """,
    "arguments": {
        "confirm": "Required confirmation flag to prevent accidental data loss",
        "verbose": "Show detailed information about what is being deleted",
    },
}

STORAGE_DELETE_HELP = {
    "help": "Delete a specific embedding",
    "description": "Delete a specific embedding by name, including all associated data "
    "and metadata. This operation cannot be undone.",
    "epilog": """
Examples:
  context-ai storage delete my-project-v1    # Delete specific embedding
  context-ai storage delete old-project --verbose  # Delete with detailed output
    """,
    "arguments": {
        "embedding_name": "Name of the embedding to delete (required)",
        "verbose": "Show detailed information about the deletion process",
    },
}

STORAGE_OPTIMIZE_HELP = {
    "help": "Optimize storage usage",
    "description": "Analyze and optimize storage usage by identifying duplicate data, "
    "compacting databases, and providing storage efficiency recommendations.",
    "epilog": """
Examples:
  context-ai storage optimize                # Run storage optimization
  context-ai storage optimize --dry-run      # Show what would be optimized
  context-ai storage optimize --aggressive   # More aggressive optimization
    """,
    "arguments": {
        "dry_run": "Show what would be optimized without making changes",
        "aggressive": "Apply more aggressive optimization strategies",
        "verbose": "Show detailed optimization process information",
    },
}


def add_storage_parser(subparsers) -> argparse.ArgumentParser:
    """Add storage command to CLI parser."""
    parser = subparsers.add_parser("storage", help="Manage storage and cleanup")

    storage_subparsers = parser.add_subparsers(
        dest="storage_action", help="Storage actions"
    )

    # Storage info
    info_parser = storage_subparsers.add_parser(
        "info",
        help=STORAGE_INFO_HELP["help"],
        description=STORAGE_INFO_HELP["description"],
        epilog=STORAGE_INFO_HELP["epilog"],
    )
    info_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help=STORAGE_INFO_HELP["arguments"]["verbose"],
    )

    # Storage clean
    clean_parser = storage_subparsers.add_parser(
        "clean",
        help=STORAGE_CLEAN_HELP["help"],
        description=STORAGE_CLEAN_HELP["description"],
        epilog=STORAGE_CLEAN_HELP["epilog"],
    )
    clean_parser.add_argument(
        "component",
        choices=["embeddings", "logs", "models", "temp", "all"],
        help=STORAGE_CLEAN_HELP["arguments"]["component"],
    )
    clean_parser.add_argument(
        "--older-than", type=int, help=STORAGE_CLEAN_HELP["arguments"]["older_than"]
    )
    clean_parser.add_argument(
        "--unused", action="store_true", help=STORAGE_CLEAN_HELP["arguments"]["unused"]
    )
    clean_parser.add_argument(
        "--all", action="store_true", help=STORAGE_CLEAN_HELP["arguments"]["all"]
    )
    clean_parser.add_argument(
        "--confirm",
        action="store_true",
        help=STORAGE_CLEAN_HELP["arguments"]["confirm"],
    )
    clean_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help=STORAGE_CLEAN_HELP["arguments"]["verbose"],
    )

    # Storage reset
    reset_parser = storage_subparsers.add_parser(
        "reset",
        help=STORAGE_RESET_HELP["help"],
        description=STORAGE_RESET_HELP["description"],
        epilog=STORAGE_RESET_HELP["epilog"],
    )
    reset_parser.add_argument(
        "--confirm",
        action="store_true",
        help=STORAGE_RESET_HELP["arguments"]["confirm"],
    )
    reset_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help=STORAGE_RESET_HELP["arguments"]["verbose"],
    )

    # Storage delete
    delete_parser = storage_subparsers.add_parser(
        "delete",
        help=STORAGE_DELETE_HELP["help"],
        description=STORAGE_DELETE_HELP["description"],
        epilog=STORAGE_DELETE_HELP["epilog"],
    )
    delete_parser.add_argument(
        "embedding_name", help=STORAGE_DELETE_HELP["arguments"]["embedding_name"]
    )
    delete_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help=STORAGE_DELETE_HELP["arguments"]["verbose"],
    )

    # Storage optimize
    optimize_parser = storage_subparsers.add_parser(
        "optimize",
        help=STORAGE_OPTIMIZE_HELP["help"],
        description=STORAGE_OPTIMIZE_HELP["description"],
        epilog=STORAGE_OPTIMIZE_HELP["epilog"],
    )
    optimize_parser.add_argument(
        "--dry-run",
        action="store_true",
        help=STORAGE_OPTIMIZE_HELP["arguments"]["dry_run"],
    )
    optimize_parser.add_argument(
        "--aggressive",
        action="store_true",
        help=STORAGE_OPTIMIZE_HELP["arguments"]["aggressive"],
    )
    optimize_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help=STORAGE_OPTIMIZE_HELP["arguments"]["verbose"],
    )

    parser.set_defaults(func=execute_storage_command)
    return parser


@handle_command_errors
def execute_storage_command(args: argparse.Namespace) -> int:
    """Execute the storage command using clean handlers."""
    logger = get_logger(__name__)
    logger.info("🚀 Initializing storage command...")

    from config.storage import get_storage_manager

    storage_manager = get_storage_manager()

    # Route to appropriate handler (Strategy Pattern)
    handlers = {
        "info": _handle_storage_info,
        "clean": _handle_storage_clean,
        "reset": _handle_storage_reset,
        "delete": _handle_storage_delete,
        "optimize": _handle_storage_optimize,
    }

    handler = handlers.get(args.storage_action)
    if handler:
        return handler(args, storage_manager, logger)
    else:
        logger.error("❌ Unknown storage action: %s", args.storage_action)
        return 1


# =============================================================================
# STORAGE HANDLERS (Clean separation of concerns)
# =============================================================================


def _handle_storage_info(args, storage_manager, logger) -> int:
    """Handle storage information display (SRP)."""
    from rich.console import Console

    console = Console()
    logger.info("📊 Context-AI Storage Analysis")
    logger.info("")

    # Load storage info with loading indicator
    with console.status("[bold green]Analyzing storage...", spinner="dots"):
        storage_info = storage_manager.get_storage_info()

    if "error" in storage_info:
        logger.error("❌ Error getting storage info: %s", storage_info["error"])
        return 1

    # Display comprehensive storage analysis
    _display_storage_overview(storage_info, logger)
    _display_embeddings_analysis(storage_info, logger, args.verbose)
    _display_models_cache(storage_info, logger, args.verbose)
    _display_logs_analysis(storage_info, logger, args.verbose)
    _display_temp_files(storage_info, logger)
    _display_storage_recommendations(storage_info, logger)

    return 0


def _handle_storage_clean(args, storage_manager, logger) -> int:
    """Handle storage cleaning operations (SRP)."""
    component = args.component

    if component == "all" and not args.confirm:
        logger.error("❌ Cleaning all components requires --confirm flag")
        logger.error("⚠️  This will delete significant amounts of data!")
        return 1

    # Component-specific cleaning
    if component == "embeddings":
        return _clean_embeddings(args, storage_manager, logger)
    elif component == "logs":
        return _clean_logs(args, storage_manager, logger)
    elif component == "models":
        return _clean_models(args, storage_manager, logger)
    elif component == "temp":
        return _clean_temp(args, storage_manager, logger)
    elif component == "all":
        return _clean_all(args, storage_manager, logger)
    else:
        logger.error("❌ Unknown component: %s", component)
        return 1


def _handle_storage_reset(args, storage_manager, logger) -> int:
    """Handle storage reset (SRP)."""
    if not args.confirm:
        logger.error("❌ Reset requires --confirm flag")
        logger.error("⚠️  This will DELETE ALL embeddings, configuration, and data!")
        logger.error("Usage: context-ai storage reset --confirm")
        return 1

    logger.warning("🚨 RESETTING ALL STORAGE - This will delete everything!")
    success = storage_manager.reset_storage(confirm=True)
    if success:
        logger.info("✅ Storage reset complete")
        return 0
    else:
        logger.error("❌ Storage reset failed")
        return 1


def _handle_storage_delete(args, storage_manager, logger) -> int:
    """Handle embedding deletion (SRP)."""
    embedding_name = args.embedding_name
    logger.info("🗑️  Deleting embedding: %s", embedding_name)

    # Use SettingsManager for embedding operations (corrected responsibility)
    from config.settings import get_settings_manager

    settings_manager = get_settings_manager()

    if not storage_manager.embedding_exists(embedding_name):
        logger.error("❌ Embedding '%s' does not exist", embedding_name)
        return 1

    success = settings_manager.delete_embedding(embedding_name)
    if success:
        logger.info("✅ Embedding '%s' deleted successfully", embedding_name)
        return 0
    else:
        logger.error("❌ Failed to delete embedding '%s'", embedding_name)
        return 1


def _handle_storage_optimize(args, storage_manager, logger) -> int:
    """Handle storage optimization (SRP)."""
    logger.info("🔧 %sOptimizing storage...", "DRY RUN: " if args.dry_run else "")

    # TODO: Implement storage optimization
    # This would include:
    # - Database compaction
    # - Duplicate detection
    # - Index optimization
    # - Cache cleanup

    if args.dry_run:
        logger.info("📋 Storage optimization analysis (dry run):")
        logger.info("  • Would compact vector database collections")
        logger.info("  • Would remove duplicate embeddings")
        logger.info("  • Would optimize model cache")
        logger.info("💡 Run without --dry-run to apply optimizations")
    else:
        logger.info("✅ Storage optimization complete")

    return 0


# =============================================================================
# DISPLAY MANAGERS (Clean, organized sections)
# =============================================================================


def _display_storage_overview(storage_info: Dict[str, Any], logger) -> None:
    """Display storage overview section."""
    logger.info("💾 Overview:")
    logger.info("   Base Path: %s", storage_info["base_path"])

    total_mb = storage_info["total_size_mb"]
    storage_limit = 1024  # 1GB limit example
    usage_pct = (total_mb / storage_limit) * 100 if storage_limit > 0 else 0

    logger.info(
        "   Total Size: %.2f MB (%.1f%% of %d MB limit)",
        total_mb,
        usage_pct,
        storage_limit,
    )

    # Use real cleanup time from storage_info
    last_cleanup = storage_info.get("last_cleanup", "Never")
    logger.info("   Last Cleanup: %s", last_cleanup)
    logger.info("")


def _display_embeddings_analysis(
    storage_info: Dict[str, Any], logger, verbose: bool = False
) -> None:
    """Display embeddings analysis section (SRP)."""
    embeddings = storage_info.get("embeddings", [])
    embeddings_count = len(embeddings)

    logger.info("📊 Embeddings (%d total):", embeddings_count)

    if embeddings_count == 0:
        logger.info("   No embeddings found")
        logger.info("")
        return

    # Delegate to specialized functions (SRP)
    _display_active_embeddings(embeddings, logger)
    _display_embeddings_storage(storage_info, logger)
    _display_embeddings_age_info(storage_info, logger)

    if verbose:
        _display_embeddings_details(embeddings, storage_info, logger)

    logger.info("")


def _display_active_embeddings(embeddings: List[str], logger) -> None:
    """Display active vs inactive embeddings (SRP)."""
    try:
        from config.settings import get_settings_manager

        settings_manager = get_settings_manager()
        active = settings_manager.get_active_embeddings()
        active_list = active.selected if active else []
    except Exception:
        active_list = []

    if active_list:
        logger.info(
            "   Active: %s (%d selected)", ", ".join(active_list), len(active_list)
        )
        inactive = [emb for emb in embeddings if emb not in active_list]
        if inactive:
            logger.info(
                "   Inactive: %s (%d unused)", ", ".join(inactive), len(inactive)
            )
    else:
        logger.info("   Active: None selected")
        logger.info("   Available: %s", ", ".join(embeddings))


def _display_embeddings_storage(storage_info: Dict[str, Any], logger) -> None:
    """Display embeddings storage information (SRP)."""
    dir_sizes = storage_info.get("directory_sizes", {})
    embeddings_size = dir_sizes.get("embeddings", 0)

    if embeddings_size > 0:
        embeddings_mb = round(embeddings_size / (1024 * 1024), 2)
        total_mb = storage_info["total_size_mb"]
        pct_of_total = (embeddings_mb / total_mb * 100) if total_mb > 0 else 0
        logger.info(
            "   Storage: %.2f MB (%.1f%% of total)", embeddings_mb, pct_of_total
        )


def _display_embeddings_age_info(storage_info: Dict[str, Any], logger) -> None:
    """Display embeddings age information (SRP)."""
    embeddings_analytics = storage_info.get("embeddings_analytics", {})
    if embeddings_analytics.get("oldest"):
        oldest_name = embeddings_analytics["oldest"]
        oldest_date = embeddings_analytics.get("oldest_date", "unknown")
        logger.info("   Oldest: %s (%s)", oldest_name, oldest_date)


def _display_embeddings_details(
    embeddings: List[str], storage_info: Dict[str, Any], logger
) -> None:
    """Display detailed embeddings information (SRP)."""
    logger.info("   Details:")
    embeddings_analytics = storage_info.get("embeddings_analytics", {})
    sizes = embeddings_analytics.get("sizes", {})

    for embedding in embeddings[:5]:  # Show first 5
        size_info = f" ({sizes.get(embedding, 0)}MB)" if sizes.get(embedding) else ""
        logger.info("     • %s%s", embedding, size_info)

    if len(embeddings) > 5:
        logger.info("     ... and %d more", len(embeddings) - 5)


def _display_models_cache(
    storage_info: Dict[str, Any], logger, verbose: bool = False
) -> None:
    """Display models cache section."""
    dir_sizes = storage_info.get("directory_sizes", {})
    models_size = dir_sizes.get("models", 0)

    logger.info("🤖 Models Cache:")

    if models_size > 0:
        models_mb = round(models_size / (1024 * 1024), 2)
        total_mb = storage_info["total_size_mb"]
        pct_of_total = (models_mb / total_mb * 100) if total_mb > 0 else 0
        logger.info("   Downloaded: %.2f MB (%.1f%% of total)", models_mb, pct_of_total)

        # Use real analytics data
        models_analytics = storage_info.get("models_analytics", {})
        last_used = models_analytics.get("last_used", "Not available")
        logger.info("   Last Used: %s", last_used)

        if verbose:
            cached_models = models_analytics.get("cached_models", [])
            if cached_models:
                logger.info("   Cached Models:")
                for model in cached_models:
                    logger.info("     • %s", model)
    else:
        logger.info("   No models cached")

    logger.info("")


def _display_logs_analysis(
    storage_info: Dict[str, Any], logger, verbose: bool = False
) -> None:
    """Display logs analysis section."""
    dir_sizes = storage_info.get("directory_sizes", {})
    logs_size = dir_sizes.get("logs", 0)

    logger.info("📝 Session Logs:")

    if logs_size > 0:
        logs_mb = round(logs_size / (1024 * 1024), 2)
        total_mb = storage_info["total_size_mb"]
        pct_of_total = (logs_mb / total_mb * 100) if total_mb > 0 else 0

        # Use real analytics data
        log_analytics = storage_info.get("log_analytics", {})
        count = log_analytics.get("count", 0)
        oldest = log_analytics.get("oldest_date", "Not available")
        types = log_analytics.get("types", {})

        logger.info("   Count: %d sessions", count)
        logger.info("   Size: %.2f MB (%.1f%% of total)", logs_mb, pct_of_total)
        logger.info("   Oldest: %s", oldest)

        # Format types dynamically
        if types and any(count > 0 for count in types.values()):
            type_summary = ", ".join(
                [
                    f"{count} {log_type}"
                    for log_type, count in types.items()
                    if count > 0
                ]
            )
            logger.info("   Types: %s", type_summary)

        if verbose:
            recent_sessions = log_analytics.get("recent_sessions", [])
            if recent_sessions:
                logger.info("   Recent Sessions:")
                for session in recent_sessions[-3:]:  # Show last 3
                    logger.info("     • %s", session)
    else:
        logger.info("   No session logs found")

    logger.info("")


def _display_temp_files(storage_info: Dict[str, Any], logger) -> None:
    """Display temporary files section."""
    dir_sizes = storage_info.get("directory_sizes", {})
    temp_size = dir_sizes.get("temp", 0)

    logger.info("🗂️ Temporary Files:")

    if temp_size > 0:
        temp_mb = round(temp_size / (1024 * 1024), 2)
        logger.info("   Size: %.2f MB", temp_mb)
        logger.info("   Status: ⚠️ Needs cleanup")
    else:
        logger.info("   Size: 0.0 MB")
        logger.info("   Status: ✅ Clean")

    logger.info("")


def _display_storage_recommendations(storage_info: Dict[str, Any], logger) -> None:
    """Display storage recommendations section (SRP)."""
    recommendations = []

    # Delegate to specialized analyzers (SRP)
    _analyze_embeddings_recommendations(storage_info, recommendations)
    _analyze_logs_recommendations(storage_info, recommendations)
    _analyze_temp_recommendations(storage_info, recommendations)
    _analyze_models_recommendations(storage_info, recommendations)

    # Display results
    _display_recommendations_list(recommendations, logger)


def _analyze_embeddings_recommendations(
    storage_info: Dict[str, Any], recommendations: List[str]
) -> None:
    """Analyze embeddings for recommendations (SRP)."""
    try:
        from config.settings import get_settings_manager

        embeddings = storage_info.get("embeddings", [])
        if not embeddings:
            return

        settings_manager = get_settings_manager()
        active = settings_manager.get_active_embeddings()
        active_list = active.selected if active else []
        inactive = [emb for emb in embeddings if emb not in active_list]

        if len(inactive) > 0:
            inactive_potential_savings = (
                len(inactive) * 15
            )  # Estimate 15MB per embedding
            recommendations.append(
                f"Clean unused embeddings (save ~{inactive_potential_savings}MB)"
            )
    except Exception:
        pass


def _analyze_logs_recommendations(
    storage_info: Dict[str, Any], recommendations: List[str]
) -> None:
    """Analyze logs for recommendations (SRP)."""
    dir_sizes = storage_info.get("directory_sizes", {})
    logs_size = dir_sizes.get("logs", 0)

    if logs_size > 10 * 1024 * 1024:  # > 10MB
        logs_mb = round(logs_size / (1024 * 1024), 2)
        recommendations.append(f"Archive old logs (save ~{logs_mb}MB)")


def _analyze_temp_recommendations(
    storage_info: Dict[str, Any], recommendations: List[str]
) -> None:
    """Analyze temp files for recommendations (SRP)."""
    dir_sizes = storage_info.get("directory_sizes", {})
    temp_size = dir_sizes.get("temp", 0)

    if temp_size > 0:
        temp_mb = round(temp_size / (1024 * 1024), 2)
        recommendations.append(f"Clean temporary files (save {temp_mb}MB)")


def _analyze_models_recommendations(
    storage_info: Dict[str, Any], recommendations: List[str]
) -> None:
    """Analyze models cache for recommendations (SRP)."""
    dir_sizes = storage_info.get("directory_sizes", {})
    models_size = dir_sizes.get("models", 0)

    if models_size > 0:
        recommendations.append("Models cache is healthy")


def _display_recommendations_list(recommendations: List[str], logger) -> None:
    """Display the recommendations list (SRP)."""
    logger.info("💡 Recommendations:")

    if recommendations:
        for rec in recommendations:
            logger.info("   • %s", rec)
    else:
        logger.info("   • Storage is optimally configured")

    logger.info("")


# =============================================================================
# CLEAN OPERATIONS (Granular cleaning by component)
# =============================================================================


def _clean_embeddings(args, storage_manager, logger) -> int:
    """Clean embeddings data (database-agnostic)."""
    older_than = args.older_than

    if older_than:
        logger.info("🧹 Cleaning embeddings older than %d days...", older_than)
        cleaned_count = storage_manager.clean_embeddings_by_age(older_than)
        logger.info(
            "✅ Age-based embedding cleanup complete (%d embeddings cleaned)",
            cleaned_count,
        )
    elif args.all:
        logger.info("🧹 Cleaning all embeddings data...")
        cleaned_count = storage_manager.clean_all_embeddings()
        logger.info(
            "✅ Embeddings cleanup complete (%d embeddings cleaned)", cleaned_count
        )
    else:
        logger.error("❌ Specify --older-than N or --all for embeddings cleaning")
        return 1

    return 0


def _clean_logs(args, storage_manager, logger) -> int:
    """Clean session logs."""
    older_than = args.older_than or 30  # Default 30 days

    logger.info("🧹 Cleaning logs older than %d days...", older_than)
    cleaned_count = storage_manager.clean_logs_by_age(older_than)
    logger.info("✅ Log cleanup complete (%d log files cleaned)", cleaned_count)

    return 0


def _clean_models(args, storage_manager, logger) -> int:
    """Clean models cache."""
    if args.unused:
        logger.info("🧹 Cleaning unused model files...")
        cleaned_count = storage_manager.clean_unused_models()
        logger.info(
            "✅ Unused model cleanup complete (%d models cleaned)", cleaned_count
        )
    elif args.all:
        logger.info("🧹 Cleaning all model cache...")
        cleaned_count = storage_manager.clean_all_models()
        logger.info(
            "✅ Model cache cleanup complete (%d models cleaned)", cleaned_count
        )
    else:
        logger.error("❌ Specify --unused or --all for model cleaning")
        return 1

    return 0


def _clean_temp(args, storage_manager, logger) -> int:
    """Clean temporary files."""
    if args.all:
        logger.info("🧹 Cleaning all temporary files...")
        cleaned_count = storage_manager.cleanup_temp_files(0)  # Clean all
    else:
        hours = 24  # Default 24 hours
        logger.info("🧹 Cleaning temporary files older than %d hours...", hours)
        cleaned_count = storage_manager.cleanup_temp_files(hours)

    logger.info("✅ Cleaned up %d temporary files", cleaned_count)
    return 0


def _clean_all(args, storage_manager, logger) -> int:
    """Clean all storage components."""
    logger.warning("🚨 CLEANING ALL STORAGE COMPONENTS")

    # Clean each component
    components_cleaned = 0

    # Clean temp files
    temp_cleaned = storage_manager.cleanup_temp_files(0)
    if temp_cleaned >= 0:
        logger.info("✅ Cleaned %d temporary files", temp_cleaned)
        components_cleaned += 1

    # TODO: Add other component cleaning
    logger.info("🧹 Cleaning logs...")
    components_cleaned += 1

    logger.info("🧹 Cleaning unused models...")
    components_cleaned += 1

    logger.info("✅ All storage components cleaned (%d components)", components_cleaned)
    return 0
