# 🎯 PLANO 01: TOKEN MANAGER CENTRALIZATION

## 📋 COMO USAR ESTE PLANO

Este arquivo é nosso **guia de desenvolvimento** para centralizar todo o token management do Context-AI em um único local.

### **📖 INSTRUÇÕES DE USO:**

1. **Siga a ordem sequencial** - cada fase depende da anterior
2. **Marque os checkboxes** ✅ conforme completar cada item
3. **Teste após cada fase** - valide antes de prosseguir
4. **Documente problemas** na seção "🐛 ISSUES ENCONTRADAS" no final
5. **Não pule etapas** - cada passo tem dependências específicas

### **🔄 FLUXO DE TRABALHO:**
```
FASE 1: Análise Completa → FASE 2: Criar TokenManager → FASE 3: Migrar TokenCalculator → FASE 4: Eliminar Duplicações → FASE 5: Migração Total → FASE 6: Validação Final
```

### **🎯 OBJETIVO ÚNICO:**
- ✅ **TokenManager centralizado** em `core/ai/token_manager.py`
- ✅ **Provider-aware counting** (Anthropic + Tiktoken)
- ✅ **Cache LRU** para performance otimizada
- ✅ **Zero duplicação** de código de token counting
- ✅ **Migração completa** - sem backward compatibility
- ✅ **Base limpa** para PLAN_02_CORE_REFACTOR e PLAN_03_SERVICES_REFACTOR

---

## 📊 **SITUAÇÃO ATUAL IDENTIFICADA:**

### **🧮 TOKEN COUNTING - ANÁLISE EXPANDIDA COMPLETA**
- **300+ ocorrências** de token-related functionality espalhadas (CONFIRMADO via busca sistemática)
- **4 implementações principais duplicadas:**
  1. **TokenCalculator** (services/ai_service.py) ⭐ - bem estruturado, mal localizado
  2. **count_tokens** (core/formatting/context_formatter.py) ✅ - tiktoken robusto + cache básico
  3. **count_tokens simples** (core/ai/prompt_builder.py) ❌ - duplicação básica
  4. **_estimate_token_count** (core/chunking/langchain_adapter.py) ❌ - duplicação com heurística

### **📁 ARQUIVOS COM TOKEN COUNTING (MAPEAMENTO COMPLETO):**

**🎯 ARQUIVOS CRÍTICOS (Alta Densidade):**
- **services/ai_service.py** (25+ usos) - TokenCalculator + display_token_stats + allocation logic
- **core/formatting/context_formatter.py** (30+ usos) - implementação principal tiktoken + cache LRU
- **utils/session_logger.py** (15+ usos) - token totals, statistics, metadata
- **core/ai/claude_client.py** (10+ usos) - streaming decisions, usage logging
- **config/constants/ai.py** (15+ constants) - ratios, thresholds, limits
- **core/ai/prompt_builder.py** (5+ usos) - logging, simple counting
- **config/providers/registry.py** (functions) - get_max_tokens(), get_max_output_tokens()

**🔧 ARQUIVOS DE CONFIGURAÇÃO (Token Ecosystem):**
- **config/providers/claude.py** (model configs) - max_output_tokens por modelo
- **config/providers/base.py** (base classes) - max_context_window, max_output_tokens
- **config/models/ai.py** (model configs) - token limits integration
- **config/settings.py** (settings) - token-related configurations
- **commands/config.py** (display) - token information display

**⚙️ ARQUIVOS DE INTEGRAÇÃO:**
- **core/chunking/langchain_adapter.py** (metadata) - token estimation em chunks
- **services/embedding_service.py** (stats) - context token statistics
- **config/constants/validation.py** (cache) - token cache settings

### **📊 ECOSYSTEM DE TOKEN MANAGEMENT DESCOBERTO:**

**🎯 Constants & Configuration (15+ occurrences):**
- `CONTEXT_TOKEN_RATIO = 0.65` (65% of capacity for context)
- `RESPONSE_TOKEN_RATIO = 0.8` (80% of remaining for response)  
- `MIN_RESPONSE_TOKENS = 4000` (minimum response tokens)
- `STREAMING_THRESHOLD_TOKENS = 50000` (streaming trigger threshold)
- `CHAT_HISTORY_TOKEN_RATIO` (history vs code context ratio)
- `TOKEN_CACHE_SIZE = 200` (LRU cache size)
- `AVG_CHARS_PER_TOKEN = 4` (fallback estimation ratio)

