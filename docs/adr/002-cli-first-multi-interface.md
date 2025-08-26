# ADR-002: CLI-first, Multi-interface Architecture

**Status:** Accepted  

## Context

context-ai needs a primary user interface. Options considered: web UI, VS Code extension only, CLI, or REST API. The tool targets developers who work in terminals and IDEs.

## Decision

Adopt a **CLI-first** architecture using `argparse` + `Rich` for terminal UI. The architecture supports multiple delivery mechanisms:

- **Primary:** CLI (`src/commands/`) — 7 commands (generate, select, query, ask, chat, config, storage)
- **Secondary:** VS Code extension (`context-ai-vscode/`) — communicates via env var `CONTEXT_AI_VSCODE`
- **Planned:** FastAPI REST API (`src/api/`) — will expose `services/` layer as HTTP endpoints

All interfaces share the same `services/` → `core/` layers. No business logic in delivery layers.

## Consequences

- **Positive:** CLI is universally accessible, scriptable, and CI-friendly.
- **Positive:** Clean Architecture enables adding FastAPI without duplicating logic.
- **Positive:** VS Code extension can either call CLI subprocess or future API.
- **Negative:** CLI has limited interactivity compared to web UI.
- **Action required:** When FastAPI is added, singletons must be replaced with DI (see ADR-005) to handle concurrent requests safely.
