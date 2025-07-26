# Generate Command Reference

> Complete documentation for the `context-ai generate` command - Generate embeddings from project directories

## 🎯 Overview

The `generate` command creates vector embeddings from your project directories, making them searchable for AI-powered assistance. It processes code files, documentation, and other supported file types into a searchable database.

## 📋 Complete Syntax

```bash
context-ai generate <path> --name <name> [OPTIONS]
```

## 📝 Arguments

### **Positional Arguments (Required)**

#### `path`
- **Type**: String (directory path)
- **Required**: Yes
- **Description**: Path to the project directory to generate embeddings from
- **Validation**: Must be a valid directory path
- **Examples**: 
  - `./my-project`
  - `/absolute/path/to/project`
  - `../relative/path`
  - `~/home/project`

### **Required Options**

#### `--name` / `-n`
- **Type**: String
- **Required**: Yes
- **Description**: Name for this embedding set (used for identification and selection)
- **Validation**: Must be unique, alphanumeric with hyphens/underscores allowed
- **Max Length**: 100 characters
- **Examples**:
  - `"frontend-v1"`
  - `"api-backend"`
  - `"design-system-2024"`

### **Optional Arguments**

#### `--ignore-file` / `-i`
- **Type**: String (file path)
- **Required**: No
- **Default**: Auto-detect (`.contextignore` → `.gitignore` → built-in defaults)
- **Description**: Custom ignore file path for specifying which files to exclude
- **Validation**: Must be a valid file path if provided
- **Examples**:
  - `--ignore-file .customignore`
  - `--ignore-file /path/to/ignore-patterns.txt`

### **Flags**

#### `--no-progress`
- **Type**: Boolean flag
- **Required**: No
- **Default**: False (progress tracking enabled)
- **Description**: Disable progress tracking and fancy output (useful for CI/CD)
- **Effect**: Removes progress bars and rich formatting

#### `--verbose` / `-v`
- **Type**: Boolean flag
- **Required**: No
- **Default**: False
- **Description**: Show detailed processing information
- **Effect**: Enables debug logging and detailed statistics

## 🚀 Usage Examples

### **Basic Usage**
```bash
# Minimum required arguments
context-ai generate ./my-project --name "project-v1"
```

### **All Flag Combinations**

#### **1. Basic with verbose**
```bash
context-ai generate ./my-project --name "project-v1" --verbose
```
**Output**: Detailed processing information, file counts, timing

#### **2. Basic with no progress**
```bash
context-ai generate ./my-project --name "project-v1" --no-progress
```
**Output**: Clean output without progress bars (good for scripts)

#### **3. With custom ignore file**
```bash
context-ai generate ./my-project --name "project-v1" --ignore-file .customignore
```
**Output**: Uses custom ignore patterns instead of defaults

#### **4. Verbose + no progress**
```bash
context-ai generate ./my-project --name "project-v1" --verbose --no-progress
```
**Output**: Detailed info but without fancy progress UI

#### **5. Custom ignore + verbose**
```bash
context-ai generate ./my-project --name "project-v1" --ignore-file .customignore --verbose
```
**Output**: Custom patterns with detailed processing info

#### **6. Custom ignore + no progress**
```bash
context-ai generate ./my-project --name "project-v1" --ignore-file .customignore --no-progress
```
**Output**: Custom patterns, clean output

#### **7. All options combined**
```bash
context-ai generate ./my-project --name "project-v1" --ignore-file .customignore --verbose --no-progress
```
**Output**: Maximum configuration - custom patterns, detailed info, clean output

### **Real-World Examples**

#### **Frontend Project**
```bash
context-ai generate ./frontend-app --name "frontend-2024" --verbose
```

#### **API Documentation**
```bash
context-ai generate ./api-docs --name "api-docs-v3" --ignore-file .docignore
```

#### **Large Codebase (CI/CD)**
```bash
context-ai generate ./large-project --name "main-codebase" --no-progress
```

#### **Design System**
```bash
context-ai generate ./design-system --name "ds-components" --verbose --ignore-file patterns/ignore-build.txt
```

## 📊 Output Examples

### **Standard Output**
```
🚀 Initializing generate command...
Loading embedding service...
Processing files from: ./my-project
Found 156 files to process
Generating embeddings: ████████████████████ 100% (156/156)
✅ Generated 1,243 chunks from 156 files
💾 Saved embedding set: project-v1
⏱️ Total time: 2m 34s
```

### **Verbose Output**
```
🚀 Initializing generate command...
🔧 Verbose mode enabled
Loading embedding service...
📁 Processing directory: ./my-project
📋 Using ignore patterns from: .gitignore
🔍 Scanning for supported files...
📊 File type breakdown:
  - JavaScript: 45 files
  - TypeScript: 32 files  
  - Markdown: 12 files
  - JSON: 8 files
  - CSS: 6 files
  - Other: 3 files
🔄 Processing files with langchain chunker...
📝 Generated chunks breakdown:
  - JavaScript: 456 chunks (avg 10.1 per file)
  - TypeScript: 389 chunks (avg 12.2 per file)
  - Markdown: 89 chunks (avg 7.4 per file)
  - JSON: 45 chunks (avg 5.6 per file)
  - CSS: 34 chunks (avg 5.7 per file)
🧮 Token statistics:
  - Total tokens: 234,567
  - Average per chunk: 188.7
  - Largest chunk: 1,456 tokens
✅ Generated 1,243 chunks from 156 files
💾 Saved embedding set: project-v1
⏱️ Total time: 2m 34s
📊 Performance: 1.0 files/second, 8.1 chunks/second
```

