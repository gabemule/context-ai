# 🎯 PLANO: REFATORAÇÃO COMPLETA DE CONFIGURAÇÕES

## 📋 COMO USAR ESTE PLANO

Este arquivo é nosso **guia de desenvolvimento** para a refatoração completa do sistema de configurações do Context-AI.

### **📖 INSTRUÇÕES DE USO:**

1. **Siga a ordem sequencial** - cada fase depende da anterior
2. **Marque os checkboxes** ✅ conforme completar cada item
3. **Teste após cada fase** - valide antes de prosseguir
4. **Documente problemas** na seção "🐛 ISSUES ENCONTRADAS" no final
5. **Não pule etapas** - cada passo tem dependências específicas

### **🔄 FLUXO DE TRABALHO:**
```
FASE 1: Setup → FASE 2: Storage → FASE 3: Samples → FASE 4: Guidelines → FASE 5: Updates → FASE 6: Tests
```

### **🎯 OBJETIVO FINAL:**
- ✅ Storage em `src/config/storage.py` (não mais em utils)
- ✅ Templates centralizados em `src/config/samples/`
- ✅ Guidelines consolidado em `src/config/languages/guidelines.py`
- ✅ Estrutura de configuração limpa e lógica
- ✅ Zero breaking changes nas APIs existentes

---

## 🚀 FASE 1: PREPARAÇÃO E ANÁLISE

### **📁 1.1 Criar Estrutura de Diretórios**

- [x] Criar diretório `src/config/samples/`
- [x] Criar subdiretório `src/config/samples/guidelines/`
- [x] Criar subdiretório `src/config/samples/prompts/`

### **📊 1.2 Análise de Dependências - Storage**

- [x] Buscar todos os imports de `utils.storage` no codebase
- [x] Buscar por `get_storage_manager` em todo o código
- [x] Documentar APIs de storage que devem ser mantidas

#### **🔍 1.2.1 Busca Real de Storage (executada com sucesso):**

**Buscar por:**
- [x] `from utils.storage import` → **0 results** ✅ (migração completa)
- [x] `import utils.storage` → **0 results** ✅ (migração completa)
- [x] `utils.storage.` → **0 results** ✅ (migração completa)
- [x] `get_storage_manager` → **13 results** ✅ (todos usando config.storage)

**📋 Lista real de arquivos encontrados:**
```
✅ STORAGE MIGRATION SUCCESSFUL - Zero imports órfãos encontrados!

✅ get_storage_manager usado em 6 arquivos (todos com import correto de config.storage):
- src/commands/storage.py - from config.storage import get_storage_manager
- src/config/storage.py - def get_storage_manager() -> StorageManager (definição)
- src/core/embeddings/model_manager.py - from config.storage import get_storage_manager
- src/core/embeddings/vector_store.py - from config.storage import get_storage_manager
- src/commands/config.py - from config.storage import get_storage_manager (2x)
- src/commands/generate.py - from config.storage import get_storage_manager

✅ APIs MANTIDAS: get_storage_manager(), storage_manager.get_storage_info(), storage_manager.embedding_exists()
```

### **📊 1.3 Análise de Dependências - Guidelines**

- [x] Buscar todos os imports de `config.guidelines` no codebase
- [x] Buscar por `get_guidelines_manager` em todo o código
- [x] Documentar APIs de guidelines que devem ser mantidas

#### **🔍 1.3.1 Busca Real de Guidelines (executada com sucesso):**

**Buscar por:**
- [x] `from config.guidelines import` → **0 results** ✅ (migração completa)
- [x] `from config.guidelines.manager import` → **0 results** ✅ (migração completa)
- [x] `get_guidelines_manager` → **7 results** ✅ (todos no novo local)
- [x] `GuidelinesManager` → **7 results** ✅ (todos no novo local)

**📋 Lista real de arquivos encontrados:**
```
✅ GUIDELINES MIGRATION SUCCESSFUL - Zero imports órfãos encontrados!

✅ get_guidelines_manager/GuidelinesManager encontrados em 2 arquivos (no novo local correto):
- src/config/languages/guidelines.py - def get_guidelines_manager() -> GuidelinesManager (definição)
- src/config/languages/guidelines.py - class GuidelinesManager (classe principal)
- src/config/languages/manager.py - comentário sobre uso do GuidelinesManager

✅ APIs MANTIDAS: get_guidelines_manager(), GuidelinesManager.get_available_languages(), 
GuidelinesManager.get_guideline(), GuidelinesManager.reset_to_default()

✅ CONSOLIDAÇÃO COMPLETA: Guidelines agora em config/languages/guidelines.py (era config/guidelines/manager.py)
```

---

## 🏗️ FASE 2: MIGRAR STORAGE PARA CONFIG

### **📦 2.1 Mover Storage**

- [x] Mover `src/utils/storage.py` → `src/config/storage.py`
- [x] Manter funcionalidade 100% idêntica (zero breaking changes)
- [x] Verificar que todos os imports internos ainda funcionam

### **🔄 2.2 Atualizar Imports de Storage**

- [x] Atualizar todos os arquivos listados em 1.2.1
- [x] Para cada arquivo, substituir:
  - [x] `from utils.storage import` → `from config.storage import`
  - [x] `import utils.storage` → `import config.storage`
  - [x] `utils.storage.` → `config.storage.`

