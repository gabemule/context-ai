# 🌐 How to Add New Programming Languages

## Complete Guide to Language Configuration System

### 📚 **Context**: This system manages programming language detection, file extensions, and text chunking for Context-AI

---

## 🚀 **Quick Start**

### **What is the Languages System?**

The languages system provides:
- **File extension detection** - Which files belong to which languages
- **Text chunking separators** - How to intelligently split code for processing
- **Language inheritance** - Reuse configurations between similar languages
- **Priority management** - Define processing priorities for different languages

### **Why This System Matters?**

- ✅ **Intelligent chunking** - Better code understanding through proper separation
- ✅ **Extensible design** - Easy to add new languages without code changes
- ✅ **Inheritance support** - Avoid duplication with language families
- ✅ **Priority handling** - Optimize processing for critical languages

---

## 📋 **Step-by-Step Process**

### **🔍 Step 1: Understand the Language**

#### **1.1 Language Analysis**
```bash
# Essential questions to answer:
- What file extensions does this language use?
- What are the main structural elements (functions, classes, etc.)?
- How should code be logically separated for chunking?
- Does it extend/inherit from another language (like TypeScript from JavaScript)?
- What's the processing priority for this language?
```

#### **1.2 Chunking Strategy**
```bash
# Think about logical separation points:
- Function definitions
- Class declarations
- Import/export statements
- Major structural blocks
- Documentation sections
```

### **⚙️ Step 2: Choose Configuration Approach**

#### **2.1 New Language (from scratch)**
```yaml
new_language:
  name: "Language Name"
  extensions: [".ext1", ".ext2"]
  separators: ["\nfunction ", "\nclass ", "\n\n", "\n", " ", ""]
  chunking_priority: "medium"
```

#### **2.2 Inherited Language (extends existing)**
```yaml
new_language:
  name: "Extended Language"
  extends: "base_language"
  extensions: [".newext"]
  additional_separators: ["\nspecial_construct "]
  chunking_priority: "high"
```

### **📝 Step 3: Add to languages.yaml**

#### **3.1 Basic Language Entry**
```yaml
# Add to src/config/languages/languages.yaml
languages:
  your_language:
    name: "Your Language"
    extensions: 
      - ".ext"
      - ".extension"
    separators:
      - "\nfunction "      # Function definitions
      - "\nclass "         # Class definitions
      - "\nimport "        # Import statements
      - "\n\n"            # Double newlines
      - "\n"              # Single newlines  
      - " "               # Spaces
      - ""                # Character level (fallback)
    chunking_priority: "medium"  # high, medium, or low
```

#### **3.2 Inherited Language Entry**
```yaml
# Example: TypeScript extends JavaScript
typescript:
  name: "TypeScript"
  extends: "javascript"           # Inherits all JavaScript config
  extensions:
    - ".ts"
    - ".tsx"
    - ".d.ts"
  additional_separators:          # Added to JavaScript separators
    - "\ninterface "
    - "\ntype "
    - "\nenum "
  chunking_priority: "high"
```

### **🎯 Step 4: Configure Properties**

#### **4.1 Extensions**
```yaml
extensions:
  - ".py"          # Main extension
  - ".pyi"         # Interface files
  - ".pyx"         # Cython files
  - ".pyw"         # Windows Python files
```

#### **4.2 Separators (Order Matters!)**
```yaml
separators:
  # 1. High-level structures (most important)
  - "\nclass "           # Class definitions
  - "\ndef "             # Function definitions
  - "\nasync def "       # Async functions
  
  # 2. Module-level constructs
  - "\nfrom "            # Import statements
  - "\nimport "          # Import statements
  - "\nif __name__"      # Main blocks
  
  # 3. General separators (fallback)
  - "\n\n"              # Paragraph breaks
  - "\n"                # Line breaks
  - " "                 # Word breaks
  - ""                  # Character level (last resort)
```