**🎯 Provider System Integration (86+ max_tokens occurrences):**
- `get_max_tokens()` - dynamic context window por modelo ativo
- `get_max_output_tokens()` - dynamic max output por modelo ativo
- Claude models: varying max_output_tokens (8K-64K depending on model)
- Provider-specific token limits and configurations

**🎯 Session & Logging System (56+ input/output token occurrences):**
- `total_tokens`, `total_prompt_tokens`, `total_response_tokens` tracking
- Token statistics per turn and session
- Token metadata in context logging
- Token relevance calculations for context quality

**🎯 Streaming & Performance System:**
- Token-based streaming decisions (`STREAMING_THRESHOLD_TOKENS`)
- Performance diagnostics based on token thresholds  
- Context window usage monitoring and warnings
- Cache performance optimization for repeated token counting

### **✅ ANÁLISE EXPANDIDA CONCLUÍDA:**
- ✅ **Busca sistemática realizada** - 300+ casos identificados
- ✅ **Patterns criativos mapeados** - input_tokens, output_tokens, max_tokens
- ✅ **Edge cases descobertos** - constants, configs, session management
- ✅ **Ecosystem completo documentado** - provider integration, performance system

---

## 🔍 FASE 1: ANÁLISE COMPLETA E MAPEAMENTO

### **🚀 FASE 1.1: VALIDAR ANÁLISE BASE**

#### **📋 1.1.1 Confirmar Implementações Principais**

- [ ] Verificar `TokenCalculator` em `services/ai_service.py`
- [ ] Verificar `count_tokens` em `core/formatting/context_formatter.py`
- [ ] Verificar `count_tokens` em `core/ai/prompt_builder.py`
- [ ] Verificar `_estimate_token_count` em `core/chunking/langchain_adapter.py`
- [ ] Documentar exatamente quais métodos cada implementação possui

#### **📋 1.1.2 Mapear APIs Críticas em TokenCalculator**

**Métodos do TokenCalculator que devem ser migrados:**
- [ ] `calculate_context_allocation()` - alocação de contexto e histórico
- [ ] `calculate_response_tokens()` - tokens máximos de resposta
- [ ] Outros métodos encontrados durante análise

---

### **🔍 FASE 1.2: BUSCA EXPANDIDA (CRÍTICA)**

#### **📋 1.2.1 Busca Sistemática por Token Counting**

**Patterns básicos (CONCLUÍDO):**
- ✅ `count_tokens` (função direta) - 22 resultados encontrados
- ✅ `token_count` (variáveis/campos) - múltiplas ocorrências
- ✅ `tokens` (em contexto de counting) - 300+ resultados
- ✅ `tiktoken` (library usage) - 4 resultados encontrados
- ✅ `anthropic.*token` (anthropic tokenizer) - 0 resultados diretos
- ✅ `len.*encode` (encoding patterns) - 2 resultados encontrados
- ✅ `// 4` ou `/ 4` (estimation heuristics) - 4 resultados cada

**Patterns avançados descobertos (CONCLUÍDO):**
- ✅ `input_tokens|output_tokens` - 56 resultados críticos
- ✅ `max_tokens` - 86 resultados críticos  
- ✅ `_estimate_token_count` - 2 resultados específicos
- ✅ `AVG_CHARS_PER_TOKEN` - 3 resultados com constante
- ✅ `RESPONSE_TOKEN_RATIO|CONTEXT_TOKEN_RATIO|MIN_RESPONSE_TOKENS` - 15 resultados
- ✅ `STREAMING_THRESHOLD_TOKENS` - 5 resultados para streaming decisions

#### **📋 1.2.2 Busca por Imports e Dependencies**

**Imports diretos (CONCLUÍDO):**
- ✅ `import tiktoken` - Apenas em context_formatter.py
- ✅ `from tiktoken import` - Não encontrado
- ✅ `import anthropic` - Não encontrado (uso via try/except)
- ✅ `from anthropic import` - Não encontrado
- ✅ Imports indiretos via other modules - Identificados via registry system

**Provider functions descobertas:**
- ✅ `get_max_tokens()` - função crítica do provider registry
- ✅ `get_max_output_tokens()` - função crítica do provider registry
- ✅ Token limits integration via config system

#### **📋 1.2.3 Análise Inteligente e Criativa**

