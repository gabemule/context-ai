# Context-AI

> Cross-project code intelligence assistant

Transform your codebase into an intelligent assistant that provides cross-project context, discovers reusable components, and guides architectural decisions.

## 🚀 Quick Start

```bash
# Install
pip install context-ai

# Generate embeddings for your projects
context-ai generate ./my-design-system --name "design-system-v1"
context-ai generate ./current-project --name "project-main-v2"

# Interactive embedding selection
context-ai select
# → Opens checkbox interface to select active embeddings

# Ask questions with cross-project intelligence
context-ai ask "Do we have existing components for file uploads?"
context-ai ask "What's our standard approach for API error handling?"

# Interactive chat mode
context-ai chat
```

## 🎯 Key Features

- **Cross-project intelligence** - Understand relationships across multiple repositories
- **Component reusability** - Discover existing components before building new ones
- **Pattern discovery** - Learn established patterns and conventions
- **Architecture guidance** - Get context-aware architectural recommendations
- **Interactive selection** - Checkbox interface for choosing active embeddings
- **AI-powered insights** - Powered by Claude for intelligent responses

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

- `generate` - Generate embeddings from a project directory
- `select` - **Interactive checkbox selection** of active embeddings
- `query` - Query embeddings for raw context
- `ask` - Ask questions and get AI-powered answers
- `chat` - Interactive chat session
- `config` - Manage configuration

### Interactive Selection

The `select` command opens an interactive checkbox interface:

```bash
context-ai select

🎯 Select active embeddings for queries

[?] Select embeddings to query (use space to select/deselect, enter to confirm):
 > [x] design-system-v1 (1.2M tokens, 3 days ago)
   [x] project-main-v2 (800K tokens, 1 day ago) 
   [ ] api-docs-v1 (300K tokens, 1 week ago)
   [ ] helpers-lib-v1 (150K tokens, 2 days ago)

✅ Selected embeddings: design-system-v1, project-main-v2
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `make dev` to ensure quality checks pass
5. Create a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🛠️ Status

**Alpha** - Core infrastructure implemented, embedding generation in progress.

See [Plan.md](Plan.md) for detailed development roadmap.