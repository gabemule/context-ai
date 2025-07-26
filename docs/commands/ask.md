# Ask Command Reference

> Complete documentation for the `context-ai ask` command - Ask AI-powered questions with codebase context

## 🎯 Overview

The `ask` command provides AI-powered question answering using Claude with context from your active embeddings. It retrieves relevant code and documentation, then uses AI to provide intelligent answers, explanations, and recommendations.

## 📋 Complete Syntax

```bash
context-ai ask <question> [OPTIONS]
```

## 📝 Arguments

### **Positional Arguments (Required)**

#### `question`
- **Type**: String (question text)
- **Required**: Yes
- **Description**: Question to ask Claude using your codebase context
- **Validation**: Cannot be empty
- **Examples**:
  - `"How do I implement authentication?"`
  - `"What are the error handling patterns?"`
  - `"Show me examples of React components"`

### **Optional Arguments**

#### `--format` / `-f`
- **Type**: Choice from predefined list
- **Required**: No
- **Default**: `ai_friendly`
- **Choices**: `["ai_friendly", "plain", "markdown", "json", "xml"]`
- **Description**: Context format for AI processing
- **Note**: Only `ai_friendly` provides AI answers; others return formatted context without AI processing
- **Examples**:
  - `--format ai_friendly` (AI processing)
  - `--format markdown` (structured context only)

#### `--prompt-mode` / `-pm`
- **Type**: Choice from predefined list
- **Required**: No
- **Default**: Uses system default (typically `standard`)
- **Choices**: `["minimal", "standard", "comprehensive", "strict"]`
- **Description**: AI prompt complexity and analysis depth
- **Examples**:
  - `--prompt-mode comprehensive`
  - `-pm strict`

### **Optional Flags**

#### `--copy` / `-c`
- **Type**: Boolean flag
- **Required**: No
- **Default**: False
- **Description**: Copy AI response to clipboard
- **Effect**: Copies final response to system clipboard using pyperclip

#### `--output` / `-o`
- **Type**: String (file path)
- **Required**: No
- **Description**: Save AI response to file instead of printing to console
- **Validation**: Must be writable file path
- **Examples**:
  - `--output answer.md`
  - `-o /path/to/response.txt`

#### `--verbose` / `-v`
- **Type**: Boolean flag
- **Required**: No
- **Default**: False
- **Description**: Show detailed processing information including token usage
- **Effect**: Enables debug logging and performance metrics

## 🚀 Usage Examples

### **Basic Usage**
```bash
# Minimum required arguments
context-ai ask "How do I implement user authentication?"
```

### **Prompt Mode Variations**
```bash
# Minimal mode - fast, basic responses
context-ai ask "What is this function?" --prompt-mode minimal

# Standard mode - balanced analysis (default)
context-ai ask "How to handle errors?" --prompt-mode standard

# Comprehensive mode - deep architectural analysis
context-ai ask "What's the best way to structure this feature?" --prompt-mode comprehensive

# Strict mode - enforced guidelines and code review
context-ai ask "Review this authentication code" --prompt-mode strict
```

### **Output Options**
```bash
# Copy to clipboard
context-ai ask "Show me validation patterns" --copy

# Save to file
context-ai ask "How to implement caching?" --output caching-guide.md

# Both copy and save
context-ai ask "API best practices" --copy --output api-guide.md
```

### **Information Levels**
```bash
# Basic question
context-ai ask "How do buttons work?"

# With verbose token information
context-ai ask "How do buttons work?" --verbose

# Comprehensive analysis with verbose
context-ai ask "How do buttons work?" --prompt-mode comprehensive --verbose
```

### **All Flag Combinations**

#### **1. Basic AI question**
```bash
context-ai ask "authentication patterns"
```

#### **2. Minimal mode for speed**
```bash
context-ai ask "authentication patterns" --prompt-mode minimal
```

#### **3. Comprehensive with verbose**
```bash
context-ai ask "authentication patterns" --prompt-mode comprehensive --verbose
```

