"""
Token Management for Context-AI.

Centralized token counting with provider-specific implementations.
Supports Anthropic (Claude) and OpenAI (GPT) token counting with LRU cache for performance.
"""

from typing import Dict, Optional
from enum import Enum
from functools import lru_cache
from utils.logging import get_logger

# Centralized fallback constants
AVG_CHARS_PER_TOKEN = 4

def _fallback_token_estimation(text: str) -> int:
    """Centralized fallback token estimation."""
    return max(1, len(text.strip()) // AVG_CHARS_PER_TOKEN)

class TokenProvider(Enum):
    """Supported token counting providers."""
    CLAUDE = "claude"  # Uses tiktoken (good approximation for Claude)
    OPENAI = "openai"  # Uses tiktoken (native)
    AUTO = "auto"  # Detect from active provider

class TiktokenCounter:
    """OpenAI-specific token counter using tiktoken."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self._encoder = None
        self._load_encoder()
    
    def _load_encoder(self):
        """Load tiktoken encoder with error handling."""
        try:
            import tiktoken
            self._encoder = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
            self.logger.debug("Tiktoken encoder loaded successfully")
        except ImportError:
            self.logger.debug("Tiktoken library not available")
            self._encoder = None
        except Exception as e:
            self.logger.warning(f"Error loading tiktoken encoder: {e}")
            self._encoder = None
    
    def count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken."""
        if self._encoder:
            try:
                return len(self._encoder.encode(text))
            except Exception as e:
                self.logger.warning(f"Tiktoken encoding error: {e}, using fallback")
                return _fallback_token_estimation(text)
        else:
            return _fallback_token_estimation(text)

class TokenManager:
    """Centralized token management with provider-specific counting and LRU cache."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        # Both providers now use tiktoken for speed and reliability
        shared_counter = TiktokenCounter()
        self._counters = {
            TokenProvider.CLAUDE: shared_counter,
            TokenProvider.OPENAI: shared_counter,
        }
        self._active_provider = TokenProvider.CLAUDE  # Default to Claude
        self._auto_detect_provider()
    
    def _auto_detect_provider(self) -> None:
        """Auto-detect provider from active configuration."""
        try:
            from config.providers.registry import get_provider_registry
            registry = get_provider_registry()
            provider_name = registry.config_core.get_active_provider()  # ← API correta
            
            if provider_name == "claude":
                self._active_provider = TokenProvider.CLAUDE
            elif provider_name == "openai":
                self._active_provider = TokenProvider.OPENAI
            else:
                self.logger.debug(f"Unknown provider {provider_name}, defaulting to Claude")
                
        except Exception as e:
            self.logger.debug(f"Provider auto-detection failed: {e}, defaulting to Claude")
            self._active_provider = TokenProvider.CLAUDE
    
    def set_active_provider(self, provider: TokenProvider) -> None:
        """Set the active token counting provider."""
        self._active_provider = provider
        self.logger.debug(f"Active token provider set to: {provider.value}")
    
    def get_active_provider(self) -> TokenProvider:
        """Get current active provider."""
        return self._active_provider
    
    @lru_cache(maxsize=1000)
    def count_tokens(self, text: str, provider: Optional[TokenProvider] = None) -> int:
        """
        Count tokens in text using specified or active provider.
        
        Uses LRU cache for performance - repeated texts are cached.
        
        Args:
            text: Text to count tokens for
            provider: Specific provider to use (defaults to active provider)
        
        Returns:
            Number of tokens in the text
        """
        if not text or not text.strip():
            return 0
        
        provider = provider or self._active_provider
        counter = self._counters[provider]
        
        try:
            token_count = counter.count_tokens(text)
            self.logger.debug(f"Token count for {len(text)} chars: {token_count} tokens ({provider.value})")
            return token_count
        except Exception as e:
            self.logger.error(f"Token counting failed: {e}")
            # Final fallback
            return _fallback_token_estimation(text)
    
    def calculate_context_allocation(self, question: str, include_history: bool = False) -> Dict[str, int]:
        """
        Calculate token allocation for context and history.
        
        Migrated from TokenCalculator in ai_service.py
        """
        from config.constants.ai import CHAT_HISTORY_TOKEN_RATIO, CONTEXT_TOKEN_RATIO
        from config.providers.registry import get_provider_registry
        
        registry = get_provider_registry()
        get_max_tokens = registry.get_max_tokens
        
        question_tokens = self.count_tokens(question)
        total_context_tokens = int(get_max_tokens() * CONTEXT_TOKEN_RATIO)
        
        if include_history:
            history_tokens = int(total_context_tokens * CHAT_HISTORY_TOKEN_RATIO)
            code_context_tokens = total_context_tokens - history_tokens
        else:
            history_tokens = 0
            code_context_tokens = total_context_tokens
        
        allocation = {
            "question_tokens": question_tokens,
            "total_context_tokens": total_context_tokens,
            "history_tokens": history_tokens,
            "code_context_tokens": code_context_tokens
        }
        
        self.logger.debug(f"Context allocation: {allocation}")
        return allocation
    
    def calculate_response_tokens(self, input_tokens: int, context_tokens: int) -> int:
        """
        Calculate maximum response tokens.
        
        Migrated from TokenCalculator in ai_service.py
        """
        from config.constants.ai import MIN_RESPONSE_TOKENS, RESPONSE_TOKEN_RATIO
        from config.providers.registry import get_provider_registry
        
        registry = get_provider_registry()
        get_max_tokens = registry.get_max_tokens
        get_max_output_tokens = registry.get_max_output_tokens
        
        model_max_tokens = get_max_tokens()
        model_max_output = get_max_output_tokens()
        
        available_tokens = model_max_tokens - input_tokens
        max_response_tokens = min(
            available_tokens * RESPONSE_TOKEN_RATIO,
            max(MIN_RESPONSE_TOKENS, context_tokens // 2),
        )
        
        final_response_tokens = int(min(max_response_tokens, model_max_output))
        
        self.logger.debug(f"Response tokens calculated: {final_response_tokens} (input: {input_tokens}, context: {context_tokens})")
        return final_response_tokens
    
    def should_use_streaming(self, text: str) -> bool:
        """Determine if streaming should be used based on input size."""
        from config.constants.ai import STREAMING_THRESHOLD_TOKENS
        token_count = self.count_tokens(text)
        use_streaming = token_count > STREAMING_THRESHOLD_TOKENS
        
        self.logger.debug(f"Streaming decision: {'yes' if use_streaming else 'no'} ({token_count} tokens)")
        return use_streaming
    
    def clear_cache(self) -> None:
        """Clear the LRU cache for token counting."""
        self.count_tokens.cache_clear()
        self.logger.debug("Token counting cache cleared")
    
    def get_cache_info(self) -> Dict[str, int]:
        """Get LRU cache statistics."""
        cache_info = self.count_tokens.cache_info()
        return {
            "hits": cache_info.hits,
            "misses": cache_info.misses,
            "maxsize": cache_info.maxsize,
            "currsize": cache_info.currsize,
            "hit_rate": cache_info.hits / (cache_info.hits + cache_info.misses) if (cache_info.hits + cache_info.misses) > 0 else 0.0
        }

# Global token manager instance
_token_manager: Optional[TokenManager] = None

def get_token_manager() -> TokenManager:
    """Get global token manager instance."""
    global _token_manager
    if _token_manager is None:
        _token_manager = TokenManager()
    return _token_manager

# NO backward compatibility functions - force migration
__all__ = [
    'TokenProvider',
    'TokenManager', 
    'get_token_manager',
]
