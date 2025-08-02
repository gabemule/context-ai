# 🎯 How to Create New Programming Guidelines

## A Practical Guide Using Prompt Engineering Best Practices

### 📚 **Based on**: [PROMPT_ENGINEERING.md](../prompt/PROMPT_ENGINEERING.md)

---

## 🚀 **Quick Start**

### **What Are Programming Guidelines?**

Programming guidelines are **structured prompts** that instruct LLMs on how to generate code following specific principles, patterns, and best practices for a programming language.

### **Why Follow This Guide?**

Using proper **prompt engineering techniques** ensures your guidelines:
- ✅ **Generate better code quality**
- ✅ **Provide consistent results** 
- ✅ **Are easily understood by LLMs**
- ✅ **Follow scientific best practices**

---

## 📋 **Step-by-Step Process**

### **🔍 Step 1: Research and Analysis**

#### **1.1 Language Analysis**
```bash
# Essential questions to answer:
- What is the main paradigm? (OOP, Functional, Procedural, Multi-paradigm)
- What are the unique idioms and features?
- What is the language philosophy?
- Which architectural principles apply naturally?
- What are common performance considerations?
```

#### **1.2 Reliable References**
- **Official documentation**
- **Recognized style guides** (PEP 8, Google Style Guides, etc.)
- **Community best practices**
- **High-quality code examples**

#### **1.3 Critical Analysis of Principles**

**Use this decision matrix:**

