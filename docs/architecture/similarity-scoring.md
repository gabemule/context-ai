# Similarity Scoring Architecture

> Technical deep-dive into Context-AI's multi-embedding similarity scoring and normalization system

## 🎯 Overview

Context-AI implements a sophisticated **multi-embedding similarity scoring system** that enables fair comparison of search results across different embeddings with incompatible score distributions. This document explains the architecture, algorithms, and implementation details.

## ❓ The Problem

### **Raw Distance Incompatibility**
When querying multiple embeddings simultaneously, ChromaDB returns raw distance values that are **not comparable** across different embedding spaces:

```python
# Example raw results from ChromaDB
design_system_results = [0.1, 0.3, 0.8]    # Different scale
backend_api_results = [0.05, 0.15, 0.4]    # Different distribution  
legacy_code_results = [0.2, 0.6, 1.2]     # Different range
```

**Issues:**
- ❌ Different embeddings have different distance scales
- ❌ Cannot fairly rank results across embeddings
- ❌ Best result from one embedding might score worse than mediocre result from another
- ❌ User sees inconsistent similarity values

### **Real-World Impact**
```bash
# Without normalization - UNFAIR
context-ai query "authentication patterns"
## From design-system-v1 (similarity: 0.95):    # High similarity
## From legacy-v1 (similarity: 0.30):           # Appears worse, but may be better match

# With normalization - FAIR  
## From design-system-v1 (similarity: 0.85):    # Properly normalized (0-1 range)
## From legacy-v1 (similarity: 0.92):           # Shows true relevance (0-1 range)
```

**Note**: Similarity scores are always displayed in the 0-1 range, where:
- `0.0` = completely dissimilar
- `1.0` = identical match
- Values are derived from `normalized_score` field, not raw ChromaDB distances

## 🧮 Normalization Algorithm

### **Core Algorithm Implementation**
Located in `src/core/query/result_merger.py`:

```python
def merge_multi_embedding_results(self, chroma_results: Dict[str, Any]) -> List[QueryResult]:
    """
    4-step normalization process:
    1. Group results by embedding_name
    2. Normalize scores per embedding (0-1 range)
    3. Apply weight factor (default: 0.9)
    4. Sort by final_score (highest first)
    """
```

### **Step-by-Step Process**

#### **Step 1: Group by Embedding**
```python
# Raw ChromaDB results grouped by source
grouped = {
    'design-system-v1': [
        {'distance': 0.1, 'text': '...', 'metadata': {...}},
        {'distance': 0.3, 'text': '...', 'metadata': {...}},
    ],
    'backend-api-v2': [
        {'distance': 0.05, 'text': '...', 'metadata': {...}},
        {'distance': 0.15, 'text': '...', 'metadata': {...}},
    ]
}
```

#### **Step 2: Per-Embedding Normalization**
```python
# For each embedding independently:
distances = [0.1, 0.3, 0.8]  # Example from design-system-v1
max_distance = max(distances)  # 0.8
min_distance = min(distances)  # 0.1
distance_range = max_distance - min_distance  # 0.7

# Normalize each distance:
for distance in distances:
    normalized_distance = (distance - min_distance) / distance_range
    normalized_score = 1.0 - normalized_distance  # Convert to similarity
```

**Example Calculation:**
```python
# Original distances: [0.1, 0.3, 0.8]
# Step 2a: Normalize to 0-1 range
normalized_distances = [0.0, 0.286, 1.0]  # (distance - min) / range

# Step 2b: Convert to similarity (invert)
similarities = [1.0, 0.714, 0.0]  # 1 - normalized_distance
```

#### **Step 3: Apply Weight Factor**
```python
DEFAULT_WEIGHT_FACTOR = 0.9  # Configurable

final_score = normalized_score * weight_factor
# [1.0, 0.714, 0.0] → [0.9, 0.643, 0.0]
```

#### **Step 4: Cross-Embedding Sorting**
```python
# All results from all embeddings, sorted by final_score
[
    QueryResult(score=0.92, source='legacy-v1', ...),      # Best match
    QueryResult(score=0.90, source='design-system-v1', ...), # Second best  
    QueryResult(score=0.85, source='backend-api-v2', ...),   # Third
    # ... more results
]
```

### **Edge Case Handling**

#### **Identical Distances**
```python
# When all distances are the same (rare but possible)
distances = [0.5, 0.5, 0.5]
distance_range = 0.0

if distance_range < MIN_SCORE_THRESHOLD:  # 0.01
    normalized_score = 0.5  # Assign medium score
    distance_range = 1.0    # Prevent division by zero
```

#### **Single Result**
```python
# When only one result per embedding
distances = [0.3]
# Still normalized to ensure consistency
normalized_score = 1.0  # Single result gets max score
```

## 📊 Score Types Explained

Context-AI displays multiple score types to users and developers:

### **1. Similarity Score (User-Facing)**
```bash
## From design-system-v1 (similarity: 0.85):
```
**Calculation:** `1.0 - original_distance`
**Range:** `0.0` (completely dissimilar) to `1.0` (identical)
**Purpose:** Intuitive user understanding

### **2. Final Score (Internal Ranking)**
```python
QueryResult(
    final_score=0.765,  # Used for cross-embedding sorting
    normalized_score=0.85,  # Before weight factor
    original_distance=0.15   # Raw ChromaDB distance
)
```

### **3. Cross-Embedding Ranking**
```bash
context-ai query "authentication" --verbose

📊 Cross-embedding statistics:
- design-system-v1: 3 results (avg: 0.82, max: 0.90)
- backend-api-v2: 2 results (avg: 0.71, max: 0.85)  
- legacy-v1: 1 result (avg: 0.95, max: 0.95) ← Best average
```

## 🔧 Configuration Options

### **Weight Factor Tuning**
```python
# src/core/query/result_merger.py
DEFAULT_WEIGHT_FACTOR = 0.9  # Conservative factor

# Custom weight factor (advanced usage)
merger = MultiEmbeddingResultMerger(weight_factor=0.8)  # More conservative
merger = MultiEmbeddingResultMerger(weight_factor=1.0)  # No dampening
```

**Weight Factor Effects:**
- `1.0`: No dampening, full normalized scores
- `0.9`: Slightly conservative (default, tested optimal)
- `0.8`: More conservative, compresses score range
- `<0.5`: Very conservative, may flatten distinctions

### **Score Threshold**
```python
MIN_SCORE_THRESHOLD = 0.01  # Prevents division by zero

# Used in edge case detection
if distance_range < MIN_SCORE_THRESHOLD:
    # Handle identical distances
```

## ⚡ Performance Optimization

### **Token Counting with Caching**
The context formatter includes intelligent caching for performance:

```python
# src/core/formatting/context_formatter.py
_token_cache = {}  # Global cache

def count_tokens(text: str) -> int:
    text_hash = hash(text)
    if text_hash in _token_cache:
        return _token_cache[text_hash]  # Cache hit
    
    # Calculate and cache
    token_count = len(_token_encoder.encode(text))
    _token_cache[text_hash] = token_count
    return token_count
```

**Cache Configuration:**
```python
# src/config/constants.py
ENABLE_TOKEN_CACHE = True
TOKEN_CACHE_SIZE = 1000  # LRU-style cache
```

### **Batch Processing**
```python
# Result merger processes all embeddings in one pass
def merge_multi_embedding_results(self, chroma_results):
    # Single pass through all results
    # O(n log n) complexity for sorting
    # Memory efficient grouping
```

## 🎨 Display Format Examples

### **AI-Friendly Output**
```
=== CONTEXT FROM MULTIPLE SOURCES ===

## From design-system-v1 (similarity: 0.85):
**File:** components/Auth/LoginForm.tsx (typescript)

```typescript
export const LoginForm: React.FC<LoginProps> = ({ onSubmit }) => {
  const [loading, setLoading] = useState(false);
  // ... authentication logic
};
```

## From backend-api-v2 (similarity: 0.92):  
**File:** auth/controllers/login.js (javascript)

```javascript
async function loginUser(req, res) {
  const { email, password } = req.body;
  // ... backend authentication
}
```
```

### **JSON Output**
```json
{
  "query": "authentication patterns",
  "total_results": 2,
  "sources": ["design-system-v1", "backend-api-v2"],
  "results": [
    {
      "index": 1,
      "score": 0.828,
      "source_embedding": "backend-api-v2",
      "file_path": "auth/controllers/login.js",
      "content": "async function loginUser..."
    },
    {
      "index": 2, 
      "score": 0.765,
      "source_embedding": "design-system-v1",
      "file_path": "components/Auth/LoginForm.tsx",
      "content": "export const LoginForm..."
    }
  ]
}
```

## 🔍 Cross-Project Analysis

### **Enhanced Context Assembly**
```python
def _generate_cross_reference_analysis(self, results: List[QueryResult]) -> str:
    """Generate project correlation analysis"""
    
    # Group by project
    projects_data = {}
    for result in results:
        project = result.source_embedding
        # Collect languages, files, patterns per project
        
    # Generate insights:
    # - Common languages across projects
    # - Similar patterns (functions, components, classes)
    # - Comparison opportunities
    # - Standardization suggestions
```

### **Output Example**
```
## Cross-reference analysis:
- 🔄 Cross-Project Analysis: Found relevant code in 3 projects
  - design-system-v1: 4 matches (typescript) - Contains: components, functions
  - backend-api-v2: 2 matches (javascript) - Contains: functions  
  - legacy-v1: 1 match (javascript) - Contains: functions

- 🧩 Project Correlations:
  - ✅ Common stack: javascript, typescript
  - 🔗 Similar patterns: functions

- 💡 Comparison Opportunities:
  - Compare implementation approaches between projects
  - Look for reusable patterns or components
  - Review function signatures and error handling patterns
```

