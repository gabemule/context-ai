# PLAN_SMARTQUERY.md
## Smart Query Processing System - Enterprise Architecture Plan

### 📋 **DOCUMENT SUMMARY**

Este documento detalha o plano técnico completo para transformar o sistema básico de query preprocessing em um **Smart Query Processing System** de classe empresarial. O plano segue rigorosamente os princípios **SOLID, DRY, Clean Code, Clean Architecture e YAGNI**, fornecendo uma roadmap para implementar:

#### **🎯 Core Components:**
1. **Context Detection Engine** - Detecta domínio técnico, linguagens e frameworks
2. **Smart Expansion Engine** - Expansão contextual inteligente de termos
3. **Intent Analysis System** - Identifica intenção do usuário (tutorial/debug/reference)
4. **Multilingual Framework** - Suporte extensível para múltiplos idiomas
5. **Progressive Enhancement** - Pipeline de melhorias incrementais com fallback
6. **File Retrieval Intelligence** - Detecta quando buscar arquivos completos vs chunks
7. **Guidelines Integration** - Mantém technology_stack para seleção automática de guidelines

#### **📊 Expected Impact:**
- **10x improvement** na relevância de queries
- **<50ms** overhead de processamento
- **Multilingual support** extensível (en, pt_br + futuro: es, fr, de, ja, zh, ru)
- **Enterprise scalability** com arquitetura limpa e extensível
- **Direct implementation** sem complexity layers

#### **🚀 Implementation Timeline:**
- **Phase 1 (Week 1-2):** Foundation architecture
- **Phase 2 (Week 3-4):** Smart expansion engine  
- **Phase 3 (Week 5-6):** Intent analysis system
- **Phase 4 (Week 7-8):** Progressive enhancement pipeline

#### **🏗️ Architecture Highlights:**
- **SOLID compliance** com dependency injection
- **Design patterns** (Strategy, Factory, Registry, Decorator, Command)
- **Clean Architecture** com camadas bem definidas
- **YAGNI approach** com implementação incremental
- **Direct implementation** sem complexity layers

---

### 📋 **EXECUTIVE SUMMARY**

#### **Vision Statement**
Transform the current basic query preprocessing into an intelligent, multilingual, context-aware query processing system that dramatically improves search precision and user experience while maintaining enterprise-grade architecture standards.

#### **Key Objectives**
- **10x improvement** in query relevance through context-aware expansion
- **Multilingual support** with extensible dictionary architecture
- **Intent-based processing** for targeted search optimization
- **Progressive enhancement** maintaining backward compatibility
- **Enterprise scalability** following SOLID, DRY, Clean Code principles

#### **Success Metrics**
- **Precision:** 85%+ relevant results in top 10
- **Performance:** <50ms query processing overhead
- **Extensibility:** New language support in <2 hours
- **Maintainability:** 90%+ code coverage, zero cyclomatic complexity >10

---

### 🏗️ **ARCHITECTURAL PRINCIPLES**

#### **SOLID Principles Application**

##### **Single Responsibility Principle (SRP)**
```python
# ❌ BEFORE: Monolithic preprocessor
class QueryPreprocessor:
    def preprocess_query(self):
        # Normalization + Validation + Expansion + Intent Detection
        pass

# ✅ AFTER: Separated responsibilities
class QueryNormalizer:           # Only text normalization
class QueryValidator:            # Only validation logic
class ContextDetector:           # Only context analysis
class IntentAnalyzer:           # Only intent detection
class SmartExpander:            # Only query expansion
```

##### **Open/Closed Principle (OCP)**
```python
# Extensible without modification
class LanguageDictionaryRegistry:
    def register_language(self, lang: str, dictionary: LanguageDictionary):
        """Add new languages without code changes"""
        
class ExpansionStrategyFactory:
    def create_strategy(self, context: TechnicalContext) -> ExpansionStrategy:
        """Add new expansion strategies without modification"""
```

##### **Liskov Substitution Principle (LSP)**
```python
# All language processors are interchangeable
class LanguageProcessor(ABC):
    @abstractmethod
    def process(self, query: str) -> ProcessedQuery: pass

class EnglishProcessor(LanguageProcessor): pass
class PortugueseProcessor(LanguageProcessor): pass
class SpanishProcessor(LanguageProcessor): pass  # Future
```

##### **Interface Segregation Principle (ISP)**
```python
# Specific interfaces for specific needs
class ContextDetectable(Protocol):
    def detect_context(self, query: str) -> TechnicalContext: pass

class IntentAnalyzable(Protocol):
    def analyze_intent(self, query: str) -> QueryIntent: pass

class Expandable(Protocol):
    def expand_terms(self, query: str, context: TechnicalContext) -> List[str]: pass
```

##### **Dependency Inversion Principle (DIP)**
```python
# Depend on abstractions, not concretions
class SmartQueryProcessor:
    def __init__(
        self,
        context_detector: ContextDetectable,
        intent_analyzer: IntentAnalyzable,
        expander: Expandable,
        language_registry: LanguageRegistry
    ):
        # Injected dependencies - easily testable and swappable
```

#### **DRY (Don't Repeat Yourself)**
- **Shared base classes** for common functionality
- **Template Method Pattern** for processing pipeline
- **Strategy Pattern** for algorithm variations
- **Registry Pattern** for dynamic component management

#### **Clean Code Principles**
- **Meaningful names:** `TechnicalContextDetector` vs `Detector`
- **Small functions:** Max 20 lines, single purpose
- **Clear abstractions:** Interfaces define contracts
- **No magic numbers:** Constants with semantic names

#### **Clean Architecture**
```
┌─────────────────────────────────────────┐
│           Presentation Layer            │ ← CLI/API interfaces
├─────────────────────────────────────────┤
│           Application Layer             │ ← Use cases/orchestration
├─────────────────────────────────────────┤
│            Domain Layer                 │ ← Business logic/entities
├─────────────────────────────────────────┤
│          Infrastructure Layer           │ ← Dictionaries/external deps
└─────────────────────────────────────────┘
```

#### **YAGNI (You Aren't Gonna Need It)**
- **Phase-based implementation:** Only build what's needed now
- **Direct implementation:** All features enabled by default, no conditional complexity
- **Minimal viable architecture:** Start simple, evolve as needed
- **Metrics-driven decisions:** Add complexity only when proven beneficial

---

### 🏗️ **UNIFIED ARCHITECTURE & GUIDELINES INTEGRATION**

#### **📁 Unified Domain Structure**

##### **Current State (Separated):**
```
src/core/query/         # Query preprocessing 
src/core/formatting/    # Context formatting
```

