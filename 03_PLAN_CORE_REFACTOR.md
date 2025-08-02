# 🎯 PLANO 03: CORE MODULES REFACTOR

## 📋 COMO USAR ESTE PLANO

Este arquivo é nosso **guia de desenvolvimento** para refatorar os módulos core do Context-AI.

### **📖 INSTRUÇÕES DE USO:**

1. **Siga a ordem sequencial** - cada fase depende da anterior
2. **Marque os checkboxes** ✅ conforme completar cada item
3. **Teste após cada fase** - valide antes de prosseguir
4. **Documente problemas** na seção "🐛 ISSUES ENCONTRADAS" no final
5. **Não pule etapas** - cada passo tem dependências específicas

### **🔄 FLUXO DE TRABALHO:**
```
FASE 1: Chunking Refactor → FASE 2: Embeddings Extensibility → FASE 3: Query Consolidation → FASE 4: Validação Final
```

### **🎯 OBJETIVOS PRINCIPAIS:**
- ✅ **Chunking** com protocol + models + melhor language detection
- ✅ **Embeddings** extensível para novos providers/vector stores
- ✅ **Query pipeline** completo consolidado
- ✅ **Zero duplicação** de código
- ✅ **Backward compatibility** mantida

### **📋 PRÉ-REQUISITOS:**
⚠️ **Este plano assume que os planos anteriores já foram executados:**
- **01_PLAN_CONFIG_REFACTOR:** Settings/Storage managers centralizados
- **02_PLAN_TOKEN_MANAGER:** TokenManager centralizado disponível
  - TokenManager centralizado já está disponível em `core/ai/token_manager.py`
  - Todas as duplicações de token counting já foram eliminadas
  - Provider-aware counting (Anthropic + Tiktoken) já funciona

---

## 📊 **SITUAÇÃO ATUAL IDENTIFICADA:**

### **🧩 CHUNKING - MELHORAR**
- **Protocol + models misturados** no mesmo arquivo
- **Language detection simples** - não usa extends/additional_separators
- **Token counting já centralizado**

### **🤖 EMBEDDINGS - POUCO EXTENSÍVEL**
- **Hardcoded model list** - não configurável
- **ChromaDB coupling** - sem abstração
- **Single provider** - só sentence-transformers

### **🔍 QUERY - DISPERSO**  
- **Context formatter** em módulo separado (deveria estar em query)
- **Data classes** espalhadas
- **Token counting já centralizado** - usar get_token_manager()

---

## 🧩 FASE 1: CHUNKING MODULE REFACTOR

### **🚀 FASE 1.1: SEPARAR PROTOCOL E MODELS**

#### **📦 1.1.1 Criar models.py**

- [ ] Criar arquivo `src/core/chunking/models.py`
- [ ] Mover `TextChunk` de `protocol.py` para `models.py`
- [ ] Mover `ChunkingStrategy` de `protocol.py` para `models.py`  
- [ ] Mover `ChunkingMetadata` de `protocol.py` para `models.py`
- [ ] Adicionar `__all__` exports em `models.py`

#### **📝 1.1.2 Estrutura do models.py**

