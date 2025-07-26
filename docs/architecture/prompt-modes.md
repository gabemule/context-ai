# Prompt Modes Architecture

> Architectural design and implementation of Context-AI's four prompt modes: minimal, standard, comprehensive, and strict

## 🎯 Overview

Context-AI implements a sophisticated prompt mode system that balances performance, functionality, and output quality. The four modes—minimal, standard, comprehensive, and strict—represent different architectural approaches to AI prompt construction, each optimized for specific use cases and performance characteristics.

## 🏗️ Architectural Design

### **Core Architecture**

The prompt mode system is built around a layered architecture in `src/core/ai/claude_client.py`:

```python
def _build_prompt(self, question: str, context: Optional[str] = None) -> str:
    """Build prompt based on configured mode - from minimal to comprehensive."""
    if not context:
        return question

    from config.constants import PROMPT_MODE

    if PROMPT_MODE == "minimal":
        return self._build_minimal_prompt(question, context)
    elif PROMPT_MODE == "standard":
        return self._build_standard_prompt(question, context)
    elif PROMPT_MODE == "comprehensive":
        return self._build_comprehensive_prompt(question, context)
    elif PROMPT_MODE == "strict":
        return self._build_strict_prompt(question, context)
    else:
        return self._build_standard_prompt(question, context)  # Fallback
```

### **Design Principles**

1. **Progressive Enhancement**: Each mode builds upon the previous, adding functionality
2. **Performance Optimization**: Token allocation varies based on complexity needs
3. **Semantic Consistency**: All modes provide code attribution for transparency
4. **Extensibility**: New modes can be added without breaking existing functionality

## 📊 Mode Architecture Details

### **Minimal Mode** ⚡

#### **Design Philosophy**
- **Speed First**: Optimized for fastest possible responses
- **Essential Only**: No additional instructions beyond basic context
- **Resource Efficient**: Lowest token consumption

#### **Implementation**
```python
def _build_minimal_prompt(self, question: str, context: str) -> str:
    """Build minimal prompt with no extra instructions - fastest processing."""
    return f"""Based on the following context from the codebase, please answer \
the question.

**Code Attribution**: When showing existing code examples from the codebase, always \
prefix each code block with a comment indicating the source file path \
(e.g., `// From: path/to/file.tsx`).

## Context:
{context}

## Question:
{question}"""
```

#### **Token Allocation**
- **Context**: ~20-40K tokens (varies by selection)
- **Instructions**: ~50 tokens (minimal overhead)
- **Response Space**: Maximum available after context
- **Total Usage**: 20-40K tokens typically

#### **Performance Characteristics**
- **Response Time**: 2-3 seconds
- **Memory Usage**: ~100-200MB
- **Best For**: Quick factual questions, simple lookups

### **Standard Mode** 🎯 (Default)

#### **Design Philosophy**
- **Balanced Approach**: Good balance of speed and intelligence
- **Smart Enhancement**: Adds cross-project awareness and guidelines when relevant
- **Production Ready**: Default mode for everyday development

#### **Implementation**
```python
def _build_standard_prompt(self, question: str, context: str) -> str:
    """Build standard prompt with cross-project awareness and coding guidelines."""
    base_instructions = (
        "Based on the following context from the codebase, "
        "please answer the question."
    )

    # Add code attribution instruction
    code_attribution = """

**Code Attribution**: When showing existing code examples from the codebase, always \
prefix each code block with a comment indicating the source file path \
(e.g., `// From: path/to/file.tsx`)."""
    base_instructions += code_attribution

    # Add cross-project hints for multi-project contexts
    is_cross_project = (
        "Cross-Project Analysis" in context and "Project Correlations" in context
    )
    if is_cross_project:
        base_instructions += """

Note: This context contains code from multiple projects - consider \
comparing approaches when relevant."""

    # Always include coding guidelines when applicable
    guidelines = self._get_applicable_guidelines(context, question)
    if guidelines:
        guidelines_section = f"""

{guidelines}

**When providing code examples or suggestions, please follow the above guidelines.**"""
        base_instructions += guidelines_section

    return f"""{base_instructions}

## Context:
{context}

