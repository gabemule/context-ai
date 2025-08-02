"""
AI service for Context-AI.

Integrates AI providers with the query system following SOLID principles.
"""

import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from config.settings import get_settings_manager
from core.ai.claude_client import get_claude_client
from core.formatting.context_formatter import count_tokens
# LAZY IMPORT: from services.embedding_service import QueryService
from utils.exceptions import APIError, ConfigurationError
from utils.logging import get_logger

if TYPE_CHECKING:
    from services.embedding_service import QueryService

# VSCode integration detection
VSCODE_MODE = os.getenv('CONTEXT_AI_VSCODE') == 'true'


@dataclass
class ChatTurn:
    """Represents a single turn in chat conversation."""
    question: str
    response: str
    timestamp: datetime
    context_used: str = ""
    context_summary: str = ""
    tokens_used: int = 0


class TokenCalculator:
    """Handles token calculations and allocations (SRP)."""
    
    @staticmethod
    def calculate_context_allocation(question: str, include_history: bool) -> Dict[str, int]:
        """Calculate token allocation for context and history."""
        from config.constants import CHAT_HISTORY_TOKEN_RATIO, CONTEXT_TOKEN_RATIO
        from config.providers import get_max_tokens
        
        question_tokens = count_tokens(question)
        total_context_tokens = int(get_max_tokens() * CONTEXT_TOKEN_RATIO)
        
        if include_history:
            history_tokens = int(total_context_tokens * CHAT_HISTORY_TOKEN_RATIO)
            code_context_tokens = total_context_tokens - history_tokens
        else:
            history_tokens = 0
            code_context_tokens = total_context_tokens
        
        return {
            "question_tokens": question_tokens,
            "total_context_tokens": total_context_tokens,
            "history_tokens": history_tokens,
            "code_context_tokens": code_context_tokens
        }
    
    @staticmethod
    def calculate_response_tokens(input_tokens: int, context_tokens: int) -> int:
        """Calculate maximum response tokens."""
        from config.constants import MIN_RESPONSE_TOKENS, RESPONSE_TOKEN_RATIO
        from config.providers import get_max_tokens, get_max_output_tokens
        
        model_max_tokens = get_max_tokens()
        model_max_output = get_max_output_tokens()
        
        available_tokens = model_max_tokens - input_tokens
        max_response_tokens = min(
            available_tokens * RESPONSE_TOKEN_RATIO,
            max(MIN_RESPONSE_TOKENS, context_tokens // 2),
        )
        return int(min(max_response_tokens, model_max_output))


class ContextManager:
    """Manages context retrieval and caching (SRP)."""
    
    def __init__(self, query_service: "QueryService", settings_manager):
        self.query_service = query_service
        self.settings_manager = settings_manager
        self._context_cache = {}
        self.logger = get_logger(__name__)
    
    def get_context(self, question: str, max_tokens: int, verbose: bool, include_history: bool) -> str:
        """Get context with intelligent caching."""
        from config.constants import CONTEXT_CACHE_TTL, ENABLE_CONTEXT_CACHE
        import hashlib
        import time
        
        if not ENABLE_CONTEXT_CACHE:
            return self._fetch_fresh_context(question, max_tokens, verbose)
        
        # Create cache key
        active = self.settings_manager.get_active_embeddings()
        cache_key_data = f"{question}:{','.join(sorted(active.selected))}:{max_tokens}:{include_history}"
        cache_key = hashlib.md5(cache_key_data.encode()).hexdigest()
        
        # Check cache validity
        if cache_key in self._context_cache:
            cached_entry = self._context_cache[cache_key]
            cache_age = time.time() - cached_entry["timestamp"]
            
            if cache_age < CONTEXT_CACHE_TTL:
                if verbose:
                    self.logger.info("📁 Using cached context (%.1fs old)", cache_age)
                return cached_entry["content"]
            else:
                del self._context_cache[cache_key]
        
        # Generate fresh context and cache it
        context = self._fetch_fresh_context(question, max_tokens, verbose)
        self._context_cache[cache_key] = {"content": context, "timestamp": time.time()}
        
        # Limit cache size
        if len(self._context_cache) > 10:
            oldest_keys = sorted(self._context_cache.keys(), key=lambda k: self._context_cache[k]["timestamp"])[:5]
            for old_key in oldest_keys:
                del self._context_cache[old_key]
        
        return context
    
    def _fetch_fresh_context(self, question: str, max_tokens: int, verbose: bool) -> str:
        """Fetch fresh context from query service."""
        if verbose:
            self.logger.info("🔄 Generating fresh context...")
        
        return self.query_service.query_context(
            question, format_type="ai_friendly", verbose=verbose, max_context_tokens=max_tokens
        )


class DisplayManager:
    """Handles all display and output operations (SRP)."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def display_response(self, content: str) -> None:
        """Display response with rich formatting."""
        if VSCODE_MODE:
            return  # Skip panel display in VSCode mode
        
        from rich.console import Console
        from rich.markdown import Markdown
        from rich.panel import Panel
        
        console = Console()
        markdown_content = Markdown(content)
        panel = Panel(markdown_content, title="🤖 Context-AI's Answer", title_align="center", border_style="green", padding=(1, 2))
        
        console.print()
        console.print(panel)
        console.print()
    
    def display_token_stats(self, response, input_tokens: int, context_tokens: int, question_tokens: int, verbose: bool, include_history: bool, code_context_tokens: int, chat_context_tokens: int) -> None:
        """Display token usage statistics."""
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text
        from config.providers import get_max_tokens
        
        actual_input = response.usage.get("input_tokens", input_tokens)
        actual_output = response.usage.get("output_tokens", 0)
        total_used = actual_input + actual_output
        max_tokens = get_max_tokens()
        total_pct = (total_used / max_tokens) * 100
        
        console = Console()
        stats_text = Text()
        stats_text.append("📊 Token Usage\n", style="bold cyan")
        stats_text.append(f"Total: {total_used:,} tokens ({total_pct:.1f}%)\n", style="bold")
        stats_text.append(f"Input: {actual_input:,} • Output: {actual_output:,}\n")
        
        if include_history and chat_context_tokens > 0:
            stats_text.append(f"Breakdown: {code_context_tokens//1000}K code + {chat_context_tokens//1000}K history\n")
        else:
            stats_text.append(f"Context: {code_context_tokens//1000}K tokens\n")
        
        remaining = max_tokens - total_used
        stats_text.append(f"Remaining: {remaining:,} tokens ({100-total_pct:.1f}%)", style="dim")
        
        panel = Panel(stats_text, title="📊 Token Usage", border_style="cyan", padding=(0, 1))
        console.print()
        console.print(panel)
        
        if VSCODE_MODE:
            print("\n#= Context-AI End =#\n", flush=True)
    
    def save_to_file(self, content: str, file_path: str) -> None:
        """Save content to file."""
        try:
            from pathlib import Path
            output_file = Path(file_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            
            self.logger.info("💾 Response saved to: %s", file_path)
        except Exception as e:
            self.logger.error("❌ Failed to save to file: %s", e)
            raise
    
    def copy_to_clipboard(self, content: str) -> None:
        """Copy content to clipboard."""
        try:
            import pyperclip
            pyperclip.copy(content)
            self.logger.info("📋 Response copied to clipboard")
        except ImportError:
            self.logger.warning("⚠️  pyperclip not installed. Install with: pip install pyperclip")
        except Exception as e:
            self.logger.warning("⚠️  Failed to copy to clipboard: %s", e)
    
    def display_chat_welcome(self, embeddings_list: str, verbose: bool) -> None:
        """Display chat welcome panel."""
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text
        
        console = Console()
        welcome_text = Text(
            f"Using embeddings: {embeddings_list}\n\n"
            "Ask questions about your codebase. Chat history will be maintained for context.\n\n"
            "Special commands:\n"
            "    /embeddings - Show active embeddings\n"
            "    /history    - Show chat statistics\n"
            "    /clear      - Reset conversation history\n"
            "    /verbose    - Toggle detailed logging\n"
            "    /mode       - Change prompt mode (minimal|standard|comprehensive|strict)\n"
            "    exit        - Quit chat session",
            style="dim",
        )
        title = f"🤖 Context-AI Chat Session with History{' (Verbose)' if verbose else ''}"
        welcome_panel = Panel(welcome_text, title=title, title_align="center", border_style="green", padding=(1, 2))
        
        console.print()
        console.print(welcome_panel)
        console.print()


class ChatHistoryManager:
    """Manages chat conversation history (SRP)."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.history: List[ChatTurn] = []
    
    def add_turn(self, question: str, response: str, context: str = "", tokens: int = 0, context_summary: str = "") -> None:
        """Add a new turn to the conversation history."""
        turn = ChatTurn(question=question, response=response, timestamp=datetime.now(), context_used=context, context_summary=context_summary, tokens_used=tokens)
        self.history.append(turn)
        self.logger.debug("Added chat turn #%d (%d tokens)", len(self.history), tokens)
    
    def get_history_context(self, max_tokens: int) -> str:
        """Get formatted history context within token limit."""
        if not self.history:
            return ""
        
        from config.constants import CHAT_MIN_HISTORY_TURNS
        
        context_parts = []
        total_tokens = 0
        
        for i, turn in enumerate(reversed(self.history)):
            turn_context = f"\n### Previous Q&A #{len(self.history) - i}\n**User:** {turn.question}\n**Assistant:** {turn.response}\n"
            turn_tokens = count_tokens(turn_context)
            
            if i < CHAT_MIN_HISTORY_TURNS:
                context_parts.insert(0, turn_context)
                total_tokens += turn_tokens
            elif total_tokens + turn_tokens <= max_tokens:
                context_parts.insert(0, turn_context)
                total_tokens += turn_tokens
            else:
                break
        
        if context_parts:
            header = f"\n## Previous Conversation ({len(context_parts)} turns, {total_tokens} tokens)\n"
            return header + "".join(context_parts)
        
        return ""
    
    def clear(self) -> None:
        """Clear all chat history."""
        self.history.clear()
        self.logger.info("Chat history cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about current chat history."""
        if not self.history:
            return {"turns": 0, "total_tokens": 0}
        
        total_tokens = sum(turn.tokens_used for turn in self.history)
        return {
            "turns": len(self.history),
            "total_tokens": total_tokens,
            "avg_tokens_per_turn": total_tokens // len(self.history) if self.history else 0,
            "oldest_turn": self.history[0].timestamp if self.history else None,
            "latest_turn": self.history[-1].timestamp if self.history else None,
        }


class APIManager:
    """Generic API manager - supports multiple providers (OCP + LSP)."""
    
    def __init__(self, provider: str, client, provider_config):
        self.provider = provider
        self.client = client
        self.provider_config = provider_config
        self.logger = get_logger(__name__)
    
    def ask_with_progress(self, question: str, context: str, max_tokens: int, verbose: bool, include_history: bool):
        """Ask AI with progress display - provider agnostic."""
        import time
        from rich.console import Console
        
        console = Console()
        provider_name = self.provider.title()
        self.logger.info("Asking %s: %s", provider_name, question)
        
        # Use streaming for better UX
        accumulated_text = ""
        start_time = time.time()
        
        try:
            
            if VSCODE_MODE:
                print("\n#= Context-AI Streaming START =#\n", flush=True)
            
            def live_streaming_callback(text_chunk: str):
                nonlocal accumulated_text
                accumulated_text += text_chunk
                print(text_chunk, end="", flush=True)
            
            # Provider-specific API call (follows LSP)
            response = self._make_api_call(question, context, max_tokens, verbose, live_streaming_callback)
            
            elapsed = time.time() - start_time
            
            if VSCODE_MODE:
                print("\n#= Context-AI Streaming END =#\n", flush=True)
            
            print("\n")  # Add spacing
            
            # Show final panel only in CLI mode
            if not VSCODE_MODE:
                try:
                    from rich.markdown import Markdown
                    final_content = Markdown(accumulated_text.strip()) if accumulated_text.strip() else "No response received"
                except:
                    final_content = accumulated_text.strip() if accumulated_text.strip() else "No response received"
                
                from rich.panel import Panel
                final_panel = Panel(final_content, title="🤖 Context-AI's Answer", title_align="center", border_style="green", padding=(1, 2))
                console.print(final_panel)
            
            if verbose:
                input_tokens = response.usage.get("input_tokens", 0)
                output_tokens = response.usage.get("output_tokens", 0)
                self.logger.info("⏱️ %s API (streaming): %.1f seconds (%s in, %s out)", provider_name, elapsed, f"{input_tokens:,}", f"{output_tokens:,}")
            
            return response, True
            
        except Exception:
            elapsed = time.time() - start_time
            from rich.panel import Panel
            error_panel = Panel(f"❌ Streaming failed after {elapsed:.1f}s", title="Error", title_align="center", border_style="red")
            console.print(error_panel)
            raise
    
    def _make_api_call(self, question: str, context: str, max_tokens: int, verbose: bool, text_callback):
        """Make provider-specific API call (Template Method Pattern)."""
        if self.provider == "claude":
            return self.client.ask(question=question, context=context, max_tokens=max_tokens, verbose=verbose, text_callback=text_callback)
        else:
            # Future providers can be added here (OCP)
            raise NotImplementedError(f"Provider {self.provider} not implemented yet")


class ChatCommandHandler:
    """Handles chat special commands (SRP)."""
    
    def __init__(self, settings_manager, chat_history: ChatHistoryManager, logger):
        self.settings_manager = settings_manager
        self.chat_history = chat_history
        self.logger = logger
    
    def handle_command(self, command: str, verbose: bool) -> tuple[bool, bool]:  # (handled, new_verbose)
        """Handle special chat commands. Returns (handled, new_verbose_value)."""
        if command == "/embeddings":
            self._show_embeddings()
            return True, verbose
        elif command == "/history":
            self._show_history()
            return True, verbose
        elif command == "/clear":
            self._clear_history()
            return True, verbose
        elif command == "/verbose":
            new_verbose = not verbose
            self.logger.info("🔧 Verbose mode %s", "enabled" if new_verbose else "disabled")
            return True, new_verbose
        elif command.startswith("/mode"):
            self._handle_mode_change(command)
            return True, verbose
        
        return False, verbose
    
    def _show_embeddings(self):
        """Show current active embeddings."""
        active = self.settings_manager.get_active_embeddings()
        if active.selected:
            self.logger.info("📊 Active embeddings: %s", ", ".join(active.selected))
        else:
            self.logger.info("❌ No active embeddings selected")
    
    def _show_history(self):
        """Show chat history statistics."""
        stats = self.chat_history.get_stats()
        if stats["turns"] > 0:
            self.logger.info("💬 Chat History: %d turns, %s total tokens, avg %d tokens/turn", stats["turns"], f"{stats['total_tokens']:,}", stats["avg_tokens_per_turn"])
        else:
            self.logger.info("💬 No chat history yet")
    
    def _clear_history(self):
        """Clear chat history."""
        self.chat_history.clear()
        self.logger.info("🗑️ Chat history cleared")
    
    def _handle_mode_change(self, command: str):
        """Handle mode change command."""
        parts = command.split()
        if len(parts) == 1:
            current_mode = self.settings_manager.get_prompt_mode()
            self.logger.info("🎯 Current prompt mode: %s", current_mode)
            # @TODO GET MODES FROM CONFIG CAGE
            self.logger.info("📋 Available modes: minimal, standard, comprehensive, strict")
            self.logger.info("💡 Usage: /mode <mode_name>")
            # @TODO GET MODES FROM CONFIG CAGE
        elif len(parts) == 2 and parts[1] in ["minimal", "standard", "comprehensive", "strict"]:
            new_mode = parts[1]
            old_mode = self.settings_manager.get_prompt_mode()
            self.settings_manager.set_prompt_mode(new_mode)
            self.logger.info("🎯 Prompt mode changed: %s → %s", old_mode, new_mode)
            
            # Get description from mode config YAML
            description = self._get_mode_description(new_mode)
            if description:
                self.logger.info("📝 %s", description)
        else:
            self.logger.error("❌ Invalid mode. Available: minimal, standard, comprehensive, strict")
            self.logger.info("💡 Usage: /mode <mode_name>")
    
    def _get_mode_description(self, mode: str) -> str:
        """Get mode description from YAML config."""
        try:
            from pathlib import Path
            import yaml
            from config.storage import get_storage_manager
            
            storage_manager = get_storage_manager()
            mode_file = storage_manager.path_manager.prompts_dir / mode / "mode.yaml"
            
            if mode_file.exists():
                with open(mode_file, 'r', encoding='utf-8') as f:
                    mode_config = yaml.safe_load(f)
                    return mode_config.get('description', f"{mode.title()} mode")
            
            # Fallback descriptions if YAML not found
            fallback_descriptions = {
                "minimal": "Basic context + question only (fastest)",
                "standard": "Context + guidelines when detected (balanced)",
                "comprehensive": "Full cross-project analysis + insights (detailed)",
                "strict": "Enforced coding standards + code review approach (thorough)",
            }
            return fallback_descriptions.get(mode, f"{mode.title()} mode")
            
        except Exception as e:
            self.logger.debug("Failed to load mode description from YAML: %s", e)
            return f"{mode.title()} mode"


class AIService:
    """Main AI service coordinator (follows SRP and DIP)."""
    
    def __init__(self):
        """Initialize AI service with dependency injection."""
        import time
        init_start_time = time.time()
        
        self.logger = get_logger(__name__)
        verbose = self.logger.isEnabledFor(10)  # DEBUG level = 10
        
        # Settings Manager
        self.settings_manager = get_settings_manager()
        
        # Query Service (LAZY IMPORT - only when needed)
        if verbose:
            t2 = time.time()
        from services.embedding_service import QueryService
        self.query_service = QueryService()
        if verbose:
            self.logger.info("⏱️  QueryService: %.3fs", time.time() - t2)
        
        # Context Manager
        self.context_manager = ContextManager(self.query_service, self.settings_manager)
        
        # Display Manager
        self.display_manager = DisplayManager()
        
        # Chat History Manager
        self.chat_history = ChatHistoryManager()
        
        # Get AI configuration
        config = self.settings_manager.get_config()
        self.active_provider = config.active_provider or "claude"
        self.provider_config = config.ai.get(self.active_provider)
        
        if not self.provider_config or not self.provider_config.api_key:
            provider_name = self.active_provider.title()
            raise ConfigurationError(f"{provider_name} API key not configured. Set it with: context-ai config set --{self.active_provider}-key YOUR_KEY")
        
        # Initialize AI API manager (provider-agnostic)
        if self.active_provider == "claude":
            claude_client = get_claude_client(self.provider_config.api_key, self.provider_config.default_model)
            self.ai_api = APIManager("claude", claude_client, self.provider_config)
        else:
            raise ConfigurationError(f"Unsupported AI provider: {self.active_provider}")
        
        # Initialize chat command handler
        self.chat_handler = ChatCommandHandler(self.settings_manager, self.chat_history, self.logger)
        
        # Final timing summary
        if verbose:
            total_time = time.time() - init_start_time
            self.logger.info("✅ AIService ready in %.3fs", total_time)
        else:
            self.logger.debug("AI service initialized with %s model: %s", self.active_provider, self.provider_config.default_model)
    
    def ask_question(self, question: str, context_format: str = "ai_friendly", verbose: bool = False, 
                    copy_to_clipboard: bool = False, output_file: str = None, include_history: bool = False) -> str:
        """Ask a question with context from active embeddings."""
        self.logger.info("🤖 Processing question: %s", question[:100] + "..." if len(question) > 100 else question)
        
        try:
            # Handle non-AI formats
            if context_format in ["json", "xml", "plain", "markdown"]:
                return self._handle_non_ai_format(question, context_format, verbose, output_file, copy_to_clipboard)
            
            # Calculate token allocations
            token_allocation = TokenCalculator.calculate_context_allocation(question, include_history)
            
            # Get contexts
            contexts = self._get_contexts(question, token_allocation, verbose, include_history)
            
            # Calculate final tokens and limits
            input_tokens = contexts["total_tokens"] + token_allocation["question_tokens"] 
            max_tokens = TokenCalculator.calculate_response_tokens(input_tokens, contexts["total_tokens"])
            
            # Log context window usage
            self._log_context_usage(token_allocation, contexts, input_tokens, include_history)
            
            # Save context to session
            self._save_context_to_session(contexts["combined"], question, token_allocation)
            
            # Get AI response  
            response, was_streamed = self.ai_api.ask_with_progress(question, contexts["combined"], max_tokens, verbose, include_history)
            
            # Update session with response
            self._update_session_with_response(response, input_tokens, include_history)
            
            # Add to chat history if needed
            if include_history:
                self._add_to_chat_history(question, response, contexts["combined"], input_tokens, verbose)
            
            # Handle output
            self._handle_output(response.content, output_file, copy_to_clipboard, was_streamed)
            
            # Display stats
            self.display_manager.display_token_stats(response, input_tokens, contexts["total_tokens"], token_allocation["question_tokens"], verbose, include_history, contexts["code_tokens"], contexts["chat_tokens"])
            
            return response.content
            
        except APIError as e:
            self.logger.error("❌ %s API error: %s", self.active_provider.title(), e)
            raise
        except Exception as e:
            self.logger.error("❌ Error processing question: %s", e)
            raise
    
    def start_chat(self, verbose: bool = False) -> None:
        """Start interactive chat session."""
        provider_name = self.active_provider.title()
        mode_text = " (VSCode mode)" if VSCODE_MODE else ""
        self.logger.info("💬 Starting chat session with %s%s...", provider_name, mode_text)
        
        # Check active embeddings
        active = self.settings_manager.get_active_embeddings()
        if not active.selected:
            self.logger.error("❌ No active embeddings selected. Use 'context-ai select' first")
            return
        
        embeddings_list = ", ".join(active.selected)
        self.logger.info("📊 Active embeddings: %s", embeddings_list)
        self.logger.info("Type 'exit', 'quit', or press Ctrl+C to end the session")
        
        # Display welcome panel
        self.display_manager.display_chat_welcome(embeddings_list, verbose)
        
        if VSCODE_MODE:
            print("\n#= Context-AI Loaded =#\n", flush=True)
        
        # Main chat loop
        self._run_chat_loop(verbose)
    
    def _handle_non_ai_format(self, question: str, context_format: str, verbose: bool, output_file: str, copy_to_clipboard: bool) -> str:
        """Handle non-AI format requests."""
        context = self.query_service.query_context(question, format_type=context_format, verbose=verbose)
        
        if verbose:
            self.logger.info("📄 Context retrieved (%d characters)", len(context))
            self.logger.info("🎯 Returning formatted context (no AI processing)")
        
        if output_file:
            self.display_manager.save_to_file(context, output_file)
        else:
            if context_format in ["json", "xml"]:
                print(context)
            else:
                self.display_manager.display_response(context)
        
        if copy_to_clipboard:
            self.display_manager.copy_to_clipboard(context)
        
        return context
    
    def _get_contexts(self, question: str, token_allocation: Dict[str, int], verbose: bool, include_history: bool) -> Dict[str, Any]:
        """Get code context and chat history."""
        # Get code context
        code_context = self.context_manager.get_context(question, token_allocation["code_context_tokens"], verbose, include_history)
        
        # Get chat history context
        chat_context = ""
        chat_context_tokens = 0
        
        if include_history:
            chat_context = self.chat_history.get_history_context(token_allocation["history_tokens"])
            chat_context_tokens = count_tokens(chat_context) if chat_context else 0
            
            if verbose and chat_context:
                self.logger.info("💬 Chat history retrieved: %dK tokens (%d turns)", chat_context_tokens // 1000, len(self.chat_history.history))
        
        # Combine contexts
        if chat_context:
            combined_context = chat_context + "\n\n" + code_context
            separator_tokens = count_tokens("\n\n")
            total_tokens = chat_context_tokens + separator_tokens + token_allocation["code_context_tokens"]
        else:
            combined_context = code_context
            total_tokens = token_allocation["code_context_tokens"]
        
        return {
            "combined": combined_context,
            "code_tokens": token_allocation["code_context_tokens"],
            "chat_tokens": chat_context_tokens,
            "total_tokens": total_tokens
        }
    
    def _log_context_usage(self, token_allocation: Dict[str, int], contexts: Dict[str, Any], input_tokens: int, include_history: bool) -> None:
        """Log context window usage information."""
        window_usage_pct = (contexts["total_tokens"] / token_allocation["total_context_tokens"]) * 100 if token_allocation["total_context_tokens"] > 0 else 0
        
        self.logger.info("📊 Context Window: %dK used (%.1f%% of %dK limit)", contexts["total_tokens"] // 1000, window_usage_pct, token_allocation["total_context_tokens"] // 1000)
        
        if include_history and contexts["chat_tokens"] > 0:
            self.logger.info("📊 Breakdown: %dK code + %dK history (%d turns) = %dK total", contexts["code_tokens"] // 1000, contexts["chat_tokens"] // 1000, len(self.chat_history.history), contexts["total_tokens"] // 1000)
        else:
            self.logger.info("📊 Code context: %dK tokens → %dK final", contexts["code_tokens"] // 1000, contexts["total_tokens"] // 1000)
        
        provider_name = self.active_provider.title()
        self.logger.info("📊 Input: %sK tokens → %s", input_tokens // 1000, provider_name)
        
        # Performance diagnostic based on selected model capacity
        model_max = self.provider_config.max_tokens
        large_threshold = model_max // 2  # 50% of selected model capacity
        medium_threshold = model_max // 4  # 25% of selected model capacity
        
        if input_tokens > large_threshold:
            self.logger.warning("⚠️  Large context (%s tokens) - %s may be slow", f"{input_tokens:,}", provider_name)
        elif input_tokens > medium_threshold:
            self.logger.info("ℹ️  Medium context (%s tokens) - expect 10-20s response", f"{input_tokens:,}")
        else:
            self.logger.info("✅ Small context (%s tokens) - should be fast", f"{input_tokens:,}")
    
    def _save_context_to_session(self, context: str, question: str, token_allocation: Dict[str, int]) -> None:
        """Save context to session logger."""
        from utils.session_logger import get_current_session
        from config.constants import CONTEXT_DEFAULT_CHUNKS
        
        session = get_current_session()
        if session:
            active = self.settings_manager.get_active_embeddings()
            context_metadata = {
                "token_count": token_allocation["total_context_tokens"],
                "embeddings_used": active.selected,
                "results_count": CONTEXT_DEFAULT_CHUNKS,
                "truncated": False
            }
            
            from core.ai.prompt_builder import get_prompt_builder
            prompt_builder = get_prompt_builder()
            
            session.save_context(context, question, context_metadata, None)
            
            # Connect session logger to prompt builder
            prompt_builder._session_logger = session
    
    def _update_session_with_response(self, response, input_tokens: int, include_history: bool) -> None:
        """Update session with response metadata."""
        from utils.session_logger import get_current_session
        
        session = get_current_session()
        if session:
            session.log_response_received(response.content)
            
            output_tokens = response.usage.get("output_tokens", 0)
            total_tokens = response.usage.get("input_tokens", input_tokens) + output_tokens
            
            if session.is_chat:
                if session.session_data["turns"]:
                    current_turn = session.session_data["turns"][-1]
                    current_turn["tokens"]["response"] = output_tokens
                    current_turn["tokens"]["total"] = total_tokens
                    current_turn["model"] = self.provider_config.default_model
                    
                    session.session_data["session_totals"]["total_response_tokens"] += output_tokens
                    session.session_data["session_totals"]["total_tokens"] += total_tokens
            else:
                session.session_data["tokens"]["response"] = output_tokens
                session.session_data["tokens"]["total"] = total_tokens
                session.session_data["model"] = self.provider_config.default_model
            
            session.session_data["status"] = "completed"
    
    def _add_to_chat_history(self, question: str, response, context: str, total_tokens_used: int, verbose: bool) -> None:
        """Add turn to chat history."""
        total_tokens_used = response.usage.get("input_tokens", total_tokens_used) + response.usage.get("output_tokens", 0)
        
        if verbose:
            self.logger.info("💾 Saving to history: %dK tokens (turn #%d)", total_tokens_used // 1000, len(self.chat_history.history) + 1)
        
        context_summary = self._extract_context_summary(context)
        self.chat_history.add_turn(question, response.content, context, total_tokens_used, context_summary)
        
        if verbose:
            self.logger.info("✅ History updated: now have %d turns total", len(self.chat_history.history))
    
    def _extract_context_summary(self, context: str) -> str:
        """Extract a brief summary of the context used."""
        if not context:
            return "No context"
        
        # Simple context summary - first 200 chars
        summary = context[:200].replace('\n', ' ').strip()
        if len(context) > 200:
            summary += "..."
        
        return summary
    
    def _handle_output(self, content: str, output_file: str, copy_to_clipboard: bool, was_streamed: bool) -> None:
        """Handle response output."""
        if output_file:
            self.display_manager.save_to_file(content, output_file)
        else:
            if not was_streamed:
                self.display_manager.display_response(content)
        
        if copy_to_clipboard:
            self.display_manager.copy_to_clipboard(content)
    
    def _run_chat_loop(self, verbose: bool) -> None:
        """Run the main chat interaction loop."""
        try:
            while True:
                try:
                    question = input("You: ").strip()
                    
                    if question.lower() in ["exit", "quit", "bye"]:
                        self._handle_chat_exit()
                        break
                    
                    if not question:
                        continue
                    
                    # Handle special commands
                    handled, verbose = self.chat_handler.handle_command(question, verbose)
                    if handled:
                        continue
                    
                    # Add chat turn before processing question
                    from utils.session_logger import get_current_session
                    session = get_current_session()
                    if session and session.is_chat:
                        session.add_chat_turn(question)
                    
                    # Process regular question
                    self.ask_question(question, verbose=verbose, include_history=True)
                    
                except KeyboardInterrupt:
                    self._handle_chat_exit()
                    break
                except EOFError:
                    self._handle_chat_exit()
                    break
                except Exception as e:
                    self.logger.error("❌ Error in chat loop: %s", e)
                    continue
        except Exception as e:
            self.logger.error("❌ Fatal error in chat loop: %s", e)
    
    def _handle_chat_exit(self) -> None:
        """Handle chat session exit."""
        stats = self.chat_history.get_stats()
        if stats["turns"] > 0:
            self.logger.info("💬 Chat completed: %d turns, %s total tokens", stats["turns"], f"{stats['total_tokens']:,}")
        else:
            self.logger.info("💬 Chat session ended")
        
        self.logger.info("👋 Goodbye!")