##### **Target State (Unified Domain):**
```
src/core/query/                    # Unified Query Processing Domain
├── __init__.py                    # Unified exports
├── preprocessor.py                # Current: Basic preprocessing
├── smart_processor.py             # NEW: Context-aware processing
├── intent_analyzer.py             # NEW: Intent detection  
├── result_merger.py               # Current: Multi-embedding merging
├── context_formatter.py           # MOVED: from core/formatting/
├── retrieval_strategy.py          # NEW: File retrieval intelligence
├── dictionary/
│   ├── __init__.py               # Current: Multilingual support
│   ├── registry.py               # NEW: Language registry
│   ├── en.py                     # Current: English dictionary
│   └── pt_br.py                  # Current: Portuguese dictionary
└── models/
    ├── __init__.py
    ├── query.py                  # NEW: Query-related models
    └── context.py                # NEW: Context-related models
```

#### **🔗 Critical Guidelines Integration**

##### **Technology Stack Flow (MUST BE PRESERVED):**
```
Query Processing → Context Detection → Technology Stack → Guidelines Selection
                                           ↓
                          <technology_stack>typescript,react,css</technology_stack>
                                           ↓
                            prompt_builder.py uses this for guidelines!
```

##### **Enhanced TechnicalContext for Guidelines:**
```python
@dataclass
class TechnicalContext:
    """Enhanced context with guidelines integration."""
    languages: List[str]           # For guidelines selection
    frameworks: List[str]          # For guidelines selection  
    domains: List[str]             # For expansion strategies
    patterns: List[str]            # For retrieval strategies
    intent_signals: List[str]      # For intent analysis
    confidence_score: float        # For quality control
    
    def get_technology_stack(self) -> str:
        """Get comma-separated tech stack for guidelines system."""
        all_tech = set(self.languages + self.frameworks)
        return ','.join(sorted(all_tech))
    
    def get_guidelines_languages(self) -> List[str]:
        """Get languages that have available guidelines (DYNAMIC)."""
        from config.guidelines.manager import get_guidelines_manager
        
        guidelines_manager = get_guidelines_manager()
        available_guidelines = guidelines_manager.get_available_languages()
        
        # Return intersection of detected languages with available guidelines
        return [lang for lang in self.languages if lang in available_guidelines]
    
    def has_guidelines_available(self) -> bool:
        """Check if any detected languages have guidelines available."""
        return len(self.get_guidelines_languages()) > 0
```

##### **Context Formatter Guidelines Compatibility:**
```python
def _generate_context_overview_xml(self, results: List[QueryResult]) -> str:
    """Generate XML with technology stack for guidelines integration."""
    
    # Analyze technical context from results
    tech_context = self._analyze_technical_context(results)
    
    # Generate technology stack in expected format
    tech_stack = tech_context.get_technology_stack()
    
    overview_parts = ["<overview>"]
    overview_parts.append(f"<summary>Found relevant code in {len(projects_data)} projects</summary>")
    
    # CRÍTICO: Manter formato esperado pelo prompt_builder
    overview_parts.append(f"<technology_stack>{tech_stack}</technology_stack>")
    
    # Additional context for smart processing
    overview_parts.append(f"<detected_frameworks>{','.join(tech_context.frameworks)}</detected_frameworks>")
    overview_parts.append(f"<code_patterns>{','.join(tech_context.patterns)}</code_patterns>")
    
    overview_parts.append("</overview>")
    return "\n".join(overview_parts)
```

#### **📊 Unified Imports Structure**

##### **core/query/__init__.py (Unified Exports):**
```python
"""
Unified Query Processing Domain for Context-AI.

Handles complete query processing pipeline:
- Preprocessing and normalization
- Context detection and intent analysis  
- Multi-embedding result merging
- AI-friendly context formatting
- File retrieval intelligence
- Guidelines integration via technology stack
"""

# Current components (moved/unified)
from .preprocessor import (
    QueryPreprocessor,
    ProcessedQuery,
    get_query_preprocessor,
    preprocess_query,
)

from .result_merger import (
    MultiEmbeddingResultMerger,
    QueryResult,
    get_result_merger,
)

from .context_formatter import (  # MOVED from core.formatting
    ContextFormatter,
    FormattedContext,
    get_context_formatter,
    format_results_for_ai,
)

# NEW smart processing components
from .smart_processor import (
    SmartQueryProcessor,
    TechnicalContext,
    ContextDetector,
    SmartExpander,
    get_smart_processor,
)

from .intent_analyzer import (
    IntentAnalyzer,
    QueryIntent,
    IntentBasedOptimizer,
    get_intent_analyzer,
)

from .retrieval_strategy import (
    SmartFileRetriever,
    RetrievalIntent,
    RetrievalStrategy,
    get_retrieval_strategy,
)

# Dictionary system (enhanced)
from .dictionary import (
    LanguageRegistry,
    LanguageDictionary,
    get_language_registry,
    get_synonyms,
    has_synonyms,
    should_remove_word,
)

# Models
from .models.query import (
    ProcessedQuery,
    QueryMetadata,
    SearchTerms,
)

from .models.context import (
    TechnicalContext,
    FormattedContext,
    RetrievalStrategy,
)
```

##### **Import Updates Across Codebase:**
```python
# ANTES (Separated):
from core.formatting.context_formatter import get_context_formatter
from core.query.preprocessor import get_query_preprocessor
from core.query.result_merger import get_result_merger

# DEPOIS (Unified):
from core.query import (
    get_context_formatter,
    get_query_preprocessor, 
    get_result_merger,
    # NEW smart processing
    get_smart_processor,
    get_intent_analyzer,
    get_retrieval_strategy,
    TechnicalContext,
    QueryIntent,
    RetrievalIntent,
)
```

---

### 🎯 **TECHNICAL CATEGORIES**

#### **1. CONTEXT DETECTION ENGINE**

##### **Concept**
Intelligent analysis of query content to determine technical domain, programming languages, frameworks, and architectural patterns mentioned or implied.