- [ ] **Busca contextual**: Procurar por logic que pode estar fazendo token estimation indiretamente
- [ ] **Análise de imports**: Verificar se outros módulos re-exportam token functions
- [ ] **Pattern recognition**: Identificar padrões de uso não óbvios
- [ ] **Cross-reference**: Verificar calls para TokenCalculator methods em outros arquivos

#### **📋 1.2.4 Documentar Achados Expandidos**

```
📋 CASOS DESCOBERTOS (ANÁLISE EXPANDIDA COMPLETA):

✅ ESCOPO REAL DESCOBERTO: 300+ ocorrências (não 61+ como estimado)
✅ src/services/ai_service.py - 25+ usos (TokenCalculator + display_token_stats + allocation logic)
✅ src/core/formatting/context_formatter.py - 30+ usos (tiktoken + cache LRU)
✅ src/utils/session_logger.py - 15+ usos (totals, statistics, metadata)
✅ src/core/ai/claude_client.py - 10+ usos (streaming, usage logging)
✅ src/config/constants/ai.py - 15+ constants (ratios, thresholds, limits)
✅ src/config/providers/registry.py - get_max_tokens(), get_max_output_tokens()
✅ src/config/providers/claude.py - max_output_tokens por modelo
✅ src/config/providers/base.py - max_context_window, max_output_tokens
✅ src/commands/config.py - token information display
✅ src/config/models/ai.py - token limits integration
✅ src/config/settings.py - token-related configurations
✅ src/core/ai/prompt_builder.py - 5+ usos (logging, simple counting)
✅ src/core/chunking/langchain_adapter.py - _estimate_token_count
✅ src/services/embedding_service.py - context token statistics
✅ src/config/constants/validation.py - token cache settings

CONFIRMADO: Ecosystem de token management muito mais complexo que estimado inicialmente
```

---

### **📊 FASE 1.3: DOCUMENTAR APIS NECESSÁRIAS**

#### **📋 1.3.1 APIs Públicas Obrigatórias**

**Funções BÁSICAS que DEVEM existir no TokenManager:**
- [ ] `count_tokens(text: str, provider: Optional[TokenProvider] = None) -> int`
- [ ] `calculate_context_allocation(question: str, include_history: bool = False) -> Dict[str, int]`
- [ ] `calculate_response_tokens(input_tokens: int, context_tokens: int) -> int`
- [ ] `should_use_streaming(text: str) -> bool` (baseado em STREAMING_THRESHOLD_TOKENS)
- [ ] `clear_cache() -> None` (para LRU cache management)

**Funções AVANÇADAS descobertas durante análise expandida:**
- [ ] `get_streaming_threshold() -> int` (retorna STREAMING_THRESHOLD_TOKENS)
- [ ] `get_model_token_limits() -> Dict[str, int]` (max_input, max_output, max_context)
- [ ] `estimate_tokens_from_chars(char_count: int) -> int` (usando AVG_CHARS_PER_TOKEN)
- [ ] `validate_token_limits(input_tokens: int, output_tokens: int = 0) -> Dict[str, Any]`
- [ ] `get_cache_info() -> Dict[str, Any]` (estatísticas LRU cache)
- [ ] `get_performance_stats() -> Dict[str, Any]` (stats completas)

#### **📋 1.3.2 Provider Support Necessário**

- [ ] **TokenProvider.CLAUDE** - Anthropic tokenizer
- [ ] **TokenProvider.OPENAI** - Tiktoken (cl100k_base)
- [ ] **Auto-detection** baseado em config ativa
- [ ] **Fallback estimation** quando libraries não disponíveis

---

## 🏗️ FASE 2: CRIAR TOKEN_MANAGER.PY

### **🚀 FASE 2.1: ESTRUTURA BASE**

#### **📦 2.1.1 Criar Arquivo e Estrutura**

- [ ] Criar arquivo `src/core/ai/token_manager.py`
- [ ] Implementar enums e classes base
- [ ] Adicionar documentação completa
- [ ] Configurar `__all__` exports

#### **📝 2.1.2 Implementação Provider-Aware com LRU Cache**