### **🧪 2.3 Validação Storage**

- [x] Testar `get_storage_manager()` funciona
- [x] Testar comando `context-ai storage` (se existir)
- [x] Verificar que paths de configuração continuam corretos
- [x] Validar que limpeza/analytics funcionam

### **🧹 2.4 Cleanup Storage**

- [x] Remover `src/utils/storage.py`
- [x] Verificar se não há imports órfãos de utils.storage
- [x] Atualizar `src/utils/__init__.py` se necessário

---

## 📁 FASE 3: CRIAR ESTRUTURA SAMPLES

### **📋 3.1 Migrar Templates para Samples**

- [x] Copiar `src/config/guidelines/*.md` → `src/config/samples/guidelines/`
- [x] Copiar `src/config/languages/languages.yaml` → `src/config/samples/languages.yaml`
- [x] Copiar `src/config/languages/README.md` → `src/config/samples/languages-README.md`
- [x] Copiar `src/config/prompt/` → `src/config/samples/prompts/` (estrutura completa)

### **📝 3.2 Criar README de Samples**

- [x] Criar `src/config/samples/README.md` explicando a estrutura
- [x] Documentar como os templates são copiados para `~/.context-ai/`
- [x] Explicar cada tipo de template (guidelines, languages, prompts)

### **🔧 3.3 Atualizar Paths nos Managers**

#### **3.3.1 Atualizar GuidelinesManager:**
- [x] Modificar `PathResolver.get_template_directory()` em `src/config/languages/guidelines.py`
- [x] Apontar para `src/config/samples/guidelines/` ao invés de `src/config/guidelines/`

#### **3.3.2 Atualizar LanguagesLoader:**
- [x] Modificar `get_source_directory()` em `src/config/languages/loader.py`
- [x] Apontar para `src/config/samples/` ao invés de `src/config/languages/`
- [x] Atualizar lista de arquivos para incluir `languages.yaml` e `languages-README.md`

#### **3.3.3 Atualizar PromptBuilder:**
- [x] Modificar `_get_default_prompt_directory()` em `src/core/ai/prompt_builder.py`
- [x] Apontar para `src/config/samples/prompts/` ao invés de `src/config/prompt/`

### **🧪 3.4 Testar Cópia de Templates**

- [x] Testar cópia de guidelines templates
- [x] Testar cópia de languages configuration
- [x] Testar cópia de prompt templates
- [x] Verificar que estrutura `~/.context-ai/` fica correta

---

## 🔄 FASE 4: CONSOLIDAR GUIDELINES EM LANGUAGES

### **📦 4.1 Mover Guidelines Manager**

- [x] Mover `src/config/guidelines/manager.py` → `src/config/languages/guidelines.py`
- [x] Manter toda a funcionalidade e APIs existentes
- [x] Atualizar imports internos se necessário

### **🔧 4.2 Atualizar Path Resolution**

- [x] Dentro de `guidelines.py`, atualizar `PathResolver.get_template_directory()`
- [x] Deve apontar para `src/config/samples/guidelines/` (não mais pasta da própria guidelines)
- [x] Manter compatibilidade com user config paths (`~/.context-ai/config/guidelines/`)

### **🔄 4.3 Atualizar Imports de Guidelines**

- [x] Atualizar todos os arquivos listados em 1.3.1
- [x] Para cada arquivo, substituir:
  - [x] `from config.guidelines.manager import` → `from config.languages.guidelines import`
  - [x] `from config.guidelines import` → `from config.languages import` (se re-exportado)

### **📋 4.4 Atualizar Languages __init__.py**

- [x] Adicionar exports de guidelines em `src/config/languages/__init__.py`:
```python
from .guidelines import get_guidelines_manager, GuidelinesManager
from .manager import get_languages_manager, LanguagesManager

__all__ = [
    'get_languages_manager', 'LanguagesManager',
    'get_guidelines_manager', 'GuidelinesManager',
]
```

### **🧹 4.5 Cleanup Guidelines**

- [x] Remover `src/config/guidelines/manager.py`
- [x] Remover diretório `src/config/guidelines/` se vazio
- [x] Verificar se não há imports órfãos

---

## 🧹 FASE 5: CLEANUP E REORGANIZAÇÃO

### **📁 5.1 Remover Templates Duplicados**

- [x] Remover `src/config/guidelines/*.md` (agora em samples)
- [x] Remover `src/config/languages/languages.yaml` (agora em samples)
- [x] Remover `src/config/languages/README.md` (agora em samples)
- [x] Remover `src/config/prompt/` (agora em samples/prompts)

### **📋 5.2 Atualizar Documentação**

- [x] Atualizar README.md do projeto se necessário
- [x] Atualizar documentação dos comandos se necessário
- [x] Verificar se guides precisam ser atualizados

### **🔧 5.3 Verificação Final de Imports**

- [x] Buscar por imports órfãos de utils.storage
- [x] Buscar por imports órfãos de config.guidelines
- [x] Verificar que todos os paths estão corretos

---

## 🧪 FASE 6: TESTES COMPLETOS

### **🔍 6.1 Testes de Storage**

