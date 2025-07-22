# Context-AI - AI-Powered Documentation Assistant

> Transform your documentation into an intelligent, queryable knowledge base using embeddings and RAG

## 🎯 Project Overview

### Mission
Create a CLI tool that converts documentation into embeddings for AI-powered contextual queries, enabling developers to get precise, relevant documentation context for any question.

### Core Features
- **Generate embeddings** from entire repositories (code + docs)
- **Smart file filtering** with .contextignore/.gitignore support
- **Code-aware chunking** that preserves context (functions, components, classes)
- **Multi-language support** (JS/TS, Python, CSS, JSON, YAML, MD, etc.)
- **Manage multiple embedding databases** (switch between projects)
- **Query embeddings** to get relevant context for AI prompts
- **Local-first approach** - no external APIs required for embeddings
- **Reliable and efficient** - dependable query responses

### Value Proposition
- **Context window optimization** - only load relevant chunks
- **Codebase exploration** - "How is authentication implemented?"
- **Multi-project support** - switch between different repositories
- **AI integration ready** - output formatted for Cline/Cursor/ChatGPT
- **Offline capability** - works without internet connection

---

## 🏗️ Architecture Design

### System Architecture
```
Context-AI CLI
├── Core Engine
│   ├── Embedding Generator (sentence-transformers)
│   ├── Vector Database (ChromaDB)
│   ├── Query Engine (RAG)
│   └── Context Formatter
├── Storage Layer
│   ├── Multiple Embedding Databases
│   ├── Metadata Management
│   └── Configuration Storage
└── CLI Interface
    ├── generate-embedding command
    ├── select-embedding command
    └── query command
```

### Technology Stack
- **Language**: Python 3.8+
- **CLI Framework**: argparse (Python built-in)
- **Embeddings**: sentence-transformers
- **Vector DB**: ChromaDB
- **Text Processing**: langchain-text-splitters
- **Configuration**: JSON/YAML
- **Packaging**: setuptools/pyproject.toml

### Directory Structure
```
context-ai/
├── pyproject.toml
├── README.md
├── Makefile                    # Development commands
├── src/
│   ├── __init__.py
│   ├── cli.py                  # Entry point
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── generate.py         # generate-embedding
│   │   ├── select.py           # select-embedding
│   │   ├── query.py            # query command (context search)
│   │   ├── ask.py              # ask command (AI integration)
│   │   └── chat.py             # chat command (interactive mode)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── embeddings.py       # Embedding generation
│   │   ├── storage.py          # Database management
│   │   ├── query.py            # RAG query engine
│   │   ├── formatter.py        # Output formatting
│   │   └── ai/                 # AI Integration Module
│   │       ├── __init__.py
│   │       ├── claude_client.py # Claude API integration
│   │       └── chat_interface.py # Simple chat interface
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py         # Configuration management
│   │   └── models.py           # Data models
│   └── utils/
│       ├── __init__.py
│       ├── file_utils.py       # File operations
│       └── text_utils.py       # Text processing
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_embeddings.py
│   ├── test_storage.py
│   └── test_query.py
```

---

## 📋 Implementation Phases

## Phase 1: Core Infrastructure

### 1.1 Project Setup
- [ ] **1.1.1** Create Python project with pyproject.toml
- [ ] **1.1.2** Setup development environment (venv, dependencies)
- [ ] **1.1.3** Configure project structure (src/)
- [ ] **1.1.4** Setup basic package metadata and entry points
- [ ] **1.1.5** Initialize git repository with .gitignore
- [ ] **1.1.6** Create Makefile with development commands
- [ ] **1.1.7** Create basic README.md with installation instructions

### 1.2 CLI Foundation
- [ ] **1.2.1** Setup argparse framework and command structure
- [ ] **1.2.2** Create main CLI entry point (cli.py)
- [ ] **1.2.3** Implement subcommand parser structure
- [ ] **1.2.4** Add basic --help and --version support
- [ ] **1.2.5** Setup logging configuration (debug, info, error levels)
- [ ] **1.2.6** Implement basic error handling and user feedback

### 1.3 Configuration System
- [ ] **1.3.1** Design configuration schema (JSON format)
- [ ] **1.3.2** Implement config file location (~/.context-ai/config.json)
- [ ] **1.3.3** Create settings management class
- [ ] **1.3.4** Add active embedding tracking (active.json)
- [ ] **1.3.5** Implement config validation and error handling
- [ ] **1.3.6** Add config initialization on first run