```python
"""
Token Management for Context-AI.

Centralized token counting with provider-specific implementations.
Supports Anthropic (Claude) and OpenAI (GPT) token counting with LRU cache for performance.
"""

from typing import Dict, Optional
from enum import Enum
from functools import lru_cache
from utils.logging import get_logger

class TokenProvider(Enum):
    """Supported token counting providers."""
    CLAUDE = "claude"
    OPENAI = "openai"
    AUTO = "auto"  # Detect from active provider

class AnthropicTokenCounter:
    """Anthropic-specific token counter using their official library."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens using Anthropic's tokenizer."""
        try:
            import anthropic
            # Use Anthropic's official token counter when available
            return len(anthropic.get_tokenizer().encode(text))
        except ImportError:
            self.logger.debug("Anthropic library not available, using fallback estimation")
            # Fallback to estimation if anthropic library not available
            return max(1, len(text.strip()) // 4)
        except Exception as e:
            self.logger.warning(f"Anthropic tokenizer error: {e}, using fallback")
            return max(1, len(text.strip()) // 4)

class OpenAITokenCounter:
    """OpenAI-specific token counter using tiktoken."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self._encoder = None
        self._load_encoder()
    
    def _load_encoder(self):
        """Load tiktoken encoder with error handling."""
        try:
            import tiktoken
            self._encoder = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
            self.logger.debug("Tiktoken encoder loaded successfully")
        except ImportError:
            self.logger.debug("Tiktoken library not available")
            self._encoder = None
        except Exception as e:
            self.logger.warning(f"Error loading tiktoken encoder: {e}")
            self._encoder = None
    
    def count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken."""
        if self._encoder:
            try:
                return len(self._encoder.encode(text))
            except Exception as e:
                self.logger.warning(f"Tiktoken encoding error: {e}, using fallback")
                return max(1, len(text.strip()) // 4)
        else:
            return max(1, len(text.strip()) // 4)  # Fallback estimation

class TokenManager:
    """Centralized token management with provider-specific counting and LRU cache."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self._counters = {
            TokenProvider.CLAUDE: AnthropicTokenCounter(),
            TokenProvider.OPENAI: OpenAITokenCounter(),
        }
        self._active_provider = TokenProvider.CLAUDE  # Default to Claude
        self._auto_detect_provider()
    
    def _auto_detect_provider(self) -> None:
        """Auto-detect provider from active configuration."""
        try:
            from config.providers.registry import get_active_provider_name
            provider_name = get_active_provider_name()
            
            if provider_name == "claude":
                self._active_provider = TokenProvider.CLAUDE
            elif provider_name == "openai":
                self._active_provider = TokenProvider.OPENAI
            else:
                self.logger.debug(f"Unknown provider {provider_name}, defaulting to Claude")
                
        except Exception as e:
            self.logger.debug(f"Provider auto-detection failed: {e}, defaulting to Claude")
            self._active_provider = TokenProvider.CLAUDE
    
    def set_active_provider(self, provider: TokenProvider) -> None:
        """Set the active token counting provider."""
        self._active_provider = provider
        self.logger.debug(f"Active token provider set to: {provider.value}")
    
    def get_active_provider(self) -> TokenProvider:
        """Get current active provider."""
        return self._active_provider
    
    @lru_cache(maxsize=1000)
    def count_tokens(self, text: str, provider: Optional[TokenProvider] = None) -> int:
        """
        Count tokens in text using specified or active provider.
        
        Uses LRU cache for performance - repeated texts are cached.
        
        Args:
            text: Text to count tokens for
            provider: Specific provider to use (defaults to active provider)
        
        Returns:
            Number of tokens in the text
        """
        if not text or not text.strip():
            return 0
        
        provider = provider or self._active_provider
        counter = self._counters[provider]
        
        try:
            token_count = counter.count_tokens(text)
            self.logger.debug(f"Token count for {len(text)} chars: {token_count} tokens ({provider.value})")
            return token_count
        except Exception as e:
            self.logger.error(f"Token counting failed: {e}")
            # Final fallback
            return max(1, len(text.strip()) // 4)
    
    def calculate_context_allocation(self, question: str, include_history: bool = False) -> Dict[str, int]:
        """
        Calculate token allocation for context and history.
        
        Migrated from TokenCalculator in ai_service.py
        """
        from config.constants.ai import CHAT_HISTORY_TOKEN_RATIO, CONTEXT_TOKEN_RATIO
        from config.providers.registry import get_max_tokens
        
        question_tokens = self.count_tokens(question)
        total_context_tokens = int(get_max_tokens() * CONTEXT_TOKEN_RATIO)
        
        if include_history:
            history_tokens = int(total_context_tokens * CHAT_HISTORY_TOKEN_RATIO)
            code_context_tokens = total_context_tokens - history_tokens
        else:
            history_tokens = 0
            code_context_tokens = total_context_tokens
        
        allocation = {
            "question_tokens": question_tokens,
            "total_context_tokens": total_context_tokens,
            "history_tokens": history_tokens,
            "code_context_tokens": code_context_tokens
        }
        
        self.logger.debug(f"Context allocation: {allocation}")
        return allocation
    
    def calculate_response_tokens(self, input_tokens: int, context_tokens: int) -> int:
        """
        Calculate maximum response tokens.
        
        Migrated from TokenCalculator in ai_service.py
        """
        from config.constants.ai import MIN_RESPONSE_TOKENS, RESPONSE_TOKEN_RATIO
        from config.providers.registry import get_max_tokens, get_max_output_tokens
        
        model_max_tokens = get_max_tokens()
        model_max_output = get_max_output_tokens()
        
        available_tokens = model_max_tokens - input_tokens
        max_response_tokens = min(
            available_tokens * RESPONSE_TOKEN_RATIO,
            max(MIN_RESPONSE_TOKENS, context_tokens // 2),
        )
        
        final_response_tokens = int(min(max_response_tokens, model_max_output))
        
        self.logger.debug(f"Response tokens calculated: {final_response_tokens} (input: {input_tokens}, context: {context_tokens})")
        return final_response_tokens
    
    def should_use_streaming(self, text: str) -> bool:
        """Determine if streaming should be used based on input size."""
        from config.constants.ai import STREAMING_THRESHOLD_TOKENS
        token_count = self.count_tokens(text)
        use_streaming = token_count > STREAMING_THRESHOLD_TOKENS
        
        self.logger.debug(f"Streaming decision: {'yes' if use_streaming else 'no'} ({token_count} tokens)")
        return use_streaming
    
    def clear_cache(self) -> None:
        """Clear the LRU cache for token counting."""
        self.count_tokens.cache_clear()
        self.logger.debug("Token counting cache cleared")
    
    def get_cache_info(self) -> Dict[str, int]:
        """Get LRU cache statistics."""
        cache_info = self.count_tokens.cache_info()
        return {
            "hits": cache_info.hits,
            "misses": cache_info.misses,
            "maxsize": cache_info.maxsize,
            "currsize": cache_info.currsize,
            "hit_rate": cache_info.hits / (cache_info.hits + cache_info.misses) if (cache_info.hits + cache_info.misses) > 0 else 0.0
        }

# Global token manager instance
_token_manager: Optional[TokenManager] = None

def get_token_manager() -> TokenManager:
    """Get global token manager instance."""
    global _token_manager
    if _token_manager is None:
        _token_manager = TokenManager()
    return _token_manager

# NO backward compatibility functions - force migration
__all__ = [
    'TokenProvider',
    'TokenManager', 
    'get_token_manager',
]
```

