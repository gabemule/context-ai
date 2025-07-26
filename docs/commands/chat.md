# Chat Command Reference

> Complete documentation for the `context-ai chat` command - Start interactive chat sessions with AI

## 🎯 Overview

The `chat` command starts an interactive AI chat session with Claude using context from your active embeddings. It maintains conversation history throughout the session, provides special commands for control, and supports different prompt modes for various use cases.

## 📋 Complete Syntax

```bash
context-ai chat [OPTIONS]
```

## 📝 Arguments

### **No Positional Arguments**
The chat command takes no positional arguments and starts an interactive session.

### **Optional Arguments**

#### `--prompt-mode` / `-pm`
- **Type**: Choice from predefined list
- **Required**: No
- **Default**: Uses system default (typically `standard`)
- **Choices**: `["minimal", "standard", "comprehensive", "strict"]`
- **Description**: Set prompt mode for the entire chat session
- **Effect**: All questions in the session use the selected mode
- **Examples**:
  - `--prompt-mode comprehensive`
  - `-pm strict`

### **Optional Flags**

#### `--verbose` / `-v`
- **Type**: Boolean flag
- **Required**: No
- **Default**: False
- **Description**: Show detailed processing information including token usage
- **Effect**: Enables debug logging and performance metrics for all interactions

## 🚀 Usage Examples

### **Basic Usage**
```bash
# Start basic chat session
context-ai chat
```

### **Prompt Mode Variations**
```bash
# Minimal mode - fast responses
context-ai chat --prompt-mode minimal

# Standard mode (default)
context-ai chat --prompt-mode standard

# Comprehensive mode - deep analysis
context-ai chat --prompt-mode comprehensive

# Strict mode - enforced guidelines
context-ai chat --prompt-mode strict
```

### **Information Levels**
```bash
# Basic chat
context-ai chat

# Chat with verbose token information
context-ai chat --verbose

# Comprehensive analysis with verbose
context-ai chat --prompt-mode comprehensive --verbose
```

### **All Flag Combinations**

#### **1. Basic chat session**
```bash
context-ai chat
```

#### **2. Verbose session**
```bash
context-ai chat --verbose
```

#### **3. Minimal mode for speed**
```bash
context-ai chat --prompt-mode minimal
```

#### **4. Comprehensive with verbose**
```bash
context-ai chat --prompt-mode comprehensive --verbose
```

#### **5. Strict mode with verbose**
```bash
context-ai chat --prompt-mode strict --verbose
```

### **Real-World Examples**

#### **Development Sessions**
```bash
# Quick development help
context-ai chat --prompt-mode minimal

# Regular development session
context-ai chat --prompt-mode standard --verbose

# Architecture planning session
context-ai chat --prompt-mode comprehensive --verbose
```

#### **Code Review Sessions**
```bash
# Detailed code review with guidelines
context-ai chat --prompt-mode strict --verbose
```

## 💬 Special Commands

During a chat session, you can use these special commands:

### **`/history` - Show Conversation Statistics**
```
You: /history
💬 Chat History: 8 turns, 45,230 total tokens, avg 5,654 tokens/turn
```

**What it shows:**
- Total number of conversation turns
- Total tokens used across all turns
- Average tokens per turn
- Useful for monitoring memory usage

### **`/clear` - Reset Chat History**
```
You: /clear
🗑️ Chat history cleared
```

**What it does:**
- Removes all previous conversation turns
- Frees up token space for new conversations
- Context from embeddings remains available
- Cannot be undone

### **`/verbose` - Toggle Verbose Mode**
```
You: /verbose
🔧 Verbose mode enabled

You: /verbose  
🔧 Verbose mode disabled
```

**Verbose mode shows:**
- Detailed token allocation breakdown
- Context retrieval timing
- Claude API response metrics
- Performance diagnostics

### **`exit`, `quit`, `bye` - End Chat Session**
```
You: exit
📊 Session stats: 8 turns, 45,230 total tokens
Goodbye! 👋
```