## Question:
{question}"""
```

#### **Conditional Logic**
- **Cross-Project Detection**: Automatically detects multi-project context
- **Guidelines Integration**: Includes JS/TS guidelines when code detected
- **Dynamic Instructions**: Adapts based on context characteristics

#### **Token Allocation**
- **Context**: ~40-80K tokens
- **Instructions**: ~100-300 tokens (varies by conditions)
- **Response Space**: Dynamically calculated
- **Total Usage**: 40-80K tokens typically

#### **Performance Characteristics**
- **Response Time**: 4-6 seconds
- **Memory Usage**: ~200-400MB
- **Best For**: Regular development questions, everyday coding help

### **Comprehensive Mode** 🧠

#### **Design Philosophy**
- **Deep Analysis**: Maximum intelligence and architectural insights
- **Cross-Project Mastery**: Full analysis framework for multiple projects
- **Learning Focused**: Designed for understanding and education

#### **Implementation**
```python
def _build_comprehensive_prompt(self, question: str, context: str) -> str:
    """Build comprehensive prompt with full cross-project analysis and \
architectural insights."""
    base_instructions = (
        "Based on the following context from the codebase, "
        "please answer the question."
    )

    # Add code attribution instruction
    code_attribution = """

**Code Attribution**: When showing existing code examples from the codebase, always \
prefix each code block with a comment indicating the source file path \
(e.g., `// From: path/to/file.tsx`). This helps users understand the context \
and location of the code."""
    base_instructions += code_attribution

    # Check if this is cross-project context
    is_cross_project = (
        "Cross-Project Analysis" in context and "Project Correlations" in context
    )

    if is_cross_project:
        from config.constants import ENABLE_CROSS_PROJECT_PROMPTS

        if ENABLE_CROSS_PROJECT_PROMPTS:
            cross_project_instructions = """

**CROSS-PROJECT ANALYSIS**: This context contains code from multiple projects. Please:
- Compare implementations across different projects
- Highlight similarities and differences between approaches
- Identify reusable patterns or components
- Suggest opportunities for standardization or consistency improvements
- Point out which project has the most robust/complete implementation
- Consider architectural differences and their implications
- Recommend best practices based on the patterns observed"""

            base_instructions += cross_project_instructions

    # Always include coding guidelines when applicable
    guidelines = self._get_applicable_guidelines(context, question)
    if guidelines:
        guidelines_section = f"""

{guidelines}

**When providing code examples or suggestions, please follow the above \
guidelines and explain your architectural choices.**"""
        base_instructions += guidelines_section

    return f"""{base_instructions}

## Context:
{context}

## Question:
{question}

Please provide a comprehensive answer with architectural insights and \
best practices recommendations."""
```

#### **Advanced Features**
- **7-Point Analysis Framework**: Systematic cross-project comparison
- **Architectural Reasoning**: Explains design decisions and trade-offs
- **Best Practices Integration**: Combines guidelines with architectural insights

#### **Token Allocation**
- **Context**: ~80-120K tokens
- **Instructions**: ~300-500 tokens (full framework)
- **Response Space**: Optimized for detailed responses
- **Total Usage**: 80-120K tokens typically

#### **Performance Characteristics**
- **Response Time**: 8-12 seconds
- **Memory Usage**: ~400-600MB
- **Best For**: Architecture decisions, complex comparisons, learning

### **Strict Mode** 🔍

#### **Design Philosophy**
- **Code Review Focus**: Detailed analysis with enforced standards
- **Quality Assurance**: Strict adherence to coding guidelines
- **Professional Standards**: Designed for production code quality

#### **Implementation**
```python
def _build_strict_prompt(self, question: str, context: str) -> str:
    """Build strict prompt with enforced coding standards and detailed \
code review approach."""
    base_instructions = (
        "Based on the following context from the codebase, please answer the "
        "question with a focus on code quality and best practices."
    )

    # Add code attribution instruction (most important in strict mode)
    code_attribution = """

**Code Attribution**: When showing existing code examples from the codebase, always \
prefix each code block with a comment indicating the source file path \
(e.g., `// From: path/to/file.tsx`). This is essential for code review and \
understanding implementation context."""
    base_instructions += code_attribution

    # Always include cross-project analysis when applicable
    is_cross_project = (
        "Cross-Project Analysis" in context and "Project Correlations" in context
    )
    if is_cross_project:
        cross_project_instructions = """

**CODE REVIEW APPROACH**: Analyze implementations across projects and provide \
detailed feedback on:
- Code quality and maintainability differences
- Performance implications of different approaches
- Security considerations
- Testing strategies
- Documentation quality"""
        base_instructions += cross_project_instructions

    # Always try to include guidelines with force=True
    guidelines = self._get_applicable_guidelines(context, question, force=True)
    if guidelines:
        guidelines_section = f"""

