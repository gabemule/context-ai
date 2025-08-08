# Context-AI Configuration System

## 🎯 O que este sistema resolve

**Problema Original:** Configurações espalhadas, inconsistentes e difíceis de manter
**Nossa Solução:** Sistema centralizado com responsabilidades claras e fluxo unidirecional
**Resultado:** Configuração confiável, testável e fácil de estender

## 🏗️ Arquitetura por Propósito

### 🏛️ **ConfigCore** - "Onde fica a configuração"
- **Responsabilidade:** Único ponto de acesso para config.json
- **Resolve:** Elimina inconsistências quando múltiplos componentes precisam da mesma configuração
- **Benefício:** Mudanças são refletidas automaticamente em todo o sistema

### 🎮 **SettingsManager** - "Como alterar configurações"
- **Responsabilidade:** Interface de negócio para configurações do usuário
- **Resolve:** Coordena operações complexas que envolvem múltiplos managers
- **Benefício:** API única e consistente para o usuário final

### 📦 **EmbeddingManager** - "Gerenciar embeddings"
- **Responsabilidade:** Todas as operações com embeddings
- **Resolve:** Operações de embedding que estavam espalhadas em vários lugares
- **Benefício:** Comportamento consistente e manutenção centralizada

### 🗂️ **StorageManager** - "Organizar arquivos e paths"
- **Responsabilidade:** Gerenciamento de caminhos e estrutura de armazenamento
- **Resolve:** Paths hardcoded e estruturas de diretório inconsistentes
- **Benefício:** Organização padronizada e fácil mudança de localização

### ⚙️ **SetupManager** - "Garantir que tudo está configurado"
- **Responsabilidade:** Copia templates quando necessário
- **Resolve:** Configurações faltando causando erros de execução
- **Benefício:** Sistema funciona "out of the box"

### 📝 **GuidelinesManager** - "Acessar diretrizes de código"
- **Responsabilidade:** Carregamento e cache de guidelines por linguagem
- **Resolve:** Leitura repetitiva de arquivos de guideline
- **Benefício:** Performance otimizada com cache inteligente

### 🌍 **LanguagesManager** - "Configurações por linguagem"
- **Responsabilidade:** Configurações específicas de linguagens de programação
- **Resolve:** Configurações hardcoded para diferentes linguagens
- **Benefício:** Sistema extensível para novas linguagens

### 🤖 **ProviderRegistry** - "Gerenciar provedores de IA"
- **Responsabilidade:** Configurações dinâmicas de provedores de IA
- **Resolve:** Configurações hardcoded de modelos e capacidades
- **Benefício:** Fácil adição de novos provedores sem mudança de código

## 🔄 Como os Componentes Interagem

```
ConfigCore ← SettingsManager → EmbeddingManager
    ↑            ↓                ↑
ProviderRegistry  StorageManager ←┘
    ↑            ↑
GuidelinesManager → SetupManager ← LanguagesManager
```

**Princípio:** Fluxo unidirecional elimina dependências circulares e bugs

---

## 🚫 REGRAS FUNDAMENTAIS - NUNCA FAÇA ISSO

### ❌ Valores Hardcoded
**Problema:** Duplicação de valores leva a inconsistências
**Solução:** SEMPRE usar constants centralizadas

```python
# ❌ ERRADO - valores hardcoded
chunk_size = 2000  # hardcoded!
provider = "claude"  # hardcoded!

# ✅ CORRETO - usar constants
from config.constants.chunking import DEFAULT_CHUNK_SIZE
from config.providers.registry import get_provider_registry

chunk_size = DEFAULT_CHUNK_SIZE
registry = get_provider_registry()
provider = registry.default_provider
```

### ❌ Fallbacks Mascarando Problemas
**Problema:** Fallbacks escondem problemas reais do sistema
**Solução:** Deixar falhar para identificar e resolver na origem

```python
# ❌ ERRADO - fallback esconde problema
try:
    extensions = languages_registry.get_supported_extensions()
except Exception:
    extensions = [".py", ".js"]  # ❌ mascara problema real!

# ✅ CORRETO - deixa falhar para resolver problema  
extensions = languages_registry.get_supported_extensions()
```

---

## 📚 Constants Directory - Guia de Responsabilidades

### 📁 `/constants/ai.py` - Processamento de IA e LLMs
**Escopo:** Tudo relacionado a IA, tokens, chat, streaming
**Contém:** Ratios de token, limites de retry, configurações de chat history
**Import:** `from config.constants.ai import CONTEXT_TOKEN_RATIO`