- [x] Testar `get_storage_manager()` em vários contextos
- [x] Testar analytics de storage
- [x] Testar cleanup operations
- [x] Verificar paths de configuração

### **📁 6.2 Testes de Templates**

- [x] Testar cópia inicial de guidelines
- [x] Testar cópia inicial de languages config
- [x] Testar cópia inicial de prompt templates
- [x] Verificar que `~/.context-ai/` fica organizada corretamente

### **📝 6.3 Testes de Guidelines**

- [x] Testar `get_guidelines_manager()` no novo local
- [x] Testar carregamento de guidelines por linguagem
- [x] Testar alias management
- [x] Verificar integração com prompt builder

### **🔄 6.4 Testes de Integração**

- [x] Testar fluxo completo: ask/query/chat commands
- [x] Verificar que prompt building continua funcionando
- [x] Testar que guidelines são aplicadas corretamente
- [x] Validar que não há regression em funcionalidades

### **📊 6.5 Testes de Commands**

- [ ] Testar `context-ai config` commands
- [ ] Testar `context-ai storage` commands
- [ ] Testar `context-ai select` (embeddings)
- [ ] Verificar que todas as configurações funcionam

---

## 🔄 FASE 7: CONSOLIDAR CONFIG MODELS

### **📦 7.1 Criar Config Models Consolidado**

- [x] Criar arquivo `src/config/models.py` (único arquivo)
- [x] Migrar todo conteúdo de `src/config/models/base.py` → `models.py`
- [x] Migrar todo conteúdo de `src/config/models/ai.py` → `models.py`
- [x] Migrar todo conteúdo de `src/config/models/chunking.py` → `models.py`
- [x] Migrar todo conteúdo de `src/config/models/storage.py` → `models.py`
- [x] Organizar imports e dependências no arquivo consolidado

### **🔄 7.2 Atualizar Imports de Config Models**

- [x] Atualizar `src/config/settings.py`:
  - [x] `from .models import` → `from .models import` (mesmo import, arquivo diferente)
- [x] Verificar outros arquivos que possam usar config.models
- [x] Buscar por imports que referenciam o diretório models/

### **🧹 7.3 Cleanup Config Models**

- [x] Remover `src/config/models/base.py`
- [x] Remover `src/config/models/ai.py`  
- [x] Remover `src/config/models/chunking.py`
- [x] Remover `src/config/models/storage.py`
- [x] Remover `src/config/models/__init__.py`
- [x] Remover diretório `src/config/models/` (deve estar vazio)

### **🧪 7.4 Validação Config Models**

- [x] Testar que `settings.py` continua funcionando
- [x] Verificar que todos os imports estão corretos
- [x] Validar que Pydantic models funcionam corretamente
- [x] Testar comandos de configuração

### **🔄 7.5 Melhorias Config Module - Separação de Responsabilidades**

#### **📋 7.5.1 Análise de Inconsistências Identificadas**

**🔍 PROBLEMA CRÍTICO: Responsabilidades Sobrepostas**

##### **1️⃣ Duplicação EMBEDDINGS Management:**
```python
# ❌ INCONSISTÊNCIA: Duas fontes de verdade
SettingsManager.get_available_embeddings()     # Lê JSON metadata files
StorageManager.list_embeddings()               # Lê dados reais do ChromaDB

SettingsManager.save_embedding_metadata()      # Salva JSON metadata  
StorageManager.delete_embedding()              # Deleta dados reais

# 🐛 PROBLEMA: Metadata pode ficar órfão dos dados reais
```

##### **2️⃣ TRIPLICAÇÃO CONFIGURATION Copy:**
```python
# ❌ INCONSISTÊNCIA: TRÊS locais copiando configs
LanguagesManager._ensure_config_exists()       # Copia languages apenas
GuidelinesManager._ensure_guidelines_exist()   # Copia guidelines apenas  
SettingsManager._ensure_all_configs_exist()    # Copia languages + guidelines + prompts

# 🐛 PROBLEMA: Configurações podem ser copiadas 3x, total inconsistência!
```

##### **3️⃣ CONSTANTS Duplicadas:**
```python
# ❌ INCONSISTÊNCIA: BYTES_PER_MB definido em 2 lugares
src/config/constants/system.py:    BYTES_PER_MB = 1024 * 1024
src/config/constants/storage.py:   BYTES_PER_MB = 1024 * 1024

# 🐛 PROBLEMA: Duplicação de constantes, pode divergir
```

##### **4️⃣ PATH Construction Hardcoded:**
```python
# ❌ INCONSISTÊNCIA: Path construction em múltiplos locais
LanguagesManager:   Path(DEFAULT_CONFIG_DIR).expanduser() / "config"
GuidelinesManager:  Path(DEFAULT_CONFIG_DIR).expanduser() / "config" / "guidelines"  
SettingsManager:    Path("~/.context-ai").expanduser()

# 🐛 PROBLEMA: Múltiplas fontes de paths, sem centralização
```

##### **5️⃣ Sobreposição DIRECTORY Management:**
```python
# ❌ INCONSISTÊNCIA: Paths duplicados
SettingsManager.embeddings_dir = config_dir / "embeddings"
StorageManager.embeddings_dir = base_path / "embeddings"

# 🐛 PROBLEMA: Múltiplas fontes de paths, pode divergir
```

