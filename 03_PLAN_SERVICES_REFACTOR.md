# 🎯 PLANO 03: SERVICES REFACTOR

## 📋 COMO USAR ESTE PLANO

Este arquivo é nosso **guia de desenvolvimento** para refatorar os services do Context-AI.

### **📖 INSTRUÇÕES DE USO:**

1. **Siga a ordem sequencial** - cada fase depende da anterior
2. **Marque os checkboxes** ✅ conforme completar cada item
3. **Teste após cada fase** - valide antes de prosseguir
4. **Documente problemas** na seção "🐛 ISSUES ENCONTRADAS" no final
5. **Não pule etapas** - cada passo tem dependências específicas

### **🔄 FLUXO DE TRABALHO:**
```
PARTE A: Services Refactor → PARTE B: Validação Integrada
```

### **🎯 OBJETIVO ÚNICO:**
- ✅ **QueryService** em arquivo próprio `src/services/query_service.py`
- ✅ **EmbeddingService** limpo (só embedding operations)
- ✅ **AIService duplicado** removido
- ✅ **Zero breaking changes** nas APIs existentes

### **📋 PRÉ-REQUISITO:**
⚠️ **Este plano assume que o 01_PLAN_TOKEN_MANAGER já foi executado com sucesso.**
- TokenManager centralizado já está disponível em `core/ai/token_manager.py`
- Todas as duplicações de token counting já foram eliminadas
- Provider-aware counting (Anthropic + Tiktoken) já funciona

---

## 📊 **SITUAÇÃO ATUAL IDENTIFICADA:**

### **🔧 SERVICES - PROBLEMÁTICO**
- **ai_service.py** ✅ (correto, já usa TokenManager)
- **embedding_service.py** ❌ (3 services misturados):
  1. **EmbeddingService** ✅ (correto aqui) - generate_embedding(), select_embeddings()
  2. **QueryService** 🔄 (extrair) - query_context(), query_context_json()
  3. **AIService** ❌ (duplicado inútil) - só placeholders "não implementado"

---

## 🔧 PARTE A: SERVICES REFACTOR

### **🚀 FASE A1: ANÁLISE DE SERVICES**

#### **📋 A1.1 Buscar Usos do QueryService**

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

#### **📋 A1.2 Buscar Usos do AIService Duplicado**

**Buscar por:**
- [ ] `from services.embedding_service import AIService`
- [ ] Qualquer uso do AIService do embedding_service

**📋 Lista esperada:**
```
Se nenhum uso encontrado:
✅ PERFEITO: AIService duplicado não é usado - pode ser removido com segurança!
```

---

### **🆕 FASE A2: CRIAR QUERY_SERVICE.PY**

#### **📦 A2.1 Extrair QueryService Completo**

- [ ] Criar arquivo `src/services/query_service.py`
- [ ] Copiar classe QueryService completa de embedding_service.py
- [ ] Copiar todos os imports necessários para QueryService
- [ ] Atualizar imports de token counting para usar TokenManager:
  - [ ] `from core.ai.token_manager import count_tokens`
- [ ] Adicionar docstring do arquivo e `__all__` exports

#### **📝 A2.2 Estrutura do Novo Arquivo**

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

#### **🧪 A2.3 Validar QueryService Extraído**

- [ ] Verificar que todos os imports estão corretos
- [ ] Verificar que usa TokenManager para contagem
- [ ] Testar import: `from services.query_service import QueryService`
- [ ] Testar funcionalidades básicas

---

### **🧹 FASE A3: LIMPAR EMBEDDING_SERVICE.PY**

#### **📦 A3.1 Remover QueryService**

- [ ] Remover classe QueryService completa
- [ ] Remover imports específicos do QueryService não usados por EmbeddingService
- [ ] Manter imports necessários para EmbeddingService

#### **📦 A3.2 Remover AIService Duplicado**

- [ ] Remover classe AIService completa do embedding_service.py
- [ ] Remover imports específicos do AIService duplicado
- [ ] Verificar que não há referências órfãs

#### **📝 A3.3 Atualizar Estrutura Limpa**

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

#### **🧪 A3.4 Validar EmbeddingService Limpo**

