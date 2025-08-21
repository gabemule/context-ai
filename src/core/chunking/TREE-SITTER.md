# Tree-sitter Provider Implementation

> **Objetivo**: Implementar TreeSitterChunker como provider adicional para o sistema de chunking registry existente

---

## 🎯 CONTEXTO

### **Infraestrutura Existente**
O sistema já possui ChunkingRegistry implementado (conforme `03_PLAN_CORE_REFACTOR.md`) com:
- Factory pattern para providers de chunking
- ChunkerProtocol interface bem definida
- LangChainChunker como provider principal
- Sistema de configuração e fallback

### **Objetivo: Novo Provider Tree-sitter**
Implementar `TreeSitterChunker` como provider adicional que oferece:
- **Parsing Real**: AST (Abstract Syntax Tree) ao invés de regex
- **Chunking Estrutural**: Preserva estrutura completa de funções/classes/módulos
- **Metadados Ricos**: Nome de funções, parâmetros, tipos, dependências
- **40+ Linguagens**: JavaScript, Python, Go, Rust, Java, C++, PHP, etc.
- **Contexto Preservado**: Mantém imports, comentários e dependências relevantes

### **Vantagens vs LangChain**
- **Precisão**: Nunca quebra código no meio de blocos
- **Contexto**: Entende estrutura real do código
- **Metadados**: Extrai informações semânticas automaticamente
- **Linguagens**: Suporte nativo para mais linguagens
- **Qualidade**: Chunks mais significativos para embedding

---

## 🏗️ ARQUITETURA DO PROVIDER

### **Estrutura de Arquivos**
```
src/core/chunking/
├── __init__.py              # Exports principais (existente)
├── protocol.py              # ChunkerProtocol (existente)
├── registry.py              # ChunkingRegistry (existente)
├── langchain_adapter.py     # LangChainChunker (existente)
└── treesitter_adapter.py    # 🆕 TreeSitterChunker (este provider)
```

### **Design Pattern**
TreeSitterChunker implementa ChunkerProtocol e se integra ao registry existente:
```python
# O registry já existe e apenas registrará o novo provider
registry = get_chunking_registry()
registry.register_provider("treesitter", TreeSitterChunker)
```

---

## 📋 IMPLEMENTAÇÃO DO TREE-SITTER PROVIDER

### **1. Dependências Necessárias**

#### **A. Atualizar pyproject.toml**
```toml
# Adicionar às dependencies existentes
tree-sitter = "^0.20.0"
tree-sitter-python = "^0.20.0"
tree-sitter-javascript = "^0.20.0"
tree-sitter-typescript = "^0.20.0"
tree-sitter-go = "^0.20.0"
tree-sitter-java = "^0.20.0"
tree-sitter-rust = "^0.20.0"
tree-sitter-cpp = "^0.20.0"
tree-sitter-php = "^0.20.0"
tree-sitter-ruby = "^0.20.0"
# Adicionar mais conforme necessário
```

### **2. Implementar treesitter_adapter.py**

#### **A. Estrutura Principal**
```python
import tree_sitter
from tree_sitter import Language, Parser
from typing import Dict, List, Optional, Set
import logging
from pathlib import Path

from .protocol import ChunkerProtocol, ChunkingStrategy, TextChunk
from ..utils.file_operations import detect_language

class TreeSitterChunker(ChunkerProtocol):
    """Tree-sitter based chunker with AST parsing"""
    
    def __init__(self, strategy: Optional[ChunkingStrategy] = None):
        self.strategy = strategy or ChunkingStrategy()
        self.parsers: Dict[str, Parser] = {}
        self.languages: Dict[str, Language] = {}
        self._load_available_parsers()
        
    def chunk_text(self, text: str, file_path: str) -> List[TextChunk]:
        """Main chunking method using Tree-sitter AST parsing"""
        try:
            language = detect_language(file_path)
            parser = self._get_parser_for_language(language)
            
            if not parser:
                raise ValueError(f"No Tree-sitter parser available for {language}")
                
            return self._chunk_with_treesitter(text, file_path, parser, language)
            
        except Exception as e:
            logging.error(f"Tree-sitter chunking failed for {file_path}: {e}")
            raise  # Let registry handle fallback
    
    def chunk_directory(self, directory_path: str) -> List[TextChunk]:
        """Chunk entire directory with Tree-sitter"""
        # Implementation similar to LangChain adapter but using Tree-sitter
        pass
    
    def get_supported_languages(self) -> Set[str]:
        """Return set of languages supported by loaded Tree-sitter grammars"""
        return set(self.parsers.keys())
```

