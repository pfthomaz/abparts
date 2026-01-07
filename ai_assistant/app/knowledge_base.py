"""
Knowledge Base management for AutoBoss AI Assistant.

This module provides functionality for storing, processing, and retrieving
AutoBoss documentation including PDF manuals, troubleshooting guides,
and expert knowledge.
"""

import logging
import hashlib
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import uuid
from pathlib import Path

import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from .models import KnowledgeDocument, DocumentChunk
from .database import get_db
from .config import settings

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Processes documents for knowledge base storage."""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.txt', '.md', '.docx']
        
    async def process_pdf(self, file_path: str) -> List[str]:
        """
        Extract text from PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of text chunks from the PDF
        """
        try:
            import PyPDF2
            
            chunks = []
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    if text.strip():
                        # Split into smaller chunks for better embedding
                        page_chunks = self._split_text_into_chunks(text, page_num + 1)
                        chunks.extend(page_chunks)
                        
            logger.info(f"Extracted {len(chunks)} chunks from PDF: {file_path}")
            return chunks
            
        except ImportError:
            logger.error("PyPDF2 not installed. Install with: pip install PyPDF2")
            raise
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {e}")
            raise
    
    async def process_text_file(self, file_path: str) -> List[str]:
        """
        Process plain text file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            List of text chunks
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            chunks = self._split_text_into_chunks(content)
            logger.info(f"Processed {len(chunks)} chunks from text file: {file_path}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing text file {file_path}: {e}")
            raise
    
    def _split_text_into_chunks(self, text: str, page_num: Optional[int] = None) -> List[str]:
        """
        Split text into manageable chunks for embedding.
        
        Args:
            text: Text to split
            page_num: Optional page number for PDF processing
            
        Returns:
            List of text chunks
        """
        # Clean and normalize text
        text = text.strip()
        if not text:
            return []
        
        # Split by paragraphs first
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = ""
        max_chunk_size = 1000  # Characters per chunk
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed max size, save current chunk
            if len(current_chunk) + len(paragraph) > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # Add page number context for PDF chunks
        if page_num is not None:
            chunks = [f"[Page {page_num}] {chunk}" for chunk in chunks]
        
        return chunks
    
    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file for duplicate detection."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()


class EmbeddingService:
    """Handles document embedding generation using OpenAI."""
    
    def __init__(self):
        self.model = "text-embedding-ada-002"
        self.max_tokens = 8191  # Max tokens for ada-002
        
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text chunks to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            import openai
            from openai import AsyncOpenAI
            
            if not settings.OPENAI_API_KEY:
                raise ValueError("OpenAI API key not configured")
            
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Process in batches to avoid rate limits
            batch_size = 100
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                # Truncate texts that are too long
                batch = [self._truncate_text(text) for text in batch]
                
                response = await client.embeddings.create(
                    model=self.model,
                    input=batch
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
                # Small delay to respect rate limits
                await asyncio.sleep(0.1)
            
            logger.info(f"Generated {len(all_embeddings)} embeddings")
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def _truncate_text(self, text: str) -> str:
        """Truncate text to fit within token limits."""
        # Rough estimation: 1 token ≈ 4 characters
        max_chars = self.max_tokens * 4
        if len(text) > max_chars:
            return text[:max_chars]
        return text
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)
        
        dot_product = np.dot(vec1_np, vec2_np)
        norm1 = np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)