#### **4.3 Chunking Priority**
```yaml
chunking_priority: "high"    # "high", "medium", or "low"

# Guidelines:
# - high: Core programming languages (Python, JavaScript, TypeScript)
# - medium: Secondary languages and frameworks (Go, Rust, Vue)
# - low: Configuration and markup languages (JSON, XML, CSS)
```

### **✅ Step 5: Test Integration**

#### **5.1 Basic Testing**
```bash
# Test language recognition
context-ai config languages

# Test specific language config
context-ai config languages your_language

# Test file extension detection
# (Create a test file with your language extension)
```

#### **5.2 Validation Checklist**
- [ ] **Extensions defined**: All relevant file extensions included
- [ ] **Separators ordered**: Most specific to most general
- [ ] **Priority set**: Appropriate chunking priority assigned
- [ ] **Inheritance works**: If using extends, base language exists
- [ ] **No conflicts**: Extensions don't conflict with existing languages
- [ ] **YAML valid**: Configuration parses without errors

---

## 💡 **Practical Examples**

### **🚀 Example 1: Adding Go Language**

#### **Analysis:**
```
Language: Go
Extensions: .go
Main constructs: func, type, var, const, package, import
Priority: medium (systems language)
```

#### **Configuration:**
```yaml
go:
  name: "Go"
  extensions:
    - ".go"
  separators:
    - "\nfunc "          # Function definitions
    - "\ntype "          # Type definitions  
    - "\nvar "           # Variable declarations
    - "\nconst "         # Constants
    - "\npackage "       # Package declarations
    - "\nimport "        # Import statements
    - "\nstruct "        # Struct definitions
    - "\ninterface "     # Interface definitions
    - "\n\n"            # Paragraph breaks
    - "\n"              # Line breaks
    - " "               # Word breaks
    - ""                # Character level
  chunking_priority: "medium"
```

### **🎨 Example 2: Adding Svelte (inherits from JavaScript)**

#### **Analysis:**
```
Language: Svelte
Base: JavaScript (similar syntax and concepts)
Extensions: .svelte
Additional constructs: <script>, <style>, component structure
Priority: medium (framework)
```

#### **Configuration:**
```yaml
svelte:
  name: "Svelte"
  extends: "javascript"         # Inherit JavaScript separators
  extensions:
    - ".svelte"
  additional_separators:        # Add Svelte-specific separators
    - "\n<script"              # Script sections
    - "\n<style"               # Style sections
  chunking_priority: "medium"
```

### **⚡ Example 3: Adding Assembly Language**

#### **Analysis:**
```
Language: Assembly
Extensions: .asm, .s, .S
Main constructs: labels, directives, sections
Priority: low (specialized use)
```

#### **Configuration:**
```yaml
assembly:
  name: "Assembly"
  extensions:
    - ".asm"
    - ".s"
    - ".S"
  separators:
    - "\n.section"       # Section directives
    - "\n.text"          # Text section
    - "\n.data"          # Data section
    - "\n.global"        # Global symbols
    - "\n:"              # Labels (ending with :)
    - "\n\n"            # Paragraph breaks
    - "\n"              # Line breaks
    - " "               # Word breaks
    - ""                # Character level
  chunking_priority: "low"
```

---

## 🛠️ **Advanced Configurations**

### **🔗 Language Inheritance**

#### **How Inheritance Works:**
```yaml
# Base language
javascript:
  name: "JavaScript"
  extensions: [".js", ".jsx"]
  separators: ["\nfunction ", "\nclass ", "\n\n", "\n", " ", ""]

# Inherited language
typescript:
  name: "TypeScript"
  extends: "javascript"              # Inherits ALL JavaScript config
  extensions: [".ts", ".tsx"]        # OVERRIDES JavaScript extensions
  additional_separators:             # ADDS to JavaScript separators
    - "\ninterface "
    - "\ntype "
  chunking_priority: "high"          # OVERRIDES JavaScript priority
```