#### **B. Parser Management**
```python
def _load_available_parsers(self):
    """Load all available Tree-sitter parsers"""
    parser_configs = {
        'python': 'tree_sitter_python',
        'javascript': 'tree_sitter_javascript', 
        'typescript': 'tree_sitter_typescript',
        'go': 'tree_sitter_go',
        'java': 'tree_sitter_java',
        'rust': 'tree_sitter_rust',
        'cpp': 'tree_sitter_cpp',
        'c': 'tree_sitter_c',
        'php': 'tree_sitter_php',
        'ruby': 'tree_sitter_ruby',
        # Adicionar mais linguagens
    }
    
    for lang, module_name in parser_configs.items():
        try:
            # Dynamic import of Tree-sitter language
            module = __import__(module_name)
            language = Language(module.language(), lang)
            parser = Parser()
            parser.set_language(language)
            
            self.languages[lang] = language
            self.parsers[lang] = parser
            logging.info(f"Loaded Tree-sitter parser for {lang}")
            
        except ImportError:
            logging.warning(f"Tree-sitter parser for {lang} not available")
        except Exception as e:
            logging.error(f"Failed to load Tree-sitter parser for {lang}: {e}")

def _get_parser_for_language(self, language: str) -> Optional[Parser]:
    """Get appropriate parser for language"""
    # Direct match
    if language in self.parsers:
        return self.parsers[language]
    
    # Language aliases and fallbacks
    language_aliases = {
        'py': 'python',
        'js': 'javascript', 
        'ts': 'typescript',
        'jsx': 'javascript',
        'tsx': 'typescript',
        'cc': 'cpp',
        'cxx': 'cpp',
        'c++': 'cpp',
        'hpp': 'cpp',
        'h': 'c',
    }
    
    alias = language_aliases.get(language.lower())
    if alias and alias in self.parsers:
        return self.parsers[alias]
        
    return None
```

#### **C. Core Chunking Logic**
```python
def _chunk_with_treesitter(self, text: str, file_path: str, parser: Parser, language: str) -> List[TextChunk]:
    """Main Tree-sitter chunking logic"""
    source_bytes = text.encode('utf8')
    tree = parser.parse(source_bytes)
    root_node = tree.root_node
    
    chunks = []
    
    # Extract top-level constructs
    for child in root_node.children:
        chunk = self._create_chunk_from_node(child, source_bytes, file_path, language)
        if chunk:
            chunks.append(chunk)
    
    # Handle imports and module-level comments separately
    imports_chunk = self._extract_imports_and_comments(root_node, source_bytes, file_path, language)
    if imports_chunk:
        chunks.insert(0, imports_chunk)  # Imports first
    
    return chunks

def _create_chunk_from_node(self, node, source_bytes: bytes, file_path: str, language: str) -> Optional[TextChunk]:
    """Create TextChunk from Tree-sitter AST node"""
    
    # Skip certain node types
    skip_types = {'comment', 'import_statement', 'from_import_statement'}
    if node.type in skip_types:
        return None
        
    # Extract node text
    start_byte = node.start_byte
    end_byte = node.end_byte
    node_text = source_bytes[start_byte:end_byte].decode('utf8')
    
    # Extract metadata based on node type
    metadata = self._extract_node_metadata(node, source_bytes, language)
    
    # Apply size limits from strategy
    if len(node_text) > self.strategy.max_chunk_size:
        return self._split_large_node(node, source_bytes, file_path, language)
    
    return TextChunk(
        content=node_text,
        file_path=file_path,
        start_line=node.start_point[0] + 1,
        end_line=node.end_point[0] + 1,
        metadata=metadata
    )
```

