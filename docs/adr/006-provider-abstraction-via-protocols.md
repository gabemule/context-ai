# ADR-006: Provider Abstraction via Python Protocols

**Status:** Accepted  

## Context

context-ai currently uses Claude as its AI provider, ChromaDB as its vector store, and LangChain for chunking. The system needs to support future providers (OpenAI, Ollama, Supabase, tree-sitter) without rewriting core logic.

## Decision

Use **Python `typing.Protocol`** for structural subtyping to define provider interfaces:

- `AIClientInterface` — abstract base class for AI providers (Claude, future OpenAI/Ollama)
- `ChunkerProtocol` — protocol for text chunking strategies (LangChain, future tree-sitter)
- `ProviderProtocol` — protocol for AI provider configuration
- `ConfigManagerProtocol` — protocol for configuration management
- `PathProvider` — protocol for storage path resolution

Concrete implementations are registered via factory/registry patterns (`AIClientFactory`, `get_provider_registry()`).

## Consequences

- **Positive:** Adding a new AI provider = implementing one interface + registering it. Zero changes to services/core.
- **Positive:** Enables future cloud vector DB providers alongside local ChromaDB.
- **Positive:** Structural subtyping (Protocol) doesn't require inheritance — cleaner than ABC for simple interfaces.
- **Negative:** Only Claude is implemented today. Abstractions are validated by one provider only.
- **Negative:** Provider registry adds indirection that can be confusing for new contributors.