#### **💡 7.5.2 Plano de Separação de Responsabilidades**

##### **📋 CONFIG (SettingsManager) - Configurações da Aplicação**
```python
# ✅ RESPONSABILIDADES CORRETAS:
- API keys, models, providers
- Prompt modes, active embeddings  
- Application configuration (config.json)
- Centralized config copying (languages + guidelines + prompts)

# ❌ MOVER PARA StorageManager:
- get_available_embeddings()
- save_embedding_metadata()  
- delete_embedding_metadata()
- embeddings_dir management
```

##### **💾 STORAGE (StorageManager) - Storage e Metadata**
```python
# ✅ ADICIONAR de SettingsManager:
+ get_available_embeddings()    # Gerencia metadata JSONs
+ save_embedding_metadata()     # Salva metadata
+ delete_embedding_metadata()   # Deleta metadata
+ Coordenação com dados reais   # Evita orphaned metadata

# ✅ RESPONSABILIDADES CORRETAS:
- Paths, directory structure
- Analytics, cleanup operations
- Storage coordination
```

##### **🌍 LANGUAGES (LanguagesManager) - Languages Logic Puro**
```python
# ❌ REMOVER (delegar para SettingsManager):
- _ensure_config_exists()       # Copy individual removido

# ✅ RESPONSABILIDADES CORRETAS:  
- Languages.yaml processing
- Guidelines integration
- Language detection e management
```

#### **🔧 7.5.3 Implementação da Refatoração**

##### **STEP 1: Mover Embeddings Management**
- [ ] **MOVER** `SettingsManager.get_available_embeddings()` → `StorageManager`
- [ ] **MOVER** `SettingsManager.save_embedding_metadata()` → `StorageManager`
- [ ] **MOVER** `SettingsManager.delete_embedding_metadata()` → `StorageManager`
- [ ] **ATUALIZAR** `StorageManager.delete_embedding()` para coordenar metadata + dados
- [ ] **REMOVER** `SettingsManager.embeddings_dir` management

##### **STEP 2: Eliminar TRIPLICAÇÃO de Configuration Copy**
- [ ] **REMOVER** `LanguagesManager._ensure_config_exists()` método
- [ ] **REMOVER** `GuidelinesManager._ensure_guidelines_exist()` método
- [ ] **ATUALIZAR** `LanguagesManager._load_config()` para verificar via SettingsManager:
```python
def _load_config(self, force_reload: bool = False) -> LanguagesConfig:
    if not self.languages_file.exists():
        # Delegar para settings manager - garante TODAS as configs
        from config.settings import get_settings_manager
        get_settings_manager()  # Isso copia languages + guidelines + prompts
    # Continue com load normal...
```
- [ ] **ATUALIZAR** `GuidelinesManager.get_guideline()` para verificar via SettingsManager:
```python
def get_guideline(self, language: str) -> Optional[str]:
    # Ensure configs exist via centralized copy
    from config.settings import get_settings_manager
    get_settings_manager()  
    # Continue with normal guideline loading...
```

##### **STEP 3: Consolidar Constants Duplicadas**
- [x] **REMOVER** `BYTES_PER_MB` de `src/config/constants/storage.py`
- [x] **ATUALIZAR** imports em `storage.py` para usar:
```python
from config.constants.system import BYTES_PER_MB
```
- [x] **VERIFICAR** outros locais que possam usar esta constante

##### **STEP 4: Centralizar Path Construction**
- [x] **ATUALIZAR** `LanguagesManager` para usar `StorageManager.path_manager.config_dir`
- [x] **ATUALIZAR** `GuidelinesManager` para usar `StorageManager.path_manager.guidelines_dir`
- [x] **ATUALIZAR** `PromptBuilder` para usar `StorageManager.path_manager.prompts_dir`
- [x] **ATUALIZAR** `SessionLogger` para usar `StorageManager.path_manager.logs_dir`
- [x] **ELIMINAR** todas as construções diretas de `Path(DEFAULT_CONFIG_DIR).expanduser()`

##### **STEP 5: Consolidar Directory Management**  
- [x] **CENTRALIZAR** todos os paths via StorageManager
- [x] **ADICIONAR** `config_dir`, `guidelines_dir`, `prompts_dir` ao StorageManager
- [x] **REMOVER** construção duplicada de paths
- [x] **ATUALIZAR** todos os módulos para usar StorageManager paths centralizados

##### **STEP 6: Mover Guidelines para Config Raiz**
- [x] **MOVER** `src/config/languages/guidelines.py` → `src/config/guidelines.py`
- [x] **ATUALIZAR** imports em todos os arquivos que usam guidelines:
```python
# ANTES:
from config.languages.guidelines import get_guidelines_manager

# DEPOIS:  
from config.guidelines import get_guidelines_manager
```
- [x] **ATUALIZAR** `src/config/__init__.py` para re-exportar guidelines
- [x] **BUSCAR** por todos os imports no codebase e atualizar:
  - [x] `src/commands/config.py` (2 locais)
  - [x] `src/config/languages/manager.py`
  - [x] `src/core/ai/prompt_builder.py` (2 locais)
- [x] **TESTAR** que GuidelinesManager continua funcionando no novo local