## 🐛 Troubleshooting

### **Common Issues**

#### **Inconsistent Similarity Scores**
```bash
# Symptoms
## From project-a (similarity: 0.99):  # Suspiciously high
## From project-b (similarity: 0.15):  # Suspiciously low

# Diagnosis
context-ai query "test" --debug --verbose
# Check: Original distances, normalization ranges, embedding quality
```

#### **All Results from One Embedding**
```bash
# Symptoms: Only seeing results from one project

# Diagnosis
context-ai select  # Check active embeddings
context-ai storage info  # Verify embeddings exist
```

#### **Score Calculation Errors**
```python
# Debug information in logs
2025-07-26 16:30:01 - core.query.result_merger - DEBUG - Grouped results: {'design-system-v1': 5, 'backend-v2': 3}
2025-07-26 16:30:01 - core.query.result_merger - INFO - Merged and normalized 8 results from 2 embeddings
```

### **Performance Issues**

#### **Slow Token Counting**
```python
# Check tiktoken availability
try:
    import tiktoken
    print("✅ tiktoken available - fast token counting")
except ImportError:
    print("⚠️ tiktoken unavailable - using fallback estimation")
```

#### **Large Result Sets**
```python
# Limit results to prevent performance issues
context-ai query "broad search" --max-results 10  # Instead of default 50
```

## 📈 Algorithm Effectiveness

### **Before vs After Normalization**

#### **Raw ChromaDB Results (Unfair)**
```
design-system-v1: [0.1, 0.3, 0.8]    → similarities: [0.90, 0.70, 0.20]
backend-api-v2:   [0.05, 0.15, 0.4]  → similarities: [0.95, 0.85, 0.60]
legacy-v1:        [0.2, 0.6, 1.2]    → similarities: [0.80, 0.40, -0.20] ❌
```

#### **Normalized Results (Fair)**
```
design-system-v1: [0.90, 0.64, 0.0]  → final: [0.81, 0.58, 0.0]
backend-api-v2:   [0.90, 0.71, 0.0]  → final: [0.81, 0.64, 0.0]
legacy-v1:        [0.90, 0.60, 0.0]  → final: [0.81, 0.54, 0.0]
```

**Cross-embedding fair ranking:**
1. `design-system-v1` result 1: `0.81` ✅
2. `backend-api-v2` result 2: `0.64` ✅  
3. `design-system-v1` result 2: `0.58` ✅
4. `legacy-v1` result 2: `0.54` ✅

## 🏗️ Architecture Integration

### **Data Flow**
```
ChromaDB Query → Result Merger → Context Formatter → AI Service
     ↓               ↓               ↓               ↓
Raw distances → Normalized scores → Formatted context → Claude API
```

### **Key Components**

| Component | File | Responsibility |
|-----------|------|----------------|
| **VectorStore** | `core/embeddings/vector_store.py` | ChromaDB interaction, raw results |
| **ResultMerger** | `core/query/result_merger.py` | Score normalization, cross-embedding ranking |
| **ContextFormatter** | `core/formatting/context_formatter.py` | AI-friendly formatting, token management |
| **QueryService** | `services/embedding_service.py` | Orchestration, user interface |

### **Extension Points**

#### **Custom Scoring Algorithms**
```python
class CustomResultMerger(MultiEmbeddingResultMerger):
    def merge_multi_embedding_results(self, chroma_results):
        # Custom normalization logic
        # Could implement: TF-IDF weighting, semantic similarity, etc.
        return super().merge_multi_embedding_results(chroma_results)
```

#### **Custom Context Formatting**
```python
class CustomContextFormatter(ContextFormatter):
    def _format_ai_friendly(self, results, query, token_limit):
        # Custom formatting logic
        # Could add: code syntax highlighting, language-specific analysis
        return super()._format_ai_friendly(results, query, token_limit)
```

## 📚 References

### **Implementation Files**
- **Core Algorithm**: [`src/core/query/result_merger.py`](../../src/core/query/result_merger.py)
- **Context Formatting**: [`src/core/formatting/context_formatter.py`](../../src/core/formatting/context_formatter.py)
- **Query Orchestration**: [`src/services/embedding_service.py`](../../src/services/embedding_service.py)
- **Configuration**: [`src/config/constants.py`](../../src/config/constants.py)

### **Related Documentation**
- **[Context Window Management](context-window-management.md)** - Token allocation and Claude integration
- **[Query Command Reference](../commands/query.md)** - User-facing query functionality
- **[Storage Command Reference](../commands/storage.md)** - Embedding management

### **External Dependencies**
- **ChromaDB**: Vector database providing raw distance calculations
- **tiktoken**: Token counting for context size management
- **sentence-transformers**: Embedding model providing vector representations

---

*This scoring system ensures fair, consistent, and meaningful similarity comparisons across all your project embeddings, enabling Context-AI to provide truly intelligent cross-project code analysis.*
