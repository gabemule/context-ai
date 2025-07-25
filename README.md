# Context-AI

> Cross-project code intelligence assistant

Transform your codebase into an intelligent assistant that provides cross-project context, discovers reusable components, and guides architectural decisions.

## 🚀 Quick Start

```bash
# Install in development mode
git clone https://github.com/gabemule/context-ai
cd context-ai
pip install -e .

# Generate embeddings for your projects
context-ai generate ./my-design-system --name "design-system-v1"
context-ai generate ./current-project --name "project-main-v2"

# Select active embeddings (interactive or direct)
context-ai select                              # Interactive checkbox interface
context-ai select design-system-v1 project-main-v2  # Direct CLI selection

# Query for context in different formats
context-ai query "authentication patterns" --verbose
context-ai query "modal components" --format json --max-results 5
context-ai query "error handling" --format markdown --output results.md

# Ask questions with cross-project intelligence
context-ai ask "Do we have existing components for file uploads?"
context-ai ask "What's our standard approach for API error handling?" --verbose
context-ai ask "How to implement authentication?" --format markdown --output auth-guide.md

# Interactive chat mode
context-ai chat
```

## 🎯 Key Features

- **Cross-project intelligence** - Advanced correlation analysis across multiple repositories
- **Component reusability** - Discover existing components before building new ones
- **Pattern discovery** - Learn established patterns and conventions with cross-project comparison
- **Architecture guidance** - Get context-aware architectural recommendations
- **Interactive selection** - Checkbox interface for choosing active embeddings
- **AI-powered insights** - Powered by Claude with enhanced cross-project correlation prompts
- **Smart token allocation** - Dynamic context sizing based on model capabilities
- **Multiple output formats** - JSON, XML, Markdown, Plain text with clipboard support
- **Configurable prompt modes** - From minimal to comprehensive analysis with coding guidelines
- **JavaScript/TypeScript guidelines** - Built-in coding standards with SOLID, DRY, YAGNI principles

## 📦 Installation

### From PyPI (Coming Soon)
```bash
pip install context-ai
```

### Development Installation
```bash
git clone https://github.com/gabemule/context-ai
cd context-ai
make setup
source venv/bin/activate
make install-dev
```

## 🔧 Configuration

Set up your Claude API key:
```bash
context-ai config set --claude-key sk-ant-xxxxxxxxxxxx
```

## 💡 Use Cases

### Component Discovery
```bash
context-ai ask "Do we have a modal component I can reuse?"
# → Finds Modal components across all your projects
```

### Helper Function Integration
```bash
context-ai ask "What validation utilities are available?"
# → Discovers validation helpers across helper libraries
```

### Architecture Guidance
```bash
context-ai ask "How should I structure a new dashboard page?"
# → Shows existing dashboard patterns and recommendations
```

## 🏗️ Development

```bash
# Setup development environment
make setup
source venv/bin/activate
make install-dev

# Development workflow
make test-watch    # Run tests continuously
make format lint   # Format and lint code

# Pre-commit checks
make test lint type-check
```

## 📋 Commands

### Core Commands (✅ Implemented)

#### `generate` - Generate embeddings from projects
```bash
# Basic usage
context-ai generate ./my-project --name "project-v1"

# With custom ignore file  
context-ai generate ./my-project --name "project-v1" --ignore-file .custom-ignore

# Disable progress bars (for CI/CD)
context-ai generate ./my-project --name "project-v1" --no-progress
```

#### `select` - Choose active embeddings  
```bash
# Interactive checkbox interface
context-ai select

# Direct CLI selection (great for scripts!)
context-ai select embedding1 embedding2 embedding3

# One-liner with query
context-ai select my-project && context-ai query "patterns"
```

#### `query` - Search embeddings for context
```bash
# Basic query
context-ai query "authentication patterns"

# Different output formats
context-ai query "components" --format json
context-ai query "error handling" --format markdown  
context-ai query "API integration" --format plain

# Limit results and save to file
context-ai query "modal components" --max-results 3 --output results.md

# Verbose mode with debug info
context-ai query "state management" --verbose --debug

# Copy results to clipboard (requires pyperclip)
context-ai query "validation helpers" --copy

# Debug mode with detailed preprocessing info
context-ai query "complex patterns" --debug --verbose
```

#### `config` - Manage configuration
```bash
# Set Claude API key
context-ai config set --claude-key sk-ant-xxxxxxxxxxxx

# View current configuration  
context-ai config list

# Test API key connectivity
context-ai config test

# Validate configuration and diagnose issues
context-ai config validate

# All config commands support --verbose for detailed output
context-ai config list --verbose
context-ai config test --verbose
```

