"""
AI Provider configurations for Context-AI.

Defines models, capabilities, and configurations for different AI providers.
"""

# AI Provider Models - First item in each dict is the default
CLAUDE_MODELS = {
    # DEFAULT: Claude 4 Sonnet - High-performance reasoning
    "claude-sonnet-4": {
        "api_name": "claude-sonnet-4-20250514",
        "max_output_tokens": 64000,
        "speed": "fast",
        "description": "High-performance with exceptional reasoning",
        "context_window": 200000,
        "pricing_input": 3.0,
        "pricing_output": 15.0,
    },
    
    # Claude 3.5 models (2024) - Fast and reliable
    "claude-3-5-haiku": {
        "api_name": "claude-3-5-haiku-20241022",
        "max_output_tokens": 8192,
        "speed": "fastest",
        "description": "Blazing fast responses",
        "context_window": 200000,
        "pricing_input": 0.8,
        "pricing_output": 4.0,
    },
    "claude-3-5-sonnet": {
        "api_name": "claude-3-5-sonnet-20241022", 
        "max_output_tokens": 8192,
        "speed": "fast",
        "description": "Intelligent and capable",
        "context_window": 200000,
        "pricing_input": 3.0,
        "pricing_output": 15.0,
    },
    
    # Claude 3.7 models (2025) - Extended capabilities
    "claude-3-7-sonnet": {
        "api_name": "claude-3-7-sonnet-20250219",
        "max_output_tokens": 64000,
        "speed": "fast",
        "description": "Fast with extended thinking capability",
        "context_window": 200000,
        "pricing_input": 3.0,
        "pricing_output": 15.0,
    },
    
    # Claude 4 Opus - Most capable
    "claude-opus-4": {
        "api_name": "claude-opus-4-20250514",
        "max_output_tokens": 32000,
        "speed": "moderately_fast", 
        "description": "Most capable, highest intelligence",
        "context_window": 200000,
        "pricing_input": 15.0,  # $/MTok
        "pricing_output": 75.0,  # $/MTok
    },
}

# Future providers (examples)
# OPENAI_MODELS = {
#     "gpt-4o": {
#         "api_name": "gpt-4o-2024-08-06",
#         "max_output_tokens": 16384,
#         "speed": "fast",
#         "description": "Most capable GPT-4 model",
#         "context_window": 128000,
#         "pricing_input": 2.5,
#         "pricing_output": 10.0,
#     },
#     "gpt-4": {
#         "api_name": "gpt-4-turbo-2024-04-09", 
#         "max_output_tokens": 4096,
#         "speed": "moderate",
#         "description": "Advanced reasoning and analysis",
#         "context_window": 128000,
#         "pricing_input": 10.0,
#         "pricing_output": 30.0,
#     },
# }

# Smart default selection - automatically picks first model from active provider
ALL_PROVIDERS = {
    "claude": CLAUDE_MODELS,
    # "openai": OPENAI_MODELS,  # Future - move to first position to make it default
}

def get_first_item(obj: dict) -> str:
    """Get the first key from any dictionary."""
    return next(iter(obj)) if obj else ""

# Dynamic defaults - always use first items
DEFAULT_AI_PROVIDER = get_first_item(ALL_PROVIDERS)
DEFAULT_MODEL = get_first_item(ALL_PROVIDERS[DEFAULT_AI_PROVIDER])

# Model configuration functions
def get_model_config(model_key: str, provider: str = None) -> dict:
    """Get configuration for a specific model."""
    provider = provider or DEFAULT_AI_PROVIDER
    
    if provider == "claude" and model_key in CLAUDE_MODELS:
        return CLAUDE_MODELS[model_key]
    # Future: elif provider == "openai" and model_key in OPENAI_MODELS:
    #     return OPENAI_MODELS[model_key]
    return {}

def get_current_model_config() -> dict:
    """Get config for currently selected default model."""
    return get_model_config(DEFAULT_MODEL, DEFAULT_AI_PROVIDER)

# Dynamic constants based on selected model
def get_max_tokens() -> int:
    """Get context window size for current model."""
    return get_current_model_config().get("context_window", 200000)

def get_max_output_tokens() -> int:
    """Get max output tokens for current model."""
    return get_current_model_config().get("max_output_tokens", 12000)

def get_api_name() -> str:
    """Get API name for current model."""
    return get_current_model_config().get("api_name", DEFAULT_MODEL)

def get_available_models(provider: str = None) -> list[str]:
    """Get available models for a provider."""
    provider = provider or DEFAULT_AI_PROVIDER
    return list(ALL_PROVIDERS.get(provider, {}).keys())

def get_available_providers() -> list[str]:
    """Get list of available AI providers."""
    return list(ALL_PROVIDERS.keys())