##### **Architecture (Direct Implementation - No Over-patterns)**
```python
@dataclass
class TechnicalContext:
    """Immutable context data (Value Object pattern)"""
    languages: List[str]
    frameworks: List[str]
    domains: List[str]
    patterns: List[str]
    intent_signals: List[str]
    confidence_score: float

class ContextDetector:
    """Context detection using languages.yaml configuration"""
    
    def __init__(self):
        # Load language configurations dynamically
        from config.languages.manager import get_languages_manager
        self.languages_manager = get_languages_manager()
        self._language_config = self.languages_manager.get_all_languages()
        
        # Build detection mappings from languages.yaml
        self._build_detection_mappings()
    
    def _build_detection_mappings(self):
        """Build hybrid detection mappings from languages.yaml + additional keywords"""
        
        # 1. Language detection from languages.yaml (base detection)
        self.language_indicators = {}
        self.framework_indicators = {}
        
        for lang_key, lang_config in self._language_config.items():
            # Use separators as base keywords
            separators = lang_config.separators + getattr(lang_config, 'additional_separators', [])
            
            # Clean separators to get meaningful keywords
            base_keywords = []
            for sep in separators:
                clean_sep = sep.strip('\n ').lower()
                if clean_sep and len(clean_sep) > 1 and not clean_sep.startswith('#'):
                    base_keywords.append(clean_sep)
            
            self.language_indicators[lang_key] = {
                'extensions': lang_config.extensions,
                'base_keywords': base_keywords,  # From languages.yaml
                'name': lang_config.name
            }
            
            # Special framework detection for frontend frameworks
            if lang_key in ['vue', 'svelte', 'astro']:
                self.framework_indicators[lang_key] = {
                    'extensions': lang_config.extensions,
                    'keywords': base_keywords,
                    'base_language': getattr(lang_config, 'extends', 'javascript')
                }
        
        # 2. Enhanced keywords (what's missing from languages.yaml)
        self.enhanced_language_keywords = {
            'python': ['python', 'pip', 'conda', 'virtualenv', 'pytest', '__init__', 'django', 'flask'],
            'javascript': ['javascript', 'js', 'node', 'npm', 'yarn', 'async', 'await', 'promise'],
            'typescript': ['typescript', 'ts', 'interface', 'type', 'enum', 'generic'],
            'react': ['react', 'jsx', 'tsx', 'useState', 'useEffect', 'component', 'props', 'hooks'],
            'vue': ['vue', 'v-model', 'v-if', 'v-for', 'directive', 'computed'],
            'java': ['java', 'maven', 'gradle', 'junit', 'spring', 'hibernate'],
            'go': ['go', 'golang', 'goroutine', 'channel', 'interface'],
            'rust': ['rust', 'cargo', 'crates', 'ownership', 'borrowing'],
            'cpp': ['cpp', 'c++', 'cmake', 'make', 'gcc', 'clang', 'std::'],
        }
        
        # 3. Framework detection (not in languages.yaml)
        self.framework_keywords = {
            'react': ['react', 'jsx', 'tsx', 'useState', 'useEffect', 'next.js', 'create-react-app'],
            'angular': ['angular', '@Component', '@Injectable', '@NgModule', 'typescript'],
            'django': ['django', 'model', 'view', 'template', 'ORM', 'drf'],
            'flask': ['flask', 'route', 'request', 'jinja2', 'sqlalchemy'],
            'express': ['express', 'express.js', 'app.get', 'middleware', 'node.js'],
            'spring': ['spring', 'springframework', '@Controller', '@Service', '@Repository'],
        }
        
        # 4. Domain detection (keep these as they're domain-specific)
        self.domain_indicators = {
            'database': ['database', 'sql', 'query', 'table', 'schema', 'migration', 'SELECT', 'INSERT', 'postgresql', 'mysql', 'sqlite'],
            'api': ['api', 'endpoint', 'request', 'response', 'rest', 'graphql', 'GET', 'POST', 'PUT', 'DELETE'],
            'authentication': ['auth', 'login', 'token', 'session', 'password', 'jwt', 'oauth', '2fa', 'bcrypt'],
            'testing': ['test', 'unit', 'integration', 'mock', 'assert', 'jest', 'pytest', 'junit', 'mocha'],
            'deployment': ['deploy', 'docker', 'kubernetes', 'k8s', 'ci/cd', 'jenkins', 'github actions'],
            'configuration': ['config', 'settings', 'env', 'yaml', 'json', 'environment', 'secret'],
        }
    
    def detect_context(self, query: str) -> TechnicalContext:
        """Direct context detection combining multiple methods"""
        query_lower = query.lower()
        
        # Keyword-based detection
        keyword_context = self._keyword_detection(query_lower)
        
        # Pattern-based detection  
        pattern_context = self._pattern_detection(query_lower)
        
        # Merge and return unified context
        return self._merge_contexts(keyword_context, pattern_context)
    
    def _keyword_detection(self, query: str) -> TechnicalContext:
        """Detect context using keyword matching"""
        # Implementation details...
        pass
    
    def _pattern_detection(self, query: str) -> TechnicalContext:
        """Detect context using semantic patterns"""
        # Implementation details...
        pass
    
    def _merge_contexts(self, keyword_ctx: TechnicalContext, pattern_ctx: TechnicalContext) -> TechnicalContext:
        """Merge multiple context detection results"""
        # Implementation details...
        pass
```

##### **Implementation Details**
- **Language Detection:** Regex patterns + keyword matching
- **Framework Detection:** Signature term analysis
- **Domain Classification:** Category mapping from dictionaries
- **Confidence Scoring:** Weighted algorithm based on signal strength

##### **SOLID Compliance**
- **SRP:** Each detector has single responsibility
- **OCP:** New detection strategies without modification
- **LSP:** All strategies interchangeable
- **ISP:** Specific interfaces for specific detection types
- **DIP:** Depends on strategy abstractions

---

#### **2. SMART EXPANSION ENGINE**

##### **Concept**
Context-aware query expansion that selects relevant synonyms and related terms based on detected technical context, avoiding noise from irrelevant expansions.

##### **Architecture (OCP + Factory Pattern)**
```python
class ExpansionStrategy(ABC):
    """Base strategy for query expansion"""
    @abstractmethod
    def expand(self, query: str, context: TechnicalContext) -> List[str]: pass

class ReactExpansionStrategy(ExpansionStrategy):
    """React-specific expansion logic"""
    def expand(self, query: str, context: TechnicalContext) -> List[str]:
        if "react" in context.frameworks:
            # Use React-specific synonyms
            # Add hook-related terms
            # Include component patterns
            pass

class DatabaseExpansionStrategy(ExpansionStrategy):
    """Database-specific expansion logic"""
    
class APIExpansionStrategy(ExpansionStrategy):
    """API-specific expansion logic"""

class ExpansionStrategyFactory:
    """Factory for creating appropriate expansion strategies"""
    def create_strategies(self, context: TechnicalContext) -> List[ExpansionStrategy]:
        strategies = []
        
        if "react" in context.frameworks:
            strategies.append(ReactExpansionStrategy())
        if "database" in context.domains:
            strategies.append(DatabaseExpansionStrategy())
        if "api" in context.domains:
            strategies.append(APIExpansionStrategy())
            
        return strategies

class SmartExpander:
    """Orchestrates context-aware expansion (SRP)"""
    def __init__(self, factory: ExpansionStrategyFactory):
        self._factory = factory
    
    def expand_query(self, query: str, context: TechnicalContext) -> List[str]:
        strategies = self._factory.create_strategies(context)
        expanded_terms = []
        
        for strategy in strategies:
            expanded_terms.extend(strategy.expand(query, context))
        
        return self._deduplicate_and_rank(expanded_terms)
```

##### **Advanced Features**
- **Contextual Filtering:** Remove irrelevant synonyms
- **Semantic Clustering:** Group related expansion terms
- **Confidence Weighting:** Rank expansions by relevance
- **Progressive Expansion:** Multiple levels of expansion depth