```python
"""
Data models for text chunking in Context-AI.

Contains data classes and metadata constants used across
different chunking implementations.
"""

from dataclasses import dataclass
from typing import Any, Dict

from config.constants.chunking import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_MIN_CHUNK_SIZE,
)

@dataclass
class TextChunk:
    """Represents a single text chunk with metadata."""

    def __init__(self, text: str, metadata: Dict[str, Any]):
        """
        Initialize a text chunk.

        Args:
            text: The chunk content
            metadata: Metadata about the chunk
        """
        self.text = text
        self.metadata = metadata

    def __repr__(self) -> str:
        return f"TextChunk(text={self.text[:50]}..., metadata={self.metadata})"

    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary."""
        return {"text": self.text, "metadata": self.metadata}

@dataclass  
class ChunkingStrategy:
    """Configuration for chunking behavior."""

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
        preserve_structure: bool = True,
        include_imports: bool = True,
        min_chunk_size: int = DEFAULT_MIN_CHUNK_SIZE,
    ):
        """
        Initialize chunking strategy.

        Args:
            chunk_size: Target size for chunks in characters
            chunk_overlap: Overlap between consecutive chunks
            preserve_structure: Try to preserve code/document structure
            include_imports: Include import statements in chunks
            min_chunk_size: Minimum size for a chunk to be valid
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.preserve_structure = preserve_structure
        self.include_imports = include_imports
        self.min_chunk_size = min_chunk_size

    def to_dict(self) -> Dict[str, Any]:
        """Convert strategy to dictionary."""
        return {
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "preserve_structure": self.preserve_structure,
            "include_imports": self.include_imports,
            "min_chunk_size": self.min_chunk_size,
        }

class ChunkingMetadata:
    """Standard metadata fields for chunks."""

    # Required fields
    FILE_PATH = "file_path"
    CHUNK_INDEX = "chunk_index"
    CHUNKER_NAME = "chunker"
    LANGUAGE = "language"

    # Optional fields
    START_LINE = "start_line"
    END_LINE = "end_line"
    FUNCTION_NAME = "function_name"
    CLASS_NAME = "class_name"
    CHUNK_TYPE = "chunk_type"  # e.g., "function", "class", "comment", "import"
    TOKEN_COUNT = "token_count"

    # File metadata
    FILE_SIZE = "file_size"
    FILE_MODIFIED = "file_modified"

    @classmethod
    def create_base_metadata(
        cls, file_path: str, chunk_index: int, chunker_name: str, language: str = None
    ) -> Dict[str, Any]:
        """
        Create base metadata dictionary with required fields.

        Args:
            file_path: Path to the source file
            chunk_index: Index of this chunk in the file
            chunker_name: Name of the chunker that created this chunk
            language: Programming language (auto-detected if None)

        Returns:
            Dictionary with base metadata
        """
        metadata = {
            cls.FILE_PATH: file_path,
            cls.CHUNK_INDEX: chunk_index,
            cls.CHUNKER_NAME: chunker_name,
        }

        if language:
            metadata[cls.LANGUAGE] = language

        return metadata

__all__ = [
    'TextChunk',
    'ChunkingStrategy', 
    'ChunkingMetadata',
]
```

#### **📦 1.1.3 Limpar protocol.py**

- [ ] Abrir `core/chunking/protocol.py`
- [ ] Remover classes `TextChunk`, `ChunkingStrategy`, `ChunkingMetadata` (agora em models.py)
- [ ] Adicionar import: `from .models import TextChunk, ChunkingStrategy, ChunkingMetadata`
- [ ] Manter só a classe `ChunkerProtocol` abstract
- [ ] Verificar que protocol.py está limpo (só interfaces)

#### **📦 1.1.4 Atualizar langchain_adapter.py**

- [ ] Abrir `core/chunking/langchain_adapter.py`
- [ ] Adicionar import: `from .models import TextChunk, ChunkingMetadata, ChunkingStrategy`
- [ ] Verificar que não há mais imports de protocol.py para data classes

#### **📦 1.1.5 Atualizar __init__.py**

- [ ] Abrir `core/chunking/__init__.py`
- [ ] Adicionar imports: `from .models import TextChunk, ChunkingStrategy, ChunkingMetadata`
- [ ] Verificar que `__all__` inclui os novos imports

---

### **🔧 FASE 1.2: MELHORAR LANGUAGE DETECTION**

#### **📦 1.2.1 Implementar Detection Robusta**

- [ ] Abrir `core/chunking/langchain_adapter.py`
- [ ] Localizar método `_detect_language_from_content()`
- [ ] Substituir implementação por versão melhorada:

```python
def _detect_language_from_content(self, content: str) -> str:
    """Enhanced language detection using separators + additional_separators + extends."""
    
    try:
        languages_data = self.languages_manager.get_all_languages_data()
        scores = {}
        content_lower = content.lower()
        
        for lang_key, lang_data in languages_data.items():
            score = 0
            all_separators = []
            
            # 1. Get base separators
            all_separators.extend(lang_data.get('separators', []))
            
            # 2. Handle 'extends' - inherit from parent language
            if 'extends' in lang_data:
                parent_lang = lang_data['extends']
                if parent_lang in languages_data:
                    parent_separators = languages_data[parent_lang].get('separators', [])
                    all_separators.extend(parent_separators)
            
            # 3. Add additional_separators
            all_separators.extend(lang_data.get('additional_separators', []))
            
            # 4. Score based on separator matches
            for separator in all_separators:
                clean_sep = separator.replace('\n', '').strip()
                if clean_sep and clean_sep in content_lower:
                    # Additional separators têm peso maior (mais específicos)
                    weight = 3 if separator in lang_data.get('additional_separators', []) else 1
                    score += weight
            
            # 5. Score based on extensions in imports/requires  
            extensions = lang_data.get('extensions', [])
            for ext in extensions:
                if ext in content_lower:  # Like ".py" in import statements
                    score += 2
                    
            if score > 0:
                scores[lang_key] = score
        
        # Return language with highest score
        if scores:
            best_lang = max(scores.items(), key=lambda x: x[1])[0]
            self.logger.debug(f"Language detection scores: {scores}, selected: {best_lang}")
            return best_lang
        else:
            return "text"
            
    except Exception as e:
        self.logger.warning(f"Language detection failed: {e}, falling back to simple detection")
        # Fallback to simple detection
        return self._simple_language_detection(content)

def _simple_language_detection(self, content: str) -> str:
    """Fallback simple language detection."""
    content_lower = content.lower()

    if "def " in content or "import " in content or "class " in content:
        return "python"
    elif "function " in content or "const " in content or "let " in content:
        return "javascript"
    elif "interface " in content or "type " in content or ": string" in content:
        return "typescript"
    elif "<html" in content_lower or "<div" in content_lower:
        return "html"
    elif content.strip().startswith("#") or "##" in content:
        return "markdown"
    elif "{" in content and '"' in content:
        return "json"
    else:
        return "text"
```

#### **🧪 1.2.2 Testar Language Detection**

- [ ] Testar com código Python (deve detectar via "def ", "class ", etc.)
- [ ] Testar com TypeScript (deve usar extends + additional_separators)
- [ ] Testar com código desconhecido (deve fallback para "text")
- [ ] Verificar logs de debug para scores

---

### **🧪 FASE 1.3: TESTES DA FASE 1**

#### **🔍 1.3.1 Testes de Import e Estrutura**

- [ ] Testar imports novos:
  - [ ] `from core.chunking import TextChunk, ChunkingStrategy, ChunkingMetadata`
  - [ ] `from core.chunking.models import TextChunk`
  - [ ] `from core.chunking.protocol import ChunkerProtocol`
- [ ] Verificar que não há circular imports
- [ ] Verificar que `get_chunker()` funciona normalmente

#### **🔍 1.3.2 Testes de Funcionalidade**

- [ ] Testar chunking de arquivo Python (deve usar detection melhorada)
- [ ] Testar chunking de arquivo TypeScript (deve detectar corretamente)
- [ ] Verificar que metadata inclui language correto
- [ ] Verificar que não há token counting duplicado

---

## 🤖 FASE 2: EMBEDDINGS MODULE EXTENSIBILITY

### **🚀 FASE 2.1: CRIAR PROTOCOLS DE EXTENSIBILIDADE**

#### **📦 2.1.1 Criar model_protocol.py**

- [ ] Criar arquivo `src/core/embeddings/model_protocol.py`
- [ ] Implementar interface abstrata para model providers

```python
"""
Model provider protocol for Context-AI embeddings.

Defines the interface that all embedding model providers must implement,
enabling support for different embedding services (SentenceTransformers, OpenAI, etc.).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class ModelInfo:
    """Information about an embedding model."""
    
    def __init__(
        self,
        name: str,
        dimensions: int,
        max_seq_length: int,
        size_mb: float,
        description: str = "",
        provider: str = "",
    ):
        self.name = name
        self.dimensions = dimensions
        self.max_seq_length = max_seq_length
        self.size_mb = size_mb
        self.description = description
        self.provider = provider

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "dimensions": self.dimensions,
            "max_seq_length": self.max_seq_length,
            "size_mb": self.size_mb,
            "description": self.description,
            "provider": self.provider,
        }

class EmbeddingModelProtocol(ABC):
    """Protocol for embedding model providers."""
    
    @abstractmethod
    def get_available_models(self) -> Dict[str, ModelInfo]:
        """Get dictionary of available models."""
        
    @abstractmethod
    def load_model(self, model_name: str, show_progress: bool = True) -> Any:
        """Load an embedding model."""
        
    @abstractmethod
    def generate_embeddings(
        self, 
        texts: List[str], 
        model_name: str = None,
        batch_size: int = None,
        show_progress: bool = True
    ) -> List[List[float]]:
        """Generate embeddings for texts."""
        
    @abstractmethod
    def is_model_cached(self, model_name: str) -> bool:
        """Check if model is cached locally."""
        
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of this provider."""

__all__ = [
    'ModelInfo',
    'EmbeddingModelProtocol',
]
```

