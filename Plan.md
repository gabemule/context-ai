# Context-AI - Cross-Project Code Intelligence Assistant

> Transform your codebase into an intelligent assistant that provides cross-project context, discovers reusable components, and guides architectural decisions

## 🎯 Project Overview

### Mission
Create an intelligent code assistant that provides cross-project context and insights, helping developers understand codebases, discover reusable components, and follow established patterns across multiple repositories.

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
- **Cross-project intelligence** - "How does our design system handle modals?"
- **Component reusability** - "Do we have existing upload components I can reuse?"
- **Pattern discovery** - "What's our standard approach for API error handling?"
- **Architecture guidance** - "How should I structure this new feature?"
- **Code consistency** - "What validation helpers are available across projects?"

### Key Use Cases
- **Cross-project intelligence** - "How does our design system handle modals?"
- **Component reusability** - "Do we have existing upload components I can reuse?"
- **Pattern discovery** - "What's our standard approach for API error handling?"
- **Architecture guidance** - "How should I structure this new feature?"
- **Code consistency** - "What validation helpers are available across projects?"

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
- **Interactive UI**: inquirer (checkbox selections)
- **Progress Tracking**: rich (fancy progress bars)
- **Embeddings**: sentence-transformers
- **Vector DB**: ChromaDB (single collection design)
- **Text Processing**: langchain-text-splitters (MVP)
- **Configuration**: JSON/YAML with pydantic validation
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
│   │   ├── chunking/           # Text Processing Module
│   │   │   ├── __init__.py
│   │   │   ├── protocol.py     # Interface comum
│   │   │   └── langchain_adapter.py # LangChain implementation
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
│   ├── test_query.py
│   └── test_chunking.py        # Chunking tests
```

---

## 🔧 Technical Specifications

### CLI Interactive Interface
```python
# Interactive embedding selection using inquirer
import inquirer

def select_embeddings():
    embeddings = get_available_embeddings()
    
    questions = [
        inquirer.Checkbox(
            'selected_embeddings',
            message="Select embeddings to query",
            choices=[
                (f"{name} ({size} tokens, {date})", name) 
                for name, size, date in embeddings
            ],
        ),
    ]
    
    answers = inquirer.prompt(questions)
    return answers['selected_embeddings']

# Usage:
# → [ ] design-system-v1 (1.2M tokens, 3 days ago)
#   [x] project-main-v2 (800K tokens, 1 day ago) 
#   [ ] api-docs-v1 (300K tokens, 1 week ago)
```

### ChromaDB Single Collection Design
```python
# Single collection for all embeddings with metadata filtering
collection_name = "context_ai_embeddings"

metadata_schema = {
    "embedding_name": "design-system-v1",    # Primary filter
    "file_path": "components/Button.tsx",
    "language": "typescript", 
    "chunk_index": 0,
    "chunker": "langchain",
    "created_at": "2025-01-15T10:30:00Z",
    "file_size": 2048,
    "chunk_type": "interface"
}

# Multi-embedding query (single operation)
results = collection.query(
    query_texts=["How to use Button?"],
    where={"embedding_name": {"$in": ["design-system-v1", "project-main-v2"]}},
    n_results=20
)
```

### Score Normalization & Result Merging
```python
def merge_multi_embedding_results(results):
    """Normalize scores and merge results from multiple embeddings"""
    # Group results by embedding_name
    grouped = {}
    for i, doc in enumerate(results['documents'][0]):
        metadata = results['metadatas'][0][i]
        embedding_name = metadata['embedding_name']
        score = results['distances'][0][i]
        
        if embedding_name not in grouped:
            grouped[embedding_name] = []
        
        grouped[embedding_name].append({
            'text': doc,
            'score': score,
            'metadata': metadata
        })
    
    # Normalize scores per embedding
    normalized_results = []
    for embedding_name, embedding_results in grouped.items():
        max_score = max(r['score'] for r in embedding_results)
        for result in embedding_results:
            normalized_score = result['score'] / max_score if max_score > 0 else 0
            result['final_score'] = normalized_score * 0.9  # Weight factor
            result['source_embedding'] = embedding_name
            normalized_results.append(result)
    
    # Sort by final score
    return sorted(normalized_results, key=lambda x: x['final_score'], reverse=True)
```

### Rich Progress Tracking
```python
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

