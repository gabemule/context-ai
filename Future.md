# Context-AI - Future Roadmap

> Long-term vision and enhancements beyond MVP

## 🚀 Post-MVP Enhancements

### Performance Optimizations (Short-term)
- [x] **CLI Performance**: Improve startup time from 6s to <1s ✅ **COMPLETED (0.4s)**
  - [x] **Lazy imports optimization**: Move heavy imports to function-level only when needed ✅ **COMPLETED**
    - [x] Moved query command parser definition inline to avoid loading query module during help
    - [x] All command handlers now use lazy imports for heavy dependencies
    - [x] Startup time improved from 6+ seconds to ~0.4 seconds (15x improvement)
  - [ ] **Instance caching**: Cache heavy service instances across CLI commands
  - [ ] **Daemon mode**: Optional background process for instant responses
  - [ ] **Startup profiling**: Detailed analysis of import bottlenecks
  - [ ] **Selective loading**: Only load necessary components per command

### Performance Notes
- **Major Bottleneck Identified**: Top-level imports in CLI parser creation
  - `from commands.query import add_query_parser` was loading the entire query module chain
  - This included heavy dependencies: ChromaDB, sentence-transformers, langchain-text-splitters
  - Solution: Moved query parser definition inline and use lazy imports in handlers
- **Results**: CLI help command now starts in ~0.4s instead of 6+ seconds
- **Next Optimizations**: Command-specific operations (storage, query) still take 5+ seconds due to ChromaDB initialization

### Phase 5: Smart Query Intelligence (Month 2)
- [ ] **Smart Query Balancing**: Intelligent embedding prioritization based on query content
  - [ ] **5.1.1** Implement keyword detection in queries ("sdk", "hub", "auth", etc.)
  - [ ] **5.1.2** Dynamic embedding weight adjustment based on detected keywords
  - [ ] **5.1.3** Smart result distribution (e.g., "sdk" queries get 70% sdk results, 30% hub)
  - [ ] **5.1.4** Query preprocessing to identify project-specific intent
  - [ ] **5.1.5** Configuration options for weight adjustment per embedding
  - **Example Impact**: `"what modules does sdk have?"` → 150+ sdk-v1 results + 100- hub-v1 results (instead of 50 sdk + 200 hub)
- [ ] **Context Relevance Scoring**: Improve result ranking
  - [ ] **5.2.1** Implement query-specific similarity boost factors
  - [ ] **5.2.2** Penalize off-topic results from wrong embeddings
  - [ ] **5.2.3** Boost results that match detected programming languages
  - [ ] **5.2.4** Smart deduplication across similar files

### Phase 6: Simple Multi-Provider Support (Month 3)
- [ ] **OpenAI Integration**: Add GPT-4, GPT-4o as second provider option
  - [ ] **6.1.1** Implement OpenAI API client with basic retry logic
  - [ ] **6.1.2** Add support for key OpenAI models (GPT-4, GPT-4o)
  - [ ] **6.1.3** Simple model selection between Claude and OpenAI
  - [ ] **6.1.4** Basic token counting for OpenAI
- [ ] **Simple Fallback System**: Basic provider fallback
  - [ ] **6.2.1** Implement simple fallback: Claude → OpenAI
  - [ ] **6.2.2** Add basic provider health checking
  - [ ] **6.2.3** Manual provider switching commands
  - [ ] **6.2.4** Basic error handling between providers

### Phase 6: Essential Format Support (Month 3)
- [ ] **Multi-modal Documentation**: Support for common doc formats
  - [ ] **6.1.1** PDF support for documentation files
  - [ ] **6.1.2** Image support (diagrams, screenshots) with OCR
  - [ ] **6.1.3** Basic text extraction from images
  - [ ] **6.1.4** Metadata preservation for multimedia content
- [ ] **Real-time Updates**: Keep embeddings current
  - [ ] **6.2.1** File watching for documentation changes
  - [ ] **6.2.2** Auto-update embeddings on file changes
  - [ ] **6.2.3** Smart incremental updates (only changed files)
  - [ ] **6.2.4** Background processing for large updates