#### `storage` - Manage embeddings and cleanup
```bash
# View storage information
context-ai storage info

# Clean up temporary files
context-ai storage cleanup --hours 24

# Delete specific embedding
context-ai storage delete embedding-name

# Reset all storage (⚠️ Destructive!)
context-ai storage reset --confirm

# All storage commands support --verbose for detailed output
context-ai storage info --verbose
context-ai storage cleanup --hours 48 --verbose
context-ai storage delete embedding-name --verbose
```

### AI Commands (✅ Implemented)

#### `ask` - AI-powered Q&A with cross-project correlation
```bash
# Basic AI question with context
context-ai ask "Do we have existing components for file uploads?"
context-ai ask "What's our standard approach for API error handling?"

# With advanced options and prompt modes
context-ai ask "Compare authentication patterns" --verbose --copy
context-ai ask "Best modal implementation?" --format markdown --output modal-analysis.md
context-ai ask "How to handle errors?" --format json --output error-patterns.json

# Different prompt modes for varying levels of analysis
context-ai ask "How to implement login?" --prompt-mode minimal      # Fast, basic response
context-ai ask "How to implement login?" --prompt-mode standard     # Default with guidelines
context-ai ask "How to implement login?" --prompt-mode comprehensive # Full analysis
context-ai ask "How to implement login?" --prompt-mode strict       # Enforced code standards
```

#### `chat` - Interactive AI chat session
```bash
# Basic chat session
context-ai chat

# Chat with different prompt modes (applies to entire session)
context-ai chat --prompt-mode minimal         # Fast, basic responses throughout chat
context-ai chat --prompt-mode standard        # Default with guidelines (recommended)
context-ai chat --prompt-mode comprehensive   # Full architectural analysis for all questions
context-ai chat --prompt-mode strict          # Enforced coding standards throughout session

# Combine with verbose mode for detailed processing info
context-ai chat --prompt-mode comprehensive --verbose
```

### 🎛️ Prompt Modes

Control the depth and focus of AI responses with configurable prompt modes:

| Mode | Description | Best For | Features |
|------|-------------|----------|----------|
| `minimal` | Basic context + question only | Quick queries, simple lookups | Fastest processing, no extra instructions |
| `standard` | Cross-project awareness + coding guidelines | Daily development work | JS/TS guidelines when detected, cross-project hints |
| `comprehensive` | Full analysis + architectural insights | Complex queries, architecture decisions | Deep cross-project comparison, best practices |
| `strict` | Enforced standards + code review approach | Code generation, refactoring | Strict guideline enforcement, detailed code review |

```bash
# Examples with ask command (single questions)
context-ai ask "How to validate forms?" --prompt-mode minimal      # Quick answer
context-ai ask "How to validate forms?" --prompt-mode standard     # With JS/TS guidelines  
context-ai ask "How to validate forms?" --prompt-mode comprehensive # Full architectural analysis
context-ai ask "How to validate forms?" --prompt-mode strict       # Code review quality

# Examples with chat command (applies to entire session)
context-ai chat --prompt-mode standard        # All questions use standard mode with guidelines
context-ai chat --prompt-mode comprehensive   # All responses include full architectural analysis
```

### 📐 Built-in Coding Guidelines

For JavaScript/TypeScript projects, Context-AI automatically applies coding guidelines focused on:

- **SOLID, DRY, YAGNI principles** - Clean architecture fundamentals
- **Functional programming over classes** - Modern JS/TS best practices  
- **Pure functions and immutability** - Predictable, testable code
- **ES6+ features** - Arrow functions, destructuring, async/await
- **Performance optimization** - Lazy loading, memoization, debouncing
- **Error handling patterns** - Explicit error handling, Result types
- **Testing philosophy** - TDD, unit tests, integration tests

Guidelines are automatically detected and applied when:
- JavaScript/TypeScript files are found in context
- Code-related keywords are used in questions
- Implementation or development queries are made

**Note**: Guidelines work identically in both `ask` (single questions) and `chat` (conversation sessions) commands. In chat mode, the selected prompt mode applies consistently throughout the entire conversation.

### Query Output Formats

