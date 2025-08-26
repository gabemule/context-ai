# ADR-014: VS Code Extension — Monorepo During Development, Separate Repo for Publication

**Status:** Accepted  

## Context

context-ai has a companion VS Code extension that provides a chat sidebar. The extension needs to be developed, versioned, and deployed. Options: separate repository from day one, monorepo with shared tooling, or npm package.

## Decision

Keep the VS Code extension as a **sub-project in the same repository** at `context-ai-vscode/` **during early development only**. Before the extension is published to the VS Code Marketplace, it **must be moved to its own repository**.

```
context-ai/              # Python CLI (main project)
├── src/                 # Python source
├── pyproject.toml       # Python config
└── context-ai-vscode/   # TypeScript extension (sub-project)
    ├── src/             # TypeScript source
    ├── package.json     # Node config
    └── tsconfig.json    # TypeScript config
```

The extension communicates with the CLI via the environment variable `CONTEXT_AI_VSCODE=true`, which changes output formatting (JSON instead of Rich terminal UI).

## Rationale for Monorepo (Temporary)

During early development, the monorepo approach reduces friction: changes to CLI output format and extension parsing can be coordinated in a single PR. Once the extension is stable and has a defined API contract, it will be extracted.

## Migration Plan

Before publishing to VS Code Marketplace:
1. Create a dedicated repository (e.g., `context-ai-vscode`)
2. Move `context-ai-vscode/` contents to the new repo
3. Define a stable API contract (CLI stdout format or FastAPI endpoints)
4. Set up independent CI/CD for the extension
5. Remove `context-ai-vscode/` from this repo

## Consequences

- **Positive:** Single repo during dev — fast iteration, coordinated changes.
- **Positive:** Simple communication model via env var — no IPC protocol needed for now.
- **Negative:** Mixed tooling — Python and TypeScript in one repo (temporary).
- **Negative:** Extension is tightly coupled to CLI subprocess — no formal API contract yet.
- **Commitment:** The extension **will not be published** from the monorepo. Separate repo is a prerequisite for publication.
- **Future:** When FastAPI API layer is added (ADR-002), the extension can switch from CLI subprocess to HTTP calls, enabling richer communication.