### Phase 7: Advanced Semantic Chunking (Month 4)
- [ ] **Tree-sitter Integration**: Upgrade from LangChain to semantic parsing
  - [ ] **7.1.1** Install Tree-sitter dependencies (python, javascript, typescript)
  - [ ] **7.1.2** Create Tree-sitter adapter module with protocol interface
  - [ ] **7.1.3** Implement JavaScript semantic chunker (functions, classes, exports, imports)
  - [ ] **7.1.4** Implement Python semantic chunker (functions, classes, imports, docstrings)
  - [ ] **7.1.5** Add rich metadata extraction (function names, parameters, types, relationships)
  - [ ] **7.1.6** Performance and accuracy comparison with LangChain
  - [ ] **7.1.7** Migration path and backward compatibility
- [ ] **Advanced Language Support**: Expand beyond MVP languages
  - [ ] **7.2.1** Add C# support with tree-sitter-c-sharp
  - [ ] **7.2.2** Add Go support with tree-sitter-go
  - [ ] **7.2.3** Add Rust support with tree-sitter-rust
  - [ ] **7.2.4** Language-specific chunking strategies

**Future Development Note:**
*Beyond Phase 7, new features will be driven by actual user feedback and demonstrated need. Focus remains on simplicity, reliability, and core value delivery rather than feature expansion.*

---

## 🔧 Tree-sitter Implementation Details

### Updated Directory Structure (Phase 7)
```
├── src/
│   ├── core/
│   │   ├── chunking/           # Text Processing Module
│   │   │   ├── __init__.py
│   │   │   ├── protocol.py     # Interface comum (existing)
│   │   │   ├── langchain_adapter.py # LangChain implementation (existing)
│   │   │   ├── treesitter_adapter.py # Tree-sitter main adapter (new)
│   │   │   └── treesitter_languages/ # Tree-sitter language implementations
│   │   │       ├── __init__.py
│   │   │       ├── base_language.py      # Base class for all Tree-sitter languages
│   │   │       ├── javascript_language.py # JavaScript/TypeScript/React/JSX
│   │   │       ├── python_language.py    # Python/Django/Flask
│   │   │       ├── csharp_language.py    # C# (future)
│   │   │       ├── go_language.py        # Go (future)
│   │   │       └── rust_language.py      # Rust (future)
```

### Tree-sitter Language-Specific File Organization
Each Tree-sitter language implementation gets its own file due to complexity:

**File Size Estimates:**
- `javascript_language.py`: ~400-500 lines (JS/TS/React/JSX support)
- `python_language.py`: ~300-400 lines (Python/Django/Flask support)  
- `csharp_language.py`: ~350-450 lines (C#/ASP.NET support)
- `go_language.py`: ~250-350 lines (Go/Gin/Echo support)
- `rust_language.py`: ~300-400 lines (Rust/Actix/Rocket support)

**Benefits of Separation:**
- ✅ **Maintainability**: Each expert can focus on their language
- ✅ **Testing**: Language-specific test files  
- ✅ **Extensibility**: Add new languages without touching existing ones
- ✅ **Performance**: Import only needed Tree-sitter language parsers
- ✅ **Debugging**: Isolate Tree-sitter language-specific issues
- ✅ **Clear Scope**: Obviously Tree-sitter specific implementations

### Tree-sitter Adapter (Following Established Pattern)
```python
# src/core/chunking/treesitter_adapter.py
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjs
from tree_sitter import Parser, Node
from typing import List, Dict, Any, Set
from pathlib import Path

class TreeSitterChunker:
    """Tree-sitter adapter following same interface as LangChain adapter"""
    
    def __init__(self):
        self.parsers = {}
        self.languages = {
            '.py': ('python', tspython.language()),
            '.js': ('javascript', tsjs.language()),
            '.jsx': ('javascript', tsjs.language()),
            '.ts': ('javascript', tsjs.language()),  # TypeScript uses JS parser
            '.tsx': ('javascript', tsjs.language())
        }
        
        # Language-specific chunk types
        self.chunk_types = {
            'javascript': {
                'function_declaration', 'arrow_function', 'method_definition',
                'class_declaration', 'interface_declaration', 'type_alias_declaration',
                'import_statement', 'export_statement', 'variable_declarator', 'jsx_element'
            },
            'python': {
                'function_definition', 'async_function_definition', 'class_definition',
                'import_statement', 'import_from_statement', 'decorated_definition'
            }
        }
    
    def chunk_file(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Main chunking method - same interface as LangChain adapter"""
        ext = Path(file_path).suffix.lower()
        if ext not in self.languages:
            raise ValueError(f"Unsupported extension: {ext}")
        
        language_name, language_obj = self.languages[ext]
        parser = self._get_parser(language_obj)
        
        tree = parser.parse(content.encode())
        chunks = []
        
        def traverse_node(node: Node, depth: int = 0):
            if node.type in self.chunk_types[language_name]:
                chunk_text = content[node.start_byte:node.end_byte]
                
                # Base metadata
                metadata = {
                    'file': file_path,
                    'language': language_name,
                    'type': node.type,
                    'start_line': node.start_point[0] + 1,
                    'end_line': node.end_point[0] + 1,
                    'depth': depth,
                    'chunker': 'treesitter'
                }
                
                # Language-specific metadata extraction
                if language_name == 'javascript':
                    metadata.update(self._extract_javascript_metadata(node, content))
                elif language_name == 'python':
                    metadata.update(self._extract_python_metadata(node, content))
                
                chunks.append({
                    'text': chunk_text,
                    'metadata': metadata
                })
            
            # Continue traversing children
            for child in node.children:
                traverse_node(child, depth + 1)
        
        traverse_node(tree.root_node)
        return chunks
    
    def supports_extension(self, extension: str) -> bool:
        """Check if extension is supported - same interface as LangChain adapter"""
        return extension.lower() in self.languages
    
    def _get_parser(self, language_obj):
        """Cache parsers for performance"""
        lang_id = id(language_obj)
        if lang_id not in self.parsers:
            parser = Parser()
            parser.set_language(language_obj)
            self.parsers[lang_id] = parser
        return self.parsers[lang_id]
```

### JavaScript Metadata Extraction (Complete Implementation)
```python
    def _extract_javascript_metadata(self, node: Node, content: str) -> Dict[str, Any]:
        """Extract JavaScript/TypeScript/React specific metadata"""
        metadata = {}
        
        if node.type == 'function_declaration':
            metadata.update(self._extract_js_function_metadata(node, content))
        
        elif node.type == 'class_declaration':
            metadata.update(self._extract_js_class_metadata(node, content))
            
        elif node.type == 'interface_declaration':
            metadata.update(self._extract_js_interface_metadata(node, content))
            
        elif node.type == 'jsx_element':
            metadata.update(self._extract_jsx_metadata(node, content))
            
        elif node.type == 'variable_declarator':
            metadata.update(self._extract_js_variable_metadata(node, content))
        
        return metadata
    
    def _extract_js_function_metadata(self, node: Node, content: str) -> Dict[str, Any]:
        """Extract function declaration metadata"""
        metadata = {'category': 'function'}
        
        # Function name
        name_node = node.child_by_field_name('name')
        if name_node:
            metadata['name'] = content[name_node.start_byte:name_node.end_byte]
        
        # Parameters
        params_node = node.child_by_field_name('parameters')
        if params_node:
            params = []
            for child in params_node.children:
                if child.type == 'identifier':
                    params.append(content[child.start_byte:child.end_byte])
                elif child.type == 'rest_pattern':
                    params.append(f"...{content[child.start_byte:child.end_byte]}")
            metadata['parameters'] = params
        
        # Check if async
        chunk_text = content[node.start_byte:node.end_byte]
        if chunk_text.strip().startswith('async'):
            metadata['is_async'] = True
        
        # Check if exported
        if self._is_exported(node, content):
            metadata['is_exported'] = True
            
        return metadata
    
    def _extract_js_class_metadata(self, node: Node, content: str) -> Dict[str, Any]:
        """Extract class metadata"""
        metadata = {'category': 'class'}
        
        # Class name
        name_node = node.child_by_field_name('name')
        if name_node:
            metadata['name'] = content[name_node.start_byte:name_node.end_byte]
        
        # Inheritance
        superclass_node = node.child_by_field_name('superclass')
        if superclass_node:
            metadata['extends'] = content[superclass_node.start_byte:superclass_node.end_byte]
        
        # Methods
        body_node = node.child_by_field_name('body')
        if body_node:
            methods = []
            for child in body_node.children:
                if child.type == 'method_definition':
                    method_name_node = child.child_by_field_name('name')
                    if method_name_node:
                        method_name = content[method_name_node.start_byte:method_name_node.end_byte]
                        methods.append(method_name)
            metadata['methods'] = methods
        
        # Check if React component
        class_name = metadata.get('name', '')
        if self._is_react_component(class_name, content):  
            metadata['is_react_component'] = True
            
        return metadata
    
    def _extract_js_interface_metadata(self, node: Node, content: str) -> Dict[str, Any]:
        """Extract TypeScript interface metadata"""
        metadata = {
            'category': 'interface',
            'language': 'typescript'
        }
        
        # Interface name
        name_node = node.child_by_field_name('name')
        if name_node:
            metadata['name'] = content[name_node.start_byte:name_node.end_byte]
        
        # Properties
        body_node = node.child_by_field_name('body')
        if body_node:
            properties = []
            for child in body_node.children:
                if child.type == 'property_signature':
                    prop_name_node = child.child_by_field_name('name')
                    if prop_name_node:
                        prop_name = content[prop_name_node.start_byte:prop_name_node.end_byte]
                        is_optional = '?' in content[child.start_byte:child.end_byte]
                        properties.append({
                            'name': prop_name,
                            'optional': is_optional
                        })
            metadata['properties'] = properties
        
        return metadata
```

### Python Metadata Extraction (Complete Implementation)
```python
    def _extract_python_metadata(self, node: Node, content: str) -> Dict[str, Any]:
        """Extract Python specific metadata"""
        metadata = {}
        
        if node.type in ['function_definition', 'async_function_definition']:
            metadata.update(self._extract_py_function_metadata(node, content))
        
        elif node.type == 'class_definition':
            metadata.update(self._extract_py_class_metadata(node, content))
            
        elif node.type in ['import_statement', 'import_from_statement']:
            metadata.update(self._extract_py_import_metadata(node, content))
        
        return metadata
    
    def _extract_py_function_metadata(self, node: Node, content: str) -> Dict[str, Any]:
        """Extract Python function metadata"""
        metadata = {'category': 'function'}
        
        # Function name
        name_node = node.child_by_field_name('name')
        if name_node:
            metadata['name'] = content[name_node.start_byte:name_node.end_byte]
        
        # Parameters
        params_node = node.child_by_field_name('parameters')
        if params_node:
            params = []
            for child in params_node.children:
                if child.type == 'identifier':
                    params.append(content[child.start_byte:child.end_byte])
                elif child.type == 'default_parameter':
                    name_node = child.child_by_field_name('name')
                    if name_node:
                        param_name = content[name_node.start_byte:name_node.end_byte]
                        params.append(f"{param_name}=...")
            metadata['parameters'] = params
        
        # Check if async
        if node.type == 'async_function_definition':
            metadata['is_async'] = True
        
        # Docstring extraction
        body_node = node.child_by_field_name('body')
        if body_node and body_node.children:
            first_stmt = body_node.children[0]
            if first_stmt.type == 'expression_statement':
                expr = first_stmt.children[0]
                if expr.type == 'string':
                    docstring = content[expr.start_byte:expr.end_byte]
                    metadata['docstring'] = docstring.strip('\'"')
        
        return metadata
    
    def _extract_py_class_metadata(self, node: Node, content: str) -> Dict[str, Any]:
        """Extract Python class metadata"""
        metadata = {'category': 'class'}
        
        # Class name
        name_node = node.child_by_field_name('name')
        if name_node:
            metadata['name'] = content[name_node.start_byte:name_node.end_byte]
        
        # Inheritance
        superclasses_node = node.child_by_field_name('superclasses')
        if superclasses_node:
            superclasses = []
            for child in superclasses_node.children:
                if child.type == 'identifier':
                    superclasses.append(content[child.start_byte:child.end_byte])
            metadata['inherits_from'] = superclasses
        
        # Methods
        body_node = node.child_by_field_name('body')
        if body_node:
            methods = []
            for child in body_node.children:
                if child.type in ['function_definition', 'async_function_definition']:
                    method_name_node = child.child_by_field_name('name')
                    if method_name_node:
                        method_name = content[method_name_node.start_byte:method_name_node.end_byte]
                        # Mark special methods
                        if method_name.startswith('__') and method_name.endswith('__'):
                            methods.append(f"{method_name} (special)")
                        else:
                            methods.append(method_name)
            metadata['methods'] = methods
        
        return metadata
    
    # Helper methods
    def _is_react_component(self, class_name: str, content: str) -> bool:
        """Detect if class is a React component"""
        if not class_name:
            return False
        
        import re
        # Check common React patterns
        patterns = [
            rf'class\s+{class_name}\s+extends\s+React\.Component',
            rf'class\s+{class_name}\s+extends\s+Component',
            r'render\s*\(\s*\)\s*\{'
        ]
        
        for pattern in patterns:
            if re.search(pattern, content):
                return True
        return False
    
    def _is_exported(self, node: Node, content: str) -> bool:
        """Check if function/class is exported"""
        start_check = max(0, node.start_byte - 50)
        preceding_text = content[start_check:node.start_byte]
        return 'export' in preceding_text.split()[-10:]
```

### Usage Example (Consistent with Plan.md)
```python
# Same interface as LangChain adapter!
# src/core/embeddings.py
from .chunking.treesitter_adapter import TreeSitterChunker

class EmbeddingGenerator:
    def __init__(self, use_treesitter: bool = False):
        if use_treesitter:
            self.chunker = TreeSitterChunker()
        else:
            self.chunker = LangChainChunker()  # Current MVP default
    
    def process_file(self, file_path: str, content: str):
        """Same interface - no client code changes needed!"""
        if not self.chunker.supports_extension(Path(file_path).suffix):
            print(f"Warning: Unsupported file type: {file_path}")
            return
        
        chunks = self.chunker.chunk_file(content, file_path)
        
        for chunk in chunks:
            embedding = self.generate_embedding(chunk['text'])
            self.store_chunk(chunk, embedding)
```

### JavaScript Chunker (Complete Implementation)
```python
class JavaScriptLanguageChunker(BaseLanguageChunker):
    """JavaScript/TypeScript semantic chunker with React support"""
    
    def __init__(self):
        super().__init__(tsjs.language())
    
    def get_chunk_types(self) -> Set[str]:
        return {
            'function_declaration',    # function foo() {}
            'arrow_function',         # const foo = () => {}
            'method_definition',      # class methods
            'class_declaration',      # class Foo {}
            'interface_declaration',  # TypeScript interfaces
            'type_alias_declaration', # TypeScript types
            'import_statement',       # imports
            'export_statement',       # exports
            'variable_declarator',    # const/let/var with complex values
            'jsx_element',           # React components
        }
    
    def extract_metadata(self, node: Node, content: str) -> Dict[str, Any]:
        """Extract JavaScript/TypeScript/React metadata"""
        metadata = {
            'language': 'javascript',
            'type': node.type
        }
        
        if node.type == 'function_declaration':
            metadata.update(self._extract_function_metadata(node, content))
        
        elif node.type == 'arrow_function':
            metadata.update(self._extract_arrow_function_metadata(node, content))
            
        elif node.type == 'class_declaration':
            metadata.update(self._extract_class_metadata(node, content))
            
        elif node.type == 'interface_declaration':
            metadata.update(self._extract_interface_metadata(node, content))
            
        elif node.type == 'import_statement':
            metadata.update(self._extract_import_metadata(node, content))
            
        elif node.type == 'jsx_element':
            metadata.update(self._extract_jsx_metadata(node, content))
            
        elif node.type == 'variable_declarator':
            metadata.update(self._extract_variable_metadata(node, content))
        
        return metadata
    
    def _extract_function_metadata(self, node: Node, content: str) -> Dict[str, Any]:
        """Extract function declaration metadata"""
        metadata = {'category': 'function'}
        
        # Function name
        name_node = node.child_by_field_name('name')
        if name_node:
            metadata['name'] = content[name_node.start_byte:name_node.end_byte]
        
        # Parameters
        params_node = node.child_by_field_name('parameters')
        if params_node:
            params = []
            for child in params_node.children:
                if child.type == 'identifier':
                    params.append(content[child.start_byte:child.end_byte])
                elif child.type == 'rest_pattern':
                    # Handle ...args
                    params.append(f"...{content[child.start_byte:child.end_byte]}")
            metadata['parameters'] = params
        
        # Check if async
        chunk_text = content[node.start_byte:node.end_byte]
        if chunk_text.strip().startswith('async'):
            metadata['is_async'] = True
        
        # Check if exported
        if self._is_exported(node, content):
            metadata['is_exported'] = True
            
        return metadata
    
    def _extract_class_metadata(self, node: Node, content: str) -> Dict[str, Any]:
        """Extract class metadata including methods and inheritance"""
        metadata = {'category': 'class'}
        
        # Class name
        name_node = node.child_by_field_name('name')
        if name_node:
            metadata['name'] = content[name_node.start_byte:name_node.end_byte]
        
        # Inheritance
        superclass_node = node.child_by_field_name('superclass')
        if superclass_node:
            metadata['extends'] = content[superclass_node.start_byte:superclass_node.end_byte]
        
        # Methods
        body_node = node.child_by_field_name('body')
        if body_node:
            methods = []
            constructors = []
            for child in body_node.children:
                if child.type == 'method_definition':
                    method_name_node = child.child_by_field_name('name')
                    if method_name_node:
                        method_name = content[method_name_node.start_byte:method_name_node.end_byte]
                        if method_name == 'constructor':
                            constructors.append(method_name)
                        else:
                            methods.append(method_name)
            
            metadata['methods'] = methods
            if constructors:
                metadata['has_constructor'] = True
        
        # Check if React component
        if self._is_react_component(metadata.get('name', ''), content):
            metadata['is_react_component'] = True
            
        return metadata
    
    def _extract_interface_metadata(self, node: Node, content: str) -> Dict[str, Any]:
        """Extract TypeScript interface metadata"""
        metadata = {
            'category': 'interface',
            'language': 'typescript'
        }
        
        # Interface name
        name_node = node.child_by_field_name('name')
        if name_node:
            metadata['name'] = content[name_node.start_byte:name_node.end_byte]
        
        # Properties
        body_node = node.child_by_field_name('body')
        if body_node:
            properties = []
            for child in body_node.children:
                if child.type == 'property_signature':
                    prop_name_node = child.child_by_field_name('name')
                    if prop_name_node:
                        prop_name = content[prop_name_node.start_byte:prop_name_node.end_byte]
                        
                        # Check if optional
                        is_optional = '?' in content[child.start_byte:child.end_byte]
                        
                        properties.append({
                            'name': prop_name,
                            'optional': is_optional
                        })
            
            metadata['properties'] = properties
        
        return metadata
    
    def _extract_jsx_metadata(self, node: Node, content: str) -> Dict[str, Any]:
        """Extract React JSX component metadata"""
        metadata = {
            'category': 'jsx_component',
            'language': 'jsx'
        }
        
        # Component name
        opening_element = node.child_by_field_name('opening_element')
        if opening_element:
            name_node = opening_element.child_by_field_name('name')
            if name_node:
                metadata['component_name'] = content[name_node.start_byte:name_node.end_byte]
        
        # Props used
        if opening_element:
            props = []
            for child in opening_element.children:
                if child.type == 'jsx_attribute':
                    attr_name_node = child.child_by_field_name('name')
                    if attr_name_node:
                        props.append(content[attr_name_node.start_byte:attr_name_node.end_byte])
            
            if props:
                metadata['props_used'] = props
        
        return metadata
    
    def _is_react_component(self, class_name: str, content: str) -> bool:
        """Detect if class is a React component"""
        if not class_name:
            return False
        
        # Check if extends React.Component or Component
        extends_patterns = [
            r'class\s+' + class_name + r'\s+extends\s+React\.Component',
            r'class\s+' + class_name + r'\s+extends\s+Component',
            r'class\s+' + class_name + r'\s+extends\s+PureComponent'
        ]
        
        for pattern in extends_patterns:
            if re.search(pattern, content):
                return True
        
        # Check if has render method
        render_pattern = r'render\s*\(\s*\)\s*\{'
        if re.search(render_pattern, content):
            return True
            
        return False
    
    def _is_exported(self, node: Node, content: str) -> bool:
        """Check if function/class is exported"""
        # Simple check - look for export keyword before the node
        start_check = max(0, node.start_byte - 50)
        preceding_text = content[start_check:node.start_byte]
        
        return 'export' in preceding_text.split()[-10:]  # Check last 10 tokens
```

### Python Language Chunker (Complete Implementation)
```python
# src/core/chunking/language_chunkers/python_chunker.py
import tree_sitter_python as tspython
from .base_language_chunker import BaseLanguageChunker
from typing import Set, Dict, Any
from tree_sitter import Node

class PythonLanguageChunker(BaseLanguageChunker):
    """Python semantic chunker with Django/Flask support"""
    
    def __init__(self):
        super().__init__(tspython.language())
    
    def get_chunk_types(self) -> Set[str]:
        return {
            'function_definition',    # def foo():
            'async_function_definition',  # async def foo():
            'class_definition',      # class Foo:
            'import_statement',      # import / from import
            'import_from_statement', # from x import y
            'decorated_definition',  # @decorator def/class
        }
    
    def extract_metadata(self, node: Node, content: str) -> Dict[str, Any]:
        """Extract Python-specific metadata"""
        metadata = {
            'language': 'python',
            'type': node.type
        }
        
        if node.type in ['function_definition', 'async_function_definition']:
            metadata.update(self._extract_function_metadata(node, content))
        
        elif node.type == 'class_definition':
            metadata.update(self._extract_class_metadata(node, content))
            
        elif node.type in ['import_statement', 'import_from_statement']:
            metadata.update(self._extract_import_metadata(node, content))
            
        elif node.type == 'decorated_definition':
            metadata.update(self._extract_decorated_metadata(node, content))
        
        return metadata
    
    def _extract_function_metadata(self, node: Node, content: str) -> Dict[str, Any]:
        """Extract function metadata including decorators and docstrings"""
        metadata = {'category': 'function'}
        
        # Function name
        name_node = node.child_by_field_name('name')
        if name_node:
            metadata['name'] = content[name_node.start_byte:name_node.end_byte]
        
        # Parameters
        params_node = node.child_by_field_name('parameters')
        if params_node:
            params = []
            for child in params_node.children:
                if child.type == 'identifier':
                    params.append(content[child.start_byte:child.end_byte])
                elif child.type == 'default_parameter':
                    # Handle default params
                    name_node = child.child_by_field_name('name')
                    if name_node:
                        param_name = content[name_node.start_byte:name_node.end_byte]
                        params.append(f"{param_name}=...")
            
            metadata['parameters'] = params
        
        # Check if async
        if node.type == 'async_function_definition':
            metadata['is_async'] = True
        
        # Docstring
        body_node = node.child_by_field_name('body')
        if body_node and body_node.children:
            first_stmt = body_node.children[0]
            if first_stmt.type == 'expression_statement':
                expr = first_stmt.children[0]
                if expr.type == 'string':
                    docstring = content[expr.start_byte:expr.end_byte]
                    metadata['docstring'] = docstring.strip('\'"')
        
        # Check for common Python patterns
        func_text = content[node.start_byte:node.end_byte]
        if '@property' in func_text or '@staticmethod' in func_text:
            metadata['is_property_or_static'] = True
        
        return metadata
    
    def _extract_class_metadata(self, node: Node, content: str) -> Dict[str, Any]:
        """Extract class metadata including inheritance and methods"""
        metadata = {'category': 'class'}
        
        # Class name
        name_node = node.child_by_field_name('name')
        if name_node:
            metadata['name'] = content[name_node.start_byte:name_node.end_byte]
        
        # Inheritance
        superclasses_node = node.child_by_field_name('superclasses')
        if superclasses_node:
            superclasses = []
            for child in superclasses_node.children:
                if child.type == 'identifier':
                    superclasses.append(content[child.start_byte:child.end_byte])
            
            metadata['inherits_from'] = superclasses
        
        # Methods
        body_node = node.child_by_field_name('body')
        if body_node:
            methods = []
            properties = []
            for child in body_node.children:
                if child.type in ['function_definition', 'async_function_definition']:
                    method_name_node = child.child_by_field_name('name')
                    if method_name_node:
                        method_name = content[method_name_node.start_byte:method_name_node.end_byte]
                        
                        # Check if it's a special method
                        if method_name.startswith('__') and method_name.endswith('__'):
                            methods.append(f"{method_name} (special)")
                        else:
                            methods.append(method_name)
                
                # Check for properties
                elif child.type == 'decorated_definition':
                    # Look for @property decorator
                    chunk_text = content[child.start_byte:child.end_byte]
                    if '@property' in chunk_text:
                        func_node = None
                        for subchild in child.children:
                            if subchild.type == 'function_definition':
                                func_node = subchild
                                break
                        
                        if func_node:
                            prop_name_node = func_node.child_by_field_name('name')
                            if prop_name_node:
                                properties.append(content[prop_name_node.start_byte:prop_name_node.end_byte])
            
            metadata['methods'] = methods
            if properties:
                metadata['properties'] = properties
        
        return metadata
```

### LangChain vs Tree-sitter Quality Comparison
```python
# Quality comparison examples

# INPUT CODE:
javascript_code = '''
interface ButtonProps {
  variant: 'primary' | 'secondary'
  size?: 'sm' | 'md' | 'lg'
  onClick?: () => void
}

export const Button = ({ variant = 'primary', size = 'md', onClick }: ButtonProps) => {
  return (
    <button 
      className={`btn-${variant} btn-${size}`}
      onClick={onClick}
    >
      Click me
    </button>
  )
}
'''

# LANGCHAIN OUTPUT (current MVP):
langchain_chunks = [
    {
        "text": "interface ButtonProps {\n  variant: 'primary' | 'secondary'\n  size?: 'sm' | 'md' | 'lg'\n  onClick?: () => void\n}\n\nexport const Button = ({ variant = 'primary', size = 'md', onClick }: ButtonProps) => {",
        "metadata": {
            "file": "Button.tsx",
            "language": "typescript", 
            "chunk_index": 0,
            "chunker": "langchain"
        }
    },
    {
        "text": "return (\n    <button \n      className={`btn-${variant} btn-${size}`}\n      onClick={onClick}\n    >\n      Click me\n    </button>\n  )\n}",
        "metadata": {
            "file": "Button.tsx", 
            "language": "typescript",
            "chunk_index": 1,
            "chunker": "langchain"
        }
    }
]

# TREE-SITTER OUTPUT (future Phase 7):
treesitter_chunks = [
    {
        "text": "interface ButtonProps {\n  variant: 'primary' | 'secondary'\n  size?: 'sm' | 'md' | 'lg'\n  onClick?: () => void\n}",
        "metadata": {
            "file": "Button.tsx",
            "language": "typescript",
            "type": "interface_declaration",
            "name": "ButtonProps",
            "category": "interface", 
            "properties": [
                {"name": "variant", "optional": False},
                {"name": "size", "optional": True}, 
                {"name": "onClick", "optional": True}
            ],
            "start_line": 1,
            "end_line": 5,
            "chunker": "treesitter"
        }
    },
    {
        "text": "export const Button = ({ variant = 'primary', size = 'md', onClick }: ButtonProps) => {\n  return (\n    <button \n      className={`btn-${variant} btn-${size}`}\n      onClick={onClick}\n    >\n      Click me\n    </button>\n  )\n}",
        "metadata": {
            "file": "Button.tsx",
            "language": "typescript", 
            "type": "variable_declarator",
            "name": "Button",
            "category": "arrow_function",
            "parameters": ["variant", "size", "onClick"],
            "is_exported": True,
            "is_react_component": True,
            "props_used": ["className", "onClick"],
            "start_line": 7,
            "end_line": 16,
            "chunker": "treesitter"
        }
    }
]

# EMBEDDING QUALITY IMPACT:
# LangChain: "button className onClick" -> generic button queries
# Tree-sitter: "Button component ButtonProps variant size primary secondary React" -> specific component queries
```

---

## 🎯 Migration Strategy

### Phase 7.1: Parallel Implementation
1. Keep LangChain as default
2. Implement Tree-sitter adapter alongside
3. A/B test both approaches
4. Compare quality and performance

### Phase 7.2: Gradual Migration
1. Switch JavaScript files to Tree-sitter
2. Monitor embedding quality improvements
3. Switch Python files to Tree-sitter
4. Full migration once stability confirmed

### Phase 7.3: Backward Compatibility
1. Maintain LangChain as fallback option
2. Configuration flag for chunker selection
3. Migration tools for existing embeddings
4. Performance monitoring and rollback capability

---

*This roadmap ensures Context-AI evolves systematically while maintaining stability and user value at each phase.*
