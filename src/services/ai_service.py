"""
AI service for Context-AI.

Integrates Claude with the query system to provide AI-powered question answering.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

from config.settings import get_settings_manager
from core.ai.claude_client import get_claude_client
from core.formatting.context_formatter import count_tokens
from services.embedding_service import QueryService
from utils.exceptions import APIError, ConfigurationError
from utils.logging import get_logger


@dataclass
class ChatTurn:
    """Represents a single turn in chat conversation."""

    question: str
    response: str
    timestamp: datetime
    context_used: str = ""
    context_summary: str = ""  # Summary of files actually sent to Claude
    tokens_used: int = 0


class ChatHistoryManager:
    """Manages chat conversation history with intelligent truncation."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.history: List[ChatTurn] = []

    def add_turn(
        self, question: str, response: str, context: str = "", tokens: int = 0, context_summary: str = ""
    ) -> None:
        """Add a new turn to the conversation history."""
        turn = ChatTurn(
            question=question,
            response=response,
            timestamp=datetime.now(),
            context_used=context,
            context_summary=context_summary,
            tokens_used=tokens,
        )
        self.history.append(turn)
        self.logger.debug("Added chat turn #%d (%d tokens)", len(self.history), tokens)

    def get_history_context(self, max_tokens: int) -> str:
        """Get formatted history context within token limit."""
        if not self.history:
            return ""

        from config.constants import CHAT_MIN_HISTORY_TURNS

        # Always include minimum recent turns, then add more if space allows
        context_parts = []
        total_tokens = 0

        # Start with most recent turns and work backwards
        for i, turn in enumerate(reversed(self.history)):
            turn_context = f"\n### Previous Q&A #{len(self.history) - i}\n"
            turn_context += f"**User:** {turn.question}\n"
            turn_context += f"**Assistant:** {turn.response}\n"

            turn_tokens = count_tokens(turn_context)

            # Always include minimum recent turns
            if i < CHAT_MIN_HISTORY_TURNS:
                context_parts.insert(0, turn_context)
                total_tokens += turn_tokens
            # Add more turns if we have token budget
            elif total_tokens + turn_tokens <= max_tokens:
                context_parts.insert(0, turn_context)
                total_tokens += turn_tokens
            else:
                break

        if context_parts:
            header = (
                f"\n## Previous Conversation ({len(context_parts)} turns, "
                f"{total_tokens} tokens)\n"
            )
            return header + "".join(context_parts)

        return ""

    def should_summarize(self) -> bool:
        """Check if history should be summarized to save tokens."""
        from config.constants import CHAT_SUMMARY_THRESHOLD

        return len(self.history) > CHAT_SUMMARY_THRESHOLD

    def get_summary_prompt(self) -> str:
        """Generate prompt for summarizing old conversation history."""
        if len(self.history) < 3:
            return ""

        # Get older turns (not the most recent ones)
        from config.constants import CHAT_MIN_HISTORY_TURNS

        old_turns = self.history[:-CHAT_MIN_HISTORY_TURNS]

        conversation_text = ""
        for i, turn in enumerate(old_turns):
            conversation_text += f"Q{i + 1}: {turn.question}\n"
            conversation_text += f"A{i + 1}: {turn.response}\n\n"

        return f"""Please summarize this conversation history in 2-3 sentences, \
focusing on:
- Key topics discussed
- Important decisions or conclusions reached
- Context that would be helpful for future questions

Conversation to summarize:
{conversation_text}

Summary:"""

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
            "avg_tokens_per_turn": (
                total_tokens // len(self.history) if self.history else 0
            ),
            "oldest_turn": self.history[0].timestamp if self.history else None,
            "latest_turn": self.history[-1].timestamp if self.history else None,
        }


