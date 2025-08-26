# Context-AI — Complete Project Context

> Auto-generated deep-dive analysis based on codebase inspection.

---

## 1. Identity & Purpose

- **What is this project?** Context-AI is a cross-project code intelligence CLI assistant that generates vector embeddings from codebases and uses them as context for AI-powered question answering via Anthropic Claude. It reads source files, chunks them intelligently by language, stores them in a local vector database (ChromaDB), and retrieves the most relevant snippets to answer developer questions about their code.

- **Problem it solves:** Developers need context-aware answers about their codebases without manually searching through files. Context-AI bridges the gap between LLMs and local codebases by providing semantic search over embedded code, enabling AI responses grounded in actual project code.

- **Target users/consumers:** Software developers who want AI assistance understanding, navigating, and working with their codebases. Both CLI users and (in progress) VS Code extension users.

- **Business domain:** Developer tooling / AI-assisted code intelligence.

- **Project maturity:** **Early Alpha (MVP)**. Evidence:
  - Package version `0.1.0a6` (`pyproject.toml` line 7)
  - PyPI name is `context-ai-alpha` (`pyproject.toml` line 6)
  - 8 actionable TODOs in source code
  - `tests/` directory exists but is empty — no test implementations
  - VS Code extension in early stage (`context-ai-vscode/TODO.md` has refactoring plan)
  - No CI/CD pipeline present
  - No Dockerfile or deployment configuration

- **README accuracy:** The README is generally accurate and well-maintained. It correctly lists all 7 commands (generate, select, query, ask, chat, config, storage), documents prompt modes, and describes the tech stack. Minor discrepancy: README mentions `pip install context-ai` but the PyPI package name is `context-ai-alpha`.

---

## 2. Stack & Infrastructure

### 2.1 Core Technologies

| Language | Version Constraint | Where Used |
|---|---|---|
| Python | >=3.9, <3.13 | Main CLI application (`src/`) |
| TypeScript | ES2021 target | VS Code extension (`context-ai-vscode/src/`) |
| JavaScript | N/A | VS Code webview (`context-ai-vscode/media/`) |
| CSS | N/A | VS Code webview styling (`context-ai-vscode/media/chat.css`) |
| YAML | N/A | Configuration files (`src/config/samples/`) |
| Markdown | N/A | Prompt templates, guidelines, docs |

- **Frameworks & runtimes:**
  - Python CLI with `argparse` (no web framework)
  - VS Code Extension API (`@types/vscode ^1.96.0`)
  - Anthropic SDK for Claude API integration
  - sentence-transformers for local embedding model
  - ChromaDB for vector storage
  - LangChain (text-splitters only) for code chunking
  - Rich for terminal UI

- **Package manager(s):**
  - Python: `pip` with `pyproject.toml` (setuptools backend). No lock file present (no `requirements.lock` or `pip.lock`).
  - Node.js: `npm` with `package-lock.json` present (`context-ai-vscode/`).

### 2.2 Build & Tooling

- **Build system/bundler:**
  - Python: `setuptools` via `pyproject.toml` with `build` package for distribution
  - VS Code extension: `vite` (`context-ai-vscode/vite.config.js`) with `rollup` for bundling

- **Transpilation/compilation:**
  - TypeScript → JavaScript via `tsc` (`context-ai-vscode/tsconfig.json`, target ES2021, module Node16)
  - Vite bundles the extension entry point

- **Linting & formatting:**
  - `flake8` — Python linter (configured in `Makefile`)
  - `black` — Python formatter
  - `isort` — Import sorting
  - `autoflake` — Remove unused imports
  - `mypy` — Static type checking
  - No ESLint/Prettier config found for the VS Code extension

- **Code generation:** None. No protobuf, GraphQL codegen, Prisma, or OpenAPI generation.

### 2.3 Infrastructure & Deployment

- **Containerization:** None. No Dockerfile or docker-compose found.
- **CI/CD:** None. No GitHub Actions, GitLab CI, or any pipeline configuration files.
- **Hosting/deployment targets:** PyPI (publishing via `twine` — see `Makefile` targets `publish` and `publish-test`). The VS Code extension has no publishing config yet.
- **Infrastructure as Code:** None.
- **Environment management:** Environment variable `ANTHROPIC_API_KEY` required for AI features. `CONTEXT_AI_VSCODE=true` env var used for VS Code integration detection (`src/services/ai_service.py` line 24). No `.env.example` file present.

### 2.4 Data Stores