| Format | Description | Use Case | Cross-Project Analysis |
|--------|-------------|----------|----------------------|
| `ai_friendly` (default) | Rich format with source attribution + cross-project correlation | AI consumption, debugging | ✅ Enhanced |
| `json` | Structured JSON with metadata | API integration, processing | ✅ Project grouping |
| `xml` | Well-formed XML structure | Enterprise integration | ✅ Hierarchical |
| `markdown` | Clean markdown format | Documentation, reports | ✅ Formatted |
| `plain` | Simple text format | Simple scripts, pipes | ✅ Basic |

### Interactive Selection Interface

The `select` command opens an interactive checkbox interface:

```bash
context-ai select

🎯 Select active embeddings for queries

[?] Select embeddings to query (use space to select/deselect, enter to confirm):
 > [x] design-system-v1 (153 chunks, 27 files, 25 Jul 2025)
   [x] project-main-v2 (800 chunks, 45 files, 1 day ago) 
   [ ] api-docs-v1 (300 chunks, 12 files, 1 week ago)
   [ ] helpers-lib-v1 (150 chunks, 8 files, 2 days ago)

✅ Selected embeddings: design-system-v1, project-main-v2
```

### Example Workflows

```bash
# 1. Complete setup workflow
context-ai generate ./my-frontend --name "frontend-v1"
context-ai generate ./my-backend --name "backend-v1"  
context-ai generate ./design-system --name "ds-v1"
context-ai select frontend-v1 backend-v1 ds-v1
context-ai query "authentication flow" --verbose

# 2. One-liner for quick queries
context-ai select my-project && context-ai query "error handling" --format json

# 3. Batch processing for documentation
context-ai query "components" --format markdown --output components.md
context-ai query "API patterns" --format markdown --output api-patterns.md
context-ai query "utilities" --format markdown --output utilities.md

# 4. Debug workflow
context-ai query "complex query" --debug --verbose --output debug.log

# 5. Interactive development sessions with different complexity levels
context-ai chat --prompt-mode standard        # Daily development work
context-ai chat --prompt-mode comprehensive   # Architecture planning sessions  
context-ai chat --prompt-mode strict          # Code review and refactoring sessions
```

## 📖 Complete Command Reference

### Global Options
- `--version` - Show program version
- `--verbose, -v` - Enable verbose output (available on all commands)
- `--help, -h` - Show help message

### Commands Summary

| Command | Purpose | Key Options |
|---------|---------|-------------|
| `generate` | Create embeddings | `--name`, `--ignore-file`, `--no-progress` |
| `select` | Choose active embeddings | Interactive or direct selection |
| `query` | Search for context | `--format`, `--max-results`, `--debug`, `--copy`, `--output` |
| `ask` | AI Q&A with context | `--format`, `--prompt-mode`, `--copy`, `--output` |
| `chat` | Interactive AI session | `--prompt-mode` |
| `config` | Manage settings | `set`, `list`, `test`, `validate` subcommands |
| `storage` | Manage data | `info`, `cleanup`, `reset`, `delete` subcommands |

### Format Options (query & ask)
- `ai_friendly` (default) - Rich context for AI processing
- `json` - Structured JSON output  
- `xml` - XML format
- `markdown` - Clean markdown
- `plain` - Simple text

### Prompt Modes (ask & chat)
- `minimal` - Basic context only
- `standard` - Default with guidelines (recommended)
- `comprehensive` - Full cross-project analysis  
- `strict` - Enforced coding standards

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `make dev` to ensure quality checks pass
5. Create a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🛠️ Status

**Beta** - Core query system fully implemented and tested! 🚀

### ✅ Completed Features
- **Embedding generation** with sentence-transformers + ChromaDB
- **Interactive selection** with checkbox interface + direct CLI args
- **Multi-format queries** (AI-friendly, JSON, XML, Markdown, Plain)
- **Cross-embedding search** with result merging & normalization  
- **Token counting** with tiktoken integration
- **Multi-language support** (English/Portuguese query processing)
- **Progress tracking** with rich UI
- **Storage management** with cleanup utilities
- **Claude integration** with AI-powered Q&A and cross-project correlation
- **Chat interface** for interactive conversations
- **Dynamic token allocation** based on model capabilities (up to 200k tokens)
- **Enhanced cross-project analysis** with pattern detection and comparison
- **Clipboard integration** and file output support
- **Configurable prompt modes** with JavaScript/TypeScript coding guidelines
- **Auto-detection of coding contexts** with SOLID, DRY, YAGNI principle enforcement

### 🚀 Production Ready
All core features are implemented and tested. The system is ready for production use!

See [Plan.md](Plan.md) for detailed development roadmap and [Future.md](Future.md) for post-MVP enhancements.