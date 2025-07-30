# 🎯 PLANO: SERVICES + TOKEN MANAGEMENT REFACTOR

## 📋 COMO USAR ESTE PLANO

Este arquivo é nosso **guia de desenvolvimento** para duas refatorações importantes do Context-AI.

### **📖 INSTRUÇÕES DE USO:**

1. **Siga a ordem sequencial** - cada fase depende da anterior
2. **Marque os checkboxes** ✅ conforme completar cada item
3. **Teste após cada fase** - valide antes de prosseguir
4. **Documente problemas** na seção "🐛 ISSUES ENCONTRADAS" no final
5. **Não pule etapas** - cada passo tem dependências específicas

### **🔄 FLUXO DE TRABALHO:**
```
PARTE A: Token Management → PARTE B: Services Refactor → PARTE C: Validação Integrada
```

### **🎯 DUPLO OBJETIVO:**
- ✅ **Token Management Centralized** em `core/ai/token_manager.py`
- ✅ **QueryService** em arquivo próprio `src/services/query_service.py`
- ✅ **EmbeddingService** limpo (só embedding operations)
- ✅ **AIService duplicado** removido
- ✅ **Provider-aware token counting** (Anthropic + Tiktoken)
- ✅ **Zero breaking changes** nas APIs existentes

---

## 📊 **SITUAÇÃO ATUAL IDENTIFICADA:**

### **🧮 TOKEN COUNTING - PROBLEMÁTICO**
- **61 ocorrências** de token counting espalhadas em 8 arquivos
- **4 implementações diferentes:**
  1. **TokenCalculator** (ai_service.py) ⭐ - bem estruturado, mal localizado
  2. **count_tokens** (context_formatter.py) ✅ - tiktoken robusto  
  3. **count_tokens simples** (prompt_builder.py) ❌ - duplicação
  4. **_estimate_token_count** (langchain_adapter.py) ❌ - duplicação

### **🔧 SERVICES - PROBLEMÁTICO**
- **ai_service.py** ✅ (correto, mas TokenCalculator deve sair)
- **embedding_service.py** ❌ (3 services misturados):
  1. **EmbeddingService** ✅ (correto aqui) - generate_embedding(), select_embeddings()
  2. **QueryService** 🔄 (extrair) - query_context(), query_context_json()
  3. **AIService** ❌ (duplicado inútil) - só placeholders "não implementado"

---

## 🧮 PARTE A: TOKEN MANAGEMENT CENTRALIZATION

### **🚀 FASE A1: ANÁLISE DE TOKEN COUNTING**

#### **📋 A1.1 Mapear Todas as Implementações**

**Implementações já identificadas:**
- [ ] `TokenCalculator` (services/ai_service.py) - cálculos avançados
- [ ] `count_tokens` (core/formatting/context_formatter.py) - tiktoken + cache
- [ ] `count_tokens` simples (core/ai/prompt_builder.py) - aproximação básica
- [ ] `_estimate_token_count` (core/chunking/langchain_adapter.py) - estimativa

#### **📋 A1.2 Mapear Todos os Usos**

**Arquivos com usos identificados (61 ocorrências):**
- [ ] services/ai_service.py (16 usos) - principalmente TokenCalculator
- [ ] core/formatting/context_formatter.py (25 usos) - função principal
- [ ] utils/session_logger.py (múltiplos) - logging de tokens
- [ ] core/ai/claude_client.py (streaming) - decisões de streaming
- [ ] core/chunking/langchain_adapter.py (metadata) - chunk tokens
- [ ] core/ai/prompt_builder.py (logging) - prompt tokens
- [ ] config/models/storage.py (field) - modelo de dados
- [ ] services/embedding_service.py (stats) - estatísticas

#### **📋 A1.3 Documentar APIs Necessárias**

**APIs que devem ser mantidas:**
- [ ] **count_tokens(text: str) -> int** - contagem básica  
- [ ] **calculate_context_allocation()** - alocação de contexto
- [ ] **calculate_response_tokens()** - tokens de resposta
- [ ] **Provider-aware counting** - Claude vs OpenAI