---

#### **3. INTENT ANALYSIS SYSTEM**

##### **Concept**
Determine user intent (tutorial, troubleshooting, reference, patterns) to optimize search strategy and result ranking.

##### **Architecture (ISP + Command Pattern)**
```python
class QueryIntent(Enum):
    TUTORIAL = "tutorial"           # "how to", "guide", "example"
    TROUBLESHOOTING = "debug"       # "error", "fix", "problem"
    REFERENCE = "reference"         # "what is", "syntax", "api"
    PATTERNS = "patterns"           # "best practice", "architecture"
    COMPARISON = "comparison"       # "vs", "difference", "compare"

class IntentDetectionRule(ABC):
    """Single intent detection rule (SRP)"""
    @abstractmethod
    def detect(self, query: str) -> Optional[QueryIntent]: pass

class TutorialIntentRule(IntentDetectionRule):
    TUTORIAL_SIGNALS = ["how to", "guide", "tutorial", "example", "learn"]
    
    def detect(self, query: str) -> Optional[QueryIntent]:
        if any(signal in query.lower() for signal in self.TUTORIAL_SIGNALS):
            return QueryIntent.TUTORIAL
        return None

class TroubleshootingIntentRule(IntentDetectionRule):
    DEBUG_SIGNALS = ["error", "fix", "problem", "issue", "debug", "broken"]
    
    def detect(self, query: str) -> Optional[QueryIntent]:
        if any(signal in query.lower() for signal in self.DEBUG_SIGNALS):
            return QueryIntent.TROUBLESHOOTING
        return None

class IntentAnalyzer:
    """Orchestrates intent detection (SRP)"""
    def __init__(self, rules: List[IntentDetectionRule]):
        self._rules = rules
    
    def analyze_intent(self, query: str) -> Optional[QueryIntent]:
        for rule in self._rules:
            intent = rule.detect(query)
            if intent:
                return intent
        return None

class IntentBasedOptimizer:
    """Optimizes search based on detected intent"""
    def optimize_for_intent(self, query: str, intent: QueryIntent) -> SearchOptimization:
        if intent == QueryIntent.TUTORIAL:
            return SearchOptimization(
                prefer_documentation=True,
                boost_example_code=True,
                filter_complex_implementations=True
            )
        elif intent == QueryIntent.TROUBLESHOOTING:
            return SearchOptimization(
                prefer_error_handling=True,
                boost_debugging_content=True,
                include_common_issues=True
            )
        # ... other intents
```

---

#### **4. MULTILINGUAL PROCESSING FRAMEWORK**

##### **Concept**
Extensible multilingual support with cross-language expansion and automatic language detection, designed for easy addition of new languages.

##### **Architecture (DIP + Registry Pattern)**
```python
class LanguageDictionary(ABC):
    """Abstract base for language dictionaries"""
    @abstractmethod
    def get_synonyms(self, word: str) -> List[str]: pass
    
    @abstractmethod
    def get_stop_words(self) -> Set[str]: pass
    
    @abstractmethod
    def get_programming_keywords(self) -> Set[str]: pass
    
    @abstractmethod
    def get_language_code(self) -> str: pass

class EnglishDictionary(LanguageDictionary):
    """English language implementation"""
    def __init__(self):
        from .en import ENGLISH_SYNONYMS, ENGLISH_STOP_WORDS
        self._synonyms = ENGLISH_SYNONYMS
        self._stop_words = ENGLISH_STOP_WORDS
    
    def get_language_code(self) -> str:
        return "en"

class PortugueseDictionary(LanguageDictionary):
    """Portuguese language implementation"""
    def __init__(self):
        from .pt_br import PORTUGUESE_SYNONYMS, PORTUGUESE_STOP_WORDS
        self._synonyms = PORTUGUESE_SYNONYMS
        self._stop_words = PORTUGUESE_STOP_WORDS
    
    def get_language_code(self) -> str:
        return "pt_br"

class LanguageRegistry:
    """Registry for managing language dictionaries (Registry Pattern)"""
    def __init__(self):
        self._dictionaries: Dict[str, LanguageDictionary] = {}
        self._default_language = "en"
    
    def register_language(self, dictionary: LanguageDictionary):
        """Register new language (OCP compliance)"""
        lang_code = dictionary.get_language_code()
        self._dictionaries[lang_code] = dictionary
    
    def get_dictionary(self, lang_code: str) -> LanguageDictionary:
        return self._dictionaries.get(lang_code, self._dictionaries[self._default_language])
    
    def get_supported_languages(self) -> List[str]:
        return list(self._dictionaries.keys())

class LanguageDetector:
    """Detects primary language of query"""
    def detect_language(self, query: str) -> str:
        # Simple heuristic-based detection
        # Can be enhanced with ML models later (YAGNI)
        portuguese_indicators = ["como", "que", "onde", "quando", "porque"]
        english_indicators = ["how", "what", "where", "when", "why"]
        
        pt_score = sum(1 for word in portuguese_indicators if word in query.lower())
        en_score = sum(1 for word in english_indicators if word in query.lower())
        
        return "pt_br" if pt_score > en_score else "en"

class MultilingualProcessor:
    """Orchestrates multilingual processing"""
    def __init__(self, registry: LanguageRegistry, detector: LanguageDetector):
        self._registry = registry
        self._detector = detector
    
    def process_multilingual(self, query: str) -> MultilingualResult:
        # Detect primary language
        primary_lang = self._detector.detect_language(query)
        primary_dict = self._registry.get_dictionary(primary_lang)
        
        # Process in primary language
        primary_expansion = self._expand_in_language(query, primary_dict)
        
        # Cross-language expansion for better coverage
        cross_expansions = {}
        for lang_code in self._registry.get_supported_languages():
            if lang_code != primary_lang:
                dict_obj = self._registry.get_dictionary(lang_code)
                cross_expansions[lang_code] = self._expand_cross_language(query, dict_obj)
        
        return MultilingualResult(
            primary_language=primary_lang,
            primary_expansion=primary_expansion,
            cross_language_expansions=cross_expansions
        )
```

##### **Future Language Support Template**
```python
# Template for adding new languages (Spanish example)
class SpanishDictionary(LanguageDictionary):
    """Spanish language implementation - Future"""
    def __init__(self):
        from .es import SPANISH_SYNONYMS, SPANISH_STOP_WORDS  # Future file
        self._synonyms = SPANISH_SYNONYMS
        self._stop_words = SPANISH_STOP_WORDS
    
    def get_language_code(self) -> str:
        return "es"

# Registration (no code changes needed)
registry.register_language(SpanishDictionary())
```

---

#### **5. PROGRESSIVE ENHANCEMENT PIPELINE**

##### **Concept**
Multi-level query enhancement that progressively adds intelligence while maintaining fallback compatibility.

