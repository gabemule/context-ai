# 🧠 Complete Prompt Engineering Guide

## Based on Scientific Research and Best Practices

### 📚 **Sources Studied:**
- **Anthropic Documentation**: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/
- **Prompting Guide**: https://www.promptingguide.ai/

---

## 🚀 **Introduction to Prompt Engineering**

### **What is Prompt Engineering?**

Prompt engineering is a **scientific discipline** for developing and optimizing prompts to efficiently apply and build with Large Language Models (LLMs) for a wide variety of applications and use cases.

> *"Think of Claude as a brilliant but very new employee (with amnesia) who needs explicit instructions"* - Anthropic

### **Why Does It Work?**

- **LLMs are contextual**: They depend on information provided in the prompt
- **Structure matters**: How we organize information affects processing
- **Examples teach**: Few-shot learning is extremely effective
- **Clarity reduces errors**: Precise instructions generate better outputs

### **When to Use Prompt Engineering vs Fine-tuning**

**✅ Prefer Prompt Engineering when:**
- **Resource efficiency**: Doesn't require GPUs or large memory
- **Cost-effectiveness**: Cheaper than fine-tuning
- **Time-saving**: Instantaneous results vs hours/days
- **Flexibility**: Rapid iteration and experimentation
- **Preserves knowledge**: Maintains model's general capabilities

---

## 🔬 **Anthropic - Fundamental Techniques**

### **🎯 1. Be Clear and Direct**

> *"The golden rule of clear prompting: Show your prompt to a colleague with minimal context - if they're confused, Claude will likely be too."*

#### **📋 How to Be Clear, Contextual, and Specific**

**✅ Give Claude Contextual Information:**
- What the task results will be used for
- What audience the output is meant for
- What workflow the task is part of
- What the end goal or success criteria looks like

**✅ Be Specific About What You Want:**
```
❌ Vague: "Analyze this code"
✅ Specific: "Analyze this Python code focusing on: 1) Performance, 2) Readability, 3) PEP 8 compliance. Format as numbered list."
```

**✅ Provide Instructions as Sequential Steps:**
```
❌ Confusing: "Process the data and create a report"
✅ Clear: 
1. Clean data by removing null values
2. Calculate aggregate metrics (mean, median, std dev)  
3. Create visualizations for each metric
4. Generate report in markdown format
```

#### **💡 Practical Examples of Clarity**

**Example: Anonymizing Customer Feedback**

❌ **Unclear Prompt:**
```
Remove personally identifiable information from this customer feedback data.
```

✅ **Clear Prompt:**
```
Your task is to anonymize customer feedback for our quarterly review.

Instructions:
1. Replace all customer names with "CUSTOMER_[ID]" (e.g., "Jane Doe" → "CUSTOMER_001").
2. Replace email addresses with "EMAIL_[ID]@example.com".
3. Redact phone numbers as "PHONE_[ID]".
4. If a message mentions a specific product (e.g., "AcmeCloud"), leave it intact.
5. If no PII is found, copy the message verbatim.
6. Output only the processed messages, separated by "---".

Data to process: {{FEEDBACK_DATA}}
```

### **🏗️ 2. Use XML Tags**

> *"XML tags can be a game-changer when your prompts involve multiple components like context, instructions, and examples."*

#### **📚 Why XML Works**

- **Clarity**: Clearly separate different parts of your prompt
- **Accuracy**: Reduce errors caused by Claude misinterpreting parts
- **Flexibility**: Easily find, add, remove, or modify parts
- **Parseability**: Having Claude use XML tags makes it easier to extract specific parts

#### **🛠️ XML Best Practices**

**✅ Be Consistent:**
```xml
<instructions>
Use the same tag names throughout your prompts
</instructions>

<!-- Refer to tag names when talking about content -->
Using the contract in <contract> tags...
```

**✅ Nest Tags:**
```xml
<analysis>
  <technical_debt>
    <code_quality>
      Detailed quality analysis
    </code_quality>
    <performance>
      Performance analysis
    </performance>
  </technical_debt>
</analysis>
```

#### **💡 Practical Example: Legal Contract Analysis**

❌ **Without XML Tags:**
```
Analyze this software licensing agreement for potential risks and liabilities. Focus on indemnification, limitation of liability, and IP ownership clauses. Compare with our standard contract and give recommendations.
```

