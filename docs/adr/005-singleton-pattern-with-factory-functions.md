# ADR-005: Singleton Pattern with Factory Functions

**Status:** Accepted with known limitations — will migrate to DI  

## Context

Multiple subsystems (config, storage, settings, languages, embeddings, token counting) need shared state across the application. Options: global singletons, dependency injection container, or app context object.

## Decision

Use **module-level singleton pattern** with `get_<thing>()` factory functions:

```python
_token_manager: Optional[TokenManager] = None

def get_token_manager() -> TokenManager:
    global _token_manager
    if _token_manager is None:
        _token_manager = TokenManager()
    return _token_manager
```

**Current singletons:** `ConfigCore`, `SettingsManager`, `StorageManager`, `LanguagesRegistry`, `ModelManager`, `TokenManager`.

## Known Limitations

1. **Not testable** — no `reset_*()` functions; tests cannot isolate state between runs.
2. **Implicit global state** — any module can access any singleton without explicit dependency declaration.
3. **Initialization order** — subtle bugs if singletons initialize in wrong order.
4. **Not concurrency-safe** — when FastAPI is added (ADR-002), concurrent requests will share mutable state (race conditions).
5. **Circular deps** — masked by lazy imports in `config/` layer rather than properly resolved.

## Planned Migration

When FastAPI is added, migrate to **Dependency Injection** (tracked in `@todo/DI-REFACTOR/`):
- Replace global singletons with an app context / DI container
- Each request gets its own scoped dependencies
- Explicit wiring makes dependencies visible and testable

## Why Not DI Now

For a CLI-only tool with zero test coverage, singletons are the simplest thing that works. DI adds boilerplate that isn't justified until either tests or FastAPI arrive.