#### **🧪 2.1.3 Validar TokenManager Base**

- [ ] Testar import: `from core.ai.token_manager import get_token_manager, TokenManager, TokenProvider`
- [ ] Testar instanciação: `token_manager = get_token_manager()`
- [ ] Testar contagem básica: `token_manager.count_tokens("test text")`
- [ ] Testar provider switching: `token_manager.set_active_provider(TokenProvider.OPENAI)`
- [ ] Testar cache: chamadas repetidas devem usar cache
- [ ] Testar cache info: `token_manager.get_cache_info()`

---

## 🔄 FASE 3: MIGRAR TOKENCALCULATOR

### **🚀 FASE 3.1: EXTRAIR TOKENCALCULATOR**

#### **📦 3.1.1 Analisar TokenCalculator Existente**

- [ ] Abrir `services/ai_service.py`
- [ ] Localizar classe `TokenCalculator` completa
- [ ] Documentar TODOS os métodos que possui
- [ ] Verificar se já tem métodos equivalentes no TokenManager

#### **📦 3.1.2 Verificar Métodos Migrados**

- [ ] Confirmar que `calculate_context_allocation()` foi implementado no TokenManager
- [ ] Confirmar que `calculate_response_tokens()` foi implementado no TokenManager  
- [ ] Verificar se há outros métodos no TokenCalculator que precisam ser migrados
- [ ] Adicionar métodos faltantes ao TokenManager se necessário

#### **📦 3.1.3 Remover TokenCalculator**

