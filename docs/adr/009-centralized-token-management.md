# ADR-009: Centralized Token Management

**Status:** Accepted (implemented)  

## Context

The codebase had 3-4 independent token counting implementations with different algorithms:

1. `context_formatter.py` — tiktoken + unbounded `_token_cache` dict
2. `prompt_builder.py` — inline `len(text.split()) + len(text) // 4` (word-based)
3. `langchain_adapter.py` — `len(text) // 4` (char-based estimation)
4. `ai_service.py` — `TokenCalculator` class with budget logic (not counting per se)

These gave **inconsistent results** for the same input. The unbounded cache was also a memory leak.

## Decision

Consolidate all token counting into a single **`TokenManager`** at `src/core/ai/token_manager.py`:

- `count_tokens(text)` — tiktoken-based, cached with `@lru_cache(maxsize=1000)`
- `calculate_context_allocation()` — migrated from `TokenCalculator`
- `calculate_response_tokens()` — migrated from `TokenCalculator`
- `should_use_streaming()` — streaming decision based on token count
- `get_token_manager()` — singleton factory

All call sites migrated to `get_token_manager().count_tokens()`. All old implementations removed.

## Consequences

- **Positive:** Single source of truth for token counting — consistent results everywhere.
- **Positive:** LRU cache fixes the unbounded memory growth (`_token_cache` dict).
- **Positive:** Budget allocation logic co-located with counting logic (cohesion).
- **Positive:** Provider-aware via `TokenProvider` enum — extensible for future providers.
- **Negative:** `lru_cache` on a method requires the instance to be hashable (works because singleton).
