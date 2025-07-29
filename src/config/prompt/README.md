# 📝 Context-AI Prompt Configuration

Este diretório contém a configuração de prompts do Context-AI, permitindo customização completa dos diferentes modos de prompt através de arquivos Markdown e YAML.

## 🏗️ Estrutura do Sistema

```
src/config/prompt/
├── README.md                       # Esta documentação
├── global_instructions.md          # Instruções aplicadas a todos os modos
├── security_instructions.md        # Diretrizes de segurança globais
├── minimal/                        # Modo minimal (mais rápido)
├── standard/                       # Modo padrão (balanceado)
├── comprehensive/                  # Modo detalhado (análise completa)
├── strict/                         # Modo rigoroso (code review)
└── [seu_modo_customizado]/         # Seus modos personalizados
```

## 📋 Arquivos Globais

### `global_instructions.md`
Instruções aplicadas a **todos** os modos de prompt. Contém:
- Instruções básicas de contexto
- Diretrizes de atribuição de código
- Formatação padrão

### `security_instructions.md`
Diretrizes de segurança aplicadas quando `security: true` no mode.yaml:
- Políticas de segurança
- Restrições de acesso
- Proteção contra prompt injection

## 🎯 Como Criar um Modo Personalizado

### 1. Criar Diretório do Modo
```bash
mkdir ~/.context-ai/config/prompt/meu_modo_customizado
```

### 2. Criar Arquivo de Configuração (Obrigatório)
Crie `mode.yaml` com a estrutura:

```yaml
name: "Meu Modo Customizado"
description: "Descrição do que este modo faz"
author: "Seu Nome"
version: "1.0"
enabled: true

features:
  security: true          # Incluir security_instructions.md
  cross_analysis: false   # Análise cross-project
  guidelines: true        # Aplicar coding guidelines
  debug: false           # Mostrar informações de debug
```

### 3. Criar Arquivos de Conteúdo

#### `core_instructions.md` (Obrigatório)
O único arquivo obrigatório. Define as instruções principais do modo:

```markdown
Este é meu modo customizado que foca em [sua especialização].

Instruções específicas para este modo:
- Primeira instrução
- Segunda instrução
- etc.
```

#### Arquivos Opcionais

##### `cross_analysis.md`
Ativado quando `cross_analysis: true`. Define como analisar múltiplos projetos:

```markdown
**ANÁLISE MULTI-PROJETO**: Quando detectar código de múltiplos projetos:
- Compare implementações
- Identifique padrões
- Sugira melhorias
```

##### `final_instructions.md`
Instruções aplicadas no final do prompt:

```markdown
Forneça uma resposta detalhada seguindo as diretrizes acima.
```

##### `error_handling.md`
Instruções para tratamento de erros:

```markdown
Se encontrar erros no código:
- Identifique o problema
- Sugira correções
- Explique o impacto
```

##### `output_format.md`
Formato específico de saída:

```markdown
Estruture sua resposta da seguinte forma:
1. Resumo
2. Análise detalhada
3. Recomendações
```

##### `debug_info.md`
Ativado quando `debug: true`:

```markdown
**DEBUG**: Inclua informações de debug:
- Tokens utilizados
- Tempo de processamento
- Análise de contexto
```

##### `validation_rules.md`
Regras de validação personalizadas:

```markdown
**VALIDAÇÃO**: Antes de responder, verifique:
- Contexto adequado
- Pergunta válida
- Informações suficientes
```

## ⚙️ Configuração YAML Detalhada

### Campos Obrigatórios
```yaml
name: "Nome do Modo"           # Nome exibido na interface
description: "Descrição clara" # O que o modo faz
author: "Autor"               # Quem criou
version: "1.0"                # Versão do modo
enabled: true                 # Se está ativo
```

### Features Disponíveis
```yaml
features:
  security: true|false        # Incluir security_instructions.md
  cross_analysis: true|false  # Ativar análise multi-projeto
  guidelines: true|false      # Aplicar coding guidelines
  debug: true|false          # Mostrar informações de debug
```