- [ ] Remover classe `TokenCalculator` completa de `services/ai_service.py`
- [ ] Manter temporariamente outros códigos do ai_service.py intactos

---

### **🔧 FASE 3.2: ATUALIZAR AI_SERVICE**

#### **📦 3.2.1 Adicionar Import do TokenManager**

- [ ] Adicionar import: `from core.ai.token_manager import get_token_manager`
- [ ] Remover imports relacionados ao TokenCalculator antigo

#### **📦 3.2.2 Substituir Uso do TokenCalculator**

- [ ] Localizar todas as chamadas para `TokenCalculator` methods
- [ ] Substituir por chamadas ao `get_token_manager()`:
  - [ ] `TokenCalculator.calculate_context_allocation()` → `get_token_manager().calculate_context_allocation()`
  - [ ] `TokenCalculator.calculate_response_tokens()` → `get_token_manager().calculate_response_tokens()`
  - [ ] Outras chamadas encontradas

#### **🧪 3.2.3 Testar AI_Service Atualizado**

- [ ] Testar que AI_service importa sem erro
- [ ] Testar que funcionalidades que usavam TokenCalculator funcionam
- [ ] Verificar que não há referências órfãs ao TokenCalculator

---

## 🧹 FASE 4: ELIMINAR IMPLEMENTAÇÕES DUPLICADAS

### **🚀 FASE 4.1: SUBSTITUIR EM CONTEXT_FORMATTER**

#### **📦 4.1.1 Analisar Implementação Atual**

- [ ] Abrir `core/formatting/context_formatter.py`
- [ ] Localizar função `count_tokens()` (duas versões: tiktoken e fallback)
- [ ] Localizar implementação de cache (se existir)
- [ ] Documentar exatamente o que precisa ser removido

#### **📦 4.1.2 Remover Implementação Duplicada**

- [ ] Remover AMBAS as implementações de `count_tokens` do arquivo
- [ ] Remover cache implementation local (se existir)
- [ ] Remover imports relacionados (tiktoken, etc.)

#### **📦 4.1.3 Adicionar Import do TokenManager**

- [ ] Adicionar import: `from core.ai.token_manager import get_token_manager`
- [ ] Substituir chamadas `count_tokens(text)` por `get_token_manager().count_tokens(text)`

#### **🧪 4.1.4 Testar Context Formatter**

- [ ] Testar formatação de contexto funciona normalmente
- [ ] Verificar que não há imports órfãos
- [ ] Validar que performance está adequada

---

### **🧹 FASE 4.2: SUBSTITUIR EM PROMPT_BUILDER**

#### **📦 4.2.1 Analisar e Remover**

- [ ] Abrir `core/ai/prompt_builder.py`
- [ ] Localizar função `count_tokens()` simples
- [ ] Remover implementação local completa
- [ ] Remover imports relacionados

#### **📦 4.2.2 Atualizar para TokenManager**

- [ ] Adicionar import: `from core.ai.token_manager import get_token_manager`
- [ ] Substituir chamadas por: `get_token_manager().count_tokens(text)`

#### **🧪 4.2.3 Testar Prompt Builder**

- [ ] Testar que prompt building funciona
- [ ] Verificar que logs de token incluem contagem correta

---

### **🧹 FASE 4.3: SUBSTITUIR EM LANGCHAIN_ADAPTER**

#### **📦 4.3.1 Analisar e Remover**

- [ ] Abrir `core/chunking/langchain_adapter.py`
- [ ] Localizar método `_estimate_token_count()`
- [ ] Remover método completo
- [ ] Documentar onde era usado

#### **📦 4.3.2 Atualizar para TokenManager**

- [ ] Adicionar import: `from core.ai.token_manager import get_token_manager`
- [ ] Substituir chamadas `self._estimate_token_count(chunk_text)` por `get_token_manager().count_tokens(chunk_text)`

#### **🧪 4.3.3 Testar Chunking Operations**

- [ ] Testar que chunking funciona normalmente
- [ ] Verificar que metadata de chunks inclui token count correto

---

## 🔄 FASE 5: MIGRAÇÃO TOTAL DE IMPORTS

### **🔍 FASE 5.1: BUSCA COMPLETA POR USOS**

#### **📋 5.1.1 Busca Sistemática Final**

