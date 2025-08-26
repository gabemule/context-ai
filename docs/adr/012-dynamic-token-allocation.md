# ADR-012: Dynamic Token Allocation Strategy

**Status:** Accepted — planned improvement to greedy fill  

## Context

Claude's 200K context window must be divided between code context, chat history, and response space. The allocation strategy directly impacts response quality.

## Decision

Use a **fixed-ratio allocation** with dynamic sub-allocation:

```
Total: 200,000 tokens (CLAUDE_MAX_TOKENS)
├── Context: 65% (130K) — CONTEXT_TOKEN_RATIO
│   ├── Code context: 70% of context (~91K)
│   └── Chat history: 30% of context (~39K) — CHAT_HISTORY_TOKEN_RATIO
└── Response: 35% (70K) — dynamic within bounds
    ├── Min: 4,000 tokens — MIN_RESPONSE_TOKENS
    └── Max: 12,000 tokens — MAX_RESPONSE_TOKENS
```

Chat history uses intelligent truncation: always preserves last 3 turns, adds older turns backwards while budget allows.

## Market Comparison

| Tool | Strategy | How it works |
|---|---|---|
| **Cursor** | Dynamic priority-based | ~60% context, adjusted by file relevance. No fixed ratio. |
| **Continue.dev** | Greedy fill | Fills with most relevant chunks until budget hit. |
| **Aider** | Map + Full | File summaries first, then full files as budget permits. |
| **Cody (Sourcegraph)** | Multi-signal greedy | BM25 + embeddings + recency, greedy fill. |
| **context-ai (us)** | Fixed 65/35 split | Predictable but less adaptive. |

## Consequences

- **Positive:** Predictable — developers know exactly how much space is available.
- **Positive:** Simple to implement and debug.
- **Positive:** Chat history management works well for typical sessions (5-10 turns).
- **Negative:** Fixed ratio wastes space — simple queries get same allocation as complex ones.
- **Negative:** Less adaptive than greedy-fill approaches used by Cursor, Aider, and Cody.
- **Negative:** Response cap at 12K may truncate long code generation tasks.
- **Planned improvement:** Migrate to greedy fill with minimum response reservation (tracked in `@todo/DYNAMIC-TOKEN-ALLOCATION/`). Key changes: fill context by relevance score, reserve minimum 4K-8K for response, no fixed percentage split.