### 1.4 Storage Foundation
- [ ] **1.4.1** Design storage directory structure (~/.context-ai/)
- [ ] **1.4.2** Implement storage path management
- [ ] **1.4.3** Create metadata schema for embeddings
- [ ] **1.4.4** Add storage directory initialization
- [ ] **1.4.5** Add basic reset/cleanup commands

**Phase 1 Success Criteria:**
- ✅ CLI runs without errors
- ✅ Basic commands show help text
- ✅ Configuration system creates and manages config files
- ✅ Storage directories are properly initialized
- ✅ Logging works at different levels

---

## Phase 2: Embedding Generation

### 2.1 Text Processing Engine
- [ ] **2.1.1** Install and configure langchain-text-splitters
- [ ] **2.1.2** Implement basic file discovery and reading
- [ ] **2.1.3** Create simple code-aware chunking (basic function/component detection)
- [ ] **2.1.4** Add basic metadata extraction (file type, language)
- [ ] **2.1.5** Implement ignore file system (.gitignore support)
- [ ] **2.1.6** Add comprehensive language support (JS/TS/Node, Python, CSS/Sass, JSON/YAML, MD, SQL, etc.)
- [ ] **2.1.7** Add progress tracking for large repository processing

### 2.2 Embedding Model Integration
- [ ] **2.2.1** Install sentence-transformers dependency
- [ ] **2.2.2** Implement model loading and caching
- [ ] **2.2.3** Use single model (all-MiniLM-L6-v2) for MVP
- [ ] **2.2.4** Create embedding generation with batch processing
- [ ] **2.2.5** Add basic model download progress indicators

### 2.3 ChromaDB Integration
- [ ] **2.3.1** Install and configure ChromaDB
- [ ] **2.3.2** Implement collection creation and management
- [ ] **2.3.3** Add document and embedding storage
- [ ] **2.3.4** Create basic metadata indexing

### 2.4 Generate Command Implementation
- [ ] **2.4.1** Create generate-embedding command structure
- [ ] **2.4.2** Add basic path validation and error handling
- [ ] **2.4.3** Implement simple ignore file resolution
- [ ] **2.4.4** Add basic file type detection and filtering
- [ ] **2.4.5** Implement progress bars and status updates
- [ ] **2.4.6** Add embedding naming system
- [ ] **2.4.7** Create basic completion statistics

**Phase 2 Success Criteria:**
- ✅ Can generate embeddings from documentation directories
- ✅ Embeddings are stored in ChromaDB with proper metadata
- ✅ Progress tracking works for large document sets
- ✅ Generated embeddings can be named and managed
- ✅ Basic completion statistics are displayed

---

## Phase 3: Query and Selection System

### 3.1 Embedding Management
- [ ] **3.1.1** Implement embedding listing functionality
- [ ] **3.1.2** Create basic embedding metadata display (size, chunks, date)
- [ ] **3.1.3** Add single embedding selection and activation system
- [ ] **3.1.4** Implement multi-embedding selection interface
- [ ] **3.1.5** Implement embedding deletion and cleanup

### 3.2 Query Engine Development
- [ ] **3.2.1** Implement similarity search algorithm (single embedding)
- [ ] **3.2.2** Add multi-embedding parallel query system
- [ ] **3.2.3** Create cross-embedding result merging and ranking
- [ ] **3.2.4** Implement source attribution and context balancing
- [ ] **3.2.5** Add basic query preprocessing

### 3.3 Context Formatting
- [ ] **3.3.1** Design AI-friendly output format
- [ ] **3.3.2** Implement context chunk assembly
- [ ] **3.3.3** Add source attribution and linking
- [ ] **3.3.4** Implement basic context size limiting

### 3.4 Select Command Implementation
- [ ] **3.4.1** Create basic selection interface
- [ ] **3.4.2** Add embedding information display
- [ ] **3.4.3** Implement active embedding switching
- [ ] **3.4.4** Create selection validation and error handling

### 3.5 Query Command Implementation
- [ ] **3.5.1** Create query command with context search processing
- [ ] **3.5.2** Implement context retrieval and assembly
- [ ] **3.5.3** Add output formatting for AI consumption
- [ ] **3.5.4** Add basic debugging and verbose output modes

**Phase 3 Success Criteria:**
- ✅ Can list and select between multiple embeddings
- ✅ Query system returns relevant, ranked results
- ✅ Output is properly formatted for AI consumption
- ✅ Selection system is intuitive and fast
- ✅ Query system performs adequately for typical use cases

---

## Phase 4: Advanced Features and Polish

