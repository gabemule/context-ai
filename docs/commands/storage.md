# Storage Command Reference

> Complete documentation for the `context-ai storage` command - Manage storage and cleanup operations

## 🎯 Overview

The `storage` command manages Context-AI's storage system including embeddings, temporary files, and configuration data. It provides subcommands for viewing storage information, cleaning up old files, resetting the entire system, and deleting specific embeddings.

## 📋 Complete Syntax

```bash
context-ai storage <subcommand> [OPTIONS]
```

## 📝 Subcommands

### **Available Subcommands**

#### `info` - Show Storage Information
```bash
context-ai storage info [OPTIONS]
```

#### `cleanup` - Clean Up Temporary Files
```bash
context-ai storage cleanup [OPTIONS]
```

#### `reset` - Reset All Storage (DELETE EVERYTHING)
```bash
context-ai storage reset [OPTIONS]
```

#### `delete` - Delete Specific Embedding
```bash
context-ai storage delete <embedding_name> [OPTIONS]
```

## 📊 Info Subcommand

### **Syntax**
```bash
context-ai storage info [OPTIONS]
```

### **Options**

#### `--verbose` / `-v`
- **Type**: Boolean flag
- **Required**: No
- **Default**: False
- **Description**: Show detailed processing information
- **Effect**: Includes additional storage details and directory breakdown

### **Usage Examples**

#### **Basic Storage Information**
```bash
# Basic storage info
context-ai storage info

# Detailed storage info with verbose
context-ai storage info --verbose
```

## 🧹 Cleanup Subcommand

### **Syntax**
```bash
context-ai storage cleanup [OPTIONS]
```

### **Options**

#### `--hours`
- **Type**: Integer
- **Required**: No
- **Default**: 24
- **Description**: Remove temporary files older than N hours
- **Validation**: Must be positive integer
- **Examples**:
  - `--hours 48` (2 days)
  - `--hours 168` (1 week)

#### `--verbose` / `-v`
- **Type**: Boolean flag
- **Required**: No
- **Default**: False
- **Description**: Show detailed processing information
- **Effect**: Shows which files are being cleaned and reasons

### **Usage Examples**

#### **Cleanup Operations**
```bash
# Basic cleanup (24 hours default)
context-ai storage cleanup

# Cleanup files older than 48 hours
context-ai storage cleanup --hours 48

# Verbose cleanup with default time
context-ai storage cleanup --verbose

# Verbose cleanup with custom time
context-ai storage cleanup --hours 72 --verbose
```

## 🗑️ Delete Subcommand

### **Syntax**
```bash
context-ai storage delete <embedding_name> [OPTIONS]
```

### **Options**

#### `embedding_name` (Positional Argument)
- **Type**: String (embedding name)
- **Required**: Yes
- **Description**: Name of the embedding to delete
- **Validation**: Must be an existing embedding name
- **Examples**:
  - `frontend-v1`
  - `legacy-project`

#### `--verbose` / `-v`
- **Type**: Boolean flag
- **Required**: No
- **Default**: False
- **Description**: Show detailed processing information
- **Effect**: Shows detailed deletion process and file removal

### **Usage Examples**

#### **Delete Specific Embedding**
```bash
# Basic deletion
context-ai storage delete frontend-v1

# Verbose deletion
context-ai storage delete legacy-project --verbose
```

## 🚨 Reset Subcommand

### **Syntax**
```bash
context-ai storage reset [OPTIONS]
```

### **Options**

#### `--confirm`
- **Type**: Boolean flag
- **Required**: Yes (for safety)
- **Default**: False
- **Description**: Confirm the reset operation (required to prevent accidents)
- **Effect**: Actually performs the reset; without it, shows error

#### `--verbose` / `-v`
- **Type**: Boolean flag
- **Required**: No
- **Default**: False
- **Description**: Show detailed processing information
- **Effect**: Shows detailed deletion process and what's being removed

### **Usage Examples**

#### **Complete System Reset**
```bash
# Basic reset (requires confirm)
context-ai storage reset --confirm

# Verbose reset with detailed output
context-ai storage reset --confirm --verbose
```

## 🚀 All Usage Examples

### **Storage Management Workflow**
```bash
# 1. Check current storage
context-ai storage info --verbose

# 2. Clean up old files
context-ai storage cleanup --hours 48 --verbose

# 3. Delete specific embedding
context-ai storage delete old-project --verbose

# 4. Check storage after cleanup
context-ai storage info
```

### **All Flag Combinations**

