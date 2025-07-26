# Select Command Reference

> Complete documentation for the `context-ai select` command - Select active embeddings for queries

## 🎯 Overview

The `select` command manages which embedding sets are active for queries and AI interactions. It provides both interactive checkbox interface and direct CLI selection, allowing you to choose which projects/embeddings to include in your context.

## 📋 Complete Syntax

```bash
context-ai select [embedding_names...] [OPTIONS]
```

## 📝 Arguments

### **Positional Arguments (Optional)**

#### `embeddings`
- **Type**: List of strings (embedding names)
- **Required**: No
- **Description**: Embedding names to select directly via CLI
- **Validation**: Must be existing embedding names
- **Behavior**: If provided, selects embeddings directly. If omitted, opens interactive interface
- **Examples**:
  - `frontend-v1`
  - `frontend-v1 backend-v2 docs-v1`

### **Optional Flags**

#### `--verbose` / `-v`
- **Type**: Boolean flag
- **Required**: No
- **Default**: False
- **Description**: Show detailed processing information
- **Effect**: Enables debug logging and selection details

## 🚀 Usage Examples

### **Interactive Mode (No Arguments)**
```bash
# Opens checkbox interface for selection
context-ai select
```

### **Direct Selection**
```bash
# Select single embedding
context-ai select frontend-v1

# Select multiple embeddings
context-ai select frontend-v1 backend-v2 docs-v1

# Select with verbose output
context-ai select frontend-v1 backend-v2 --verbose
```

### **All Flag Combinations**

#### **1. Interactive mode (default)**
```bash
context-ai select
```
**Result**: Opens interactive checkbox interface

#### **2. Interactive mode with verbose**
```bash
context-ai select --verbose
```
**Result**: Interactive interface + detailed logging

#### **3. Direct single selection**
```bash
context-ai select project-v1
```
**Result**: Immediately selects `project-v1`

#### **4. Direct single selection with verbose**
```bash
context-ai select project-v1 --verbose
```
**Result**: Selects `project-v1` + shows detailed information

#### **5. Direct multiple selection**
```bash
context-ai select frontend-v1 backend-v2
```
**Result**: Selects both embeddings immediately

#### **6. Direct multiple selection with verbose**
```bash
context-ai select frontend-v1 backend-v2 docs-v1 --verbose
```
**Result**: Selects all three + shows detailed selection info

### **Real-World Examples**

#### **Development Workflow**
```bash
# Quick selection for development
context-ai select dev-frontend dev-backend

# Full project context
context-ai select main-project design-system utils-library --verbose
```

#### **Documentation Work**
```bash
# Select docs and related code
context-ai select api-docs frontend-components

# Interactive selection for exploration
context-ai select
```

#### **Scripting/Automation**
```bash
# Automated selection in scripts
context-ai select "${PROJECT_NAME}" "${DOCS_NAME}"

# Conditional selection
if [ "$INCLUDE_DOCS" = "true" ]; then
  context-ai select main-project documentation
else
  context-ai select main-project
fi
```

## 📊 Output Examples

### **Interactive Mode Output**
```bash
$ context-ai select

🚀 Initializing select command...
🎯 Select active embeddings for queries

[?] Select embeddings to query (use space to select/deselect, enter to confirm):
 > [x] frontend-v1 (153 chunks, 27 files, 25 Jan 2025)
   [x] backend-v2 (800 chunks, 45 files, 1 day ago) 
   [ ] api-docs-v1 (300 chunks, 12 files, 1 week ago)
   [ ] design-system (450 chunks, 35 files, 3 days ago)
   [ ] legacy-code (120 chunks, 8 files, 1 month ago)

✅ Selected embeddings: frontend-v1, backend-v2
```

### **Direct Selection Output**
```bash
$ context-ai select frontend-v1 backend-v2

🚀 Initializing select command...
🎯 Setting active embeddings: frontend-v1, backend-v2
✅ Selected embeddings: frontend-v1, backend-v2
```

### **Verbose Direct Selection Output**
```bash
$ context-ai select frontend-v1 backend-v2 --verbose

🚀 Initializing select command...
🔧 Verbose mode enabled
🎯 Setting active embeddings: frontend-v1, backend-v2
📊 Validating embedding existence...
✅ frontend-v1: Found (153 chunks, 27 files)
✅ backend-v2: Found (800 chunks, 45 files)
💾 Updating active embeddings configuration...
📋 Active embeddings saved to: ~/.context-ai/active.json
✅ Selected embeddings: frontend-v1, backend-v2
📊 Total context: 953 chunks from 72 files
```

### **Interactive Mode with Verbose**
```bash
$ context-ai select --verbose

🚀 Initializing select command...
🔧 Verbose mode enabled
📊 Loading available embeddings...
Found 5 embedding sets:
  - frontend-v1: 153 chunks, 27 files, 2.3MB
  - backend-v2: 800 chunks, 45 files, 8.1MB
  - api-docs-v1: 300 chunks, 12 files, 1.8MB
  - design-system: 450 chunks, 35 files, 4.2MB
  - legacy-code: 120 chunks, 8 files, 0.9MB
🎯 Select active embeddings for queries

[Interactive checkbox interface appears...]

✅ Selected embeddings: frontend-v1, backend-v2
📊 Total context: 953 chunks from 72 files
💾 Configuration saved
```

## 🎛️ Interactive Interface Details

### **Navigation Controls**
- **Space**: Toggle selection (select/deselect)
- **Up/Down arrows**: Navigate between options
- **Enter**: Confirm selection and exit
- **Ctrl+C**: Cancel selection and exit

