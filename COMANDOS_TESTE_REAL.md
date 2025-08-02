# 🎯 COMANDOS PARA TESTAR A REFATORAÇÃO

Você está certo! Chega de testes Python que tentam usar APIs que não existem. 
Aqui estão os **comandos CLI REAIS** para testar se tudo funciona:

## 🚀 **1. TESTES BÁSICOS:**

```bash
# Verificar se CLI funciona
context-ai --version

# Ver configuração atual
context-ai config list

# Ver ajuda dos novos subcomandos
context-ai config --help
```

## 🔧 **2. TESTES DOS NOVOS SUBCOMANDOS:**

```bash
# Testar config models (novo!)
context-ai config models

# Testar config guidelines (novo!)  
context-ai config guidelines list

# Mostrar guidelines específicas
context-ai config guidelines show python

# Testar config languages (novo!)
context-ai config languages list

# Mostrar linguagem específica
context-ai config languages show python
```

## 💾 **3. TESTES DE STORAGE:**

```bash
# Info do storage
context-ai storage info

# Listar embeddings
context-ai storage list
```

## 🎯 **4. TESTES DE FUNCIONALIDADE CORE:**

```bash
# Se você tem embeddings, testar:
context-ai select

# Query básico (precisa de embeddings ativos)
context-ai query "test query"
```

## 🎉 **5. TESTE FINAL - O MAIS IMPORTANTE:**

Este é o teste que importa de verdade - usar ASK que deve aplicar guidelines automaticamente:

```bash
# TESTE REAL com guidelines aplicadas
context-ai ask "Como posso melhorar este código Python?" --verbose

# Deve mostrar guidelines de Python sendo aplicadas!
```

---

## 📋 **CHECKLIST - MARQUE O QUE FUNCIONA:**

- [ ] `context-ai --version` - CLI básico
- [ ] `context-ai config list` - Config funciona
- [ ] `context-ai config models` - **NOVO SUBCOMANDO**
- [ ] `context-ai config guidelines list` - **NOVO SUBCOMANDO** 
- [ ] `context-ai config languages list` - **NOVO SUBCOMANDO**
- [ ] `context-ai storage info` - Storage funciona
- [ ] `context-ai ask "test"` - Funcionalidade core

---

**🎯 RODA ESSES E ME FALA QUAL QUEBRA!**

O importante é que os **novos subcomandos** (models, guidelines, languages) funcionem e que o `ask` aplique guidelines automaticamente.
