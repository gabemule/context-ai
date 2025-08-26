# ADR-013: Lazy Import Strategy for Startup Performance

**Status:** Accepted  

## Context

context-ai depends on heavy libraries: `tiktoken` (~50ms), `chromadb` (~500ms), `sentence-transformers` (~2s), `anthropic` (~100ms). Importing all at module load time makes CLI startup slow (~5s), even for simple commands like `context-ai config show` that don't need AI or embeddings.

## Decision

Use **lazy imports** — heavy dependencies are imported inside functions/methods at first use, not at module level:

```python
# Instead of top-level:
# import tiktoken

# Import at point of use:
def _load_encoder(self):
    import tiktoken
    self._encoder = tiktoken.get_encoding("cl100k_base")
```

Applied to: tiktoken, chromadb, sentence-transformers, anthropic, langchain.

## Consequences

- **Positive:** CLI startup reduced from ~5s to ~1s for lightweight commands.
- **Positive:** Commands that don't need AI/embeddings never pay the import cost.
- **Negative:** Masks circular dependency violations — imports that would fail at module level succeed because lazy import runs after all modules are loaded.
- **Negative:** First use of a heavy feature has a cold-start penalty (~2-3s for embeddings).
- **Negative:** Makes it harder to see all dependencies at a glance (not visible in top-of-file imports).
- **Action required:** When circular deps are resolved (tracked in `@todo/CONFIG-REFACTOR/`), some lazy imports can be promoted to top-level.