##### **STEP 7: Extrair Utils Genéricos de Loading**
- [x] **CRIAR** `src/utils/yaml_loader.py` com classe genérica:
```python
class GenericYAMLLoader:
    def load(self, file_path: Path) -> Dict[str, Any]:
        # YAML loading com error handling genérico
        # Sem lógica específica de configuração
```
- [x] **CRIAR** `src/utils/file_operations.py` com operações genéricas:
```python  
class FileSystemOperations:
    def copy_file(self, source: Path, target: Path) -> bool:
    def list_files(self, directory: Path, pattern: str) -> List[Path]:
    def ensure_directory_exists(self, directory: Path) -> None:
    # File operations genéricas reutilizáveis
```
- [x] **ATUALIZAR** `config/languages/loader.py` para usar utils genéricos:
```python
from utils.yaml_loader import get_yaml_loader
from utils.file_operations import get_file_operations
```
- [x] **MANTER** lógica específica de languages no loader (validação, models, etc.)
- [x] **IMPLEMENTAR** Adapter Pattern para seamless integration

##### **STEP 8: Reorganizar Providers Structure**
- [ ] **PROBLEMA IDENTIFICADO**: `src/config/providers/base.py` mistura responsabilidades:
```python
# ❌ MISTURA: Protocols + Models + Abstract Classes
class ProviderCapabilities:        # → Deveria ser Pydantic model local
class AIProviderProtocol(Protocol): # → OK como protocol  
class BaseProvider(ABC):           # → Desnecessário se temos protocol
```
- [ ] **CRIAR** `src/config/providers/models.py` com modelos locais:
```python
class ProviderCapabilities(BaseModel):
    supports_streaming: bool = False
    supports_function_calling: bool = False
    supports_vision: bool = False
    max_context_window: int = 200000
    max_output_tokens: int = 4000
```
- [ ] **RENOMEAR** `src/config/providers/base.py` → `src/config/providers/protocols.py`
- [ ] **MANTER** apenas `AIProviderProtocol` no arquivo protocols
- [ ] **REMOVER** `BaseProvider` (implementações usam protocol diretamente)
- [ ] **ATUALIZAR** `src/config/providers/claude.py` para:
```python
from .protocols import AIProviderProtocol
from .models import ProviderCapabilities
```
- [ ] **ATUALIZAR** imports em outros arquivos que usam providers

##### **STEP 9: Criar Setup Manager (Separação Final de Responsabilidades)**
- [ ] **PROBLEMA IDENTIFICADO**: `_ensure_all_configs_exist()` não deveria estar no SettingsManager:
```python
# ❌ VIOLAÇÃO SRP: SettingsManager fazendo file operations
SettingsManager._ensure_all_configs_exist()
├── shutil.copy2()        # File operations
├── mkdir()               # Directory creation  
├── file.glob()           # File system access
└── project path logic   # Template resolution
```
- [ ] **CRIAR** `src/config/setup.py` com responsabilidade única de setup:
```python
class SetupManager:
    """Handles initial setup and configuration file copying (SRP)."""
    
    def ensure_all_configs_exist(self) -> None:
        """Central method for ensuring all config files exist."""
        self._ensure_languages_config()
        self._ensure_guidelines_config()  
        self._ensure_prompts_config()
        
    def _ensure_languages_config(self) -> None:
        """Copy languages.yaml from samples/ if missing."""
        
    def _ensure_guidelines_config(self) -> None:
        """Copy guidelines/*.md from samples/ if missing."""
        
    def _ensure_prompts_config(self) -> None:
        """Copy prompts/ structure from samples/ if missing."""

def get_setup_manager() -> SetupManager:
    """Get global setup manager instance."""
```
- [ ] **MOVER** `_ensure_all_configs_exist()` do Settings → Setup
- [ ] **ATUALIZAR** `SettingsManager.get_settings_manager()` para:
```python
def get_settings_manager() -> SettingsManager:
    if _settings_manager is None:
        # Ensure setup is complete first
        from config.setup import get_setup_manager
        get_setup_manager().ensure_all_configs_exist()
        
        _settings_manager = SettingsManager()
        _settings_manager.initialize()  # Only config.json/active.json
    return _settings_manager
```
- [ ] **ATUALIZAR** Languages/Guidelines managers para usar SetupManager:
```python
# Ao invés de chamar get_settings_manager()
from config.setup import get_setup_manager
get_setup_manager().ensure_all_configs_exist()
```
- [ ] **RESULTADO**: Separação perfeita de responsabilidades:
```python
SetupManager    = Initial setup, file copying, templates
SettingsManager = config.json, active.json, application config  
StorageManager  = Storage operations, cleanup, analytics
```

#### **📋 7.5.4 Checklist Detalhado de Refatoração**

##### **🔄 Refatorar SettingsManager**
```python
# ❌ REMOVER métodos (mover para StorageManager):
- [ ] def get_available_embeddings() -> List[EmbeddingInfo]
- [ ] def save_embedding_metadata(self, embedding_info: EmbeddingInfo) -> None  
- [ ] def delete_embedding_metadata(self, embedding_name: str) -> None
- [ ] self.embeddings_dir = self.config_dir / "embeddings"

# ✅ MANTER métodos (config puro):
- [x] def set_claude_api_key()
- [x] def get_prompt_mode() / set_prompt_mode()
- [x] def set_active_embeddings() # Apenas lista de nomes
- [x] def _ensure_all_configs_exist() # Copy centralizado de TUDO

# 🔄 ATUALIZAR métodos:
- [ ] def set_active_embeddings() # Usar StorageManager para validar nomes
```

