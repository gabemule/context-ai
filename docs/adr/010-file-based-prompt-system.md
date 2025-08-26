# ADR-010: File-based Prompt System (Markdown + YAML)

**Status:** Accepted  

## Context

AI prompts need to be configurable, versionable, and extensible without code changes. Options: hardcoded template strings in Python, Jinja2 templates, or file-based loading from Markdown/YAML.

## Decision

Load prompts from **Markdown files** (prose content) and **YAML files** (mode configuration) in `config/samples/prompts/`. Four prompt modes supported:

```
prompts/
├── global_instructions.md      # Shared across all modes
├── security_instructions.md    # Optional security layer
├── minimal/
│   ├── mode.yaml               # Features, metadata
│   └── core_instructions.md    # Mode-specific prompt
├── standard/
│   ├── mode.yaml
│   ├── core_instructions.md
│   └── cross_analysis.md       # Cross-project analysis instructions
├── comprehensive/              # All features enabled
└── strict/                     # Maximum rigor
```

`PromptBuilder` (`src/core/ai/prompt_builder.py`) assembles the final prompt by loading and concatenating files based on the active mode's `mode.yaml` feature flags.

## Consequences

- **Positive:** Non-developers can edit prompts without touching Python code.
- **Positive:** Modes are composable — each mode enables/disables features via YAML flags.
- **Positive:** Easy A/B testing — duplicate a mode folder, tweak, compare results.
- **Positive:** Language-specific coding guidelines also loaded from Markdown (`config/samples/guidelines/`).
- **Negative:** `PromptBuilder` is 910 lines — the file-loading + assembly logic is complex (god module, tracked in SPLIT-PROMPT-BUILDER).
- **Negative:** No validation that prompt files are syntactically correct or complete.