---

### **🏗️ FASE A2: CRIAR TOKEN_MANAGER.PY**

#### **📦 A2.1 Estrutura Base do TokenManager**

- [ ] Criar arquivo `src/core/ai/token_manager.py`
- [ ] Implementar classes base e provider detection
- [ ] Adicionar documentação e `__all__` exports

#### **📝 A2.2 Implementação Provider-Aware**

```python
"""
Token Management for Context-AI.

Centralized token counting with provider-specific implementations.
Supports Anthropic (Claude) and OpenAI (GPT) token counting.
"""

from typing import Dict, Optional, Protocol
from enum import Enum
from functools import lru_cache

class TokenProvider(Enum):
    """Supported token counting providers."""
    CLAUDE = "claude"
    OPENAI = "openai"
    AUTO = "auto"  # Detect from active provider

class AnthropicTokenCounter:
    """Anthropic-specific token counter using their official library."""
    
    def count_tokens(self, text: str) -> int:
        """Count tokens using Anthropic's tokenizer."""
        try:
            import anthropic
            # Use Anthropic's official token counter
            return len(anthropic.get_tokenizer().encode(text))
        except ImportError:
            # Fallback to estimation if anthropic library not available
            return max(1, len(text.strip()) // 4)

class OpenAITokenCounter:
    """OpenAI-specific token counter using tiktoken."""
    
    def __init__(self):
        self._encoder = None
        self._load_encoder()
    
    def _load_encoder(self):
        """Load tiktoken encoder with error handling."""
        try:
            import tiktoken
            self._encoder = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
        except ImportError:
            self._encoder = None
    
    def count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken."""
        if self._encoder:
            return len(self._encoder.encode(text))
        else:
            return max(1, len(text.strip()) // 4)  # Fallback

class TokenManager:
    """Centralized token management with provider-specific counting."""
    
    def __init__(self):
        self._counters = {
            TokenProvider.CLAUDE: AnthropicTokenCounter(),
            TokenProvider.OPENAI: OpenAITokenCounter(),
        }
        self._cache = {}
        self._active_provider = TokenProvider.CLAUDE  # Default to Claude
    
    @lru_cache(maxsize=1000)
    def count_tokens(self, text: str, provider: Optional[TokenProvider] = None) -> int:
        """Count tokens in text using specified or active provider."""
        if not text or not text.strip():
            return 0
        
        provider = provider or self._active_provider
        counter = self._counters[provider]
        return counter.count_tokens(text)
    
    def calculate_context_allocation(self, question: str, include_history: bool = False) -> Dict[str, int]:
        """Calculate token allocation for context and history."""
        # Migrated from TokenCalculator in ai_service.py
        pass
    
    def calculate_response_tokens(self, input_tokens: int, context_tokens: int) -> int:
        """Calculate maximum response tokens."""
        # Migrated from TokenCalculator in ai_service.py
        pass

# Global instance
_token_manager: Optional[TokenManager] = None

def get_token_manager() -> TokenManager:
    """Get global token manager instance."""
    global _token_manager
    if _token_manager is None:
        _token_manager = TokenManager()
    return _token_manager

def count_tokens(text: str, provider: Optional[str] = None) -> int:
    """Convenience function for token counting."""
    return get_token_manager().count_tokens(text)
```

#### **🧪 A2.3 Validar TokenManager**

- [ ] Testar Anthropic token counting
- [ ] Testar Tiktoken fallback  
- [ ] Testar provider switching
- [ ] Testar cache functionality
- [ ] Testar backward compatibility functions

---

### **🔄 FASE A3: MIGRAR TOKENCALCULATOR**

#### **📦 A3.1 Mover TokenCalculator**

- [ ] Remover `TokenCalculator` de `services/ai_service.py`
- [ ] Verificar que métodos foram integrados ao `TokenManager`
- [ ] Atualizar imports no ai_service.py:
  - [ ] `from core.ai.token_manager import get_token_manager`

#### **🔧 A3.2 Atualizar Uso no AIService**