##### **🔄 Refatorar StorageManager**
```python
# ✅ ADICIONAR métodos (vindo de SettingsManager):
- [ ] def get_available_embeddings() -> List[EmbeddingInfo]
- [ ] def save_embedding_metadata(self, embedding_info: EmbeddingInfo) -> None
- [ ] def delete_embedding_metadata(self, embedding_name: str) -> None

# 🔄 MELHORAR métodos existentes:
- [ ] def delete_embedding() # Coordenar: dados reais + metadata JSON
- [ ] def list_embeddings() # Coordenar com metadata para info completa
- [ ] def embedding_exists() # Verificar dados reais + metadata

# ✅ MANTER métodos (storage puro):
- [x] def get_storage_info() 
- [x] def cleanup_* methods
- [x] path management methods
```

##### **🔄 Refatorar LanguagesManager**
```python
# ❌ REMOVER métodos (copy delegado):
- [ ] def _ensure_config_exists()

# 🔄 ATUALIZAR métodos:
- [ ] def _load_config() # Delegar copy para get_settings_manager()

# ✅ MANTER métodos (languages puro):
- [x] def get_all_languages()
- [x] def get_supported_extensions()
- [x] def get_guidelines_languages()  
```

#### **🧪 7.5.5 Atualizar Integrações**

##### **Arquivos que usam get_available_embeddings:**
- [ ] Buscar por `get_available_embeddings` no codebase
- [ ] Atualizar imports: `from config.settings import` → `from config.storage import`
- [ ] Testar que commands continuam funcionando

##### **Arquivos que usam embedding metadata:**
- [ ] Buscar por `save_embedding_metadata` no codebase
- [ ] Buscar por `delete_embedding_metadata` no codebase
- [ ] Atualizar todos os imports e calls

#### **🧪 7.5.6 Validação da Separação**

##### **Testes de Responsabilidades:**
- [ ] **SettingsManager**: Só gerencia config.json, active.json, API keys
- [ ] **StorageManager**: Só gerencia paths, metadata JSONs, cleanup
- [ ] **LanguagesManager**: Só gerencia languages.yaml, guidelines logic

##### **Testes de Integração:**
- [ ] **Embeddings workflow**: Create → Save metadata → List → Delete (coordenado)
- [ ] **Config workflow**: First run → Copy all configs → Load configs
- [ ] **Commands workflow**: Todos os commands funcionam sem regression

##### **Testes de Coordenação:**
- [ ] Delete embedding: Remove dados reais + metadata (sem orphans)
- [ ] List embeddings: Mostra metadata + status dos dados reais
- [ ] Save embeddings: Metadata sempre consistente com dados

#### **📊 7.5.7 Critérios de Sucesso**

##### **✅ Separação Completa:**
```
CONFIG (SettingsManager):
- Zero gerenciamento de metadata de embeddings  
- Zero paths hardcoded
- Apenas configurações da aplicação

STORAGE (StorageManager):  
- Embeddings metadata consolidado
- Coordenação dados + metadata
- Zero configurações da aplicação

LANGUAGES (LanguagesManager):
- Zero copy de configurações
- Apenas lógica de languages
```

##### **✅ Zero Inconsistências:**
```
- Uma fonte de verdade para embeddings metadata
- Uma fonte de verdade para config copying  
- Uma fonte de verdade para directory paths
- Coordenação perfeita entre dados reais e metadata
```

##### **✅ APIs Mantidas:**
```
- Todos os commands funcionam sem mudanças
- Backwards compatibility 100%
- Performance mantida ou melhorada
```

---

## 🔄 FASE 8: CENTRALIZAR CONFIGURAÇÕES E STORAGE

### **🔍 8.1 Análise de Violações**

**Busca por violações já realizada. Principais violadores identificados:**

#### **📋 8.1.1 Path Hardcoding Violators:**
- [ ] `src/config/guidelines/manager.py` - path construction direto
- [ ] `src/config/languages/manager.py` - path construction direto  
- [ ] `src/core/ai/prompt_builder.py` - path management duplicado
- [ ] `src/utils/session_logger.py` - session paths hardcoded
- [ ] `src/services/ai_service.py` - file operations diretas
- [ ] `src/services/embedding_service.py` - path operations diretas
- [ ] `src/core/embeddings/model_manager.py` - directory creation direta
- [ ] `src/core/embeddings/vector_store.py` - storage path direta

#### **📋 8.1.2 Configuration Access Violators:**
- [ ] Imports diretos de `DEFAULT_CONFIG_DIR` em múltiplos arquivos
- [ ] Construction de `config.json` / `active.json` paths duplicada
- [ ] Directory creation sem usar storage manager
- [ ] Path resolution sem usar settings manager

### **🔄 8.2 Refatorar Guidelines Manager**