✅ **With XML Tags:**
```xml
Analyze this software licensing agreement for legal risks and liabilities.

We're a multinational enterprise considering this agreement for our core data infrastructure.

<agreement>
{{CONTRACT}}
</agreement>

<standard_contract>
{{STANDARD_CONTRACT}}
</standard_contract>

<instructions>
1. Analyze these clauses:
   - Indemnification
   - Limitation of liability
   - IP ownership

2. Note unusual or concerning terms
3. Compare to our standard contract
4. Summarize findings in <findings> tags
5. List actionable recommendations in <recommendations> tags
</instructions>
```

### **📚 3. Use Examples (Multishot Prompting)**

> *"Examples are your secret weapon shortcut for getting Claude to generate exactly what you need."*

#### **⚡ Why Examples Work**

- **Accuracy**: Examples reduce misinterpretation of instructions
- **Consistency**: Examples enforce uniform structure and style
- **Performance**: Well-chosen examples boost capability for complex tasks

#### **🎯 Crafting Effective Examples**

**✅ Relevant**: Your examples mirror your actual use case
**✅ Diverse**: Your examples cover edge cases and vary enough to avoid unintended patterns  
**✅ Clear**: Your examples are wrapped in `<example>` tags for structure

#### **💡 Practical Example: Customer Feedback Analysis**

❌ **No Examples:**
```
Analyze this customer feedback and categorize the issues. Use categories: UI/UX, Performance, Feature Request, Integration, Pricing, Other. Rate sentiment (Positive/Neutral/Negative) and priority (High/Medium/Low).
```

✅ **With Examples:**
```
Our CS team is overwhelmed with unstructured feedback. Your task is to analyze feedback and categorize issues for our product and engineering teams.

<example>
Input: The new dashboard is a mess! It takes forever to load, and I can't find the export button. Fix this ASAP!
Category: UI/UX, Performance
Sentiment: Negative  
Priority: High
</example>

Now, analyze this feedback: {{FEEDBACK}}
```

### **🤔 4. Let Claude Think (Chain of Thought)**

> *"Chain of thought prompting enables complex reasoning capabilities through intermediate reasoning steps."*

#### **⛓️ Basic Chain of Thought**

**Combine with few-shot prompting:**
```
The odd numbers in this group add up to an even number: 4, 8, 9, 15, 12, 2, 1.
A: Adding all the odd numbers (9, 15, 1) gives 25. The answer is False.

The odd numbers in this group add up to an even number: 15, 32, 5, 13, 82, 7, 1.
A:
```

#### **🎯 Zero-shot Chain of Thought**

**"Let's think step by step":**
```
❌ Without CoT:
Question: I went to the market and bought 10 apples. I gave 2 to the neighbor and 2 to the repairman. Then I bought 5 more and ate 1. How many do I have left?
Answer: 11 apples (INCORRECT)

✅ With CoT:
Question: I went to the market and bought 10 apples. I gave 2 to the neighbor and 2 to the repairman. Then I bought 5 more and ate 1. How many do I have left?

Let's think step by step.

Answer: 
First, you started with 10 apples.
You gave away 4 apples (2+2), so you had 6 left.
Then you bought 5 more, so you had 11 apples.
Finally, you ate 1, so you would be left with 10 apples. (CORRECT)
```

### **👤 5. Give Claude a Role (System Prompts)**

**Define specific roles for better context:**

```xml
<role>
You are a senior software architect specialized in distributed systems. 
You value simplicity, performance, and maintainability.
When analyzing code, focus on:
- Architectural patterns
- Points of failure  
- Scalability
- Testability
</role>

Given this context, analyze the proposed architecture...
```

### **🔗 6. Chain Complex Prompts**

**For complex tasks, break into smaller prompts and connect:**

```
Prompt 1: "Analyze requirements and identify main components"
Prompt 2: "Given components {{COMPONENTS}}, design the architecture"  
Prompt 3: "Given architecture {{ARCHITECTURE}}, implement the critical component"
```

---

## 🧠 **Prompting Guide - Advanced Techniques**

### **📋 Elements of an Effective Prompt**

Every effective prompt contains:

1. **📝 Instruction** - A specific task or instruction you want the model to perform
2. **🌍 Context** - External information or additional context  
3. **💾 Input Data** - The input or question we are interested to find a response for
4. **📤 Output Indicator** - The type or format of the output

**Complete Example:**
```
[CONTEXT] You are a Python expert for data science.
[INSTRUCTION] Create a function for data cleaning
[INPUT] Dataset with null values, duplicates, and outliers
[OUTPUT] Documented Python code with usage examples
```

### **💡 General Tips for Prompt Design**

#### **🔄 1. Start Simple**
- Use simple playground for rapid iteration
- Add elements progressively
- Version your prompts during development
- Specificity + simplicity + conciseness = better results