#### **Inheritance Rules:**
- **extends**: Language to inherit from
- **extensions**: Completely replaces base extensions
- **separators**: If not specified, inherits base separators
- **additional_separators**: Adds to base separators (at the beginning)
- **chunking_priority**: Overrides base priority

### **📊 Priority Guidelines**

#### **High Priority** (`"high"`)
```yaml
# Use for core development languages
languages_high_priority:
  - python      # Core scripting
  - javascript  # Web development
  - typescript  # Type-safe web development
  - java        # Enterprise development
```

#### **Medium Priority** (`"medium"`)
```yaml
# Use for secondary languages and frameworks
languages_medium_priority:
  - go          # Systems programming
  - rust        # Systems programming
  - cpp         # Systems programming
  - vue         # Frontend framework
  - html        # Markup
```

#### **Low Priority** (`"low"`)
```yaml
# Use for configuration and data languages
languages_low_priority:
  - json        # Configuration
  - yaml        # Configuration
  - css         # Styling
  - xml         # Data
  - sql         # Database
```

---

## 🔧 **System Integration**

### **📋 Files That Will Be Updated**

When you add a language to `languages.yaml`, the system automatically:

1. **Copies to user config cache** - Your language becomes available to all Context-AI operations
2. **Updates extension mappings** - File detection works immediately
3. **Enables chunking** - Text processing uses your separators
4. **Guideline integration** - Can reference guidelines if available

### **📂 File Locations**

```bash
# Source configuration (edit this)
src/config/languages/languages.yaml

# User cache (automatically copied)
~/.context-ai/config/languages.yaml

# Guidelines (if available)
src/config/guidelines/your_language.md
~/.context-ai/config/guidelines/your_language.md
```

### **🔄 Testing Commands**

```bash
# List all languages
context-ai config languages

# Show specific language configuration  
context-ai config languages python

# Test with a file
echo "print('hello')" > test.py
# Context-AI will automatically detect it as Python

# Check chunking
context-ai query "test patterns" --files="*.py"
```

---

## 🚨 **Troubleshooting**

### **❌ Common Issues**

#### **Problem: Language not detected**
```yaml
# ❌ Wrong: Missing dot in extension
extensions: ["py", "js"]

# ✅ Correct: Extensions must start with dot
extensions: [".py", ".js"]
```

#### **Problem: Poor chunking quality**
```yaml
# ❌ Wrong: Generic separators only
separators: ["\n", " ", ""]

# ✅ Correct: Language-specific separators first
separators: ["\ndef ", "\nclass ", "\n\n", "\n", " ", ""]
```

#### **Problem: Inheritance not working**
```yaml
# ❌ Wrong: Base language doesn't exist
extends: "nonexistent_language"

# ✅ Correct: Base language must be defined first
extends: "javascript"
```

#### **Problem: Invalid YAML**
```yaml
# ❌ Wrong: Inconsistent indentation
languages:
  python:
    name: "Python"
  extensions:      # Wrong indentation!
    - ".py"

# ✅ Correct: Consistent indentation
languages:
  python:
    name: "Python"
    extensions:
      - ".py"
```

### **🔍 Validation Steps**

#### **1. YAML Syntax Check**
```bash
# Use YAML validator
python -c "import yaml; yaml.safe_load(open('src/config/languages/languages.yaml'))"
```

#### **2. Extension Conflicts**
```bash
# Check for duplicate extensions
context-ai config languages --validate
```

#### **3. Inheritance Chain**
```bash
# Verify inheritance resolves
context-ai config languages your_language
```

---

## 📊 **Configuration Reference**

### **🔧 Complete Schema**