- [ ] Atualizar `src/config/guidelines/manager.py`:
  - [ ] Remover path construction direto
  - [ ] Usar `get_settings_manager()` para paths
  - [ ] Usar `get_storage_manager()` para operações de diretório
  - [ ] Eliminar `Path(DEFAULT_CONFIG_DIR).expanduser()` hardcoded

### **🔄 8.3 Refatorar Languages Manager**

- [ ] Atualizar `src/config/languages/manager.py`:
  - [ ] Remover `Path(DEFAULT_CONFIG_DIR).expanduser() / "config"` hardcoded
  - [ ] Usar settings manager para config directory
  - [ ] Usar storage manager para mkdir operations
  - [ ] Centralizar path resolution

### **🔄 8.4 Refatorar Prompt Builder**

- [ ] Atualizar `src/core/ai/prompt_builder.py`:
  - [ ] Remover path construction duplicado
  - [ ] Usar settings manager para prompt paths
  - [ ] Usar storage manager para directory operations
  - [ ] Eliminar `Path(DEFAULT_CONFIG_DIR).expanduser()` hardcoded

### **🔄 8.5 Refatorar Session Logger**

- [ ] Atualizar `src/utils/session_logger.py`:
  - [ ] Usar storage manager para session paths
  - [ ] Remover construction direta de logs directory
  - [ ] Centralizar session storage management

### **🔄 8.6 Refatorar Services**

- [ ] Atualizar `src/services/ai_service.py`:
  - [ ] Usar storage manager para file operations
  - [ ] Remover `output_file.parent.mkdir()` direto
  - [ ] Centralizar file management

- [ ] Atualizar `src/services/embedding_service.py`:
  - [ ] Usar settings/storage managers apropriados
  - [ ] Remover path operations diretas

### **🔄 8.7 Refatorar Core Modules**

- [ ] Atualizar `src/core/embeddings/model_manager.py`:
  - [ ] Usar storage manager para cache directories
  - [ ] Remover `mkdir()` operations diretas
  - [ ] Centralizar cache path management

- [ ] Atualizar `src/core/embeddings/vector_store.py`:
  - [ ] Usar storage manager para database paths
  - [ ] Remover path construction direta

### **🧹 8.8 Cleanup Imports**

- [ ] Remover imports desnecessários de `DEFAULT_CONFIG_DIR`
- [ ] Buscar por imports órfãos de constants após refatoração
- [ ] Verificar que todos os paths usam managers centralizados
- [ ] Eliminar path hardcoding restante

### **🧪 8.9 Validação Centralização**

- [ ] Testar que todos os paths funcionam via managers
- [ ] Verificar que directory creation funciona corretamente
- [ ] Validar que configurações são acessadas centralmente
- [ ] Testar que storage operations funcionam via storage manager

---

## 📊 FASE 9: VALIDAÇÃO FINAL

### **✅ 9.1 Checklist de Qualidade**

- [ ] Todos os imports atualizados
- [ ] Nenhum arquivo órfão
- [ ] APIs públicas mantidas
- [ ] Templates centralizados em samples/
- [ ] Storage em config/ (não mais utils/)
- [ ] Guidelines consolidado em languages/
- [ ] Config models consolidado em models.py
- [ ] **Configurações e storage centralizados**
- [ ] **Zero path hardcoding restante**
- [ ] Zero breaking changes
- [ ] Documentação atualizada

### **📈 9.2 Benchmarks**

- [ ] Performance de inicialização mantida
- [ ] Cópia de templates eficiente
- [ ] Memory usage estável
- [ ] File structure limpa e organizada
- [ ] **Path resolution eficiente via managers**

### **🏗️ 9.3 Arquitetura Final**

Verificar que a estrutura final está como planejado:

```
src/config/
├── models.py               # ✅ NEW: Consolidated config models
├── storage.py              # ✅ Moved from utils/ + used everywhere
├── settings.py             # ✅ Uses models.py + used everywhere
├── samples/                # ✅ NEW: Centralized templates
│   ├── README.md           # ✅ Documentation
│   ├── languages.yaml      # ✅ Language configuration template
│   ├── languages-README.md # ✅ Languages documentation
│   ├── guidelines/         # ✅ Guidelines templates
│   │   ├── javascript.md   
│   │   ├── python.md
│   │   ├── typescript.md
│   │   └── ...
│   └── prompts/            # ✅ Prompt templates (plural!)
│       ├── global_instructions.md
│       ├── security_instructions.md
│       ├── comprehensive/
│       ├── standard/
│       ├── minimal/
│       └── strict/
├── languages/              # ✅ Consolidated language management
│   ├── __init__.py         # ✅ Exports both managers
│   ├── manager.py          # ✅ Uses settings/storage managers
│   ├── loader.py           # ✅ Uses settings/storage managers
│   ├── models.py           # ✅ Language-specific models
│   └── guidelines.py       # ✅ Uses settings/storage managers
├── constants/              # ✅ Unchanged
└── providers/              # ✅ Unchanged (no models needed)
```

### **🎯 9.4 Princípios Aplicados**

- [ ] **Single Responsibility**: Cada manager tem responsabilidade única
- [ ] **DRY**: Zero duplicação de path/config logic
- [ ] **Centralization**: Todos os acessos via managers centralizados
- [ ] **Consistency**: Padrão uniforme em todo o codebase