#### **D. Metadata Extraction**
```python
def _extract_node_metadata(self, node, source_bytes: bytes, language: str) -> Dict:
    """Extract rich metadata from AST node"""
    metadata = {
        'node_type': node.type,
        'language': language,
        'start_line': node.start_point[0] + 1,
        'end_line': node.end_point[0] + 1,
        'byte_range': [node.start_byte, node.end_byte]
    }
    
    # Function-specific metadata
    if node.type in {'function_definition', 'method_definition', 'function_declaration'}:
        metadata.update(self._extract_function_metadata(node, source_bytes))
    
    # Class-specific metadata  
    elif node.type in {'class_definition', 'class_declaration', 'interface_declaration'}:
        metadata.update(self._extract_class_metadata(node, source_bytes))
        
    # Module/namespace metadata
    elif node.type in {'module', 'namespace_definition', 'package_declaration'}:
        metadata.update(self._extract_module_metadata(node, source_bytes))
    
    return metadata

def _extract_function_metadata(self, node, source_bytes: bytes) -> Dict:
    """Extract function-specific metadata"""
    metadata = {}
    
    # Function name
    name_node = node.child_by_field_name('name')
    if name_node:
        metadata['function_name'] = source_bytes[name_node.start_byte:name_node.end_byte].decode('utf8')
    
    # Parameters
    params_node = node.child_by_field_name('parameters')
    if params_node:
        metadata['parameters'] = self._extract_parameters(params_node, source_bytes)
    
    # Return type (if available)
    return_type_node = node.child_by_field_name('return_type')
    if return_type_node:
        metadata['return_type'] = source_bytes[return_type_node.start_byte:return_type_node.end_byte].decode('utf8')
    
    # Decorators (Python)
    decorators = []
    for child in node.children:
        if child.type == 'decorator':
            decorator_text = source_bytes[child.start_byte:child.end_byte].decode('utf8')
            decorators.append(decorator_text)
    metadata['decorators'] = decorators
    
    return metadata

def _extract_class_metadata(self, node, source_bytes: bytes) -> Dict:
    """Extract class-specific metadata"""
    metadata = {}
    
    # Class name
    name_node = node.child_by_field_name('name')
    if name_node:
        metadata['class_name'] = source_bytes[name_node.start_byte:name_node.end_byte].decode('utf8')
    
    # Inheritance
    superclasses_node = node.child_by_field_name('superclasses')
    if superclasses_node:
        metadata['inherits_from'] = source_bytes[superclasses_node.start_byte:superclasses_node.end_byte].decode('utf8')
    
    # Methods count
    methods = [child for child in node.children if child.type in {'method_definition', 'function_definition'}]
    metadata['methods_count'] = len(methods)
    
    return metadata
```

#### **E. Import and Context Handling**
```python
def _extract_imports_and_comments(self, root_node, source_bytes: bytes, file_path: str, language: str) -> Optional[TextChunk]:
    """Extract imports and module-level comments as context"""
    
    imports_and_comments = []
    
    for child in root_node.children:
        if child.type in {'import_statement', 'from_import_statement', 'import_declaration', 
                         'package_declaration', 'comment', 'module_comment'}:
            node_text = source_bytes[child.start_byte:child.end_byte].decode('utf8')
            imports_and_comments.append(node_text)
    
    if not imports_and_comments:
        return None
        
    content = '\n'.join(imports_and_comments)
    
    return TextChunk(
        content=content,
        file_path=file_path,
        start_line=1,
        end_line=len(imports_and_comments),
        metadata={
            'chunk_type': 'imports_and_context',
            'language': language,
            'imports_count': len([c for c in imports_and_comments if 'import' in c])
        }
    )

def _split_large_node(self, node, source_bytes: bytes, file_path: str, language: str) -> List[TextChunk]:
    """Split large nodes (like big classes) into smaller chunks"""
    
    chunks = []
    current_chunk_nodes = []
    current_size = 0
    
    for child in node.children:
        child_size = child.end_byte - child.start_byte
        
        if current_size + child_size > self.strategy.max_chunk_size and current_chunk_nodes:
            # Create chunk from accumulated nodes
            chunk = self._create_chunk_from_nodes(current_chunk_nodes, source_bytes, file_path, language)
            if chunk:
                chunks.append(chunk)
            
            current_chunk_nodes = [child]
            current_size = child_size
        else:
            current_chunk_nodes.append(child)
            current_size += child_size
    
    # Handle remaining nodes
    if current_chunk_nodes:
        chunk = self._create_chunk_from_nodes(current_chunk_nodes, source_bytes, file_path, language)
        if chunk:
            chunks.append(chunk)
    
    return chunks
```

