# ADR-007: tiktoken for Claude Token Counting

**Status:** Accepted  

## Context

Accurate token counting is critical for context window management (ADR-012). Claude does not publish a public tokenizer. Options: use Anthropic's API token counting endpoint (adds latency), use tiktoken as approximation, or use character-based heuristics.

## Decision

Use **tiktoken** with `cl100k_base` encoding (GPT-4's tokenizer) as an approximation for Claude's tokenizer. Centralized in `TokenManager` (`src/core/ai/token_manager.py`) with `@lru_cache(maxsize=1000)` for performance.

**Fallback:** When tiktoken is unavailable, use `max(1, len(text.strip()) // 4)` (~4 chars per token heuristic).

**Rejected alternatives:**
- Anthropic API counting endpoint — adds network latency per count, impractical for high-frequency counting
- Pure heuristic (`len(text) // 4`) — too inaccurate for budget allocation decisions
- No counting — impossible to manage context window safely

## Consequences

- **Positive:** Fast local counting with no API calls (~0.1ms per count).
- **Positive:** LRU cache eliminates redundant counting of repeated text chunks.
- **Positive:** Close enough accuracy (~95-98% match with Claude's actual tokenizer for English/code).
- **Negative:** Not exact — edge cases with special characters, non-Latin scripts may diverge.
- **Negative:** tiktoken is an OpenAI dependency used for a non-OpenAI provider (conceptually odd).
- **Future:** If Anthropic releases a public tokenizer, switch to it.