#### **📋 2. The Instruction is Key**
**Effective command verbs:**
- "Write", "Classify", "Summarize", "Translate", "Sort"
- Experiment with different instructions
- Place instructions at the beginning
- Use clear separators like "###"

**Example:**
```
### Instruction ###
Translate the text below to Spanish:

Text: "hello!"
```

#### **🎯 3. Specificity**
❌ **Vague**: "Analyze this code"
✅ **Specific**: 
```
Analyze this Python code focusing on:
1. PEP 8 compliance
2. Possible performance optimizations  
3. Potential bugs or edge cases
4. Refactoring suggestions

Desired format:
- Issue: [description]
- Severity: [High/Medium/Low]  
- Solution: [recommended action]
```

#### **✅ 4. Do vs Don't**
❌ **Negative**: "DON'T ASK for personal information"
✅ **Positive**: "Recommend movies based only on global trending topics"

### **🎯 Advanced Prompting Techniques**

#### **🎯 Zero-shot Prompting**
**When to use**: Simple tasks without prior examples
```
Classify the sentiment of this sentence: "I loved the movie!"
```

#### **📚 Few-shot Prompting**  
**When to use**: More complex tasks that need demonstration

**Important properties** (Min et al. 2022):
- Label space and text distribution matter
- Format is crucial, even with random labels
- True distribution labels > uniform distribution

**Example:**
```
Sentiment: Positive | Text: Amazing movie!
Sentiment: Negative | Text: Terrible experience  
Sentiment: Positive | Text: Great service today
Sentiment: ? | Text: The weather is okay
```

#### **⛓️ Chain-of-Thought (CoT) Prompting**

**📋 Fundamental Technique:**
```
Question: Roger has 5 tennis balls. He buys 2 more cans of tennis balls. Each can has 3 tennis balls. How many tennis balls does he have now?

Answer with CoT:
Roger started with 5 tennis balls.
2 cans of tennis balls × 3 tennis balls per can = 6 tennis balls.
5 + 6 = 11 tennis balls.
Roger has 11 tennis balls.
```

**🚀 Zero-shot CoT:**
```
Question: [complex problem]
Let's think step by step.
```

#### **🔄 Self-Consistency**
**Run multiple times and use most consistent answer:**
```
Run 1: [reasoning path 1] → Answer A
Run 2: [reasoning path 2] → Answer A  
Run 3: [reasoning path 3] → Answer B
Run 4: [reasoning path 4] → Answer A
Run 5: [reasoning path 5] → Answer A

Final Answer: A (most consistent)
```

#### **📚 Generate Knowledge Prompting**
**Generate relevant knowledge before the main task:**
```
Step 1: "List important facts about renewable energy"
[Generates relevant knowledge]

Step 2: "Based on these facts: {{KNOWLEDGE}}, answer: What is the future of solar energy?"
[Uses generated knowledge]
```

#### **🔗 Prompt Chaining**
**Break complex tasks into smaller steps:**
```
Chain 1: Extract requirements → {{REQUIREMENTS}}
Chain 2: Create architecture based on {{REQUIREMENTS}} → {{ARCHITECTURE}}  
Chain 3: Implement {{ARCHITECTURE}} → {{CODE}}
Chain 4: Review {{CODE}} → {{FINAL_CODE}}
```

#### **🌳 Tree of Thoughts (ToT)**
**Explore multiple reasoning paths:**
```
Problem: How to optimize this algorithm?

Path 1: Complexity Optimization
├── Use better data structures
├── More efficient algorithms
└── Big O analysis

Path 2: Memory Optimization  
├── Reduce allocations
├── Reuse objects
└── Garbage collection

Path 3: I/O Optimization
├── Batch operations
├── Async processing  
└── Caching

Evaluate paths → Choose best approach → Implement
```

#### **🔍 Retrieval Augmented Generation (RAG)**
**Combine prompt with external information:**
```
<context>
{{RETRIEVED_DOCUMENTS}}
</context>

<question>
Based on the context above, answer: {{USER_QUESTION}}
</question>

<instructions>
- Use only information from the context
- Cite sources when relevant
- If information is not available, say so clearly
</instructions>
```

#### **🎭 Meta-prompting**
**Prompts that generate prompts:**
```
Create a prompt for a sentiment classification task that:
1. Includes 3 diverse examples
2. Specifies output format  
3. Handles edge cases
4. Is clear about classification criteria

The prompt should be usable by non-experts.
```

### **⚡ Specialized Techniques Studied**