def track_embedding_generation(files):
    """Fancy progress tracking for embedding generation"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("[bold blue]{task.fields[current_file]}"),
    ) as progress:
        
        task = progress.add_task("Generating embeddings...", total=len(files))
        
        for file in files:
            progress.update(task, current_file=file.name, advance=1)
            # Process file...
            progress.console.print(f"✅ Processed {file.name}")
```

### Hierarchical Configuration Schema
```python
from pydantic import BaseModel
from typing import Dict, List, Optional

class AIProviderConfig(BaseModel):
    api_key: str
    default_model: str
    max_tokens: int = 4000

class ChunkingConfig(BaseModel):
    chunk_size: int = 2000
    chunk_overlap: int = 200
    supported_extensions: List[str] = [".py", ".js", ".ts", ".md", ".tsx", ".jsx"]

class StorageConfig(BaseModel):
    base_path: str = "~/.context-ai"
    max_embeddings: int = 50
    cleanup_after_days: int = 30

class ContextAIConfig(BaseModel):
    storage: StorageConfig = StorageConfig()
    chunking: ChunkingConfig = ChunkingConfig()
    ai: Dict[str, AIProviderConfig] = {}
    active_provider: str = "claude"
    active_embeddings: List[str] = []

# Example config.json:
{
    "storage": {
        "base_path": "~/.context-ai",
        "max_embeddings": 50,
        "cleanup_after_days": 30
    },
    "chunking": {
        "chunk_size": 2000,
        "chunk_overlap": 200,  
        "supported_extensions": [".py", ".js", ".ts", ".md", ".tsx", ".jsx"]
    },
    "ai": {
        "claude": {
            "api_key": "sk-ant-xxxxxxxxxxxx",
            "default_model": "claude-3-sonnet",
            "max_tokens": 4000
        }
    },
    "active_provider": "claude",
    "active_embeddings": ["design-system-v1", "project-main-v2"]
}
```

### Dependencies
```toml
# pyproject.toml
[project]
dependencies = [
    "sentence-transformers>=2.2.0",
    "chromadb>=0.4.0", 
    "langchain-text-splitters>=0.0.1",
    "inquirer>=3.0.0",          # Interactive CLI (~300KB)
    "rich>=13.0.0",             # Progress bars (~2MB)
    "pydantic>=2.0.0",          # Config validation (~1MB)
    "anthropic>=0.3.0",         # Claude API client
    "pathspec>=0.11.0",         # .gitignore parsing
]
```

---

## ⚠️ Critical Success Factors

### Multi-Embedding Score Normalization
The biggest technical risk is merging results from different embeddings with incompatible score distributions. This requires extensive testing and potentially machine learning approaches, not simple mathematical normalization.

### Embedding Quality Dependency  
90% of user value depends on chunking quality. Poor chunks = poor recommendations = user abandonment. Tree-sitter upgrade (Phase 7) is critical for long-term success.

### Token Cost Management
Multi-project context can easily generate 8000+ token queries. Without aggressive optimization, users will face $50+ monthly bills and churn.

---

## 📋 Implementation Phases

## Phase 1: Core Infrastructure

### 1.1 Project Setup
- [x] **1.1.1** Create Python project with pyproject.toml
- [x] **1.1.2** Setup development environment (venv, dependencies)
- [x] **1.1.3** Configure project structure (src/)
- [x] **1.1.4** Setup basic package metadata and entry points
- [x] **1.1.5** Initialize git repository with .gitignore
- [x] **1.1.6** Create Makefile with development commands
- [x] **1.1.7** Create basic README.md with installation instructions

### 1.2 CLI Foundation
- [x] **1.2.1** Setup argparse framework and command structure
- [x] **1.2.2** Create main CLI entry point (cli.py)
- [x] **1.2.3** Implement subcommand parser structure
- [x] **1.2.4** Add basic --help and --version support
- [x] **1.2.5** Setup logging configuration (debug, info, error levels)
- [x] **1.2.6** Implement basic error handling and user feedback

### 1.3 Configuration System
- [x] **1.3.1** Design configuration schema (JSON format)
- [x] **1.3.2** Implement config file location (~/.context-ai/config.json)
- [x] **1.3.3** Create settings management class
- [x] **1.3.4** Add active embedding tracking (active.json)
- [x] **1.3.5** Implement config validation and error handling
- [x] **1.3.6** Add config initialization on first run

### 1.4 Storage Foundation
- [x] **1.4.1** Design storage directory structure (~/.context-ai/)
- [x] **1.4.2** Implement storage path management
- [x] **1.4.3** Create metadata schema for embeddings
- [x] **1.4.4** Add storage directory initialization
- [x] **1.4.5** Add basic reset/cleanup commands

**Phase 1 Success Criteria:**
- ✅ CLI runs without errors
- ✅ Basic commands show help text
- ✅ Configuration system creates and manages config files
- ✅ Storage directories are properly initialized
- ✅ Logging works at different levels

---

## Phase 2: Embedding Generation

### 2.1 Text Processing Engine
- [x] **2.1.1** Install and configure langchain-text-splitters
- [x] **2.1.2** Create chunker protocol (interface comum)
- [x] **2.1.3** Implement LangChain adapter with language support
- [x] **2.1.4** Add basic metadata extraction (file type, language, chunk_index)
- [x] **2.1.5** Implement ignore file system (.contextignore/.gitignore support)  
- [x] **2.1.6** Add comprehensive language support (JS/TS, Python, CSS, JSON, YAML, MD)
- [x] **2.1.7** Add progress tracking for large repository processing

### 2.2 Embedding Model Integration
- [x] **2.2.1** Install sentence-transformers dependency
- [x] **2.2.2** Implement model loading and caching
- [x] **2.2.3** Use single model (all-MiniLM-L6-v2) for MVP
- [x] **2.2.4** Create embedding generation with batch processing
- [x] **2.2.5** Add basic model download progress indicators

### 2.3 ChromaDB Integration
- [x] **2.3.1** Install and configure ChromaDB
- [x] **2.3.2** Implement collection creation and management
- [x] **2.3.3** Add document and embedding storage
- [x] **2.3.4** Create basic metadata indexing

### 2.4 Generate Command Implementation
- [x] **2.4.1** Create generate-embedding command structure
- [x] **2.4.2** Add basic path validation and error handling
- [x] **2.4.3** Implement simple ignore file resolution
- [x] **2.4.4** Add basic file type detection and filtering
- [x] **2.4.5** Implement progress bars and status updates
- [x] **2.4.6** Add embedding naming system
- [x] **2.4.7** Create basic completion statistics

**Phase 2 Success Criteria:**
- ✅ Can generate embeddings from documentation directories
- ✅ Embeddings are stored in ChromaDB with proper metadata
- ✅ Progress tracking works for large document sets
- ✅ Generated embeddings can be named and managed
- ✅ Basic completion statistics are displayed

---

## Phase 3: Query and Selection System

### 3.1 Embedding Management
- [x] **3.1.1** Implement embedding listing functionality
- [x] **3.1.2** Create basic embedding metadata display (size, chunks, date)
- [x] **3.1.3** Add single embedding selection and activation system
- [x] **3.1.4** Implement multi-embedding selection interface
- [x] **3.1.5** Implement embedding deletion and cleanup

### 3.2 Query Engine Development
- [x] **3.2.1** Implement similarity search algorithm (single embedding)
- [x] **3.2.2** Add multi-embedding parallel query system
- [x] **3.2.3** Create cross-embedding result merging and ranking
- [x] **3.2.4** Implement source attribution and context balancing
- [x] **3.2.5** Add basic query preprocessing

### 3.3 Context Formatting
- [x] **3.3.1** Design AI-friendly output format
- [x] **3.3.2** Implement context chunk assembly
- [x] **3.3.3** Add source attribution and linking
- [x] **3.3.4** Implement basic context size limiting

### 3.4 Select Command Implementation
- [x] **3.4.1** Create basic selection interface
- [x] **3.4.2** Add embedding information display
- [x] **3.4.3** Implement active embedding switching
- [x] **3.4.4** Create selection validation and error handling

### 3.5 Query Command Implementation
- [x] **3.5.1** Create query command with context search processing
- [x] **3.5.2** Implement context retrieval and assembly
- [x] **3.5.3** Add output formatting for AI consumption
- [x] **3.5.4** Add basic debugging and verbose output modes

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
  - [x] **4.3.2.1** Basic Claude API key storage
  - [ ] **4.3.2.2** Key validation and connectivity testing
  - [x] **4.3.2.3** Simple configuration management
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

## 📈 Next Steps

For post-MVP enhancements and long-term roadmap, see [Future.md](./Future.md).

---

## 🎯 Success Criteria (MVP)

### Core Functionality
- ✅ Tool provides accurate answers about codebase patterns and architecture
- ✅ Cross-project queries return relevant context from multiple sources  
- ✅ Assistant naturally surfaces reusable components and helpers
- ✅ Response quality matches or exceeds single-project tools like Copilot Chat
- ✅ Multi-embedding result merging produces coherent, ranked outputs

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
- **Constants**: Use centralized constants files to eliminate code duplication
- **Configuration**: All magic numbers and default values in constants.py

### Core Development Principles
- **SOLID Principles**:
  - Single Responsibility: Each class/function has one clear purpose
  - Open/Closed: Open for extension, closed for modification
  - Liskov Substitution: Derived classes must be substitutable for base classes
  - Interface Segregation: Prefer specific interfaces over general ones
  - Dependency Inversion: Depend on abstractions, not concretions
- **DRY (Don't Repeat Yourself)**: Eliminate code duplication through constants, utilities, and abstractions
- **YAGNI (You Aren't Gonna Need It)**: Only implement what's required for current phase
- **Clean Code**: Self-documenting code with clear naming and simple logic
- **Clean Architecture**: Separation of concerns with clear boundaries between layers


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

### Code-Aware Chunking Examples (LangChain MVP)
```python
# TypeScript Component Chunking
chunk = {
    "text": "interface ButtonProps {\n  variant: 'primary' | 'secondary'\n  size: 'sm' | 'md' | 'lg'\n}\n\nexport const Button = ({ variant, size }: ButtonProps) => {\n  return <button className={`btn-${variant} btn-${size}`}>\n}",
    "metadata": {
        "file": "components/Button/Button.tsx",
        "language": "typescript",
        "chunk_index": 0,
        "chunker": "langchain"
    }
}

# Python Function Chunking  
chunk = {
    "text": "def useForm(schema: Dict[str, Any]) -> FormState:\n    \"\"\"Custom hook for form management\"\"\"\n    state = FormState(schema)\n    return state",
    "metadata": {
        "file": "hooks/useForm.py",
        "language": "python",
        "chunk_index": 0,
        "chunker": "langchain"
    }
}

# Documentation Chunking
chunk = {
    "text": "## Button Component\n\nThe Button component provides consistent styling and behavior.\n\n### Props\n- variant: 'primary' | 'secondary'\n- size: 'sm' | 'md' | 'lg'",
    "metadata": {
        "file": "docs/Button.md",
        "language": "markdown",
        "chunk_index": 0,
        "chunker": "langchain"
    }
}
```

### Usage Examples (MVP)
```bash
# Generate embeddings for different projects
context-ai generate ./my-design-system --name "design-system-v1"
context-ai generate ./current-project --name "project-main-v2"
context-ai generate ./helpers-lib --name "helpers-v1"

# Configure Claude API key
context-ai config set --claude-key sk-ant-xxxxxxxxxxxx

# Multi-project selection
context-ai select design-system-v1,project-main-v2,helpers-v1

# General code assistance with cross-project intelligence
context-ai ask "How do I implement user authentication in our app?"
context-ai ask "What's the standard way to handle form validation?"
context-ai ask "How should I structure a new dashboard page?"

# Component and helper discovery  
context-ai ask "Do we have existing components for file uploads?"
context-ai ask "What date formatting utilities are available?"
context-ai ask "Show me modal implementations across projects"

# Architecture and pattern guidance
context-ai ask "What's our API calling convention?"
context-ai ask "How do we handle error boundaries in React?"
context-ai ask "What's the preferred state management approach?"

# Interactive problem-solving
context-ai chat
> "I need to build a user profile page"
> "I found 3 similar pages in your codebase. The UserSettings component would be a great starting point..."
> "Can you show me how to integrate the design system components?"
> "Sure! Here's how to use the Card and Form components from your design system..."
```

### AI Configuration Schema (MVP - Claude Only)
```json
{
  "claude_api_key": "sk-ant-xxxxxxxxxxxx",
  "default_model": "claude-3-sonnet",
  "max_tokens": 4000,
  "system_prompt_strategy": "general_assistant_with_reusability_focus",
  "context_assembly": {
    "max_chunks": 8,
    "prioritize_cross_project": true,
    "include_metadata": true
  }
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
