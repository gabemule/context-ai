"""
Result merging and score normalization for multi-embedding queries.

Implements the score normalization algorithm specified in Plan.md
for merging results from different embeddings with incompatible score distributions.
"""

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

from utils.logging import get_logger


# Score normalization constants
DEFAULT_WEIGHT_FACTOR = 0.9
MIN_SCORE_THRESHOLD = 0.01


@dataclass
class QueryResult:
    """Normalized query result with unified scoring."""
    text: str
    metadata: Dict[str, Any]
    original_distance: float
    normalized_score: float
    final_score: float
    source_embedding: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "text": self.text,
            "metadata": self.metadata,
            "original_distance": self.original_distance,
            "normalized_score": self.normalized_score,
            "final_score": self.final_score,
            "source_embedding": self.source_embedding
        }


class MultiEmbeddingResultMerger:
    """
    Merges and normalizes results from multiple embeddings.
    
    Implements the score normalization algorithm from Plan.md technical specs
    to handle incompatible score distributions across different embeddings.
    """
    
    def __init__(self, weight_factor: float = DEFAULT_WEIGHT_FACTOR):
        """
        Initialize result merger.
        
        Args:
            weight_factor: Factor applied to normalized scores (default: 0.9)
        """
        self.logger = get_logger(__name__)
        self.weight_factor = weight_factor
    
    def merge_multi_embedding_results(self, chroma_results: Dict[str, Any]) -> List[QueryResult]:
        """
        Normalize scores and merge results from multiple embeddings.
        
        Implements the algorithm from Plan.md:
        1. Group results by embedding_name
        2. Normalize scores per embedding 
        3. Apply weight factor
        4. Sort by final score
        
        Args:
            chroma_results: Raw results from ChromaDB query
            
        Returns:
            List of normalized and sorted QueryResult objects
        """
        if not chroma_results.get('documents') or not chroma_results['documents'][0]:
            self.logger.debug("No documents in results")
            return []
        
        # Extract data from ChromaDB results
        documents = chroma_results['documents'][0]
        metadatas = chroma_results['metadatas'][0]
        distances = chroma_results['distances'][0]
        
        if not (len(documents) == len(metadatas) == len(distances)):
            self.logger.error("Mismatched result lengths: docs=%d, meta=%d, dist=%d", 
                            len(documents), len(metadatas), len(distances))
            return []
        
        # Group results by embedding_name
        grouped = {}
        for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
            embedding_name = metadata.get('embedding_name', 'unknown')
            
            if embedding_name not in grouped:
                grouped[embedding_name] = []
            
            grouped[embedding_name].append({
                'text': doc,
                'distance': distance,
                'metadata': metadata,
                'index': i
            })
        
        self.logger.debug("Grouped results: %s", 
                         {name: len(results) for name, results in grouped.items()})
        
        # Normalize scores per embedding and create final results
        normalized_results = []
        
        for embedding_name, embedding_results in grouped.items():
            if not embedding_results:
                continue
                
            # Find max distance for normalization (convert to similarity)
            distances_list = [r['distance'] for r in embedding_results]
            max_distance = max(distances_list) if distances_list else 1.0
            min_distance = min(distances_list) if distances_list else 0.0
            
            # Handle edge case where all distances are the same
            distance_range = max_distance - min_distance
            if distance_range < MIN_SCORE_THRESHOLD:
                distance_range = 1.0
            
            # Normalize each result
            for result in embedding_results:
                distance = result['distance']
                
                # Convert distance to similarity score (lower distance = higher similarity)
                if distance_range > MIN_SCORE_THRESHOLD:
                    # Normalize to 0-1 range, then invert (1 - normalized_distance)
                    normalized_distance = (distance - min_distance) / distance_range
                    normalized_score = 1.0 - normalized_distance
                else:
                    # All distances are the same, assign medium score
                    normalized_score = 0.5
                
                # Apply weight factor
                final_score = normalized_score * self.weight_factor
                
                # Create normalized result
                query_result = QueryResult(
                    text=result['text'],
                    metadata=result['metadata'],
                    original_distance=distance,
                    normalized_score=normalized_score,
                    final_score=final_score,
                    source_embedding=embedding_name
                )
                
                normalized_results.append(query_result)
        
        # Sort by final score (highest first)
        normalized_results.sort(key=lambda x: x.final_score, reverse=True)
        
        self.logger.info("Merged and normalized %d results from %d embeddings", 
                        len(normalized_results), len(grouped))
        
        return normalized_results
    
    def format_results_for_display(self, results: List[QueryResult], max_results: int = 10) -> str:
        """
        Format normalized results for user display.
        
        Args:
            results: List of normalized QueryResult objects
            max_results: Maximum number of results to display
            
        Returns:
            Formatted string for display
        """
        if not results:
            return "No relevant context found."
        
        # Limit results to maximum
        display_results = results[:max_results]
        
        context_parts = []
        for i, result in enumerate(display_results):
            file_path = result.metadata.get('file_path', 'unknown')
            language = result.metadata.get('language', 'unknown')
            
            context_parts.append(f"""
## Result {i+1} (score: {result.final_score:.3f}, source: {result.source_embedding})
**File:** {file_path} ({language})

```{language}
{result.text}
```
""")
        
        return "\n".join(context_parts)
    
    def get_cross_embedding_stats(self, results: List[QueryResult]) -> Dict[str, Any]:
        """
        Get statistics about cross-embedding result distribution.
        
        Args:
            results: List of normalized QueryResult objects
            
        Returns:
            Dictionary with statistics
        """
        if not results:
            return {"total_results": 0, "embeddings": {}}
        
        # Count results per embedding
        embedding_counts = {}
        embedding_scores = {}
        
        for result in results:
            embedding = result.source_embedding
            
            if embedding not in embedding_counts:
                embedding_counts[embedding] = 0
                embedding_scores[embedding] = []
            
            embedding_counts[embedding] += 1
            embedding_scores[embedding].append(result.final_score)
        
        # Calculate average scores per embedding
        embedding_stats = {}
        for embedding, scores in embedding_scores.items():
            embedding_stats[embedding] = {
                "count": embedding_counts[embedding],
                "avg_score": sum(scores) / len(scores) if scores else 0.0,
                "max_score": max(scores) if scores else 0.0,
                "min_score": min(scores) if scores else 0.0
            }
        
        return {
            "total_results": len(results),
            "embeddings": embedding_stats,
            "top_embedding": max(embedding_stats.keys(), 
                               key=lambda k: embedding_stats[k]["avg_score"]) if embedding_stats else None
        }


# Global result merger instance
_result_merger: MultiEmbeddingResultMerger = None


def get_result_merger() -> MultiEmbeddingResultMerger:
    """Get global result merger instance."""
    global _result_merger
    if _result_merger is None:
        _result_merger = MultiEmbeddingResultMerger()
    return _result_merger