#### **🎯 Active-Prompt**
**Adapt prompts based on context:**
```
IF task_type == "web_development":
    examples = web_specific_examples
ELIF task_type == "data_science":  
    examples = data_science_examples
ELIF task_type == "mobile_app":
    examples = mobile_specific_examples

prompt = base_template + context_specific_examples
```

#### **📍 Directional Stimulus Prompting**
**Direct towards specific results:**
```
❌ Generic: "Write Python code"
✅ Directed: "Write Python code optimized for PERFORMANCE and READABILITY"

Result: Code with explicit focus on performance and readability
```

#### **🔧 Program-Aided Language Models (PAL)**
**Combine reasoning with code:**
```
Problem: "Calculate 15% discount on $120"

Reasoning + Code:
# First, let's understand the problem
price = 120  # Original price in dollars
discount_rate = 0.15  # 15% discount

# Calculate the discount
discount_amount = price * discount_rate
final_price = price - discount_amount

print(f"Original price: ${price}")
print(f"Discount (15%): ${discount_amount}")  
print(f"Final price: ${final_price}")
```

#### **🔄 ReAct (Reasoning + Acting)**
**Alternate between reasoning and action:**
```
Thought: I need to find information about Python 3.12
Action: Search["Python 3.12 new features"]
Observation: Python 3.12 introduces improved error messages...

Thought: Now I need specific examples  
Action: Search["Python 3.12 f-string improvements examples"]
Observation: F-strings now support...

Thought: With this information I can answer
Action: Generate[Comprehensive answer about Python 3.12]
```

#### **🪞 Reflexion**
**Self-reflection and improvement:**
```
Initial Response: [first attempt]

Reflection: "Is this response correct? What can I improve?"
- Missing edge case considerations
- Examples are not diverse enough
- Explanation could be clearer

Improved Response: [improved version based on reflection]
```

---

## 🎯 **Practical Applications**

### **📋 Generating Code Guidelines**

**Application of Multiple Techniques:**
```xml
<role>You are a Python expert who creates guidelines for development teams</role>

<instructions>
Create Python guidelines following this structure:
1. Fundamental principles  
2. Python-specific practices
3. Good vs bad code examples
4. Justifications for each recommendation
</instructions>

<context>
Guidelines will be used by Jr-Sr developers in production projects.
Focus on readability, maintainability, and performance.
</context>

<examples>
<good_practice>
```python
# ✅ Clear function with type hints
def calculate_discount(price: Decimal, rate: float) -> Decimal:
    """Calculate discount amount for given price and rate."""
    return price * Decimal(str(rate))
```
</good_practice>

<bad_practice>
```python  
# ❌ Unclear function without types
def calc(p, r):
    return p * r
```
</bad_practice>
</examples>

Let's think step by step about Python best practices.
```

### **🔍 Code Analysis**

**Chain of Thought applied:**
```
Analyze this Python code:

```python
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
```

Let's analyze step by step:

1. **Functionality**: Filters positive numbers and doubles them
2. **Type hints**: Missing - makes understanding and maintenance harder  
3. **Performance**: Manual loop - could use list comprehension
4. **Readability**: Generic names 'data' and 'item'

Suggested improvements:
```python
def double_positive_numbers(numbers: List[float]) -> List[float]:
    """Double all positive numbers in the input list."""
    return [num * 2 for num in numbers if num > 0]
```
```

### **📚 Creating Documentation**

**RAG + Examples:**
```xml
<knowledge_base>
{{PROJECT_SOURCE_CODE}}
{{CURRENT_ARCHITECTURE}}
{{ESTABLISHED_PATTERNS}}
</knowledge_base>

<task>
Based on the knowledge base, create documentation for new developers on the project.
</task>

<examples>
<good_doc>
## UserService

### Purpose
Manages user authentication and profile operations.

### Usage
```python
user_service = UserService(database_connection)
user = await user_service.authenticate(email, password)
```

### Dependencies  
- DatabaseConnection
- PasswordHasher
- Logger
</good_doc>
</examples>

<output_format>
Use markdown with clear sections:
- Purpose
- Usage examples  
- Dependencies
- Common patterns
- Troubleshooting
</output_format>
```

---

## 📊 **Metrics and Evaluation**

### **📏 How to Measure Prompt Effectiveness**

#### **🎯 Quantitative Criteria**
- **Accuracy**: % of correct responses
- **Consistency**: Variation between multiple runs
- **Completeness**: % of requirements met
- **Format compliance**: Adherence to specified format

#### **🎨 Qualitative Criteria**  
- **Relevance**: Relevance to the context
- **Clarity**: Clarity of instructions and outputs
- **Usefulness**: Practical utility of the result
- **Safety**: Absence of harmful content

### **🧪 Testing Process**

