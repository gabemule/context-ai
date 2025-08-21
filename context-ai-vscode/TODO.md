# TODO: Context-AI VSCode Extension Refactoring

## 🎯 Visão Geral
Refatorar o `ChatViewProvider` aplicando princípios DRY, SOLID e Clean Architecture para tornar o código mais escalável, testável e maintível.

## 📋 Problemas Identificados

### ❌ Violações de SOLID
- **SRP**: `ChatViewProvider` tem muitas responsabilidades
- **OCP**: Difícil adicionar novos tipos de panels/comandos
- **DIP**: Dependências hardcoded, sem interfaces

### ❌ Violações de DRY
- Parsing de panels duplicado
- Lógica de cleanup repetida
- Verificações de estado duplicadas

### ❌ Problemas de Arquitetura
- Métodos gigantescos (150+ linhas)
- Comandos especiais não mostram resultado
- Código difícil de testar
- Acoplamento alto

## 🏗️ Estrutura Proposta

```
src/
├── types/
│   └── ChatTypes.ts              # Interfaces e tipos compartilhados
├── services/
│   ├── ProcessManager.ts         # Gerencia processo Context-AI
│   ├── PanelParser.ts           # Parser unificado de panels
│   ├── MessageHandler.ts        # Streaming e handling de mensagens
│   └── CommandHandler.ts        # Handler para comandos especiais
├── utils/
│   └── PlatformDetector.ts      # Detecção de plataforma e comandos
├── shared/
│   ├── logger.ts               # (existente)
│   └── constants.ts            # Constantes compartilhadas
└── chatViewProvider.ts         # Refatorado, mais limpo
```

---

## 📝 CHECKLISTS DE IMPLEMENTAÇÃO

### ✅ 1. ANÁLISE INICIAL
- [x] Analisar código atual e identificar problemas
- [x] Definir estrutura de refatoração
- [x] Criar plano detalhado (este TODO.md)

### 🔲 2. TIPOS E INTERFACES

#### Arquivo: `src/types/ChatTypes.ts`
- [ ] Criar interface `IChatProcess`
- [ ] Criar interface `IPanel` e tipos específicos
- [ ] Criar interface `IMessageHandler`
- [ ] Criar interface `IProcessManager`
- [ ] Criar tipos para comandos especiais
- [ ] Criar tipos para platform detection
- [ ] Documentar todas as interfaces

**Critérios de Aceitação:**
- [ ] Todas as interfaces bem tipadas
- [ ] Documentação TSDoc em todas as interfaces
- [ ] Separação clara entre tipos de domínio e infraestrutura

### 🔲 3. PLATFORM DETECTOR

#### Arquivo: `src/utils/PlatformDetector.ts`
- [ ] Extrair lógica de detecção de plataforma
- [ ] Implementar método `detectPlatform()`
- [ ] Implementar método `getPossibleCommands()`
- [ ] Adicionar suporte para novas plataformas facilmente
- [ ] Adicionar testes unitários

**Critérios de Aceitação:**
- [ ] Windows, macOS, Linux e WSL suportados
- [ ] Fácil adicionar novos paths de comando
- [ ] Classe testável e isolada

### 🔲 4. PANEL PARSER

#### Arquivo: `src/services/PanelParser.ts`
- [ ] Unificar `detectPanel()` e parsing methods
- [ ] Implementar método genérico `extractPanel(content, title)`
- [ ] Criar parsers específicos:
  - [ ] `TokenUsageParser`
  - [ ] `ChatInfoParser`
  - [ ] `EmbeddingsParser` (novo)
  - [ ] `HistoryParser` (novo)
- [ ] Implementar factory pattern para parsers
- [ ] Adicionar validação de panels

**Critérios de Aceitação:**
- [ ] DRY: zero duplicação de parsing logic
- [ ] Fácil adicionar novos tipos de panels
- [ ] Parser retorna dados estruturados
- [ ] Error handling robusto

### 🔲 5. PROCESS MANAGER

#### Arquivo: `src/services/ProcessManager.ts`
- [ ] Extrair toda lógica de processo do ChatViewProvider
- [ ] Implementar métodos:
  - [ ] `initializeProcess()`
  - [ ] `ensureProcessRunning()`
  - [ ] `cleanupProcess()`
  - [ ] `isProcessHealthy()`
- [ ] Implementar fallback logic para comandos
- [ ] Implementar retry mechanism
- [ ] Adicionar process monitoring
- [ ] Implementar graceful shutdown

**Critérios de Aceitação:**
- [ ] Processo isolado em classe própria
- [ ] Fallback de comandos funciona perfeitamente
- [ ] Error recovery robusto
- [ ] Logs estruturados e informativos

### 🔲 6. MESSAGE HANDLER

#### Arquivo: `src/services/MessageHandler.ts`
- [ ] Extrair lógica de streaming do ChatViewProvider
- [ ] Implementar métodos:
  - [ ] `handleStreamStart()`
  - [ ] `handleStreamChunk()`
  - [ ] `handleStreamEnd()`
  - [ ] `handleCommandResponse()` (novo)
- [ ] Implementar command detection
- [ ] Melhorar handling de respostas de comandos especiais
- [ ] Implementar timeout management
- [ ] Adicionar streaming statistics

**Critérios de Aceitação:**
- [ ] Streaming funciona perfeitamente
- [ ] Comandos `/embeddings`, `/history` mostram resultado
- [ ] Timeout management melhorado
- [ ] Error handling consistente

### 🔲 7. COMMAND HANDLER