| Principle | Applicable? | Justification |
|-----------|------------|---------------|
| **SOLID** | OOP languages (Java, C#) | ✅ Object-oriented design principles |
| **SOLID** | JavaScript/Python | ⚠️ Adapt for functional paradigm |
| **SOLID** | SQL | ❌ Doesn't apply to declarative languages |
| **DRY** | All languages | ✅ Universal for code reuse |
| **CLEAN CODE** | All languages | ✅ Universal for readability |
| **YAGNI** | Application languages | ✅ Avoid over-engineering |
| **YAGNI** | SQL/HTML | ❌ Data modeling needs planning |

### **⚙️ Step 2: Apply XML Structure** *(Anthropic: Use XML Tags)*

#### **2.1 Base Template**
```xml
<language_guidelines>

# 🔷 [Language] Coding Guidelines

<header>
<language_name>[Language Name]</language_name>
<paradigm>[Main paradigm]</paradigm>
<philosophy>[Core philosophy/characteristic quote]</philosophy>
</header>

When providing [language] code suggestions, follow these principles:

<core_principles>

### 📐 Architecture Principles

<solid_principles>
[Applicable SOLID principles]
</solid_principles>

<dry_principle>
[DRY application]
</dry_principle>

<clean_code>
[Clean code principles]
</clean_code>

[YAGNI if applicable]

</core_principles>

<language_specific>

### 🛠️ [Language]-Specific Best Practices

<best_practices>
[Language-specific practices]
</best_practices>

<idioms>
[Language idioms and philosophies]
</idioms>

<performance>
[Performance considerations]
</performance>

</language_specific>

### 🎨 [Language-specific sections]

<examples>
[Practical examples]
</examples>

<ecosystem>
[Tools and ecosystem - optional]
</ecosystem>

</language_guidelines>
```

### **📚 Step 3: Create Diverse Examples** *(Anthropic: Multishot Prompting)*

#### **3.1 Example Strategy**
```
For each important concept:
1. Basic example (introduction)
2. Intermediate example (common usage)  
3. Advanced example (complex case)
4. Anti-pattern (what NOT to do)
```

#### **3.2 Example Structure**
```xml
<examples>

### 🌟 [Language] Examples

```[language]
// ✅ Good Practice: [Concept]
[well-structured code]

// ❌ Anti-pattern: [Problem]  
[problematic code]

// ✅ Better: [Solution]
[improved code]
```

</examples>
```

### **🎯 Step 4: Apply Chain of Thought** *(Prompting Guide: CoT)*

#### **4.1 Explain the "Why"**
```xml
**Interfaces vs Types - Decision Process:**

1. **Ask**: "Will this shape be extended?"
   - If YES → Use `interface` (extensible)
   - If NO → Consider `type` alias

2. **Ask**: "Is this a union or primitive?"
   - If YES → Use `type` (unions, primitives)
   - If NO → Use `interface` (object shapes)

3. **Example Decision Tree:**
   [concrete examples showing the reasoning]
```

### **✅ Step 5: Quality Validation**

#### **5.1 Quality Checklist**
- [ ] **XML Structure**: Valid and well-formed
- [ ] **Header Complete**: name, paradigm, philosophy
- [ ] **Principles Applied Critically**: Not forced
- [ ] **Language-Specific Practices**: Included
- [ ] **Examples**: 3-5 diverse and relevant
- [ ] **Clear Instructions**: Specific and actionable
- [ ] **All Tags Closed**: Proper XML closure

#### **5.2 Practical Test**
```
Test your guideline:
1. Give it to someone without context
2. See if they generate expected code
3. Identify ambiguities
4. Refine iteratively
```

---

## 💡 **Language-Specific Examples**

### **🐍 Example: Python Guideline Creation**

#### **Analysis Result:**
```
Language: Python
Paradigm: Multi-paradigm (functional preferred)
Philosophy: "Simple is better than complex" - Zen of Python
Applicable Principles: SOLID (adapted), DRY, CLEAN CODE, YAGNI
```

#### **Critical Principle Application:**
```xml
<core_principles>

<solid_principles>
- **Single Responsibility**: Each function should have one clear purpose
- **Open/Closed**: Use protocols and composition for extensibility  
- **Interface Segregation**: Create focused, specific protocols
- **Dependency Inversion**: Depend on abstractions through protocols and ABC
</solid_principles>

<dry_principle>
- **"There should be one obvious way to do it"**
- **Functional composition**: Break logic into small, reusable functions
- **Decorators**: Extract cross-cutting concerns
</dry_principle>

<clean_code>
- **"Readability counts"**: Write self-documenting code
- **"Explicit is better than implicit"**: Make intent obvious
- **Meaningful names**: Use descriptive, intention-revealing names
</clean_code>

<yagni>
- **"You aren't gonna need it"**: Don't implement until needed
- **"Simple is better than complex"**: Prefer straightforward solutions
</yagni>

</core_principles>
```

#### **Language-Specific Section:**
```xml
<language_specific>

<best_practices>
- **Functional programming**: Prefer functions over classes
- **Type hints**: Always use type annotations
- **Dataclasses**: Use @dataclass for data containers
- **Context managers**: Use `with` statements for resources
</best_practices>

<idioms>
- **"Pythonic code"**: Follow Python's idioms and conventions
- **"Duck typing"**: "If it walks like a duck..."
- **"EAFP"**: Easier to Ask for Forgiveness than Permission
- **"Batteries included"**: Leverage rich standard library
</idioms>

</language_specific>
```

### **🔷 Example: TypeScript Guideline Creation**

#### **Analysis Result:**
```
Language: TypeScript
Paradigm: JavaScript + static type checking
Philosophy: Extends JavaScript with type safety
Strategy: Inherit JavaScript guidelines + TypeScript-specific additions
```

#### **Concise Approach:**
```xml
<language_guidelines>

# 🔷 TypeScript Coding Guidelines

<header>
<language_name>TypeScript</language_name>
<paradigm>JavaScript + static type checking</paradigm>
<philosophy>Extends JavaScript guidelines with type safety and developer experience</philosophy>
</header>

**Inherits all JavaScript guidelines** with these TypeScript-specific additions:

<core_principles>

### 📐 TypeScript-Specific Principles

<type_safety>
- **Type-first development**: Define interfaces before implementation
- **Make impossible states impossible**: Use types to prevent invalid states
- **Fail at compile time**: Catch errors during development, not runtime
</type_safety>

</core_principles>

<language_specific>

<best_practices>
- **Strict configuration**: Enable strict mode and all strict flags
- **Never use any**: Prefer unknown, proper types, or type assertions
- **Interfaces over types**: For object shapes that might be extended
- **Utility types**: Leverage Pick, Omit, Partial, Record, etc.
</best_practices>

<idioms>
- **"Narrow, then widen"**: Start specific, generalize when needed
- **"Types are free at runtime"**: Use them liberally for safety
- **"Explicit over implicit"**: Prefer explicit type annotations for public APIs
</idioms>

</language_specific>

<!-- Examples with all major TypeScript constructs -->
<examples>
[Interface, Type, Enum, Generic examples]
</examples>

</language_guidelines>
```

---

## 🛠️ **Adding to Languages System**

### **📋 Integration Steps**

After creating your guideline, you need to register it in the languages system:

#### **1. Add to `languages.yaml`**
```yaml
languages:
  - name: "your_language"
    extensions: [".ext1", ".ext2"] 
    guideline_file: "your_language.md"
    description: "Description of the language"
    category: "programming"  # or "markup", "data", "config"
```

#### **2. Create Guideline File**
Place your guideline at: `src/config/guidelines/your_language.md`

#### **3. Test Integration**
```bash
# Test that the system recognizes your language
context-ai config languages

# Test guideline loading
context-ai config guidelines your_language
```

---

## 🔧 **Troubleshooting Common Issues**

### **❌ Problem: Guidelines too vague**
```
Symptom: Generic instructions like "use good practices"
Solution: Apply "Be Clear and Direct" - specify exactly what to do
Example: Instead of "use good naming", say "use snake_case for variables"
```

### **❌ Problem: Forced principles**
```
Symptom: SOLID applied to SQL or HTML
Solution: Critical analysis - apply only relevant principles
```

### **❌ Problem: Few examples**  
```
Symptom: Theory without practical demonstrations
Solution: Multishot prompting - add 3-5 diverse examples
```

### **❌ Problem: Malformed XML**
```
Symptom: Unclosed tags, inconsistent structure
Solution: XML validation and rigorous template
```

---

## 📊 **Quality Metrics**

### **⭐ Quantitative Criteria**
- **Completeness**: 100% of mandatory sections
- **Examples**: Minimum 3, maximum 8 per language
- **Specificity**: 80%+ of instructions with concrete examples
- **XML Validation**: 0 structural errors

### **🎯 Qualitative Criteria**
- **Clarity**: Person without context can follow
- **Relevance**: Examples mirror real-world usage
- **Consistency**: Uniform style across guidelines
- **Applicability**: Generates expected code quality

---

## 🔄 **Iterative Improvement**

### **📊 Improvement Cycle**
```
1. Create initial version
2. Test with real users  
3. Collect specific feedback
4. Identify confusion points
5. Refine based on feedback
6. Repeat until satisfactory
```

### **🎯 Focus Areas by Iteration**
- **Iteration 1**: Structure and completeness
- **Iteration 2**: Clarity and specificity  
- **Iteration 3**: Examples and relevance
- **Iteration 4**: Polish and consistency

---

## 🎓 **Key Success Factors**

### **🌟 Essential Points**

1. **📚 Study first**: Understand the language deeply
2. **🎯 Be specific**: Clarity trumps brevity
3. **🏗️ Use XML**: Hierarchical structure improves parsing
4. **📝 Provide examples**: 3-5 diverse examples are essential
5. **🔍 Test iteratively**: Validation with real users
6. **⚖️ Analyze critically**: Not all principles apply everywhere

### **💡 Final Reminder**

> *"A good guideline is not just documentation - it's a teaching tool that guides LLMs toward generating better code."*

**Your guideline should:**
- ✅ Teach the LLM about the language
- ✅ Provide context about the "why"  
- ✅ Demonstrate with practical examples
- ✅ Structure information clearly
- ✅ Be specific and actionable

---

## 📚 **References**

- **[PROMPT_ENGINEERING.md](../prompt/PROMPT_ENGINEERING.md)** - Complete prompt engineering techniques
- **[Anthropic Documentation](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/)** - Fundamental techniques
- **[Prompting Guide](https://www.promptingguide.ai/)** - Advanced methodologies

---

**Happy Guidelines Creation! 🎉**

*This guide evolves with new discoveries in prompt engineering. Contributions and improvements are welcome.*
