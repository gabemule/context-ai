"""
AI service for Context-AI.

Integrates Claude with the query system to provide AI-powered question answering.
"""

from typing import Optional, List

from utils.logging import get_logger
from utils.exceptions import ConfigurationError, APIError
from config.settings import get_settings_manager
from core.ai.claude_client import get_claude_client
from services.embedding_service import QueryService
from core.formatting.context_formatter import count_tokens


class AIService:
    """AI service that combines context retrieval with Claude."""
    
    def __init__(self):
        """Initialize AI service."""
        self.logger = get_logger(__name__)
        self.settings_manager = get_settings_manager()
        self.query_service = QueryService()
        
        # Get Claude configuration
        config = self.settings_manager.get_config()
        self.claude_config = config.ai.get("claude")
        
        if not self.claude_config or not self.claude_config.api_key:
            raise ConfigurationError(
                "Claude API key not configured. Set it with: context-ai config set --claude-key YOUR_KEY"
            )
        
        self.claude_client = get_claude_client(
            self.claude_config.api_key,
            self.claude_config.default_model
        )
        
        self.logger.debug("AI service initialized with model: %s", self.claude_config.default_model)
    
    def ask_question(self, question: str, context_format: str = "ai_friendly", 
                     verbose: bool = False, copy_to_clipboard: bool = False, 
                     output_file: str = None) -> str:
        """
        Ask a question with context from active embeddings.
        
        Args:
            question: User question
            context_format: Format for context retrieval and output
            verbose: Show detailed information
            copy_to_clipboard: Copy response to clipboard
            output_file: Save response to file
            
        Returns:
            The AI response text or formatted context (depending on format)
        """
        self.logger.info("🤖 Processing question: %s", question[:100] + "..." if len(question) > 100 else question)
        
        try:
            # Get context from embeddings
            if verbose:
                self.logger.info("🔍 Retrieving context from active embeddings...")
            
            # For non-AI formats, return formatted context directly
            if context_format in ["json", "xml", "plain", "markdown"]:
                context = self.query_service.query_context(
                    question, 
                    format_type=context_format,
                    verbose=verbose
                )
                
                if verbose:
                    self.logger.info("📄 Context retrieved (%d characters)", len(context))
                    self.logger.info("🎯 Returning formatted context (no AI processing)")
                
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
                CLAUDE_MAX_TOKENS, CLAUDE_CONTEXT_TOKEN_RATIO, CLAUDE_RESPONSE_TOKEN_RATIO,
                CLAUDE_MIN_RESPONSE_TOKENS, CLAUDE_MAX_RESPONSE_TOKENS
            )
            
            # Reserve space for question and response, use rest for context
            question_tokens = count_tokens(question)
            max_context_tokens = int(CLAUDE_MAX_TOKENS * CLAUDE_CONTEXT_TOKEN_RATIO)
            
            # For ai_friendly format, continue with Claude processing
            context = self.query_service.query_context(
                question, 
                format_type="ai_friendly",
                verbose=verbose,
                max_context_tokens=max_context_tokens
            )
            
            if verbose:
                self.logger.info("📄 Context retrieved (%d characters)", len(context))
            
            # Calculate final token allocation
            context_tokens = count_tokens(context)
            input_tokens = context_tokens + question_tokens
            
            # Calculate available tokens and allocate response space
            available_tokens = CLAUDE_MAX_TOKENS - input_tokens
            max_response_tokens = min(
                available_tokens * CLAUDE_RESPONSE_TOKEN_RATIO,
                max(CLAUDE_MIN_RESPONSE_TOKENS, context_tokens // 2)
            )
            max_tokens = int(min(max_response_tokens, CLAUDE_MAX_RESPONSE_TOKENS))
            
            if verbose:
                self.logger.info("📊 Context limit: %d tokens (65%% of %d)", max_context_tokens, CLAUDE_MAX_TOKENS)
                self.logger.info("📊 Input tokens: %d (context: %d, question: %d)", 
                               input_tokens, context_tokens, question_tokens)
                self.logger.info("📊 Dynamic response tokens: %d", max_tokens)
            
            # Ask Claude with context
            if verbose:
                self.logger.info("🧠 Asking Claude...")
            
            response = self.claude_client.ask(
                question=question,
                context=context,
                max_tokens=max_tokens
            )
            
            # Handle output
            if output_file:
                self._save_to_file(response.content, output_file)
            else:
                self._display_response(response.content)
            
            if copy_to_clipboard:
                self._copy_to_clipboard(response.content)
            
            # Show token usage stats (always, but elegantly)
            self._display_token_stats(response, input_tokens, context_tokens, question_tokens, verbose)
            
            return response.content
        
        except APIError as e:
            self.logger.error("❌ Claude API error: %s", e)
            raise
        except Exception as e:
            self.logger.error("❌ Error processing question: %s", e)
            raise
    
    def start_chat(self) -> None:
        """Start interactive chat session (basic implementation)."""
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text
        
        self.logger.info("💬 Starting chat session with Claude...")
        self.logger.info("Type 'exit', 'quit', or press Ctrl+C to end the session")
        
        console = Console()
        
        # Welcome panel
        welcome_text = Text("Ask questions about your codebase. Type 'exit' to quit.", style="dim")
        welcome_panel = Panel(
            welcome_text,
            title="🤖 Claude Chat Session",
            title_align="center",
            border_style="green",
            padding=(1, 2)
        )
        
        console.print()
        console.print(welcome_panel)
        console.print()
        
        try:
            while True:
                try:
                    question = input("You: ").strip()
                    
                    if question.lower() in ['exit', 'quit', 'bye']:
                        self.logger.info("Goodbye! 👋")
                        break
                    
                    if not question:
                        continue
                    
                    # Use the same display method but without verbose logging
                    self.ask_question(question, verbose=False)
                    
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
            
            with open(output_file, 'w', encoding='utf-8') as f:
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
            self.logger.warning("⚠️  pyperclip not installed. Install with: pip install pyperclip")
        except Exception as e:
            self.logger.warning("⚠️  Failed to copy to clipboard: %s", e)
    
    def _display_response(self, content: str) -> None:
        """Display response with rich formatting."""
        from rich.console import Console
        from rich.panel import Panel
        from rich.markdown import Markdown
        
        console = Console()
        
        # Create markdown content
        markdown_content = Markdown(content)
        
        # Display in a styled panel
        panel = Panel(
            markdown_content,
            title="🤖 Claude's Answer",
            title_align="center",
            border_style="green",
            padding=(1, 2)
        )
        
        console.print()
        console.print(panel)
        console.print()
    
    def _display_token_stats(self, response, input_tokens: int, context_tokens: int, 
                           question_tokens: int, verbose: bool = False) -> None:
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
            self.logger.info("  Context: %s tokens (%.1f%%)", f"{context_tokens:,}", context_pct)
            self.logger.info("  Question: %s tokens (%.1f%%)", f"{question_tokens:,}", question_pct)
            self.logger.info("  Input Total: %s tokens (%.1f%%)", f"{actual_input:,}", input_pct)
            self.logger.info("  Response: %s tokens (%.1f%%)", f"{actual_output:,}", output_pct)
            self.logger.info("  Total Used: %s tokens (%.1f%%)", f"{total_used:,}", total_pct)
            self.logger.info("  Remaining: %s tokens (%.1f%%)", f"{CLAUDE_MAX_TOKENS - total_used:,}", 100 - total_pct)
        else:
            # Compact one-liner for normal mode
            self.logger.info("📊 Tokens: %s in + %s out = %s total (%.1f%% of %s)", 
                           f"{actual_input:,}", f"{actual_output:,}", f"{total_used:,}", 
                           total_pct, f"{CLAUDE_MAX_TOKENS:,}")


def get_ai_service() -> AIService:
    """Get AI service instance."""
    return AIService()