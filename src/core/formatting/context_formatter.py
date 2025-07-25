"""
Context formatting for AI consumption in Context-AI.

Formats query results into AI-friendly formats with proper source attribution,
context assembly, and size limiting as specified in Plan.md.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re

from utils.logging import get_logger
from config.constants import DEFAULT_DISPLAY_RESULTS, CLAUDE_MAX_TOKENS
from core.query.result_merger import QueryResult


# Context formatting constants
DEFAULT_MAX_TOKENS = 4000  # From Plan.md context assembly example
CONTEXT_HEADER_TEMPLATE = "=== CONTEXT FROM MULTIPLE SOURCES ==="
RESULT_HEADER_TEMPLATE = "## Result {index} (score: {score:.3f}, source: {source})"
SOURCE_HEADER_TEMPLATE = "## From {source} (similarity: {similarity:.2f}):"
FILE_INFO_TEMPLATE = "**File:** {file_path} ({language})"
CROSS_REFERENCE_HEADER = "## Cross-reference analysis:"

try:
    import tiktoken
    # cl100k_base provides good approximation for Claude token counting
    _token_encoder = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(text: str) -> int:
        """Count tokens using tiktoken for accurate estimation."""
        return len(_token_encoder.encode(text))
        
except ImportError:
    AVG_CHARS_PER_TOKEN = 4
    
    def count_tokens(text: str) -> int:
        """Fallback token estimation when tiktoken unavailable."""
        clean_text = re.sub(r'[#*`\[\](){}]', '', text)
        char_count = len(clean_text)
        return max(1, char_count // AVG_CHARS_PER_TOKEN)


@dataclass
class FormattedContext:
    """Formatted context ready for AI consumption."""
    content: str
    token_count: int
    chunk_count: int
    source_count: int
    truncated: bool
    sources: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/debugging."""
        return {
            "token_count": self.token_count,
            "chunk_count": self.chunk_count,
            "source_count": self.source_count,
            "truncated": self.truncated,
            "sources": self.sources,
            "content_length": len(self.content)
        }


