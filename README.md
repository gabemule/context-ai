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

#### Quick Setup (Recommended)
```bash
git clone https://github.com/gabemule/context-ai
cd context-ai
./dev-install.sh  # 🚀 Smart installer - auto-detects and removes conflicts
```

**Smart Installation Features:**
- 🔍 **Conflict Detection**: Automatically finds conflicting editable packages (like codex-ai)
- 🧹 **Clean Removal**: Uninstalls conflicts before installation
- ✅ **Verification**: Tests that context-ai command works properly
- 📊 **Smart Reporting**: Shows what was removed and installed

#### Manual Setup (Alternative)
```bash
git clone https://github.com/gabemule/context-ai
cd context-ai
make setup
source venv/bin/activate
make install-dev
```

**Note**: If you get `ModuleNotFoundError` or conflicts with other local AI packages, the smart installer (`./dev-install.sh`) will resolve them automatically.

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

### 🎛️ Prompt Modes - Complete Guide

Control the depth and analysis level of AI responses. Each mode serves different development scenarios:

#### ⚡ `minimal` - Speed First
**Perfect for**: Quick lookups, simple questions, when you just need facts
- **Processing**: Basic context + question only (fastest)
- **Instructions sent**: Simple prompt with no extra analysis
- **Guidelines**: None applied
- **Cross-project**: Basic mention only
- **Response time**: ~2-3 seconds

**Actual prompt sent to Claude**:
```
Based on the following context from the codebase, please answer the question.

## Context: [your context]
## Question: [your question]
```

```bash
context-ai ask "Do we have a Button component?" --prompt-mode minimal
```

**Example Response**:
```
Yes, found Button component in design-system-v1/components/Button.tsx
```

---

#### 🎯 `standard` - Daily Development (Default)
**Perfect for**: Regular development work, moderate complexity questions
- **Processing**: Cross-project awareness + auto-detected coding guidelines
- **Instructions sent**: Conditional cross-project hints + guidelines when detected
- **Guidelines**: JS/TS guidelines only when JS/TS files detected in context
- **Cross-project**: Only activated when multiple projects detected in context
- **Response time**: ~4-6 seconds

**Actual prompt additions**:
- **Cross-project detection**: If context contains `"Cross-Project Analysis"` → adds: *"Note: This context contains code from multiple projects - consider comparing approaches when relevant."*
- **Guidelines detection**: If JS/TS files found → adds full SOLID/DRY/YAGNI guidelines + *"When providing code examples or suggestions, please follow the above guidelines."*

```bash
context-ai ask "How should I implement form validation?" --prompt-mode standard
# Or simply: context-ai ask "How should I implement form validation?"
```

**Example Response**:
```
For form validation, use the ValidationSchema from utils-v2 which follows our established patterns:

```typescript
const loginSchema = ValidationSchema({
  email: [required(), isEmail()],
  password: [required(), minLength(8)]
});
```

This approach maintains consistency with your existing forms in project-main-v2 
and follows the functional programming patterns from your JS/TS guidelines.
```

---

#### 🧠 `comprehensive` - Deep Analysis
**Perfect for**: Architecture decisions, complex comparisons, learning existing patterns
- **Processing**: Full cross-project analysis + architectural insights
- **Instructions sent**: Detailed 7-point analysis framework + guidelines + architectural reasoning
- **Guidelines**: Applied with architectural explanations
- **Cross-project**: Always detailed when multiple projects detected
- **Response time**: ~8-12 seconds

**Actual prompt additions**:
When multiple projects detected, adds **CROSS-PROJECT ANALYSIS** with these specific instructions:
- Compare implementations across different projects
- Highlight similarities and differences between approaches  
- Identify reusable patterns or components
- Suggest opportunities for standardization or consistency improvements
- Point out which project has the most robust/complete implementation
- Consider architectural differences and their implications
- Recommend best practices based on the patterns observed

Plus: *"Please provide a comprehensive answer with architectural insights and best practices recommendations."*

```bash
context-ai ask "How should I structure user authentication?" --prompt-mode comprehensive
```

**Example Response**:
```
## Cross-Project Authentication Analysis

I found 3 different authentication approaches across your projects:

### 🔍 **Current Implementations**

**design-system-v1** (⭐ Most Robust):
- JWT-based authentication with refresh tokens
- Centralized auth context with React hooks
- Proper error boundaries and loading states
- TypeScript interfaces for all auth types

**backend-v2** (Simple but Effective):
- Session-based authentication
- Express middleware pattern
- Basic error handling

**legacy-v1** (⚠️ Needs Migration):
- Basic auth with hardcoded tokens
- No proper error handling
- Security vulnerabilities

### 🏗️ **Recommended Architecture**

Follow the design-system-v1 pattern because:
1. **Security**: Implements JWT best practices with refresh tokens
2. **TypeScript**: Full type safety for auth flows  
3. **UX**: Proper loading states and error handling
4. **Testability**: Pure functions and clear separation of concerns

### 📋 **Implementation Plan**

1. Create unified AuthContext from design-system-v1
2. Extract reusable auth hooks
3. Implement token refresh mechanism
4. Add proper TypeScript interfaces
5. Migrate legacy-v1 gradually

**Code Example**: [Shows complete implementation with explanations]
```