#### **Info Command Variations**
```bash
# Basic info
context-ai storage info

# Verbose info
context-ai storage info --verbose
```

#### **Cleanup Command Variations**
```bash
# Basic cleanup (24h default)
context-ai storage cleanup

# Custom hours
context-ai storage cleanup --hours 48

# Verbose cleanup
context-ai storage cleanup --verbose

# Custom hours with verbose
context-ai storage cleanup --hours 72 --verbose
```

#### **Delete Command Variations**
```bash
# Basic delete
context-ai storage delete project-name

# Verbose delete
context-ai storage delete project-name --verbose
```

#### **Reset Command Variations**
```bash
# Basic reset (DANGEROUS)
context-ai storage reset --confirm

# Verbose reset (DANGEROUS)
context-ai storage reset --confirm --verbose
```

### **Maintenance Workflows**

#### **Regular Maintenance**
```bash
# Weekly cleanup
context-ai storage cleanup --hours 168 --verbose

# Check storage usage
context-ai storage info --verbose
```

#### **Project Cleanup**
```bash
# Remove old project versions
context-ai storage delete project-v1
context-ai storage delete project-v2
context-ai storage delete legacy-code

# Verify cleanup
context-ai storage info
```

#### **Complete Fresh Start**
```bash
# DANGEROUS: Complete reset
context-ai storage reset --confirm --verbose

# Verify everything is gone
context-ai storage info
```

## 📊 Output Examples

### **Info Command Output**
```bash
$ context-ai storage info

📊 Storage Information:
Base path: /Users/user/.context-ai
Total size: 245 MB
Embeddings count: 5
Available embeddings: frontend-v1, backend-v2, api-docs, design-system, legacy-code

Directory breakdown:
  embeddings: 220 MB
  config: 0.1 MB
  logs: 24.9 MB
```

### **Info Command Verbose Output**
```bash
$ context-ai storage info --verbose

🚀 Initializing storage command...
🔧 Verbose mode enabled
📊 Storage Information:

🏠 Base Directory:
  Path: /Users/user/.context-ai
  Total size: 245.3 MB
  Created: 2025-01-15 10:30:00
  Last accessed: 2025-01-25 15:45:00
  Permissions: drwx------ (700)

📦 Embeddings (5 total):
  ✅ frontend-v1: 45.2 MB, 153 chunks, 27 files, created 1 day ago
  ✅ backend-v2: 123.4 MB, 800 chunks, 45 files, created 3 days ago
  ✅ api-docs: 28.7 MB, 300 chunks, 12 files, created 1 week ago
  ✅ design-system: 67.3 MB, 450 chunks, 35 files, created 3 days ago
  ✅ legacy-code: 15.6 MB, 120 chunks, 8 files, created 1 month ago

📁 Directory Breakdown:
  embeddings/: 220.2 MB (89.8%)
  logs/: 24.9 MB (10.1%)
  config/: 0.1 MB (0.04%)
  temp/: 0.1 MB (0.04%)

📊 Health Status:
  - Storage accessible: ✅
  - Permissions correct: ✅
  - No corruption detected: ✅
  - Free space available: ✅ (15.2 GB remaining)
```

### **Cleanup Command Output**
```bash
$ context-ai storage cleanup --hours 48

🧹 Cleaning up temporary files older than 48 hours...
✅ Cleaned up 3 temporary files
```

### **Cleanup Command Verbose Output**
```bash
$ context-ai storage cleanup --hours 48 --verbose

🚀 Initializing storage command...
🔧 Verbose mode enabled
🧹 Cleaning up temporary files older than 48 hours...

🔍 Scanning for temporary files...
📁 Checking directory: /Users/user/.context-ai/temp/
📁 Checking directory: /Users/user/.context-ai/logs/

🗑️ Files to be cleaned:
  - temp/chunk_cache_2025-01-23.tmp (2 days old, 1.2 MB)
  - temp/embedding_temp_xyz.tmp (3 days old, 0.8 MB)
  - logs/debug_2025-01-22.log (3 days old, 15.3 MB)

🗑️ Removing files...
  ✅ Deleted: temp/chunk_cache_2025-01-23.tmp
  ✅ Deleted: temp/embedding_temp_xyz.tmp
  ✅ Deleted: logs/debug_2025-01-22.log

✅ Cleaned up 3 temporary files
💾 Freed up 17.3 MB of disk space
📊 Remaining storage: 228.0 MB
```

