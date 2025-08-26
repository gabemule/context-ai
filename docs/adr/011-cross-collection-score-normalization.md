# ADR-011: Cross-Collection Query with Score Normalization

**Status:** Accepted  

## Context

context-ai supports querying multiple indexed projects (collections) simultaneously. ChromaDB returns raw distance values per collection, but these distances have **incompatible scales** — a score of 0.3 from collection A is not comparable to 0.3 from collection B. Without normalization, cross-collection ranking is unfair.

## Decision

Implement **min-max normalization per collection** in `ResultMerger` (`src/core/query/result_merger.py`):

1. Query each collection independently via ChromaDB
2. For each collection, normalize raw distances to 0-1 range using min-max within that collection
3. Convert distances to similarity scores (`1 - normalized_distance`)
4. Merge all normalized results into a single ranked list
5. Sort by normalized similarity score descending

All results use `normalized_score` (0-1) for display and ranking, never raw ChromaDB distances.

## Consequences

- **Positive:** Fair ranking across collections — results from different projects are directly comparable.
- **Positive:** User sees consistent 0-1 similarity scores regardless of collection characteristics.
- **Positive:** Enables "cross-project intelligence" — the core value proposition of context-ai.
- **Negative:** Min-max normalization within a collection can be misleading when a collection has few results (single result always gets score 1.0).
- **Negative:** Known bug with multi-query expansion — normalized scores can compound incorrectly (tracked in `@todo/SCORING-ALGORITHM/`).
- **Future:** Consider weighted scoring with additional signals (recency, file type, edit frequency).