### 4.1 Integration Features
- [ ] **4.1.1** Add output format options (JSON, XML, plain text)
- [ ] **4.1.2** Implement clipboard integration (--copy flag)
- [ ] **4.1.3** Add file output options for large contexts

### 4.2 User Experience Enhancements 
- [ ] **4.2.1** Add colorized output and better formatting
- [ ] **4.2.2** Add comprehensive help and examples
- [ ] **4.2.3** Add configuration validation and repair tools

### 4.3 AI Integration - Claude MVP
- [ ] **4.3.1** Claude Integration Foundation
  - [ ] **4.3.1.1** Implement basic Anthropic API client
  - [ ] **4.3.1.2** Add support for Claude-3 models (Sonnet, Haiku)
  - [ ] **4.3.1.3** Basic prompt formatting for Claude
  - [ ] **4.3.1.4** Simple retry logic and timeout handling
- [ ] **4.3.2** API Key Configuration (Simple)
  - [ ] **4.3.2.1** Basic Claude API key storage
  - [ ] **4.3.2.2** Key validation and connectivity testing
  - [ ] **4.3.2.3** Simple configuration management
- [ ] **4.3.3** Core Ask Command Implementation
  - [ ] **4.3.3.1** Create ask command with Claude integration
  - [ ] **4.3.3.2** Basic context retrieval and assembly
  - [ ] **4.3.3.3** Simple response formatting and output
- [ ] **4.3.4** Basic Chat Mode
  - [ ] **4.3.4.1** Implement simple chat interface with Claude
  - [ ] **4.3.4.2** Basic conversation history (in-memory only)
- [ ] **4.3.5** Basic Error Handling
  - [ ] **4.3.5.1** Basic error handling and user messages
  - [ ] **4.3.5.2** Simple rate limiting

**Phase 4 Success Criteria:**
- ✅ Advanced features work seamlessly with core functionality
- ✅ User experience is polished and intuitive
- ✅ Error handling covers edge cases gracefully
- ✅ Integration options work with major AI tools

---

## 🧪 Testing Strategy (MVP)

### Basic Testing
- [ ] **Core Functions**: Test embedding generation and query functionality
- [ ] **Error Handling**: Test with invalid inputs and edge cases
- [ ] **Tool Works**: Verify tool works on developer's machine

### Manual Validation
- [ ] **End-to-End Flow**: Generate → select → query → ask workflow
- [ ] **Claude Integration**: Verify ask and chat commands work
- [ ] **Multi-embedding**: Test cross-project queries
- [ ] **Output Quality**: Verify AI-friendly output format

---

## 📦 Deployment Plan (MVP)

### Package Distribution
- [ ] **PyPI Package**: Upload to Python Package Index
- [ ] **GitHub Releases**: Tagged releases with changelog

### Documentation
- [ ] **Installation Guide**: Basic pip install instructions
- [ ] **User Manual**: Simple usage examples
- [ ] **README**: Quick start guide


---

## 🔮 Future Enhancements

### Phase 5: Simple Multi-Provider Support (Month 2)
- [ ] **OpenAI Integration**: Add GPT-4, GPT-4o as second provider option
  - [ ] **5.1.1** Implement OpenAI API client with basic retry logic
  - [ ] **5.1.2** Add support for key OpenAI models (GPT-4, GPT-4o)
  - [ ] **5.1.3** Simple model selection between Claude and OpenAI
  - [ ] **5.1.4** Basic token counting for OpenAI
- [ ] **Simple Fallback System**: Basic provider fallback
  - [ ] **5.2.1** Implement simple fallback: Claude → OpenAI
  - [ ] **5.2.2** Add basic provider health checking
  - [ ] **5.2.3** Manual provider switching commands
  - [ ] **5.2.4** Basic error handling between providers

### Phase 6: Essential Format Support (Month 3)
- [ ] **Multi-modal Documentation**: Support for common doc formats
  - [ ] **6.1.1** PDF support for documentation files
  - [ ] **6.1.2** Image support (diagrams, screenshots) with OCR
  - [ ] **6.1.3** Basic text extraction from images
  - [ ] **6.1.4** Metadata preservation for multimedia content
- [ ] **Real-time Updates**: Keep embeddings current
  - [ ] **6.2.1** File watching for documentation changes
  - [ ] **6.2.2** Auto-update embeddings on file changes
  - [ ] **6.2.3** Smart incremental updates (only changed files)
  - [ ] **6.2.4** Background processing for large updates