- **Databases:**
  - ChromaDB (vector database) — local persistent storage at `~/.context-ai/storage/<name>/chroma/` (`src/config/constants/storage.py`)
  - Backed by SQLite internally (ChromaDB's default)
  - Accessed via `src/core/embeddings/vector_store.py`

- **Caching:**
  - In-memory token counting cache (`src/core/formatting/context_formatter.py` — `_token_cache` dict)
  - In-memory config caching in `ConfigCore` (`src/config/core.py` — `_cache` dict with `_cache_dirty` flag)
  - Embedding model cached as singleton (`src/core/embeddings/model_manager.py` — `_model_instance`)

- **File storage:**
  - Local filesystem at `~/.context-ai/` for all data
  - `config.json` for configuration
  - `languages.yaml` for language settings
  - `guidelines/` for coding guidelines per language
  - `prompts/` for prompt mode templates
  - `storage/` for embedding collections

- **Message brokers / queues:** None.
- **Search engines:** ChromaDB's built-in similarity search (cosine distance).

### 2.5 Observability

- **Logging:**
  - Custom logger module (`src/utils/logging.py`)
  - Uses Python's `logging` stdlib
  - Two handlers: file handler (DEBUG level → `~/.context-ai/context-ai.log`) and console handler (WARNING level by default, configurable)
  - Structured format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
  - Per-module loggers via `get_logger(name)` factory

- **Monitoring:** None.
- **Error tracking:** None (no Sentry, Bugsnag, etc.).
- **Tracing:** None.

---

## 3. Architecture & Structure

### 3.1 Architectural Pattern

- **Primary pattern:** **Modular Monolith with Clean Architecture layers** — a single Python package with clear separation into commands (CLI interface), services (business logic orchestration), core (domain logic and adapters), config (configuration management), and utils (cross-cutting concerns).

- **Evidence:**
  - Commands layer depends on services, never on core directly for business logic
  - Services orchestrate core components (AI clients, embeddings, formatters)
  - Core has no upward dependencies to commands or services
  - Config module uses centralized `ConfigCore` to eliminate circular dependencies (`src/config/core.py` docstring)
  - Protocol/interface pattern used for extensibility (`src/core/chunking/protocol.py`, `src/core/ai/ai_client_interface.py`, `src/config/providers/protocols.py`)

- **Layers identified:**

| Layer | Directory | Responsibility |
|---|---|---|
| CLI Interface | `src/commands/`, `src/cli.py` | Parse args, invoke services, display output |
| Services | `src/services/` | Business logic orchestration, workflow coordination |
| Core | `src/core/` | Domain logic: AI clients, embeddings, chunking, formatting, query |
| Configuration | `src/config/` | Settings, providers, languages, storage management |
| Utilities | `src/utils/` | Cross-cutting: logging, errors, file ops, progress tracking |
| VS Code Extension | `context-ai-vscode/` | Separate sub-project for IDE integration |

### 3.2 Directory Structure Map

```
src/
├── cli.py                     — Main CLI entry point, argparse setup, command routing
├── commands/                  — CLI command handlers (one file per command)
│   ├── ask.py                 — AI Q&A with context (single question)
│   ├── chat.py                — Interactive AI chat session
│   ├── config.py              — Configuration management (get/set/reset/show)
│   ├── generate.py            — Generate embeddings from codebase
│   ├── query.py               — Query embeddings for relevant context
│   ├── select.py              — Select active embeddings
│   └── storage.py             — Manage stored embeddings (list/delete/info/clean)
├── config/                    — Configuration system
│   ├── core.py                — Centralized config.json access (ConfigCore)
│   ├── settings.py            — User settings management (SettingsManager)
│   ├── setup.py               — First-run setup and defaults (SetupManager)
│   ├── storage.py             — Storage path management (StorageManager)
│   ├── models.py              — Pydantic config models
│   ├── interfaces.py          — Configuration protocols/interfaces
│   ├── embeddings.py          — Embedding-specific config (EmbeddingsManager)
│   ├── guidelines.py          — Coding guidelines management (GuidelinesManager)
│   ├── constants/             — System-wide constants (AI, chunking, storage, validation)
│   ├── languages/             — Language detection, config loading, registry
│   ├── providers/             — AI provider registry (Claude models, capabilities)
│   └── samples/               — Default config templates (prompts, guidelines, languages)
├── core/                      — Domain logic
│   ├── ai/                    — AI client interface, Claude client, prompt builder
│   ├── chunking/              — Code chunking (LangChain adapter, protocol)
│   ├── embeddings/            — Embedding model manager, ChromaDB vector store
│   ├── formatting/            — Context formatting for AI consumption
│   └── query/                 — Query preprocessing, result merging, dictionaries
├── services/                  — Business logic orchestration
│   ├── ai_service.py          — AI service (ask, chat, token calc, display, history)
│   └── embedding_service.py   — Embedding generation, query, selection services
└── utils/                     — Cross-cutting utilities
    ├── error_handler.py       — Error handling decorators and validators
    ├── exceptions.py          — Custom exception hierarchy
    ├── file_operations.py     — File system operations wrapper
    ├── ignore_patterns.py     — .gitignore-style pattern matching
    ├── logging.py             — Centralized logging setup
    ├── progress_tracker.py    — Rich progress bars
    ├── session_logger.py      — Session logging for debugging
    ├── version.py             — Version constant
    └── yaml_loader.py         — YAML file loading utility

context-ai-vscode/             — VS Code extension (separate sub-project)
├── src/
│   ├── extension.ts           — Extension entry point (activate/deactivate)
│   ├── chatViewProvider.ts    — Webview panel provider for chat UI
│   └── shared/logger.ts       — Extension logger
├── media/
│   ├── chat.css               — Chat UI styles
│   └── chat.js                — Chat UI JavaScript (webview)
└── src/webview/
    └── chat-entry.js          — Webview bundled entry point

docs/                          — Documentation
├── architecture/              — Architecture docs (context window, prompt modes, scoring)
├── commands/                  — Per-command documentation
└── deployment/                — PyPI publishing guide
```

### 3.3 Entry Points

- **Application entry point:** `src/cli.py` → `main()` function. Registered as `context-ai` console script in `pyproject.toml` (`[project.scripts]`). Calls `create_parser()` then dispatches to command handlers.

- **CLI entry points:** Each command in `src/commands/` has an `add_<cmd>_parser()` function (registers subcommand) and `execute_<cmd>_command()` function (handler). Commands: `generate`, `select`, `query`, `ask`, `chat`, `config`, `storage`.

- **API entry points:** N/A — this is a CLI application, not a web service.

- **Worker/job entry points:** N/A — no background workers or cron jobs.

- **Build entry points:**
  - `pyproject.toml` — Python package build config
  - `Makefile` — Development automation (setup, install, test, lint, format, build, publish)
  - `context-ai-vscode/vite.config.js` — VS Code extension build
  - `context-ai-vscode/setup.sh` — Extension development setup script

### 3.4 Request/Data Flow

**Typical "ask" flow (user asks a question about their codebase):**

1. User runs: `context-ai ask "How does auth work?"`
2. `src/cli.py` → `main()` parses args, dispatches to `execute_ask_command()`
3. `src/commands/ask.py` → `execute_ask_command()` creates `ServiceContainer` with `EmbeddingsManager`, `SettingsManager`, `QueryService`, `AIService`
4. `src/services/ai_service.py` → `AIService.ask_question()`:
   a. `ContextManager.get_context()` → calls `QueryService.query_embeddings()` to get relevant code
   b. `QueryService` uses `VectorStore` to search ChromaDB → returns ranked results
   c. Results formatted by `ContextFormatter` into AI-friendly format
   d. `APIManager.make_request()` → calls `ClaudeClient.ask()` with context + question
   e. Claude API returns response
   f. `DisplayManager` renders response with Rich panels, optionally copies to clipboard / saves to file
5. Exit code returned to CLI

**Typical "generate" flow (user creates embeddings):**

1. User runs: `context-ai generate my-project --path ./src`
2. `src/commands/generate.py` → validates name/path, creates `EmbeddingService`
3. `src/services/embedding_service.py` → `EmbeddingService.generate_embeddings()`:
   a. Scans files respecting `.gitignore` patterns (`IgnorePatternMatcher`)
   b. Detects language per file via `LanguagesRegistry`
   c. Chunks files using `LangChainChunker` (language-aware separators)
   d. Generates embeddings via `sentence-transformers` model (`ModelManager`)
   e. Stores vectors in ChromaDB via `VectorStore`
   f. Auto-selects new embedding if configured

### 3.5 Module/Package Dependency Graph

**Internal dependency flow (top → bottom = depends on):**

```
cli.py
  └── commands/*
        └── services/ai_service.py
        │     ├── core/ai/claude_client.py
        │     ├── core/formatting/context_formatter.py
        │     ├── services/embedding_service.py (lazy import)
        │     ├── config/settings.py
        │     └── utils/*
        └── services/embedding_service.py
              ├── core/embeddings/model_manager.py
              ├── core/embeddings/vector_store.py
              ├── core/chunking/langchain_adapter.py
              ├── core/formatting/context_formatter.py
              ├── core/query/preprocessor.py
              ├── core/query/result_merger.py
              ├── config/embeddings.py
              ├── config/storage.py
              ├── config/languages/registry.py
              └── utils/*
```

- **Circular dependencies:** None detected. The `ai_service.py` → `embedding_service.py` import is handled via `TYPE_CHECKING` lazy import to avoid potential cycles.

- **Most depended-upon modules (high afferent coupling):**
  - `src/utils/logging.py` — imported by nearly every module
  - `src/utils/exceptions.py` — imported by most modules
  - `src/config/constants/` — used across all layers
  - `src/config/core.py` — used by all config managers

- **Modules with most external dependencies (high efferent coupling):**
  - `src/services/ai_service.py` — depends on config, core/ai, core/formatting, services/embedding, utils (1141 lines, largest file)
  - `src/services/embedding_service.py` — depends on config, core/embeddings, core/chunking, core/formatting, core/query, utils (761 lines)
  - `src/core/ai/prompt_builder.py` — depends on config, utils, file system operations (910 lines)

### 3.6 Monorepo / Workspace Structure

This is **not a formal monorepo** but contains two independent sub-projects:

| Sub-project | Technology | Relationship |
|---|---|---|
| Root (`src/`) | Python CLI | Main application |
| `context-ai-vscode/` | TypeScript VS Code ext | Consumes CLI via `CONTEXT_AI_VSCODE` env var |

- No shared dependencies between them (different languages).
- The VS Code extension communicates with the Python CLI via process spawning (detected by `CONTEXT_AI_VSCODE` env var check in `src/services/ai_service.py` line 24).

---

## 4. Code Patterns & Conventions

### 4.1 Naming Conventions

| Element | Convention | Examples |
|---|---|---|
| Python files | `snake_case.py` | `ai_service.py`, `error_handler.py`, `vector_store.py` |
| Python classes | `PascalCase` | `AIService`, `ConfigCore`, `VectorStore`, `ClaudeClient` |
| Python functions | `snake_case` | `get_settings_manager()`, `execute_ask_command()` |
| Python constants | `SCREAMING_SNAKE_CASE` | `EXIT_ERROR`, `MAX_TOKENS`, `CLAUDE_MODELS` |
| Python private | `_prefix` | `_cache`, `_make_request_with_retry()`, `_build_prompt()` |
| TypeScript files | `camelCase.ts` | `chatViewProvider.ts`, `extension.ts` |
| TypeScript classes | `PascalCase` | `ChatViewProvider` |
| Config files | `snake_case` or `kebab-case` | `config.json`, `languages.yaml`, `context-ai-vscode/` |
| Commands | `snake_case` (internal), `kebab-case` (CLI) | `context-ai generate`, `context-ai ask` |
| Directories | `snake_case` | `error_handler/`, `query/`, `embeddings/` |

### 4.2 Design Patterns Identified

| Pattern | Where Used | Description |
|---|---|---|
| **Factory** | `src/core/ai/ai_client_interface.py` — `AIClientFactory` | Provider registry with `register_provider()` / `create_client()`. Claude auto-registers itself. |
| **Strategy** | `src/core/ai/prompt_builder.py` — `PromptBuilder` | Four prompt modes (minimal/standard/comprehensive/strict) loaded from YAML configs, each with different instruction sets. |
| **Adapter** | `src/core/chunking/langchain_adapter.py` — `LangChainChunker` | Adapts LangChain's `RecursiveCharacterTextSplitter` to the `ChunkerProtocol` interface. |
| **Protocol (Port)** | `src/core/chunking/protocol.py` — `ChunkerProtocol` | Python Protocol defining chunking interface for dependency inversion. |
| **Protocol (Port)** | `src/config/providers/protocols.py` — `ProviderProtocol` | Protocol for AI provider implementations. |
| **Protocol (Port)** | `src/config/interfaces.py` — `ConfigManagerProtocol` | Protocol for configuration managers. |
| **Singleton** | `src/core/embeddings/model_manager.py` — `get_model_manager()` | Global `_model_instance` ensures single embedding model loaded in memory. |
| **Singleton** | `src/config/core.py` — `get_config_core()` | Global `_instance` for centralized config access. |
| **Singleton** | `src/config/settings.py` — `get_settings_manager()` | Global `_instance` pattern. |
| **Singleton** | `src/config/storage.py` — `get_storage_manager()` | Global `_instance` pattern. |
| **Singleton** | `src/config/languages/registry.py` — `get_languages_registry()` | Global `_instance` pattern. |
| **Registry** | `src/config/providers/registry.py` — `ProviderRegistry` | Registers AI providers with capabilities, models, and factory functions. |
| **Registry** | `src/config/languages/registry.py` — `LanguagesRegistry` | Extension → language mapping, language config registry. |
| **Facade** | `src/services/ai_service.py` — `AIService` | Coordinates `TokenCalculator`, `ContextManager`, `DisplayManager`, `ChatHistoryManager`, `APIManager`, `ChatCommandHandler`. |
| **Chain of Responsibility** | `src/core/query/preprocessor.py` — `QueryPreprocessor` | Query goes through normalization → stop word removal → synonym expansion → keyword extraction pipeline. |
| **Builder** | `src/core/ai/prompt_builder.py` — `PromptBuilder` | Builds system prompts piece by piece: global instructions → security → mode-specific → guidelines → cross-analysis. |
| **Decorator** | `src/utils/error_handler.py` — `handle_command_errors` | Python decorator wrapping command handlers with consistent error handling. |
| **Observer / Pub-Sub** | N/A | Not found in the codebase. |
| **Repository** | `src/core/embeddings/vector_store.py` — `VectorStore` | Wraps ChromaDB collection with `add_documents()`, `query()`, `delete_collection()` etc. |
| **Context Manager** | `src/commands/generate.py` — `generation_context()` | Python context manager for embedding generation lifecycle. |
| **Dependency Injection** | Limited — via constructor params | Services receive dependencies through constructors (e.g., `AIService.__init__()` takes settings, query service). Not a full IoC container. |

### 4.3 Error Handling Strategy

- **Global error handler:** `handle_command_errors` decorator (`src/utils/error_handler.py`) wraps all command handlers. Catches `KeyboardInterrupt`, `ValidationError`, `ConfigurationError`, `StorageError`, `APIError`, and generic `Exception`.

- **Error types/classes:** Custom exception hierarchy in `src/utils/exceptions.py`:
  ```
  ContextAIError (base)
  ├── ConfigurationError — config file issues
  ├── StorageError — storage/embedding operations
  ├── ValidationError — input validation
  ├── APIError — AI provider API issues
  └── EmbeddingError — embedding generation/query
  ```

- **Error propagation pattern:** Exceptions are thrown from core/config layers, propagated through services, and caught at the command layer by the `handle_command_errors` decorator. Each error type maps to a specific exit code.

- **User-facing errors:** The decorator logs user-friendly emoji-prefixed messages (e.g., `❌ Configuration error: ...`) via the Rich console/logger.

- **Logging on error:** All caught exceptions are logged at appropriate levels — `ValidationError` at INFO, `ConfigurationError`/`StorageError` at ERROR with traceback via `logger.debug()`.

### 4.4 Logging Patterns

- **Logger setup:** Central logger factory in `src/utils/logging.py` via `get_logger(name)`. Each module gets its own named logger.

- **Log levels used:**
  - `DEBUG` — detailed execution flow, written to file only
  - `INFO` — user-facing operation status (via console when verbose)
  - `WARNING` — console output (default threshold)
  - `ERROR` — operation failures

- **Structured logging:** Semi-structured format `%(asctime)s - %(name)s - %(levelname)s - %(message)s`. Not JSON-formatted.

- **Sensitive data:** API keys are loaded from environment variables and not logged. No PII handling needed (local tool).

### 4.5 Code Style & Formatting

- **Linter config:** `flake8` (no `.flake8` config file found — uses defaults). `mypy` for type checking (no `mypy.ini` found).
- **Formatter:** `black` (no `pyproject.toml` [tool.black] section — uses defaults: 88 char line width, double quotes).
- **Import ordering:** `isort` for import sorting. `autoflake` removes unused imports.
- **File organization:** Modules typically follow: docstring → imports → constants → classes → factory functions → module-level registration.

### 4.6 Type System Usage

- **Strictness level:** Type hints used extensively throughout Python code. No `mypy` strict mode config found. Pydantic models used for configuration validation.

- **Type patterns:**
  - `typing.Protocol` for interfaces (`ChunkerProtocol`, `ProviderProtocol`, `ConfigManagerProtocol`)
  - `typing.NamedTuple` for lightweight value objects (`ServiceContainer`, `GenerateRequest`, `QueryRequest`)
  - `dataclasses.dataclass` for data containers (`ChatTurn`, `ClaudeResponse`, `AIResponse`, `QueryResult`)
  - Pydantic `BaseModel` for config models (`LanguageConfig`, `ProviderCapabilities`, etc.)
  - `TYPE_CHECKING` guard for lazy imports (`src/services/ai_service.py`)

- **Type-only imports:** Used via `TYPE_CHECKING` in `ai_service.py` for `QueryService`.

- **Runtime type validation:** Pydantic for configuration models (`src/config/models.py`, `src/config/languages/models.py`, `src/config/providers/models.py`). No Zod/Joi equivalent for CLI input — validation is manual in command handlers.

---

## 5. API Surface

### 5.1 External APIs Exposed

N/A — Context-AI is a CLI application. It does not expose HTTP, GraphQL, gRPC, or WebSocket APIs.

The **CLI interface** serves as the "API surface":

| Command | Purpose | Key Arguments |
|---|---|---|
| `context-ai generate <name> --path <dir>` | Generate embeddings from codebase | `name`, `--path`, `--chunk-size`, `--chunk-overlap` |
| `context-ai select [names...]` | Select active embeddings | `names` (optional, interactive if omitted) |
| `context-ai query <question>` | Search embeddings for relevant context | `question`, `--format`, `--top-k`, `--threshold` |
| `context-ai ask <question>` | AI-powered Q&A with context | `question`, `--format`, `--copy`, `--verbose`, `--mode` |
| `context-ai chat` | Interactive AI chat session | `--verbose`, `--mode` |
| `context-ai config <action>` | Configuration management | `show`, `get <key>`, `set <key> <value>`, `reset` |
| `context-ai storage <action>` | Embedding storage management | `list`, `info <name>`, `delete <name>`, `clean`, `optimize` |

### 5.2 Authentication & Authorization

- **Auth mechanism:** Anthropic API key via `ANTHROPIC_API_KEY` environment variable. Used by `ClaudeClient` for API calls (`src/core/ai/claude_client.py`).
- **Auth flow:** No user authentication — this is a local CLI tool. The API key is read from env vars at client initialization.
- **Authorization model:** N/A — single-user local tool.
- **Protected vs public routes:** N/A.

### 5.3 API Middleware / Pipeline

N/A — CLI application. However, there is a **decorator pipeline** for commands:

1. `handle_command_errors` decorator wraps every command handler
2. Command parser validation (argparse)
3. Manual validation in each command's `_validate_*_request()` functions
4. Service-level validation (e.g., checking embedding existence)

### 5.4 Real-time Communication

- **VS Code Extension:** The VS Code extension (`context-ai-vscode/`) uses VS Code's webview messaging protocol (`postMessage` / `onDidReceiveMessage`) for communication between the extension host and the chat webview panel. Defined in `context-ai-vscode/src/chatViewProvider.ts` and `context-ai-vscode/media/chat.js`.

- **Streaming:** Claude API responses support streaming via `_make_streaming_request()` in `src/core/ai/claude_client.py`. Streaming is auto-enabled when expected response exceeds a token threshold.

---

## 6. Data Layer

### 6.1 Data Models / Schema

**Core domain entities:**

| Entity | Location | Key Fields | Stored In |
|---|---|---|---|
| Embedding Collection | `VectorStore` (`src/core/embeddings/vector_store.py`) | name, documents, embeddings, metadatas, ids | ChromaDB |
| Document Chunk | Metadata in ChromaDB | source (file path), language, chunk_index, total_chunks | ChromaDB metadata |
| Query Result | `QueryResult` (`src/core/query/result_merger.py`) | content, source, score, metadata, language, file_path | In-memory |
| Chat Turn | `ChatTurn` (`src/services/ai_service.py`) | question, response, timestamp, context_used, tokens_used | In-memory (session only) |
| Claude Response | `ClaudeResponse` (`src/core/ai/claude_client.py`) | content, model, usage (input/output tokens), stop_reason | In-memory |
| Config | `config.json` | active_embeddings, settings, model, mode, verbose | JSON file |
| Language Config | `LanguageConfig` (`src/config/languages/models.py`) | name, extensions, separators, priority, guidelines, inherits | YAML file |

**Relationships:**
- An Embedding Collection contains many Document Chunks (1:N)
- A Query Result references a Document Chunk (source attribution)
- A Chat session contains many Chat Turns (1:N, in-memory)
- Config references active Embedding Collections by name (N:N via list)

### 6.2 Data Access Patterns

- **Vector store wrapper:** `VectorStore` class (`src/core/embeddings/vector_store.py`) wraps ChromaDB's `Collection` API with methods: `add_documents()`, `query()`, `get_collection_info()`, `delete_collection()`, `list_collections()`.

- **Repository pattern:** `VectorStore` acts as a repository for embeddings. `ConfigCore` acts as a repository for configuration.

- **Raw queries:** No raw SQL. ChromaDB is accessed via its Python SDK.

- **Query optimization:**
  - `ResultMerger` (`src/core/query/result_merger.py`) merges and deduplicates results across multiple collections using configurable scoring weights (distance, keyword overlap, recency).
  - `QueryPreprocessor` (`src/core/query/preprocessor.py`) normalizes queries, expands synonyms, extracts keywords for better retrieval.
  - Configurable `top_k` and `threshold` parameters for result filtering.

- **Connection management:** ChromaDB uses `PersistentClient` — one client per collection, no connection pooling needed for local storage.

### 6.3 Migrations & Seeds

- **Migration strategy:** N/A — no formal migration system. ChromaDB collections are created/deleted atomically.
- **Seed data:** Default configuration files are copied from `src/config/samples/` on first run by `SetupManager` (`src/config/setup.py`). Includes default prompt templates, language configs, and coding guidelines.
- **Schema versioning:** No explicit schema versioning. Config structure is defined by Pydantic models.

### 6.4 Data Validation

- **Validation layers:**
  - CLI input: argparse type checking + manual validation in command handlers (`_validate_*_request()` functions)
  - Configuration: Pydantic model validation (`src/config/models.py`, `src/config/languages/models.py`)
  - Embedding names: regex validation via `validate_embedding_name()` (`src/utils/error_handler.py`)
  - File paths: `validate_file_path()` (`src/utils/error_handler.py`)

- **Validation libraries:** Pydantic v2 for config models. Manual validation with regex for CLI inputs.

- **Validation constants:** Defined in `src/config/constants/validation.py` — `MAX_EMBEDDING_NAME_LENGTH`, `EMBEDDING_NAME_PATTERN`, `MAX_PATH_LENGTH`.

### 6.5 Caching Strategy

- **What's cached:**
  - Token counts: `_token_cache` dict in `src/core/formatting/context_formatter.py`
  - Config data: `ConfigCore._cache` with dirty flag (`src/config/core.py`)
  - Embedding model: singleton instance in `ModelManager` (`src/core/embeddings/model_manager.py`)
  - Query context: `ContextManager` caches last context in `_last_context` / `_last_context_summary` (`src/services/ai_service.py`)

- **Cache invalidation:**
  - Token cache: No invalidation (grows unbounded — potential memory concern for very long sessions)
  - Config cache: Invalidated via `_cache_dirty` flag on writes
  - Model cache: Never invalidated (lives for process lifetime)
  - Context cache: Overwritten on each new query

- **Cache layers:** In-memory only. No Redis, CDN, or external cache.

---

## 7. State Management

### 7.1 Client-Side State (VS Code Extension)

- **State library:** None — vanilla JavaScript state management in `context-ai-vscode/media/chat.js`.
- **Store structure:** DOM-based state. Messages stored as HTML in the chat container. No formal store.
- **State flow:** User types message → `postMessage` to extension host → host processes → `postMessage` back → DOM updated.
- **Persistence:** No state persistence. Chat history lost on panel close.

### 7.2 Server-Side State (Python CLI)

- **Session management:** Chat sessions are in-memory via `ChatHistoryManager` (`src/services/ai_service.py`). No persistence between CLI invocations.
- **In-memory state:**
  - `ChatHistoryManager._turns: List[ChatTurn]` — chat history
  - `ContextManager._last_context` — cached last query context
  - `ConfigCore._cache` — config cache
  - `ModelManager._model_instance` — embedding model
- **Implications for scaling:** Single-process CLI tool — scaling not applicable.

### 7.3 State Synchronization

N/A — single-user, single-process CLI application. No multi-instance state synchronization needed.

---

## 8. Configuration & Environment

### 8.1 Configuration Files Inventory

| File | Purpose |
|---|---|
| `pyproject.toml` | Python package config, dependencies, build settings, entry point |
| `Makefile` | Development automation scripts |
| `.gitignore` | Git ignore patterns |
| `~/.context-ai/config.json` | Runtime user configuration (created on first run) |
| `~/.context-ai/languages.yaml` | Language detection and chunking config |
| `~/.context-ai/guidelines/*.md` | Per-language coding guidelines |
| `~/.context-ai/prompts/**` | Prompt mode templates (minimal/standard/comprehensive/strict) |
| `src/config/constants/*.py` | Compile-time constants (AI, chunking, storage, validation) |
| `src/config/samples/` | Default templates copied on first run |
| `context-ai-vscode/package.json` | VS Code extension manifest and dependencies |
| `context-ai-vscode/tsconfig.json` | TypeScript compiler configuration |
| `context-ai-vscode/vite.config.js` | Vite bundler configuration for extension |

### 8.2 Environment Variables

| Variable | Description | Required | Default |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude | Yes (for AI commands) | None |
| `CONTEXT_AI_VSCODE` | Set to `"true"` when running from VS Code extension | No | Not set |

- **Defaults:** When `ANTHROPIC_API_KEY` is missing, commands that need AI (`ask`, `chat`) will fail with `ConfigurationError`.
- **Validation:** API key presence checked at `ClaudeClient` initialization.
- **Environment-specific overrides:** None — single-environment CLI tool.

### 8.3 Feature Flags

No formal feature flag system. The closest equivalent:
- `CONTEXT_AI_VSCODE` env var toggles VS Code-specific behavior (suppresses Rich output)
- `--verbose` CLI flag enables detailed output per command
- `--mode` flag selects prompt mode (minimal/standard/comprehensive/strict)

### 8.4 Secrets Management

- **Approach:** API key via environment variable (`ANTHROPIC_API_KEY`). No vault or secrets manager.
- **Rotation strategy:** Manual — user updates their env var.
- **Development secrets:** Developers set `ANTHROPIC_API_KEY` in their shell profile or `.env` file (not committed).

---

## 9. Testing

### 9.1 Test Infrastructure

- **Test runner:** `pytest` (listed as dev dependency in `pyproject.toml`)
- **Assertion library:** pytest's built-in `assert`
- **Mocking:** Not configured (no evidence of mock libraries in dependencies beyond pytest)
- **Test database:** Not configured

### 9.2 Test Structure & Coverage

- **Test file location:** `tests/` directory at project root
- **Naming convention:** Unknown — `tests/__init__.py` exists but is empty
- **Coverage metrics:** **0% — No tests implemented.** The `tests/` directory contains only an empty `__init__.py`.
- **Coverage gaps:** Everything. No unit, integration, or e2e tests exist.

### 9.3 Test Types Present

| Test Type | Present? | Details |
|---|---|---|
| Unit tests | ❌ No | — |
| Integration tests | ❌ No | — |
| End-to-end tests | ❌ No | — |
| Contract tests | ❌ No | — |
| Performance tests | ❌ No | — |
| Snapshot tests | ❌ No | — |

### 9.4 Test Patterns

N/A — no tests exist. The `Makefile` has `test` and `test-watch` targets that run `pytest`, but there's nothing to run.

---

## 10. Security

### 10.1 Authentication Implementation

- **API key flow:**
  1. User sets `ANTHROPIC_API_KEY` environment variable
  2. `ClaudeClient.__init__()` reads it via `os.getenv("ANTHROPIC_API_KEY")` or from config
  3. Passed to `anthropic.Anthropic(api_key=...)` client
  4. Used for all Claude API calls
  - File: `src/core/ai/claude_client.py`

- No user authentication (local tool).

### 10.2 Authorization Implementation

N/A — single-user local CLI tool. No roles, permissions, or access control.

### 10.3 Input Security

- **Input validation:** CLI arguments validated via argparse + manual validators. Embedding names validated with regex pattern (`src/utils/error_handler.py`).
- **SQL injection prevention:** N/A — no SQL database. ChromaDB accessed via SDK.
- **XSS prevention:** The VS Code extension webview uses `chat.js` which creates DOM elements — **UNCERTAIN:** whether user input is properly sanitized before insertion into the webview DOM.
- **CSRF protection:** N/A — no web server.
- **Path traversal:** File paths validated via `validate_file_path()` (`src/utils/error_handler.py`), but `pathspec` is used for gitignore-style filtering which inherently limits scope.

### 10.4 Security Headers & Configuration

N/A — no HTTP server. The VS Code extension webview uses VS Code's built-in CSP.

### 10.5 Sensitive Data Handling

- **PII storage:** None — tool processes code, not personal data.
- **Secrets in code:** No hardcoded secrets found. API key loaded from environment variable.
- **Logging safety:** API key is not logged. The prompt builder includes `security_instructions.md` that instructs AI to not reveal API keys or passwords found in code context.

---

## 11. Dependencies & Integrations

### 11.1 External Services Consumed

| Service | Purpose | Auth Method | Adapter Location |
|---|---|---|---|
| Anthropic Claude API | AI-powered code Q&A and chat | API Key (`ANTHROPIC_API_KEY`) | `src/core/ai/claude_client.py` |
| Hugging Face Hub | Download embedding models (sentence-transformers) | None (public models) | `src/core/embeddings/model_manager.py` (via sentence-transformers) |

### 11.2 Third-Party Libraries (Key Dependencies)

| Library | Purpose | Why This One |
|---|---|---|
| `anthropic` | Claude API client | Official Anthropic SDK |
| `sentence-transformers` | Local embedding model | Industry standard for semantic embeddings |
| `chromadb` | Vector database | Lightweight local vector DB, no server needed |
| `langchain-text-splitters` | Code-aware text chunking | Language-aware recursive splitting |
| `rich` | Terminal UI (panels, progress bars, markdown) | Best-in-class Python terminal formatting |
| `pydantic` | Configuration model validation | Type-safe data models |
| `tiktoken` | Token counting (OpenAI tokenizer) | Fast, accurate token estimation for Claude |
| `inquirer` | Interactive CLI prompts | User-friendly selection menus |
| `pathspec` | Gitignore-style pattern matching | Respects `.gitignore` during file scanning |
| `pyperclip` | Clipboard access | Cross-platform copy-to-clipboard |

### 11.3 Dependency Health

- **Outdated packages:** UNCERTAIN — no `pip audit` output available. The `pyproject.toml` pins no versions (uses `>=` constraints), which risks breaking changes.
- **Deprecated packages:** None known.
- **Security vulnerabilities:** UNCERTAIN — no `pip audit` or safety check evidence.
- **Lock file integrity:** **No Python lock file present.** This means builds are not reproducible — different installs could get different dependency versions. The VS Code extension has `package-lock.json` committed.

### 11.4 Internal Shared Code

- **Shared libraries:** `src/utils/` serves as a shared utility library used by all other modules.
- **Copy-paste patterns:** `src/services/embedding_service.py` contains a stub `AIService` class (lines 739-760) that appears to be a leftover/duplicate of the main `AIService` in `src/services/ai_service.py`.

---

## 12. Developer Experience

### 12.1 Onboarding

- **Setup steps (from README and Makefile):**
  1. Clone the repo
  2. Run `make setup` (creates venv, installs dependencies)
  3. Set `ANTHROPIC_API_KEY` environment variable
  4. Run `context-ai generate <name> --path <dir>` to create first embeddings
  5. Run `context-ai ask "your question"` to start querying

- **Setup friction:**
  - No `.env.example` file — developers must know about `ANTHROPIC_API_KEY`
  - Python version constraint (>=3.9, <3.13) may surprise some
  - First embedding model download can be slow (sentence-transformers model)
  - No Docker setup for isolated development

- **Prerequisites:**
  - Python 3.9-3.12
  - pip or pipx
  - Git
  - `ANTHROPIC_API_KEY`
  - Node.js/npm (only for VS Code extension development)

- **Setup automation:** `make setup` and `make install-dev` handle virtualenv creation and dependency installation. `context-ai-vscode/setup.sh` handles VS Code extension setup.

### 12.2 Available Scripts

**Makefile targets:**

| Script | Command | Purpose |
|---|---|---|
| `setup` | `make setup` | Create virtualenv and install dependencies |
| `install` | `make install` | Install package in production mode |
| `install-dev` | `make install-dev` | Install with dev dependencies |
| `clean` | `make clean` | Remove build artifacts, caches, venv |
| `test` | `make test` | Run pytest |
| `test-watch` | `make test-watch` | Run pytest in watch mode (ptw) |
| `lint` | `make lint` | Run flake8 + mypy |
| `format` | `make format` | Run autoflake + black + isort |
| `type-check` | `make type-check` | Run mypy |
| `build` | `make build` | Build distribution package |
| `publish` | `make publish` | Publish to PyPI |
| `publish-test` | `make publish-test` | Publish to Test PyPI |

### 12.3 Documentation

- **README quality:** Good. Covers installation, quick start, all commands, configuration, and tech stack. Could benefit from architecture diagrams.

- **Inline documentation:** Excellent. Every module has a top-level docstring. Classes and public methods have detailed docstrings. Constants are documented.

- **Architecture docs:**
  - `docs/architecture/context-window-management.md` — 200K token context window strategy
  - `docs/architecture/prompt-modes.md` — four prompt modes detailed
  - `docs/architecture/similarity-scoring.md` — scoring algorithm documentation
  - No ADRs (Architecture Decision Records)

- **API docs:** N/A (CLI, not an API). CLI usage documented in `docs/commands/` (one file per command).

- **Runbooks:** `docs/deployment/pypi-publishing.md` covers PyPI publishing process.

### 12.4 Git Workflow

- **Branching strategy:** UNCERTAIN — no branch protection rules or workflow docs found.
- **Commit conventions:** UNCERTAIN — no commit convention config (no commitlint, no `.commitlintrc`).
- **PR process:** No PR templates found.
- **Git hooks:** None configured (no `.husky/`, no `pre-commit-config.yaml`).
- **.gitignore coverage:** Adequate — covers `__pycache__/`, `*.pyc`, `venv/`, `dist/`, `.env`, `node_modules/`, etc.

---

## 13. Business Logic Deep-Dive

### 13.1 Core Domain Entities

**Embedding Collection**
- **Purpose:** A named set of code chunks + vectors from a project directory
- **Key properties:** name, path, chunk_size, chunk_overlap, document count
- **Relationships:** Contains many Document Chunks. Referenced by config's `active_embeddings` list.
- **Invariants:** Name must match `EMBEDDING_NAME_PATTERN` (alphanumeric + hyphens/underscores, max 64 chars). Path must exist and be a directory.
- **File:** `src/core/embeddings/vector_store.py`, `src/services/embedding_service.py`

**Document Chunk**
- **Purpose:** A piece of source code with metadata, stored as vector in ChromaDB
- **Key properties:** content (text), source (file path), language, chunk_index, total_chunks
- **Relationships:** Belongs to one Embedding Collection
- **Invariants:** Content must be non-empty. Source must be a valid file path.
- **File:** Created in `src/services/embedding_service.py`, metadata schema in ChromaDB

**Query Result**
- **Purpose:** A ranked result from similarity search
- **Key properties:** content, source, score (0-1), metadata, language, file_path
- **Relationships:** References a Document Chunk
- **File:** `src/core/query/result_merger.py`

**Chat Session**
- **Purpose:** An interactive conversation with AI using codebase context
- **Key properties:** turns (list of ChatTurn), model, mode
- **Relationships:** Each turn contains a question, response, context, and token count
- **Invariants:** History is truncated to fit within token budget (preserves last 3 turns always)
- **File:** `src/services/ai_service.py`

### 13.2 Business Workflows

**1. Embedding Generation**
- **Trigger:** `context-ai generate <name> --path <dir>`
- **Steps:**
  1. Validate name format and uniqueness
  2. Validate path exists
  3. Scan directory for source files (respecting `.gitignore` patterns via `IgnorePatternMatcher`)
  4. Detect language per file via `LanguagesRegistry` (extension mapping)
  5. Chunk each file using `LangChainChunker` with language-specific separators
  6. Load sentence-transformers model (lazy, cached singleton)
  7. Generate embeddings for all chunks
  8. Store in ChromaDB collection
  9. Auto-select new embedding if configured
- **Side effects:** Creates directory at `~/.context-ai/storage/<name>/chroma/`, updates `config.json`
- **Error scenarios:** Invalid name format, path not found, duplicate name, model download failure, disk space
- **Files:** `src/commands/generate.py`, `src/services/embedding_service.py`, `src/core/embeddings/*`, `src/core/chunking/*`

**2. Context Query**
- **Trigger:** `context-ai query <question>` or internally by ask/chat
- **Steps:**
  1. Load active embeddings from config
  2. Preprocess query: normalize → remove stop words → expand synonyms → extract keywords (`QueryPreprocessor`)
  3. For each active embedding: query ChromaDB with preprocessed query
  4. Merge results across collections (`ResultMerger`): deduplicate, score, rank
  5. Format results (`ContextFormatter`) into requested format (ai_friendly, plain, markdown, json, xml)
  6. Apply token limits
- **Side effects:** None (read-only)
- **Error scenarios:** No active embeddings, empty results, collection corrupted
- **Files:** `src/commands/query.py`, `src/services/embedding_service.py`, `src/core/query/*`, `src/core/formatting/*`

**3. AI-Powered Ask**
- **Trigger:** `context-ai ask <question>`
- **Steps:**
  1. Get context via Query workflow (above)
  2. Build system prompt via `PromptBuilder` (mode-specific)
  3. Send to Claude API via `ClaudeClient.ask()`
  4. Stream or standard response based on expected token count
  5. Display response via Rich panels
  6. Optionally copy to clipboard or save to file
- **Side effects:** API call to Anthropic, optional clipboard/file write
- **Error scenarios:** API key missing, API error, rate limit, context too large
- **Files:** `src/commands/ask.py`, `src/services/ai_service.py`, `src/core/ai/*`

**4. Interactive Chat**
- **Trigger:** `context-ai chat`
- **Steps:**
  1. Initialize chat session with `ChatHistoryManager`
  2. Enter REPL loop: read user input
  3. Check for slash commands (`/embeddings`, `/history`, `/clear`, `/verbose`, `/mode`)
  4. If regular message: get context → build prompt with history → send to Claude → display
  5. Manage token budget: truncate history if needed (always keep last 3 turns)
  6. Continue until `/exit` or Ctrl+C
- **Side effects:** API calls per turn
- **Error scenarios:** Same as Ask + session state corruption
- **Files:** `src/commands/chat.py`, `src/services/ai_service.py`

**5. Configuration Management**
- **Trigger:** `context-ai config <action>`
- **Steps:** CRUD operations on `~/.context-ai/config.json` via `ConfigCore`
- **Files:** `src/commands/config.py`, `src/config/core.py`, `src/config/settings.py`

### 13.3 Business Rules & Validations

| Rule | Where Enforced | File |
|---|---|---|
| Embedding name: alphanumeric + hyphens/underscores, max 64 chars | CLI validation | `src/utils/error_handler.py` |
| No duplicate embedding names | generate command | `src/commands/generate.py` |
| Path must exist and be a directory | generate command | `src/commands/generate.py` |
| Token budget: 65% context / 35% response | `TokenCalculator` | `src/services/ai_service.py` |
| Chat history: always preserve last 3 turns on truncation | `ChatHistoryManager` | `src/services/ai_service.py` |
| Chat history: 30% of context budget for history, 70% for code | Token allocation | `src/services/ai_service.py` |
| Auto-streaming when response >2K tokens expected | `ClaudeClient` | `src/core/ai/claude_client.py` |
| File filtering: respect `.gitignore` patterns | `IgnorePatternMatcher` | `src/utils/ignore_patterns.py` |
| Language detection: extension-based via `LanguagesRegistry` | Embedding generation | `src/config/languages/registry.py` |

### 13.4 State Machines

**Chat Session States:**
- **States:** `idle` → `awaiting_input` → `processing` → `displaying` → `awaiting_input` (or `exited`)
- **Transitions:**
  - `idle` → `awaiting_input`: chat session starts
  - `awaiting_input` → `processing`: user sends message
  - `awaiting_input` → `exited`: user types `/exit` or Ctrl+C
  - `processing` → `displaying`: AI response received
  - `displaying` → `awaiting_input`: response rendered
- **Guards:** API key must be valid, at least one embedding selected
- UNCERTAIN: This state machine is implicit in the chat loop code, not formally defined.

---

## 14. Performance & Scalability

### 14.1 Performance Patterns

- **Caching:** Token count cache, config cache, embedding model singleton (see Section 6.5).

- **Lazy loading:**
  - Embedding model loaded on first use, not at import (`ModelManager` singleton)
  - `QueryService` lazily imported in `ai_service.py` via `TYPE_CHECKING`
  - `sentence-transformers`, `chromadb`, and other heavy libraries imported at function level in several places

- **Database optimization:** ChromaDB's built-in HNSW index for approximate nearest neighbor search. Configurable `top_k` (default from `CONTEXT_DEFAULT_CHUNKS` constant).

- **Async processing:** None — all operations are synchronous. Claude API streaming is handled via synchronous iteration over the stream.

- **Connection pooling:** N/A — local ChromaDB, no external database connections to pool.

- **Pagination:** Results limited by `top_k` parameter. No cursor-based pagination.

### 14.2 Scalability Considerations

- **Stateless design:** N/A — local CLI tool, not a distributed service.
- **Database scaling:** ChromaDB is local-only. For very large codebases, performance depends on embedding model speed and ChromaDB's HNSW index.
- **Rate limiting:** Anthropic API has its own rate limits. No client-side rate limiting implemented.
- **CDN usage:** N/A.
- **Bottlenecks:**
  - Embedding generation is CPU-bound (sentence-transformers model inference). Could benefit from GPU support.
  - Large codebases (>10K files) will have slow embedding generation.
  - Token counting cache (`_token_cache`) grows unbounded — potential memory issue for very long chat sessions.
  - `ai_service.py` at 1141 lines is a maintenance bottleneck (god module risk).

---

## 15. Error Handling & Resilience

### 15.1 Error Architecture

- **Error class hierarchy:** (`src/utils/exceptions.py`)
  ```
  ContextAIError(Exception)
  ├── ConfigurationError
  ├── StorageError
  ├── ValidationError
  ├── APIError
  └── EmbeddingError
  ```

- **Error codes:** Exit codes defined in `src/config/constants/system.py`:
  - `EXIT_SUCCESS = 0`
  - `EXIT_ERROR = 1`
  - `EXIT_INTERRUPTED = 130`

- **Error serialization:** Errors are displayed as emoji-prefixed strings via Rich console. No structured error response format (CLI, not API).

### 15.2 Resilience Patterns

- **Retry logic:** `ClaudeClient._make_request_with_retry()` implements retry logic for API calls (`src/core/ai/claude_client.py`). UNCERTAIN: specific retry strategy (exponential backoff vs fixed) — the subagent summary mentions retry but details were truncated.

- **Circuit breaker:** Not implemented.

- **Timeout configuration:** UNCERTAIN — likely relies on Anthropic SDK defaults for HTTP timeouts.

- **Fallback strategies:** None — if Claude API is down, commands fail with `APIError`.

- **Graceful degradation:** None — AI features require working API connection.

- **Health checks:** None — no liveness/readiness probes (local CLI).

### 15.3 Error Recovery

- **Transaction management:** ChromaDB operations are atomic per collection. No multi-collection transactions.
- **Idempotency:** Embedding generation is idempotent (can regenerate same collection). Deletion is idempotent.
- **Dead letter queues:** N/A — no async job processing.
- **Manual intervention:** If `config.json` is corrupted, user can run `context-ai config reset` to restore defaults.

---

## 16. Technical Debt & Observations

### 16.1 Code Smells

| Issue | File | Lines | Description |
|---|---|---|---|
| God module | `src/services/ai_service.py` | 1141 | Too many responsibilities: 7 internal classes (TokenCalculator, ContextManager, DisplayManager, ChatHistoryManager, APIManager, ChatCommandHandler, AIService) |
| God module | `src/core/ai/prompt_builder.py` | 910 | Complex prompt building with many internal classes |
| Large file | `src/services/embedding_service.py` | 761 | Could split EmbeddingService and QueryService into separate files |
| Large file | `src/core/formatting/context_formatter.py` | 766 | Multiple formatters could be separate modules |
| Stub code | `src/services/embedding_service.py` | ~739-760 | Duplicate `AIService` stub class with TODO comments — dead code |
| No tests | `tests/` | — | Entire test directory is empty |

### 16.2 TODO/FIXME/HACK Inventory

| File | Line | Comment | Priority |
|---|---|---|---|
| `src/core/chunking/langchain_adapter.py` | 194 | `# @TODO: Expand text splitters for more programming languages` | Medium |
| `src/core/chunking/langchain_adapter.py` | 312 | `# @TODO CHANGE FOR CONFIG TOKEN COUNT` | Medium |
| `src/commands/storage.py` | 353 | `# TODO: Implement storage optimization` | Low |
| `src/commands/storage.py` | 762 | `# TODO: Add other component cleaning` | Low |
| `src/services/ai_service.py` | 579 | `# @TODO GET MODES FROM CONFIG CAGE` | Medium |
| `src/services/ai_service.py` | 584 | `# @TODO GET MODES FROM CONFIG CAGE` | Medium |
| `src/services/embedding_service.py` | 739 | `# TODO: Implement actual AI integration` | High |
| `src/services/embedding_service.py` | 760 | `# TODO: Implement actual chat` | High |

### 16.3 Dead Code

| Issue | Location | Details |
|---|---|---|
| Stub `AIService` class | `src/services/embedding_service.py` lines 739-760 | Incomplete placeholder with TODO comments, duplicates `src/services/ai_service.py` |
| Empty test directory | `tests/__init__.py` | No test implementations |
| UNCERTAIN: unused imports | Various | Would need `autoflake --check` to verify |

### 16.4 Inconsistencies

| Issue | Details |
|---|---|
| TODO format inconsistency | Some use `# @TODO`, others `# TODO:`, others `# TODO` |
| Singleton pattern inconsistency | Most use `_instance` global variable, but `ModelManager` uses `_model_instance` for the model and a different pattern for the manager |
| `AIService` name collision | Two classes named `AIService` exist — one in `ai_service.py` (full impl) and one in `embedding_service.py` (stub) |
| PyPI name mismatch | Package is `context-ai-alpha` on PyPI but README says `pip install context-ai` |

### 16.5 Improvement Opportunities

| Priority | Area | Description | Effort |
|---|---|---|---|
| High | Testing | Add unit and integration tests (0% coverage currently) | Large |
| High | CI/CD | Add GitHub Actions pipeline (test, lint, build) | Medium |
| High | Lock file | Add `pip-compile` or `uv.lock` for reproducible builds | Small |
| Medium | God module | Split `ai_service.py` into separate service files per class | Medium |
| Medium | Dead code | Remove stub `AIService` in `embedding_service.py` | Small |
| Medium | `.env.example` | Add environment variable template | Small |
| Medium | Retry config | Make API retry strategy configurable | Small |
| Low | Token cache | Add cache size limit to prevent unbounded growth | Small |
| Low | Storage optimization | Implement the TODO'd `optimize` subcommand in storage | Medium |
| Low | Tree-sitter | Replace LangChain chunking with tree-sitter for AST-aware chunking (documented in `src/core/chunking/TREE-SITTER.md`) | Large |

### 16.6 Risks

- **Single points of failure:**
  - Anthropic Claude API — only AI provider implemented. If Anthropic is down, all AI features fail.
  - `config.json` — single file for all configuration. Corruption breaks the app (mitigated by `config reset`).

- **Bus factor risks:**
  - No tests means refactoring is risky — any change could break things silently.
  - Complex prompt building logic in `prompt_builder.py` (910 lines) would be hard to modify without deep understanding.

- **Scaling risks:**
  - Local ChromaDB will struggle with very large codebases (>100K documents).
  - Token cache unbounded growth during long chat sessions.
  - Sentence-transformers model loading is slow without GPU.

- **Security risks:**
  - No Python lock file — supply chain vulnerability via dependency confusion.
  - UNCERTAIN: VS Code webview XSS risk from unsanitized user input in `chat.js`.

---

## 17. Summary & Key Takeaways

### 17.1 Architecture Strengths

- **Clean layered architecture:** Clear separation between CLI commands, services, core logic, and configuration.
- **Protocol-based extensibility:** `ChunkerProtocol`, `AIClientInterface`, `ProviderProtocol` enable future swapping of implementations (e.g., different AI providers, chunking strategies).
- **Singleton + factory patterns:** Well-implemented resource management for expensive objects (embedding models, config access).
- **Comprehensive prompt system:** Four prompt modes with file-based templates, language-aware guidelines, and security instructions.
- **Excellent documentation:** Thorough docstrings, architecture docs, per-command documentation.
- **Smart token management:** Sophisticated token budget allocation (65/35 split, history truncation with preservation of last 3 turns).
- **Language-aware chunking:** Different chunking separators per programming language via configurable YAML.

### 17.2 Architecture Weaknesses

- **Zero test coverage:** Critical risk — no unit, integration, or e2e tests.
- **No CI/CD:** No automated quality gates.
- **God modules:** `ai_service.py` (1141 lines) and `prompt_builder.py` (910 lines) have too many responsibilities.
- **No lock file:** Non-reproducible Python builds.
- **Single AI provider:** Only Claude supported despite the `AIClientFactory` abstraction.
- **No async:** Everything synchronous — could benefit from async for API calls and file I/O.
- **Dead code:** Stub `AIService` in `embedding_service.py` should be removed.

### 17.3 Key Files Reference

| File | Why It Matters |
|---|---|
| `src/cli.py` | Main entry point — all commands registered here |
| `src/services/ai_service.py` | Core AI orchestration — ask, chat, token management, display |
| `src/services/embedding_service.py` | Embedding generation, query, and selection logic |
| `src/core/ai/claude_client.py` | Claude API integration with retry and streaming |
| `src/core/ai/prompt_builder.py` | Prompt construction system (modes, guidelines, security) |
| `src/core/ai/ai_client_interface.py` | Provider abstraction layer (factory + interface) |
| `src/core/embeddings/vector_store.py` | ChromaDB vector store wrapper |
| `src/core/embeddings/model_manager.py` | Sentence-transformers model singleton |
| `src/core/chunking/langchain_adapter.py` | Language-aware code chunking |
| `src/core/formatting/context_formatter.py` | Formats retrieved context for AI consumption |
| `src/core/query/preprocessor.py` | Query normalization, synonyms, keyword extraction |
| `src/core/query/result_merger.py` | Cross-collection result merging and deduplication |
| `src/config/core.py` | Centralized config.json access (eliminates race conditions) |
| `src/config/settings.py` | User settings management |
| `src/config/storage.py` | Storage path management |
| `src/config/languages/registry.py` | Language detection and config registry |
| `src/config/providers/registry.py` | AI provider registry |
| `src/utils/exceptions.py` | Custom exception hierarchy |
| `src/utils/error_handler.py` | Command error handling decorator |
| `pyproject.toml` | Package definition, dependencies, entry point |

### 17.4 Glossary

| Term | Definition |
|---|---|
| **Embedding** | A vector representation of a code chunk, used for semantic similarity search |
| **Collection** | A named set of embeddings generated from a specific directory |
| **Active Embeddings** | Currently selected collections used for context retrieval |
| **Prompt Mode** | One of four AI response styles: minimal, standard, comprehensive, strict |
| **Context Window** | Claude's 200K token input limit; managed by token allocation strategy |
| **Chunking** | Process of splitting source files into smaller pieces for embedding |
| **Separators** | Language-specific text boundaries used during chunking (e.g., class/function definitions) |
| **Token Budget** | Allocated tokens split between context (65%) and response (35%) |
| **Guidelines** | Per-language coding standards injected into AI prompts |
| **Cross-Analysis** | Prompt component that considers relationships between multiple code files |

### 17.5 Quick Start for New Developers

1. **Start by reading:** `README.md` for overview, then `docs/architecture/prompt-modes.md` and `docs/architecture/context-window-management.md` for core concepts.
2. **Then understand the flow:** Trace `src/cli.py` → `src/commands/ask.py` → `src/services/ai_service.py` → `src/core/ai/claude_client.py` for the main ask workflow.
3. **Key abstractions to know:**
   - `AIClientInterface` / `ClaudeClient` — AI provider abstraction
   - `VectorStore` — ChromaDB wrapper
   - `PromptBuilder` — mode-based prompt construction
   - `ConfigCore` — centralized config access
   - `QueryPreprocessor` + `ResultMerger` — search pipeline
4. **Run the project:**
   ```bash
   make setup
   export ANTHROPIC_API_KEY="your-key"
   context-ai generate test-embed --path ./src
   context-ai ask "What does this project do?"
   ```
5. **Make your first change:** Add a new prompt mode by creating a new directory under `src/config/samples/prompts/` with `mode.yaml` and `core_instructions.md`, then reference it in the prompt builder.