### **Display Information**
Each embedding shows:
- **Name**: Embedding identifier
- **Chunk count**: Number of searchable chunks
- **File count**: Number of processed files  
- **Date**: When the embedding was created
- **Selection state**: `[x]` selected, `[ ]` unselected

### **Visual Indicators**
- `>` indicates current cursor position
- `[x]` indicates selected embedding
- `[ ]` indicates unselected embedding
- Colors and formatting for better visibility

## 🚨 Error Handling

### **Common Errors**

#### **Invalid Embedding Name**
```bash
context-ai select nonexistent-project
```
**Error**: 
```
❌ Invalid embedding names: nonexistent-project
Available embeddings: frontend-v1, backend-v2, api-docs-v1
```

#### **Multiple Invalid Names**
```bash
context-ai select valid-project invalid-one another-invalid
```
**Error**:
```
❌ Invalid embedding names: invalid-one, another-invalid
Available embeddings: frontend-v1, backend-v2, api-docs-v1, valid-project
```

#### **No Embeddings Available**
```bash
context-ai select
```
**Output**:
```
⚠️ No embeddings available
Generate embeddings first with: context-ai generate
```

#### **Storage Access Issues**
```bash
context-ai select frontend-v1
```
**Error**:
```
❌ Unable to access embedding storage
Check permissions for: ~/.context-ai/
```

### **Validation Rules**

#### **Embedding Name Validation**
- Must exactly match existing embedding names
- Case sensitive
- No partial matching

#### **Selection Validation**
- At least one embedding can be selected
- Empty selection is allowed (clears active embeddings)
- Duplicate names in CLI are deduplicated

## 💡 Pro Tips

### **Quick Selection Workflows**
```bash
# One-liner: select and immediately query
context-ai select my-project && context-ai query "how to authenticate"

# One-liner: select and start chat
context-ai select frontend backend && context-ai chat

# Quick switching between contexts
alias select-frontend="context-ai select frontend-v1 design-system"
alias select-backend="context-ai select backend-v2 api-docs"
```

### **Scripting Integration**
```bash
#!/bin/bash
# Smart project selection script

PROJECT_TYPE="$1"
case "$PROJECT_TYPE" in
  "frontend")
    context-ai select frontend-v1 design-system components
    ;;
  "backend")
    context-ai select backend-v2 api-docs database-models
    ;;
  "fullstack")
    context-ai select frontend-v1 backend-v2 shared-utils
    ;;
  *)
    echo "Usage: $0 {frontend|backend|fullstack}"
    exit 1
    ;;
esac
```

### **Context Management**
```bash
# Save current selection before experimenting
context-ai select > current_selection.txt

# Restore selection later (manual process)
# Read the saved file and select those embeddings

# Clear all selections
context-ai select ""  # Empty string clears all
```

### **Development Workflow**
```bash
# Morning routine: select relevant projects
context-ai select current-sprint design-system --verbose

# Feature work: add specific context
context-ai select current-sprint feature-docs component-library

# Bug investigation: add legacy context
context-ai select current-sprint legacy-codebase bug-reports
```

## 🔍 Embedding Information Display

### **Interactive Mode Information**
```
frontend-v1 (153 chunks, 27 files, 25 Jan 2025)
│
├── 153 chunks: Number of searchable text segments
├── 27 files: Original files processed
└── 25 Jan 2025: Creation date
```

### **Verbose Mode Statistics**
```bash
📊 Embedding Details:
  Name: frontend-v1
  Chunks: 153
  Files: 27  
  Size: 2.3MB
  Created: 2025-01-25 10:30:00
  Languages: JavaScript (15), TypeScript (8), CSS (4)
  Average chunk size: 188 tokens
  Token range: 45-1,456 tokens
```

## 🔄 State Management

### **Configuration Storage**
- **Location**: `~/.context-ai/active.json`
- **Format**: JSON list of active embedding names
- **Persistence**: Survives between CLI sessions
- **Scope**: Global (affects all commands)

### **Example Configuration File**
```json
{
  "selected": [
    "frontend-v1",
    "backend-v2"
  ],
  "last_updated": "2025-01-25T15:30:00Z"
}
```

### **Selection State**
- **Active**: Currently selected embeddings used for queries
- **Available**: All generated embeddings on system
- **Persistent**: Selection survives restarts
- **Global**: Affects `query`, `ask`, and `chat` commands

## 📈 Performance Characteristics

### **Interactive Mode**
- **Load time**: <1 second for up to 50 embeddings
- **Memory usage**: ~10MB for interface
- **Response time**: Immediate selection feedback

### **Direct Selection**
- **Validation time**: <0.1 seconds per embedding
- **Update time**: <0.1 seconds to save configuration
- **Memory usage**: Minimal (text processing only)

### **Large Scale Usage**
- **Max embeddings**: No hard limit (tested with 100+)
- **Interface performance**: Remains responsive
- **Storage efficiency**: JSON configuration is compact

## 🔗 Integration with Other Commands

### **Query Command**
```bash
# Select then query
context-ai select frontend-v1 backend-v2
context-ai query "authentication patterns"
```

### **Ask Command**
```bash
# Select then ask AI
context-ai select design-system components
context-ai ask "How do I use the Button component?"
```

### **Chat Command**
```bash
# Select then start chat session
context-ai select fullstack-project
context-ai chat --prompt-mode comprehensive
```

### **Pipeline Usage**
```bash
# Full workflow pipeline
context-ai select project-main design-docs && \
context-ai query "error handling" --format markdown --output errors.md && \
context-ai ask "Summarize the error handling patterns" --output summary.md
```

---

*This document provides complete documentation for the `select` command. Use `context-ai select --help` for quick reference.*