**Future Development Note:**
*Beyond Phase 6, new features will be driven by actual user feedback and demonstrated need. Focus remains on simplicity, reliability, and core value delivery rather than feature expansion.*

---

## 🎯 Success Criteria (MVP)

### Core Functionality
- ✅ Tool generates embeddings from documentation successfully
- ✅ Query system returns relevant results from embeddings
- ✅ Claude integration works for ask and chat commands
- ✅ Multi-embedding selection enables cross-project queries
- ✅ Tool runs reliably on developer's local machine

### Code Quality
- ✅ All public APIs have proper type hints
- ✅ Code passes linting (flake8, black, mypy)
- ✅ Core functions have docstrings and basic tests
- ✅ CLI commands work as documented
- ✅ Error handling provides helpful user feedback

---

## 🛠️ Development Guidelines (MVP)

### Code Quality Standards
- **Type Hints**: Type coverage for public APIs
- **Documentation**: Docstrings for all public functions and classes
- **Linting**: Pass flake8, black, and mypy checks
- **Testing**: Basic tests for core functionality


### Performance Goals (Realistic)
- **Startup Time**: CLI should start reasonably fast
- **Memory Usage**: Should not consume excessive memory
- **Offline Operation**: Work completely offline after initial setup
- **File Support**: Handle typical documentation sets effectively

### Makefile Commands
```makefile
# Development Setup
setup:          # Complete development setup (venv + deps)
	echo "Run 'source venv/bin/activate' to activate environment"
install:        # Install production dependencies  
install-dev:    # Install development dependencies
clean:          # Clean build artifacts and cache

# Development
dev-install:    # Install in development mode (-e .)

# Testing & Quality
test:           # Run all tests
test-watch:     # Run tests in watch mode  
lint:           # Run linting (flake8, mypy)
format:         # Auto-format code (black, isort)
type-check:     # Run type checking (mypy)

# Build & Release
build:          # Build package for distribution
publish:        # Publish to PyPI
```

**Usage Examples:**
```bash
# Setup new development environment
make setup

# Development workflow  
make dev-install
make test-watch    # Run tests continuously
make format lint   # Format and lint code

# Pre-commit checks
make test lint type-check

# Release workflow
make clean build publish
```

---

## 📋 File Processing Strategy

### Ignore File Hierarchy
```python
def resolve_ignore_patterns(project_path, custom_config=None):
    """Resolve ignore patterns with intelligent fallback"""
    if custom_config:
        return load_ignore_file(custom_config)
    
    context_ignore = project_path / ".contextignore" 
    if context_ignore.exists():
        return load_ignore_file(context_ignore)
    
    gitignore = project_path / ".gitignore"
    if gitignore.exists():
        return load_ignore_file(gitignore) + CONTEXT_DEFAULTS
    
    return CONTEXT_DEFAULTS

CONTEXT_DEFAULTS = [
    "node_modules/", ".git/", "dist/", "build/", 
    "*.log", ".env*", "coverage/", "__pycache__/",
    "*.min.js", "*.bundle.js", "*.map"
]
```

### Supported File Types
- **JavaScript/TypeScript**: `.js`, `.ts`, `.tsx`, `.jsx`
- **Python**: `.py`, `.pyx`, `.pyi`
- **Web**: `.html`, `.css`, `.scss`, `.sass`, `.less`
- **Templates**: `.vue`, `.svelte`, `.astro`, `.twig`
- **Configuration**: `.json`, `.yaml`, `.yml`, `.toml`, `.ini`
- **Documentation**: `.md`, `.rst`, `.txt`, `.mdx`
- **Data**: `.sql`, `.graphql`, `.gql`, `.xml`
- **Other Languages**: `.go`, `.rs`, `.java`, `.c`, `.cpp`, `.h`

### Code-Aware Chunking Examples
```python
# React Component Chunking
chunk = {
    "text": "interface ButtonProps { variant: 'primary' | 'secondary' }",
    "metadata": {
        "file": "components/Button/Button.tsx",
        "type": "interface", 
        "component": "Button",
        "props": ["variant"],
        "language": "typescript"
    }
}

# Python Function Chunking  
chunk = {
    "text": "def useForm(schema: Dict) -> FormState:",
    "metadata": {
        "file": "hooks/useForm.py",
        "type": "function",
        "name": "useForm", 
        "params": ["schema"],
        "language": "python"
    }
}

# HTML Component Chunking
chunk = {
    "text": "<button class='btn btn-primary' data-variant='primary'>",
    "metadata": {
        "file": "templates/button.html",
        "type": "element",
        "tag": "button",
        "classes": ["btn", "btn-primary"],
        "language": "html"
    }
}
```

