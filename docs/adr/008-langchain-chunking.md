# ADR-008: LangChain Text Splitters for Code Chunking

**Status:** Accepted — tree-sitter planned as future evolution  

## Context

Source code files must be split into semantically meaningful chunks before embedding. Options: naive splitting (by lines/characters), LangChain's `RecursiveCharacterTextSplitter` with language-aware separators, or AST-based splitting via tree-sitter.

## Decision

Use **LangChain's `RecursiveCharacterTextSplitter`** with configurable separators per language. Language-specific separator lists are defined in `config/samples/languages.yaml` and loaded by `LanguagesRegistry`.

Implementation: `src/core/chunking/langchain_adapter.py` implements `ChunkerProtocol`.

**Rejected alternatives:**
- Naive line/character splitting — loses semantic boundaries (splits mid-function)
- tree-sitter AST parsing — superior accuracy but significantly more complex (requires per-language grammar binaries, AST traversal logic, handling of edge cases)

## Consequences

- **Positive:** Plug-and-play — LangChain handles chunking out of the box with minimal code.
- **Positive:** Configurable per language via YAML — add new languages without code changes.
- **Positive:** Good enough for ~80% of code files — splits on function/class boundaries when separators match.
- **Negative:** Heuristic-based — doesn't understand code structure. Can split mid-function if separators don't match or chunk size is too small.
- **Negative:** No AST awareness — can't distinguish "important" code (public API) from "trivial" code (imports, boilerplate).
- **Future:** tree-sitter migration is planned (`@todo/FUTURE/PLAN.md`). When implemented, this ADR will be updated to reflect the new approach. The `ChunkerProtocol` abstraction (ADR-006) enables swapping implementations.