---

## 🔧 INTEGRAÇÃO COM O REGISTRY

### **Registro Automático**
```python
# src/core/chunking/__init__.py - adicionar ao final
# Auto-register Tree-sitter provider if available
def _register_treesitter_provider():
    """Register TreeSitterChunker if Tree-sitter is available"""
    try:
        from .treesitter_adapter import TreeSitterChunker
        registry = get_chunking_registry()
        registry.register_provider("treesitter", TreeSitterChunker)
        logging.info("Tree-sitter provider registered successfully")
        return True
    except ImportError:
        logging.warning("Tree-sitter not available, provider not registered")
        return False

# Call during module initialization
_register_treesitter_provider()
```

### **Provider Selection Logic**
O sistema de registry já existente escolherá automaticamente Tree-sitter para linguagens suportadas:
```python
# Exemplo de uso (já funciona com registry existente)
registry = get_chunking_registry()

# Auto-seleção - escolherá Tree-sitter se disponível para Python
chunker = registry.get_optimal_chunker(language="python")

# Força Tree-sitter especificamente
chunker = registry.get_chunker("treesitter")
```

---

## 🧪 TESTES

### **Estrutura de Testes**
```
tests/core/chunking/
├── test_treesitter_adapter.py      # Testes unitários TreeSitterChunker
├── test_treesitter_languages.py    # Testes por linguagem
├── test_treesitter_metadata.py     # Testes de metadata extraction
└── test_treesitter_integration.py  # Testes de integração com registry
```

### **Exemplo de Teste**
```python
# tests/core/chunking/test_treesitter_adapter.py
import pytest
from src.core.chunking.treesitter_adapter import TreeSitterChunker
from src.core.chunking.protocol import ChunkingStrategy

class TestTreeSitterChunker:
    
    def test_python_function_chunking(self):
        """Test chunking Python functions with Tree-sitter"""
        chunker = TreeSitterChunker()
        
        python_code = '''
import math

def calculate_area(radius):
    """Calculate circle area"""
    return math.pi * radius ** 2

class Circle:
    def __init__(self, radius):
        self.radius = radius
        '''
        
        chunks = chunker.chunk_text(python_code, "test.py")
        
        # Should have imports, function, and class as separate chunks
        assert len(chunks) == 3
        
        # Check function chunk
        func_chunk = next(c for c in chunks if 'calculate_area' in c.content)
        assert func_chunk.metadata['function_name'] == 'calculate_area'
        assert func_chunk.metadata['parameters'] == ['radius']
        
    def test_unsupported_language_raises_error(self):
        """Test that unsupported languages raise appropriate error"""
        chunker = TreeSitterChunker()
        
        with pytest.raises(ValueError, match="No Tree-sitter parser available"):
            chunker.chunk_text("some content", "test.unsupported")
```

---

## 📊 BENCHMARKS & PERFORMANCE

### **Performance Targets**
- **Chunking Speed**: < 100ms para arquivos < 10KB
- **Memory Usage**: < 50MB para arquivos < 1MB
- **Accuracy**: > 95% de chunks preservando estrutura correta

### **Benchmark Script**
```python
# scripts/benchmark_treesitter.py
import time
import memory_profiler
from src.core.chunking import get_chunking_registry

def benchmark_chunking_providers():
    """Compare Tree-sitter vs LangChain performance"""
    
    registry = get_chunking_registry()
    treesitter_chunker = registry.get_chunker("treesitter")
    langchain_chunker = registry.get_chunker("langchain")
    
    # Test files por linguagem
    test_files = {
        "python": "large_python_file.py",
        "javascript": "large_js_file.js", 
        "go": "large_go_file.go"
    }
    
    results = {}
    
    for language, file_path in test_files.items():
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Benchmark Tree-sitter
        start_time = time.time()
        ts_chunks = treesitter_chunker.chunk_text(content, file_path)
        ts_time = time.time() - start_time
        
        # Benchmark LangChain
        start_time = time.time() 
        lc_chunks = langchain_chunker.chunk_text(content, file_path)
        lc_time = time.time() - start_time
        
        results[language] = {
            "treesitter": {"time": ts_time, "chunks": len(ts_chunks)},
            "langchain": {"time": lc_time, "chunks": len(lc_chunks)}
        }
    
    return results
```