##### **Architecture (LSP + Decorator Pattern)**
```python
class QueryProcessor(ABC):
    """Base processor interface"""
    @abstractmethod
    def process(self, query: str) -> ProcessedQuery: pass

class BasicQueryProcessor(QueryProcessor):
    """Basic processing (current functionality)"""
    def process(self, query: str) -> ProcessedQuery:
        # Current normalization + basic synonym expansion
        pass

class ContextAwareProcessor(QueryProcessor):
    """Adds context detection (Decorator Pattern)"""
    def __init__(self, base_processor: QueryProcessor, context_detector: ContextDetector):
        self._base_processor = base_processor
        self._context_detector = context_detector
    
    def process(self, query: str) -> ProcessedQuery:
        # Get base processing
        base_result = self._base_processor.process(query)
        
        # Add context detection
        context = self._context_detector.detect_context(query)
        
        return ProcessedQuery(
            **base_result.__dict__,
            technical_context=context
        )

class IntentAwareProcessor(QueryProcessor):
    """Adds intent analysis (Decorator Pattern)"""
    def __init__(self, base_processor: QueryProcessor, intent_analyzer: IntentAnalyzer):
        self._base_processor = base_processor
        self._intent_analyzer = intent_analyzer
    
    def process(self, query: str) -> ProcessedQuery:
        base_result = self._base_processor.process(query)
        intent = self._intent_analyzer.analyze_intent(query)
        
        return ProcessedQuery(
            **base_result.__dict__,
            detected_intent=intent
        )

class SmartQueryProcessor(QueryProcessor):
    """Full smart processing (Decorator Pattern)"""
    def __init__(
        self,
        base_processor: QueryProcessor,
        smart_expander: SmartExpander,
        multilingual_processor: MultilingualProcessor
    ):
        self._base_processor = base_processor
        self._smart_expander = smart_expander
        self._multilingual_processor = multilingual_processor
    
    def process(self, query: str) -> ProcessedQuery:
        base_result = self._base_processor.process(query)
        
        # Smart expansion based on context
        if hasattr(base_result, 'technical_context'):
            smart_expansion = self._smart_expander.expand_query(
                query, base_result.technical_context
            )
        else:
            smart_expansion = []
        
        # Multilingual processing
        multilingual_result = self._multilingual_processor.process_multilingual(query)
        
        return ProcessedQuery(
            **base_result.__dict__,
            smart_expansion=smart_expansion,
            multilingual_result=multilingual_result
        )
```

---

#### **6. FILE RETRIEVAL INTELLIGENCE**

##### **Concept**
Intelligent determination of when to retrieve complete files versus individual chunks based on query intent, context, and content analysis. This optimization improves relevance by providing appropriate granularity of information.

