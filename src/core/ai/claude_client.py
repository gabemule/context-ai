"""
Claude API client for Context-AI.

Provides basic integration with Anthropic's Claude API for AI-powered
question answering and chat functionality.
"""

import time
from dataclasses import dataclass
from typing import Dict, Optional

from config.constants import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_DELAY,
    DEFAULT_TIMEOUT,
)
from config.providers.claude import (
    CLAUDE_MODELS,
    DEFAULT_MODEL,
    get_max_tokens,
)
from core.ai.ai_client_interface import AIClientFactory, AIClientInterface, AIResponse
from core.ai.token_manager import get_token_manager
from utils.exceptions import APIError, ConfigurationError
from utils.logging import get_logger


@dataclass
class ClaudeResponse:
    """Internal Claude API response (before conversion to AIResponse)."""

    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: Optional[str] = None


class ClaudeClient(AIClientInterface):
    """Basic Claude API client with retry logic and Claude-3/4 model support."""

    def __init__(self, api_key: str, default_model: str = DEFAULT_MODEL):
        """
        Initialize Claude client.

        Args:
            api_key: Anthropic API key
            default_model: Default Claude model to use (model key, not full name)
        """
        self.logger = get_logger(__name__)

        if not api_key or not api_key.startswith("sk-ant-"):
            raise ConfigurationError("Invalid Claude API key format")

        # Validate model
        if default_model not in CLAUDE_MODELS:
            raise ConfigurationError(
                f"Unsupported model: {default_model}. "
                f"Supported models: {list(CLAUDE_MODELS.keys())}"
            )

        self.api_key = api_key
        self.default_model = default_model
        self.base_url = "https://api.anthropic.com/v1"

        # Configuration from constants
        self.max_retries = DEFAULT_MAX_RETRIES
        self.retry_delay = DEFAULT_RETRY_DELAY
        self.timeout = DEFAULT_TIMEOUT

        self.logger.debug(
            "Claude client initialized with model: %s (%s)",
            default_model,
            CLAUDE_MODELS[default_model],
        )

    def validate_connection(self) -> bool:
        """
        Test API key validity with a minimal request.

        Returns:
            True if connection is valid, False otherwise
        """
        try:
            self.logger.debug("Validating Claude API connection")
            self.ask("Hi", max_tokens=10)
            self.logger.info("✅ Claude API connection validated successfully")
            return True
        except APIError as e:
            if "401" in str(e) or "403" in str(e):
                self.logger.error("❌ Invalid Claude API key")
            else:
                self.logger.error("❌ Claude API connection failed: %s", e)
            return False
        except Exception as e:
            self.logger.error("❌ Unexpected error validating connection: %s", e)
            return False

    def ask(
        self,
        question: str,
        context: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        **provider_kwargs,
    ) -> AIResponse:
        """
        Ask Claude a question with optional context.

        Args:
            question: User question
            context: Optional context to include
            model: Override default model
            max_tokens: Maximum tokens to generate
            **provider_kwargs: Claude-specific parameters (verbose, text_callback, etc.)

        Returns:
            Standardized AIResponse
        """
        model = model or self.default_model
        max_tokens = max_tokens or get_max_tokens()

        # Get API name dynamically from model config
        from config.providers.registry import get_provider_function

        get_model_config = get_provider_function("get_model_config")
        model_config = get_model_config(model)
        model_name = model_config.get("api_name", model) if model_config else model

        # Extract parameters from provider_kwargs
        verbose = provider_kwargs.get("verbose", False)
        text_callback = provider_kwargs.get("text_callback", None)

        # Build prompt using the dedicated PromptBuilder
        from core.ai.prompt_builder import get_prompt_builder

        prompt_builder = get_prompt_builder()
        prompt = prompt_builder.build_prompt(question, context)

        # Show streaming message after prompt is built (correct position!)
        if text_callback:  # Only show if streaming is expected
            from rich.console import Console

            console = Console()
            console.print("\n🌊 Context-AI Streaming Response...\n", style="bold green")

        self.logger.debug(
            "Using model: %s (%s), max_tokens: %d", model, model_name, max_tokens
        )

        # Make API call with retry
        claude_response = self._make_request_with_retry(
            prompt=prompt,
            model=model_name,
            max_tokens=max_tokens,
            text_callback=text_callback,
        )

        # Only log response in verbose mode
        if verbose:
            self.logger.info(
                "Claude response received (%d tokens)",
                claude_response.usage.get("output_tokens", 0),
            )

        # Convert to standardized AIResponse
        return AIResponse(
            content=claude_response.content,
            model=claude_response.model,
            usage=claude_response.usage,
            finish_reason=claude_response.finish_reason,
            provider="claude",
        )

    def get_available_models(self) -> list[str]:
        """Get list of available Claude models."""
        return list(CLAUDE_MODELS.keys())

    def get_provider_name(self) -> str:
        """Get the name of this AI provider."""
        return "claude"

    def _make_request_with_retry(
        self, prompt: str, model: str, max_tokens: int, text_callback=None
    ) -> ClaudeResponse:
        """Make API request with retry logic."""
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                return self._make_request(prompt, model, max_tokens, text_callback)

            except APIError as e:
                last_error = e

                # Don't retry on authentication errors
                if "401" in str(e) or "403" in str(e):
                    raise e

                # Don't retry on the last attempt
                if attempt == self.max_retries:
                    break

                # Exponential backoff
                delay = self.retry_delay * (2**attempt)
                self.logger.warning(
                    "API request failed (attempt %d/%d), retrying in %.1fs: %s",
                    attempt + 1,
                    self.max_retries + 1,
                    delay,
                    e,
                )
                time.sleep(delay)

        # All retries failed
        raise APIError(
            f"API request failed after {self.max_retries + 1} attempts: {last_error}"
        )

    def _should_use_streaming(self, prompt: str) -> bool:
        """Determine if streaming should be used based on input size."""
        from config.constants import STREAMING_THRESHOLD_TOKENS

        # Use streaming for large contexts to avoid timeouts
        input_tokens = get_token_manager().count_tokens(prompt)

        should_stream = input_tokens > STREAMING_THRESHOLD_TOKENS
        if should_stream:
            self.logger.debug(
                "🌊 Using streaming for large context (%dK tokens > %dK threshold)",
                input_tokens // 1000,
                STREAMING_THRESHOLD_TOKENS // 1000,
            )

        return should_stream

    def _make_request(
        self, prompt: str, model: str, max_tokens: int, text_callback=None
    ) -> ClaudeResponse:
        """Make API request with automatic streaming detection."""
        use_streaming = self._should_use_streaming(prompt)

        try:
            if use_streaming:
                return self._make_streaming_request(
                    prompt, model, max_tokens, text_callback
                )
            else:
                return self._make_standard_request(prompt, model, max_tokens)
        except Exception as e:
            # Fallback: if streaming fails, try standard (if we were streaming)
            if use_streaming:
                self.logger.warning(
                    "🌊 Streaming failed, falling back to standard API: %s", e
                )
                try:
                    return self._make_standard_request(prompt, model, max_tokens)
                except Exception as fallback_error:
                    raise APIError(
                        f"Both streaming and standard API failed. Last error: {fallback_error}"
                    )
            else:
                raise

    def _make_standard_request(
        self, prompt: str, model: str, max_tokens: int
    ) -> ClaudeResponse:
        """Make standard (non-streaming) API request."""
        try:
            import anthropic
        except ImportError:
            raise ConfigurationError(
                "Anthropic library not installed. Install with: pip install anthropic"
            )

        try:
            client = anthropic.Anthropic(api_key=self.api_key)

            self.logger.debug("Making standard API request to Claude")

            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract response content
            content = ""
            if response.content and len(response.content) > 0:
                content = response.content[0].text

            return ClaudeResponse(
                content=content,
                model=response.model,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
                finish_reason=response.stop_reason,
            )

        except anthropic.AuthenticationError as e:
            raise APIError(f"Authentication failed: {e}")
        except anthropic.RateLimitError as e:
            raise APIError(f"Rate limit exceeded: {e}")
        except anthropic.APIError as e:
            raise APIError(f"Claude API error: {e}")
        except Exception as e:
            raise APIError(f"Unexpected error calling Claude API: {e}")

    def _make_streaming_request(
        self, prompt: str, model: str, max_tokens: int, text_callback=None
    ) -> ClaudeResponse:
        """Make streaming API request with real-time progress and optional text callback."""
        try:
            import anthropic
        except ImportError:
            raise ConfigurationError(
                "Anthropic library not installed. Install with: pip install anthropic"
            )

        try:
            client = anthropic.Anthropic(api_key=self.api_key)

            self.logger.debug("🌊 Making streaming API request to Claude")

            # Collect streaming response
            content_parts = []
            input_tokens = 0
            output_tokens = 0
            model_used = model
            finish_reason = None

            # Create streaming request
            with client.messages.stream(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            ) as stream:

                for event in stream:
                    if hasattr(event, "type"):
                        # Handle different event types
                        if event.type == "message_start":
                            if hasattr(event.message, "usage"):
                                input_tokens = event.message.usage.input_tokens
                            if hasattr(event.message, "model"):
                                model_used = event.message.model

                        elif event.type == "content_block_delta":
                            if hasattr(event.delta, "text"):
                                text_chunk = event.delta.text
                                content_parts.append(text_chunk)

                                # Call text callback for real-time display
                                if text_callback:
                                    text_callback(text_chunk)

                        elif event.type == "message_delta":
                            if hasattr(event.delta, "stop_reason"):
                                finish_reason = event.delta.stop_reason
                            if hasattr(event.usage, "output_tokens"):
                                output_tokens = event.usage.output_tokens

            # Combine all content parts
            content = "".join(content_parts)

            self.logger.debug(
                "🌊 Streaming completed successfully (%d tokens)", output_tokens
            )

            return ClaudeResponse(
                content=content,
                model=model_used,
                usage={
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                },
                finish_reason=finish_reason,
            )

        except anthropic.AuthenticationError as e:
            raise APIError(f"Authentication failed: {e}")
        except anthropic.RateLimitError as e:
            raise APIError(f"Rate limit exceeded: {e}")
        except anthropic.APIError as e:
            raise APIError(f"Claude API error: {e}")
        except Exception as e:
            raise APIError(f"Unexpected error in streaming request: {e}")


def get_claude_client(api_key: str, model: Optional[str] = None) -> ClaudeClient:
    """Get Claude client instance."""
    return ClaudeClient(api_key=api_key, default_model=model or DEFAULT_MODEL)


# Register Claude client in the factory
AIClientFactory.register_provider("claude", ClaudeClient)