#### **4. Save comprehensive analysis**
```bash
context-ai ask "authentication patterns" --prompt-mode comprehensive --output auth-analysis.md
```

#### **5. Copy quick answer**
```bash
context-ai ask "authentication patterns" --prompt-mode minimal --copy
```

#### **6. Maximum configuration**
```bash
context-ai ask "authentication and security patterns" --prompt-mode strict --verbose --copy --output security-review.md
```

### **Non-AI Formats (Context Only)**
```bash
# Get structured context without AI processing
context-ai ask "authentication" --format json --output context.json
context-ai ask "validation" --format markdown --output validation-context.md
context-ai ask "components" --format xml --output components.xml
```

### **Real-World Examples**

#### **Code Understanding**
```bash
# Learn about patterns
context-ai ask "What are the common React patterns used in this codebase?" --prompt-mode comprehensive

# Understand specific implementations
context-ai ask "How is error handling implemented?" --verbose --output error-handling.md
```

#### **Development Help**
```bash
# Get implementation guidance
context-ai ask "How should I implement user registration?" --prompt-mode comprehensive --copy

# Quick coding help
context-ai ask "Show me how to validate email addresses" --prompt-mode minimal
```

#### **Architecture Questions**
```bash
# Architectural analysis
context-ai ask "What's the overall architecture of this system?" --prompt-mode comprehensive --output architecture.md

# Best practices review
context-ai ask "What coding standards are used here?" --prompt-mode strict --verbose
```

## 📊 Output Examples

### **AI-Friendly Format (Default) - Standard Mode**
```
🤖 Claude's Answer

Based on your codebase, here's how authentication is typically implemented:

## Current Authentication Patterns

From `src/auth/login.tsx`:
```typescript
// From: src/auth/login.tsx
const LoginForm = () => {
  const handleLogin = async (credentials) => {
    try {
      const response = await authAPI.login(credentials);
      localStorage.setItem('token', response.token);
      return response.user;
    } catch (error) {
      throw new Error('Authentication failed');
    }
  };
};
```

The codebase uses JWT tokens stored in localStorage with these key components:

1. **Login Form**: Handles user credentials
2. **Auth API**: Manages authentication requests  
3. **Token Storage**: Uses localStorage for persistence
4. **Error Handling**: Provides user feedback

## Recommendations

- Consider using secure httpOnly cookies instead of localStorage
- Add token refresh logic for better UX
- Implement proper error boundaries

📊 Tokens: 45,230 in + 8,950 out = 54,180 total (27.1% of 200,000)
```

### **Comprehensive Mode Output**
```
🤖 Claude's Answer

# Authentication Architecture Analysis

Based on comprehensive analysis of your codebase, here's the authentication implementation:

## Current Implementation

### Frontend Authentication (`src/auth/`)
```typescript
// From: src/auth/login.tsx
const LoginForm = () => {
  // Implementation details with extensive analysis
};
```

### Backend Middleware (`src/middleware/auth.ts`)
```typescript
// From: src/middleware/auth.ts
export const validateToken = (req, res, next) => {
  // JWT validation logic
};
```

## Cross-Project Comparison

After analyzing multiple projects in your codebase:

- **Project A**: Uses session-based auth (more secure)
- **Project B**: Implements OAuth2 flow (better UX)
- **Current Project**: Uses simple JWT (needs improvement)

## Architectural Recommendations

1. **Security Enhancements**
   - Migrate from localStorage to httpOnly cookies
   - Implement CSRF protection
   - Add rate limiting to auth endpoints

2. **Code Quality Improvements**
   - Extract auth logic into custom hooks
   - Add comprehensive error handling
   - Implement token refresh mechanism

3. **Best Practices Alignment**
   - Follow OAuth2 standards from Project B
   - Adopt session management from Project A
   - Implement proper logout functionality

## Implementation Roadmap

1. **Phase 1**: Secure token storage
2. **Phase 2**: Add refresh token logic  
3. **Phase 3**: Implement OAuth2 integration

This analysis shows opportunities for significant security and UX improvements.

📊 Token Usage Details:
  Context: 87,450 tokens (43.7%)
  Question: 1,240 tokens (0.6%)
  Input Total: 88,690 tokens (44.3%)
  Response: 8,950 tokens (4.5%)
  Total Used: 97,640 tokens (48.8%)
```