### **No Progress Output**
```
🚀 Initializing generate command...
Loading embedding service...
Processing files from: ./my-project
Found 156 files to process
Processing files...
✅ Generated 1,243 chunks from 156 files
💾 Saved embedding set: project-v1
⏱️ Total time: 2m 34s
```

## 🔧 File Processing Details

### **Supported File Types**
- **JavaScript**: `.js`, `.jsx`, `.mjs`
- **TypeScript**: `.ts`, `.tsx`
- **Python**: `.py`, `.pyx`, `.pyi`
- **Web**: `.html`, `.css`, `.scss`, `.sass`, `.less`
- **Markup**: `.md`, `.mdx`, `.markdown`
- **Data**: `.json`, `.yaml`, `.yml`
- **Configuration**: Many others (see constants.py)

### **Default Ignore Patterns**
```
# Version control
.git/
.svn/

# Dependencies  
node_modules/
__pycache__/
.venv/

# Build artifacts
dist/
build/
*.min.js
*.bundle.*

# IDE files
.vscode/
.idea/
*.swp

# Logs and temp
*.log
.cache/
tmp/
```

### **Custom Ignore File Format**
```bash
# .contextignore or custom ignore file
# Uses .gitignore syntax

# Ignore specific directories
build/
dist/
coverage/

# Ignore file patterns
*.test.js
*.spec.ts
*.min.*

# Include exceptions  
!important-config.json
!docs/*.md
```

## 🚨 Error Handling

### **Common Errors**

#### **Invalid Path**
```bash
context-ai generate ./nonexistent --name "test"
```
**Error**: `❌ Directory './nonexistent' does not exist`

#### **Missing Name**
```bash
context-ai generate ./my-project
```
**Error**: `❌ the following arguments are required: --name/-n`

#### **Invalid Ignore File**
```bash
context-ai generate ./my-project --name "test" --ignore-file ./missing.ignore
```
**Error**: `❌ Ignore file './missing.ignore' not found`

#### **Empty Directory**
```bash
context-ai generate ./empty-dir --name "test"
```
**Warning**: `⚠️ No supported files found in directory`

#### **Duplicate Name**
```bash
context-ai generate ./project --name "existing-name"
```
**Error**: `❌ Embedding 'existing-name' already exists`

#### **Permission Issues**
```bash
context-ai generate /restricted-path --name "test"
```
**Error**: `❌ Permission denied accessing directory`

### **Validation Rules**

#### **Embedding Name Validation**
- Must be 1-100 characters
- Alphanumeric, hyphens, underscores only
- Cannot start/end with hyphens
- Case sensitive

**Valid**: `frontend-v1`, `API_Backend`, `design_system_2024`  
**Invalid**: `-invalid`, `invalid-`, `with spaces`, `with/slash`

#### **Path Validation**
- Must exist and be readable
- Must be a directory (not a file)
- Must contain at least one supported file type

#### **Ignore File Validation**
- Must exist if specified
- Must be readable
- Uses standard .gitignore syntax

## 💡 Pro Tips

### **Performance Optimization**
```bash
# For large projects, use no-progress to avoid UI overhead
context-ai generate ./huge-project --name "large-v1" --no-progress

# Use verbose to identify performance bottlenecks
context-ai generate ./project --name "debug-v1" --verbose
```

### **CI/CD Integration**
```bash
# Perfect for automated builds
context-ai generate $PROJECT_PATH --name "${CI_COMMIT_SHA}" --no-progress
```

### **Custom Ignore Strategies**
```bash
# Create project-specific ignore patterns
echo "*.test.js\n*.spec.ts\nstorybook-static/" > .contextignore
context-ai generate . --name "clean-v1"
```

### **Incremental Updates**
```bash
# Generate with version suffixes for tracking
context-ai generate ./project --name "project-$(date +%Y%m%d)"
```

### **Development Workflow**
```bash
# Quick development embedding
context-ai generate ./src --name "dev-quick" --ignore-file dev.ignore

# Full project embedding
context-ai generate . --name "project-full" --verbose
```

## 🔍 Troubleshooting

### **Slow Processing**
- **Cause**: Large files or many files
- **Solution**: Use custom ignore file to exclude unnecessary files
- **Monitor**: Use `--verbose` to see processing statistics

### **Out of Memory**
- **Cause**: Very large files (>10MB)
- **Solution**: Add large files to ignore patterns
- **Check**: Files are automatically skipped if >10MB

### **No Files Found**
- **Cause**: All files ignored or unsupported file types
- **Solution**: Check ignore patterns and supported extensions
- **Debug**: Use `--verbose` to see file discovery process

### **Permission Errors**
- **Cause**: Insufficient read permissions
- **Solution**: Run with appropriate permissions or change directory ownership
- **Check**: Verify directory and file permissions

## 📈 Performance Characteristics

### **Processing Speed**
- **Small projects** (<100 files): ~30 seconds
- **Medium projects** (100-500 files): ~2-5 minutes  
- **Large projects** (500+ files): ~5-15 minutes

### **Memory Usage**
- **Typical**: ~200-500MB during processing
- **Large files**: Up to 1GB temporarily
- **After completion**: Minimal resident memory

### **Storage Requirements**
- **Vector embeddings**: ~1-5MB per 1000 chunks
- **Metadata**: ~100KB per embedding set
- **Total**: Usually 10-50MB per project

---

*This document provides complete documentation for the `generate` command. Use `context-ai generate --help` for quick reference.*