#### **📦 2.1.2 Criar vector_protocol.py**

- [ ] Criar arquivo `src/core/embeddings/vector_protocol.py`
- [ ] Implementar interface para vector stores

```python
"""
Vector store protocol for Context-AI.

Defines the interface that all vector database implementations must follow,
enabling support for different vector stores (ChromaDB, Pinecone, Weaviate, etc.).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class VectorStoreProtocol(ABC):
    """Protocol for vector database implementations."""
    
    @abstractmethod
    def store_embeddings(
        self,
        embedding_name: str,
        documents: List[str],
        embeddings: List[List[float]], 
        metadatas: List[Dict[str, Any]],
    ) -> bool:
        """Store documents and their embeddings with metadata."""
        
    @abstractmethod
    def query_embeddings(
        self,
        query_texts: List[str],
        embedding_names: Optional[List[str]] = None,
        n_results: int = 10,
    ) -> Dict[str, Any]:
        """Query embeddings with optional filtering."""
        
    @abstractmethod
    def get_embedding_info(self, embedding_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a stored embedding."""
        
    @abstractmethod
    def list_embeddings(self) -> List[Dict[str, Any]]:
        """List all available embeddings."""
        
    @abstractmethod
    def delete_embedding(self, embedding_name: str) -> bool:
        """Delete all documents for a specific embedding."""
        
    @abstractmethod
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get overall collection statistics."""
        
    @abstractmethod
    def reset_collection(self) -> bool:
        """Reset the entire collection (delete all data)."""
        
    @abstractmethod
    def get_store_name(self) -> str:
        """Get the name of this vector store."""

__all__ = [
    'VectorStoreProtocol',
]
```

---

### **🔧 FASE 3.2: REFATORAR MODEL_MANAGER**

#### **📦 3.2.1 Adicionar Constants no Arquivo**

- [ ] Abrir `core/embeddings/model_manager.py`
- [ ] Substituir `AVAILABLE_MODELS` por versão extensível no início do arquivo:

```python
# Model specifications - extensible for multiple providers  
AVAILABLE_MODELS = {
    # SentenceTransformers models
    "all-MiniLM-L6-v2": {
        "name": "all-MiniLM-L6-v2",
        "provider": "sentence_transformers",
        "dimensions": 384,
        "max_seq_length": 256,
        "size_mb": 90.0,
        "description": "Fast and efficient model, good for most use cases",
    },
    "all-mpnet-base-v2": {
        "name": "all-mpnet-base-v2",
        "provider": "sentence_transformers",
        "dimensions": 768,
        "max_seq_length": 384,
        "size_mb": 420.0,
        "description": "Higher quality embeddings, slower processing",
    },
    "all-MiniLM-L12-v2": {
        "name": "all-MiniLM-L12-v2", 
        "provider": "sentence_transformers",
        "dimensions": 384,
        "max_seq_length": 256,
        "size_mb": 130.0,
        "description": "Balance between speed and quality",
    },
    
    # OpenAI models (prepared for future implementation)
    "text-embedding-ada-002": {
        "name": "text-embedding-ada-002",
        "provider": "openai",
        "dimensions": 1536,
        "max_seq_length": 8191,
        "size_mb": 0,  # API-based
        "description": "OpenAI's embedding model",
    },
}

# Default configurations
DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_PROVIDER = "sentence_transformers"
DEFAULT_BATCH_SIZE = 32
LARGE_BATCH_THRESHOLD = 100
```

#### **📦 3.2.2 Implementar Factory Pattern**

- [ ] Adicionar import do protocol: `from .model_protocol import EmbeddingModelProtocol, ModelInfo`
- [ ] Modificar `EmbeddingModelManager` para usar provider pattern:

```python
class EmbeddingModelManager:
    """
    Manages embedding models with extensible provider support.
    """
    
    def __init__(self, provider_name: str = DEFAULT_PROVIDER):
        """Initialize with specified provider."""
        self.logger = get_logger(__name__)
        self.storage_manager = get_storage_manager()
        self.provider_name = provider_name
        self.provider = self._create_provider(provider_name)
        self._model_cache_dir = self.storage_manager.path_manager.models_dir
        self._model_cache_dir.mkdir(parents=True, exist_ok=True)

    def _create_provider(self, provider_name: str) -> EmbeddingModelProtocol:
        """Factory method to create provider instances."""
        if provider_name == "sentence_transformers":
            from .sentence_transformers_adapter import SentenceTransformersProvider
            return SentenceTransformersProvider()
        elif provider_name == "openai":
            # Future implementation
            raise NotImplementedError("OpenAI provider not yet implemented")
        else:
            raise ValueError(f"Unknown provider: {provider_name}")
    
    def get_available_models(self) -> Dict[str, ModelInfo]:
        """Get available models for current provider."""
        return self.provider.get_available_models()
    
    # Delegate other methods to provider...
```

#### **📦 3.2.3 Criar SentenceTransformers Adapter**

- [ ] Criar arquivo `src/core/embeddings/sentence_transformers_adapter.py`
- [ ] Mover lógica atual do model_manager para o adapter:

```python
"""
SentenceTransformers adapter for Context-AI embeddings.

Implements the EmbeddingModelProtocol using sentence-transformers library
for local embedding generation.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch
from sentence_transformers import SentenceTransformer

from .model_protocol import EmbeddingModelProtocol, ModelInfo
from utils.exceptions import ConfigurationError
from utils.logging import get_logger
from utils.storage import get_storage_manager

# Import model configurations from model_manager
from .model_manager import AVAILABLE_MODELS, DEFAULT_BATCH_SIZE, LARGE_BATCH_THRESHOLD

class SentenceTransformersProvider(EmbeddingModelProtocol):
    """SentenceTransformers implementation of embedding model provider."""
    
    def __init__(self):
        """Initialize SentenceTransformers provider."""
        self.logger = get_logger(__name__)
        self.storage_manager = get_storage_manager()
        self._loaded_models: Dict[str, SentenceTransformer] = {}
        self._model_cache_dir = self.storage_manager.path_manager.models_dir
        self._model_cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_available_models(self) -> Dict[str, ModelInfo]:
        """Get available SentenceTransformers models."""
        models = {}
        for name, spec in AVAILABLE_MODELS.items():
            if spec.get("provider") == "sentence_transformers":
                models[name] = ModelInfo(**spec)
        return models
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return "sentence_transformers"
    
    # ... implement other methods by moving from model_manager.py
```

#### **📦 3.2.4 Refatorar VectorStore para usar Protocol**

- [ ] Abrir `core/embeddings/vector_store.py`
- [ ] Adicionar import: `from .vector_protocol import VectorStoreProtocol`
- [ ] Modificar `VectorStoreManager` para implementar protocol:

```python
class VectorStoreManager(VectorStoreProtocol):
    """ChromaDB implementation of vector store protocol."""
    
    def get_store_name(self) -> str:
        """Get the name of this vector store."""
        return "chromadb"
    
    # ... existing methods already implement the protocol
```

---

### **🧪 FASE 3.3: TESTES DA FASE 3**

#### **🔍 3.3.1 Testes de Protocol Implementation**

- [ ] Testar que `EmbeddingModelManager` funciona com factory pattern
- [ ] Testar que `SentenceTransformersProvider` implementa protocol corretamente
- [ ] Testar que `VectorStoreManager` implementa protocol corretamente
- [ ] Verificar que backward compatibility é mantida

#### **🔍 3.3.2 Testes de Extensibilidade**

- [ ] Verificar que é fácil adicionar novo provider (criar mock OpenAI provider)
- [ ] Verificar que é fácil adicionar novo vector store (criar mock Pinecone store)
- [ ] Testar switching entre providers

---

## 🔍 FASE 4: QUERY MODULE CONSOLIDATION

### **🚀 FASE 4.1: MOVER CONTEXT FORMATTER**

#### **📦 4.1.1 Mover Arquivo**

- [ ] Mover `core/formatting/context_formatter.py` → `core/query/formatter.py`
- [ ] Verificar que o arquivo foi movido corretamente

#### **📦 4.1.2 Atualizar Imports no Formatter**

- [ ] Abrir `core/query/formatter.py`
- [ ] Verificar import de `count_tokens` já foi atualizado para TokenManager (fase 1)
- [ ] Adicionar import para QueryResult: `from .result_merger import QueryResult`
- [ ] Verificar que não há imports órfãos

#### **📦 4.1.3 Remover Diretório Vazio**