- [ ] Substituir `TokenCalculator.calculate_context_allocation()` → `token_manager.calculate_context_allocation()`
- [ ] Substituir `TokenCalculator.calculate_response_tokens()` → `token_manager.calculate_response_tokens()`
- [ ] Testar que AIService funciona normalmente

---

### **🧹 FASE A4: SUBSTITUIR IMPLEMENTAÇÕES DUPLICADAS**

#### **📦 A4.1 Substituir em context_formatter.py**

- [ ] Remover função `count_tokens()` de `core/formatting/context_formatter.py`
- [ ] Substituir por import: `from core.ai.token_manager import count_tokens`
- [ ] Testar formatação de contexto

#### **📦 A4.2 Substituir em prompt_builder.py**

- [ ] Remover função `count_tokens()` simples de `core/ai/prompt_builder.py`
- [ ] Substituir por import: `from core.ai.token_manager import count_tokens`  
- [ ] Testar prompt building

#### **📦 A4.3 Substituir em langchain_adapter.py**

- [ ] Remover `_estimate_token_count()` de `core/chunking/langchain_adapter.py`
- [ ] Substituir por: `get_token_manager().count_tokens()`
- [ ] Testar chunking operations

#### **📦 A4.4 Atualizar Outros Usos**

- [ ] Atualizar imports em `utils/session_logger.py`
- [ ] Atualizar imports em `core/ai/claude_client.py`
- [ ] Verificar outros arquivos com token counting

---

## 🔧 PARTE B: SERVICES REFACTOR

### **🚀 FASE B1: ANÁLISE DE SERVICES**

#### **📋 B1.1 Buscar Usos do QueryService**

**Buscar por:**
- [ ] `from services.embedding_service import QueryService`
- [ ] `QueryService()`
- [ ] `.query_context(`
- [ ] `.query_context_json(`

**📋 Lista real de arquivos encontrados:**
```
[ Documentar aqui os arquivos reais encontrados durante a busca ]

Exemplo:
✅ src/services/ai_service.py - line 15: from services.embedding_service import QueryService
✅ src/commands/query.py - line 25: QueryService().query_context()
[ ... adicionar conforme encontrado ... ]
```

#### **📋 B1.2 Buscar Usos do AIService Duplicado**

**Buscar por:**
- [ ] `from services.embedding_service import AIService`
- [ ] Qualquer uso do AIService do embedding_service

**📋 Lista esperada:**
```
Se nenhum uso encontrado:
✅ PERFEITO: AIService duplicado não é usado - pode ser removido com segurança!
```

---

### **🆕 FASE B2: CRIAR QUERY_SERVICE.PY**

#### **📦 B2.1 Extrair QueryService Completo**

- [ ] Criar arquivo `src/services/query_service.py`
- [ ] Copiar classe QueryService completa de embedding_service.py
- [ ] Copiar todos os imports necessários para QueryService
- [ ] Atualizar imports de token counting para usar TokenManager:
  - [ ] `from core.ai.token_manager import count_tokens`
- [ ] Adicionar docstring do arquivo e `__all__` exports

#### **📝 B2.2 Estrutura do Novo Arquivo**

```python
"""
Query service for Context-AI.

Handles query operations including context retrieval,
search preprocessing, and result formatting.
"""

from typing import Any, Dict, List, Optional
import json

from config.constants import QUERY_POOL_SIZE, CONTEXT_DEFAULT_CHUNKS, CONTEXT_PERFORMANCE_LIMIT
from config.settings import get_settings_manager
from core.embeddings.vector_store import get_vector_store
from core.formatting.context_formatter import get_context_formatter
from core.query.preprocessor import get_query_preprocessor
from core.query.result_merger import get_result_merger
from core.ai.token_manager import count_tokens  # ✅ Using centralized token manager
from utils.exceptions import ValidationError
from utils.logging import get_logger

__all__ = [
    'QueryService',
]

class QueryService:
    # ... código completo do QueryService com token counting atualizado
```

#### **🧪 B2.3 Validar QueryService Extraído**

