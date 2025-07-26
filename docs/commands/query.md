# Query Command Reference

> Complete documentation for the `context-ai query` command - Search embeddings for relevant context

## 🎯 Overview

The `query` command searches active embeddings to find relevant code and documentation context based on your search query. It returns structured results without AI processing, making it perfect for raw context retrieval and debugging.

## 📋 Complete Syntax

```bash
context-ai query <question> [OPTIONS]
```

## 📝 Arguments

### **Positional Arguments (Required)**

#### `question`
- **Type**: String (search query)
- **Required**: Yes
- **Description**: Question or search query to find relevant context
- **Validation**: Cannot be empty or whitespace-only
- **Examples**:
  - `"authentication patterns"`
  - `"how to handle errors"`
  - `"React component props"`

### **Optional Arguments**

#### `--format` / `-f`
- **Type**: Choice from predefined list
- **Required**: No
- **Default**: `ai_friendly`
- **Choices**: `["ai_friendly", "plain", "markdown", "json"]`
- **Description**: Output format for search results
- **Examples**:
  - `--format json`
  - `-f markdown`

#### `--max-results` / `-n`
- **Type**: Integer
- **Required**: No
- **Default**: Uses config default (typically 20)
- **Description**: Maximum number of results to display
- **Validation**: Must be positive integer
- **Examples**:
  - `--max-results 50`
  - `-n 10`

### **Optional Flags**

#### `--verbose` / `-v`
- **Type**: Boolean flag
- **Required**: No
- **Default**: False
- **Description**: Show detailed search information and statistics
- **Effect**: Enables debug logging and search metrics

#### `--debug`
- **Type**: Boolean flag
- **Required**: No
- **Default**: False
- **Description**: Show debug information including query preprocessing details
- **Effect**: Enables debug logging level and internal processing info

#### `--copy` / `-c`
- **Type**: Boolean flag
- **Required**: No
- **Default**: False
- **Description**: Copy results to clipboard (requires pyperclip)
- **Effect**: Copies formatted output to system clipboard

#### `--output` / `-o`
- **Type**: String (file path)
- **Required**: No
- **Description**: Save results to file instead of printing to console
- **Validation**: Must be writable file path
- **Examples**:
  - `--output results.md`
  - `-o /path/to/output.json`

## 🚀 Usage Examples

### **Basic Usage**
```bash
# Minimum required arguments
context-ai query "authentication patterns"
```

### **Format Variations**
```bash
# AI-friendly format (default)
context-ai query "error handling" --format ai_friendly

# Plain text format
context-ai query "React hooks" --format plain

# Markdown format
context-ai query "API endpoints" --format markdown

# JSON format for parsing
context-ai query "database models" --format json
```

### **Result Limiting**
```bash
# Limit to 10 results
context-ai query "validation functions" --max-results 10

# Get more results
context-ai query "utility functions" --max-results 50
```

### **Information Levels**
```bash
# Basic query
context-ai query "button component"

# With verbose info
context-ai query "button component" --verbose

# With debug info
context-ai query "button component" --debug

# Both verbose and debug
context-ai query "button component" --verbose --debug
```

### **Output Options**
```bash
# Copy to clipboard
context-ai query "API authentication" --copy

# Save to file
context-ai query "error patterns" --output errors.md

# Both copy and save
context-ai query "React patterns" --copy --output react-patterns.json --format json
```

### **All Flag Combinations (Common)**

#### **1. Basic query**
```bash
context-ai query "authentication"
```

#### **2. Verbose query**
```bash
context-ai query "authentication" --verbose
```

#### **3. JSON output with copy**
```bash
context-ai query "authentication" --format json --copy
```

#### **4. Limited results with output file**
```bash
context-ai query "authentication" --max-results 5 --output auth.md --format markdown
```

#### **5. Debug mode with verbose**
```bash
context-ai query "authentication" --debug --verbose
```