- [ ] Verificar se `core/formatting/` está vazio
- [ ] Se sim, remover diretório `core/formatting/`
- [ ] Verificar que não há outros arquivos importantes

---

### **🔧 FASE 4.2: CRIAR MODELS.PY CENTRALIZADO**

#### **📦 4.2.1 Criar models.py**

- [ ] Criar arquivo `src/core/query/models.py`
- [ ] Mover `ProcessedQuery` de `preprocessor.py` para `models.py`
- [ ] Mover `QueryResult` de `result_merger.py` para `models.py`
- [ ] Mover `FormattedContext` de `formatter.py` para `models.py`

#### **📝 4.2.2 Estrutura do models.py**

```python
"""
Data models for query processing in Context-AI.

Contains data classes used across the query processing pipeline:
preprocessing, result merging, and context formatting.
"""

from dataclasses import dataclass
from typing import Any, Dict, List

@dataclass
class ProcessedQuery:
    """Processed query with metadata."""

    original: str
    normalized: str
    cleaned: str
    expanded_terms: List[str]
    is_valid: bool
    issues: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/debugging."""
        return {
            "original": self.original,
            "normalized": self.normalized,
            "cleaned": self.cleaned,
            "expanded_terms": self.expanded_terms,
            "is_valid": self.is_valid,
            "issues": self.issues,
        }

@dataclass
class QueryResult:
    """Normalized query result with unified scoring."""

    text: str
    metadata: Dict[str, Any]
    original_distance: float
    normalized_score: float
    final_score: float
    source_embedding: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "text": self.text,
            "metadata": self.metadata,
            "original_distance": self.original_distance,
            "normalized_score": self.normalized_score,
            "final_score": self.final_score,
            "source_embedding": self.source_embedding,
        }

@dataclass
class FormattedContext:
    """Formatted context ready for AI consumption."""

    content: str
    token_count: int
    chunk_count: int
    source_count: int
    truncated: bool
    sources: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/debugging."""
        return {
            "token_count": self.token_count,
            "chunk_count": self.chunk_count,
            "source_count": self.source_count,
            "truncated": self.truncated,
            "sources": self.sources,
            "content_length": len(self.content),
        }

__all__ = [
    'ProcessedQuery',
    'QueryResult', 
    'FormattedContext',
]
```

#### **📦 4.2.3 Atualizar Arquivos Existentes**

- [ ] Abrir `core/query/preprocessor.py`
- [ ] Remover `ProcessedQuery` dataclass
- [ ] Adicionar import: `from .models import ProcessedQuery`

- [ ] Abrir `core/query/result_merger.py`  
- [ ] Remover `QueryResult` dataclass
- [ ] Adicionar import: `from .models import QueryResult`

- [ ] Abrir `core/query/formatter.py`
- [ ] Remover `FormattedContext` dataclass
- [ ] Adicionar import: `from .models import FormattedContext, QueryResult`

#### **📦 4.2.4 Atualizar __init__.py**

- [ ] Abrir `core/query/__init__.py`
- [ ] Adicionar exports:
```python
from .models import ProcessedQuery, QueryResult, FormattedContext
from .preprocessor import QueryPreprocessor, get_query_preprocessor, preprocess_query
from .result_merger import MultiEmbeddingResultMerger, get_result_merger
from .formatter import ContextFormatter, get_context_formatter, format_results_for_ai

__all__ = [
    'ProcessedQuery',
    'QueryResult', 
    'FormattedContext',
    'QueryPreprocessor',
    'get_query_preprocessor',
    'preprocess_query',
    'MultiEmbeddingResultMerger',
    'get_result_merger',
    'ContextFormatter',
    'get_context_formatter', 
    'format_results_for_ai',
]
```

---

### **🔄 FASE 4.3: ATUALIZAR IMPORTS EXTERNOS**

#### **📦 4.3.1 Atualizar Services**

- [ ] Abrir `services/embedding_service.py` (QueryService)
- [ ] Substituir: `from core.formatting.context_formatter import get_context_formatter` 
- [ ] Por: `from core.query.formatter import get_context_formatter`

- [ ] Abrir `services/ai_service.py`
- [ ] Verificar se usa context_formatter (já foi atualizado na fase 1 para TokenManager)
- [ ] Se necessário, atualizar import para: `from core.query.formatter import count_tokens`

#### **📦 4.3.2 Verificar Outros Imports**

