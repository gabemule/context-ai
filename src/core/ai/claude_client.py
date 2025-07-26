"""
Claude API client for Context-AI.

Provides basic integration with Anthropic's Claude API for AI-powered
question answering and chat functionality.
"""

import time
from dataclasses import dataclass
from typing import Dict, Optional

from config.constants import (
    CLAUDE_DEFAULT_MODEL,
    CLAUDE_MAX_RETRIES,
    CLAUDE_MAX_TOKENS,
    CLAUDE_MODELS,
    CLAUDE_RETRY_DELAY,
    CLAUDE_TIMEOUT,
)
from core.ai.ai_client_interface import AIClientInterface, AIResponse, AIClientFactory
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

    def __init__(self, api_key: str, default_model: str = CLAUDE_DEFAULT_MODEL):
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
        self.max_retries = CLAUDE_MAX_RETRIES
        self.retry_delay = CLAUDE_RETRY_DELAY
        self.timeout = CLAUDE_TIMEOUT

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
        **provider_kwargs
    ) -> AIResponse:
        """
        Ask Claude a question with optional context.

        Args:
            question: User question
            context: Optional context to include
            model: Override default model
            max_tokens: Maximum tokens to generate
            **provider_kwargs: Claude-specific parameters (ignored for now)

        Returns:
            Standardized AIResponse
        """
        model = model or self.default_model
        max_tokens = max_tokens or CLAUDE_MAX_TOKENS
        model_name = CLAUDE_MODELS[model]

        # Build prompt using the dedicated PromptBuilder
        from core.ai.prompt_builder import get_prompt_builder
        prompt_builder = get_prompt_builder()
        prompt = prompt_builder.build_prompt(question, context)

        self.logger.info(
            "Asking Claude: %s",
            question[:100] + "..." if len(question) > 100 else question,
        )
        self.logger.debug(
            "Using model: %s (%s), max_tokens: %d", model, model_name, max_tokens
        )

        # Make API call with retry
        claude_response = self._make_request_with_retry(
            prompt=prompt, model=model_name, max_tokens=max_tokens
        )

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
            provider="claude"
        )

    def get_available_models(self) -> list[str]:
        """Get list of available Claude models."""
        return list(CLAUDE_MODELS.keys())

    def get_provider_name(self) -> str:
        """Get the name of this AI provider."""
        return "claude"

    def _make_request_with_retry(
        self, prompt: str, model: str, max_tokens: int
    ) -> ClaudeResponse:
        """Make API request with retry logic."""
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                return self._make_request(prompt, model, max_tokens)

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

    def _make_request(self, prompt: str, model: str, max_tokens: int) -> ClaudeResponse:
        """Make single API request."""
        try:
            import anthropic
        except ImportError:
            raise ConfigurationError(
                "Anthropic library not installed. Install with: pip install anthropic"
            )

        try:
            client = anthropic.Anthropic(api_key=self.api_key)

            self.logger.debug("Making API request to Claude")

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


def get_claude_client(api_key: str, model: Optional[str] = None) -> ClaudeClient:
    """Get Claude client instance."""
    return ClaudeClient(api_key=api_key, default_model=model or CLAUDE_DEFAULT_MODEL)


# Register Claude client in the factory
AIClientFactory.register_provider("claude", ClaudeClient)