#### **A/B Testing Prompts**
```
Prompt A: [current version]
Prompt B: [improved version]

Metrics:
- Time to completion
- Quality score (1-10)
- User satisfaction  
- Task completion rate

Choice: Prompt with best overall performance
```

#### **Continuous Iteration**
```
1. Create baseline prompt
2. Test with real users
3. Identify failure modes  
4. Apply prompt engineering techniques
5. A/B test improvements
6. Deploy best version
7. Monitor and repeat
```

---

## 🚀 **Consolidated Best Practices**

### **✅ Do's**

1. **📋 Start Simple**: Begin with basic prompts and add complexity
2. **🎯 Be Specific**: Clarity > brevity  
3. **📚 Use Examples**: 3-5 diverse examples are ideal
4. **🏗️ Structure with XML**: Organize information hierarchically
5. **🤔 Chain Reasoning**: Use "let's think step by step"
6. **👤 Set Roles**: Define context and persona
7. **🔄 Iterate**: Test and refine continuously
8. **📊 Measure**: Use metrics to validate improvements

### **❌ Don'ts**

1. **❌ Don't be vague**: Avoid ambiguous instructions
2. **❌ Don't use negatives**: Focus on what to do, not what not to do
3. **❌ Don't assume context**: Provide all necessary information
4. **❌ Don't ignore examples**: Examples are fundamental for performance
5. **❌ Don't overcomplicate**: Unnecessary complexity hurts
6. **❌ Don't skip testing**: Always validate with real users
7. **❌ Don't forget edge cases**: Consider atypical scenarios
8. **❌ Don't use jargon**: Keep language accessible

---

## 📚 **References and Resources**

### **📖 Primary Sources Studied**

#### **🔬 Anthropic Documentation**
- **Overview**: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview
- **Be Clear and Direct**: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/be-clear-and-direct  
- **Use XML Tags**: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags
- **Multishot Prompting**: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/multishot-prompting

#### **🧠 Prompting Guide**
- **Main Guide**: https://www.promptingguide.ai/
- **Introduction**: https://www.promptingguide.ai/introduction  
- **Elements**: https://www.promptingguide.ai/introduction/elements
- **Tips**: https://www.promptingguide.ai/introduction/tips
- **Few-shot**: https://www.promptingguide.ai/techniques/fewshot
- **Chain-of-Thought**: https://www.promptingguide.ai/techniques/cot

### **📄 Reference Papers**

- **Wei et al. (2022)**: Chain-of-Thought Prompting Elicits Reasoning in Large Language Models
- **Kojima et al. (2022)**: Large Language Models are Zero-Shot Reasoners  
- **Min et al. (2022)**: Rethinking the Role of Demonstrations: What Makes In-Context Learning Work?
- **Brown et al. (2020)**: Language Models are Few-Shot Learners

### **🛠️ Recommended Tools**

- **Anthropic Console**: https://console.anthropic.com/
- **OpenAI Playground**: https://platform.openai.com/playground
- **Prompting Tutorials**: 
  - GitHub: https://github.com/anthropics/prompt-eng-interactive-tutorial
  - Google Sheets: Interactive prompting tutorial

---

## 🎓 **Final Considerations**

### **🌟 Key Insights**

1. **🎯 Clarity is King**: Clarity is more important than brevity
2. **🏗️ Structure Matters**: XML tags dramatically improve parsing
3. **📚 Examples Teach**: Few-shot prompting is extremely effective
4. **🤔 Reasoning Helps**: Chain of thought improves complex tasks
5. **🔄 Iteration is Essential**: Continuous improvement through testing
6. **📊 Measurement Enables**: Metrics guide optimizations

### **🚀 Next Steps**

1. **Apply the techniques**: Use this knowledge in real prompts
2. **Experiment with combinations**: Combine multiple techniques  
3. **Measure results**: Use metrics to validate improvements
4. **Share learnings**: Contribute to the community
5. **Stay updated**: Field evolves rapidly

### **💡 Final Reminder**

> *"Prompt engineering is far faster than other methods of model behavior control and can often yield leaps in performance in far less time."* - Anthropic

Prompt engineering is a **fundamental skill** for working effectively with LLMs. Mastering these techniques enables:

- ✅ **Better quality** outputs
- ✅ **Greater consistency** in results  
- ✅ **Reduced errors** and ambiguities
- ✅ **Time savings** in iteration
- ✅ **Maximum leverage** of LLM capabilities

**Happy Prompting! 🎉**

---

*This document is based on scientific research and will be updated as new techniques and discoveries emerge in the field of prompt engineering.*
