"""
Claude API client for Context-AI.

Provides basic integration with Anthropic's Claude API for AI-powered
question answering and chat functionality.
"""

import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from utils.logging import get_logger
from utils.exceptions import APIError, ConfigurationError
from config.constants import (
    CLAUDE_MODELS, 
    CLAUDE_DEFAULT_MODEL, 
    CLAUDE_MAX_TOKENS,
    CLAUDE_MAX_RETRIES,
    CLAUDE_RETRY_DELAY,
    CLAUDE_TIMEOUT
)


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
        
        self.logger.debug("Claude client initialized with model: %s (%s)", 
                         default_model, CLAUDE_MODELS[default_model])
    
    def validate_connection(self) -> bool:
        """
        Test API key validity with a minimal request.
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            self.logger.debug("Validating Claude API connection")
            response = self.ask("Hi", max_tokens=10)
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
    
    def ask(self, 
            question: str, 
            context: Optional[str] = None,
            model: Optional[str] = None,
            max_tokens: int = CLAUDE_MAX_TOKENS) -> ClaudeResponse:
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
        
        self.logger.info("Asking Claude: %s", question[:100] + "..." if len(question) > 100 else question)
        self.logger.debug("Using model: %s (%s), max_tokens: %d", model, model_name, max_tokens)
        
        # Make API call with retry
        response = self._make_request_with_retry(
            prompt=prompt,
            model=model_name,
            max_tokens=max_tokens
        )
        
        self.logger.info("Claude response received (%d tokens)", response.usage.get("output_tokens", 0))
        return response
    
    def _build_prompt(self, question: str, context: Optional[str] = None) -> str:
        """Build enhanced prompt for Claude with cross-project correlation focus."""
        if not context:
            return question
        
        # Check if this is cross-project context (contains multiple source embeddings)
        is_cross_project = "Cross-Project Analysis" in context and "Project Correlations" in context
        
        base_instructions = """Based on the following context from the codebase, please answer the question."""
        
        if is_cross_project:
            cross_project_instructions = """

**IMPORTANT**: This context contains code from multiple projects. Please:
- Compare implementations across different projects
- Highlight similarities and differences between approaches
- Identify reusable patterns or components
- Suggest opportunities for standardization or consistency improvements
- Point out which project has the most robust/complete implementation
- Consider architectural differences and their implications"""
            
            base_instructions += cross_project_instructions
        
        return f"""{base_instructions}

## Context:
{context}

## Question:
{question}

Please provide a comprehensive answer that leverages the cross-project insights when available."""
    
    def _make_request_with_retry(self, 
                                prompt: str, 
                                model: str, 
                                max_tokens: int) -> ClaudeResponse:
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
                delay = self.retry_delay * (2 ** attempt)
                self.logger.warning(
                    "API request failed (attempt %d/%d), retrying in %.1fs: %s",
                    attempt + 1, self.max_retries + 1, delay, e
                )
                time.sleep(delay)
        
        # All retries failed
        raise APIError(f"API request failed after {self.max_retries + 1} attempts: {last_error}")
    
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
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
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
                    "output_tokens": response.usage.output_tokens
                },
                finish_reason=response.stop_reason
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