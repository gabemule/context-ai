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
                      max_results: int = DEFAULT_DISPLAY_RESULTS) -> FormattedContext:
        """
        Format query results into AI-friendly context.
        
        Args:
            results: List of normalized query results
            query: Original query for context
            format_type: Output format ("ai_friendly", "plain", "markdown")
            max_results: Maximum number of results to include
            
        Returns:
            FormattedContext object with formatted content
        """
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
            return self._format_ai_friendly(limited_results, query)
        elif format_type == "plain":
            return self._format_plain_text(limited_results)
        elif format_type == "markdown":
            return self._format_markdown(limited_results)
        else:
            raise ValueError(f"Unsupported format type: {format_type}")
    
    def _format_ai_friendly(self, results: List[QueryResult], query: str = "") -> FormattedContext:
        """Format results in AI-friendly format following Plan.md example."""
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
            if token_count + section_tokens > self.max_tokens:
                truncated = True
                self.logger.info("Context truncated at %d tokens (limit: %d)", 
                               token_count, self.max_tokens)
                break
            
            content_parts.append(section)
            token_count += section_tokens
        
        # Add cross-reference analysis if space permits
        if not truncated and len(sources) > 1:
            analysis = self._generate_cross_reference_analysis(results, list(sources))
            analysis_tokens = count_tokens(analysis)
            
            if token_count + analysis_tokens <= self.max_tokens:
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
    
    def _generate_cross_reference_analysis(self, results: List[QueryResult], sources: List[str]) -> str:
        """Generate cross-reference analysis section."""
        analysis_parts = [f"\n{CROSS_REFERENCE_HEADER}"]
        
        # Basic analysis based on metadata
        languages = set()
        files = set()
        
        for result in results:
            lang = result.metadata.get('language')
            file_path = result.metadata.get('file_path')
            if lang:
                languages.add(lang)
            if file_path:
                files.add(file_path)
        
        # Add analysis points
        if len(sources) > 1:
            analysis_parts.append(f"- ✅ Found relevant code in {len(sources)} different projects")
        
        if len(languages) > 1:
            analysis_parts.append(f"- 📝 Multiple languages involved: {', '.join(sorted(languages))}")
        
        if len(files) > 3:
            analysis_parts.append(f"- 📁 Code spans across {len(files)} files")
        
        # Generic suggestions
        analysis_parts.append("- 💡 Consider checking for consistency across implementations")
        if "typescript" in languages or "javascript" in languages:
            analysis_parts.append("- 🔍 Review TypeScript interfaces and prop definitions")
        
        return "\n".join(analysis_parts)
    
    
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