### Usage Examples (MVP)
```bash
# Generate embeddings for different projects
context-ai generate ./my-design-system --name "design-system-v1"
context-ai generate ./current-project --name "project-main-v2"
context-ai generate ./api-docs --name "api-docs-v1"

# Configure Claude API key
context-ai config set --claude-key sk-ant-xxxxxxxxxxxx
context-ai config list

# Single embedding selection
context-ai select design-system-v1

# Multi-embedding selection
context-ai select design-system-v1,project-main-v2

# Context-only queries (original functionality)
context-ai query "How to use Button from design-system in my current project?"
context-ai query "What authentication patterns can I reuse from api-docs?"

# RAG Complete - Direct Questions with AI Responses
context-ai ask "How to use Button from design-system in my current project?"
# → Returns AI-generated answer based on retrieved context

context-ai ask "What props does the Button component accept?"
# → Analyzes design system docs and provides answer

# Interactive Chat Mode
context-ai chat
# → Enters interactive mode with full conversation memory
# User: "How to use Button component?"
# AI: "Based on your design system, the Button component accepts..."
# User: "Can you show me an example with primary variant?"
# AI: "Sure! Here's an example using the primary variant..."
```

### AI Configuration Schema (MVP - Claude Only)
```json
{
  "claude_api_key": "sk-ant-xxxxxxxxxxxx",
  "default_model": "claude-3-sonnet",
  "max_tokens": 4000
}
```

### MVP Implementation Notes

#### API Key Storage (Simple)
```python
# MVP: Simple plaintext storage in config file
# Security can be added in v2 if needed
{
  "claude_api_key": "sk-ant-xxxxxxxxxxxx"
}
```

#### Context Management (Basic)
```python
# MVP: Simple context assembly
def assemble_context(chunks, max_tokens=4000):
    context = ""
    for chunk in sorted_chunks_by_relevance:
        if len(context + chunk.text) < max_tokens:
            context += f"\n## {chunk.source}:\n{chunk.text}\n"
    return context
```

### Multi-Embedding Output Example
```
=== CONTEXT FROM MULTIPLE SOURCES ===

## From design-system-v1 (similarity: 0.92):
Button component interface:
```typescript
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'outline'
  size: 'sm' | 'md' | 'lg'
  disabled?: boolean
  onClick?: () => void
}
```

## From project-main-v2 (similarity: 0.87):
Current usage in LoginForm.tsx:
```typescript
import { Button } from '@company/design-system'

export const LoginForm = () => {
  return (
    <Button 
      variant="primary" 
      size="lg"
      onClick={handleLogin}
    >
      Sign In
    </Button>
  )
}
```

## Cross-reference analysis:
- ✅ All props used correctly
- ✅ Import path matches design system
- 💡 Consider adding loading state prop
```

---

## 📚 Resources and References

### Technical Documentation
- [Sentence Transformers Documentation](https://www.sbert.net/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Python argparse Documentation](https://docs.python.org/3/library/argparse.html)
- [LangChain Text Splitters](https://python.langchain.com/docs/modules/data_connection/document_transformers/)

### Example Implementations
- [Similar RAG Tools](https://github.com/topics/rag)
- [CLI Best Practices](https://clig.dev/)
- [Python Packaging Guide](https://packaging.python.org/)
- [Vector Database Comparisons](https://vdbs.superlinked.com/)

### File Processing Libraries
- [Tree-sitter](https://tree-sitter.github.io/tree-sitter/) - Syntax-aware parsing
- [Pygments](https://pygments.org/) - Language detection and highlighting
- [GitPython](https://gitpython.readthedocs.io/) - Git integration for ignore files
- [Pathspec](https://pypi.org/project/pathspec/) - Path pattern matching


---

## ✅ MVP Checklist

### Pre-Release Validation
- [ ] All core features implemented and tested
- [ ] Basic documentation written (README, usage examples)
- [ ] Tool works on developer's machine
- [ ] Code is properly typed and linted
- [ ] PyPI package can be built and uploaded

### Post-Release Tasks
- [ ] Monitor initial user feedback
- [ ] Address critical bug reports
- [ ] Update documentation based on user questions
- [ ] Plan next phase features based on actual usage
- [ ] Celebrate successful launch! 🎉

---

*This document serves as the complete roadmap for Context-AI development. Each checkbox represents a concrete, measurable step toward building a powerful AI-assisted documentation tool that will transform how developers interact with technical documentation.*