### **🔍 9.5 Busca Final por Violações**

**Após todas as refatorações, fazer busca completa para garantir centralização total:**

#### **📋 9.5.1 Buscas Específicas Direcionadas:**
- [ ] Buscar por `Path(.*\.context-ai` - verificar hardcoding restante
- [ ] Buscar por `DEFAULT_CONFIG_DIR` - validar uso apenas em constants e managers
- [ ] Buscar por `config\.json|active\.json` - garantir que só managers acessam
- [ ] Buscar por `\.mkdir\(|\.expanduser\(\)` - verificar operações diretas
- [ ] Buscar por `pathlib|Path\(` - validar se todos usam managers
- [ ] Buscar por `~/.context-ai` hardcoded - eliminar qualquer restante

#### **🤖 9.5.2 Busca Inteligente e Criativa pela IA:**
- [ ] **TAREFA PARA IA:** Analisar TODO o codebase de forma criativa e inteligente procurando por:
  - [ ] Patterns de configuração não cobertos pelas buscas específicas
  - [ ] Operações de arquivo/diretório que podem estar violando centralização
  - [ ] Imports suspeitos relacionados a config/storage/paths
  - [ ] Hardcoding de paths ou configurações não detectado pelas regex
  - [ ] Duplicação de lógica de configuração em locais inesperados
  - [ ] Violações sutis do princípio de centralização
  - [ ] Qualquer coisa relacionada a configuração que pareça suspeita

**🎯 INSTRUÇÕES PARA A IA:**
> Use sua inteligência para encontrar violações que as buscas regex específicas podem ter perdido. 
> Seja criativa e pense em padrões não óbvios. Analise imports, lógica de negócio, 
> operações de arquivo, e qualquer coisa que possa estar duplicando responsabilidades 
> de config/storage sem usar os managers centralizados.

**📋 Documentar achados da busca final:**
```
[ Documentar aqui qualquer violação encontrada nas buscas ]

BUSCAS ESPECÍFICAS:
❌ ENCONTRADO: src/core/some_file.py - linha 25: Path("~/.context-ai").expanduser()
✅ AÇÃO: Refatorar para usar get_settings_manager().config_dir
✅ STATUS: Corrigido

BUSCA INTELIGENTE DA IA:
❌ ENCONTRADO: [exemplo de padrão não óbvio encontrado pela IA]
✅ AÇÃO: [ação corretiva]
✅ STATUS: [status]

Se NENHUMA violação encontrada:
✅ PERFEITO: Zero violações restantes - centralização 100% completa!
```

**🎯 Critério de Sucesso:** Tanto buscas específicas quanto análise da IA devem retornar ZERO violações de config/storage

---

## 🐛 ISSUES ENCONTRADAS

### **Durante Desenvolvimento:**
```
[ Documentar problemas aqui conforme aparecerem ]

Exemplo:
- Issue: Import circular entre languages/guidelines.py e languages/manager.py
- Solução: Mover import para dentro da função
- Status: ✅ Resolvido
```

### **Durante Testes:**
```
✅ Issue: Template file warnings nos testes
- Sintoma: "Template file not found: languages.yaml", "Template file not found: README.md"
- Causa: Arquivos removidos conforme planejado mas loaders ainda buscam na localização antiga
- Impacto: Apenas warnings, funcionalidade OK
- Status: 🟡 Minor - requer atualização de paths nos managers (FASE 3.3)

✅ Issue: "No templates found to copy" no guidelines
- Sintoma: Guidelines manager reporta "No templates found to copy"
- Causa: Templates já copiados para samples/ conforme planejado
- Impacto: Apenas warning, funcionalidade OK
- Status: 🟡 Minor - paths corretos precisam ser configurados
```

---

## 📋 CHECKLIST FINAL

- [x] **FASE 1:** Setup e análise completos
- [x] **FASE 2:** Storage migrado para config/
- [x] **FASE 3:** Samples estrutura criada
- [x] **FASE 4:** Guidelines consolidado em languages/
- [x] **FASE 5:** Cleanup e reorganização
- [ ] **FASE 6:** Testes completos passando
- [x] **FASE 7:** Config models consolidado
- [ ] **FASE 8:** Configurações e storage centralizados
- [ ] **FASE 9:** Validação final OK

### **🎯 ENTREGÁVEL FINAL:**
```
✅ Storage em src/config/storage.py (não mais utils/)
✅ Templates centralizados em src/config/samples/
✅ Guidelines consolidado em src/config/languages/guidelines.py
✅ Config models consolidado em src/config/models.py
✅ Configurações e storage 100% centralizados
✅ Zero path hardcoding no codebase
✅ Estrutura de config limpa e lógica  
✅ Zero breaking changes nas APIs
✅ Testes completos passando
✅ Documentação atualizada
```

---

## 🚀 PRÓXIMOS PASSOS

Após conclusão deste plano:

1. **Documentar a nova arquitetura** em README.md
2. **Criar guia de migração** para usuários (se necessário)
3. **Considerar** automatizar validação de templates
4. **Avaliar** outras melhorias de configuração

**🎯 Ready to start? Toggle to Act mode quando quiser começar a implementação!**
