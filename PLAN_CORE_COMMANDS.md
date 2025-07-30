# 🎯 PLANO: REFATORAÇÃO CORE COMMANDS + COMANDO /CLEAR

## 📋 COMO USAR ESTE PLANO

Este arquivo é nosso **guia de desenvolvimento** para a refatoração do sistema de sessões e implementação do comando `/clear` melhorado.

### **📖 INSTRUÇÕES DE USO:**

1. **Siga a ordem sequencial** - cada fase depende da anterior
2. **Marque os checkboxes** ✅ conforme completar cada item
3. **Teste após cada fase** - valide antes de prosseguir
4. **Documente problemas** na seção "🐛 ISSUES ENCONTRADAS" no final
5. **Não pule etapas** - cada passo tem dependências específicas

### **🔄 FLUXO DE TRABALHO:**
```
FASE 1: Setup → FASE 2: Migração → FASE 3: Refatoração → FASE 4: Feature /clear → FASE 5: Testes
```

### **🎯 OBJETIVO FINAL:**
- ✅ Session management em `src/core/commands/`
- ✅ Separação clara: session handling vs logging  
- ✅ Comando `/clear` funcionando com restart completo de sessão
- ✅ Zero breaking changes nas APIs existentes

---

## 🚀 FASE 1: PREPARAÇÃO E SETUP

### **📁 1.1 Criar Estrutura de Diretórios**

- [ ] Criar diretório `src/core/commands/`
- [ ] Criar arquivo `src/core/commands/__init__.py`
- [ ] Criar arquivo `src/core/commands/handle-session.py`
- [ ] Criar arquivo `src/core/commands/log-manager.py`

### **📊 1.2 Análise de Dependências**

- [ ] Mapear todos os imports de `utils.session_logger` no codebase usando busca
- [ ] Identificar arquivos que precisarão de atualização de imports
- [ ] Documentar APIs públicas que devem ser mantidas

#### **🔍 1.2.1 Busca Real de Ocorrências (fazer durante execução):**

**Buscar por:**
- [ ] `from utils.session_logger import`
- [ ] `import utils.session_logger`
- [ ] `utils.session_logger.`
- [ ] `session_logger.`

**📋 Lista real de arquivos encontrados (atualizar durante busca):**
```
[ Documentar aqui os arquivos reais encontrados durante a busca ]

Exemplo:
✅ src/commands/ask.py - line 15: from utils.session_logger import start_command_session
✅ src/commands/chat.py - line 22: from utils.session_logger import start_command_session, end_command_session
[ ... adicionar conforme encontrado ... ]
```

**📋 APIs públicas em uso (documentar durante busca):**
```
[ Listar as funções/classes realmente usadas no código ]

Exemplo:
✅ start_command_session() - usado em: ask.py, chat.py, query.py
✅ get_current_session() - usado em: ai_service.py, prompt_builder.py
✅ end_command_session() - usado em: ask.py, chat.py, query.py
✅ CommandSession - usado em: ai_service.py
[ ... adicionar conforme encontrado ... ]
```

---

## 🔄 FASE 2: MIGRAÇÃO DE CÓDIGO

### **📦 2.1 Migrar SessionDataManager**

- [ ] Copiar `SessionDataManager` para `log-manager.py`
- [ ] Atualizar documentação da classe
- [ ] Adicionar imports necessários
- [ ] Testar criação de estruturas de dados

### **📦 2.2 Migrar e Renomear FileManager → LogManager**

- [ ] Copiar `FileManager` para `log-manager.py`
- [ ] Renomear classe para `LogManager`
- [ ] Renomear métodos conforme planejado:
  - [ ] `setup_turn_files()` → `setup_turn_logs()`
  - [ ] `save_prompt()` → `save_prompt_log()`
  - [ ] `save_response()` → `save_response_log()`
  - [ ] `save_json()` → `save_session_data()`
  - [ ] `save_query_result()` → `save_query_result_log()`
- [ ] Atualizar documentação dos métodos
- [ ] Atualizar imports necessários

### **📦 2.3 Migrar ChatTurnManager**

