# Context-AI

> Cross-project code intelligence assistant

Transform your codebase into an intelligent assistant that provides cross-project context, discovers reusable components, and guides architectural decisions.

## 🎯 Overview

- **🧠 Cross-project intelligence** - Advanced correlation analysis across multiple repositories
- **🔍 Component discovery** - Find existing components before building new ones
- **📋 Pattern discovery** - Learn established patterns with cross-project comparison
- **🏗️ Architecture guidance** - Get context-aware architectural recommendations
- **🤖 AI-powered insights** - Powered by Claude with enhanced prompts
- **⚡ Smart token management** - Dynamic context sizing (up to 200K tokens)
- **📊 Multiple output formats** - JSON, XML, Markdown, Plain text
- **🎛️ Configurable prompt modes** - From minimal to comprehensive analysis
- **📐 Built-in coding guidelines** - JavaScript/TypeScript best practices

## 🚀 Installation

### For End Users (Simplest) 🏆
```bash
# Install globally with pipx (cleanest option)
pipx install git+https://github.com/gabemule/context-ai.git

# Now available everywhere:
context-ai --version
context-ai generate ./my-project --name "v1"
```

**What pipx does:**
- 🌍 **Command available globally** - use from any terminal
- 🔒 **Isolated dependencies** - doesn't pollute your global Python
- 🧹 **Clean environment** - best of both worlds!

### For Developers (Contributing & Development)
```bash
# Clone and run the smart installer  
git clone https://github.com/gabemule/context-ai
cd context-ai
source dev-install.sh  # 🎯 Creates venv + installs + activates everything automatically
```

**What the smart installer does:**
- 🔍 **Auto-detects environment**: Checks if you're in a venv
- 📦 **Creates venv automatically**: `python -m venv venv` if needed
- ⚡ **Activates venv**: Keeps it active in your current shell (when using `source`)
- 🧹 **Removes conflicts**: Uninstalls conflicting packages automatically
- ✅ **Installs project**: Development mode with all dependencies
- 🧪 **Tests installation**: Verifies everything works

#### 🛠️ Development Commands (Makefile)
```bash
# Setup & Installation
make setup          # Complete development setup (venv + deps)
make install        # Install production dependencies  
make install-dev    # Install development dependencies
make clean          # Clean build artifacts and cache

# Development & Testing
make test           # Run all tests
make test-watch     # Run tests in watch mode
make dev           # Complete development checks (format + lint + test)

# Code Quality
make format         # Auto-format code (black, isort, autoflake)
make lint          # Run linting (flake8, mypy)
make type-check    # Run type checking (mypy)

# Build & Release
make build         # Build package for distribution
make test-publish  # Publish to TestPyPI (alpha testing)
make publish       # Publish to PyPI (production)
make test-install  # Install from TestPyPI for testing
make test-uninstall # Remove test installation
make verify-install # Verify installation works

# Quick workflows
make format lint test    # Pre-commit checks
make dev                # Full development cycle
make test-publish && make test-install && make verify-install  # Test release cycle
```


### Manual Setup (Full Control)

#### Option A: pipx editable (Recommended for local development) 🏆
```bash  
git clone https://github.com/gabemule/context-ai
cd context-ai
pipx install -e .  # Global command + live code changes
```

**What this gives you:**
- 🌍 **Global command**: `context-ai` works from anywhere
- 🔧 **Live editing**: Code changes reflect immediately
- 🧹 **Clean environment**: Dependencies isolated in pipx venv
- 💨 **No activation needed**: Just use the command!

#### Option B: Traditional venv
```bash
git clone https://github.com/gabemule/context-ai
cd context-ai

# Always use venv to avoid conflicts with other Python projects
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

pip install -e ".[dev]"
```

### Installing pipx (if you don't have it)
```bash
python -m pip install --user pipx
python -m pipx ensurepath
# Restart your terminal or run: source ~/.bashrc (or ~/.zshrc)
```

💡 **Which option to choose?**
- **End User**: Just want to use context-ai → Use pipx
- **Developer**: Want to contribute or modify → Use dev-install.sh  
- **Advanced**: Need full control → Manual setup

### Verify Installation
```bash
context-ai --version
context-ai --help
```

## 🔧 Managing Your Installation

### Check what's installed
```bash
pipx list  # Shows all pipx applications
pip show context-ai  # For venv installations
```

### Update after code changes
```bash
# pipx automatically detects changes in editable installs
# But if something seems wrong:
pipx reinstall context-ai

# For venv installations:
pip install -e . --force-reinstall
```

### Uninstall
```bash
# Remove context-ai from pipx
pipx uninstall context-ai

# Remove from venv
pip uninstall context-ai
```

### Switch installation methods
```bash
# From pipx to venv
pipx uninstall context-ai
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"

# From venv to pipx  
deactivate && rm -rf venv
pipx install -e .
```

### Troubleshooting
```bash
# Context-AI command not found after pipx install
pipx ensurepath
source ~/.bashrc  # or ~/.zshrc

# Development tools not working with pipx
source dev-install.sh  # Use venv for development
```

## ⚡ Quick Start

```bash
# 1. Generate embeddings for your projects
context-ai generate ./my-design-system --name "design-system-v1"
context-ai generate ./current-project --name "project-main-v2"

# 2. Select active embeddings
context-ai select  # Interactive checkbox interface

# 3. Query for context
context-ai query "authentication patterns" --verbose

# 4. Ask AI-powered questions
context-ai ask "Do we have existing components for file uploads?"

# 5. Interactive chat mode
context-ai chat
```