- [ ] Buscar por imports de `core.formatting` em todo o projeto
- [ ] Buscar por imports de `context_formatter` em todo o projeto
- [ ] Atualizar todos os imports encontrados

---

### **🧪 FASE 4.4: TESTES DA FASE 4**

#### **🔍 4.4.1 Testes de Import**

- [ ] Testar imports consolidados:
  - [ ] `from core.query import ProcessedQuery, QueryResult, FormattedContext`
  - [ ] `from core.query.formatter import get_context_formatter`
  - [ ] `from core.query.models import QueryResult`
- [ ] Verificar que não há circular imports

#### **🔍 4.4.2 Testes de Funcionalidade**

- [ ] Testar query preprocessing (deve funcionar normalmente)
- [ ] Testar result merging (deve funcionar normalmente)
- [ ] Testar context formatting (deve funcionar normalmente)
- [ ] Testar pipeline completo: preprocess → query → merge → format

---

## ✅ FASE 5: VALIDAÇÃO FINAL

### **🧪 FASE 5.1: TESTES END-TO-END**

#### **🔄 5.1.1 Testes de Comandos CLI**

- [ ] Testar comando `ask` completo:
  - [ ] Token counting funciona (TokenManager)
  - [ ] Query preprocessing funciona
  - [ ] Context formatting funciona
  - [ ] AIService usa TokenCalculator migrado

- [ ] Testar comando `generate`:
  - [ ] Chunking funciona com language detection melhorada
  - [ ] Embedding generation funciona com provider pattern
  - [ ] Vector storage funciona com protocol

- [ ] Testar comando `query`:
  - [ ] Query preprocessing funciona
  - [ ] Vector query funciona
  - [ ] Result merging funciona
  - [ ] Context formatting funciona

- [ ] Testar comando `select`:
  - [ ] Lista embeddings funciona
  - [ ] Embedding info funciona

#### **🔄 5.1.2 Testes de Integração**

- [ ] Testar fluxo completo: generate → select → query → ask
- [ ] Verificar que não há memory leaks
- [ ] Verificar que performance não regrediu
- [ ] Testar error handling e fallbacks

---

### **📋 FASE 5.2: VALIDAÇÃO DE ARQUITETURA**

#### **✅ 5.2.1 Checklist de Qualidade**

**Token Management:**
- [ ] TokenManager centralizado em core/ai/
- [ ] Provider-aware counting (Anthropic + Tiktoken)  
- [ ] Todas as duplicações eliminadas
- [ ] Backward compatibility mantida
- [ ] Cache funcionando corretamente

**Chunking:**
- [ ] Protocol + models separados
- [ ] Language detection melhorada (extends + additional_separators)
- [ ] Token counting usa TokenManager
- [ ] Backward compatibility mantida

**Embeddings:**
- [ ] Model provider protocol implementado
- [ ] Vector store protocol implementado
- [ ] Factory pattern funcionando
- [ ] Extensível para novos providers
- [ ] Constants organizadas

**Query:**
- [ ] Context formatter movido para query module
- [ ] Data classes centralizadas em models.py
- [ ] Pipeline completo em um módulo
- [ ] Imports limpos e organizados

#### **🏗️ 5.2.2 Arquitetura Final**

Verificar que a estrutura final está como planejado:

```
core/
├── ai/
│   ├── token_manager.py        # 🆕 Centralized token management
│   ├── claude_client.py        # ✅ Uses TokenManager
│   └── prompt_builder.py       # ✅ Uses TokenManager
├── chunking/
│   ├── __init__.py             # ✅ Updated exports
│   ├── protocol.py             # ✅ Only ChunkerProtocol
│   ├── models.py               # 🆕 TextChunk, ChunkingStrategy, ChunkingMetadata
│   └── langchain_adapter.py    # 🔧 Enhanced language detection + TokenManager
├── embeddings/
│   ├── __init__.py             # ✅ Updated exports
│   ├── model_protocol.py       # 🆕 EmbeddingModelProtocol
│   ├── vector_protocol.py      # 🆕 VectorStoreProtocol
│   ├── model_manager.py        # 🔧 Uses factory pattern + constants
│   ├── vector_store.py         # 🔧 Implements VectorStoreProtocol
│   └── sentence_transformers_adapter.py  # 🆕 Extracted implementation
├── query/
│   ├── __init__.py             # 🔧 Updated exports
│   ├── models.py               # 🆕 ProcessedQuery, QueryResult, FormattedContext
│   ├── preprocessor.py         # ✅ Uses models.py
│   ├── result_merger.py        # ✅ Uses models.py
│   └── formatter.py            # 🔄 Moved from core/formatting/ + uses models.py
└── formatting/                 # 🗑️ REMOVED (empty)
```