class KnowledgeBaseManager:
    """Main knowledge base management class."""
    
    def __init__(self):
        self.processor = DocumentProcessor()
        self.embedding_service = EmbeddingService()
        
    async def add_document(
        self,
        file_path: str,
        title: str,
        document_type: str = "manual",
        version: Optional[str] = None,
        language: str = "en",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a document to the knowledge base.
        
        Args:
            file_path: Path to the document file
            title: Document title
            document_type: Type of document (manual, troubleshooting, etc.)
            version: AutoBoss version (e.g., "V4.0", "V3.1B")
            language: Document language
            metadata: Additional metadata
            
        Returns:
            Document ID
        """
        try:
            # Validate file exists and format is supported
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if path.suffix.lower() not in self.processor.supported_formats:
                raise ValueError(f"Unsupported file format: {path.suffix}")
            
            # Calculate file hash for duplicate detection
            file_hash = self.processor.calculate_file_hash(file_path)
            
            # Check for existing document with same hash
            db = next(get_db())
            existing = db.query(KnowledgeDocument).filter(
                KnowledgeDocument.file_hash == file_hash
            ).first()
            
            if existing:
                logger.warning(f"Document with same content already exists: {existing.id}")
                return existing.id
            
            # Process document based on file type
            if path.suffix.lower() == '.pdf':
                text_chunks = await self.processor.process_pdf(file_path)
            else:
                text_chunks = await self.processor.process_text_file(file_path)
            
            if not text_chunks:
                raise ValueError("No text content extracted from document")
            
            # Generate embeddings for all chunks
            embeddings = await self.embedding_service.generate_embeddings(text_chunks)
            
            # Create document record
            document_id = str(uuid.uuid4())
            document = KnowledgeDocument(
                id=document_id,
                title=title,
                document_type=document_type,
                version=version,
                language=language,
                file_path=str(path),
                file_hash=file_hash,
                chunk_count=len(text_chunks),
                metadata=metadata or {},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(document)
            db.flush()  # Get the document ID
            
            # Create chunk records
            for i, (chunk_text, embedding) in enumerate(zip(text_chunks, embeddings)):
                chunk = DocumentChunk(
                    id=str(uuid.uuid4()),
                    document_id=document_id,
                    chunk_index=i,
                    content=chunk_text,
                    embedding=embedding,
                    created_at=datetime.utcnow()
                )
                db.add(chunk)
            
            db.commit()
            
            logger.info(f"Successfully added document: {title} ({len(text_chunks)} chunks)")
            return document_id
            
        except Exception as e:
            logger.error(f"Error adding document {title}: {e}")
            if 'db' in locals():
                db.rollback()
            raise
        finally:
            if 'db' in locals():
                db.close()
    
    async def search_documents(
        self,
        query: str,
        version: Optional[str] = None,
        document_type: Optional[str] = None,
        language: str = "en",
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant document chunks.
        
        Args:
            query: Search query
            version: Filter by AutoBoss version
            document_type: Filter by document type
            language: Document language
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of relevant document chunks with metadata
        """
        try:
            # Generate embedding for query
            query_embeddings = await self.embedding_service.generate_embeddings([query])
            query_embedding = query_embeddings[0]
            
            # Get database session
            db = next(get_db())
            
            # Build query filters
            filters = [KnowledgeDocument.language == language]
            
            if version:
                filters.append(KnowledgeDocument.version == version)
            
            if document_type:
                filters.append(KnowledgeDocument.document_type == document_type)
            
            # Get all chunks from matching documents
            chunks_query = db.query(DocumentChunk, KnowledgeDocument).join(
                KnowledgeDocument,
                DocumentChunk.document_id == KnowledgeDocument.id
            ).filter(and_(*filters))
            
            chunks = chunks_query.all()
            
            # Calculate similarities and rank results
            results = []
            for chunk, document in chunks:
                similarity = self.embedding_service.cosine_similarity(
                    query_embedding, chunk.embedding
                )
                
                if similarity >= similarity_threshold:
                    results.append({
                        'chunk_id': chunk.id,
                        'document_id': document.id,
                        'document_title': document.title,
                        'document_type': document.document_type,
                        'version': document.version,
                        'content': chunk.content,
                        'chunk_index': chunk.chunk_index,
                        'similarity': similarity,
                        'metadata': document.metadata
                    })
            
            # Sort by similarity and limit results
            results.sort(key=lambda x: x['similarity'], reverse=True)
            results = results[:limit]
            
            logger.info(f"Found {len(results)} relevant chunks for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise
        finally:
            if 'db' in locals():
                db.close()
    
    async def get_document_info(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific document."""
        try:
            db = next(get_db())
            document = db.query(KnowledgeDocument).filter(
                KnowledgeDocument.id == document_id
            ).first()
            
            if not document:
                return None
            
            return {
                'id': document.id,
                'title': document.title,
                'document_type': document.document_type,
                'version': document.version,
                'language': document.language,
                'chunk_count': document.chunk_count,
                'metadata': document.metadata,
                'created_at': document.created_at,
                'updated_at': document.updated_at
            }
            
        except Exception as e:
            logger.error(f"Error getting document info: {e}")
            raise
        finally:
            if 'db' in locals():
                db.close()
    
    async def list_documents(
        self,
        document_type: Optional[str] = None,
        version: Optional[str] = None,
        language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List all documents in the knowledge base."""
        try:
            db = next(get_db())
            
            query = db.query(KnowledgeDocument)
            
            if document_type:
                query = query.filter(KnowledgeDocument.document_type == document_type)
            
            if version:
                query = query.filter(KnowledgeDocument.version == version)
            
            if language:
                query = query.filter(KnowledgeDocument.language == language)
            
            documents = query.order_by(desc(KnowledgeDocument.created_at)).all()
            
            return [
                {
                    'id': doc.id,
                    'title': doc.title,
                    'document_type': doc.document_type,
                    'version': doc.version,
                    'language': doc.language,
                    'chunk_count': doc.chunk_count,
                    'created_at': doc.created_at,
                    'updated_at': doc.updated_at
                }
                for doc in documents
            ]
            
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            raise
        finally:
            if 'db' in locals():
                db.close()
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document and all its chunks."""
        try:
            db = next(get_db())
            
            # Delete chunks first
            db.query(DocumentChunk).filter(
                DocumentChunk.document_id == document_id
            ).delete()
            
            # Delete document
            result = db.query(KnowledgeDocument).filter(
                KnowledgeDocument.id == document_id
            ).delete()
            
            db.commit()
            
            if result > 0:
                logger.info(f"Successfully deleted document: {document_id}")
                return True
            else:
                logger.warning(f"Document not found: {document_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            if 'db' in locals():
                db.rollback()
            raise
        finally:
            if 'db' in locals():
                db.close()


# Global knowledge base manager instance
knowledge_base = KnowledgeBaseManager()