**What happens:**
- Shows final session statistics
- Gracefully closes the chat
- Saves conversation data for analysis

## 🎛️ Prompt Mode Details

### **Minimal Mode** ⚡
- **Speed**: ~2-3 seconds per response
- **Features**: Basic code context only
- **Guidelines**: None applied
- **Best for**: Quick factual questions
- **Token usage**: Lowest (~20-40K tokens)

### **Standard Mode** 🎯 (Default)
- **Speed**: ~4-6 seconds per response  
- **Features**: Cross-project hints when detected
- **Guidelines**: JS/TS guidelines when applicable
- **Best for**: Regular development questions
- **Token usage**: Moderate (~40-80K tokens)

### **Comprehensive Mode** 🧠
- **Speed**: ~8-12 seconds per response
- **Features**: Full cross-project analysis with 7-point framework
- **Guidelines**: Applied with architectural reasoning
- **Best for**: Architecture decisions, complex comparisons
- **Token usage**: High (~80-120K tokens)

### **Strict Mode** 🔍
- **Speed**: ~10-15 seconds per response
- **Features**: Detailed code review approach
- **Guidelines**: Strict enforcement with violation detection
- **Best for**: Code generation, refactoring, standards enforcement
- **Token usage**: Highest (~100-150K tokens)

## 📊 Output Examples

### **Session Startup**
```bash
$ context-ai chat --prompt-mode comprehensive --verbose

🤖 Claude Chat Session with History (Verbose)

Ask questions about your codebase. Chat history will be maintained for context.
Special commands: /history (stats), /clear (reset), /verbose (toggle), 'exit' (quit)

You: 
```

### **Verbose Mode Output**
```
You: How should I implement user authentication?
🔍 Retrieving context from active embeddings...
🔄 Generating fresh context...
📊 Context limit: 130,000 tokens (65% of 200,000)
📊 Allocation: 91,000 code + 0 history = 91,000 total context
📊 Input tokens: 52,340 (context: 51,100, question: 1,240)
📊 Dynamic response tokens: 8,000
🧠 Asking Claude (51,100 chars, max 8,000 tokens)...
✅ Response received in 6.2s (7,234 tokens)

[Claude's detailed authentication analysis]

📊 Token Usage Details:
  Context: 51,100 tokens (25.6%)
  Question: 1,240 tokens (0.6%)
  Input Total: 52,340 tokens (26.2%)
  Response: 7,234 tokens (3.6%)
  Total Used: 59,574 tokens (29.8%)
  Remaining: 140,426 tokens (70.2%)
```

### **Chat History Growth**
```
You: What about session management?
📁 Using cached context (12.4s old)
💬 Chat history: 15,890 tokens (1 turns)
📊 Allocation: 91,000 code + 15,890 history = 106,890 total context
🧠 Thinking... (with 1 turn context) (~8s)
✅ Response received in 7.8s (6,890 tokens)

[Claude's response building on previous conversation]

📊 Tokens: 61,450 in + 6,890 out = 68,340 total (34.2% of 200,000)
```

### **Special Commands Output**
```
You: /history
💬 Chat History: 2 turns, 14,124 total tokens, avg 7,062 tokens/turn

You: /verbose
🔧 Verbose mode disabled

You: exit
📊 Session stats: 2 turns, 14,124 total tokens
Goodbye! 👋
```

## 🚨 Error Handling

### **Common Errors**

#### **No Active Embeddings**
```bash
context-ai chat  # No embeddings selected
```
**Error**: `⚠️ No active embeddings selected`
**Solution**: Use `context-ai select` to choose embeddings before starting chat

#### **Invalid API Key**
```bash
context-ai chat  # Invalid Claude API key
```
**Error**: `❌ Invalid Claude API key`
**Solution**: Set API key with `context-ai config set --claude-key YOUR_KEY`

#### **API Timeouts**
```
You: How do I implement authentication?
❌ Claude API connection failed: Request timeout
```
**Solution**: Wait a moment and try again. The session remains active.

