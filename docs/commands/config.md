# Config Command Reference

> Complete documentation for the `context-ai config` command - Manage configuration settings

## 🎯 Overview

The `config` command manages Context-AI configuration settings including API keys, preferences, and system validation. It provides subcommands for setting values, listing current configuration, testing connectivity, and validating the complete setup.

## 📋 Complete Syntax

```bash
context-ai config <subcommand> [OPTIONS]
```

## 📝 Subcommands

### **Available Subcommands**

#### `set` - Set Configuration Values
```bash
context-ai config set [OPTIONS]
```

#### `list` - List Current Configuration  
```bash
context-ai config list [OPTIONS]
```

#### `test` - Test API Key Connectivity
```bash
context-ai config test [OPTIONS]
```

#### `validate` - Validate Complete Configuration
```bash
context-ai config validate [OPTIONS]
```

## 🔧 Set Subcommand

### **Syntax**
```bash
context-ai config set [OPTIONS]
```

### **Options**

#### `--claude-key`
- **Type**: String (API key)
- **Required**: No (but must provide at least one option)
- **Description**: Set Claude API key for AI functionality
- **Validation**: Must start with `sk-ant-` (Anthropic format)
- **Security**: Stored securely in user config directory
- **Example**: `--claude-key sk-ant-api03-your-key-here`

#### `--verbose` / `-v`
- **Type**: Boolean flag
- **Required**: No
- **Default**: False
- **Description**: Show detailed processing information
- **Effect**: Enables debug logging during configuration

### **Usage Examples**

#### **Set Claude API Key**
```bash
# Set API key
context-ai config set --claude-key sk-ant-api03-your-actual-key-here

# Set with verbose output
context-ai config set --claude-key sk-ant-api03-your-key --verbose
```

## 📋 List Subcommand

### **Syntax**
```bash
context-ai config list [OPTIONS]
```

### **Options**

#### `--verbose` / `-v`
- **Type**: Boolean flag
- **Required**: No
- **Default**: False
- **Description**: Show detailed processing information
- **Effect**: Includes additional configuration details

### **Usage Examples**

#### **List Configuration**
```bash
# Basic configuration list
context-ai config list

# Detailed configuration with verbose
context-ai config list --verbose
```

## 🔍 Test Subcommand

### **Syntax**
```bash
context-ai config test [OPTIONS]
```

### **Options**

#### `--verbose` / `-v`
- **Type**: Boolean flag
- **Required**: No
- **Default**: False
- **Description**: Show detailed processing information
- **Effect**: Shows connection details and timing

### **Usage Examples**

#### **Test API Connectivity**
```bash
# Basic connectivity test
context-ai config test

# Detailed connectivity test
context-ai config test --verbose
```

## ✅ Validate Subcommand

### **Syntax**
```bash
context-ai config validate [OPTIONS]
```

### **Options**

#### `--verbose` / `-v`
- **Type**: Boolean flag
- **Required**: No
- **Default**: False
- **Description**: Show detailed processing information
- **Effect**: Shows comprehensive validation details

### **Usage Examples**

#### **Validate Complete Setup**
```bash
# Basic validation
context-ai config validate

# Detailed validation with verbose
context-ai config validate --verbose
```

## 🚀 All Usage Examples

### **Complete Setup Workflow**
```bash
# 1. Set API key
context-ai config set --claude-key sk-ant-api03-your-key

# 2. Test connectivity
context-ai config test

# 3. Validate complete setup
context-ai config validate

# 4. View final configuration
context-ai config list
```

### **All Flag Combinations**

#### **Set Command Variations**
```bash
# Basic set
context-ai config set --claude-key sk-ant-api03-key

# Set with verbose
context-ai config set --claude-key sk-ant-api03-key --verbose
```

#### **List Command Variations**
```bash
# Basic list
context-ai config list

# Verbose list
context-ai config list --verbose
```

#### **Test Command Variations**
```bash
# Basic test
context-ai config test

# Verbose test
context-ai config test --verbose
```

#### **Validate Command Variations**
```bash
# Basic validate
context-ai config validate

# Verbose validate
context-ai config validate --verbose
```

### **Troubleshooting Workflow**
```bash
# Check current config
context-ai config list --verbose

# Test API connectivity
context-ai config test --verbose

# Run full validation
context-ai config validate --verbose

# Fix issues and re-test
context-ai config set --claude-key new-key
context-ai config test
```

## 📊 Output Examples

