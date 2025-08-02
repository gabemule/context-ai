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
