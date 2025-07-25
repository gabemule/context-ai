"""
Vector database management for Context-AI using ChromaDB.

Implements single collection design with metadata filtering
for multi-embedding storage and querying.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import uuid

import chromadb
from chromadb.config import Settings

from utils.logging import get_logger
from utils.storage import get_storage_manager
from config.constants import DEFAULT_CHUNK_SIZE, DEFAULT_QUERY_RESULTS, MAX_QUERY_RESULTS
from utils.exceptions import ConfigurationError


# Collection configuration
COLLECTION_NAME = "context_ai_embeddings"

# Metadata schema constants  
METADATA_EMBEDDING_NAME = "embedding_name"
METADATA_FILE_PATH = "file_path"
METADATA_LANGUAGE = "language"
METADATA_CHUNK_INDEX = "chunk_index"
METADATA_CHUNKER = "chunker"
METADATA_CREATED_AT = "created_at"
METADATA_FILE_SIZE = "file_size"
METADATA_CHUNK_TYPE = "chunk_type"

# Import query configuration from constants


class VectorStoreManager:
    """
    Manages ChromaDB vector storage with single collection design.
    
    Provides document storage, embedding management, and similarity search
    with metadata filtering for multi-embedding queries.
    """
    
    def __init__(self):
        """Initialize vector store manager."""
        self.logger = get_logger(__name__)
        self.storage_manager = get_storage_manager()
        self._client: Optional[chromadb.ClientAPI] = None
        self._collection: Optional[chromadb.Collection] = None
        
        # Setup ChromaDB storage path
        self._db_path = self.storage_manager.embeddings_dir / "chromadb"
        self._db_path.mkdir(parents=True, exist_ok=True)
    
    def _get_client(self) -> chromadb.ClientAPI:
        """Get or create ChromaDB client."""
        if self._client is None:
            try:
                # Create persistent client with proper settings
                self._client = chromadb.PersistentClient(
                    path=str(self._db_path),
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )
                self.logger.debug("ChromaDB client initialized at: %s", self._db_path)
                
            except Exception as e:
                raise ConfigurationError(f"Failed to initialize ChromaDB client: {e}") from e
                
        return self._client
    
    def _get_collection(self) -> chromadb.Collection:
        """Get or create the main collection."""
        if self._collection is None:
            try:
                client = self._get_client()
                
                # Try to get existing collection first
                try:
                    self._collection = client.get_collection(name=COLLECTION_NAME)
                    self.logger.debug("Using existing collection: %s", COLLECTION_NAME)
                    
                except Exception:
                    # Collection doesn't exist, create it
                    self._collection = client.create_collection(
                        name=COLLECTION_NAME,
                        metadata={"description": "Context-AI embeddings with multi-project support"}
                    )
                    self.logger.info("✅ Created new collection: %s", COLLECTION_NAME)
                    
            except Exception as e:
                raise ConfigurationError(f"Failed to access collection '{COLLECTION_NAME}': {e}") from e
                
        return self._collection
    
    def store_embeddings(self, 
                        embedding_name: str,
                        documents: List[str], 
                        embeddings: List[List[float]], 
                        metadatas: List[Dict[str, Any]]) -> bool:
        """
        Store documents and their embeddings with metadata.
        
        Args:
            embedding_name: Name of the embedding set
            documents: List of text documents
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries
            
        Returns:
            True if storage was successful
            
        Raises:
            ConfigurationError: If storage fails
        """
        if not documents or not embeddings or not metadatas:
            raise ConfigurationError("Documents, embeddings, and metadatas cannot be empty")
            
        if not (len(documents) == len(embeddings) == len(metadatas)):
            raise ConfigurationError("Documents, embeddings, and metadatas must have the same length")
        
        try:
            collection = self._get_collection()
            
            # Generate unique IDs for each document
            document_ids = [f"{embedding_name}_{uuid.uuid4().hex[:8]}_{i}" 
                          for i in range(len(documents))]
            
            # Add embedding_name to all metadata entries
            enhanced_metadatas = []
            current_time = datetime.now().isoformat()
            
            for metadata in metadatas:
                enhanced_metadata = metadata.copy()
                enhanced_metadata[METADATA_EMBEDDING_NAME] = embedding_name
                enhanced_metadata[METADATA_CREATED_AT] = current_time
                enhanced_metadatas.append(enhanced_metadata)
            
            # Store in ChromaDB
            collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=enhanced_metadatas,
                ids=document_ids
            )
            
            self.logger.info("✅ Stored %d documents for embedding '%s'", 
                           len(documents), embedding_name)
            return True
            
        except Exception as e:
            self.logger.error("Failed to store embeddings: %s", e)
            raise ConfigurationError(f"Failed to store embeddings: {e}") from e
    
    def query_embeddings(self, 
                        query_texts: List[str],
                        embedding_names: Optional[List[str]] = None,
                        n_results: int = DEFAULT_QUERY_RESULTS) -> Dict[str, Any]:
        """
        Query embeddings with optional filtering by embedding names.
        
        Args:
            query_texts: List of query texts
            embedding_names: Optional list of embedding names to filter by
            n_results: Number of results to return (max 100)
            
        Returns:
            Query results dictionary
            
        Raises:
            ConfigurationError: If query fails
        """
        if not query_texts:
            raise ConfigurationError("Query texts cannot be empty")
            
        # Limit results to maximum
        n_results = min(n_results, MAX_QUERY_RESULTS)
        
        try:
            collection = self._get_collection()
            
            # Build where clause for filtering
            where_clause = None
            if embedding_names:
                if len(embedding_names) == 1:
                    where_clause = {METADATA_EMBEDDING_NAME: embedding_names[0]}
                else:
                    where_clause = {METADATA_EMBEDDING_NAME: {"$in": embedding_names}}
            
            # Execute query
            results = collection.query(
                query_texts=query_texts,
                where=where_clause,
                n_results=n_results
            )
            
            self.logger.debug("Query returned %d results", 
                            len(results.get('documents', [[]])[0]) if results.get('documents') else 0)
            
            return results
            
        except Exception as e:
            self.logger.error("Failed to query embeddings: %s", e)
            raise ConfigurationError(f"Failed to query embeddings: {e}") from e
    
    def get_embedding_info(self, embedding_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a stored embedding.
        
        Args:
            embedding_name: Name of the embedding
            
        Returns:
            Dictionary with embedding information or None if not found
        """
        try:
            collection = self._get_collection()
            
            # Query for documents from this embedding
            results = collection.get(
                where={METADATA_EMBEDDING_NAME: embedding_name},
                include=["metadatas"]
            )
            
            if not results['metadatas']:
                return None
            
            # Calculate statistics
            metadatas = results['metadatas']
            total_chunks = len(metadatas)
            
            # Get unique files
            unique_files = set()
            languages = set()
            total_size = 0
            
            for metadata in metadatas:
                if METADATA_FILE_PATH in metadata:
                    unique_files.add(metadata[METADATA_FILE_PATH])
                if METADATA_LANGUAGE in metadata:
                    languages.add(metadata[METADATA_LANGUAGE])
                if METADATA_FILE_SIZE in metadata:
                    total_size += metadata.get(METADATA_FILE_SIZE, 0)
            
            # Get creation date (from first chunk)
            created_at = metadatas[0].get(METADATA_CREATED_AT) if metadatas else None
            
            return {
                "name": embedding_name,
                "total_chunks": total_chunks,
                "unique_files": len(unique_files),
                "languages": sorted(list(languages)),
                "total_size_bytes": total_size,
                "created_at": created_at,
                "sample_files": sorted(list(unique_files))[:5]  # Show first 5 files
            }
            
        except Exception as e:
            self.logger.error("Failed to get embedding info for '%s': %s", embedding_name, e)
            return None
    
    def list_embeddings(self) -> List[Dict[str, Any]]:
        """
        List all available embeddings.
        
        Returns:
            List of embedding information dictionaries
        """
        try:
            collection = self._get_collection()
            
            # Get all metadatas to find unique embedding names
            results = collection.get(include=["metadatas"])
            
            if not results['metadatas']:
                return []
            
            # Find unique embedding names
            embedding_names = set()
            for metadata in results['metadatas']:
                embedding_name = metadata.get(METADATA_EMBEDDING_NAME)
                if embedding_name:
                    embedding_names.add(embedding_name)
            
            # Get info for each embedding
            embeddings_info = []
            for name in sorted(embedding_names):
                info = self.get_embedding_info(name)
                if info:
                    embeddings_info.append(info)
            
            return embeddings_info
            
        except Exception as e:
            self.logger.error("Failed to list embeddings: %s", e)
            return []
    
    def delete_embedding(self, embedding_name: str) -> bool:
        """
        Delete all documents for a specific embedding.
        
        Args:
            embedding_name: Name of the embedding to delete
            
        Returns:
            True if deletion was successful
        """
        try:
            collection = self._get_collection()
            
            # Get all IDs for this embedding
            results = collection.get(
                where={METADATA_EMBEDDING_NAME: embedding_name},
                include=["documents"]  # We just need the IDs
            )
            
            if not results['ids']:
                self.logger.warning("No documents found for embedding '%s'", embedding_name)
                return False
            
            # Delete all documents for this embedding
            collection.delete(
                where={METADATA_EMBEDDING_NAME: embedding_name}
            )
            
            self.logger.info("✅ Deleted %d documents for embedding '%s'", 
                           len(results['ids']), embedding_name)
            return True
            
        except Exception as e:
            self.logger.error("Failed to delete embedding '%s': %s", embedding_name, e)
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get overall collection statistics.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            collection = self._get_collection()
            
            # Get collection count
            total_count = collection.count()
            
            if total_count == 0:
                return {
                    "total_documents": 0,
                    "total_embeddings": 0,
                    "collection_name": COLLECTION_NAME,
                    "database_path": str(self._db_path)
                }
            
            # Get all metadatas for detailed stats
            results = collection.get(include=["metadatas"])
            metadatas = results['metadatas']
            
            # Calculate statistics
            embedding_names = set()
            languages = set()
            total_size = 0
            
            for metadata in metadatas:
                embedding_name = metadata.get(METADATA_EMBEDDING_NAME)
                if embedding_name:
                    embedding_names.add(embedding_name)
                
                language = metadata.get(METADATA_LANGUAGE)
                if language:
                    languages.add(language)
                    
                file_size = metadata.get(METADATA_FILE_SIZE, 0)
                total_size += file_size
            
            return {
                "total_documents": total_count,
                "total_embeddings": len(embedding_names),
                "languages": sorted(list(languages)),
                "total_size_bytes": total_size,
                "collection_name": COLLECTION_NAME,
                "database_path": str(self._db_path),
                "embeddings": sorted(list(embedding_names))
            }
            
        except Exception as e:
            self.logger.error("Failed to get collection stats: %s", e)
            return {
                "error": str(e),
                "collection_name": COLLECTION_NAME,
                "database_path": str(self._db_path)
            }
    
    def reset_collection(self) -> bool:
        """
        Reset the entire collection (delete all data).
        
        Returns:
            True if reset was successful
        """
        try:
            client = self._get_client()
            
            # Delete the collection if it exists
            try:
                client.delete_collection(name=COLLECTION_NAME)
                self.logger.info("🗑️  Deleted collection: %s", COLLECTION_NAME)
            except Exception:
                pass  # Collection might not exist
            
            # Clear cached collection reference
            self._collection = None
            
            self.logger.info("✅ Collection reset complete")
            return True
            
        except Exception as e:
            self.logger.error("Failed to reset collection: %s", e)
            return False


# Global vector store manager instance
_vector_store: Optional[VectorStoreManager] = None


def get_vector_store() -> VectorStoreManager:
    """Get global vector store manager instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStoreManager()
    return _vector_store