**Buscar em todo o codebase por:**
- [ ] `count_tokens` (função direta)
- [ ] `TokenCalculator` (classe antiga) 
- [ ] `_estimate_token_count` (método removido)
- [ ] `tiktoken` (imports diretos que podem ter sobrado)
- [ ] `anthropic.*token` (usos diretos)

#### **📋 5.1.2 Verificar Arquivos Conhecidos**

- [ ] `utils/session_logger.py` - atualizar usos de token counting
- [ ] `core/ai/claude_client.py` - verificar usos para streaming
- [ ] `services/embedding_service.py` - verificar estatísticas de contexto
- [ ] Qualquer outro arquivo encontrado nas buscas

#### **📋 5.1.3 Documentar Todos os Achados**

```
📋 MIGRAÇÃO COMPLETA (atualizar durante execução):

✅ src/utils/session_logger.py - line X: count_tokens() → get_token_manager().count_tokens()
✅ src/core/ai/claude_client.py - line Y: uso direto → TokenManager
[ ... adicionar CADA arquivo encontrado ... ]

Se NENHUM uso restante:
✅ PERFEITO: Migração 100% completa - zero usos antigos
```

---

### **🔄 FASE 5.2: ATUALIZAR CADA ARQUIVO ENCONTRADO**

#### **📦 5.2.1 Template de Atualização**

**Para cada arquivo encontrado:**
- [ ] Adicionar import: `from core.ai.token_manager import get_token_manager`
- [ ] Remover imports antigos (tiktoken, anthropic se diretos)
- [ ] Substituir chamadas antigas por `get_token_manager().count_tokens()`
- [ ] Testar que arquivo continua funcionando

#### **📦 5.2.2 Casos Especiais**

**Se encontrar usos mais complexos:**
- [ ] Documentar uso específico
- [ ] Determinar método apropriado do TokenManager
- [ ] Migrar com cuidado extra
- [ ] Testar extensivamente

---

### **🧪 FASE 5.3: VALIDAÇÃO DE MIGRAÇÃO COMPLETA**

#### **📋 5.3.1 Busca por Violações**

**Buscar no codebase inteiro por:**
- [ ] `import tiktoken` (deve haver zero)
- [ ] `TokenCalculator` (deve haver zero)
- [ ] `_estimate_token_count` (deve haver zero)
- [ ] `count_tokens` sem `get_token_manager` (deve haver zero, exceto no próprio TokenManager)

#### **📋 5.3.2 Critério de Sucesso**

```
✅ MIGRAÇÃO 100% COMPLETA quando:
- Zero imports diretos de tiktoken fora do TokenManager
- Zero referências ao TokenCalculator antigo
- Zero implementações duplicadas de count_tokens
- Todas as 61+ ocorrências migradas para get_token_manager()
- Todos os testes passando
```

---

## ✅ FASE 6: VALIDAÇÃO FINAL E TESTES

### **🧪 FASE 6.1: TESTES DE FUNCIONALIDADE**

#### **🔄 6.1.1 Testes de TokenManager**

- [ ] Testar `count_tokens()` com textos diversos
- [ ] Testar provider switching (Claude ↔ OpenAI)
- [ ] Testar cache LRU (hit rate deve melhorar com repetições)
- [ ] Testar `calculate_context_allocation()` com diferentes cenários
- [ ] Testar `calculate_response_tokens()` com limites diversos
- [ ] Testar `should_use_streaming()` com textos grandes e pequenos

#### **🔄 6.1.2 Testes de Integração**

- [ ] Testar comando `ask` (usa TokenManager via AI_service)
- [ ] Testar comando `query` (usa TokenManager via context formatting)
- [ ] Testar comando `generate` (usa TokenManager via chunking)
- [ ] Testar comando `chat` (usa TokenManager via streaming decisions)
- [ ] Verificar que session logging ainda funciona

### **📊 FASE 6.2: TESTES DE PERFORMANCE**

#### **⚡ 6.2.1 Benchmark de Cache LRU**

- [ ] Testar token counting sem cache (simular)
- [ ] Testar token counting com cache LRU
- [ ] Medir hit rate do cache após uso normal
- [ ] Verificar que performance é pelo menos igual ou melhor que antes

#### **📈 6.2.2 Benchmark de Providers**

- [ ] Comparar performance Anthropic vs Tiktoken
- [ ] Testar fallback quando libraries não disponíveis
- [ ] Verificar que auto-detection funciona corretamente

### **🏗️ FASE 6.3: VALIDAÇÃO ARQUITETURAL**

