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
from utils.exceptions import APIError, ConfigurationError
from utils.logging import get_logger


@dataclass
class ClaudeResponse:
    """Response from Claude API."""

    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: Optional[str] = None


class ClaudeClient:
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
        max_tokens: int = CLAUDE_MAX_TOKENS,
    ) -> ClaudeResponse:
        """
        Ask Claude a question with optional context.

        Args:
            question: User question
            context: Optional context to include
            model: Override default model
            max_tokens: Maximum tokens to generate

        Returns:
            ClaudeResponse with answer
        """
        model = model or self.default_model
        model_name = CLAUDE_MODELS[model]

        # Build prompt
        prompt = self._build_prompt(question, context)

        self.logger.info(
            "Asking Claude: %s",
            question[:100] + "..." if len(question) > 100 else question,
        )
        self.logger.debug(
            "Using model: %s (%s), max_tokens: %d", model, model_name, max_tokens
        )

        # Make API call with retry
        response = self._make_request_with_retry(
            prompt=prompt, model=model_name, max_tokens=max_tokens
        )

        self.logger.info(
            "Claude response received (%d tokens)",
            response.usage.get("output_tokens", 0),
        )
        return response

    def _build_prompt(self, question: str, context: Optional[str] = None) -> str:
        """Build prompt based on configured mode - from minimal to comprehensive."""
        if not context:
            return question

        from config.constants import PROMPT_MODE

        if PROMPT_MODE == "minimal":
            return self._build_minimal_prompt(question, context)
        elif PROMPT_MODE == "standard":
            return self._build_standard_prompt(question, context)
        elif PROMPT_MODE == "comprehensive":
            return self._build_comprehensive_prompt(question, context)
        elif PROMPT_MODE == "strict":
            return self._build_strict_prompt(question, context)
        else:
            # Default to standard
            return self._build_standard_prompt(question, context)

    def _build_minimal_prompt(self, question: str, context: str) -> str:
        """Build minimal prompt with no extra instructions - fastest processing."""
        return f"""Based on the following context from the codebase, please answer \
the question.

## Context:
{context}

## Question:
{question}"""

    def _build_standard_prompt(self, question: str, context: str) -> str:
        """Build standard prompt with cross-project awareness and coding \
guidelines."""
        base_instructions = (
            "Based on the following context from the codebase, "
            "please answer the question."
        )

        # Add cross-project hints for multi-project contexts
        is_cross_project = (
            "Cross-Project Analysis" in context and "Project Correlations" in context
        )
        if is_cross_project:
            base_instructions += """

Note: This context contains code from multiple projects - consider \
comparing approaches when relevant."""

        # Always include coding guidelines when applicable
        guidelines = self._get_applicable_guidelines(context, question)
        if guidelines:
            guidelines_section = f"""

{guidelines}

**When providing code examples or suggestions, please follow the above guidelines.**"""
            base_instructions += guidelines_section

        return f"""{base_instructions}

## Context:
{context}

## Question:
{question}"""

    def _build_comprehensive_prompt(self, question: str, context: str) -> str:
        """Build comprehensive prompt with full cross-project analysis and \
architectural insights."""
        base_instructions = (
            "Based on the following context from the codebase, "
            "please answer the question."
        )

        # Check if this is cross-project context
        is_cross_project = (
            "Cross-Project Analysis" in context and "Project Correlations" in context
        )

        if is_cross_project:
            from config.constants import ENABLE_CROSS_PROJECT_PROMPTS

            if ENABLE_CROSS_PROJECT_PROMPTS:
                cross_project_instructions = """

**CROSS-PROJECT ANALYSIS**: This context contains code from multiple projects. Please:
- Compare implementations across different projects
- Highlight similarities and differences between approaches
- Identify reusable patterns or components
- Suggest opportunities for standardization or consistency improvements
- Point out which project has the most robust/complete implementation
- Consider architectural differences and their implications
- Recommend best practices based on the patterns observed"""

                base_instructions += cross_project_instructions

        # Always include coding guidelines when applicable
        guidelines = self._get_applicable_guidelines(context, question)
        if guidelines:
            guidelines_section = f"""

{guidelines}

**When providing code examples or suggestions, please follow the above \
guidelines and explain your architectural choices.**"""
            base_instructions += guidelines_section

        return f"""{base_instructions}

## Context:
{context}

## Question:
{question}

Please provide a comprehensive answer with architectural insights and \
best practices recommendations."""

    def _build_strict_prompt(self, question: str, context: str) -> str:
        """Build strict prompt with enforced coding standards and detailed \
code review approach."""
        base_instructions = (
            "Based on the following context from the codebase, please answer the "
            "question with a focus on code quality and best practices."
        )

        # Always include cross-project analysis when applicable
        is_cross_project = (
            "Cross-Project Analysis" in context and "Project Correlations" in context
        )
        if is_cross_project:
            cross_project_instructions = """

**CODE REVIEW APPROACH**: Analyze implementations across projects and provide \
detailed feedback on:
- Code quality and maintainability differences
- Performance implications of different approaches
- Security considerations
- Testing strategies
- Documentation quality"""
            base_instructions += cross_project_instructions

        # Always try to include guidelines with force=True
        guidelines = self._get_applicable_guidelines(context, question, force=True)
        if guidelines:
            guidelines_section = f"""

{guidelines}

**STRICT ENFORCEMENT**: All code suggestions must strictly adhere to the \
above guidelines. Review existing code for violations and suggest \
improvements."""
            base_instructions += guidelines_section

        return f"""{base_instructions}

## Context:
{context}

## Question:
{question}

Provide a detailed answer with code review insights, strict adherence to \
guidelines, and actionable improvement recommendations."""

    def _get_applicable_guidelines(
        self, context: str, question: str, force: bool = False
    ) -> Optional[str]:
        """Get applicable coding guidelines for the current context and question."""
        try:
            from config.constants import ENABLE_CODING_GUIDELINES

            if not ENABLE_CODING_GUIDELINES and not force:
                return None

            from config.guidelines.manager import get_guidelines_manager

            guidelines_manager = get_guidelines_manager()

            if force:
                # Force mode: try to detect languages and apply guidelines regardless
                languages = guidelines_manager.detect_languages_in_context(context)
                if languages:
                    return guidelines_manager.get_guidelines_for_languages(languages)
                return None
            else:
                return guidelines_manager.get_applicable_guidelines(context, question)

        except Exception as e:
            # Don't let guidelines errors break the main functionality
            from utils.logging import get_logger

            logger = get_logger(__name__)
            logger.debug("Failed to load guidelines: %s", e)
            return None

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