class AIService:
    """AI service that combines context retrieval with Claude."""

    def __init__(self):
        """Initialize AI service."""
        self.logger = get_logger(__name__)
        self.settings_manager = get_settings_manager()
        self.query_service = QueryService()
        self.chat_history = ChatHistoryManager()
        self._context_cache = {}  # Cache for expensive context operations

        # Get current configuration
        config = self.settings_manager.get_config()
        self.active_provider = config.active_provider or "claude"
        self.provider_config = config.ai.get(self.active_provider)

        if not self.provider_config or not self.provider_config.api_key:
            provider_name = self.active_provider.title()
            raise ConfigurationError(
                f"{provider_name} API key not configured. Set it with: "
                f"context-ai config set --{self.active_provider}-key YOUR_KEY"
            )

        # Initialize provider-specific client
        if self.active_provider == "claude":
            self.claude_client = get_claude_client(
                self.provider_config.api_key, self.provider_config.default_model
            )
        # Future providers can be added here
        # elif self.active_provider == "openai":
        #     self.openai_client = get_openai_client(...)
        else:
            raise ConfigurationError(f"Unsupported AI provider: {self.active_provider}")

        self.logger.debug(
            "AI service initialized with %s model: %s", 
            self.active_provider, self.provider_config.default_model
        )

    def ask_question(
        self,
        question: str,
        context_format: str = "ai_friendly",
        verbose: bool = False,
        copy_to_clipboard: bool = False,
        output_file: str = None,
        include_history: bool = False,
    ) -> str:
        """
        Ask a question with context from active embeddings.

        Args:
            question: User question
            context_format: Format for context retrieval and output
            verbose: Show detailed information
            copy_to_clipboard: Copy response to clipboard
            output_file: Save response to file
            include_history: Include chat history in context (for chat mode)

        Returns:
            The AI response text or formatted context (depending on format)
        """
        self.logger.info(
            "🤖 Processing question: %s",
            question[:100] + "..." if len(question) > 100 else question,
        )

        try:
            # Get context from embeddings
            if verbose:
                self.logger.info("🔍 Retrieving context from active embeddings...")

            # For non-AI formats, return formatted context directly
            if context_format in ["json", "xml", "plain", "markdown"]:
                context = self.query_service.query_context(
                    question, format_type=context_format, verbose=verbose
                )

                if verbose:
                    self.logger.info(
                        "📄 Context retrieved (%d characters)", len(context)
                    )
                    self.logger.info(
                        "🎯 Returning formatted context (no AI processing)"
                    )

                # Handle output
                if output_file:
                    self._save_to_file(context, output_file)
                else:
                    # For structured formats, print directly without rich formatting
                    if context_format in ["json", "xml"]:
                        print(context)
                    else:
                        self._display_response(context)

                if copy_to_clipboard:
                    self._copy_to_clipboard(context)

                return context

            # Calculate dynamic context limit first
            from config.constants import (
                CHAT_HISTORY_TOKEN_RATIO,
                CONTEXT_TOKEN_RATIO,
                MIN_RESPONSE_TOKENS,
                RESPONSE_TOKEN_RATIO,
            )
            from config.providers import get_max_tokens, get_max_output_tokens

            # Reserve space for question and response, use rest for context
            question_tokens = count_tokens(question)
            total_context_tokens = int(get_max_tokens() * CONTEXT_TOKEN_RATIO)

            # Allocate tokens between code context and chat history
            if include_history:
                history_tokens = int(total_context_tokens * CHAT_HISTORY_TOKEN_RATIO)
                code_context_tokens = total_context_tokens - history_tokens

                # Debug: Check history state before retrieval
                history_count = len(self.chat_history.history)
                if verbose:
                    self.logger.info(
                        "🔍 History Debug: %d turns available, %dK token budget",
                        history_count,
                        history_tokens // 1000,
                    )

                # Get chat history within token budget
                chat_context = self.chat_history.get_history_context(history_tokens)
                chat_context_tokens = count_tokens(chat_context) if chat_context else 0

                # Enhanced history logging
                if verbose:
                    if chat_context:
                        self.logger.info(
                            "💬 Chat history retrieved: %dK tokens (%d turns)",
                            chat_context_tokens // 1000,
                            history_count,
                        )
                        # Show a preview of the history content
                        preview = chat_context[:200].replace('\n', ' ')
                        self.logger.info("📝 History preview: %s...", preview)
                    else:
                        self.logger.info(
                            "💬 No chat history retrieved (%d turns available)",
                            history_count,
                        )
            else:
                code_context_tokens = total_context_tokens
                chat_context = ""
                chat_context_tokens = 0

            # For ai_friendly format, continue with Claude processing
            # Use context caching for chat to avoid reprocessing
            context = self._get_cached_context(
                question, code_context_tokens, verbose, include_history
            )

            # Combine code context with chat history
            if chat_context:
                context = chat_context + "\n\n" + context
                # Calculate tokens accurately: individual counts + separator
                separator_tokens = count_tokens("\n\n")
                context_tokens = chat_context_tokens + separator_tokens + code_context_tokens
            else:
                context_tokens = code_context_tokens

            # Note: context_tokens now calculated above, not recounted
            input_tokens = context_tokens + question_tokens

            # Calculate available tokens and allocate response space
            from config.providers import get_max_tokens, get_max_output_tokens
            
            model_max_tokens = get_max_tokens()
            model_max_output = get_max_output_tokens()
            
            available_tokens = model_max_tokens - input_tokens
            max_response_tokens = min(
                available_tokens * RESPONSE_TOKEN_RATIO,
                max(MIN_RESPONSE_TOKENS, context_tokens // 2),
            )
            max_tokens = int(min(max_response_tokens, model_max_output))

            # Calculate actual used window context (always show)
            window_context_used = code_context_tokens + chat_context_tokens
            window_usage_pct = (window_context_used / total_context_tokens) * 100 if total_context_tokens > 0 else 0
            
            # Always show main stats
            self.logger.info(
                "📊 Context Window: %dK used (%.1f%% of %dK limit)",
                window_context_used // 1000,
                window_usage_pct,
                total_context_tokens // 1000,
            )
            
            if include_history and chat_context_tokens > 0:
                self.logger.info(
                    "📊 Breakdown: %dK code + %dK history (%d turns) = %dK total",
                    code_context_tokens // 1000,
                    chat_context_tokens // 1000,
                    len(self.chat_history.history),
                    context_tokens // 1000,
                )
            else:
                self.logger.info(
                    "📊 Code context: %dK tokens → %dK final",
                    code_context_tokens // 1000,
                    context_tokens // 1000,
                )

            # Always show input total and performance expectation 
            provider_name = self.active_provider.title()
            self.logger.info("📊 Input: %sK tokens → %s", input_tokens // 1000, provider_name)
            
            # Performance diagnostic (always useful)
            if input_tokens > 100000:
                self.logger.warning(
                    "⚠️  Large context (%s tokens) - Claude may be slow",
                    f"{input_tokens:,}",
                )
            elif input_tokens > 50000:
                self.logger.info(
                    "ℹ️  Medium context (%s tokens) - expect 10-20s response",
                    f"{input_tokens:,}",
                )
            else:
                self.logger.info(
                    "✅ Small context (%s tokens) - should be fast",
                    f"{input_tokens:,}",
                )

            if verbose:
                self.logger.info("📄 Context retrieved (%d characters)", len(context))
                self.logger.info("📊 Token calculation: %dK chat + %dK code + separator = %dK total", 
                                chat_context_tokens // 1000, 
                                code_context_tokens // 1000, 
                                context_tokens // 1000)
                self.logger.info(
                    "📊 Input breakdown: %d context + %d question = %d total",
                    context_tokens,
                    question_tokens,
                    input_tokens,
                )
                self.logger.info("📊 Dynamic response tokens: %d", max_tokens)

            # Save context to session logger if available
            from utils.session_logger import get_current_session
            from config.constants import CONTEXT_DEFAULT_CHUNKS
            session = get_current_session()
            if session:
                active = self.settings_manager.get_active_embeddings()
                context_metadata = {
                    "token_count": context_tokens,
                    "embeddings_used": active.selected,
                    "results_count": CONTEXT_DEFAULT_CHUNKS,  # We can make this more accurate later
                    "truncated": False  # We can determine this from context formatter
                }
                
                # Capture guidelines that will be applied to the prompt
                from core.ai.prompt_builder import get_prompt_builder
                prompt_builder = get_prompt_builder()
                guidelines = prompt_builder._get_applicable_guidelines(context, question)
                
                session.save_context(context, question, context_metadata, guidelines)

            # Use simple progress for all queries
            import time
            start_time = time.time()
            response, was_streamed = self._ask_claude_with_progress(
                question, context, max_tokens, verbose, include_history
            )
            duration = time.time() - start_time

            # Save response to session logger if available
            if session:
                from config.providers import get_provider_display_name
                
                response_metadata = {
                    "tokens_in": response.usage.get("input_tokens", input_tokens),
                    "tokens_out": response.usage.get("output_tokens", 0),
                    "duration_seconds": duration,
                    "provider": get_provider_display_name(self.active_provider),
                    "model": self.provider_config.default_model
                }
                session.save_response(response.content, response_metadata, question)

            # Add to chat history if this is part of a conversation
            if include_history:
                total_tokens_used = response.usage.get(
                    "input_tokens", input_tokens
                ) + response.usage.get("output_tokens", 0)
                
                if verbose:
                    self.logger.info(
                        "💾 Saving to history: %dK tokens (turn #%d)",
                        total_tokens_used // 1000,
                        len(self.chat_history.history) + 1,
                    )
                
                # Extract context summary from formatted context
                context_summary = self._extract_context_summary_from_formatted(context)
                
                self.chat_history.add_turn(
                    question, response.content, context, total_tokens_used, context_summary
                )
                
                if verbose:
                    self.logger.info(
                        "✅ History updated: now have %d turns total",
                        len(self.chat_history.history),
                    )

            # Handle output
            if output_file:
                self._save_to_file(response.content, output_file)
            else:
                # Only display response if it wasn't streamed (streaming already shows formatted result)
                if not was_streamed:
                    self._display_response(response.content)

            if copy_to_clipboard:
                self._copy_to_clipboard(response.content)

            # Show token usage stats (always, but elegantly)
            self._display_token_stats(
                response, input_tokens, context_tokens, question_tokens, verbose,
                include_history, code_context_tokens, chat_context_tokens
            )

            return response.content

        except APIError as e:
            self.logger.error("❌ Claude API error: %s", e)
            raise
        except Exception as e:
            self.logger.error("❌ Error processing question: %s", e)
            raise

    def start_chat(self, verbose: bool = False) -> None:
        """Start interactive chat session with optional verbose mode."""
        import os
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text

        # Detect VSCode integration mode
        self._vscode_mode = os.getenv('CONTEXT_AI_VSCODE') == 'true'
        
        provider_name = self.active_provider.title()
        if self._vscode_mode:
            self.logger.info("💬 Starting chat session with %s (VSCode mode)...", provider_name)
        else:
            self.logger.info("💬 Starting chat session with %s...", provider_name)

        # Check and display active embeddings
        active = self.settings_manager.get_active_embeddings()
        if not active.selected:
            self.logger.error(
                "❌ No active embeddings selected. Use 'context-ai select' first"
            )
            return

        # Show active embeddings before welcome panel
        embeddings_list = ", ".join(active.selected)
        self.logger.info("📊 Active embeddings: %s", embeddings_list)
        self.logger.info("Type 'exit', 'quit', or press Ctrl+C to end the session")

        console = Console()

        # Enhanced welcome panel with embedding info
        welcome_text = Text(
            f"Using embeddings: {embeddings_list}\n\n"
            "Ask questions about your codebase. Chat history will be maintained "
            "for context.\n\n"
            "Special commands:\n"
            "    /embeddings - Show active embeddings\n"
            "    /history    - Show chat statistics\n"
            "    /clear      - Reset conversation history\n"
            "    /verbose    - Toggle detailed logging\n"
            "    /mode       - Change prompt mode (minimal|standard|comprehensive|strict)\n"
            "    exit        - Quit chat session",
            style="dim",
        )
        title = (
            f"🤖 Context-AI Chat Session with History{' (Verbose)' if verbose else ''}"
        )
        welcome_panel = Panel(
            welcome_text,
            title=title,
            title_align="center",
            border_style="green",
            padding=(1, 2),
        )

        console.print()
        console.print(welcome_panel)
        console.print()
        
        # Send initialization complete marker for VSCode (only in VSCode mode)
        if self._vscode_mode:
            print("\n#= Context-AI Loaded =#\n", flush=True)

        try:
            while True:
                try:
                    question = input("You: ").strip()

                    if question.lower() in ["exit", "quit", "bye"]:
                        # Show final stats
                        stats = self.chat_history.get_stats()
                        if stats["turns"] > 0:
                            self.logger.info(
                                "📊 Session stats: %d turns, %s total tokens",
                                stats["turns"],
                                f"{stats['total_tokens']:,}",
                            )
                        self.logger.info("Goodbye! 👋")
                        break

                    if not question:
                        continue

                    # Handle special commands
                    if question.lower() == "/embeddings":
                        # Show current active embeddings
                        active = self.settings_manager.get_active_embeddings()
                        if active.selected:
                            self.logger.info(
                                "📊 Active embeddings: %s", ", ".join(active.selected)
                            )
                        else:
                            self.logger.info("❌ No active embeddings selected")
                        continue
                    elif question.lower() == "/history":
                        stats = self.chat_history.get_stats()
                        if stats["turns"] > 0:
                            self.logger.info(
                                "💬 Chat History: %d turns, %s total tokens, "
                                "avg %d tokens/turn",
                                stats["turns"],
                                f"{stats['total_tokens']:,}",
                                stats["avg_tokens_per_turn"],
                            )
                        else:
                            self.logger.info("💬 No chat history yet")
                        continue
                    elif question.lower() == "/clear":
                        self.chat_history.clear()
                        self.logger.info("🗑️ Chat history cleared")
                        continue
                    elif question.lower() == "/verbose":
                        verbose = not verbose
                        self.logger.info(
                            "🔧 Verbose mode %s", "enabled" if verbose else "disabled"
                        )
                        continue
                    elif question.lower().startswith("/mode"):
                        # Parse and handle mode change
                        parts = question.split()
                        if len(parts) == 1:
                            # Show current mode and available options
                            import config.constants

                            current_mode = config.constants.PROMPT_MODE
                            self.logger.info("🎯 Current prompt mode: %s", current_mode)
                            self.logger.info(
                                "📋 Available modes: minimal, standard, comprehensive, strict"
                            )
                            self.logger.info("💡 Usage: /mode <mode_name>")
                            continue
                        elif len(parts) == 2 and parts[1] in [  # noqa: E501
                            "minimal",
                            "standard",
                            "comprehensive",
                            "strict",
                        ]:
                            # Change mode
                            new_mode = parts[1]
                            import config.constants

                            old_mode = config.constants.PROMPT_MODE
                            config.constants.PROMPT_MODE = new_mode
                            self.logger.info(
                                "🎯 Prompt mode changed: %s → %s", old_mode, new_mode
                            )

                            # Show helpful description of new mode
                            mode_descriptions = {
                                "minimal": "Basic context + question only (fastest)",
                                "standard": "Context + guidelines when detected (balanced)",
                                "comprehensive": "Full cross-project analysis + insights (detailed)",
                                "strict": "Enforced coding standards + code review approach (thorough)",
                            }
                            self.logger.info("📝 %s", mode_descriptions[new_mode])
                            continue
                        else:
                            self.logger.error(
                                "❌ Invalid mode. Available: minimal, standard, comprehensive, strict"
                            )
                            self.logger.info("💡 Usage: /mode <mode_name>")
                            continue

                    # Use the same display method but with history enabled
                    self.ask_question(question, verbose=verbose, include_history=True)

                except KeyboardInterrupt:
                    self.logger.info("\n\nGoodbye! 👋")
                    break
                except EOFError:
                    self.logger.info("\n\nGoodbye! 👋")
                    break

        except Exception as e:
            self.logger.error("❌ Chat session error: %s", e)

    def _save_to_file(self, content: str, file_path: str) -> None:
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

    def _copy_to_clipboard(self, content: str) -> None:
        """Copy content to clipboard."""
        try:
            import pyperclip

            pyperclip.copy(content)
            self.logger.info("📋 Response copied to clipboard")

        except ImportError:
            self.logger.warning(
                "⚠️  pyperclip not installed. Install with: pip install pyperclip"
            )
        except Exception as e:
            self.logger.warning("⚠️  Failed to copy to clipboard: %s", e)

    def _display_response(self, content: str) -> None:
        """Display response with rich formatting."""
        # Only show Answer panel in CLI mode (not in VSCode)
        if hasattr(self, '_vscode_mode') and self._vscode_mode:
            return  # Skip panel display in VSCode mode
            
        from rich.console import Console
        from rich.markdown import Markdown
        from rich.panel import Panel

        console = Console()

        # Create markdown content
        markdown_content = Markdown(content)

        # Display in a styled panel
        panel = Panel(
            markdown_content,
            title="🤖 Context-AI's Answer",
            title_align="center",
            border_style="green",
            padding=(1, 2),
        )

        console.print()
        console.print(panel)
        console.print()

    def _display_token_stats(
        self,
        response,
        input_tokens: int,
        context_tokens: int,
        question_tokens: int,
        verbose: bool = False,
        include_history: bool = False,
        code_context_tokens: int = 0,
        chat_context_tokens: int = 0,
    ) -> None:
        """Display token usage statistics with Rich panel."""
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text
        from config.providers import get_max_tokens

        # Get actual usage from response
        actual_input = response.usage.get("input_tokens", input_tokens)
        actual_output = response.usage.get("output_tokens", 0)
        total_used = actual_input + actual_output
        max_tokens = get_max_tokens()

        # Calculate percentages
        total_pct = (total_used / max_tokens) * 100

        console = Console()
        
        # Create stats text
        stats_text = Text()
        
        # Title line
        stats_text.append("📊 Token Usage\n", style="bold cyan")
        
        # Main usage line
        stats_text.append(f"Total: {total_used:,} tokens ({total_pct:.1f}%)\n", style="bold")
        
        # Input/Output breakdown
        stats_text.append(f"Input: {actual_input:,} • Output: {actual_output:,}\n")
        
        # Context breakdown
        if include_history and chat_context_tokens > 0:
            stats_text.append(f"Breakdown: {code_context_tokens//1000}K code + {chat_context_tokens//1000}K history\n")
        else:
            stats_text.append(f"Context: {code_context_tokens//1000}K tokens\n")
        
        # Model limit
        remaining = max_tokens - total_used
        stats_text.append(f"Remaining: {remaining:,} tokens ({100-total_pct:.1f}%)", style="dim")
        
        # Create panel
        panel = Panel(
            stats_text,
            title="📊 Token Usage",
            border_style="cyan",
            padding=(0, 1)
        )
        
        # Display panel
        console.print()
        console.print(panel)
        
        # Send end marker for VSCode (only for chat sessions in VSCode mode)
        if hasattr(self, '_vscode_mode') and self._vscode_mode:
            print("\n#= Context-AI End =#\n", flush=True)

    def _ask_claude_with_progress(
        self,
        question: str,
        context: str,
        max_tokens: int,
        verbose: bool = False,
        include_history: bool = False,
    ):
        """Ask Claude with progress spinner and timer, with streaming text display."""
        import time
        from rich.console import Console
        from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
        from core.formatting.context_formatter import count_tokens

        console = Console()

        # Log the question BEFORE starting timer
        provider_name = self.active_provider.title()
        self.logger.info("Asking %s: %s", provider_name, question)

        # Build full prompt to check if streaming will be used
        from core.ai.prompt_builder import get_prompt_builder
        prompt_builder = get_prompt_builder()
        full_prompt = prompt_builder.build_prompt(question, context)
        
        # Always use streaming for better UX (with fallback to standard if needed)
        will_use_streaming = True
        
        # Variables for streaming display
        accumulated_text = ""
        
        if will_use_streaming:
            # For streaming: print() direct for guaranteed scroll + final formatted panel
            start_time = time.time()
            
            try:
                from rich.markdown import Markdown
                from rich.panel import Panel
                
                # Send streaming start marker for VSCode (only in VSCode mode)
                if self._vscode_mode:
                    print("\n#= Context-AI Streaming START =#\n", flush=True)
                
                # Print header with Rich styling
                console.print("🌊 Context-AI Streaming Response...\n", style="bold green")
                
                def live_streaming_callback(text_chunk: str):
                    """Live callback with direct print for guaranteed scroll."""
                    nonlocal accumulated_text
                    accumulated_text += text_chunk
                    # Print directly to terminal for natural scroll
                    print(text_chunk, end="", flush=True)
                
                # Make streaming API call with direct print callback
                response = self.claude_client.ask(
                    question=question, 
                    context=context, 
                    max_tokens=max_tokens, 
                    verbose=verbose,
                    text_callback=live_streaming_callback
                )
                
                elapsed = time.time() - start_time
                response_tokens = response.usage.get("output_tokens", 0)
                
                # Send streaming end marker for VSCode (only in VSCode mode)
                if self._vscode_mode:
                    print("\n#= Context-AI Streaming END =#\n", flush=True)
                
                # After streaming, add final formatted panel to terminal history (only in CLI mode)
                print("\n")  # Add some spacing
                
                # Only show final panel in CLI mode (not in VSCode)
                if not (hasattr(self, '_vscode_mode') and self._vscode_mode):
                    try:
                        final_content = Markdown(accumulated_text.strip()) if accumulated_text.strip() else "No response received"
                    except:
                        final_content = accumulated_text.strip() if accumulated_text.strip() else "No response received"
                    
                    final_panel = Panel(
                        final_content,
                        title="🤖 Context-AI's Answer",
                        title_align="center",
                        border_style="green",
                        padding=(1, 2)
                    )
                    console.print(final_panel)
                
            except Exception:
                elapsed = time.time() - start_time
                error_panel = Panel(
                    f"❌ Streaming failed after {elapsed:.1f}s",
                    title="Error",
                    title_align="center",
                    border_style="red"
                )
                console.print(error_panel)
                raise
                
        else:
            # For non-streaming: use normal progress spinner
            progress_msg = "🧠 Asking Claude..." if include_history and hasattr(self, "chat_history") and self.chat_history.history else "🧠 Thinking..."
            
            # Start progress indication with timer
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                TimeElapsedColumn(),
                console=console,
                transient=False,
            ) as progress:
                task = progress.add_task(progress_msg, total=None)
                start_time = time.time()

                try:
                    # Make the actual API call (no streaming)
                    response = self.claude_client.ask(
                        question=question, context=context, max_tokens=max_tokens, verbose=verbose
                    )

                    elapsed = time.time() - start_time

                except Exception:
                    elapsed = time.time() - start_time
                    progress.update(task, description=f"❌ Request failed after {elapsed:.1f}s")
                    raise

                # Create completion message with response info
                response_tokens = response.usage.get("output_tokens", 0)
                
                if response_tokens > 0:
                    completion_msg = (
                        f"✅ Received response in {elapsed:.1f}s "
                        f"({response_tokens:,} tokens)"
                    )
                else:
                    completion_msg = f"✅ Received response in {elapsed:.1f}s"

                progress.update(task, description=completion_msg)

        # Log timing if verbose with streaming info
        if verbose:
            input_tokens = response.usage.get("input_tokens", 0)
            output_tokens = response.usage.get("output_tokens", 0)
            method = "streaming" if will_use_streaming else "standard"
            self.logger.info(
                "⏱️ Claude API (%s): %.1f seconds (%s in, %s out)",
                method,
                elapsed,
                f"{input_tokens:,}",
                f"{output_tokens:,}",
            )

        return response, will_use_streaming

    def _get_cached_context(
        self, question: str, max_tokens: int, verbose: bool, include_history: bool
    ) -> str:
        """Get context with intelligent caching for performance."""
        import hashlib
        import time

        from config.constants import CONTEXT_CACHE_TTL, ENABLE_CONTEXT_CACHE

        if not ENABLE_CONTEXT_CACHE:
            return self.query_service.query_context(
                question,
                format_type="ai_friendly",
                verbose=verbose,
                max_context_tokens=max_tokens,
            )

        # Create cache key based on question, active embeddings, token limit, and history inclusion
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
                # Remove expired entry
                del self._context_cache[cache_key]

        # Generate fresh context
        if verbose:
            self.logger.info("🔄 Generating fresh context...")

        context = self.query_service.query_context(
            question,
            format_type="ai_friendly",
            verbose=verbose,
            max_context_tokens=max_tokens,
        )

        # Cache the result
        self._context_cache[cache_key] = {"content": context, "timestamp": time.time()}

        # Limit cache size (keep only recent entries)
        if len(self._context_cache) > 10:
            # Remove oldest entries
            oldest_keys = sorted(
                self._context_cache.keys(),
                key=lambda k: self._context_cache[k]["timestamp"],
            )[
                :5
            ]  # Remove 5 oldest

            for old_key in oldest_keys:
                del self._context_cache[old_key]

        return context

    def _extract_context_summary_from_formatted(self, formatted_context: str) -> str:
        """Extract file summary from already formatted context sent to Claude."""
        import re
        
        if not formatted_context:
            return ""
        
        files_by_source = {}
        
        # Look for patterns like "## From sdk-v1 (similarity: 0.85):" followed by "**File:** path/to/file.py"
        source_pattern = r'## From ([^(]+) \(similarity: [^)]+\):'
        file_pattern = r'\*\*File:\*\* ([^(]+) \([^)]+\)'
        
        lines = formatted_context.split('\n')
        current_source = None
        
        for line in lines:
            # Check for source header
            source_match = re.search(source_pattern, line)
            if source_match:
                current_source = source_match.group(1).strip()
                if current_source not in files_by_source:
                    files_by_source[current_source] = set()
                continue
            
            # Check for file info
            if current_source:
                file_match = re.search(file_pattern, line)
                if file_match:
                    file_path = file_match.group(1).strip()
                    files_by_source[current_source].add(file_path)
        
        # Format compactly: source1: file1, file2 | source2: file3, file4  
        summary_parts = []
        for source, files in files_by_source.items():
            if files:  # Only include if we found files
                file_list = ', '.join(sorted(files))
                summary_parts.append(f"{source}: {file_list}")
        
        return ' | '.join(summary_parts)


def get_ai_service() -> AIService:
    """Get AI service instance."""
    return AIService()