##### **Architecture (Strategy + Template Method Pattern)**
```python
@dataclass
class RetrievalStrategy:
    """Strategy for file vs chunk retrieval"""
    prefer_complete_files: bool
    max_file_size_kb: int
    chunk_overlap_required: bool
    content_type_filter: Optional[List[str]]

class RetrievalIntent(Enum):
    CHUNK_LEVEL = "chunk"           # Specific code snippets, functions
    FILE_LEVEL = "file"             # Complete implementations, configurations
    HYBRID = "chunk_plus_file"      # Both chunks AND complete files
    MULTI_FILE = "multi_file"       # Cross-file relationships, architecture
    FULL = "full_analysis"          # Complete analysis: chunks + files + cross-file + dependencies

class FileRetrievalAnalyzer:
    """Analyzes query to determine optimal retrieval strategy"""
    
    # Signals that indicate need for complete files
    COMPLETE_FILE_SIGNALS = {
        "implementation": ["full implementation", "complete code", "entire file", "whole class"],
        "configuration": ["config file", "settings", "configuration", "env", "yaml", "json"],
        "architecture": ["structure", "organization", "layout", "architecture", "design"],
        "examples": ["example", "template", "boilerplate", "starter", "scaffold"],
        "documentation": ["readme", "docs", "documentation", "guide", "tutorial"]
    }
    
    # File types that benefit from complete retrieval
    COMPLETE_FILE_TYPES = {
        "config": [".json", ".yaml", ".yml", ".env", ".ini", ".toml"],
        "small_code": [".sql", ".sh", ".bat", ".dockerfile"],
        "documentation": [".md", ".rst", ".txt"],
        "templates": [".html", ".xml", ".svg"]
    }
    
    def analyze_retrieval_intent(self, query: str, context: TechnicalContext) -> RetrievalIntent:
        """Determine optimal retrieval strategy based on query analysis"""
        query_lower = query.lower()
        
        # Check for complete file signals
        for category, signals in self.COMPLETE_FILE_SIGNALS.items():
            if any(signal in query_lower for signal in signals):
                return RetrievalIntent.FILE_LEVEL
        
        # Check for architecture/cross-file queries
        architecture_signals = ["how files", "project structure", "relationship", "imports", "dependencies"]
        if any(signal in query_lower for signal in architecture_signals):
            return RetrievalIntent.MULTI_FILE
        
        # Default to chunk level for specific code searches
        return RetrievalIntent.CHUNK_LEVEL

class SmartRetrievalStrategy(ABC):
    """Base strategy for intelligent retrieval"""
    @abstractmethod
    def should_retrieve_complete_file(self, file_metadata: Dict[str, Any], query_context: TechnicalContext) -> bool: pass
    
    @abstractmethod
    def get_retrieval_params(self) -> RetrievalStrategy: pass

class ConfigFileRetrievalStrategy(SmartRetrievalStrategy):
    """Strategy for configuration files - prefer complete files"""
    
    def should_retrieve_complete_file(self, file_metadata: Dict[str, Any], query_context: TechnicalContext) -> bool:
        file_path = file_metadata.get("file_path", "")
        file_extension = Path(file_path).suffix.lower()
        
        # Configuration files are usually small and benefit from complete context
        if file_extension in [".json", ".yaml", ".yml", ".env", ".ini", ".toml"]:
            return True
        
        # Package files (dependencies, manifests)
        if any(name in file_path.lower() for name in ["package.json", "requirements.txt", "cargo.toml", "pom.xml"]):
            return True
            
        return False
    
    def get_retrieval_params(self) -> RetrievalStrategy:
        return RetrievalStrategy(
            prefer_complete_files=True,
            max_file_size_kb=100,  # Config files are usually small
            chunk_overlap_required=False,
            content_type_filter=["config", "manifest"]
        )

class DocumentationRetrievalStrategy(SmartRetrievalStrategy):
    """Strategy for documentation files - prefer complete files for context"""
    
    def should_retrieve_complete_file(self, file_metadata: Dict[str, Any], query_context: TechnicalContext) -> bool:
        file_path = file_metadata.get("file_path", "")
        file_extension = Path(file_path).suffix.lower()
        
        # Documentation files benefit from complete context
        if file_extension in [".md", ".rst", ".txt"]:
            return True
            
        # README files are important for project understanding
        if "readme" in file_path.lower():
            return True
            
        return False
    
    def get_retrieval_params(self) -> RetrievalStrategy:
        return RetrievalStrategy(
            prefer_complete_files=True,
            max_file_size_kb=500,  # Documentation can be longer
            chunk_overlap_required=False,
            content_type_filter=["documentation", "guide"]
        )

class CodeRetrievalStrategy(SmartRetrievalStrategy):
    """Strategy for code files - prefer chunks unless specific intent detected"""
    
    def should_retrieve_complete_file(self, file_metadata: Dict[str, Any], query_context: TechnicalContext) -> bool:
        file_path = file_metadata.get("file_path", "")
        file_size = file_metadata.get("file_size_kb", 0)
        
        # Small utility files can be retrieved completely
        if file_size < 10:  # Less than 10KB
            return True
        
        # Specific file types that benefit from complete context
        if any(pattern in file_path.lower() for pattern in ["utils", "helpers", "constants", "types", "interfaces"]):
            return True
            
        return False
    
    def get_retrieval_params(self) -> RetrievalStrategy:
        return RetrievalStrategy(
            prefer_complete_files=False,
            max_file_size_kb=50,  # Larger code files stay as chunks
            chunk_overlap_required=True,  # Maintain context between chunks
            content_type_filter=["code", "implementation"]
        )

class RetrievalStrategyFactory:
    """Factory for creating appropriate retrieval strategies"""
    
    def create_strategy(self, intent: RetrievalIntent, context: TechnicalContext) -> SmartRetrievalStrategy:
        # Configuration intent
        if "config" in context.domains or "settings" in context.domains:
            return ConfigFileRetrievalStrategy()
        
        # Documentation intent  
        if intent == RetrievalIntent.FILE_LEVEL and "documentation" in context.domains:
            return DocumentationRetrievalStrategy()
        
        # Default to code strategy
        return CodeRetrievalStrategy()

class SmartFileRetriever:
    """Orchestrates intelligent file vs chunk retrieval"""
    
    def __init__(self, factory: RetrievalStrategyFactory, analyzer: FileRetrievalAnalyzer):
        self._factory = factory
        self._analyzer = analyzer
        self.logger = get_logger(__name__)
    
    def determine_retrieval_approach(self, query: str, context: TechnicalContext, search_results: List[QueryResult]) -> Dict[str, Any]:
        """Determine optimal retrieval approach for search results"""
        
        # Analyze query intent
        retrieval_intent = self._analyzer.analyze_retrieval_intent(query, context)
        
        # Get appropriate strategy
        strategy = self._factory.create_strategy(retrieval_intent, context)
        retrieval_params = strategy.get_retrieval_params()
        
        # Analyze each result to determine file vs chunk retrieval
        retrieval_decisions = []
        complete_files_needed = []
        
        for result in search_results:
            should_get_complete = strategy.should_retrieve_complete_file(
                result.metadata, context
            )
            
            if should_get_complete:
                file_path = result.metadata.get("file_path")
                if file_path and file_path not in complete_files_needed:
                    complete_files_needed.append(file_path)
            
            retrieval_decisions.append({
                "result": result,
                "retrieve_complete_file": should_get_complete,
                "strategy_used": strategy.__class__.__name__
            })
        
        # Log decision summary
        chunk_count = len([d for d in retrieval_decisions if not d["retrieve_complete_file"]])
        file_count = len(complete_files_needed)
        
        self.logger.info(
            "🎯 Retrieval Strategy: %s chunks + %s complete files (intent: %s)",
            chunk_count, file_count, retrieval_intent.value
        )
        
        return {
            "retrieval_intent": retrieval_intent,
            "strategy_params": retrieval_params,
            "decisions": retrieval_decisions,
            "complete_files_needed": complete_files_needed,
            "summary": {
                "chunk_results": chunk_count,
                "complete_files": file_count,
                "strategy_used": strategy.__class__.__name__
            }
        }

# Integration with existing embedding service
class EnhancedEmbeddingService:
    """Enhanced embedding service with smart file retrieval"""
    
    def __init__(self, base_service, file_retriever: SmartFileRetriever):
        self._base_service = base_service
        self._file_retriever = file_retriever
    
    def query_with_smart_retrieval(self, query: str, context: TechnicalContext) -> List[QueryResult]:
        """Execute query with intelligent file vs chunk retrieval"""
        
        # Get initial chunk-based results
        chunk_results = self._base_service.query_embeddings(query)
        
        # Determine optimal retrieval approach
        retrieval_plan = self._file_retriever.determine_retrieval_approach(
            query, context, chunk_results
        )
        
        # Execute retrieval plan
        final_results = []
        
        # Add chunk results that don't need complete files
        for decision in retrieval_plan["decisions"]:
            if not decision["retrieve_complete_file"]:
                final_results.append(decision["result"])
        
        # Add complete file results
        for file_path in retrieval_plan["complete_files_needed"]:
            complete_file_result = self._retrieve_complete_file(file_path)
            if complete_file_result:
                final_results.append(complete_file_result)
        
        return final_results
    
    def _retrieve_complete_file(self, file_path: str) -> Optional[QueryResult]:
        """Retrieve complete file content from embeddings"""
        # Implementation would query embeddings for all chunks of a specific file
        # and reconstruct the complete file content
        # This leverages existing embedding infrastructure
        pass
```

##### **Implementation Benefits**
- **Context-Aware Retrieval:** Automatically selects optimal granularity
- **Performance Optimization:** Reduces unnecessary large file transfers
- **Improved Relevance:** Complete files when needed, chunks for specifics
- **SOLID Compliance:** Strategy pattern allows easy extension of retrieval logic

##### **Use Cases Examples**
```python
# Query: "show me the complete package.json"
# → RetrievalIntent.FILE_LEVEL, ConfigFileRetrievalStrategy
# → Returns complete package.json file

# Query: "how to handle authentication errors"  
# → RetrievalIntent.CHUNK_LEVEL, CodeRetrievalStrategy
# → Returns relevant code chunks about error handling

# Query: "project structure and file organization"
# → RetrievalIntent.MULTI_FILE, DocumentationRetrievalStrategy  
# → Returns README + multiple architecture files

# Query: "complete implementation of user service"
# → RetrievalIntent.FILE_LEVEL, CodeRetrievalStrategy
# → Returns complete service class file

# Query: "how authentication flows work across the entire application"
# → RetrievalIntent.HYBRID, CodeRetrievalStrategy
# → Returns auth-related chunks + complete auth config files

# Query: "analyze the complete authentication architecture and dependencies"
# → RetrievalIntent.FULL, FullAnalysisStrategy
# → Returns: auth chunks + complete files + related dependencies + 
#            cross-file imports + dependency tree + related configs
#            Example: auth.service.ts chunks + complete auth.config.js + 
#            middleware files + database models + API routes + tests

# Query: "understand how data flows from API to database including all middleware"
# → RetrievalIntent.FULL, FullAnalysisStrategy  
# → Returns: API chunks + complete middleware files + database schemas +
#            request/response flow + error handling + logging + validation
```