#### Arquivo: `src/services/CommandHandler.ts`
- [ ] Implementar detecção de comandos especiais:
  - [ ] `/embeddings`
  - [ ] `/history`
  - [ ] `/clear`
  - [ ] `/verbose`
  - [ ] `/mode`
- [ ] Implementar handlers específicos para cada comando
- [ ] Garantir que resultados são exibidos
- [ ] Implementar command validation
- [ ] Adicionar help command

**Critérios de Aceitação:**
- [ ] Todos os comandos especiais funcionam
- [ ] Resultados são exibidos corretamente
- [ ] Fácil adicionar novos comandos
- [ ] Feedback claro para usuário

### 🔲 8. SHARED CONSTANTS

#### Arquivo: `src/shared/constants.ts`
- [ ] Extrair magic strings e números
- [ ] Definir timeouts como constantes
- [ ] Definir markers de streaming
- [ ] Definir mensagens de erro padrão
- [ ] Organizar por categoria

**Critérios de Aceitação:**
- [ ] Zero magic numbers/strings no código
- [ ] Constantes bem organizadas
- [ ] Documentação clara de cada constante

### 🔲 9. REFATORAR CHAT VIEW PROVIDER

#### Arquivo: `src/chatViewProvider.ts`
- [ ] Injetar dependencies via constructor
- [ ] Reduzir classe para orchestration apenas
- [ ] Implementar error boundaries
- [ ] Simplificar métodos para < 20 linhas cada
- [ ] Remover toda lógica de domínio
- [ ] Melhorar separation of concerns

**Critérios de Aceitação:**
- [ ] Classe < 200 linhas total
- [ ] Métodos < 20 linhas cada
- [ ] Zero lógica de domínio na view
- [ ] Dependencies injetadas
- [ ] Error handling centralizado

### 🔲 10. TESTING

#### Estrutura de Testes:
- [ ] `tests/services/ProcessManager.test.ts`
- [ ] `tests/services/PanelParser.test.ts`
- [ ] `tests/services/MessageHandler.test.ts`
- [ ] `tests/services/CommandHandler.test.ts`
- [ ] `tests/utils/PlatformDetector.test.ts`
- [ ] `tests/integration/ChatViewProvider.test.ts`

**Critérios de Aceitação:**
- [ ] Coverage > 90%
- [ ] Unit tests para todas as classes
- [ ] Integration tests para fluxo completo
- [ ] Mock das dependencies externas

### 🔲 11. DOCUMENTAÇÃO

- [ ] Atualizar README.md com nova arquitetura
- [ ] Documentar APIs das novas classes
- [ ] Criar diagramas de arquitetura
- [ ] Documentar padrões utilizados
- [ ] Criar guia de contribuição

### 🔲 12. VALIDAÇÃO FINAL

- [ ] Todas as funcionalidades existentes funcionam
- [ ] Comandos especiais (`/embeddings`, etc.) mostram resultado
- [ ] Performance mantida ou melhorada
- [ ] Logs mais limpos e informativos
- [ ] Extensibilidade demonstrada
- [ ] Code review completo

---

## 🚀 ORDEM DE IMPLEMENTAÇÃO RECOMENDADA

1. **Tipos e Interfaces** → Base para tudo
2. **Constants** → Remove magic strings/numbers
3. **PlatformDetector** → Funcionalidade isolada
4. **PanelParser** → Core functionality, alto reuso
5. **ProcessManager** → Funcionalidade crítica
6. **CommandHandler** → Nova funcionalidade
7. **MessageHandler** → Orquestra tudo
8. **Refatorar ChatViewProvider** → Final cleanup
9. **Tests** → Garantir qualidade
10. **Documentation** → Finalizar

---

## 💡 NOTAS TÉCNICAS

### Padrões a Aplicar
- **Factory Pattern** para parsers
- **Strategy Pattern** para command handlers
- **Observer Pattern** para process monitoring
- **Dependency Injection** para testabilidade

### Princípios SOLID
- **SRP**: Uma responsabilidade por classe
- **OCP**: Fácil extensão sem modificação
- **LSP**: Interfaces bem definidas
- **ISP**: Interfaces específicas e pequenas
- **DIP**: Dependência em abstrações

### Best Practices
- Async/await consistently
- Error handling com types específicos
- Logging estruturado
- Timeout management
- Resource cleanup
- Memory leak prevention

---

## 🎯 RESULTADOS ESPERADOS

### Antes da Refatoração
- ❌ ChatViewProvider: 700+ linhas
- ❌ Métodos com 150+ linhas
- ❌ Duplicação de código
- ❌ Comandos especiais não funcionam
- ❌ Difícil de testar
- ❌ Acoplamento alto

### Depois da Refatoração
- ✅ ChatViewProvider: < 200 linhas
- ✅ Métodos < 20 linhas
- ✅ Zero duplicação
- ✅ Todos os comandos funcionam
- ✅ Testabilidade alta
- ✅ Baixo acoplamento
- ✅ Fácil extensibilidade

---

## 📊 MÉTRICAS DE SUCESSO

- [ ] **Redução de complexidade**: ChatViewProvider < 200 linhas
- [ ] **Cobertura de testes**: > 90%
- [ ] **Duplicação de código**: 0%
- [ ] **Comandos especiais**: 100% funcionais
- [ ] **Performance**: Mantida ou melhorada
- [ ] **Manutenibilidade**: Métrica de complexidade reduzida

---

**Status**: 🏁 Em Progresso
**Última Atualização**: 2025-08-21
**Responsável**: Cline + Barney