```yaml
languages:
  language_name:                    # Unique identifier (snake_case)
    name: "Display Name"            # Human-readable name
    extensions:                     # List of file extensions
      - ".ext1"
      - ".ext2" 
    separators:                     # Text chunking separators (order matters)
      - "\nhigh_priority_construct "
      - "\nmedium_priority_construct "
      - "\n\n"                     # Always include paragraph breaks
      - "\n"                       # Always include line breaks
      - " "                        # Always include word breaks
      - ""                         # Always include character level
    chunking_priority: "medium"     # "high", "medium", or "low"
    
    # Optional inheritance
    extends: "base_language"         # Language to inherit from
    additional_separators:           # Additional separators (optional)
      - "\nspecial_construct "

# Global settings
settings:
  default_chunking_priority: "low"  # Default for new languages
  auto_detect_languages: true       # Enable auto-detection
  cache_language_configs: true      # Cache loaded configs
  reload_on_change: true           # Reload when files change
```

### **🎯 Best Practices**

#### **Extension Naming**
```yaml
# ✅ Good: Include all common extensions
extensions: [".py", ".pyi", ".pyx", ".pyw"]

# ❌ Bad: Missing important extensions
extensions: [".py"]
```

#### **Separator Ordering**
```yaml
# ✅ Good: Most specific to most general
separators:
  - "\nclass "        # Specific to language
  - "\ndef "          # Specific to language
  - "\n\n"           # General structure
  - "\n"             # General structure
  - " "              # Word boundaries
  - ""               # Character level

# ❌ Bad: Random order
separators: ["\n", "\nclass ", " ", "\ndef ", ""]
```

#### **Inheritance Usage**
```yaml
# ✅ Good: Use inheritance for similar languages
typescript:
  extends: "javascript"
  extensions: [".ts", ".tsx"]
  additional_separators: ["\ninterface "]

# ❌ Bad: Duplicate entire configuration
typescript:
  extensions: [".ts", ".tsx"]
  separators: ["\nfunction ", "\nclass ", "\ninterface ", ...] # Duplicated
```

---

## 🔄 **Update Process**

### **📝 Making Changes**

#### **1. Edit Source Configuration**
```bash
# Edit the main configuration file
vi src/config/languages/languages.yaml
```

#### **2. Test Changes**
```bash
# Validate configuration
context-ai config languages --validate

# Test specific language
context-ai config languages your_language
```

#### **3. Changes Propagate Automatically**
- System automatically copies updated config to user cache
- Changes take effect immediately
- No restart required

### **🚀 Contributing Changes**

#### **For Project Contribution:**
1. **Edit**: `src/config/languages/languages.yaml`
2. **Test**: Verify language works correctly
3. **Document**: Update this README if needed
4. **Submit**: Create pull request with changes

#### **For Personal Use:**
1. **Copy**: Configuration gets copied to `~/.context-ai/config/`
2. **Edit**: Modify your personal copy
3. **Use**: Changes apply to your Context-AI instance

---

## 🎓 **Key Success Factors**

### **🌟 Essential Points**

1. **📚 Research first**: Understand the language's structure and common patterns
2. **🎯 Order separators**: Most specific language constructs first
3. **🔗 Use inheritance**: Leverage existing configurations for similar languages
4. **📊 Set appropriate priority**: Match the language's importance in your workflow
5. **🔍 Test thoroughly**: Verify detection and chunking work as expected
6. **📖 Document changes**: Help others understand your additions

### **💡 Final Reminders**

> *"Good language configuration makes the difference between accurate and poor code understanding."*

**Your configuration should:**
- ✅ **Accurately detect** all relevant file types
- ✅ **Intelligently chunk** code at logical boundaries
- ✅ **Respect inheritance** to avoid duplication
- ✅ **Set proper priority** for processing efficiency
- ✅ **Be well-tested** with real code examples

---

## 📚 **References**

- **[Languages YAML](languages.yaml)** - Main configuration file
- **[Models](models.py)** - Python data models and validation
- **[Manager](manager.py)** - Core language management system
- **[Loader](loader.py)** - Configuration loading utilities

---

**Happy Language Configuration! 🎉**

*This system is designed to be extensible and maintainable. Contributions and improvements are always welcome.*