#### **Invalid Prompt Mode**
```bash
context-ai chat --prompt-mode invalid
```
**Error**: `❌ argument --prompt-mode: invalid choice: 'invalid' (choose from 'minimal', 'standard', 'comprehensive', 'strict')`

## 💡 Pro Tips

### **Session Management**
```bash
# Start with context selection
context-ai select project-main design-system
context-ai chat --prompt-mode comprehensive

# Monitor token usage during long sessions
# Use /history regularly in chat

# Clear history when switching topics
# Use /clear in chat
```

### **Mode Selection Strategy**
```bash
# Quick questions - minimal mode
context-ai chat --prompt-mode minimal

# Learning and exploration - comprehensive mode  
context-ai chat --prompt-mode comprehensive --verbose

# Code generation and review - strict mode
context-ai chat --prompt-mode strict
```

### **Performance Optimization**
```bash
# For large codebases, start with minimal
context-ai chat --prompt-mode minimal

# Use verbose to understand performance
context-ai chat --verbose

# Switch modes within session as needed
# Use /verbose toggle in chat
```

### **Workflow Integration**
```bash
# Morning development session
context-ai select current-project
context-ai chat --prompt-mode standard --verbose

# Architecture planning session
context-ai select all-projects
context-ai chat --prompt-mode comprehensive

# Code review session
context-ai select feature-branch
context-ai chat --prompt-mode strict
```

## 🔧 Keyboard Shortcuts

- **Ctrl+C**: Interrupt current request and exit chat
- **Ctrl+D**: EOF signal, exits chat gracefully  
- **Up/Down arrows**: Navigate command history (terminal dependent)

## 🔍 Troubleshooting

### **Slow Responses**
- **Cause**: Large context, complex prompt mode
- **Solution**: Use `--prompt-mode minimal`, select fewer embeddings
- **Monitor**: Use `--verbose` to see token allocation

### **Memory Issues in Long Sessions**
- **Cause**: Chat history growing too large
- **Solution**: Use `/clear` command, monitor with `/history`
- **Prevention**: Clear history when switching topics

### **Context Not Relevant**
- **Cause**: Wrong embeddings selected
- **Solution**: Exit chat, use `context-ai select`, restart chat
- **Optimization**: Select only relevant embeddings before starting

### **Token Limit Reached**
- **Cause**: Very long conversation or large context
- **Solution**: System automatically truncates old history
- **Monitor**: Use `/history` and `/verbose` to track usage

## 📈 Performance Characteristics

### **Session Startup**
- **Time**: 1-3 seconds to initialize
- **Memory**: ~50-100MB base usage
- **Token overhead**: Minimal startup cost

### **Response Times by Mode**
- **Minimal**: 2-5 seconds per question
- **Standard**: 4-8 seconds per question
- **Comprehensive**: 8-15 seconds per question
- **Strict**: 10-20 seconds per question

### **Memory Usage**
- **Short sessions** (<10 turns): ~100-200MB
- **Medium sessions** (10-50 turns): ~200-500MB
- **Long sessions** (50+ turns): ~500MB-1GB

## 🔗 Integration with Other Commands

### **Pre-Chat Setup**
```bash
# Complete setup workflow
context-ai config validate
context-ai select relevant-projects
context-ai chat --prompt-mode comprehensive --verbose
```

### **Post-Chat Analysis**
```bash
# After ending chat, analyze what was learned
# (Chat automatically shows final statistics)

# Select different context for next session
context-ai select different-projects
context-ai chat --prompt-mode standard
```

### **Pipeline Usage**
```bash
# Research and documentation workflow
context-ai select all-projects
context-ai chat --prompt-mode comprehensive  # Interactive research
# Then use ask command for specific documentation
context-ai ask "Document the authentication flow" --output auth-docs.md
```

---

*This document provides complete documentation for the `chat` command. Use `context-ai chat --help` for quick reference.*