---

## 🚀 PLANO DE IMPLEMENTAÇÃO

### **FASE 1: Core Implementation (3-4 dias)**
- [ ] Implementar TreeSitterChunker básico
- [ ] Suporte para Python e JavaScript
- [ ] Integração com registry existente
- [ ] Testes básicos funcionando

### **FASE 2: Language Expansion (2-3 dias)**
- [ ] Adicionar Go, Rust, Java, TypeScript
- [ ] Metadata extraction completa
- [ ] Testes por linguagem
- [ ] Benchmarks vs LangChain

### **FASE 3: Production Features (2-3 dias)**
- [ ] Error handling robusto
- [ ] Performance optimization
- [ ] Large file splitting
- [ ] Complete test coverage

### **FASE 4: Documentation & Polish (1-2 dias)**
- [ ] Documentação completa
- [ ] Usage examples
- [ ] Migration guide
- [ ] Performance benchmarks

---

## ⚙️ CONFIGURAÇÃO

### **Configuração YAML**
O sistema de configuração existente já suporta provider selection:
```yaml
# config/chunking.yaml (já existe no registry system)
chunking:
  provider: "treesitter"  # Registry escolherá Tree-sitter quando possível
  fallback_provider: "langchain"
  
  treesitter:
    max_file_size: 1048576      # 1MB limit
    parse_timeout: 5.0          # timeout para parsing
    include_imports: true       # incluir imports no contexto
    preserve_comments: true     # preservar docstrings
    
  language_preferences:
    python: "treesitter"
    javascript: "treesitter" 
    go: "treesitter"
    rust: "treesitter"
    markdown: "langchain"       # LangChain melhor para markdown
    html: "langchain"           # LangChain melhor para HTML
```

---

## 🔍 TROUBLESHOOTING

### **Problemas Comuns**
1. **Parser not available**: Provider não registrado, fallback para LangChain
2. **Parse timeout**: Arquivo muito grande, usar splitting strategy
3. **Memory usage**: Implementar streaming para arquivos grandes
4. **Invalid syntax**: Tree-sitter é tolerante, mas pode precisar fallback

### **Debug Tools**
```python
# Verificar providers disponíveis
registry = get_chunking_registry()
print(f"Available providers: {registry.get_available_providers()}")

# Verificar linguagens suportadas pelo Tree-sitter
if "treesitter" in registry.get_available_providers():
    ts_chunker = registry.get_chunker("treesitter")
    print(f"Tree-sitter languages: {ts_chunker.get_supported_languages()}")

# Forçar provider para debug
chunker = registry.get_chunker("treesitter")  # Força Tree-sitter
```

---

## ✅ CRITÉRIOS DE ACEITAÇÃO

### **Funcionalidades**
- [ ] TreeSitterChunker implementa ChunkerProtocol corretamente
- [ ] Registry integration funciona sem modificar código existente
- [ ] Suporte para pelo menos 5 linguagens (Python, JS, Go, Rust, Java)
- [ ] Metadata extraction funcional
- [ ] Fallback graceful quando Tree-sitter falha

### **Qualidade**
- [ ] Cobertura de testes > 90%
- [ ] Performance comparable ou melhor que LangChain
- [ ] Zero breaking changes na API existente
- [ ] Documentação e exemplos completos

### **Produção**
- [ ] Error handling robusto
- [ ] Logging adequado
- [ ] Memory usage otimizado
- [ ] Configuração flexível via YAML

---

*Este provider se integra perfeitamente ao sistema de chunking registry existente, oferecendo chunking estrutural avançado como opção adicional sem quebrar compatibilidade.*
