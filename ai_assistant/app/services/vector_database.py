"""
Vector database service for knowledge base embeddings using FAISS.
"""

import os
import json
import pickle
import numpy as np
import faiss
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import logging

from ..config import settings

logger = logging.getLogger(__name__)


class VectorDatabase:
    """
    Local vector database using FAISS for document embeddings.
    """

    def __init__(self, dimension: Optional[int] = None, index_path: Optional[str] = None):
        """
        Initialize vector database.

        Args:
            dimension: Embedding vector dimension (defaults to settings.EMBEDDING_DIMENSION)
            index_path: Path to store FAISS index files (defaults to settings.VECTOR_INDEX_PATH)
        """
        self.dimension = dimension or settings.EMBEDDING_DIMENSION
        self.index_path = Path(index_path or settings.VECTOR_INDEX_PATH)
        self.index_path.mkdir(parents=True, exist_ok=True)

        # Initialize FAISS index
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
        self.document_metadata: Dict[int, Dict[str, Any]] = {}
        self.next_id = 0
        self._loaded_mtime: float = 0.0

        # Load existing index if available
        self._load_index()

    @property
    def _index_file(self) -> Path:
        return self.index_path / "faiss.index"

    @property
    def _metadata_file(self) -> Path:
        return self.index_path / "metadata.pkl"

    def _load_index(self):
        """Load existing FAISS index and metadata from disk."""
        index_file = self._index_file
        metadata_file = self._metadata_file

        try:
            if index_file.exists() and metadata_file.exists():
                loaded_index = faiss.read_index(str(index_file))
                if loaded_index.d != self.dimension:
                    logger.error(
                        f"On-disk vector index has dimension {loaded_index.d} but the "
                        f"configured embedding dimension is {self.dimension}. Ignoring the "
                        f"stale index - run POST /knowledge/reindex to rebuild it."
                    )
                    return
                self.index = loaded_index
                with open(metadata_file, 'rb') as f:
                    data = pickle.load(f)
                    self.document_metadata = data.get('metadata', {})
                    self.next_id = data.get('next_id', 0)
                try:
                    self._loaded_mtime = index_file.stat().st_mtime
                except OSError:
                    self._loaded_mtime = 0.0
                logger.info(f"Loaded vector index with {self.index.ntotal} vectors")
            else:
                logger.warning(
                    f"No vector index found at {self.index_path}. The knowledge base will "
                    f"return no results until documents are indexed (POST /knowledge/reindex)."
                )
        except Exception as e:
            logger.warning(f"Could not load existing index: {e}")
            # Reset to empty index
            self.index = faiss.IndexFlatIP(self.dimension)
            self.document_metadata = {}
            self.next_id = 0

    def reload_if_stale(self) -> bool:
        """
        Reload the index from disk if it has changed since we last loaded it.
        Lets a long-lived process pick up a rebuild performed by /knowledge/reindex.
        Returns True if a reload happened.
        """
        try:
            if not self._index_file.exists():
                return False
            mtime = self._index_file.stat().st_mtime
            if mtime > self._loaded_mtime:
                logger.info("Vector index on disk changed - reloading")
                self._load_index()
                return True
        except Exception as e:
            logger.warning(f"Could not check vector index freshness: {e}")
        return False

    def reset(self):
        """Drop every vector and start from an empty index (used by full reindex)."""
        self.index = faiss.IndexFlatIP(self.dimension)
        self.document_metadata = {}
        self.next_id = 0
        self._save_index()
        logger.info("Vector index reset to empty")
    
    def _save_index(self):
        """Save FAISS index and metadata to disk atomically (write temp + rename)
        so a concurrent reader never sees a half-written index."""
        try:
            index_file = self._index_file
            metadata_file = self._metadata_file
            tmp_index = index_file.with_suffix(".index.tmp")
            tmp_meta = metadata_file.with_suffix(".pkl.tmp")

            faiss.write_index(self.index, str(tmp_index))
            with open(tmp_meta, 'wb') as f:
                pickle.dump({
                    'metadata': self.document_metadata,
                    'next_id': self.next_id
                }, f)

            os.replace(tmp_index, index_file)
            os.replace(tmp_meta, metadata_file)

            try:
                self._loaded_mtime = index_file.stat().st_mtime
            except OSError:
                pass
            logger.info(f"Saved vector index with {self.index.ntotal} vectors")
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
            raise
    
    def add_document(self, document_id: str, content_chunks: List[str],
                    embeddings: List[List[float]], metadata: Dict[str, Any],
                    chunk_metadata: Optional[List[Dict[str, Any]]] = None,
                    save: bool = True) -> List[int]:
        """
        Add document chunks and their embeddings to the vector database.

        Args:
            document_id: Unique document identifier
            content_chunks: List of text chunks
            embeddings: List of embedding vectors for each chunk
            metadata: Document-level metadata applied to every chunk
            chunk_metadata: Optional per-chunk metadata (e.g. section heading)
            save: Persist to disk immediately (set False for bulk reindex, then
                  call save_index() once at the end)

        Returns:
            List of vector IDs assigned to the chunks
        """
        if len(content_chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")

        vector_ids = []
        vectors = np.array(embeddings, dtype=np.float32)

        # Normalize vectors for cosine similarity
        faiss.normalize_L2(vectors)

        for i, (chunk, embedding) in enumerate(zip(content_chunks, embeddings)):
            vector_id = self.next_id
            extra = (chunk_metadata[i] if chunk_metadata and i < len(chunk_metadata) else {})
            self.document_metadata[vector_id] = {
                'document_id': document_id,
                'content_chunk': chunk,
                'chunk_index': i,
                **metadata,
                **extra,
            }
            vector_ids.append(vector_id)
            self.next_id += 1

        # Add vectors to index
        self.index.add(vectors)

        # Save to disk
        if save:
            self._save_index()

        logger.info(f"Added {len(content_chunks)} chunks for document {document_id}")
        return vector_ids

    def save_index(self):
        """Public wrapper to flush the index to disk (used after bulk add)."""
        self._save_index()
    
    def search(self, query_embedding: List[float], k: int = 10, 
              filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for similar documents using vector similarity.
        
        Args:
            query_embedding: Query vector
            k: Number of results to return
            filters: Optional filters to apply (machine_model, document_type, etc.)
            
        Returns:
            List of search results with metadata and scores
        """
        if self.index.ntotal == 0:
            return []
        
        # Normalize query vector
        query_vector = np.array([query_embedding], dtype=np.float32)
        faiss.normalize_L2(query_vector)
        
        # Search in FAISS index
        scores, indices = self.index.search(query_vector, min(k * 2, self.index.ntotal))
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for empty slots
                continue
                
            metadata = self.document_metadata.get(idx, {})

            # Skip chunks belonging to deleted documents (FAISS has no real delete)
            if metadata.get('deleted', False):
                continue

            # Apply filters if provided
            if filters:
                if not self._matches_filters(metadata, filters):
                    continue
            
            results.append({
                'vector_id': int(idx),
                'document_id': metadata.get('document_id'),
                'content_chunk': metadata.get('content_chunk', ''),
                'chunk_index': metadata.get('chunk_index', 0),
                'relevance_score': float(score),
                'metadata': metadata
            })
            
            if len(results) >= k:
                break
        
        return results
    
    def _matches_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if metadata matches the provided filters."""
        for key, value in filters.items():
            if key == 'machine_model':
                machine_models = metadata.get('machine_models', [])
                if value not in machine_models:
                    return False
            elif key == 'document_type':
                if metadata.get('document_type') != value:
                    return False
            elif key == 'language':
                if metadata.get('language') != value:
                    return False
            elif key in metadata:
                if metadata[key] != value:
                    return False
        return True
    
    def delete_document(self, document_id: str) -> int:
        """
        Delete all chunks for a document from the vector database.
        Note: FAISS doesn't support deletion, so we mark as deleted in metadata.
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            Number of chunks marked as deleted
        """
        deleted_count = 0
        for vector_id, metadata in self.document_metadata.items():
            if metadata.get('document_id') == document_id:
                metadata['deleted'] = True
                deleted_count += 1
        
        if deleted_count > 0:
            self._save_index()
            logger.info(f"Marked {deleted_count} chunks as deleted for document {document_id}")
        
        return deleted_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector database statistics."""
        total_vectors = self.index.ntotal
        active_vectors = sum(1 for meta in self.document_metadata.values() 
                           if not meta.get('deleted', False))
        
        return {
            'total_vectors': total_vectors,
            'active_vectors': active_vectors,
            'deleted_vectors': total_vectors - active_vectors,
            'dimension': self.dimension,
            'index_path': str(self.index_path)
        }
    
    def rebuild_index(self):
        """
        Rebuild the index excluding deleted vectors.
        This is expensive but necessary for cleanup.
        """
        logger.info("Rebuilding vector index to remove deleted vectors")
        
        # Collect active vectors and metadata
        active_vectors = []
        active_metadata = {}
        new_id = 0
        
        for vector_id, metadata in self.document_metadata.items():
            if not metadata.get('deleted', False):
                # Get the vector from the index
                vector = self.index.reconstruct(vector_id)
                active_vectors.append(vector)
                active_metadata[new_id] = metadata
                new_id += 1
        
        if not active_vectors:
            # Empty index
            self.index = faiss.IndexFlatIP(self.dimension)
            self.document_metadata = {}
            self.next_id = 0
        else:
            # Create new index with active vectors
            vectors_array = np.array(active_vectors, dtype=np.float32)
            self.index = faiss.IndexFlatIP(self.dimension)
            self.index.add(vectors_array)
            self.document_metadata = active_metadata
            self.next_id = new_id
        
        self._save_index()
        logger.info(f"Index rebuilt with {len(active_vectors)} active vectors")