---

#### 🔍 `strict` - Code Review Mode
**Perfect for**: Code generation, refactoring, enforcing team standards
- **Processing**: Rigorous guideline enforcement + detailed code analysis
- **Instructions sent**: Code review framework + forced guidelines + strict enforcement
- **Guidelines**: **Always applied** with `force=True` - detects languages and enforces standards
- **Cross-project**: Code quality comparison with specific review criteria
- **Response time**: ~10-15 seconds

**Actual prompt additions**:
Base instruction: *"Based on the following context from the codebase, please answer the question **with a focus on code quality and best practices**."*

When multiple projects detected, adds **CODE REVIEW APPROACH**:
- Code quality and maintainability differences
- Performance implications of different approaches
- Security considerations
- Testing strategies
- Documentation quality

**Guidelines enforcement**: Uses `force=True` to detect languages and apply guidelines even when not auto-detected, plus: *"**STRICT ENFORCEMENT**: All code suggestions must strictly adhere to the above guidelines. Review existing code for violations and suggest improvements."*

Final instruction: *"Provide a detailed answer with code review insights, strict adherence to guidelines, and actionable improvement recommendations."*

```bash
context-ai ask "Review my authentication implementation" --prompt-mode strict
```

**Example Response**:
```
## 🔍 Code Review Analysis

### ❌ **Issues Found**

**Guideline Violations**:
- Using class components instead of functional (violates modern JS/TS practices)
- Mixing authentication logic with UI components (violates SOLID principles)
- Hardcoded API endpoints (violates DRY principle)
- Missing error boundaries (violates YAGNI - should implement error handling)

**Cross-Project Inconsistencies**:
- Different error handling patterns vs design-system-v1
- Missing TypeScript interfaces that exist in other projects
- Not using established hooks pattern from utils-v2

### ✅ **Recommended Refactor**

```typescript
// ❌ Current (violates guidelines)
class LoginForm extends React.Component {
  handleSubmit = () => {
    fetch('http://localhost:3000/login', {...})  // hardcoded
    // no error handling
  }
}

// ✅ Improved (follows all guidelines)
const LoginForm: React.FC<LoginProps> = ({ onSubmit }) => {
  const { login, loading, error } = useAuth(); // reuse existing hook
  
  const handleSubmit = useCallback(async (data: LoginData) => {
    try {
      await login(data); // proper error handling
      onSubmit?.(); // optional chaining
    } catch (err) {
      // error boundary will handle
    }
  }, [login, onSubmit]);

  return (
    <Form onSubmit={handleSubmit} loading={loading}>
      <ErrorBoundary error={error} />
      {/* Use design system components */}
    </Form>
  );
};
```

### 📋 **Action Items**
1. Extract auth logic to custom hook (follow useAuth pattern)
2. Add TypeScript interfaces (copy from design-system-v1)
3. Implement error boundaries consistently
4. Use environment variables for API endpoints
5. Add unit tests (follow existing test patterns)

**Estimated refactor time**: 2-3 hours
**Priority**: High (security implications)
```

---

### 📊 **Quick Reference**

| Use Case | Recommended Mode | Why |
|----------|------------------|-----|
| "Do we have component X?" | `minimal` | Quick fact lookup |
| "How to implement feature Y?" | `standard` | Needs context + guidelines |  
| "What's our auth architecture?" | `comprehensive` | Needs full project analysis |
| "Review my code implementation" | `strict` | Needs rigorous standards enforcement |
| Daily coding questions | `standard` | Balanced speed + quality |
| Architecture planning | `comprehensive` | Needs deep insights |
| Code generation | `strict` | Needs perfect standards compliance |

### ⚙️ **Usage Examples**

```bash
# Quick lookups (minimal)
context-ai ask "Where is the API endpoint defined?" --prompt-mode minimal

# Daily development (standard - default)
context-ai ask "How to add error handling to this form?"
context-ai ask "What's the pattern for API calls?" --prompt-mode standard

# Architecture decisions (comprehensive)  
context-ai ask "Should I use Redux or Context API?" --prompt-mode comprehensive
context-ai ask "How to structure this new microservice?" --prompt-mode comprehensive

# Code review and generation (strict)
context-ai ask "Generate a user profile component" --prompt-mode strict
context-ai ask "Review this authentication flow" --prompt-mode strict

# Chat sessions maintain mode throughout conversation
context-ai chat --prompt-mode comprehensive  # All responses will be comprehensive
context-ai chat --prompt-mode strict         # All responses will enforce strict standards
```

**💡 Pro Tip**: Start with `standard` mode for daily work, use `comprehensive` for learning your codebase, and `strict` when generating new code or doing refactoring.

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