- [ ] Verificar que todos os imports estão corretos
- [ ] Verificar que usa TokenManager para contagem
- [ ] Testar import: `from services.query_service import QueryService`
- [ ] Testar funcionalidades básicas

---

### **🧹 FASE B3: LIMPAR EMBEDDING_SERVICE.PY**

#### **📦 B3.1 Remover QueryService**

- [ ] Remover classe QueryService completa
- [ ] Remover imports específicos do QueryService não usados por EmbeddingService
- [ ] Manter imports necessários para EmbeddingService

#### **📦 B3.2 Remover AIService Duplicado**

- [ ] Remover classe AIService completa do embedding_service.py
- [ ] Remover imports específicos do AIService duplicado
- [ ] Verificar que não há referências órfãs

#### **📝 B3.3 Atualizar Estrutura Limpa**

```python
"""
Embedding management service for Context-AI.

Handles business logic for embedding operations including
generation, selection, and management.
"""

from typing import Any, Dict, List, Optional
from pathlib import Path

# Só imports necessários para EmbeddingService
from config.constants import QUERY_POOL_SIZE, CONTEXT_DEFAULT_CHUNKS, CONTEXT_PERFORMANCE_LIMIT
from config.settings import get_settings_manager
from core.chunking import get_chunker
from core.embeddings.model_manager import get_model_manager
from core.embeddings.vector_store import get_vector_store
from utils.error_handler import validate_embedding_name, validate_file_path
from utils.exceptions import ValidationError
from utils.logging import get_logger

__all__ = [
    'EmbeddingService',
]

class EmbeddingService:
    # ... código completo do EmbeddingService (inalterado)
```

#### **🧪 B3.4 Validar EmbeddingService Limpo**

- [ ] Verificar que EmbeddingService funciona normalmente
- [ ] Verificar que não há imports órfãos
- [ ] Testar import: `from services.embedding_service import EmbeddingService`

---

### **🔄 FASE B4: ATUALIZAR IMPORTS DE SERVICES**

#### **🔄 B4.1 Atualizar Imports de QueryService**

- [ ] Atualizar todos os arquivos listados em B1.1
- [ ] Para cada arquivo, substituir:
  - [ ] `from services.embedding_service import QueryService` → `from services.query_service import QueryService`

#### **🔄 B4.2 Atualizar services/__init__.py**

- [ ] Adicionar export do QueryService:
```python
from .query_service import QueryService
from .embedding_service import EmbeddingService
from .ai_service import AIService

__all__ = [
    'QueryService',
    'EmbeddingService', 
    'AIService',
]
```

#### **🔄 B4.3 Verificar AIService Principal**

- [ ] Verificar que ai_service.py não foi afetado pela migração de TokenCalculator
- [ ] Verificar que import de QueryService funciona
- [ ] Verificar que novo TokenManager funciona no AIService

---

## ✅ PARTE C: VALIDAÇÃO INTEGRADA

### **🧪 FASE C1: TESTES END-TO-END**

#### **🔄 C1.1 Testes de Fluxo Completo**

- [ ] Testar fluxo: generate → select → query → ask
- [ ] Verificar que token counting funciona em todo fluxo
- [ ] Testar provider switching com diferentes comandos
- [ ] Validar que cache de tokens funciona

#### **📊 C1.2 Testes de Performance**

- [ ] Comparar performance de token counting antes/depois
- [ ] Verificar eficiência do cache do TokenManager
- [ ] Testar com contextos grandes (>100K tokens)
- [ ] Benchmark de Anthropic vs Tiktoken counting

#### **🔍 C1.3 Testes de Regressão**

- [ ] Verificar que todas as APIs públicas funcionam
- [ ] Testar comandos CLI: ask, chat, query, generate, select
- [ ] Verificar que session logging funciona
- [ ] Testar integração VSCode mode

---

### **📋 FASE C2: VALIDAÇÃO DE ARQUITETURA**

#### **✅ C2.1 Checklist de Qualidade**

**Token Management:**
- [ ] TokenManager centralizado em core/ai/
- [ ] Provider-aware counting (Anthropic + Tiktoken)
- [ ] Cache eficiente implementado
- [ ] Todas as duplicações eliminadas
- [ ] Backward compatibility mantida