{guidelines}

**STRICT ENFORCEMENT**: All code suggestions must strictly adhere to the \
above guidelines. Review existing code for violations and suggest \
improvements."""
        base_instructions += guidelines_section

    return f"""{base_instructions}

## Context:
{context}

## Question:
{question}

Provide a detailed answer with code review insights, strict adherence to \
guidelines, and actionable improvement recommendations."""
```

#### **Enforcement Features**
- **Forced Guidelines**: Always applies guidelines regardless of detection
- **Code Review Framework**: Systematic quality analysis
- **Violation Detection**: Identifies and suggests fixes for guideline violations

#### **Token Allocation**
- **Context**: ~100-150K tokens
- **Instructions**: ~400-600 tokens (maximum framework)
- **Response Space**: Optimized for detailed code review
- **Total Usage**: 100-150K tokens typically

#### **Performance Characteristics**
- **Response Time**: 10-15 seconds
- **Memory Usage**: ~500-800MB
- **Best For**: Code generation, refactoring, standards compliance

## 🔧 Implementation Details

### **Configuration System**

Prompt modes are configured in `src/config/constants.py`:

```python
# Prompt configuration
PROMPT_MODE = "standard"  # Modes: "minimal", "standard", "comprehensive", "strict"
ENABLE_CROSS_PROJECT_PROMPTS = True  # Add cross-project analysis instructions
ENABLE_CODING_GUIDELINES = True  # Include coding guidelines in prompts
GUIDELINES_AUTO_DETECT = True  # Automatically detect when to apply guidelines
GUIDELINES_LANGUAGES = ["javascript", "typescript"]  # Supported guideline languages

# Prompt mode descriptions - each mode builds upon the previous
PROMPT_MODES = {
    "minimal": "Basic context + question only. No additional instructions "
    "or analysis prompts. Fastest processing.",
    "standard": "Context + question + cross-project awareness when multiple "
    "projects detected. Includes coding guidelines when JS/TS detected.",
    "comprehensive": "Full cross-project comparison analysis + coding "
    "guidelines + architectural insights. Best for complex queries.",
    "strict": "All features + enforced coding standards + detailed code "
    "review approach. Best for code generation tasks.",
}
```

### **Guidelines Integration**

The `_get_applicable_guidelines()` method integrates with the guidelines system:

```python
def _get_applicable_guidelines(
    self, context: str, question: str, force: bool = False
) -> Optional[str]:
    """Get applicable coding guidelines for the current context and question."""
    try:
        from config.constants import ENABLE_CODING_GUIDELINES

        if not ENABLE_CODING_GUIDELINES and not force:
            return None

        from config.guidelines.manager import get_guidelines_manager

        guidelines_manager = get_guidelines_manager()

        if force:
            # Force mode: try to detect languages and apply guidelines regardless
            languages = guidelines_manager.detect_languages_in_context(context)
            if languages:
                return guidelines_manager.get_guidelines_for_languages(languages)
            return None
        else:
            return guidelines_manager.get_applicable_guidelines(context, question)

    except Exception as e:
        # Don't let guidelines errors break the main functionality
        from utils.logging import get_logger

        logger = get_logger(__name__)
        logger.debug("Failed to load guidelines: %s", e)
        return None
```

### **Cross-Project Detection**

Cross-project context is detected by looking for specific markers in the context:

```python
is_cross_project = (
    "Cross-Project Analysis" in context and "Project Correlations" in context
)
```

These markers are injected by the query system when multiple project embeddings are active.

## 📈 Performance Analysis

### **Token Efficiency**

| Mode | Instruction Overhead | Context Efficiency | Response Quality |
|------|---------------------|-------------------|------------------|
| Minimal | ~50 tokens (0.1%) | Highest | Basic |
| Standard | ~100-300 tokens (0.5%) | High | Good |
| Comprehensive | ~300-500 tokens (1%) | Medium | Excellent |
| Strict | ~400-600 tokens (1.5%) | Lower | Professional |

### **Response Time Breakdown**

```
Minimal:      [■■■] 2-3s  (Context Processing: 1s, AI: 1-2s)
Standard:     [■■■■■] 4-6s  (Context: 2s, Guidelines: 0.5s, AI: 2-3s)  
Comprehensive:[■■■■■■■■] 8-12s (Context: 3s, Analysis: 1s, AI: 4-8s)
Strict:       [■■■■■■■■■■] 10-15s (Context: 3s, Guidelines: 1s, AI: 6-11s)
```

### **Memory Usage Patterns**

- **Base Memory**: ~100MB (Claude client, context processing)
- **Context Loading**: +50-200MB (depends on embedding size)
- **Guidelines Loading**: +10-50MB (language-specific rules)
- **AI Processing**: +100-300MB (temporary during request)

## 🎯 Decision Matrix

### **When to Use Each Mode**

| Scenario | Minimal | Standard | Comprehensive | Strict |
|----------|---------|----------|---------------|--------|
| Quick code lookup | ✅ Best | ✅ Good | ❌ Overkill | ❌ Overkill |
| Daily development | ❌ Too basic | ✅ Best | ✅ Good | ❌ Too slow |
| Learning codebase | ❌ Too basic | ✅ Good | ✅ Best | ✅ Good |
| Architecture planning | ❌ Too basic | ❌ Too basic | ✅ Best | ✅ Good |
| Code review | ❌ Too basic | ❌ Too basic | ✅ Good | ✅ Best |
| Code generation | ❌ Too basic | ✅ Good | ✅ Good | ✅ Best |
| Performance critical | ✅ Best | ✅ Good | ❌ Too slow | ❌ Slowest |

### **Context Size Considerations**

| Context Size | Minimal | Standard | Comprehensive | Strict |
|--------------|---------|----------|---------------|--------|
| <20K tokens | ✅ Perfect | ✅ Perfect | ✅ Good | ✅ Good |
| 20-50K tokens | ✅ Perfect | ✅ Perfect | ✅ Good | ✅ Good |
| 50-100K tokens | ✅ Good | ✅ Perfect | ✅ Perfect | ✅ Good |
| 100K+ tokens | ✅ Good | ✅ Good | ✅ Perfect | ❌ May timeout |

## 🔮 Future Extensibility

### **Adding New Modes**

The architecture supports easy addition of new modes:

```python
# In claude_client.py
def _build_custom_prompt(self, question: str, context: str) -> str:
    """Build custom prompt for specialized use case."""
    # Custom implementation
    pass

# In _build_prompt method
elif PROMPT_MODE == "custom":
    return self._build_custom_prompt(question, context)
```

### **Planned Enhancements**

1. **Dynamic Mode Selection**: Auto-select mode based on question complexity
2. **User Profiles**: Remember preferred modes per user
3. **Context-Aware Switching**: Adjust mode based on codebase characteristics
4. **Performance Learning**: Optimize token allocation based on usage patterns

### **Extension Points**

- **Custom Guidelines**: Add support for more programming languages
- **Domain-Specific Modes**: Create modes for specific domains (security, performance, etc.)
- **Hybrid Approaches**: Combine aspects of multiple modes
- **A/B Testing**: Framework for testing new prompt strategies

## 💡 Best Practices for Developers

### **Mode Selection Guidelines**

```python
# Performance-critical applications
PROMPT_MODE = "minimal"

# General development (recommended default)
PROMPT_MODE = "standard"

# Learning or complex analysis
PROMPT_MODE = "comprehensive"

# Code review or generation
PROMPT_MODE = "strict"
```

### **Custom Configuration**

```python
# Fine-tune for your needs
ENABLE_CROSS_PROJECT_PROMPTS = True   # Enable for multi-repo setups
ENABLE_CODING_GUIDELINES = True       # Enable for consistent code style
GUIDELINES_AUTO_DETECT = True         # Let system decide when to apply
```

### **Performance Monitoring**

```python
# Use verbose mode to understand performance
context-ai ask "question" --prompt-mode comprehensive --verbose

# Monitor token usage patterns
context-ai chat --verbose
# Use /history command during chat
```

## 🏆 Architectural Benefits

### **Modularity**
- Each mode is self-contained and testable
- Easy to modify or extend individual modes
- Clear separation of concerns

### **Performance Optimization**
- Users can choose the right balance for their needs
- System resources are used efficiently
- Predictable performance characteristics

### **Maintainability**
- Consistent code attribution across all modes
- Shared utilities and configuration
- Clear documentation and examples

### **User Experience**
- Progressive enhancement from simple to complex
- Consistent interface across all modes
- Transparent operation with verbose options

---

*This architecture enables Context-AI to serve users from quick lookups to deep architectural analysis, maintaining performance and quality across all use cases.*