### **Delete Command Output**
```bash
$ context-ai storage delete legacy-code

🗑️ Deleting embedding: legacy-code
✅ Embedding 'legacy-code' deleted successfully
```

### **Delete Command Verbose Output**
```bash
$ context-ai storage delete legacy-code --verbose

🚀 Initializing storage command...
🔧 Verbose mode enabled
🗑️ Deleting embedding: legacy-code

🔍 Validating embedding exists...
✅ Found embedding: legacy-code (15.6 MB, 120 chunks, 8 files)

📊 Embedding Details:
  Created: 2025-01-05 14:20:00
  Last used: 2025-01-20 09:15:00
  Size: 15.6 MB
  Files: src/legacy/*.py, docs/old/*.md

🗑️ Removing files...
  🗑️ Deleting: embeddings/legacy-code/vectors.pkl
  🗑️ Deleting: embeddings/legacy-code/metadata.json
  🗑️ Deleting: embeddings/legacy-code/chunks.json
  🗑️ Deleting: embeddings/legacy-code/ (directory)

💾 Updating configuration...
  📝 Removing from available embeddings list
  📝 Removing from active selection (if selected)

✅ Embedding 'legacy-code' deleted successfully
💾 Freed up 15.6 MB of disk space
📊 Remaining embeddings: 4 (229.7 MB total)
```

### **Reset Command Output**
```bash
$ context-ai storage reset --confirm

🚨 RESETTING ALL STORAGE - This will delete everything!
✅ Storage reset complete
```

### **Reset Command Verbose Output**
```bash
$ context-ai storage reset --confirm --verbose

🚀 Initializing storage command...
🔧 Verbose mode enabled
🚨 RESETTING ALL STORAGE - This will delete everything!

⚠️ WARNING: This will permanently delete:
  - 5 embeddings (245.3 MB)
  - All configuration files
  - All logs and temporary files
  - Active embedding selections

🗑️ Beginning reset process...

📦 Deleting embeddings...
  🗑️ Deleting: frontend-v1 (45.2 MB)
  🗑️ Deleting: backend-v2 (123.4 MB)  
  🗑️ Deleting: api-docs (28.7 MB)
  🗑️ Deleting: design-system (67.3 MB)
  🗑️ Deleting: legacy-code (15.6 MB)

📁 Deleting configuration...
  🗑️ Deleting: config.json
  🗑️ Deleting: active.json

📋 Deleting logs...
  🗑️ Deleting: logs/ directory (24.9 MB)

🗂️ Deleting temporary files...
  🗑️ Deleting: temp/ directory (0.1 MB)

🏠 Recreating base directory structure...
  📁 Creating: /Users/user/.context-ai/
  📁 Creating: /Users/user/.context-ai/embeddings/
  📁 Creating: /Users/user/.context-ai/logs/

✅ Storage reset complete
💾 Freed up 245.3 MB of disk space
📊 Storage is now empty and ready for use
```

## 🚨 Error Handling

### **Info Command Errors**

#### **Storage Access Error**
```bash
context-ai storage info
```
**Error**: `❌ Error getting storage info: Permission denied`

### **Cleanup Command Errors**

#### **Invalid Hours Value**
```bash
context-ai storage cleanup --hours -5
```
**Error**: `❌ Hours must be a positive integer`

#### **Storage Access Error**
```bash
context-ai storage cleanup
```
**Error**: `❌ Unable to access storage directory for cleanup`

### **Delete Command Errors**

#### **Embedding Not Found**
```bash
context-ai storage delete nonexistent-project
```
**Error**: `❌ Embedding 'nonexistent-project' does not exist`

#### **Deletion Failed**
```bash
context-ai storage delete project-name  # Permission issues
```
**Error**: `❌ Failed to delete embedding 'project-name': Permission denied`

### **Reset Command Errors**

#### **Missing Confirm Flag**
```bash
context-ai storage reset
```
**Error**: 
```
❌ Reset requires --confirm flag
⚠️ This will DELETE ALL embeddings, configuration, and data!
Usage: context-ai storage reset --confirm
```

#### **Reset Failed**
```bash
context-ai storage reset --confirm  # Permission issues
```
**Error**: `❌ Storage reset failed: Unable to delete files`

## 💡 Pro Tips

### **Regular Maintenance**
```bash
# Weekly cleanup routine
context-ai storage cleanup --hours 168 --verbose
context-ai storage info --verbose

# Create maintenance script
#!/bin/bash
echo "Running weekly Context-AI maintenance..."
context-ai storage cleanup --hours 168
context-ai storage info
```