- [ ] Copiar `ChatTurnManager` para `handle-session.py`
- [ ] Manter funcionalidade idêntica
- [ ] Atualizar documentação
- [ ] Adicionar imports necessários

### **📦 2.4 Migrar CommandSession**

- [ ] Copiar `CommandSession` para `handle-session.py`
- [ ] Atualizar referências para `LogManager` (ex-FileManager)
- [ ] Atualizar chamadas de métodos renomeados
- [ ] Manter interface pública idêntica
- [ ] Adicionar documentação melhorada (conforme planejado)

---

## 🏗️ FASE 3: IMPLEMENTAR HELPERS E API

### **🔧 3.1 Implementar Helper Functions**

- [ ] Migrar `start_command_session()` para `handle-session.py`
- [ ] Migrar `get_current_session()` para `handle-session.py` 
- [ ] Migrar `end_command_session()` para `handle-session.py`
- [ ] **IMPLEMENTAR NOVO:** `restart_current_session()` em `handle-session.py`

### **📋 3.2 Configurar Public API**

- [ ] Configurar `src/core/commands/__init__.py` com exports corretos
- [ ] Testar imports da nova API
- [ ] Validar que todas as funções estão acessíveis

### **🧪 3.3 Validação Básica**

- [ ] Testar criação de CommandSession
- [ ] Testar start/end session cycle
- [ ] Validar criação de arquivos de log
- [ ] Testar session restart (novo)

---

## 🔄 FASE 4: ATUALIZAR IMPORTS EM TODO CODEBASE

### **🔍 4.1 Validação da Lista de Arquivos (se necessário)**

- [ ] Re-verificar lista de arquivos da seção 1.2.1 se houver dúvidas
- [ ] Buscar por possíveis imports esquecidos
- [ ] Confirmar que todos os arquivos estão identificados

### **📝 4.2 Atualizar Arquivos Identificados**

**Usar a lista real da seção 1.2.1 para atualizar:**

- [ ] Atualizar todos os arquivos listados em 1.2.1
- [ ] Para cada arquivo, substituir:
  - [ ] `from utils.session_logger import` → `from core.commands import`
  - [ ] `import utils.session_logger` → `import core.commands`
  - [ ] `utils.session_logger.` → `core.commands.`
  - [ ] `session_logger.` → verificar contexto e ajustar

### **🧠 4.3 Verificação Adicional**

- [ ] Buscar por imports que podem ter sido esquecidos
- [ ] Verificar outros arquivos em `src/core/` se necessário
- [ ] Verificar arquivos de teste se existirem

### **🧹 4.4 Cleanup**

- [ ] Remover `src/utils/session_logger.py`
- [ ] Verificar se não há imports órfãos
- [ ] Atualizar `src/utils/__init__.py` se necessário

---

## ✨ FASE 5: IMPLEMENTAR FEATURE /CLEAR

### **🔧 5.1 Atualizar ChatCommandHandler**

**Local:** `src/services/ai_service.py`

- [ ] Adicionar import: `from core.commands import restart_current_session`
- [ ] Modificar construtor do `ChatCommandHandler` para aceitar referência do `AIService`
- [ ] Atualizar inicialização no `AIService.__init__()`

### **🗑️ 5.2 Implementar Novo _clear_history()**

- [ ] Implementar nova lógica de `_clear_history()`:
  - [ ] Preservar contagem de turns antigas para logging
  - [ ] Limpar `ChatHistoryManager.history`
  - [ ] Limpar `context_manager._context_cache`
  - [ ] Chamar `restart_current_session()`
  - [ ] Limpar terminal visualmente
  - [ ] Mostrar feedback ao usuário
- [ ] Adicionar método `_clear_terminal()` se não existir
- [ ] Adicionar import `import os` se necessário

### **💬 5.3 Aprimorar Feedback do Usuario**

- [ ] Implementar mensagem de confirmação de restart
- [ ] Mostrar novo session_id para o usuário
- [ ] Incluir contagem de turns que foram limpos

---

## 🧪 FASE 6: TESTES COMPLETOS

### **🔍 6.1 Testes de Migração**