#### **🎯 5.2.3 Princípios Aplicados**

**Consistency:**
- [ ] **Protocol + Models pattern** aplicado em todos os módulos
- [ ] **Factory pattern** para extensibilidade
- [ ] **Global singleton functions** para convenience
- [ ] **Naming conventions** consistentes

**SOLID Principles:**
- [ ] **Single Responsibility**: Cada módulo focado
- [ ] **Open/Closed**: Extensível via protocols
- [ ] **Liskov Substitution**: Protocols permitem substituição
- [ ] **Interface Segregation**: Interfaces específicas
- [ ] **Dependency Inversion**: Dependências abstratas

---

## 🐛 ISSUES ENCONTRADAS

### **Durante Token Management:**
```
[ Documentar problemas relacionados a token counting aqui ]

Exemplo:
- Issue: Import path conflicts
- Description: Multiple files importing old count_tokens
- Solution: Systematic replacement with TokenManager
- Status: ✅ Resolvido
```

### **Durante Chunking Refactor:**
```
[ Documentar problemas relacionados a chunking aqui ]

Exemplo:  
- Issue: Language detection não reconhece extends
- Description: TypeScript não detectado corretamente
- Solution: Implementar herança de separators
- Status: ✅ Resolvido
```

### **Durante Embeddings Extensibility:**
```
[ Documentar problemas relacionados a embeddings aqui ]

Exemplo:
- Issue: Factory pattern complex
- Description: Provider creation com muitas dependencies
- Solution: Simplificar interface e usar dependency injection
- Status: ⏳ Em progresso
```

### **Durante Query Consolidation:**
```
[ Documentar problemas relacionados a query aqui ]

Exemplo:
- Issue: Circular imports entre models
- Description: QueryResult usado em múltiplos arquivos
- Solution: Centralizar em models.py e ajustar imports
- Status: ✅ Resolvido
```

---

## 📋 CHECKLIST FINAL

### **FASE 1 - Token Management:**
- [ ] **1.1:** TokenManager criado e funcional
- [ ] **1.2:** TokenCalculator migrado de ai_service.py
- [ ] **1.3:** Todas as duplicações eliminadas

### **FASE 2 - Chunking Refactor:**
- [ ] **2.1:** Protocol e models separados
- [ ] **2.2:** Language detection melhorada
- [ ] **2.3:** Testes passando

### **FASE 3 - Embeddings Extensibility:**
- [ ] **3.1:** Protocols criados (model + vector)
- [ ] **3.2:** Model manager refatorado
- [ ] **3.3:** Testes de extensibilidade passando

### **FASE 4 - Query Consolidation:**
- [ ] **4.1:** Context formatter movido
- [ ] **4.2:** Models.py centralizado
- [ ] **4.3:** Imports externos atualizados
- [ ] **4.4:** Testes de funcionalidade passando

### **FASE 5 - Validação Final:**
- [ ] **5.1:** Testes end-to-end passando
- [ ] **5.2:** Arquitetura validada

### **🎯 ENTREGÁVEIS FINAIS:**
```
✅ TokenManager centralizado com provider-aware counting
✅ Chunking com protocol + models + language detection robusto
✅ Embeddings extensível para múltiplos providers/vector stores
✅ Query pipeline completo consolidado em um módulo
✅ Zero duplicação de código em todo o projeto
✅ Backward compatibility 100% mantida
✅ Performance mantida ou melhorada
✅ Arquitetura consistente com protocols em todos módulos
✅ Facilidade de extensão para novos providers
✅ Testes completos passando
```

---

## 🚀 PRÓXIMOS PASSOS

Após conclusão deste plano:

1. **Implementar novos providers** (OpenAI embeddings, outros vector stores)
2. **Adicionar métricas** avançadas de performance
3. **Criar testes unitários** específicos para cada protocol
4. **Documentar** APIs dos novos protocols
5. **Otimizações** baseadas na nova arquitetura

**🎯 Ready for implementation! Esta refatoração estabelecerá uma base sólida e extensível para o Context-AI.**
