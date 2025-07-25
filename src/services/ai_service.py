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
    tokens_used: int = 0


class ChatHistoryManager:
    """Manages chat conversation history with intelligent truncation."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.history: List[ChatTurn] = []

    def add_turn(
        self, question: str, response: str, context: str = "", tokens: int = 0
    ) -> None:
        """Add a new turn to the conversation history."""
        turn = ChatTurn(
            question=question,
            response=response,
            timestamp=datetime.now(),
            context_used=context,
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
            conversation_text += f"Q{i+1}: {turn.question}\n"
            conversation_text += f"A{i+1}: {turn.response}\n\n"

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

        # Get Claude configuration
        config = self.settings_manager.get_config()
        self.claude_config = config.ai.get("claude")

        if not self.claude_config or not self.claude_config.api_key:
            raise ConfigurationError(
                "Claude API key not configured. Set it with: "
                "context-ai config set --claude-key YOUR_KEY"
            )

        self.claude_client = get_claude_client(
            self.claude_config.api_key, self.claude_config.default_model
        )

        self.logger.debug(
            "AI service initialized with model: %s", self.claude_config.default_model
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
                CLAUDE_CONTEXT_TOKEN_RATIO,
                CLAUDE_MAX_RESPONSE_TOKENS,
                CLAUDE_MAX_TOKENS,
                CLAUDE_MIN_RESPONSE_TOKENS,
                CLAUDE_RESPONSE_TOKEN_RATIO,
            )

            # Reserve space for question and response, use rest for context
            question_tokens = count_tokens(question)
            total_context_tokens = int(CLAUDE_MAX_TOKENS * CLAUDE_CONTEXT_TOKEN_RATIO)

            # Allocate tokens between code context and chat history
            if include_history:
                history_tokens = int(total_context_tokens * CHAT_HISTORY_TOKEN_RATIO)
                code_context_tokens = total_context_tokens - history_tokens

                # Get chat history within token budget
                chat_context = self.chat_history.get_history_context(history_tokens)
                chat_context_tokens = count_tokens(chat_context) if chat_context else 0

                if verbose and chat_context:
                    self.logger.info(
                        "💬 Chat history: %d tokens (%d turns)",
                        chat_context_tokens,
                        len(self.chat_history.history),
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

            if verbose:
                self.logger.info("📄 Context retrieved (%d characters)", len(context))

            # Calculate final token allocation
            context_tokens = count_tokens(context)
            input_tokens = context_tokens + question_tokens

            # Calculate available tokens and allocate response space
            available_tokens = CLAUDE_MAX_TOKENS - input_tokens
            max_response_tokens = min(
                available_tokens * CLAUDE_RESPONSE_TOKEN_RATIO,
                max(CLAUDE_MIN_RESPONSE_TOKENS, context_tokens // 2),
            )
            max_tokens = int(min(max_response_tokens, CLAUDE_MAX_RESPONSE_TOKENS))

            if verbose:
                self.logger.info(
                    "📊 Context limit: %d tokens (65%% of %d)",
                    total_context_tokens,
                    CLAUDE_MAX_TOKENS,
                )
                if include_history:
                    self.logger.info(
                        "📊 Allocation: %d code + %d history = %d total context",
                        code_context_tokens,
                        chat_context_tokens,
                        context_tokens,
                    )
                self.logger.info(
                    "📊 Input tokens: %d (context: %d, question: %d)",
                    input_tokens,
                    context_tokens,
                    question_tokens,
                )
                self.logger.info("📊 Dynamic response tokens: %d", max_tokens)

                # Performance diagnostic
                if input_tokens > 100000:
                    self.logger.warning(
                        "⚠️  Large context detected (%s tokens) - Claude may be slow",
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

            # Ask Claude with context with progress indication
            response = self._ask_claude_with_progress(
                question, context, max_tokens, verbose, include_history
            )

            # Handle output
            if output_file:
                self._save_to_file(response.content, output_file)
            else:
                self._display_response(response.content)

            if copy_to_clipboard:
                self._copy_to_clipboard(response.content)

            # Show token usage stats (always, but elegantly)
            self._display_token_stats(
                response, input_tokens, context_tokens, question_tokens, verbose
            )

            # Add to chat history if this is part of a conversation
            if include_history:
                total_tokens_used = response.usage.get(
                    "input_tokens", input_tokens
                ) + response.usage.get("output_tokens", 0)
                self.chat_history.add_turn(
                    question, response.content, context, total_tokens_used
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
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text

        self.logger.info("💬 Starting chat session with Claude...")
        self.logger.info("Type 'exit', 'quit', or press Ctrl+C to end the session")

        console = Console()

        # Welcome panel
        welcome_text = Text(
            "Ask questions about your codebase. Chat history will be maintained "
            "for context.\n\n"
            "Special commands: /history (stats), /clear (reset), "
            "/verbose (toggle), 'exit' (quit)",
            style="dim",
        )
        title = f"🤖 Claude Chat Session with History{' (Verbose)' if verbose else ''}"
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
                    if question.lower() == "/history":
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
        from rich.console import Console
        from rich.markdown import Markdown
        from rich.panel import Panel

        console = Console()

        # Create markdown content
        markdown_content = Markdown(content)

        # Display in a styled panel
        panel = Panel(
            markdown_content,
            title="🤖 Claude's Answer",
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
    ) -> None:
        """Display token usage statistics using logging."""
        from config.constants import CLAUDE_MAX_TOKENS

        # Get actual usage from response
        actual_input = response.usage.get("input_tokens", input_tokens)
        actual_output = response.usage.get("output_tokens", 0)
        total_used = actual_input + actual_output

        # Calculate percentages
        total_pct = (total_used / CLAUDE_MAX_TOKENS) * 100

        if verbose:
            # Detailed breakdown for verbose mode
            context_pct = (context_tokens / CLAUDE_MAX_TOKENS) * 100
            question_pct = (question_tokens / CLAUDE_MAX_TOKENS) * 100
            input_pct = (actual_input / CLAUDE_MAX_TOKENS) * 100
            output_pct = (actual_output / CLAUDE_MAX_TOKENS) * 100

            self.logger.info("📊 Token Usage Details:")
            self.logger.info(
                "  Context: %s tokens (%.1f%%)", f"{context_tokens:,}", context_pct
            )
            self.logger.info(
                "  Question: %s tokens (%.1f%%)", f"{question_tokens:,}", question_pct
            )
            self.logger.info(
                "  Input Total: %s tokens (%.1f%%)", f"{actual_input:,}", input_pct
            )
            self.logger.info(
                "  Response: %s tokens (%.1f%%)", f"{actual_output:,}", output_pct
            )
            self.logger.info(
                "  Total Used: %s tokens (%.1f%%)", f"{total_used:,}", total_pct
            )
            self.logger.info(
                "  Remaining: %s tokens (%.1f%%)",
                f"{CLAUDE_MAX_TOKENS - total_used:,}",
                100 - total_pct,
            )
        else:
            # Compact one-liner for normal mode
            self.logger.info(
                "📊 Tokens: %s in + %s out = %s total (%.1f%% of %s)",
                f"{actual_input:,}",
                f"{actual_output:,}",
                f"{total_used:,}",
                total_pct,
                f"{CLAUDE_MAX_TOKENS:,}",
            )

    def _ask_claude_with_progress(
        self,
        question: str,
        context: str,
        max_tokens: int,
        verbose: bool = False,
        include_history: bool = False,
    ):
        """Ask Claude with a progress spinner."""
        import time

        from rich.console import Console

        console = Console()

        # Create a descriptive progress message
        if verbose:
            context_info = f"{len(context):,} chars"
            if (
                include_history
                and hasattr(self, "chat_history")
                and self.chat_history.history
            ):
                context_info += f" + {len(self.chat_history.history)} turns history"
            progress_msg = (
                f"🧠 Asking Claude ({context_info}, max {max_tokens:,} tokens)..."
            )
        else:
            if (
                include_history
                and hasattr(self, "chat_history")
                and self.chat_history.history
            ):
                progress_msg = (
                    f"🧠 Thinking... (with {len(self.chat_history.history)} "
                    f"turn context)"
                )
            else:
                progress_msg = "🧠 Thinking..."

        # For longer contexts, show estimated time and choose appropriate spinner
        estimated_seconds = max(3, min(15, len(context) // 10000))  # Rough estimate
        if len(context) > 50000:
            progress_msg += f" (~{estimated_seconds}s)"
            spinner_type = "moon"  # Slower spinner for longer requests
        else:
            spinner_type = "dots"  # Fast spinner for quick requests

        # Start progress indication
        with console.status(progress_msg, spinner=spinner_type) as status:
            start_time = time.time()

            try:
                # Make the actual API call
                response = self.claude_client.ask(
                    question=question, context=context, max_tokens=max_tokens
                )

                elapsed = time.time() - start_time

            except Exception:
                elapsed = time.time() - start_time
                status.update(f"❌ Request failed after {elapsed:.1f}s")
                time.sleep(0.5)
                raise

            # Create completion message with response info
            response_tokens = response.usage.get("output_tokens", 0)
            if response_tokens > 0:
                completion_msg = (
                    f"✅ Response received in {elapsed:.1f}s "
                    f"({response_tokens:,} tokens)"
                )
            else:
                completion_msg = f"✅ Response received in {elapsed:.1f}s"

            status.update(completion_msg)
            time.sleep(0.8)  # Brief pause to show completion

        # Log timing if verbose
        if verbose:
            input_tokens = response.usage.get("input_tokens", 0)
            output_tokens = response.usage.get("output_tokens", 0)
            self.logger.info(
                "⏱️ Claude API: %.1f seconds (%s in, %s out)",
                elapsed,
                f"{input_tokens:,}",
                f"{output_tokens:,}",
            )

        return response

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

        # Create cache key based on question, active embeddings, and token limit
        active = self.settings_manager.get_active_embeddings()
        cache_key_data = f"{question}:{','.join(sorted(active.selected))}:{max_tokens}"
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


def get_ai_service() -> AIService:
    """Get AI service instance."""
    return AIService()