##### **FULL Analysis Strategy Benefits**
```python
class FullAnalysisStrategy(SmartRetrievalStrategy):
    """Strategy for comprehensive analysis - chunks + files + dependencies + cross-file"""
    
    def should_retrieve_complete_file(self, file_metadata: Dict[str, Any], query_context: TechnicalContext) -> bool:
        # Always include small critical files (configs, types, constants)
        file_path = file_metadata.get("file_path", "")
        file_size = file_metadata.get("file_size_kb", 0)
        
        # Include all config, type definition, and interface files
        if any(pattern in file_path.lower() for pattern in [
            "config", "types", "interfaces", "constants", "schema", "model"
        ]):
            return True
            
        # Include small files that provide context
        if file_size < 15:  # Increased threshold for FULL analysis
            return True
            
        return False
    
    def get_retrieval_params(self) -> RetrievalStrategy:
        return RetrievalStrategy(
            prefer_complete_files=True,
            max_file_size_kb=100,  # Higher threshold for comprehensive analysis
            chunk_overlap_required=True,  # Always maintain context
            content_type_filter=None  # No filtering - include everything relevant
        )
    
    def analyze_dependencies(self, query: str, context: TechnicalContext) -> List[str]:
        """Analyze and retrieve related dependencies and cross-file references"""
        # This would analyze import statements, require() calls, dependencies
        # and return additional files that should be included for complete context
        pass
```

---

### 🚀 **IMPLEMENTATION PHASES**

#### **Phase 0: Structure Migration (Week 0)**
**YAGNI Focus:** Clean migration to unified structure without compatibility layers

##### **Deliverables:**
- [ ] **Move** `core/formatting/context_formatter.py` → `core/query/context_formatter.py`
- [ ] **Delete** `core/formatting/` directory completely
- [ ] **Update all imports** across codebase:
  ```python
  # ANTES:
  from core.formatting.context_formatter import get_context_formatter
  
  # DEPOIS:
  from core.query.context_formatter import get_context_formatter
  # OU melhor ainda:
  from core.query import get_context_formatter
  ```
- [ ] **Update** `core/query/__init__.py` with unified exports
- [ ] **Update imports** in all affected files:
  - [ ] `services/embedding_service.py`
  - [ ] `services/ai_service.py`
  - [ ] `commands/query.py`
  - [ ] `commands/ask.py`
  - [ ] `commands/chat.py`
  - [ ] Any test files importing from `core.formatting`

##### **Acceptance Criteria:**
- All imports updated successfully
- Zero test failures after migration
- Clean directory structure with no orphaned files
- No `core.formatting` references remaining
- All CLI commands working correctly
- **CRITICAL:** Technology stack XML format preserved for guidelines integration

#### **Phase 1: Foundation (Week 1-2)**
**YAGNI Focus:** Core architecture without advanced features

##### **Deliverables:**
- [ ] `TechnicalContext` value object in `core/query/models/context.py`
- [ ] `ContextDetector` with basic keyword detection in `core/query/smart_processor.py`
- [ ] `LanguageRegistry` in `core/query/dictionary/registry.py`
- [ ] `MultilingualProcessor` basic implementation in `core/query/smart_processor.py`
- [ ] **Guidelines Integration:** Enhanced `TechnicalContext` with `get_technology_stack()` method
- [ ] **Context Formatter:** Updated to maintain `<technology_stack>` XML format
- [ ] Unit tests for core components

##### **Acceptance Criteria:**
- Context detection accuracy >70% on test queries
- Multilingual expansion working for en/pt_br
- **CRITICAL:** Technology stack detection working and XML format preserved
- **CRITICAL:** Guidelines system integration maintained (prompt_builder compatibility)
- Zero breaking changes to existing API
- 100% test coverage for new components

#### **Phase 2: Smart Expansion (Week 3-4)**
**YAGNI Focus:** Context-aware expansion without over-engineering

##### **Deliverables:**
- [ ] `ExpansionStrategy` interface and implementations
- [ ] `SmartExpander` with context-aware logic
- [ ] React/Database/API specific expansion strategies
- [ ] Performance benchmarks and optimization

##### **Acceptance Criteria:**
- Query expansion relevance >80%
- Processing overhead <50ms
- Configurable expansion levels
- Backward compatibility maintained

#### **Phase 3: Intent Analysis (Week 5-6)**
**YAGNI Focus:** Basic intent detection for major use cases

##### **Deliverables:**
- [ ] `IntentAnalyzer` with rule-based detection
- [ ] Intent-based search optimization
- [ ] Integration with existing search pipeline
- [ ] Performance monitoring and benchmarks

##### **Acceptance Criteria:**
- Intent detection accuracy >75%
- Measurable improvement in result relevance
- Direct integration with search pipeline
- Performance impact <10ms

#### **Phase 4: Progressive Enhancement (Week 7-8)**
**YAGNI Focus:** Decorator pattern for complete system integration

##### **Deliverables:**
- [ ] Decorator-based processor pipeline
- [ ] Complete smart processing integration
- [ ] Performance monitoring and metrics
- [ ] Documentation and migration guide

##### **Acceptance Criteria:**
- Seamless integration with existing system
- All enhancement levels working together
- Direct deployment without complexity
- Complete documentation

---

### 📊 **PERFORMANCE & SCALABILITY**

#### **Performance Targets**
- **Query Processing:** <50ms total overhead
- **Context Detection:** <10ms
- **Smart Expansion:** <20ms
- **Multilingual Processing:** <15ms
- **Memory Usage:** <50MB additional footprint

#### **Caching Strategy**
```python
class QueryProcessingCache:
    """LRU cache for processed queries"""
    def __init__(self, max_size: int = 10000, ttl_seconds: int = 3600):
        self._cache = {}
        self._max_size = max_size
        self._ttl = ttl_seconds
    
    def get_or_process(self, query: str, processor: Callable) -> ProcessedQuery:
        cache_key = self._generate_cache_key(query)
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]["result"]
        
        result = processor(query)
        self._cache_result(cache_key, result)
        return result
```

#### **Scalability Considerations**
- **Horizontal Scaling:** Stateless processors
- **Memory Optimization:** Lazy loading of dictionaries
- **CPU Optimization:** Parallel processing for multiple strategies
- **I/O Optimization:** Async processing where applicable

---

### 🧪 **TESTING STRATEGY**