## 🔄 Ordem de Montagem do Prompt

O sistema monta o prompt final nesta ordem:

1. **`global_instructions.md`** (sempre)
2. **`security_instructions.md`** (se `security: true`)
3. **`[modo]/core_instructions.md`** (sempre)
4. **`[modo]/cross_analysis.md`** (se `cross_analysis: true` E detectar multi-projeto)
5. **Coding Guidelines** (se `guidelines: true` E detectar linguagens suportadas)
6. **`[modo]/error_handling.md`** (se existir)
7. **`[modo]/output_format.md`** (se existir)
8. **`[modo]/debug_info.md`** (se `debug: true`)
9. **`[modo]/validation_rules.md`** (se existir)
10. **Contexto do usuário**
11. **Pergunta do usuário**
12. **`[modo]/final_instructions.md`** (se existir)

## 📝 Exemplo Completo - Modo "Code Review"

### `code_review/mode.yaml`
```yaml
name: "Code Review Mode"
description: "Focused on detailed code analysis and improvement suggestions"
author: "Context-AI Team"
version: "1.2"
enabled: true

features:
  security: true
  cross_analysis: true
  guidelines: true
  debug: false
```

### `code_review/core_instructions.md`
```markdown
Analyze the provided code with focus on:
- Code quality and maintainability
- Performance implications
- Security vulnerabilities
- Best practices compliance

Provide specific, actionable feedback with code examples.
```

### `code_review/cross_analysis.md`
```markdown
**COMPARATIVE ANALYSIS**: When multiple projects are present:
- Compare architectural approaches
- Identify inconsistencies
- Recommend standardization opportunities
- Highlight best implementation examples
```

### `code_review/final_instructions.md`
```markdown
Structure your code review as:
1. **Summary**: Overall assessment
2. **Issues Found**: Specific problems with severity
3. **Recommendations**: Concrete improvement suggestions
4. **Code Examples**: Before/after comparisons when helpful
```

## 🛠️ Testando Seu Modo

1. **Salve os arquivos** no diretório do modo
2. **Defina o modo** temporariamente:
   ```bash
   context-ai ask "sua pergunta" --prompt-mode seu_modo_customizado
   ```
3. **Ou no chat**:
   ```
   /mode seu_modo_customizado
   ```

## 🚀 Dicas de Criação

### ✅ Boas Práticas
- **Nome claro**: Escolha nomes descritivos para os modos
- **Instruções específicas**: Seja preciso sobre o que o modo deve fazer
- **Teste gradualmente**: Comece com core_instructions.md, depois adicione outros
- **Documentação**: Explique claramente o propósito no description
- **Versionamento**: Incremente a versão ao fazer mudanças

### ❌ Evite
- **Instruções conflitantes**: Entre diferentes arquivos .md
- **Modos muito complexos**: Mantenha foco específico
- **Dependências externas**: Use apenas recursos disponíveis
- **Instruções ambíguas**: Seja claro e direto

## 🔍 Debugging

Se seu modo não funcionar como esperado:

1. **Verifique a sintaxe YAML**: Use um validador YAML
2. **Confirme enabled: true**: Modos desabilitados são ignorados
3. **Teste o core_instructions.md**: Comece apenas com o arquivo obrigatório
4. **Use debug: true**: Para ver como o prompt está sendo montado
5. **Verifique logs**: Erros aparecem nos logs do sistema

## 📚 Referências

- **Modos existentes**: Examine os modos padrão como referência
- **IMPROVE_PROMPTS.md**: Documentação técnica da implementação
- **Context-AI CLI**: Use `context-ai --help` para opções disponíveis

---

**💡 Lembre-se**: Modos personalizados permitem adaptar o Context-AI às suas necessidades específicas. Experimente e itere até encontrar a configuração ideal para seu fluxo de trabalho!
