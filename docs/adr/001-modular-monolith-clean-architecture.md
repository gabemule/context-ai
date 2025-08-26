# ADR-001: Modular Monolith with Clean Architecture Layers

**Status:** Accepted  

## Context

context-ai is a CLI tool that integrates multiple subsystems: AI clients, embeddings, vector storage, chunking, query processing, and formatting. Without clear architectural boundaries, the codebase risks becoming a tangle of cross-cutting dependencies.

## Decision

Adopt a **Modular Monolith** with **Clean Architecture** layering:

```
commands/   → CLI handlers (argparse + Rich UI)
services/   → Business logic orchestration
core/       → Domain logic (AI, chunking, embeddings, formatting, query)
config/     → Configuration, constants, providers, languages
utils/      → Cross-cutting utilities (logging, errors, file ops)
```

**Dependency rule:** Each layer may only import from layers below it. `commands/` → `services/` → `core/` → `config/` + `utils/`. No upward imports.

## Consequences

- **Positive:** Clear separation of concerns. New delivery mechanisms (FastAPI, MCP server) can be added as peer layers to `commands/` without touching business logic.
- **Positive:** Easier to reason about, test, and refactor individual layers.
- **Negative:** Requires discipline — lazy imports in `config/` currently mask circular dependency violations.
- **Negative:** The `services/ai_service.py` (1141 lines) and `core/ai/prompt_builder.py` (910 lines) violate the spirit of modularity and need splitting.