#### **Unit Tests (>95% Coverage)**
```python
class TestContextDetector:
    def test_react_context_detection(self):
        detector = ContextDetector([KeywordBasedDetector()])
        context = detector.detect_context("react component props")
        
        assert "react" in context.frameworks
        assert "frontend" in context.domains
        assert context.confidence_score > 0.8

class TestSmartExpander:
    def test_react_specific_expansion(self):
        context = TechnicalContext(frameworks=["react"])
        expander = SmartExpander(ExpansionStrategyFactory())
        
        expanded = expander.expand_query("component state", context)
        
        assert "useState" in expanded
        assert "props" in expanded
        assert "hooks" in expanded
```

#### **Integration Tests**
```python
class TestSmartQueryPipeline:
    def test_end_to_end_processing(self):
        processor = self._create_full_processor()
        
        result = processor.process("como fazer autenticação react")
        
        assert result.detected_language == "pt_br"
        assert "react" in result.technical_context.frameworks
        assert "authentication" in result.smart_expansion
        assert result.detected_intent == QueryIntent.TUTORIAL
```

#### **Performance Tests**
```python
class TestPerformance:
    def test_processing_latency(self):
        processor = SmartQueryProcessor(...)
        
        start_time = time.time()
        processor.process("complex query with multiple contexts")
        end_time = time.time()
        
        assert (end_time - start_time) < 0.05  # 50ms limit
```

---

### 🔄 **MIGRATION PLAN**

#### **Clean Import Migration Strategy**
**No backward compatibility - direct migration with complete export audit**

##### **Step 1: Complete Export Audit**
```python
# Audit ALL exports from core.formatting
CORE_FORMATTING_EXPORTS = {
    "classes": [
        "ContextFormatter",
        "FormattedContext", 
    ],
    "functions": [
        "get_context_formatter",
        "format_results_for_ai",
        "count_tokens",
    ],
    "constants": [
        "RESULT_HEADER_TEMPLATE",
        "SOURCE_HEADER_TEMPLATE", 
        "FILE_INFO_TEMPLATE",
    ]
}

# Search ALL imports across codebase
IMPORT_SEARCH_PATTERNS = [
    "from core.formatting",
    "import core.formatting", 
    "core.formatting.",
]
```

##### **Step 2: Mass Import Update**
```python
# Direct import mapping (no compatibility layers)
IMPORT_MIGRATIONS = {
    "from core.formatting.context_formatter import ContextFormatter": 
        "from core.query import ContextFormatter",
    "from core.formatting.context_formatter import get_context_formatter": 
        "from core.query import get_context_formatter",
    "from core.formatting import format_results_for_ai": 
        "from core.query import format_results_for_ai",
    # ... complete mapping for ALL exports
}
```

##### **Step 3: Clean Deletion**
- **Move** `context_formatter.py` to `core/query/`
- **Update** `core/query/__init__.py` with ALL exports
- **Update** ALL import statements simultaneously
- **Delete** `core/formatting/` directory completely
- **Verify** zero broken imports with full test suite

#### **Direct Implementation Strategy**
**No feature flags - all smart processing enabled by default**

```python
class SmartQueryProcessor:
    """Direct implementation without feature flags"""
    def __init__(self):
        # All features enabled - no conditional logic
        self.context_detector = ContextDetector()
        self.intent_analyzer = IntentAnalyzer()
        self.smart_expander = SmartExpander()
        self.multilingual_processor = MultilingualProcessor()
        self.file_retriever = SmartFileRetriever()
    
    def process(self, query: str) -> ProcessedQuery:
        # Direct execution path - no feature checking
        context = self.context_detector.detect_context(query)
        intent = self.intent_analyzer.analyze_intent(query)
        expanded_terms = self.smart_expander.expand_query(query, context)
        
        return ProcessedQuery(
            original=query,
            technical_context=context,
            detected_intent=intent,
            smart_expansion=expanded_terms,
            multilingual_result=self.multilingual_processor.process_multilingual(query)
        )
```

#### **Deployment Strategy**
**Simple, direct deployment without gradual rollout**

1. **Complete migration** in single deployment
2. **Full smart processing** enabled immediately
3. **Thorough testing** before deployment
4. **Monitor** performance and quality metrics
5. **Fix issues** directly without rollback complexity

---

### 📈 **SUCCESS METRICS**

#### **Technical Metrics**
- **Query Processing Latency:** <50ms (current: ~5ms)
- **Memory Usage:** <50MB additional
- **CPU Usage:** <20% increase
- **Cache Hit Rate:** >80%

#### **Quality Metrics**
- **Context Detection Accuracy:** >85%
- **Intent Detection Accuracy:** >80%
- **Expansion Relevance:** >85%
- **Cross-Language Coverage:** >90%

#### **Business Metrics**
- **Search Result Relevance:** +40% improvement
- **User Query Success Rate:** +25% improvement
- **Time to Find Information:** -30% reduction
- **User Satisfaction Score:** +20% improvement

---

### 🔮 **FUTURE ROADMAP**

#### **Phase 5: Machine Learning Enhancement (Future)**
- **Semantic Embeddings:** For better context understanding
- **Query Intent Classification:** ML-based intent detection
- **Personalized Expansion:** User-specific query enhancement
- **Feedback Learning:** Continuous improvement from user interactions

#### **Phase 6: Advanced Language Support (Future)**
- **Spanish (es):** Hispanic market expansion
- **French (fr):** European market expansion
- **German (de):** DACH region support
- **Asian Languages:** Japanese, Chinese, Korean support

#### **Phase 7: Enterprise Features (Future)**
- **Custom Dictionaries:** Organization-specific terminology
- **Domain-Specific Models:** Industry-specific processing
- **Analytics Dashboard:** Query processing insights
- **API Rate Limiting:** Enterprise-grade controls

---

### 📚 **REFERENCES & STANDARDS**

#### **Design Patterns**
- **Strategy Pattern:** Gang of Four, Design Patterns (1994)
- **Registry Pattern:** Martin Fowler, Patterns of Enterprise Application Architecture
- **Decorator Pattern:** Gang of Four, Design Patterns (1994)
- **Factory Pattern:** Gang of Four, Design Patterns (1994)

#### **Architecture Principles**
- **SOLID Principles:** Robert C. Martin, Clean Code (2008)
- **Clean Architecture:** Robert C. Martin, Clean Architecture (2017)
- **DRY Principle:** Andy Hunt, The Pragmatic Programmer (1999)
- **YAGNI Principle:** Extreme Programming practices

#### **Performance Standards**
- **Google Web Vitals:** <100ms for good user experience
- **Nielsen's Response Time Guidelines:** <100ms feels instantaneous
- **Industry Benchmarks:** Search processing <50ms standard

---

**Este plano segue rigorosamente os princípios SOLID, DRY, Clean Code, Clean Architecture e YAGNI, fornecendo uma roadmap detalhada para implementar um sistema de Smart Query Processing de classe mundial.**