#### **✅ 6.3.1 Checklist de Qualidade Final**

**TokenManager:**
- [ ] Centralizado em `core/ai/token_manager.py`
- [ ] Provider-aware (Anthropic + Tiktoken) funcionando
- [ ] Cache LRU implementado e funcionando
- [ ] Auto-detection de provider funcionando
- [ ] APIs críticas migradas (context_allocation, response_tokens)

**Migração:**
- [ ] ZERO implementações duplicadas restantes
- [ ] ZERO imports diretos de tiktoken/anthropic fora do TokenManager
- [ ] ZERO referências ao TokenCalculator antigo
- [ ] Todas as 61+ ocorrências migradas

**Qualidade:**
- [ ] Logging adequado em todas as operações
- [ ] Error handling robusto
- [ ] Performance igual ou melhor que antes
- [ ] Zero breaking changes para usuários finais

#### **🎯 6.3.2 Preparação para Próximos Planos**

**Verificar que está pronto para:**
- [ ] **PLAN_02_CORE_REFACTOR**: Pode usar `get_token_manager()` em qualquer lugar
- [ ] **PLAN_03_SERVICES_REFACTOR**: Pode focar só no QueryService sem token management
- [ ] **Outros planos**: Token management não será mais uma preocupação

---

## 🐛 ISSUES ENCONTRADAS

### **Durante Análise:**
```
[ Documentar problemas encontrados durante análise expandida ]

Exemplo:
- Issue: Encontrado token counting não documentado em module X
- Descrição: Module usa tiktoken diretamente sem nosso conhecimento
- Solução: Migrar para get_token_manager()
- Status: ✅ Resolvido
```

### **Durante Implementação:**
```
[ Documentar problemas durante criação do TokenManager ]

Exemplo:
- Issue: Cache LRU não funcionando com provider switching
- Descrição: Cache key não inclui provider
- Solução: Ajustar implementação do cache
- Status: ✅ Resolvido
```

### **Durante Migração:**
```
[ Documentar problemas durante migração de código ]

Exemplo:
- Issue: Import circular entre TokenManager e config
- Descrição: TokenManager importa config que importa TokenManager
- Solução: Mover import para dentro da função
- Status: ✅ Resolvido
```

---

## 📋 CHECKLIST FINAL

### **FASES OBRIGATÓRIAS:**
- [ ] **FASE 1:** Análise completa e mapeamento
- [ ] **FASE 2:** TokenManager criado e validado
- [ ] **FASE 3:** TokenCalculator migrado
- [ ] **FASE 4:** Implementações duplicadas eliminadas
- [ ] **FASE 5:** Migração total de imports
- [ ] **FASE 6:** Validação final e testes

### **🎯 ENTREGÁVEL FINAL:**
```
✅ TokenManager centralizado em core/ai/token_manager.py
✅ Provider-aware counting (Anthropic + Tiktoken)
✅ Cache LRU implementado para performance
✅ Auto-detection de provider ativo
✅ TokenCalculator migrado de ai_service.py
✅ 4 implementações duplicadas eliminadas
✅ Todas as 61+ ocorrências migradas para get_token_manager()
✅ Zero imports diretos de tiktoken/anthropic fora do TokenManager
✅ Zero backward compatibility - migração completa
✅ Base limpa para PLAN_02_CORE_REFACTOR e PLAN_03_SERVICES_REFACTOR
✅ Performance igual ou melhor com cache LRU
✅ Error handling robusto com fallbacks
✅ Logging detalhado para debugging
✅ Todos os testes passando
```

---

## 🚀 PRÓXIMOS PASSOS

Após conclusão deste plano:

### **📋 PLANOS DEPENDENTES PODEM EXECUTAR:**
- **PLAN_02_CORE_REFACTOR**: Pode usar `get_token_manager()` sem se preocupar com token counting
- **PLAN_03_SERVICES_REFACTOR**: Pode focar na extração do QueryService sem token management
- **Outros planos**: Token management não será mais duplicação ou preocupação

### **🔧 MELHORIAS FUTURAS POSSÍVEIS:**
1. **Novos providers** (Cohere, local models, etc.)
2. **Cache persistente** entre sessões
3. **Métricas avançadas** de uso de tokens
4. **Otimizações específicas** por tipo de texto

**🎯 Ready for implementation! Este plano criará a base sólida de token management que todos os outros planos precisam.**