#### **6. Maximum options**
```bash
context-ai query "authentication patterns" --format json --max-results 25 --verbose --debug --copy --output auth-complete.json
```

### **Real-World Examples**

#### **Code Research**
```bash
# Find authentication patterns
context-ai query "user authentication login" --format markdown --output auth-research.md

# API endpoint patterns
context-ai query "REST API routes" --format json --max-results 30 --copy
```

#### **Debugging Workflow**
```bash
# Find error handling
context-ai query "error handling try catch" --verbose --debug

# Locate specific functions
context-ai query "validation helper functions" --max-results 15 --format plain
```

#### **Documentation Generation**
```bash
# Extract component usage
context-ai query "React component props interface" --format markdown --output components.md

# API documentation
context-ai query "API endpoints swagger" --format json --output api-docs.json
```

## 📊 Output Examples

### **AI-Friendly Format (Default)**
```
🔍 Query Results (ai_friendly)

## Search Results for: "authentication patterns"

### File: src/auth/login.tsx (Score: 0.89)
```typescript
// User authentication component with email/password
const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
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

### File: src/auth/middleware.ts (Score: 0.82)
```typescript
// JWT token validation middleware
export const validateToken = (req, res, next) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  if (!token) {
    return res.status(401).json({ error: 'Token required' });
  }
  // ... validation logic
};
```

Total: 8 results from 3 files
```

### **JSON Format**
```json
{
  "query": "authentication patterns",
  "total_results": 8,
  "results": [
    {
      "file_path": "src/auth/login.tsx",
      "score": 0.89,
      "content": "const LoginForm = () => {\n  const [email, setEmail] = useState('');\n  // ...",
      "metadata": {
        "language": "typescript",
        "chunk_id": "auth_login_1",
        "tokens": 156
      }
    },
    {
      "file_path": "src/auth/middleware.ts",
      "score": 0.82,
      "content": "export const validateToken = (req, res, next) => {\n  // ...",
      "metadata": {
        "language": "typescript", 
        "chunk_id": "auth_middleware_1",
        "tokens": 143
      }
    }
  ],
  "search_metadata": {
    "embeddings_searched": ["frontend-v1", "backend-v2"],
    "total_chunks": 953,
    "search_time_ms": 234
  }
}
```

### **Verbose Output**
```
🚀 Initializing query command...
🔍 Searching for: authentication patterns
📊 Query format: ai_friendly
📊 Max results: 20
📊 Active embeddings: frontend-v1, backend-v2
📊 Total chunks to search: 953
⏱️ Search completed in 234ms
📊 Found 8 relevant results from 3 files
📊 Score range: 0.89 - 0.65
📊 Average score: 0.78

[Results displayed...]

✅ Query completed successfully
```

### **Debug Output**
```
🚀 Initializing query command...
🔧 Debug mode enabled
Query arguments: {'question': 'authentication patterns', 'format': 'ai_friendly', 'debug': True}
🔍 Preprocessing query: 'authentication patterns'
📊 Query tokens: ['authentication', 'patterns', 'login', 'auth', 'security']
📊 Embedding models loaded: sentence-transformers/all-MiniLM-L6-v2
📊 Vector similarity search...
📊 Raw results: 15 chunks above threshold 0.6
📊 Post-processing and ranking...
📊 Final results: 8 chunks selected

[Results displayed...]

📊 Performance metrics:
  - Query preprocessing: 12ms
  - Vector search: 145ms
  - Post-processing: 77ms
  - Total time: 234ms
