# Context-AI Documentation

> Complete technical documentation for Context-AI - Cross-project code intelligence assistant

## 📚 Documentation Index

### **Architecture & Design**
- **[Context Window Management](architecture/context-window-management.md)** - How Context-AI manages Claude's 200K token context window
- **[Prompt Modes Architecture](architecture/prompt-modes.md)** - Design and implementation of the four prompt modes

### **Command References**
- **[Chat Command](commands/chat.md)** - Start interactive chat sessions with AI
- **[Ask Command](commands/ask.md)** - Ask AI-powered questions with codebase context
- **[Query Command](commands/query.md)** - Search embeddings for relevant context
- **[Generate Command](commands/generate.md)** - Generate embeddings from project directories
- **[Select Command](commands/select.md)** - Select active embeddings for queries
- **[Config Command](commands/config.md)** - Manage configuration settings
- **[Storage Command](commands/storage.md)** - Manage storage and cleanup operations

### **Quick Navigation**

| Topic | Document | Description |
|-------|----------|-------------|
| 🧠 **Token Management** | [architecture/context-window-management.md](architecture/context-window-management.md) | Dynamic allocation, history truncation, performance tuning |
| 🎛️ **Prompt Modes** | [architecture/prompt-modes.md](architecture/prompt-modes.md) | Architecture of minimal, standard, comprehensive, strict modes |
| 💬 **Chat Sessions** | [commands/chat.md](commands/chat.md) | Interactive sessions, special commands, prompt modes |
| 🤖 **AI Questions** | [commands/ask.md](commands/ask.md) | Prompt modes, output options, integration workflows |
| 🔍 **Query Context** | [commands/query.md](commands/query.md) | Search syntax, output formats, performance tuning |
| 📦 **Generate Embeddings** | [commands/generate.md](commands/generate.md) | Complete syntax, file processing, ignore patterns |
| 🎯 **Select Context** | [commands/select.md](commands/select.md) | Interactive selection, direct CLI, state management |
| ⚙️ **Configuration** | [commands/config.md](commands/config.md) | API keys, validation, troubleshooting |
| 💾 **Storage Management** | [commands/storage.md](commands/storage.md) | Cleanup, deletion, reset operations |

## 🎯 Key Topics Covered

### Context Window Management
- **200K Token Allocation**: How tokens are distributed between context (65%) and response (35%)
- **Chat History Management**: Intelligent truncation preserving recent conversations
- **Dynamic Reallocation**: Automatic adjustment based on context size and conversation length
- **Performance Optimization**: Caching strategies and response time characteristics
- **Real-World Scenarios**: Examples from normal usage to edge cases
- **Developer Configuration**: How to customize token limits and behavior

### Chat Commands & Usage
- **Special Commands**: `/history`, `/clear`, `/verbose`, `exit` and their functions
- **Prompt Modes**: Detailed explanation of minimal, standard, comprehensive, and strict modes
- **Verbose Mode**: Understanding detailed token allocation and performance metrics
- **Session Management**: Best practices for long conversations
- **Error Handling**: Common issues and solutions
- **Performance Tips**: Optimizing chat sessions for different use cases

## 🚀 Getting Started

### **New Users**
1. Start with the main [README.md](../README.md) for installation and basic usage
2. Review [Chat Command Reference](commands/chat.md) for interactive features
3. Check [Context Window Management](architecture/context-window-management.md) if you're curious about the internals

### **Power Users**
1. Read [Context Window Management](architecture/context-window-management.md) for deep technical understanding
2. Use [Chat Command Reference](commands/chat.md) as a reference for advanced features
3. Experiment with different configurations mentioned in the docs

### **Developers**
1. Study [Context Window Management](architecture/context-window-management.md) for system architecture
2. Reference the configuration sections for customization options
3. Use the troubleshooting sections for debugging

## 🔧 Configuration Files Referenced

The documentation references these key files:
- `src/config/constants.py` - Token limits and system constants
- `src/services/ai_service.py` - Chat history management and token allocation
- `src/commands/chat.py` - Chat command implementation
- `src/core/ai/claude_client.py` - Claude API integration and prompt building

## 📊 System Overview

```
Context-AI Architecture (Token Management)
├── Claude-4 Context Window (200K tokens)
│   ├── Context Allocation (65% = 130K tokens)
│   │   ├── Chat History (~30% = 39K tokens)
│   │   └── Code Context (~70% = 91K tokens)
│   └── Response Space (35% = 70K tokens)
├── ChatHistoryManager
│   ├── Intelligent Truncation
│   ├── Turn Preservation (min 3 recent)
│   └── Token Budget Management
└── Dynamic Reallocation
    ├── Context Caching (5min TTL)
    ├── Performance Optimization
    └── Seamless User Experience
```

## 🎯 Key Features Documented

### **Automatic Token Management**
- ✅ No manual intervention required
- ✅ Seamless conversation continuation
- ✅ Intelligent history preservation
- ✅ Performance optimization

### **Chat Session Features**
- ✅ Persistent conversation history
- ✅ Special commands for control
- ✅ Multiple prompt modes
- ✅ Verbose monitoring capabilities

### **Developer Flexibility**
- ✅ Configurable token ratios
- ✅ Customizable preservation rules
- ✅ Performance tuning options
- ✅ Debug and monitoring tools

## 🔍 Common Use Cases

### **Daily Development**
```bash
context-ai chat --prompt-mode standard
# Standard mode with automatic guidelines
```

### **Architecture Planning**
```bash
context-ai chat --prompt-mode comprehensive --verbose
# Deep analysis with token monitoring
```

### **Code Review Sessions**
```bash
context-ai chat --prompt-mode strict
# Enforced standards and detailed feedback
```

### **Quick Questions**
```bash
context-ai chat --prompt-mode minimal
# Fast responses for simple queries
```

## 📈 Performance Characteristics

| Context Size | Response Time | Memory Usage | Best Mode |
|--------------|---------------|--------------|-----------|
| <50K tokens  | ~3-5 seconds  | <30MB       | Any       |
| 50-100K tokens | ~8-12 seconds | <40MB     | Standard+ |
| 100K+ tokens | ~15-20 seconds | <50MB      | Minimal   |

## 🚨 Important Notes

### **Token Limits**
- The system **never breaks** due to token limits
- Recent conversation history is **always preserved**
- Code context quality is **maintained** through intelligent allocation

### **Performance**
- Response times scale with context size
- Caching improves performance for repeated queries
- Verbose mode provides detailed performance insights

### **Customization**
- All token ratios are configurable
- Multiple optimization strategies available
- Developer-friendly debugging tools included

## 💡 Pro Tips

1. **Use verbose mode** to understand system behavior
2. **Monitor `/history`** in long chat sessions
3. **Choose appropriate prompt modes** for your task
4. **Clear history** when switching topics completely
5. **Combine with `context-ai select`** for optimal context

---

*This documentation covers the complete Context-AI system from user features to deep technical implementation. The system is designed to be both powerful for advanced users and transparent for those who just want it to work.*

## 📝 Contributing to Documentation

Found an issue or want to improve the docs? 
1. Check the main [Plan.md](../Plan.md) for development status
2. Review the [Future.md](../Future.md) for planned enhancements
3. Submit issues and suggestions via GitHub