### **Minimal Mode Output**
```
🤖 Claude's Answer

Authentication in your codebase uses JWT tokens:

```typescript
// From: src/auth/login.tsx
const handleLogin = async (credentials) => {
  const response = await authAPI.login(credentials);
  localStorage.setItem('token', response.token);
  return response.user;
};
```

Key components:
- Login form with email/password
- JWT token storage in localStorage  
- API middleware for validation

Consider using httpOnly cookies for better security.

📊 Tokens: 25,340 in + 4,230 out = 29,570 total (14.8% of 200,000)
```

### **Verbose Output**
```
🚀 Initializing ask command...
🎯 Using prompt mode: comprehensive
🔍 Retrieving context from active embeddings...
📄 Context retrieved (87,450 characters)
📊 Context limit: 130,000 tokens (65% of 200,000)
📊 Input tokens: 88,690 (context: 87,450, question: 1,240)
📊 Dynamic response tokens: 8,950
🧠 Asking Claude (87,450 chars, max 8,950 tokens)...
✅ Response received in 8.3s (8,950 tokens)

[Claude's Answer displayed...]

⏱️ Claude API: 8.3 seconds (88,690 in, 8,950 out)
📊 Token Usage Details:
  Context: 87,450 tokens (43.7%)
  Question: 1,240 tokens (0.6%)
  Input Total: 88,690 tokens (44.3%)
  Response: 8,950 tokens (4.5%)
  Total Used: 97,640 tokens (48.8%)
  Remaining: 102,360 tokens (51.2%)
```

## 🎛️ Prompt Mode Details

### **Minimal Mode** ⚡
- **Speed**: ~2-3 seconds
- **Features**: Basic context + question only
- **Guidelines**: None applied
- **Best for**: Quick factual questions, simple lookups
- **Token usage**: Lowest (~20-40K tokens)

### **Standard Mode** 🎯 (Default)
- **Speed**: ~4-6 seconds  
- **Features**: Cross-project hints, coding guidelines when applicable
- **Guidelines**: JS/TS guidelines when detected
- **Best for**: Regular development questions, everyday coding help
- **Token usage**: Moderate (~40-80K tokens)

### **Comprehensive Mode** 🧠
- **Speed**: ~8-12 seconds
- **Features**: Full cross-project analysis, architectural insights
- **Guidelines**: Applied with architectural reasoning
- **Best for**: Architecture decisions, complex comparisons, learning
- **Token usage**: High (~80-120K tokens)

### **Strict Mode** 🔍
- **Speed**: ~10-15 seconds
- **Features**: Enforced coding standards, detailed code review
- **Guidelines**: Strict enforcement with violation detection
- **Best for**: Code generation, refactoring, standards compliance
- **Token usage**: Highest (~100-150K tokens)

## 🚨 Error Handling

### **Common Errors**

#### **No Question Provided**
```bash
context-ai ask
```
**Error**: `❌ the following arguments are required: question`

#### **No Active Embeddings**
```bash
context-ai ask "test question"  # No embeddings selected
```
**Error**: `❌ No active embeddings selected. Use: context-ai select`

#### **Invalid Prompt Mode**
```bash
context-ai ask "test" --prompt-mode invalid
```
**Error**: `❌ argument --prompt-mode: invalid choice: 'invalid' (choose from 'minimal', 'standard', 'comprehensive', 'strict')`

#### **Claude API Error**
```bash
context-ai ask "test question"
```
**Error**: `❌ Claude API error: Invalid API key`

#### **File Write Error**
```bash
context-ai ask "test" --output /read-only/file.txt
```
**Error**: `❌ Failed to save to file: Permission denied`

