"""
Context formatting for AI consumption in Context-AI.

Formats query results into AI-friendly formats with proper source attribution,
context assembly, and size limiting as specified in Plan.md.
"""

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from config.constants import CONTEXT_DEFAULT_CHUNKS
from config.providers import get_max_tokens
from core.query.result_merger import QueryResult
from utils.logging import get_logger

RESULT_HEADER_TEMPLATE = "## Result {index} (score: {score:.3f}, source: {source})"
SOURCE_HEADER_TEMPLATE = "## From {source} (similarity: {similarity:.2f}):"
FILE_INFO_TEMPLATE = "**File:** {file_path} ({language})"

# Token calculation with caching for performance
_token_cache = {}

try:
    import tiktoken

    # cl100k_base provides good approximation for Claude token counting
    _token_encoder = tiktoken.get_encoding("cl100k_base")

    def count_tokens(text: str) -> int:
        """Count tokens using tiktoken with caching for performance."""
        from config.constants import ENABLE_TOKEN_CACHE, TOKEN_CACHE_SIZE

        if not ENABLE_TOKEN_CACHE:
            return len(_token_encoder.encode(text))

        # Use hash of text as cache key for memory efficiency
        text_hash = hash(text)

        if text_hash in _token_cache:
            return _token_cache[text_hash]

        # Calculate tokens
        token_count = len(_token_encoder.encode(text))

        # Cache with size limit (LRU-style)
        if len(_token_cache) >= TOKEN_CACHE_SIZE:
            # Remove oldest entry (simple FIFO for now)
            oldest_key = next(iter(_token_cache))
            del _token_cache[oldest_key]

        _token_cache[text_hash] = token_count
        return token_count