### 📁 `/constants/chunking.py` - Processamento de Texto  
**Escopo:** Configurações de chunks e assembly de contexto
**Contém:** Tamanhos de chunk, overlap, limites de chunks por query
**Import:** `from config.constants.chunking import DEFAULT_CHUNK_SIZE`

### 📁 `/constants/storage.py` - Armazenamento e Arquivos
**Escopo:** Paths, arquivos, ignore patterns, limpeza
**Contém:** Diretórios padrão, limites de arquivo, padrões ignore
**Import:** `from config.constants.storage import DEFAULT_CONFIG_DIR`

### 📁 `/constants/system.py` - Sistema e Logs
**Escopo:** Configurações de sistema, logging, exit codes
**Contém:** Exit codes, conversões, configurações de log
**Import:** `from config.constants.system import LOG_RETENTION_DAYS`

### 📁 `/constants/validation.py` - Validação e Performance  
**Escopo:** Limites de validação, cache, performance
**Contém:** Validações de input, limites de performance, cache configs
**Import:** `from config.constants.validation import MIN_CHUNK_SIZE_LIMIT`

## ⚡ Guia de Decisão - Qual Arquivo Usar?

| Se você precisa de... | Use o arquivo... | Exemplo de import |
|----------------------|------------------|-------------------|
| **Tamanhos de chunk, overlap** | `chunking.py` | `from config.constants.chunking import DEFAULT_CHUNK_SIZE` |
| **Ratios de token, limites IA** | `ai.py` | `from config.constants.ai import CONTEXT_TOKEN_RATIO` |
| **Paths, diretórios padrão** | `storage.py` | `from config.constants.storage import DEFAULT_CONFIG_DIR` |
| **Validações de input** | `validation.py` | `from config.constants.validation import MIN_CHUNK_SIZE_LIMIT` |
| **Configurações de log** | `system.py` | `from config.constants.system import LOG_RETENTION_DAYS` |

---

## 🚨 Anti-Patterns - O que NÃO fazer

### ❌ Paths Hardcoded
```python
# ❌ ERRADO
config_file = base_path / "config.json"  # hardcoded!

# ✅ CORRETO  
storage_manager = get_storage_manager()
config_file = storage_manager.path_manager.config_file
```

### ❌ Validações Hardcoded
```python
# ❌ ERRADO
if tokens < 1000:  # hardcoded validation!
    raise ValueError("Too small")

# ✅ CORRETO
from config.constants.validation import MIN_CONTEXT_WINDOW_VALIDATION
if tokens < MIN_CONTEXT_WINDOW_VALIDATION:
    raise ValueError("Too small")
```

### ❌ Extensões Hardcoded
```python
# ❌ ERRADO
extensions = [".py", ".js", ".ts"]  # hardcoded!

# ✅ CORRETO
languages_registry = get_languages_registry()
extensions = languages_registry.get_supported_extensions()
```

---

## 🤖 Guidelines para Desenvolvimento com LLMs

### Antes de Modificar Qualquer Código
1. **SEMPRE** verificar se existe constant para o valor
2. **NUNCA** criar fallbacks - resolver o problema na origem
3. **SEMPRE** usar os managers centralizados
4. **VERIFICAR** se existe registry antes de hardcoding

### Checklist de Desenvolvimento
- [ ] Valor vem de constant centralizada?
- [ ] Está usando o manager correto?  
- [ ] Não há duplicação de lógica?
- [ ] Sem fallbacks mascarando problemas?
- [ ] Registry/Manager existe para essa responsabilidade?

### Processo de Debugging
```bash
# 1. Procurar valores suspeitos
grep -r "2000\|200\|claude\|standard" src/config/ --exclude-dir=samples

# 2. Verificar se constant já existe  
find src/config/constants/ -name "*.py" -exec grep -l "valor_suspeito" {} \;

# 3. Se não existe, adicionar no arquivo correto
```

---

## 🚀 Exemplos Práticos de Uso

### ❌ vs ✅ Exemplos Comparativos

#### Configuração de Chunking
```python
# ❌ ERRADO
chunk_size = 2000
overlap = 200

# ✅ CORRETO
from config.constants.chunking import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP
chunk_size = DEFAULT_CHUNK_SIZE
overlap = DEFAULT_CHUNK_OVERLAP
```

#### Configuração de Storage
```python
# ❌ ERRADO
max_embeddings = 50
cleanup_days = 30

# ✅ CORRETO
from config.constants.storage import DEFAULT_MAX_EMBEDDINGS, DEFAULT_CLEANUP_AFTER_DAYS
max_embeddings = DEFAULT_MAX_EMBEDDINGS
cleanup_days = DEFAULT_CLEANUP_AFTER_DAYS
```