```

## 📋 Format Details

### **AI-Friendly Format**
- **Purpose**: Optimized for AI consumption
- **Structure**: Markdown-like with clear sections
- **Features**: File paths, similarity scores, syntax highlighting
- **Use Case**: Default for most queries

### **Plain Format**  
- **Purpose**: Simple text output
- **Structure**: Clean text without formatting
- **Features**: Minimal markup, easy parsing
- **Use Case**: Scripting, simple display

### **Markdown Format**
- **Purpose**: Documentation-ready output
- **Structure**: Proper markdown with headers
- **Features**: Code blocks, links, formatting
- **Use Case**: Documentation generation

### **JSON Format**
- **Purpose**: Programmatic processing
- **Structure**: Structured data with metadata
- **Features**: Complete result data, search metrics
- **Use Case**: Integration, analysis, further processing

## 🚨 Error Handling

### **Common Errors**

#### **Empty Query**
```bash
context-ai query ""
```
**Error**: `❌ Validation error: Query cannot be empty`

#### **No Active Embeddings**
```bash
context-ai query "test"  # No embeddings selected
```
**Error**: `❌ No active embeddings selected. Use: context-ai select`

#### **Invalid Format**
```bash
context-ai query "test" --format xml
```
**Error**: `❌ argument --format: invalid choice: 'xml' (choose from 'ai_friendly', 'plain', 'markdown', 'json')`

#### **Invalid Max Results**
```bash
context-ai query "test" --max-results -5
```
**Error**: `❌ Max results must be a positive integer`

#### **File Write Error**
```bash
context-ai query "test" --output /read-only/file.txt
```
**Error**: `❌ Failed to save to file: Permission denied`

#### **Clipboard Error**
```bash
context-ai query "test" --copy  # pyperclip not installed
```
**Warning**: `⚠️ pyperclip not installed. Install with: pip install pyperclip`

## 💡 Pro Tips

### **Search Optimization**
```bash
# Use specific technical terms
context-ai query "JWT token validation middleware"

# Multiple related terms
context-ai query "React useState useEffect hooks"

# Include context keywords
context-ai query "API error handling axios catch"
```

### **Result Analysis**
```bash
# Get diverse results with high limit
context-ai query "component patterns" --max-results 50 --format json

# Focus on best matches
context-ai query "authentication" --max-results 5 --verbose
```

### **Workflow Integration**
```bash
# Research workflow
context-ai query "error boundaries" --format markdown --output research.md
context-ai query "error boundaries" --format json --copy  # For processing

# Quick debugging
context-ai query "specific error message" --debug --verbose
```

### **Documentation Pipeline**
```bash
#!/bin/bash
# Generate documentation for different topics
topics=("authentication" "validation" "error-handling" "api-routes")

for topic in "${topics[@]}"; do
  context-ai query "$topic patterns" \
    --format markdown \
    --max-results 10 \
    --output "docs/${topic}.md"
done
```

## 🔍 Troubleshooting

### **No Results Found**
- **Cause**: Query terms not in embeddings or too specific
- **Solution**: Try broader terms, check active embeddings
- **Debug**: Use `--debug` to see preprocessing

### **Low Quality Results**
- **Cause**: Query too generic or embeddings don't match domain
- **Solution**: Use more specific technical terms
- **Check**: Use `--verbose` to see similarity scores

### **Slow Performance**
- **Cause**: Large number of chunks or complex query
- **Solution**: Limit results with `--max-results`, select fewer embeddings
- **Monitor**: Use `--debug` to see timing breakdown

### **Memory Issues**
- **Cause**: Very large result sets or embeddings
- **Solution**: Reduce `--max-results`, query smaller embedding sets
- **Check**: Monitor system memory usage

## 📈 Performance Characteristics

### **Search Speed**
- **Small embeddings** (<500 chunks): <100ms
- **Medium embeddings** (500-2000 chunks): 100-500ms
- **Large embeddings** (2000+ chunks): 500ms-2s

### **Memory Usage**
- **Query processing**: ~50-200MB temporarily
- **Result formatting**: ~10-50MB depending on size
- **JSON format**: Higher memory for large result sets

### **Accuracy**
- **Similarity threshold**: 0.6 (configurable)
- **Typical score range**: 0.6-0.95
- **Best results**: Usually >0.8 similarity

---

*This document provides complete documentation for the `query` command. Use `context-ai query --help` for quick reference.*
