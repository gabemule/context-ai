# ADR-004: ChromaDB as Local Vector Store

**Status:** Accepted  

## Context

Embedded code chunks need persistent vector storage for semantic search. Options: cloud-hosted (Pinecone, Weaviate, Supabase pgvector) or local (ChromaDB, FAISS, LanceDB).

## Decision

Use **ChromaDB** with local persistent storage at `~/.context-ai/storage/`. Each indexed project gets its own ChromaDB collection.

**Rejected alternatives:**
- Pinecone — cloud-only, adds cost and latency, requires account
- FAISS — no built-in persistence, lower-level API, no metadata filtering
- Supabase pgvector — requires PostgreSQL setup, overkill for local use
- LanceDB — promising but less mature at time of decision

## Consequences

- **Positive:** Zero infrastructure — no database server, no cloud account, no cost.
- **Positive:** Data stays local — full privacy, works offline.
- **Positive:** Simple API — `collection.query()` with metadata filtering out of the box.
- **Positive:** Persistent storage — survives process restarts.
- **Negative:** No sharing between machines — each dev has their own local index.
- **Negative:** Doesn't scale to very large codebases (>100K files) as well as cloud solutions.
- **Future:** Provider abstraction (ADR-006) will support cloud vector DB providers (Supabase, Pinecone) for team/enterprise use cases.
