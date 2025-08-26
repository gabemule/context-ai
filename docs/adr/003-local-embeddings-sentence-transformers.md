# ADR-003: Local Embeddings with sentence-transformers

**Status:** Accepted  

## Context

Code chunks need to be converted to vector embeddings for semantic search. Two approaches: cloud API (OpenAI Embeddings, Cohere) or local model (sentence-transformers, fastembed).

## Decision

Use **sentence-transformers** to run embedding models locally on the user's hardware. The model is managed by `ModelManager` singleton (`src/core/embeddings/model_manager.py`).

**Rejected alternatives:**
- OpenAI Embeddings API — adds cost per query, requires internet, sends code to third-party
- Cohere Embed — same concerns as OpenAI
- fastembed — lighter but less mature ecosystem

## Consequences

- **Positive:** Zero cost per query — embeddings are free after initial model download.
- **Positive:** Full privacy — code never leaves the user's machine.
- **Positive:** Works offline after first model download.
- **Negative:** Requires ~500MB-1GB disk for model files.
- **Negative:** First load is slow (~3-5s) on machines without GPU.
- **Negative:** Embedding quality may be lower than OpenAI's latest models for code-specific tasks.
- **Future:** Provider abstraction (ADR-006) allows adding cloud embedding providers without changing core logic.