### Configurar API Key do Claude
```python
from config.settings import get_settings_manager

settings = get_settings_manager()
settings.set_claude_api_key("sua-api-key")
# Automaticamente: define provider ativo, modelo padrão, etc
```

### Listar Embeddings Disponíveis
```python
from config.embeddings import get_embedding_manager

embeddings = get_embedding_manager()
nomes = embeddings.list_embeddings()
print(f"Embeddings disponíveis: {nomes}")
```

### Obter Guidelines para uma Linguagem
```python
from config.guidelines import get_guidelines_manager

guidelines = get_guidelines_manager()
python_guide = guidelines.get_guideline("python")
```

### Verificar Configurações de Linguagem
```python
from config.languages import get_languages_manager

languages = get_languages_manager()
extensions = languages.get_supported_extensions()
```

## 🏗️ Padrões Arquiteturais Utilizados

### Dependency Injection
**Por que:** Permite testes unitários e modularidade
**Como:** Todos os managers aceitam dependencies via construtor

### Single Responsibility Principle
**Por que:** Cada manager tem uma responsabilidade específica
**Como:** ConfigCore = dados, SettingsManager = negócio, etc

### Interface Segregation
**Por que:** Componentes dependem apenas do que precisam
**Como:** Protocols específicos ao invés de interfaces grandes

### Factory Pattern
**Por que:** Criação consistente de instâncias globais
**Como:** Funções `get_*_manager()` para cada componente

## 🧪 Testabilidade

Todos os managers suportam dependency injection:

```python
# Teste com mock
mock_config = MockConfigCore()
settings = SettingsManager(config_core=mock_config)

# Teste isolado
mock_vector_store = MockVectorStore()
embeddings = EmbeddingManager(vector_store=mock_vector_store)
```

## 🔧 Extensibilidade

### Adicionar Novo Provider de IA
1. Criar arquivo em `providers/novo_provider.py`
2. Implementar `AIProviderProtocol`
3. Adicionar ao `ProviderRegistry`
4. Zero mudanças em outros componentes

### Adicionar Nova Linguagem
1. Editar `languages.yaml`
2. Opcional: criar guideline em `guidelines/`
3. Sistema detecta automaticamente

## 📚 Estrutura de Diretórios

```
src/config/
├── README.md              # Este arquivo
├── core.py               # Acesso centralizado a config.json
├── settings.py           # Interface de negócio
├── embeddings.py         # Operações de embeddings
├── storage.py            # Gerenciamento de paths
├── setup.py              # Cópia de templates
├── guidelines.py         # Cache de guidelines
├── models.py             # Estruturas de dados
├── interfaces.py         # Protocols para DI
├── constants/            # Constantes organizadas por domínio
├── providers/            # Configurações de provedores IA
├── languages/            # Sistema de linguagens
└── samples/              # Templates padrão
```

---

## 📂 Guia de Arquivos e Pastas - Onde Encontrar Cada Coisa

### 📄 Arquivos Principais (src/config/)

**`core.py`** - Ponto único de acesso ao config.json  
- Elimina inconsistências quando múltiplos componentes precisam da mesma configuração
- CRUD operations centralizadas para config.json
- Cache interno para performance

**`settings.py`** - Interface de negócio para usuário final  
- Coordena operações complexas entre múltiplos managers
- API amigável que combina ConfigCore + EmbeddingManager + outros
- Ponto de entrada principal para commands/

**`embeddings.py`** - Gerenciamento completo de embeddings  
- Lista, seleção, analytics de embeddings
- Interface com vector store (ChromaDB)
- Operações de cleanup e manutenção

**`storage.py`** - Paths centralizados e estrutura de armazenamento  
- PathManager para todos os caminhos do sistema
- Estrutura de diretórios padronizada
- Analytics de storage e cleanup

**`setup.py`** - Inicialização automática do sistema  
- Cópia de templates quando configs não existem
- Garante que sistema funciona "out of the box"
- Dependency injection para componentes

**`guidelines.py`** - Cache inteligente de guidelines  
- Carregamento lazy de guidelines por linguagem
- Cache com invalidação baseada em timestamp
- Copy de templates para guidelines customizadas

**`models.py`** - Estruturas de dados com Pydantic  
- Validação de tipos para todas as configurações
- Serialização/deserialização consistente
- Type hints para melhor IDE support

**`interfaces.py`** - Protocols para Dependency Injection  
- Contratos que permitem testing com mocks
- Interface Segregation Principle aplicado
- Permite substituição de implementações