**Services Refactor:**
- [ ] QueryService extraído com sucesso
- [ ] EmbeddingService limpo e focado
- [ ] AIService duplicado removido
- [ ] Imports atualizados corretamente
- [ ] Zero breaking changes

#### **🏗️ C2.2 Arquitetura Final**

Verificar que a estrutura final está como planejado:

```
src/
├── core/ai/
│   ├── token_manager.py        # 🆕 Centralized token management
│   ├── claude_client.py        # ✅ Uses TokenManager
│   └── prompt_builder.py       # ✅ Uses TokenManager
├── services/
│   ├── __init__.py             # 🔄 Updated exports
│   ├── ai_service.py           # 🔄 Uses TokenManager
│   ├── embedding_service.py    # 🔄 Cleaned (EmbeddingService only)
│   └── query_service.py        # 🆕 Extracted QueryService
├── core/formatting/
│   └── context_formatter.py    # 🔄 Uses TokenManager
└── core/chunking/
    └── langchain_adapter.py     # 🔄 Uses TokenManager
```

#### **🎯 C2.3 Princípios Aplicados**

**Token Management:**
- [ ] **Single Responsibility**: TokenManager é responsável por todos os tokens
- [ ] **Provider Pattern**: Suporte extensível a diferentes provedores
- [ ] **Caching Strategy**: Performance otimizada com cache inteligente
- [ ] **Dependency Inversion**: Interfaces claras para token counting

**Services:**
- [ ] **Single Responsibility**: Cada service tem propósito claro
- [ ] **DRY**: Eliminada duplicação do AIService
- [ ] **Clean Architecture**: Services bem organizados
- [ ] **Maintainability**: Código mais fácil de manter

---

## 🐛 ISSUES ENCONTRADAS

### **Durante Token Management:**
```
[ Documentar problemas relacionados a token counting aqui ]

Exemplo:
- Issue: Anthropic library não disponível
- Solução: Implementar fallback estimation
- Status: ✅ Resolvido
```

### **Durante Services Refactor:**
```
[ Documentar problemas relacionados a services aqui ]

Exemplo:
- Issue: Import circular entre services
- Solução: Reorganizar imports
- Status: ✅ Resolvido
```

### **Durante Integração:**
```
[ Documentar problemas de integração aqui ]

Exemplo:
- Issue: Performance degradation
- Solução: Otimizar cache strategy
- Status: ⏳ Em progresso
```

---

## 📋 CHECKLIST FINAL

**PARTE A - Token Management:**
- [ ] **FASE A1:** Análise de token counting completa
- [ ] **FASE A2:** TokenManager criado e funcional
- [ ] **FASE A3:** TokenCalculator migrado
- [ ] **FASE A4:** Duplicações eliminadas

**PARTE B - Services Refactor:**
- [ ] **FASE B1:** Análise de services completa
- [ ] **FASE B2:** QueryService extraído
- [ ] **FASE B3:** EmbeddingService limpo
- [ ] **FASE B4:** Imports atualizados

**PARTE C - Validação Integrada:**
- [ ] **FASE C1:** Testes end-to-end passando
- [ ] **FASE C2:** Arquitetura validada

### **🎯 ENTREGÁVEL FINAL:**
```
✅ TokenManager centralizado com Anthropic + Tiktoken
✅ Provider-aware token counting
✅ Cache eficiente para performance
✅ Todas as duplicações de token counting eliminadas
✅ QueryService em arquivo próprio
✅ EmbeddingService limpo e focado
✅ AIService duplicado removido
✅ Zero breaking changes nas APIs
✅ Performance mantida ou melhorada
✅ Arquitetura limpa e extensível
```

---

## 🚀 PRÓXIMOS PASSOS

Após conclusão deste plano:

1. **Implementar novos providers** (OpenAI, outros)
2. **Adicionar métricas** de uso de tokens
3. **Otimizações avançadas** de cache
4. **Testes unitários** específicos para cada componente

**🎯 Ready to start implementation!**