### **Before Major Operations**
```bash
# Check storage before generating new embeddings
context-ai storage info --verbose

# Clean up space if needed
context-ai storage cleanup --hours 72 --verbose
```

### **Project Management**
```bash
# Remove old project versions systematically
for version in v1 v2 v3; do
  context-ai storage delete "project-$version" --verbose
done

# Verify cleanup
context-ai storage info
```

### **Backup Strategy**
```bash
# Manual backup (copy entire directory)
cp -r ~/.context-ai ~/.context-ai-backup-$(date +%Y%m%d)

# Verify backup
ls -la ~/.context-ai-backup-*
```

### **Disk Space Management**
```bash
# Check available space before operations
df -h ~/.context-ai

# Clean up aggressively if low on space
context-ai storage cleanup --hours 24 --verbose

# Remove unused embeddings
context-ai storage delete old-project-1
context-ai storage delete old-project-2
```

## 🔍 Storage Structure Details

### **Directory Layout**
```
~/.context-ai/
├── config.json                    # Main configuration
├── active.json                   # Active embedding selection
├── embeddings/                   # Embedding data
│   ├── frontend-v1/
│   │   ├── vectors.pkl          # Vector embeddings
│   │   ├── metadata.json        # File metadata
│   │   └── chunks.json          # Text chunks
│   └── backend-v2/
│       ├── vectors.pkl
│       ├── metadata.json
│       └── chunks.json
├── logs/                         # Application logs
│   ├── context-ai.log
│   └── debug_YYYY-MM-DD.log
└── temp/                         # Temporary files
    ├── chunk_cache_*.tmp
    └── embedding_temp_*.tmp
```

### **File Types and Cleanup**
- **Vectors (*.pkl)**: Permanent until embedding deleted
- **Metadata (*.json)**: Permanent until embedding deleted
- **Logs (*.log)**: Cleaned up based on age
- **Temp files (*.tmp)**: Cleaned up based on age
- **Cache files**: Cleaned up based on age

### **Storage Optimization**
- **Embeddings**: 80-95% of total storage
- **Logs**: 5-15% of total storage
- **Config**: <1% of total storage
- **Temp**: <1% of total storage (varies)

## 📈 Performance Characteristics

### **Command Performance**
- **Info**: <0.1 seconds (directory scan)
- **Cleanup**: 0.1-2 seconds (depends on file count)
- **Delete**: 0.1-1 seconds (depends on embedding size)
- **Reset**: 1-10 seconds (depends on total storage size)

### **Storage Growth Patterns**
- **Small project**: 10-50 MB per embedding
- **Medium project**: 50-200 MB per embedding
- **Large project**: 200-1000 MB per embedding
- **Logs**: ~1-5 MB per day of usage

### **Cleanup Efficiency**
- **Temp files**: Usually small (<1 MB each)
- **Log files**: Can be large (10-100 MB each)
- **Cache files**: Medium size (1-10 MB each)

## 🔗 Integration with Other Commands

### **Pre-Generation Cleanup**
```bash
# Clean up before generating large embedding
context-ai storage cleanup --hours 48
context-ai storage info
context-ai generate ./large-project --name "large-v1"
```

### **Post-Development Cleanup**
```bash
# After switching projects
context-ai storage delete old-frontend
context-ai storage delete old-backend
context-ai storage cleanup --hours 24
context-ai select new-project
```

### **System Health Check**
```bash
# Complete system health check
context-ai storage info --verbose
context-ai config validate --verbose
context-ai storage cleanup --hours 72 --verbose
```

### **Migration Workflow**
```bash
# Before major update or migration
context-ai storage info --verbose > storage-backup-info.txt
# ... perform migration ...
context-ai storage info --verbose
```

## ⚠️ Safety Considerations

### **Reset Command Safety**
- **DESTRUCTIVE**: `reset` command permanently deletes everything
- **Confirmation required**: Must use `--confirm` flag
- **No recovery**: No built-in backup or recovery
- **Manual backup**: Copy `~/.context-ai/` before reset

### **Delete Command Safety**
- **Permanent**: Deleted embeddings cannot be recovered
- **Active embeddings**: Automatically removed from active selection
- **Validation**: Checks embedding exists before deletion

### **Cleanup Command Safety**
- **Safe**: Only removes temporary files and old logs
- **Preserves**: All embeddings and configuration
- **Reversible**: Generally safe to run

---

*This document provides complete documentation for the `storage` command. Use `context-ai storage --help` for quick reference.*