### **Set Command Output**
```bash
$ context-ai config set --claude-key sk-ant-api03-example

🔑 Setting Claude API key...
✅ Claude API key configured successfully
```

### **Set Command Verbose Output**
```bash
$ context-ai config set --claude-key sk-ant-api03-example --verbose

🚀 Initializing config command...
🔧 Verbose mode enabled
🔑 Setting Claude API key...
📁 Config directory: /Users/user/.context-ai
💾 Saving configuration to: /Users/user/.context-ai/config.json
🔒 API key stored securely (masked: sk-ant-***-example)
✅ Claude API key configured successfully
```

### **List Command Output**
```bash
$ context-ai config list

📋 Current configuration:
Storage path: /Users/user/.context-ai
Active provider: claude
System prompt strategy: general_assistant_with_reusability_focus
Claude model: claude-4
Claude max tokens: 200000
Claude API key: ***configured***
Active embeddings: frontend-v1, backend-v2
```

### **List Command Verbose Output**
```bash
$ context-ai config list --verbose

🚀 Initializing config command...
🔧 Verbose mode enabled
📋 Current configuration:

🏠 Storage Configuration:
  Base path: /Users/user/.context-ai
  Config file: /Users/user/.context-ai/config.json
  Storage size: 245 MB
  Last accessed: 2025-01-25 15:30:00

🤖 AI Configuration:
  Active provider: claude
  System prompt strategy: general_assistant_with_reusability_focus
  
🔮 Claude Configuration:
  Model: claude-4 (claude-sonnet-4-20250514)
  Max tokens: 200000
  Max retries: 3
  Timeout: 60.0s
  API key: ***configured*** (sk-ant-***-ending)
  
📊 Active Embeddings:
  Selected: frontend-v1, backend-v2
  Total available: 5 embeddings
  Selection file: /Users/user/.context-ai/active.json
  Last updated: 2025-01-25 14:45:00
```

### **Test Command Output**
```bash
$ context-ai config test

🔍 Testing API key connectivity...
✅ Claude API key is valid and working
```

### **Test Command Verbose Output**
```bash
$ context-ai config test --verbose

🚀 Initializing config command...
🔧 Verbose mode enabled
🔍 Testing API key connectivity...
📊 API Configuration:
  Model: claude-4
  Endpoint: https://api.anthropic.com/v1
  Key format: Valid (sk-ant-***-ending)
  
🔗 Testing connection...
📡 Sending test request to Claude API...
⏱️ Response received in 1.2 seconds
✅ Claude API key is valid and working

📊 Connection Details:
  Model used: claude-sonnet-4-20250514
  Test tokens: 15 input, 8 output
  Latency: 1.2s
  Status: Healthy
```

### **Validate Command Output**
```bash
$ context-ai config validate

🔧 Validating configuration...
✅ Claude API key configured
✅ Active embeddings: frontend-v1, backend-v2
✅ Storage: 5 embeddings available
✅ Configuration is valid and ready to use!
```

### **Validate Command Verbose Output**
```bash
$ context-ai config validate --verbose

🚀 Initializing config command...
🔧 Verbose mode enabled
🔧 Validating configuration...

🔑 API Key Validation:
  ✅ Claude API key is configured
  ✅ Key format is valid (sk-ant-***-ending)
  ✅ Key length: 108 characters
  
📊 Embeddings Validation:
  ✅ Active embeddings selected: frontend-v1, backend-v2
  ✅ frontend-v1: 153 chunks, 27 files (healthy)
  ✅ backend-v2: 800 chunks, 45 files (healthy)
  
💾 Storage Validation:
  ✅ Storage directory exists: /Users/user/.context-ai
  ✅ Storage is writable
  ✅ 5 embeddings available (245 MB total)
  ✅ Configuration files valid
  
🔗 Connectivity Validation:
  🔍 Testing Claude API connection...
  ✅ API connection successful (1.1s response)
  ✅ Model access confirmed: claude-4
  
✅ Configuration is valid and ready to use!

📊 System Status:
  - API: Ready ✅
  - Storage: Ready ✅  
  - Embeddings: 2 active ✅
  - Total health: 100% ✅
```

## 🚨 Error Handling

### **Set Command Errors**

#### **No Options Provided**
```bash
context-ai config set
```
**Error**: `❌ No configuration option provided`

#### **Invalid API Key Format**
```bash
context-ai config set --claude-key invalid-key-format
```
**Error**: `❌ Claude API key format invalid (must start with sk-ant-)`