- [ ] Verificar que EmbeddingService funciona normalmente
- [ ] Verificar que não há imports órfãos
- [ ] Testar import: `from services.embedding_service import EmbeddingService`

---

### **🔄 FASE A4: ATUALIZAR IMPORTS DE SERVICES**

#### **🔄 A4.1 Atualizar Imports de QueryService**

- [ ] Atualizar todos os arquivos listados em A1.1
- [ ] Para cada arquivo, substituir:
  - [ ] `from services.embedding_service import QueryService` → `from services.query_service import QueryService`

#### **🔄 A4.2 Atualizar services/__init__.py**

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

#### **🔄 A4.3 Verificar AIService Principal**

- [ ] Verificar que ai_service.py já usa TokenManager (pré-requisito cumprido)
- [ ] Verificar que import de QueryService funciona
- [ ] Validar que não há dependências quebradas

---

## ✅ PARTE B: VALIDAÇÃO INTEGRADA

### **🧪 FASE B1: TESTES END-TO-END**

#### **🔄 B1.1 Testes de Fluxo Completo**

- [ ] Testar fluxo: generate → select → query → ask
- [ ] Verificar que QueryService funciona no novo local
- [ ] Verificar que EmbeddingService limpo funciona normalmente
- [ ] Validar que não há regressões funcionais

#### **📊 B1.2 Testes de Performance**

- [ ] Comparar performance antes/depois da separação
- [ ] Verificar que não há degradação de performance
- [ ] Testar com contextos grandes (verificar que QueryService funciona)
- [ ] Benchmark de query operations

#### **🔍 B1.3 Testes de Regressão**

- [ ] Verificar que todas as APIs públicas funcionam
- [ ] Testar comandos CLI: ask, chat, query, generate, select
- [ ] Verificar que session logging funciona
- [ ] Testar integração VSCode mode

---

### **📋 FASE B2: VALIDAÇÃO DE ARQUITETURA**

#### **✅ B2.1 Checklist de Qualidade**

**Services Refactor:**
- [ ] QueryService extraído com sucesso
- [ ] EmbeddingService limpo e focado
- [ ] AIService duplicado removido
- [ ] Imports atualizados corretamente
- [ ] Zero breaking changes
- [ ] TokenManager sendo usado corretamente (pré-requisito)

#### **🏗️ B2.2 Arquitetura Final**

Verificar que a estrutura final está como planejado:

```
src/services/
├── __init__.py             # 🔄 Updated exports
├── ai_service.py           # ✅ Uses TokenManager (pré-requisito)
├── embedding_service.py    # 🔄 Cleaned (EmbeddingService only)
└── query_service.py        # 🆕 Extracted QueryService
```

#### **🎯 B2.3 Princípios Aplicados**

**Services:**
- [ ] **Single Responsibility**: Cada service tem propósito claro
- [ ] **DRY**: Eliminada duplicação do AIService
- [ ] **Clean Architecture**: Services bem organizados
- [ ] **Maintainability**: Código mais fácil de manter
- [ ] **Separation of Concerns**: Query vs Embedding operations separadas

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

**PARTE A - Services Refactor:**
- [ ] **FASE A1:** Análise de services completa
- [ ] **FASE A2:** QueryService extraído
- [ ] **FASE A3:** EmbeddingService limpo
- [ ] **FASE A4:** Imports atualizados

**PARTE B - Validação Integrada:**
- [ ] **FASE B1:** Testes end-to-end passando
- [ ] **FASE B2:** Arquitetura validada

### **🎯 ENTREGÁVEL FINAL:**
```
✅ QueryService em arquivo próprio
✅ EmbeddingService limpo e focado
✅ AIService duplicado removido
✅ Zero breaking changes nas APIs
✅ Performance mantida ou melhorada
✅ Arquitetura limpa e extensível
✅ Imports atualizados corretamente
✅ TokenManager sendo usado (pré-requisito cumprido)
✅ Separation of Concerns implementada
✅ Services bem organizados
```

---

## 🚀 PRÓXIMOS PASSOS

Após conclusão deste plano:

1. **Implementar novos providers** (OpenAI, outros)
2. **Adicionar métricas** de uso de tokens
3. **Otimizações avançadas** de cache
4. **Testes unitários** específicos para cada componente

**🎯 Ready to start implementation!**