## 📋 Commands Overview

| Command | Purpose | Quick Example |
|---------|---------|---------------|
| **[`generate`](docs/commands/generate.md)** | Create embeddings from projects | `context-ai generate ./my-project --name "v1"` |
| **[`select`](docs/commands/select.md)** | Choose active embeddings | `context-ai select` (interactive) |
| **[`query`](docs/commands/query.md)** | Search for context | `context-ai query "auth patterns" --format json` |
| **[`ask`](docs/commands/ask.md)** | AI Q&A with context | `context-ai ask "How to implement login?"` |
| **[`chat`](docs/commands/chat.md)** | Interactive AI session | `context-ai chat --prompt-mode comprehensive` |
| **[`config`](docs/commands/config.md)** | Manage settings | `context-ai config set --claude-key sk-ant-xxx` |
| **[`storage`](docs/commands/storage.md)** | Manage data | `context-ai storage info` |

## 🎛️ Prompt Modes

Control the depth of AI analysis:

| Mode | Speed | Use Case | Description |
|------|-------|----------|-------------|
| `minimal` | ⚡ Fastest | Quick lookups | Basic context + question only |
| `standard` | 🎯 Balanced | Daily development | Context + guidelines (default) |
| `comprehensive` | 🧠 Detailed | Architecture planning | Full cross-project analysis |
| `strict` | 🔍 Thorough | Code review | Enforced coding standards |

```bash
# Examples
context-ai ask "Where is Button component?" --prompt-mode minimal
context-ai ask "How to implement auth?" --prompt-mode comprehensive
context-ai chat --prompt-mode strict  # For code generation sessions
```

## 🔧 Configuration

Set up your Claude API key:
```bash
context-ai config set --claude-key sk-ant-xxxxxxxxxxxx
context-ai config test  # Verify connection
```

## 💡 Example Workflows

### Component Discovery
```bash
context-ai ask "Do we have a modal component I can reuse?"
# → Finds Modal components across all your projects with usage examples
```

### Architecture Guidance  
```bash
context-ai ask "How should I structure a new dashboard page?" --prompt-mode comprehensive
# → Shows existing dashboard patterns and architectural recommendations
```

### Code Review Session
```bash
context-ai chat --prompt-mode strict
# Interactive session with enforced coding standards for all responses
```

## 📚 Complete Documentation

For detailed information, see our comprehensive documentation:

### **🚀 Getting Started Guide**
New to Context-AI? Check the [complete documentation index](docs/README.md) for guided learning paths.

### **📖 Command References** 
- **[Generate Command](docs/commands/generate.md)** - Embedding creation, ignore patterns, processing
- **[Select Command](docs/commands/select.md)** - Interactive selection, CLI usage, state management
- **[Query Command](docs/commands/query.md)** - Search syntax, formats, performance tuning
- **[Ask Command](docs/commands/ask.md)** - AI questions with prompt modes and output options
- **[Chat Command](docs/commands/chat.md)** - Interactive sessions, special commands, history management
- **[Config Command](docs/commands/config.md)** - API setup, validation, troubleshooting
- **[Storage Command](docs/commands/storage.md)** - Data management, cleanup, operations

### **🏗️ Architecture**
- **[Context Window Management](docs/architecture/context-window-management.md)** - How Context-AI manages Claude's 200K token context
- **[Prompt Modes Architecture](docs/architecture/prompt-modes.md)** - Deep dive into the four prompt modes
- **[Similarity Scoring System](docs/architecture/similarity-scoring.md)** - Multi-embedding ranking algorithms

## 🏗️ Built With

Context-AI is built on top of cutting-edge technologies:

### **🧠 AI & Embeddings**
- **[Anthropic Claude](https://www.anthropic.com/)** - Advanced AI for code analysis and Q&A
- **[sentence-transformers](https://www.sbert.net/)** - State-of-the-art text embeddings
- **[tiktoken](https://github.com/openai/tiktoken)** - Efficient token counting and management

### **🗄️ Vector Storage & Processing**
- **[ChromaDB](https://www.trychroma.com/)** - High-performance vector database
- **[LangChain Text Splitters](https://python.langchain.com/)** - Intelligent text chunking algorithms

### **🛠️ Development & CLI**
- **[Rich](https://rich.readthedocs.io/)** - Beautiful terminal interfaces and formatting
- **[Inquirer](https://github.com/magmax/python-inquirer)** - Interactive CLI prompts
- **[Pydantic](https://pydantic.dev/)** - Data validation and settings management
- **[argparse](https://docs.python.org/3/library/argparse.html)** - Built-in command-line interface framework

### **🧪 Code Quality & Testing**
- **[pytest](https://pytest.org/)** - Testing framework
- **[Black](https://black.readthedocs.io/)** - Code formatting
- **[flake8](https://flake8.pycqa.org/)** - Linting and style checking
- **[mypy](https://mypy.readthedocs.io/)** - Static type checking
- **[isort](https://pep8.readthedocs.io/en/release-1.7.x/intro.html)** - Import sorting

### **⚡ Performance & Utilities**
- **[pathspec](https://pathspec.readthedocs.io/)** - Gitignore-style pattern matching
- **[pyperclip](https://pyperclip.readthedocs.io/)** - Cross-platform clipboard operations

**Why these choices?**
- 🎯 **Best-in-class**: Each technology is a leader in its domain
- 🔄 **Interoperability**: Designed to work seamlessly together
- 📈 **Scalability**: Can handle large codebases efficiently
- 🛡️ **Reliability**: Battle-tested in production environments

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