#### **Storage Permission Error**
```bash
context-ai config set --claude-key sk-ant-valid-key
```
**Error**: `❌ Unable to save configuration: Permission denied`

### **List Command Errors**

#### **Configuration Access Error**
```bash
context-ai config list
```
**Error**: `❌ Unable to read configuration file: File not found`

### **Test Command Errors**

#### **No API Key Configured**
```bash
context-ai config test
```
**Error**: 
```
❌ No Claude API key configured
Set your API key with: context-ai config set --claude-key YOUR_KEY
```

#### **Invalid API Key**
```bash
context-ai config test  # With invalid key
```
**Error**: `❌ Claude API key validation failed`

#### **Network Connection Error**
```bash
context-ai config test  # Network issues
```
**Error**: `❌ Error testing connection: Connection timeout`

### **Validate Command Errors**

#### **Multiple Configuration Issues**
```bash
context-ai config validate  # Various issues
```
**Error**:
```
Configuration issues found:
  ❌ Claude API key not set
  ⚠️ No active embeddings selected
  ⚠️ No embeddings generated yet
```

## 💡 Pro Tips

### **Initial Setup**
```bash
# Complete setup in one workflow
context-ai config set --claude-key sk-ant-your-key --verbose
context-ai config test --verbose
context-ai config validate --verbose
```

### **Troubleshooting**
```bash
# Diagnose issues step by step
context-ai config list --verbose       # Check current state
context-ai config test --verbose       # Test connectivity  
context-ai config validate --verbose   # Full system check
```

### **Security Best Practices**
```bash
# Verify key is set correctly
context-ai config list | grep "Claude API key"

# Test immediately after setting
context-ai config set --claude-key your-key && context-ai config test
```

### **Automation Scripts**
```bash
#!/bin/bash
# Automated setup script

if [ -z "$CLAUDE_API_KEY" ]; then
  echo "Error: CLAUDE_API_KEY environment variable not set"
  exit 1
fi

# Set API key from environment
context-ai config set --claude-key "$CLAUDE_API_KEY"

# Validate setup
if context-ai config validate; then
  echo "✅ Context-AI configured successfully"
else
  echo "❌ Configuration failed"
  exit 1
fi
```

### **CI/CD Integration**
```bash
# In CI/CD pipeline
export CLAUDE_API_KEY="${SECRET_CLAUDE_KEY}"
context-ai config set --claude-key "$CLAUDE_API_KEY"
context-ai config validate || exit 1
```

## 🔍 Configuration Details

### **Storage Locations**
- **Config file**: `~/.context-ai/config.json`
- **Active embeddings**: `~/.context-ai/active.json`
- **Embeddings data**: `~/.context-ai/embeddings/`
- **Logs**: `~/.context-ai/logs/`

### **Configuration Structure**
```json
{
  "storage": {
    "base_path": "/Users/user/.context-ai"
  },
  "active_provider": "claude",
  "system_prompt_strategy": "general_assistant_with_reusability_focus",
  "ai": {
    "claude": {
      "api_key": "sk-ant-***-encrypted",
      "default_model": "claude-4",
      "max_tokens": 200000
    }
  }
}
```

### **Security Considerations**
- API keys are stored in user directory with restricted permissions
- Keys are masked in output displays
- Configuration files are readable only by user
- No API keys logged in verbose output

## 📈 Performance Characteristics

### **Command Performance**
- **Set**: <0.1 seconds (file write)
- **List**: <0.1 seconds (file read)
- **Test**: 1-3 seconds (API request)
- **Validate**: 1-5 seconds (comprehensive check)

### **Storage Requirements**
- **Config file**: <1KB
- **Active embeddings**: <1KB
- **Total config overhead**: <10KB

### **API Usage**
- **Test command**: ~15 tokens per test
- **Validate command**: ~15 tokens if connectivity test included
- **No tokens used**: Set and list commands

## 🔗 Integration with Other Commands

### **Setup Workflow**
```bash
# 1. Configure
context-ai config set --claude-key your-key

# 2. Generate embeddings
context-ai generate ./project --name "my-project"

# 3. Select for use
context-ai select my-project

# 4. Validate complete setup
context-ai config validate
```

### **Troubleshooting Workflow**
```bash
# Check configuration
context-ai config list --verbose

# Test connectivity
context-ai config test --verbose

# Validate complete system
context-ai config validate --verbose

# Test actual functionality
context-ai ask "test question" --verbose
```

---

*This document provides complete documentation for the `config` command. Use `context-ai config --help` for quick reference.*