except ImportError:
    AVG_CHARS_PER_TOKEN = 4

    def count_tokens(text: str) -> int:
        """Fallback token estimation with caching when tiktoken unavailable."""
        from config.constants import ENABLE_TOKEN_CACHE, TOKEN_CACHE_SIZE

        if not ENABLE_TOKEN_CACHE:
            clean_text = re.sub(r"[#*`\[\](){}]", "", text)
            char_count = len(clean_text)
            return max(1, char_count // AVG_CHARS_PER_TOKEN)

        text_hash = hash(text)

        if text_hash in _token_cache:
            return _token_cache[text_hash]

        clean_text = re.sub(r"[#*`\[\](){}]", "", text)
        char_count = len(clean_text)
        token_count = max(1, char_count // AVG_CHARS_PER_TOKEN)

        if len(_token_cache) >= TOKEN_CACHE_SIZE:
            oldest_key = next(iter(_token_cache))
            del _token_cache[oldest_key]

        _token_cache[text_hash] = token_count
        return token_count


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
            "content_length": len(self.content),
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

    def __init__(self, max_tokens: Optional[int] = None):
        """
        Initialize context formatter.

        Args:
            max_tokens: Maximum tokens for context. If None, calculated dynamically
                       from Claude limits (get_max_tokens() * CONTEXT_TOKEN_RATIO)
        """
        self.logger = get_logger(__name__)
        self.max_tokens = self._validate_token_limit(max_tokens)

    def _validate_token_limit(self, max_tokens: Optional[int]) -> int:
        """
        Validate and sanitize token limit with intelligent fallbacks.
        
        Args:
            max_tokens: Requested token limit or None for auto-calculation
            
        Returns:
            Validated token limit within safe bounds
        """
        from config.constants import CONTEXT_TOKEN_RATIO
        
        # If not provided, calculate dynamically from Claude limits
        if max_tokens is None:
            dynamic_limit = int(get_max_tokens() * CONTEXT_TOKEN_RATIO)
            self.logger.debug(
                "🔧 Dynamic token limit: %dK (%d%% of %dK Claude max)",
                dynamic_limit // 1000,
                int(CONTEXT_TOKEN_RATIO * 100),
                get_max_tokens() // 1000,
            )
            return dynamic_limit
        
        # If exceeds Claude limit, cap with warning
        if max_tokens > get_max_tokens():
            self.logger.warning(
                "⚠️  Token limit %dK exceeds Claude max %dK, capping at %dK",
                max_tokens // 1000,
                get_max_tokens() // 1000,
                get_max_tokens() // 1000,
            )
            return get_max_tokens()
        
        # If too small, use sensible minimum
        min_tokens = 1000
        if max_tokens < min_tokens:
            self.logger.warning(
                "⚠️  Token limit %d too small, using minimum %d",
                max_tokens,
                min_tokens,
            )
            return min_tokens
            
        return max_tokens

    def format_context(
        self,
        results: List[QueryResult],
        query: str = "",
        format_type: str = "ai_friendly",
        max_results: int = CONTEXT_DEFAULT_CHUNKS,
        max_tokens: Optional[int] = None,
    ) -> FormattedContext:
        """
        Format query results into AI-friendly context.

        Args:
            results: List of normalized query results
            query: Original query for context
            format_type: Output format ("ai_friendly", "plain", "markdown",
                "json", "xml")
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
                sources=[],
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

    def _format_ai_friendly(
        self, results: List[QueryResult], query: str = "", token_limit: int = None
    ) -> FormattedContext:
        """Format results in XML-structured AI-friendly format."""
        if token_limit is None:
            token_limit = self.max_tokens

        # Start XML context
        content_parts = ["<context>"]
        sources = set()
        token_count = count_tokens("<context>")
        truncated = False
        results_sent = 0
        source_stats = {}

        # 1. Context Overview (moved to beginning)
        overview = self._generate_context_overview_xml(results)
        content_parts.append(overview)
        token_count += count_tokens(overview)

        # Collect sources for tracking
        for result in results:
            sources.add(result.source_embedding)

        # 2. Project Structures
        project_structure = self._generate_project_structure_xml(results, max_depth=None)
        if project_structure:
            content_parts.append(project_structure)
            token_count += count_tokens(project_structure)

        # 3. Similarity Matches
        matches_result = self._generate_similarity_matches_xml(results, token_limit - token_count, source_stats)
        content_parts.append(matches_result["content"])
        token_count += matches_result["tokens"]
        results_sent = matches_result["results_sent"]
        truncated = matches_result["truncated"]
        source_stats = matches_result["source_stats"]

        # Close XML context
        content_parts.append("</context>")
        token_count += count_tokens("</context>")

        # Log results
        if truncated:
            truncated_count = len(results) - results_sent
            self.logger.info(
                "📊 Context Results: %d/%d sent to AI (%d truncated by %dK token limit)",
                results_sent,
                len(results),
                truncated_count,
                token_limit // 1000,
            )
        else:
            self.logger.info(
                "📊 Context Results: %d/%d sent to AI (no truncation, %dK token limit)",
                results_sent,
                len(results),
                token_limit // 1000,
            )

        # Log per-source breakdown
        for source_name, stats in source_stats.items():
            self.logger.info(
                "  • %s: %d results (%dK tokens)",
                source_name,
                stats["count"],
                stats["tokens"] // 1000,
            )

        content = "\n".join(content_parts)

        return FormattedContext(
            content=content,
            token_count=token_count,
            chunk_count=results_sent,
            source_count=len(sources),
            truncated=truncated,
            sources=sorted(list(sources)),
        )

    def _format_plain_text(self, results: List[QueryResult]) -> FormattedContext:
        """Format results as plain text."""
        content_parts = []
        sources = set()

        for i, result in enumerate(results, 1):
            source = result.source_embedding
            sources.add(source)
            file_path = result.metadata.get("file_path", "unknown")

            section = (
                f"Result {i} (Source: {source}):\nFile: {file_path}\n\n"
                f"{result.text}\n\n---\n"
            )
            content_parts.append(section)

        content = "\n".join(content_parts)
        token_count = count_tokens(content)

        return FormattedContext(
            content=content,
            token_count=token_count,
            chunk_count=len(results),
            source_count=len(sources),
            truncated=False,
            sources=sorted(list(sources)),
        )

    def _format_markdown(self, results: List[QueryResult]) -> FormattedContext:
        """Format results as markdown."""
        content_parts = ["# Query Results\n"]
        sources = set()

        for i, result in enumerate(results, 1):
            source = result.source_embedding
            sources.add(source)
            file_path = result.metadata.get("file_path", "unknown")
            language = result.metadata.get("language", "text")
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
            sources=sorted(list(sources)),
        )

    def _build_directory_tree(self, file_paths):
        """Build a nested directory tree from file paths."""
        tree = {}
        
        for file_path in file_paths:
            if file_path == "unknown":
                continue
                
            parts = file_path.split("/")
            current = tree
            
            for part in parts:
                if part not in current:
                    current[part] = {}
                current = current[part]
        
        return tree
    
    def _format_tree(self, tree, prefix="", is_last=True, max_depth=4, current_depth=0):
        """Format directory tree with proper indentation."""
        if max_depth is not None and current_depth >= max_depth:
            return ["  └── ... (more files)"] if tree else []
        
        items = []
        sorted_items = sorted(tree.items())
        
        for i, (name, subtree) in enumerate(sorted_items):
            is_last_item = i == len(sorted_items) - 1
            
            # Choose connector
            if current_depth == 0:
                connector = "├── " if not is_last_item else "└── "
            else:
                connector = "├── " if not is_last_item else "└── "
            
            # Add current item
            items.append(f"{prefix}{connector}{name}")
            
            # Add children if it's a directory
            if subtree:
                # Determine prefix for children
                if current_depth == 0:
                    child_prefix = prefix + ("│   " if not is_last_item else "    ")
                else:
                    child_prefix = prefix + ("│   " if not is_last_item else "    ")
                
                child_items = self._format_tree(
                    subtree, child_prefix, is_last_item, max_depth, current_depth + 1
                )
                items.extend(child_items)
        
        return items
    
    def _generate_context_overview_xml(self, results: List[QueryResult]) -> str:
        """Generate XML-structured context overview for the beginning of the context."""
        projects_data = self._analyze_projects(results)
        
        overview_parts = ["<overview>"]
        overview_parts.append(f"<summary>Found relevant code in {len(projects_data)} projects</summary>")
        overview_parts.append("<projects>")
        
        all_languages = set()
        all_patterns = set()
        
        for project, data in projects_data.items():
            languages = ",".join(sorted(data["languages"] - {"unknown"}))
            patterns = ",".join(sorted(set(data["patterns"])))
            
            overview_parts.append(
                f'<project name="{project}" matches="{len(data["results"])}" '
                f'languages="{languages}" patterns="{patterns}"/>'
            )
            
            all_languages.update(data["languages"] - {"unknown"})
            all_patterns.update(data["patterns"])
        
        overview_parts.append("</projects>")
        overview_parts.append(f"<technology_stack>{','.join(sorted(all_languages))}</technology_stack>")
        overview_parts.append(f"<code_patterns>{','.join(sorted(all_patterns))}</code_patterns>")
        overview_parts.append("</overview>")
        
        return "\n".join(overview_parts)
    
    def _analyze_projects(self, results: List[QueryResult]) -> Dict[str, Dict]:
        """Analyze query results and group by project with metadata."""
        projects_data = {}
        
        for result in results:
            project = result.source_embedding
            if project not in projects_data:
                projects_data[project] = {
                    "results": [],
                    "languages": set(),
                    "files": set(),
                    "patterns": [],
                }

            projects_data[project]["results"].append(result)
            projects_data[project]["languages"].add(
                result.metadata.get("language", "unknown")
            )
            projects_data[project]["files"].add(
                result.metadata.get("file_path", "unknown")
            )

            # Extract potential patterns (function names, class names, etc.)
            text = result.text.lower()
            if "function " in text or "def " in text:
                projects_data[project]["patterns"].append("functions")
            if "class " in text or "interface " in text:
                projects_data[project]["patterns"].append("classes/interfaces")
            if "component" in text or "export default" in text:
                projects_data[project]["patterns"].append("components")
        
        return projects_data
    
    def _generate_project_structure_xml(self, results: List[QueryResult], max_depth: int = 4) -> str:
        """Generate XML-structured project structures."""
        if not results:
            return ""
        
        # Group files by source embedding
        projects = {}
        for result in results:
            source = result.source_embedding
            file_path = result.metadata.get("file_path", "unknown")
            
            if source not in projects:
                projects[source] = set()
            projects[source].add(file_path)
        
        if not projects:
            return ""
        
        structure_parts = ["<project_structures>"]
        
        for source, files in projects.items():
            structure_parts.append(f'<project name="{source}">')
            
            # Build directory tree
            tree = self._build_directory_tree(files)
            
            # Add tree structure
            structure_parts.append(f"📁 {source}:")
            structure_parts.extend(self._format_tree(tree, max_depth=max_depth))
            
            structure_parts.append("</project>")
        
        structure_parts.append("</project_structures>")
        return "\n".join(structure_parts)
    
    def _generate_similarity_matches_xml(self, results: List[QueryResult], remaining_tokens: int, source_stats: Dict) -> Dict:
        """Generate XML-structured similarity matches with token management."""
        matches_parts = ["<similarity_matches>"]
        token_count = count_tokens("<similarity_matches>")
        results_sent = 0
        truncated = False
        
        for result in results:
            source = result.source_embedding
            
            # Create match XML
            match_xml = self._create_match_xml(result)
            match_tokens = count_tokens(match_xml)
            
            # Check token limit
            if token_count + match_tokens > remaining_tokens:
                truncated = True
                break
            
            matches_parts.append(match_xml)
            token_count += match_tokens
            results_sent += 1
            
            # Track tokens per source
            if source not in source_stats:
                source_stats[source] = {"count": 0, "tokens": 0}
            source_stats[source]["count"] += 1
            source_stats[source]["tokens"] += match_tokens
        
        matches_parts.append("</similarity_matches>")
        token_count += count_tokens("</similarity_matches>")
        
        return {
            "content": "\n".join(matches_parts),
            "tokens": token_count,
            "results_sent": results_sent,
            "truncated": truncated,
            "source_stats": source_stats
        }
    
    def _create_match_xml(self, result: QueryResult) -> str:
        """Create XML structure for a single match."""
        source = result.source_embedding
        similarity = result.normalized_score
        file_path = result.metadata.get("file_path", "unknown")
        language = result.metadata.get("language", "text")
        
        # Escape XML special characters in attributes
        file_path_escaped = file_path.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
        
        return f'''<match source="{source}" similarity="{similarity:.3f}" file="{file_path_escaped}" language="{language}">
<content>
```{language}
{result.text}
```
</content>
</match>'''

    def _format_json(
        self, results: List[QueryResult], query: str = ""
    ) -> FormattedContext:
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
                "file_path": result.metadata.get("file_path", "unknown"),
                "language": result.metadata.get("language", "text"),
                "chunk_index": result.metadata.get("chunk_index", 0),
                "content": result.text,
                "metadata": result.metadata,
            }
            results_data.append(result_data)

        output_data = {
            "query": query,
            "total_results": len(results),
            "sources": sorted(list(sources)),
            "results": results_data,
        }

        content = json.dumps(output_data, indent=2, ensure_ascii=False)
        token_count = count_tokens(content)

        return FormattedContext(
            content=content,
            token_count=token_count,
            chunk_count=len(results),
            source_count=len(sources),
            truncated=False,
            sources=sorted(list(sources)),
        )

    def _format_xml(
        self, results: List[QueryResult], query: str = ""
    ) -> FormattedContext:
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
            file_elem.text = result.metadata.get("file_path", "unknown")

            lang_elem = ET.SubElement(meta_elem, "language")
            lang_elem.text = result.metadata.get("language", "text")

            chunk_elem = ET.SubElement(meta_elem, "chunk_index")
            chunk_elem.text = str(result.metadata.get("chunk_index", 0))

            # Add content
            content_elem = ET.SubElement(result_elem, "content")
            content_elem.text = result.text

        # Convert to string with pretty formatting
        rough_string = ET.tostring(root, encoding="unicode")
        reparsed = minidom.parseString(rough_string)
        content = reparsed.toprettyxml(indent="  ")

        # Remove empty lines
        content = "\n".join([line for line in content.split("\n") if line.strip()])

        token_count = count_tokens(content)

        return FormattedContext(
            content=content,
            token_count=token_count,
            chunk_count=len(results),
            source_count=len(sources),
            truncated=False,
            sources=sorted(list(sources)),
        )

    def format_for_claude(self, results: List[QueryResult], query: str = "") -> str:
        """
        Format context specifically for Claude consumption.

        Uses Claude's optimal token limit and formatting preferences.
        """
        # Use Claude's token limit from constants
        original_max = self.max_tokens
        self.max_tokens = min(
            self.max_tokens, get_max_tokens() // 4
        )  # Leave room for query + response

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
            "token_percentage": ((formatted.token_count / self.max_tokens) * 100),
            "chunk_count": formatted.chunk_count,
            "source_count": formatted.source_count,
            "sources": formatted.sources,
            "truncated": formatted.truncated,
            "efficiency": (
                f"{formatted.chunk_count}/{formatted.token_count:.0f} chunks/token"
            ),
        }


# Global formatter instance
_context_formatter: Optional[ContextFormatter] = None


def get_context_formatter(max_tokens: Optional[int] = None) -> ContextFormatter:
    """Get global context formatter instance with dynamic token limit."""
    global _context_formatter
    if _context_formatter is None:
        _context_formatter = ContextFormatter(max_tokens)
    return _context_formatter


def format_results_for_ai(
    results: List[QueryResult], query: str = "", max_tokens: Optional[int] = None
) -> str:
    """Convenience function to format results for AI consumption."""
    formatter = get_context_formatter(max_tokens)
    formatted = formatter.format_context(results, query, "ai_friendly")
    return formatted.content