class ContextFormatter:
    """
    Formats query results into AI-friendly context format.
    
    Implements the context formatting strategy from Plan.md with:
    - Multi-source context assembly
    - Source attribution and linking
    - Token-based size limiting
    - Cross-reference analysis
    """
    
    def __init__(self, max_tokens: int = DEFAULT_MAX_TOKENS):
        """
        Initialize context formatter.
        
        Args:
            max_tokens: Maximum tokens for context (default: 4000 from Plan.md)
        """
        self.logger = get_logger(__name__)
        self.max_tokens = max_tokens
    
    def format_context(self, 
                      results: List[QueryResult], 
                      query: str = "",
                      format_type: str = "ai_friendly",
                      max_results: int = DEFAULT_DISPLAY_RESULTS,
                      max_tokens: Optional[int] = None) -> FormattedContext:
        """
        Format query results into AI-friendly context.
        
        Args:
            results: List of normalized query results
            query: Original query for context
            format_type: Output format ("ai_friendly", "plain", "markdown", "json", "xml")
            max_results: Maximum number of results to include
            max_tokens: Override default token limit for this formatting
            
        Returns:
            FormattedContext object with formatted content
        """
        # Use provided max_tokens or fall back to instance default
        token_limit = max_tokens if max_tokens is not None else self.max_tokens
        if not results:
            return FormattedContext(
                content="No relevant context found.",
                token_count=0,
                chunk_count=0,
                source_count=0,
                truncated=False,
                sources=[]
            )
        
        # Limit results to maximum
        limited_results = results[:max_results]
        
        # Format based on type
        if format_type == "ai_friendly":
            return self._format_ai_friendly(limited_results, query, token_limit)
        elif format_type == "plain":
            return self._format_plain_text(limited_results)
        elif format_type == "markdown":
            return self._format_markdown(limited_results)
        elif format_type == "json":
            return self._format_json(limited_results, query)
        elif format_type == "xml":
            return self._format_xml(limited_results, query)
        else:
            raise ValueError(f"Unsupported format type: {format_type}")
    
    def _format_ai_friendly(self, results: List[QueryResult], query: str = "", token_limit: int = None) -> FormattedContext:
        """Format results in AI-friendly format following Plan.md example."""
        if token_limit is None:
            token_limit = self.max_tokens
            
        content_parts = []
        sources = set()
        token_count = 0
        truncated = False
        
        # Add header
        header = CONTEXT_HEADER_TEMPLATE
        content_parts.append(header)
        token_count += count_tokens(header)
        
        # Process each result
        for i, result in enumerate(results):
            source = result.source_embedding
            sources.add(source)
            
            # Create result section
            similarity = 1.0 - result.original_distance  # Convert distance back to similarity
            file_path = result.metadata.get('file_path', 'unknown')
            language = result.metadata.get('language', 'text')
            
            # Format result header
            result_header = f"\n{SOURCE_HEADER_TEMPLATE.format(source=source, similarity=similarity)}"
            file_info = FILE_INFO_TEMPLATE.format(file_path=file_path, language=language)
            
            # Format code block
            code_block = f"\n```{language}\n{result.text}\n```\n"
            
            # Combine section
            section = f"{result_header}\n{file_info}\n{code_block}"
            section_tokens = count_tokens(section)
            
            # Check if adding this section would exceed token limit
            if token_count + section_tokens > token_limit:
                truncated = True
                self.logger.info("Context truncated at %d tokens (limit: %d)", 
                               token_count, token_limit)
                break
            
            content_parts.append(section)
            token_count += section_tokens
        
        # Add cross-reference analysis if space permits
        if not truncated and len(sources) > 1:
            analysis = self._generate_cross_reference_analysis(results)
            analysis_tokens = count_tokens(analysis)
            
            if token_count + analysis_tokens <= token_limit:
                content_parts.append(analysis)
                token_count += analysis_tokens
            else:
                truncated = True
        
        content = "\n".join(content_parts)
        
        return FormattedContext(
            content=content,
            token_count=token_count,
            chunk_count=len([r for r in results if not truncated or results.index(r) < len(content_parts) - 2]),
            source_count=len(sources),
            truncated=truncated,
            sources=sorted(list(sources))
        )
    
    def _format_plain_text(self, results: List[QueryResult]) -> FormattedContext:
        """Format results as plain text."""
        content_parts = []
        sources = set()
        
        for i, result in enumerate(results, 1):
            source = result.source_embedding
            sources.add(source)
            file_path = result.metadata.get('file_path', 'unknown')
            
            section = f"Result {i} (Source: {source}):\nFile: {file_path}\n\n{result.text}\n\n---\n"
            content_parts.append(section)
        
        content = "\n".join(content_parts)
        token_count = count_tokens(content)
        
        return FormattedContext(
            content=content,
            token_count=token_count,
            chunk_count=len(results),
            source_count=len(sources),
            truncated=False,
            sources=sorted(list(sources))
        )
    
    def _format_markdown(self, results: List[QueryResult]) -> FormattedContext:
        """Format results as markdown."""
        content_parts = ["# Query Results\n"]
        sources = set()
        
        for i, result in enumerate(results, 1):
            source = result.source_embedding
            sources.add(source)
            file_path = result.metadata.get('file_path', 'unknown')
            language = result.metadata.get('language', 'text')
            score = result.final_score
            
            section = f"""## Result {i}

**Source:** {source}  
**File:** {file_path}  
**Score:** {score:.3f}

```{language}
{result.text}
```

---
"""
            content_parts.append(section)
        
        content = "\n".join(content_parts)
        token_count = count_tokens(content)
        
        return FormattedContext(
            content=content,
            token_count=token_count,
            chunk_count=len(results),
            source_count=len(sources),
            truncated=False,
            sources=sorted(list(sources))
        )
    
    def _generate_cross_reference_analysis(self, results: List[QueryResult]) -> str:
        """Generate enhanced cross-reference analysis section with project correlation."""
        analysis_parts = [f"\n{CROSS_REFERENCE_HEADER}"]
        
        # Group results by project (source_embedding)
        projects_data = {}
        for result in results:
            project = result.source_embedding
            if project not in projects_data:
                projects_data[project] = {
                    'results': [],
                    'languages': set(),
                    'files': set(),
                    'patterns': []
                }
            
            projects_data[project]['results'].append(result)
            projects_data[project]['languages'].add(result.metadata.get('language', 'unknown'))
            projects_data[project]['files'].add(result.metadata.get('file_path', 'unknown'))
            
            # Extract potential patterns (function names, class names, etc.)
            text = result.text.lower()
            if 'function ' in text or 'def ' in text:
                projects_data[project]['patterns'].append('functions')
            if 'class ' in text or 'interface ' in text:
                projects_data[project]['patterns'].append('classes/interfaces')
            if 'component' in text or 'export default' in text:
                projects_data[project]['patterns'].append('components')
        
        # Project overview
        analysis_parts.append(f"- 🔄 **Cross-Project Analysis**: Found relevant code in {len(projects_data)} projects")
        
        # Per-project breakdown
        for project, data in projects_data.items():
            result_count = len(data['results'])
            lang_list = ', '.join(sorted(data['languages']))
            patterns = list(set(data['patterns']))
            
            project_line = f"  - **{project}**: {result_count} matches"
            if lang_list != 'unknown':
                project_line += f" ({lang_list})"
            if patterns:
                project_line += f" - Contains: {', '.join(patterns)}"
            
            analysis_parts.append(project_line)
        
        # Cross-project correlations
        if len(projects_data) > 1:
            analysis_parts.append("\n- 🧩 **Project Correlations**:")
            
            # Find common languages
            all_languages = set()
            common_languages = None
            for data in projects_data.values():
                all_languages.update(data['languages'])
                if common_languages is None:
                    common_languages = data['languages'].copy()
                else:
                    common_languages.intersection_update(data['languages'])
            
            if common_languages and 'unknown' not in common_languages:
                analysis_parts.append(f"  - ✅ **Common stack**: {', '.join(sorted(common_languages))}")
            
            # Find common patterns
            all_patterns = set()
            common_patterns = None
            for data in projects_data.values():
                patterns_set = set(data['patterns'])
                all_patterns.update(patterns_set)
                if common_patterns is None:
                    common_patterns = patterns_set.copy()
                else:
                    common_patterns.intersection_update(patterns_set)
            
            if common_patterns:
                analysis_parts.append(f"  - 🔗 **Similar patterns**: {', '.join(common_patterns)}")
            
            # Suggest comparison points
            analysis_parts.append("\n- 💡 **Comparison Opportunities**:")
            analysis_parts.append("  - Compare implementation approaches between projects")
            analysis_parts.append("  - Look for reusable patterns or components")
            analysis_parts.append("  - Identify opportunities for code standardization")
            
            if 'components' in all_patterns:
                analysis_parts.append("  - Check component APIs and prop interfaces for consistency")
            if 'functions' in all_patterns:
                analysis_parts.append("  - Review function signatures and error handling patterns")
        
        return "\n".join(analysis_parts)
    
    def _format_json(self, results: List[QueryResult], query: str = "") -> FormattedContext:
        """Format results as JSON."""
        import json
        
        sources = set()
        results_data = []
        
        for i, result in enumerate(results):
            source = result.source_embedding
            sources.add(source)
            
            result_data = {
                "index": i + 1,
                "score": result.final_score,
                "source_embedding": source,
                "file_path": result.metadata.get('file_path', 'unknown'),
                "language": result.metadata.get('language', 'text'),
                "chunk_index": result.metadata.get('chunk_index', 0),
                "content": result.text,
                "metadata": result.metadata
            }
            results_data.append(result_data)
        
        output_data = {
            "query": query,
            "total_results": len(results),
            "sources": sorted(list(sources)),
            "results": results_data
        }
        
        content = json.dumps(output_data, indent=2, ensure_ascii=False)
        token_count = count_tokens(content)
        
        return FormattedContext(
            content=content,
            token_count=token_count,
            chunk_count=len(results),
            source_count=len(sources),
            truncated=False,
            sources=sorted(list(sources))
        )
    
    def _format_xml(self, results: List[QueryResult], query: str = "") -> FormattedContext:
        """Format results as XML."""
        import xml.etree.ElementTree as ET
        from xml.dom import minidom
        
        sources = set()
        
        # Create root element
        root = ET.Element("context_search")
        root.set("query", query)
        root.set("total_results", str(len(results)))
        
        # Add sources
        sources_elem = ET.SubElement(root, "sources")
        for result in results:
            source = result.source_embedding
            sources.add(source)
        
        for source in sorted(sources):
            source_elem = ET.SubElement(sources_elem, "source")
            source_elem.text = source
        
        # Add results
        results_elem = ET.SubElement(root, "results")
        for i, result in enumerate(results):
            result_elem = ET.SubElement(results_elem, "result")
            result_elem.set("index", str(i + 1))
            result_elem.set("score", f"{result.final_score:.6f}")
            
            # Add metadata
            meta_elem = ET.SubElement(result_elem, "metadata")
            
            source_elem = ET.SubElement(meta_elem, "source_embedding")
            source_elem.text = result.source_embedding
            
            file_elem = ET.SubElement(meta_elem, "file_path")
            file_elem.text = result.metadata.get('file_path', 'unknown')
            
            lang_elem = ET.SubElement(meta_elem, "language")
            lang_elem.text = result.metadata.get('language', 'text')
            
            chunk_elem = ET.SubElement(meta_elem, "chunk_index")
            chunk_elem.text = str(result.metadata.get('chunk_index', 0))
            
            # Add content
            content_elem = ET.SubElement(result_elem, "content")
            content_elem.text = result.text
        
        # Convert to string with pretty formatting
        rough_string = ET.tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        content = reparsed.toprettyxml(indent="  ")
        
        # Remove empty lines
        content = '\n'.join([line for line in content.split('\n') if line.strip()])
        
        token_count = count_tokens(content)
        
        return FormattedContext(
            content=content,
            token_count=token_count,
            chunk_count=len(results),
            source_count=len(sources),
            truncated=False,
            sources=sorted(list(sources))
        )
    
    def format_for_claude(self, results: List[QueryResult], query: str = "") -> str:
        """
        Format context specifically for Claude consumption.
        
        Uses Claude's optimal token limit and formatting preferences.
        """
        # Use Claude's token limit from constants
        original_max = self.max_tokens
        self.max_tokens = min(self.max_tokens, CLAUDE_MAX_TOKENS // 4)  # Leave room for query + response
        
        try:
            formatted = self._format_ai_friendly(results, query)
            return formatted.content
        finally:
            # Restore original limit
            self.max_tokens = original_max
    
    def get_context_stats(self, formatted: FormattedContext) -> Dict[str, Any]:
        """Get statistics about formatted context."""
        return {
            "token_count": formatted.token_count,
            "token_percentage": (formatted.token_count / self.max_tokens) * 100,
            "chunk_count": formatted.chunk_count,
            "source_count": formatted.source_count,
            "sources": formatted.sources,
            "truncated": formatted.truncated,
            "efficiency": f"{formatted.chunk_count}/{formatted.token_count:.0f} chunks/token"
        }


# Global formatter instance
_context_formatter: Optional[ContextFormatter] = None


def get_context_formatter(max_tokens: int = DEFAULT_MAX_TOKENS) -> ContextFormatter:
    """Get global context formatter instance."""
    global _context_formatter
    if _context_formatter is None:
        _context_formatter = ContextFormatter(max_tokens)
    return _context_formatter


def format_results_for_ai(results: List[QueryResult], 
                         query: str = "",
                         max_tokens: int = DEFAULT_MAX_TOKENS) -> str:
    """Convenience function to format results for AI consumption."""
    formatter = get_context_formatter(max_tokens)
    formatted = formatter.format_context(results, query, "ai_friendly")
    return formatted.content