### 📁 `/constants/` - Constants Organizadas por Domínio

**Padrão:** Uma constant, um lugar, zero duplicação

- **`ai.py`** → Ratios de token, limites de retry, configurações de chat
- **`chunking.py`** → Tamanhos de chunk, overlap, limites por query
- **`storage.py`** → Paths padrão, limites de arquivo, ignore patterns
- **`system.py`** → Exit codes, conversões, configurações de logging
- **`validation.py`** → Limites de validação, cache, performance

### 📁 `/providers/` - Sistema de Registry para Provedores IA

**Arquitetura:** Registry Pattern + Protocol-based Design

**`registry.py`** - Registry central que gerencia todos os providers  
- Descoberta automática de providers disponíveis
- Validação de capabilities por provider
- Factory methods para criação de clients

**`protocols.py`** - Interfaces que todos os providers devem implementar  
- `AIProviderProtocol` define contrato obrigatório
- Garante consistência entre diferentes providers
- Permite extensão sem modificar código existente

**`models.py`** - Estruturas para capabilities dos providers  
- `ProviderCapabilities` com validação Pydantic
- Metadados sobre context window, streaming, etc.
- Type-safe configuration

**`claude.py`** - Implementação específica do provider Claude  
- Modelos disponíveis com especificações completas
- Context windows e limites por modelo
- Configurações específicas do Claude

**Extensibilidade:** Para adicionar novo provider, criar arquivo similar ao `claude.py`

### 📁 `/languages/` - Sistema de Registry para Linguagens

**Arquitetura:** Registry Pattern + Inheritance System + YAML Configuration

**`registry.py`** - Registry central para configurações de linguagem  
- Cache inteligente de configurações resolvidas
- API unificada para acessar extensões, separators, etc.
- Hot reload quando configurações mudam

**`models.py`** - Estruturas de dados com herança e validação  
- `LanguageConfig` com suporte a extends (herança)
- `ResolvedLanguageConfig` com herança já aplicada
- Validação de cycles em herança

**`loader.py`** - Carregamento e parsing de configurações YAML  
- SOLID principles aplicados (SRP, OCP, DIP)
- Error handling robusto com contexto
- Template copying quando configs não existem

**Benefício:** Sistema extensível que permite herança entre linguagens (ex: TSX extends TypeScript)

### 📁 `/samples/` - Templates Padrão

**`languages.yaml`** - Template completo de configuração de linguagens  
- Exemplos de herança (vue extends javascript)
- Todas as linguagens suportadas com defaults
- Documentação inline dos campos

**`/guidelines/`** - Guidelines padrão por linguagem  
- Templates markdown para cada linguagem de programação
- Best practices e coding standards
- Exemplos práticos de uso

**`/prompts/`** - Templates de prompts organizados por modo  
- `/standard/`, `/comprehensive/`, `/minimal/`, `/strict/`
- Cada modo com arquivos específicos: `mode.yaml`, `core_instructions.md`
- Sistema modular de composição de prompts

---

## 🎯 Benefícios da Arquitetura

- ✅ **Zero dependências circulares**
- ✅ **Componentes testáveis isoladamente**
- ✅ **Fácil extensão sem mudanças em código existente**
- ✅ **Configuração consistente em todo o sistema**
- ✅ **Performance otimizada com cache inteligente**
- ✅ **Manutenção simplificada com responsabilidades claras**

## 🔍 Debugging e Troubleshooting

### Problema: Valores Hardcoded Encontrados
**Sintomas:** Números mágicos, strings duplicadas, paths hardcoded
**Solução:** 
1. Verificar se constant já existe nos arquivos `/constants/`
2. Se existe, fazer import e usar
3. Se não existe, criar no arquivo de responsabilidade correta

### Problema: Fallback Mascarando Erro
**Sintomas:** Código funciona mas erro real não é mostrado
**Solução:** Remover fallback e resolver problema na origem usando os managers

### Problema: Extensões não atualizadas
**Sintomas:** Sistema não reconhece novos tipos de arquivo
**Solução:** Usar `LanguagesRegistry.get_supported_extensions()` ao invés de lista hardcoded

### Problema: Configuração não encontrada
**Solução:** `SetupManager.ensure_all_configs_exist()` copia templates

### Problema: Embedding não aparece
**Solução:** Use `EmbeddingManager.list_embeddings()` para verificar

### Problema: Provider não funciona
**Solução:** Verifique `ProviderRegistry.get_available_providers()`

---

**Esta arquitetura é um exemplo de Clean Architecture em Python, focada em manutenibilidade e extensibilidade.**