#### **Clipboard Error**
```bash
context-ai ask "test" --copy  # pyperclip not installed
```
**Warning**: `⚠️ pyperclip not installed. Install with: pip install pyperclip`

## 💡 Pro Tips

### **Question Optimization**
```bash
# Be specific with technical terms
context-ai ask "How is JWT token validation implemented in the middleware?"

# Ask for comparisons
context-ai ask "What are the differences between our authentication approaches?" --prompt-mode comprehensive

# Request examples
context-ai ask "Show me examples of React custom hooks with TypeScript"
```

### **Mode Selection Strategy**
```bash
# Quick answers - use minimal
context-ai ask "What does this function do?" --prompt-mode minimal

# Learning - use comprehensive
context-ai ask "Explain the architecture of this system" --prompt-mode comprehensive

# Code review - use strict
context-ai ask "Review this authentication implementation" --prompt-mode strict
```

### **Workflow Integration**
```bash
# Research and document
context-ai ask "How should I implement caching?" --prompt-mode comprehensive --output caching-research.md

# Quick development help
context-ai ask "How to validate email with regex?" --prompt-mode minimal --copy

# Architecture planning
context-ai ask "What's the best way to structure user management?" --prompt-mode comprehensive --verbose
```

### **Context Management**
```bash
# Select relevant embeddings first
context-ai select frontend-v1 design-system
context-ai ask "How do I use the Button component?" --prompt-mode standard

# Different contexts for different questions
context-ai select backend-v2 api-docs
context-ai ask "How to implement API authentication?" --prompt-mode strict
```

## 🔍 Troubleshooting

### **Poor Quality Responses**
- **Cause**: Irrelevant context or too generic questions
- **Solution**: Be more specific, select relevant embeddings, use appropriate prompt mode
- **Check**: Use `--verbose` to see context quality

### **Slow Responses**
- **Cause**: Large context, complex prompt mode
- **Solution**: Use `--prompt-mode minimal`, select fewer embeddings
- **Monitor**: Use `--verbose` to see token usage and timing

### **Token Limit Issues**
- **Cause**: Very large context exceeding limits
- **Solution**: Select fewer embeddings, use minimal mode
- **Check**: Verbose mode shows token allocation

### **Context Not Relevant**
- **Cause**: Wrong embeddings selected or query mismatch
- **Solution**: Use `context-ai select` to choose appropriate embeddings
- **Debug**: Try `context-ai query` first to see raw context

## 📈 Performance Characteristics

### **Response Times by Mode**
- **Minimal**: 2-5 seconds
- **Standard**: 4-8 seconds
- **Comprehensive**: 8-15 seconds
- **Strict**: 10-20 seconds

### **Token Usage by Mode**
- **Minimal**: 20-40K tokens (10-20% of limit)
- **Standard**: 40-80K tokens (20-40% of limit)  
- **Comprehensive**: 80-120K tokens (40-60% of limit)
- **Strict**: 100-150K tokens (50-75% of limit)

### **Memory Usage**
- **Context processing**: ~100-500MB temporarily
- **AI processing**: ~50-200MB during request
- **Output formatting**: Minimal

## 🔗 Integration with Other Commands

### **Combined Workflows**
```bash
# Research workflow
context-ai query "authentication" --format json --output context.json
context-ai ask "Analyze these authentication patterns" --prompt-mode comprehensive

# Development workflow  
context-ai select frontend-v1 backend-v2
context-ai ask "How do I implement user login?" --copy
# Paste into code editor

# Documentation workflow
context-ai ask "Document the API authentication flow" --prompt-mode comprehensive --output api-auth-docs.md
```

### **Pipeline Usage**
```bash
# Full analysis pipeline
context-ai select main-project utils-library && \
context-ai ask "What are the main architectural patterns?" --prompt-mode comprehensive --output architecture.md && \
context-ai ask "What coding standards are used?" --prompt-mode strict --output standards.md
```

---

*This document provides complete documentation for the `ask` command. Use `context-ai ask --help` for quick reference.*