- [ ] Testar comando `ask` - deve funcionar normalmente
- [ ] Testar comando `query` - deve funcionar normalmente  
- [ ] Testar comando `chat` básico - deve funcionar normalmente
- [ ] Verificar criação de arquivos de log em todos os comandos

### **🗑️ 6.2 Testes do /clear**

- [ ] **Cenário 1:** Chat vazio + `/clear`
  - [ ] Não deve dar erro
  - [ ] Deve mostrar mensagem apropriada
- [ ] **Cenário 2:** Chat com 1 turn + `/clear`
  - [ ] Deve limpar histórico
  - [ ] Nova pergunta deve ser turn #1
  - [ ] Session old deve estar finalizada e salva
- [ ] **Cenário 3:** Chat com múltiplos turns + `/clear`
  - [ ] Deve limpar todos os turns
  - [ ] Nova pergunta deve ser turn #1
  - [ ] Deve mostrar contagem de turns limpos
- [ ] **Cenário 4:** `/clear` múltiplo
  - [ ] Múltiplos `/clear` seguidos não devem dar erro
  - [ ] Cada `/clear` deve criar nova sessão

### **📁 6.3 Validação de Arquivos**

- [ ] Verificar estrutura de arquivos de sessão antiga (deve estar completa)
- [ ] Verificar estrutura de arquivos de nova sessão (deve estar limpa)
- [ ] Verificar que session.json da sessão antiga contém todos os turns
- [ ] Verificar que nova sessão começa com turns=[]

### **🔄 6.4 Testes de Integração**

- [ ] Testar fluxo completo: start chat → perguntas → /clear → mais perguntas → exit
- [ ] Verificar que serviços não são recarregados (AI, embeddings permanecem)
- [ ] Verificar performance (restart deve ser rápido)
- [ ] Testar em diferentes modos de prompt

---

## 📊 FASE 7: VALIDAÇÃO FINAL

### **✅ 7.1 Checklist de Qualidade**

- [ ] Todos os imports atualizados
- [ ] Nenhum arquivo órfão
- [ ] APIs públicas mantidas
- [ ] Funcionalidade `/clear` operacional  
- [ ] Zero breaking changes
- [ ] Documentação atualizada

### **📈 7.2 Benchmarks**

- [ ] Tempo de `/clear` < 1 segundo
- [ ] Memory usage estável após restart
- [ ] File structure correta em ambas as sessões
- [ ] Logs completos e analisáveis

---

## 🐛 ISSUES ENCONTRADAS

### **Durante Desenvolvimento:**
```
[ Documentar problemas aqui conforme aparecerem ]

Exemplo:
- Issue: Import circular em handle-session.py
- Solução: Mover import para dentro da função
- Status: ✅ Resolvido
```

### **Durante Testes:**
```
[ Documentar bugs de teste aqui ]

Exemplo:  
- Bug: /clear não limpa cache em modo verbose
- Reprodução: chat --verbose → pergunta → /clear
- Fix: Adicionar limpeza de cache específica para verbose
- Status: ⏳ Em progresso
```

---

## 📋 CHECKLIST FINAL

- [ ] **FASE 1:** Setup completo
- [ ] **FASE 2:** Migração completa  
- [ ] **FASE 3:** API implementada
- [ ] **FASE 4:** Imports atualizados
- [ ] **FASE 5:** Feature /clear implementada
- [ ] **FASE 6:** Testes passando
- [ ] **FASE 7:** Validação final OK

### **🎯 ENTREGÁVEL FINAL:**
```
✅ Estrutura core/commands/ funcionando
✅ Session management refatorado  
✅ Comando /clear com restart de sessão
✅ Zero breaking changes
✅ Testes completos passando
✅ Documentação atualizada
```

---

## 🚀 PRÓXIMOS PASSOS

Após conclusão deste plano:

1. **Documentar a nova arquitetura** em README.md
2. **Criar testes unitários** para core/commands/
3. **Considerar** adicionar métricas de performance para restarts
4. **Avaliar** outras features que poderiam se beneficiar do novo sistema

**🎯 Ready to start? Toggle to Act mode quando quiser começar a implementação!**
