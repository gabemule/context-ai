# 📁 Context-AI Configuration Templates

This directory contains **default templates** for Context-AI configuration files. These templates are automatically copied to the user's configuration directory (`~/.context-ai/config/`) when needed.

## 🏗️ **Directory Structure**

```
src/config/samples/
├── README.md                    # This file - explains template system
├── languages.yaml               # Language configuration template
├── languages-README.md          # Languages documentation
├── guidelines/                  # Coding guidelines templates
│   ├── README.md                # Guidelines documentation
│   ├── cpp.md                   # C++ coding guidelines
│   ├── css.md                   # CSS coding guidelines
│   ├── go.md                    # Go coding guidelines
│   ├── html.md                  # HTML coding guidelines
│   ├── java.md                  # Java coding guidelines
│   ├── javascript.md            # JavaScript coding guidelines
│   ├── python.md                # Python coding guidelines
│   ├── rust.md                  # Rust coding guidelines
│   ├── sql.md                   # SQL coding guidelines
│   ├── typescript.md            # TypeScript coding guidelines
│   └── vue.md                   # Vue.js coding guidelines
└── prompts/                     # Prompt system templates
    ├── README.md                # Prompts documentation
    ├── global_instructions.md   # Global prompt instructions
    ├── security_instructions.md # Security-focused instructions
    ├── PROMPT_ENGINEERING.md    # Prompt engineering guide
    ├── comprehensive/           # Comprehensive prompt mode
    │   ├── core_instructions.md
    │   ├── cross_analysis.md
    │   ├── final_instructions.md
    │   └── mode.yaml
    ├── minimal/                # Minimal prompt mode
    │   ├── core_instructions.md
    │   └── mode.yaml
    ├── standard/               # Standard prompt mode
    │   ├── core_instructions.md
    │   ├── cross_analysis.md
    │   └── mode.yaml
    └── strict/                 # Strict prompt mode
        ├── core_instructions.md
        ├── cross_analysis.md
        ├── final_instructions.md
        └── mode.yaml
```

## 🔄 **Template Copy Process**

### **How It Works:**
1. **First Run:** When Context-AI runs for the first time, it checks if user config exists
2. **Auto-Copy:** If missing, templates are automatically copied from this directory to `~/.context-ai/config/`
3. **User Customization:** Users can then modify their copies without affecting the defaults
4. **Preservation:** User customizations are preserved - templates are only copied if files don't exist

### **Copy Destinations:**
```
src/config/samples/languages.yaml          → ~/.context-ai/config/languages.yaml
src/config/samples/languages-README.md     → ~/.context-ai/config/languages-README.md
src/config/samples/guidelines/             → ~/.context-ai/config/guidelines/
src/config/samples/prompts/                → ~/.context-ai/config/prompt/
```

## 📋 **Template Types**

### **1. 🌍 Languages Configuration (`languages.yaml`)**
- **Purpose:** Defines supported programming languages and their properties
- **Contains:** File extensions, separators, chunking priorities, inheritance rules
- **Used By:** `LanguagesManager`, `ChunkingConfig`, file processing
- **User Impact:** Controls which files are processed and how they're chunked

### **2. 📝 Coding Guidelines (`guidelines/*.md`)**
- **Purpose:** Language-specific coding standards and best practices
- **Contains:** Style guides, naming conventions, architecture recommendations
- **Used By:** `GuidelinesManager`, AI prompt building when guidelines are enabled
- **User Impact:** Influences AI responses to follow specific coding standards
- **Languages:** 12 languages supported (Python, JavaScript, TypeScript, etc.)

### **3. 🎯 Prompt System (`prompts/`)**
- **Purpose:** AI prompt templates for different interaction modes
- **Contains:** Core instructions, security rules, analysis templates, mode configurations
- **Used By:** `PromptBuilder`, AI services for question processing
- **User Impact:** Controls AI behavior, response style, and analysis depth
- **Modes:** 4 modes available (minimal, standard, comprehensive, strict)

## 🔧 **For Developers**

### **Adding New Templates:**
1. Add template files to appropriate subdirectory
2. Update copy logic in respective managers if needed
3. Test template copying process
4. Update this README

### **Template Guidelines:**
- **Use Markdown** for documentation templates
- **Use YAML** for configuration templates
- **Include clear comments** explaining options
- **Follow existing naming conventions**
- **Test templates** before committing

### **Manager Responsibilities:**
- **`LanguagesLoader`**: Copies `languages.yaml` and `languages-README.md`
- **`GuidelinesManager`**: Copies `guidelines/` directory
- **`PromptBuilder`**: Copies `prompts/` directory

## 🎯 **Template Philosophy**

### **Design Principles:**
1. **Sensible Defaults:** Templates should work well out-of-the-box
2. **User Freedom:** Users can customize without breaking the system
3. **Documentation:** Every template is self-documenting
4. **Consistency:** Similar structure and style across all templates
5. **Preservation:** User changes are never overwritten

### **Template vs. User Config:**
- **Templates (here):** Default configurations, version controlled, read-only for users
- **User Config (`~/.context-ai/`):** Customizable copies, user-specific, preserved across updates

## 📚 **Related Documentation**

- [`guidelines/README.md`](guidelines/README.md) - Detailed guidelines documentation
- [`prompts/README.md`](prompts/README.md) - Detailed prompts documentation  
- [`languages-README.md`](languages-README.md) - Languages configuration guide
- Project README - Overall Context-AI documentation

---

**💡 Note:** This template system ensures users get working defaults while maintaining full customization freedom. The templates in this directory should be treated as the "source of truth" for default configurations.
