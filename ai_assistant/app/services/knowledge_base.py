"""
Knowledge base service for document management and search.
"""

import json
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import PyPDF2
import io

from sqlalchemy.orm import Session
from sqlalchemy import text, and_, or_

from ..database import get_db_session
from ..llm_client import LLMClient
from .vector_database import VectorDatabase
from ..models import DocumentType

logger = logging.getLogger(__name__)


class KnowledgeBaseService:
    """
    Service for managing knowledge base documents and search.
    """
    
    def __init__(self, llm_client: LLMClient, vector_db: VectorDatabase):
        """
        Initialize knowledge base service.
        
        Args:
            llm_client: LLM client for generating embeddings
            vector_db: Vector database for similarity search
        """
        self.llm_client = llm_client
        self.vector_db = vector_db
        self.chunk_size = 1000  # Characters per chunk
        self.chunk_overlap = 200  # Overlap between chunks
    
    async def create_document(self, title: str, content: str, document_type: str,
                            machine_models: List[str], tags: List[str], 
                            language: str = "en", version: str = "1.0",
                            file_path: Optional[str] = None,
                            metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new knowledge document with embeddings.
        
        Args:
            title: Document title
            content: Document content
            document_type: Type of document
            machine_models: List of applicable machine models
            tags: List of tags
            language: Document language
            version: Document version
            file_path: Path to original file
            metadata: Additional metadata
            
        Returns:
            Document ID
        """
        document_id = str(uuid.uuid4())
        
        try:
            # Store document in database
            with get_db_session() as db:
                db.execute(text("""
                    INSERT INTO knowledge_documents 
                    (document_id, title, content, document_type, machine_models, tags, 
                     language, version, file_path, document_metadata, created_at, updated_at)
                    VALUES (:document_id, :title, :content, :document_type, :machine_models, 
                            :tags, :language, :version, :file_path, :metadata, NOW(), NOW())
                """), {
                    'document_id': document_id,
                    'title': title,
                    'content': content,
                    'document_type': document_type,
                    'machine_models': machine_models,
                    'tags': tags,
                    'language': language,
                    'version': version,
                    'file_path': file_path,
                    'metadata': json.dumps(metadata or {})
                })
            
            # Generate embeddings and store in vector database
            await self._generate_and_store_embeddings(document_id, content, {
                'title': title,
                'document_type': document_type,
                'machine_models': machine_models,
                'tags': tags,
                'language': language,
                'version': version
            })
            
            logger.info(f"Created knowledge document: {document_id}")
            return document_id
            
        except Exception as e:
            logger.error(f"Failed to create document: {e}")
            # Cleanup on failure
            try:
                self.vector_db.delete_document(document_id)
                with get_db_session() as db:
                    db.execute(text("DELETE FROM knowledge_documents WHERE document_id = :id"), 
                             {'id': document_id})
            except:
                pass
            raise
    
    async def update_document(self, document_id: str, **updates) -> bool:
        """
        Update an existing knowledge document.
        
        Args:
            document_id: Document ID to update
            **updates: Fields to update
            
        Returns:
            True if successful
        """
        try:
            # Build update query
            set_clauses = []
            params = {'document_id': document_id}
            
            for field, value in updates.items():
                if field in ['title', 'content', 'document_type', 'language', 'version', 'file_path']:
                    set_clauses.append(f"{field} = :{field}")
                    params[field] = value
                elif field in ['machine_models', 'tags']:
                    set_clauses.append(f"{field} = :{field}")
                    params[field] = value
                elif field == 'metadata':
                    set_clauses.append("document_metadata = :metadata")
                    params['metadata'] = json.dumps(value)
            
            if not set_clauses:
                return True
            
            set_clauses.append("updated_at = NOW()")
            query = f"UPDATE knowledge_documents SET {', '.join(set_clauses)} WHERE document_id = :document_id"
            
            with get_db_session() as db:
                result = db.execute(text(query), params)
                if result.rowcount == 0:
                    return False
            
            # If content was updated, regenerate embeddings
            if 'content' in updates:
                # Delete old embeddings
                self.vector_db.delete_document(document_id)
                
                # Get updated document metadata
                doc_metadata = await self._get_document_metadata(document_id)
                if doc_metadata:
                    await self._generate_and_store_embeddings(
                        document_id, updates['content'], doc_metadata
                    )
            
            logger.info(f"Updated knowledge document: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update document {document_id}: {e}")
            raise
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a knowledge document and its embeddings.
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            True if successful
        """
        try:
            # Delete from vector database
            self.vector_db.delete_document(document_id)
            
            # Delete from SQL database
            with get_db_session() as db:
                result = db.execute(text("""
                    DELETE FROM knowledge_documents WHERE document_id = :document_id
                """), {'document_id': document_id})
                
                if result.rowcount == 0:
                    return False
            
            logger.info(f"Deleted knowledge document: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            raise
    
    async def search_documents(self, query: str, machine_model: Optional[str] = None,
                             document_type: Optional[str] = None, language: str = "en",
                             limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search knowledge base documents using vector similarity.
        
        Args:
            query: Search query
            machine_model: Filter by machine model
            document_type: Filter by document type
            language: Search language
            limit: Maximum number of results
            
        Returns:
            List of search results with relevance scores
        """
        try:
            # Generate query embedding
            query_embedding = await self.llm_client.generate_embedding(query)
            
            # Prepare filters
            filters = {'language': language}
            if machine_model:
                filters['machine_model'] = machine_model
            if document_type:
                filters['document_type'] = document_type
            
            # Search vector database
            vector_results = self.vector_db.search(
                query_embedding, k=limit * 2, filters=filters
            )
            
            # Group results by document and get document details
            document_results = {}
            for result in vector_results:
                doc_id = result['document_id']
                if doc_id not in document_results:
                    document_results[doc_id] = {
                        'document_id': doc_id,
                        'chunks': [],
                        'max_score': result['relevance_score']
                    }
                else:
                    document_results[doc_id]['max_score'] = max(
                        document_results[doc_id]['max_score'],
                        result['relevance_score']
                    )
                
                document_results[doc_id]['chunks'].append({
                    'content': result['content_chunk'],
                    'chunk_index': result['chunk_index'],
                    'score': result['relevance_score']
                })
            
            # Get document details from database
            final_results = []
            for doc_id, doc_data in document_results.items():
                doc_details = await self._get_document_details(doc_id)
                if doc_details:
                    # Find best matching chunk
                    best_chunk = max(doc_data['chunks'], key=lambda x: x['score'])
                    
                    final_results.append({
                        'document': doc_details,
                        'relevance_score': doc_data['max_score'],
                        'matched_content': best_chunk['content'][:500] + "..." if len(best_chunk['content']) > 500 else best_chunk['content']
                    })
            
            # Sort by relevance score and limit results
            final_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            return final_results[:limit]
            
        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            raise
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific document by ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document details or None if not found
        """
        return await self._get_document_details(document_id)
    
    async def list_documents(self, document_type: Optional[str] = None,
                           machine_model: Optional[str] = None,
                           language: Optional[str] = None,
                           limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List documents with optional filters.
        
        Args:
            document_type: Filter by document type
            machine_model: Filter by machine model
            language: Filter by language
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of documents
        """
        try:
            # Build query with filters
            where_clauses = []
            params = {'limit': limit, 'offset': offset}
            
            if document_type:
                where_clauses.append("document_type = :document_type")
                params['document_type'] = document_type
            
            if machine_model:
                where_clauses.append(":machine_model = ANY(machine_models)")
                params['machine_model'] = machine_model
            
            if language:
                where_clauses.append("language = :language")
                params['language'] = language
            
            where_clause = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
            
            query = f"""
                SELECT document_id, title, document_type, machine_models, tags, 
                       language, version, file_path, created_at, updated_at,
                       LEFT(content, 200) as content_preview
                FROM knowledge_documents
                {where_clause}
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
            """
            
            with get_db_session() as db:
                result = db.execute(text(query), params)
                documents = []
                
                for row in result:
                    documents.append({
                        'document_id': str(row.document_id),
                        'title': row.title,
                        'document_type': row.document_type,
                        'machine_models': row.machine_models or [],
                        'tags': row.tags or [],
                        'language': row.language,
                        'version': row.version,
                        'file_path': row.file_path,
                        'content_preview': row.content_preview,
                        'created_at': row.created_at,
                        'updated_at': row.updated_at
                    })
                
                return documents
                
        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            raise
    
    async def process_pdf_file(self, file_content: bytes, filename: str) -> str:
        """
        Extract text content from PDF file.
        
        Args:
            file_content: PDF file content as bytes
            filename: Original filename
            
        Returns:
            Extracted text content
        """
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_content = []
            for page in pdf_reader.pages:
                text_content.append(page.extract_text())
            
            content = "\n\n".join(text_content)
            logger.info(f"Extracted {len(content)} characters from PDF: {filename}")
            return content
            
        except Exception as e:
            logger.error(f"Failed to process PDF {filename}: {e}")
            raise
    
    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks for embedding.
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 100 characters
                sentence_end = text.rfind('.', end - 100, end)
                if sentence_end > start:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    async def _generate_and_store_embeddings(self, document_id: str, content: str, 
                                           metadata: Dict[str, Any]):
        """
        Generate embeddings for document content and store in vector database.
        
        Args:
            document_id: Document ID
            content: Document content
            metadata: Document metadata
        """
        # Split content into chunks
        chunks = self._chunk_text(content)
        
        # Generate embeddings for all chunks
        embeddings = []
        for chunk in chunks:
            embedding = await self.llm_client.generate_embedding(chunk)
            embeddings.append(embedding)
        
        # Store in vector database
        self.vector_db.add_document(document_id, chunks, embeddings, metadata)
        
        logger.info(f"Generated {len(embeddings)} embeddings for document {document_id}")
    
    async def _get_document_details(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get full document details from database."""
        try:
            with get_db_session() as db:
                result = db.execute(text("""
                    SELECT document_id, title, content, document_type, machine_models, tags,
                           language, version, file_path, document_metadata, created_at, updated_at
                    FROM knowledge_documents
                    WHERE document_id = :document_id
                """), {'document_id': document_id})
                
                row = result.fetchone()
                if not row:
                    return None
                
                metadata = {}
                if row.document_metadata:
                    try:
                        metadata = json.loads(row.document_metadata)
                    except:
                        pass
                
                return {
                    'document_id': str(row.document_id),
                    'title': row.title,
                    'content': row.content,
                    'document_type': row.document_type,
                    'machine_models': row.machine_models or [],
                    'tags': row.tags or [],
                    'language': row.language,
                    'version': row.version,
                    'file_path': row.file_path,
                    'metadata': metadata,
                    'created_at': row.created_at,
                    'updated_at': row.updated_at
                }
                
        except Exception as e:
            logger.error(f"Failed to get document details for {document_id}: {e}")
            return None
    
    async def _get_document_metadata(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document metadata for embedding generation."""
        try:
            with get_db_session() as db:
                result = db.execute(text("""
                    SELECT title, document_type, machine_models, tags, language, version
                    FROM knowledge_documents
                    WHERE document_id = :document_id
                """), {'document_id': document_id})
                
                row = result.fetchone()
                if not row:
                    return None
                
                return {
                    'title': row.title,
                    'document_type': row.document_type,
                    'machine_models': row.machine_models or [],
                    'tags': row.tags or [],
                    'language': row.language,
                    'version': row.version
                }
                
        except Exception as e:
            logger.error(f"Failed to get document metadata for {document_id}: {e}")
            return None