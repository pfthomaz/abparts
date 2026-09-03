"""
Knowledge base service for document management and search.
"""

import asyncio
import hashlib
import json
import re
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
from ..config import settings

logger = logging.getLogger(__name__)

# Lines that introduce a section - used to keep procedures whole and to attach
# section context to every chunk so retrieval stays grounded.
_HEADING_PATTERNS = [
    re.compile(r'^\s*#{1,6}\s+\S'),                                  # markdown headings
    re.compile(r'^\s*(section|chapter|appendix)\s+[0-9ivxlc]+', re.I),
    re.compile(r'^\s*[0-9]+(\.[0-9]+){0,3}\.?\s+[A-Z(].{2,80}$'),    # "8.3 Pre-operation Check"
    re.compile(r'^\s*step\s+[0-9]+\b', re.I),                        # "Step 3 ..."
    re.compile(r'^\s*[A-Z][A-Z0-9 ,/&\-]{6,70}$'),                   # ALL-CAPS heading lines
]


class KnowledgeBaseService:
    """
    Service for managing knowledge base documents and search.
    """

    # Set once per process after we confirm document_chunks.embedding exists.
    _embedding_column_checked = False

    def __init__(self, llm_client: LLMClient, vector_db: VectorDatabase):
        """
        Initialize knowledge base service.

        Args:
            llm_client: LLM client for generating embeddings
            vector_db: Vector database for similarity search
        """
        self.llm_client = llm_client
        self.vector_db = vector_db
        self.chunk_size = settings.KB_CHUNK_SIZE
        self.chunk_overlap = settings.KB_CHUNK_OVERLAP
        self.embedding_model = settings.OPENAI_EMBEDDING_MODEL
        self.min_relevance = settings.KB_SEARCH_MIN_RELEVANCE
        self.neighbor_radius = settings.KB_SEARCH_NEIGHBOR_RADIUS
        self.max_context_chunks = settings.KB_SEARCH_MAX_CONTEXT_CHUNKS
    
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
        content_hash = hashlib.sha256((content or "").encode("utf-8", "ignore")).hexdigest()

        try:
            self._ensure_embedding_column()

            # De-duplicate: if the exact same content was already ingested, replace it
            # so a re-upload refreshes the entry instead of hitting the unique constraint.
            with get_db_session() as db:
                existing = db.execute(
                    text("SELECT id FROM knowledge_documents WHERE file_hash = :h"),
                    {'h': content_hash}
                ).fetchone()
            if existing:
                logger.info(f"Identical content already indexed ({existing[0]}); replacing it")
                await self.delete_document(str(existing[0]))

            # Store document row
            with get_db_session() as db:
                db.execute(text("""
                    INSERT INTO knowledge_documents
                    (id, title, document_type, language, version, file_path, file_hash,
                     document_metadata, chunk_count, machine_models, tags)
                    VALUES (:document_id, :title, :document_type, :language, :version, :file_path,
                            :file_hash, :metadata, 0, :machine_models, :tags)
                """), {
                    'document_id': document_id,
                    'title': title,
                    'document_type': document_type,
                    'language': language,
                    'version': version,
                    'file_path': file_path,
                    'file_hash': content_hash,
                    'metadata': json.dumps(metadata or {}),
                    'machine_models': machine_models,
                    'tags': tags,
                })

            doc_metadata = {
                'title': title,
                'document_type': document_type,
                'machine_models': machine_models,
                'tags': tags,
                'language': language,
                'version': version,
            }

            chunk_count = await self._index_document_content(
                document_id, title, content, doc_metadata, write_chunks=True
            )

            logger.info(f"Created knowledge document {document_id} with {chunk_count} chunks")
            return document_id

        except Exception as e:
            logger.error(f"Failed to create document: {e}")
            # Cleanup on failure
            try:
                self.vector_db.delete_document(document_id)
                with get_db_session() as db:
                    db.execute(text("DELETE FROM knowledge_documents WHERE id = :id"),
                             {'id': document_id})
            except Exception:
                pass
            raise

    def _ensure_embedding_column(self):
        """Make sure the columns we rely on exist (older deployments may lack some)."""
        if KnowledgeBaseService._embedding_column_checked:
            return
        try:
            with get_db_session() as db:
                db.execute(text(
                    "ALTER TABLE document_chunks ADD COLUMN IF NOT EXISTS embedding JSONB"
                ))
                db.execute(text(
                    "ALTER TABLE knowledge_documents ADD COLUMN IF NOT EXISTS file_hash VARCHAR"
                ))
            KnowledgeBaseService._embedding_column_checked = True
        except Exception as e:
            logger.warning(f"Could not verify knowledge base columns: {e}")

    async def _embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a batch of texts with bounded concurrency.
        Propagates errors so callers can distinguish 'no match' from 'embedding down'.
        """
        semaphore = asyncio.Semaphore(max(1, settings.KB_EMBED_CONCURRENCY))

        async def _one(t: str) -> List[float]:
            async with semaphore:
                return await self.llm_client.generate_embedding(t, model=self.embedding_model)

        return await asyncio.gather(*[_one(t) for t in texts])

    async def _index_document_content(self, document_id: str, title: str, content: str,
                                      doc_metadata: Dict[str, Any],
                                      *, write_chunks: bool = True) -> int:
        """
        (Re)build the chunks, embeddings and vector entries for one document.
        Replaces any existing chunks/vectors for that document id.
        """
        chunks = self._chunk_document(title, content)
        if not chunks:
            logger.warning(f"Document {document_id} produced no chunks")
            return 0

        texts = [c['text'] for c in chunks]
        embeddings = await self._embed_texts(texts)

        # Record which model produced these embeddings so a later reindex knows
        # whether it can reuse them or must re-embed.
        doc_metadata = {
            **doc_metadata,
            'embedding_model': self.embedding_model,
            'embedding_dim': self.vector_db.dimension,
        }

        # Refresh vector store entries for this document
        self.vector_db.delete_document(document_id)
        self.vector_db.add_document(
            document_id, texts, embeddings, doc_metadata,
            chunk_metadata=[{'section': c['heading']} for c in chunks],
            save=True,
        )

        if write_chunks:
            self._ensure_embedding_column()
            with get_db_session() as db:
                db.execute(text("DELETE FROM document_chunks WHERE document_id = :d"),
                           {'d': document_id})
                for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
                    db.execute(text("""
                        INSERT INTO document_chunks (id, document_id, chunk_index, content, embedding)
                        VALUES (:id, :document_id, :chunk_index, :content, :embedding)
                    """), {
                        'id': f"{document_id}_chunk_{i}",
                        'document_id': document_id,
                        'chunk_index': i,
                        'content': chunk['text'],
                        'embedding': json.dumps(emb),
                    })
                # Merge embedding-model provenance into document_metadata
                row = db.execute(text(
                    "SELECT document_metadata FROM knowledge_documents WHERE id = :d"
                ), {'d': document_id}).fetchone()
                meta = {}
                if row and row.document_metadata:
                    meta = row.document_metadata if isinstance(row.document_metadata, dict) \
                        else json.loads(row.document_metadata)
                meta['embedding_model'] = self.embedding_model
                meta['embedding_dim'] = self.vector_db.dimension
                db.execute(text(
                    "UPDATE knowledge_documents SET chunk_count = :c, document_metadata = :m, "
                    "updated_at = NOW() WHERE id = :d"
                ), {'c': len(chunks), 'm': json.dumps(meta), 'd': document_id})

        return len(chunks)
    
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
                if field in ['title', 'document_type', 'language', 'version', 'file_path']:
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
            query = f"UPDATE knowledge_documents SET {', '.join(set_clauses)} WHERE id = :document_id"
            
            with get_db_session() as db:
                result = db.execute(text(query), params)
                if result.rowcount == 0:
                    return False
            
            # If content was updated, regenerate chunks + embeddings + vectors
            if 'content' in updates:
                doc_metadata = await self._get_document_metadata(document_id)
                if doc_metadata:
                    new_hash = hashlib.sha256(
                        (updates['content'] or "").encode("utf-8", "ignore")
                    ).hexdigest()
                    with get_db_session() as db:
                        db.execute(text(
                            "UPDATE knowledge_documents SET file_hash = :h WHERE id = :d"
                        ), {'h': new_hash, 'd': document_id})
                    await self._index_document_content(
                        document_id,
                        doc_metadata.get('title', ''),
                        updates['content'],
                        doc_metadata,
                        write_chunks=True,
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
            
            # Delete from SQL database (document_chunks will be deleted by CASCADE)
            with get_db_session() as db:
                result = db.execute(text("""
                    DELETE FROM knowledge_documents WHERE id = :document_id
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
                             limit: int = 10,
                             min_relevance: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Search knowledge base documents using vector similarity.

        Thin wrapper around multi_search() for a single query - kept for the
        existing /knowledge/search endpoint and callers.
        """
        return await self.multi_search(
            [query], machine_model=machine_model, document_type=document_type,
            language=language, limit=limit, min_relevance=min_relevance,
        )

    async def multi_search(self, queries: List[str], machine_model: Optional[str] = None,
                           document_type: Optional[str] = None, language: str = "en",
                           limit: Optional[int] = None,
                           min_relevance: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant knowledge chunks for one or more queries.

        - Runs every query, keeps the best score per (document, chunk).
        - Machine model AND language are soft ranking boosts, NOT hard filters:
          the manuals are English-only, so a Greek/Arabic/etc. question must
          still be able to match them (the embedding model is multilingual).
          The LLM answers in the user's language regardless.
        - Pulls neighbouring chunks so procedures/tables are not cut mid-step.
        - Returns one entry per matched chunk (granular context for the LLM),
          each shaped like the old result: {document, relevance_score, matched_content}.
        """
        limit = limit or self.max_context_chunks
        threshold = self.min_relevance if min_relevance is None else min_relevance

        # De-duplicate queries, drop empties
        seen_q = set()
        clean_queries = []
        for q in queries:
            q = (q or "").strip()
            if q and q.lower() not in seen_q:
                seen_q.add(q.lower())
                clean_queries.append(q)
        if not clean_queries:
            return []

        try:
            query_embeddings = await self._embed_texts(clean_queries)
        except Exception as e:
            logger.error(f"Failed to embed search queries: {e}")
            raise

        # Only hard-filter on document_type. Language is a soft boost (see docstring).
        filters: Dict[str, Any] = {}
        if document_type:
            filters['document_type'] = document_type

        # best score per (doc_id, chunk_index)
        best: Dict[Tuple[str, int], Dict[str, Any]] = {}
        per_query_k = max(limit * 3, 20)
        for emb in query_embeddings:
            for r in self.vector_db.search(emb, k=per_query_k, filters=filters):
                key = (r['document_id'], r['chunk_index'])
                if key not in best or r['relevance_score'] > best[key]['score']:
                    best[key] = {
                        'document_id': r['document_id'],
                        'chunk_index': r['chunk_index'],
                        'content': r['content_chunk'],
                        'score': r['relevance_score'],
                    }

        if not best:
            return []

        # Hydrate document details + all chunks once per document
        doc_ids = {k[0] for k in best}
        doc_details = {d: await self._get_document_details(d) for d in doc_ids}
        doc_chunks = {d: await self._get_document_chunk_map(d) for d in doc_ids}

        # Soft boosts / penalties - never exclude, only re-rank
        def adjust(entry: Dict[str, Any]) -> float:
            score = entry['score']
            det = doc_details.get(entry['document_id']) or {}
            models = det.get('machine_models') or []
            if machine_model:
                if not models or 'ALL' in models:
                    score += 0.03
                elif machine_model in models:
                    score += 0.08
                else:
                    score -= 0.05
            if language and det.get('language') == language:
                score += 0.02
            if det.get('document_type') == 'support_case':
                score += 0.05  # verified field experience
            return score

        ranked = sorted(best.values(), key=adjust, reverse=True)
        ranked = [e for e in ranked if adjust(e) >= threshold][:limit]

        # Neighbour expansion so the LLM sees complete procedures
        selected: Dict[Tuple[str, int], float] = {}
        for e in ranked:
            selected[(e['document_id'], e['chunk_index'])] = adjust(e)
            for delta in range(1, self.neighbor_radius + 1):
                for nb in (e['chunk_index'] - delta, e['chunk_index'] + delta):
                    cmap = doc_chunks.get(e['document_id'], {})
                    if nb in cmap and (e['document_id'], nb) not in selected:
                        selected[(e['document_id'], nb)] = adjust(e) - 0.001 * delta

        results: List[Dict[str, Any]] = []
        for (doc_id, chunk_idx), score in selected.items():
            det = doc_details.get(doc_id)
            if not det:
                continue
            content = doc_chunks.get(doc_id, {}).get(chunk_idx) or best.get((doc_id, chunk_idx), {}).get('content', '')
            if not content:
                continue
            results.append({
                'document': det,
                'relevance_score': round(float(score), 4),
                'matched_content': content,
                'chunk_index': chunk_idx,
            })

        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:limit]

    async def _get_document_chunk_map(self, document_id: str) -> Dict[int, str]:
        """Return {chunk_index: content} for a document."""
        try:
            with get_db_session() as db:
                rows = db.execute(text("""
                    SELECT chunk_index, content FROM document_chunks
                    WHERE document_id = :d ORDER BY chunk_index
                """), {'d': document_id}).fetchall()
            return {row.chunk_index: row.content for row in rows}
        except Exception as e:
            logger.warning(f"Could not load chunk map for {document_id}: {e}")
            return {}

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
                SELECT kd.id, kd.title, kd.document_type, kd.language, kd.version, kd.file_path, 
                       kd.created_at, kd.updated_at, kd.machine_models, kd.tags, kd.document_metadata,
                       STRING_AGG(dc.content, ' ' ORDER BY dc.chunk_index) as content
                FROM knowledge_documents kd
                LEFT JOIN document_chunks dc ON kd.id = dc.document_id
                {where_clause}
                GROUP BY kd.id, kd.title, kd.document_type, kd.language, kd.version, kd.file_path,
                         kd.created_at, kd.updated_at, kd.machine_models, kd.tags, kd.document_metadata
                ORDER BY kd.created_at DESC
                LIMIT :limit OFFSET :offset
            """
            
            with get_db_session() as db:
                result = db.execute(text(query), params)
                documents = []
                
                for row in result:
                    documents.append({
                        'document_id': str(row.id),
                        'title': row.title,
                        'content': row.content or '',  # Handle case where no chunks exist
                        'document_type': row.document_type,
                        'machine_models': row.machine_models or [],
                        'tags': row.tags or [],
                        'language': row.language,
                        'version': row.version,
                        'file_path': row.file_path,
                        'created_at': row.created_at,
                        'updated_at': row.updated_at,
                        'metadata': row.document_metadata or {}
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
    
    @staticmethod
    def _looks_like_heading(line: str) -> bool:
        line = line.strip()
        if not line or len(line) > 90:
            return False
        return any(p.match(line) for p in _HEADING_PATTERNS)

    def _split_into_sections(self, content: str) -> List[Tuple[str, str]]:
        """
        Break raw document text into (heading, body) sections using heading
        heuristics. Keeps whole procedures together so retrieval returns
        complete steps rather than fragments.
        """
        lines = content.splitlines()
        sections: List[Tuple[str, List[str]]] = []
        current_heading = ""
        current_body: List[str] = []

        for line in lines:
            if self._looks_like_heading(line):
                if current_body or current_heading:
                    sections.append((current_heading, current_body))
                current_heading = line.strip().lstrip('#').strip()
                current_body = []
            else:
                current_body.append(line)
        if current_body or current_heading:
            sections.append((current_heading, current_body))

        return [(h, "\n".join(b).strip()) for h, b in sections if "\n".join(b).strip() or h]

    def _chunk_document(self, title: str, content: str) -> List[Dict[str, Any]]:
        """
        Turn a document into overlapping, section-aware chunks.

        Every chunk is prefixed with "[<document title> - <section>]" so the
        embedded text (and the text shown to the LLM) always carries the context
        it came from. This markedly improves grounding for terse manual passages.

        Returns a list of {"text": <prefixed chunk>, "heading": <section>, "raw": <chunk>}.
        """
        content = (content or "").replace("\r\n", "\n").strip()
        if not content:
            return []

        sections = self._split_into_sections(content) or [("", content)]
        out: List[Dict[str, Any]] = []

        for heading, body in sections:
            for piece in self._sliding_window(body):
                piece = piece.strip()
                if len(piece) < 40:
                    continue
                ctx = f"[{title}" + (f" - {heading}]" if heading else "]")
                out.append({
                    'text': f"{ctx}\n{piece}",
                    'heading': heading,
                    'raw': piece,
                })

        # Fallback: never return zero chunks for non-trivial content
        if not out and len(content) >= 40:
            out.append({'text': f"[{title}]\n{content[:self.chunk_size]}",
                        'heading': '', 'raw': content[:self.chunk_size]})
        return out

    def _sliding_window(self, text_block: str) -> List[str]:
        """Overlapping windows over a single section body, broken on sentence/line ends."""
        text_block = text_block.strip()
        if len(text_block) <= self.chunk_size:
            return [text_block] if text_block else []

        chunks = []
        start = 0
        while start < len(text_block):
            end = start + self.chunk_size
            if end < len(text_block):
                best_break = -1
                for sep in ['.\n', '. ', '!\n', '! ', '?\n', '? ', '\n\n', '\n', '; ']:
                    pos = text_block.rfind(sep, start + (self.chunk_size // 2), end)
                    if pos > best_break:
                        best_break = pos + len(sep)
                if best_break > start:
                    end = best_break
            chunk = text_block[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = max(end - self.chunk_overlap, start + 1)
            if end >= len(text_block):
                break
        return chunks

    # Kept for backwards compatibility (unused internally).
    def _chunk_text(self, text: str) -> List[str]:
        return [c['raw'] for c in self._chunk_document("", text)]

    async def reindex_from_database(self, re_embed: bool = False) -> Dict[str, Any]:
        """
        Rebuild the FAISS vector index entirely from Postgres.

        Recovery path when the vector index is lost (e.g. container recreated
        without a persistent volume) but knowledge_documents / document_chunks
        are intact - no source PDFs required.

        Args:
            re_embed: if False, reuse embeddings stored on document_chunks and
                only call OpenAI for chunks that are missing one. If True,
                re-embed every chunk from its text (use after changing the
                embedding model).

        Returns a summary dict.
        """
        self._ensure_embedding_column()
        summary = {
            'documents': 0, 'chunks_indexed': 0,
            'embeddings_reused': 0, 'embeddings_generated': 0,
            'documents_skipped': 0, 're_embed': re_embed,
        }

        with get_db_session() as db:
            docs = db.execute(text("""
                SELECT id, title, document_type, language, version, machine_models, tags,
                       document_metadata
                FROM knowledge_documents
                ORDER BY created_at
            """)).fetchall()

        # Start from a clean index
        self.vector_db.reset()

        for doc in docs:
            document_id = str(doc.id)

            # Only reuse stored embeddings when they were produced by the model
            # we are currently querying with - otherwise the vector spaces differ
            # and similarity is meaningless.
            meta = {}
            if doc.document_metadata:
                meta = doc.document_metadata if isinstance(doc.document_metadata, dict) \
                    else json.loads(doc.document_metadata)
            stored_model = meta.get('embedding_model')
            reuse_ok = (not re_embed) and stored_model == self.embedding_model

            with get_db_session() as db:
                rows = db.execute(text("""
                    SELECT chunk_index, content, embedding
                    FROM document_chunks
                    WHERE document_id = :d
                    ORDER BY chunk_index
                """), {'d': document_id}).fetchall()

            if not rows:
                summary['documents_skipped'] += 1
                continue

            texts = [r.content for r in rows]
            embeddings: List[Optional[List[float]]] = []
            for r in rows:
                emb = None
                if reuse_ok and r.embedding:
                    emb = r.embedding if isinstance(r.embedding, list) else None
                    if emb is None:
                        try:
                            emb = json.loads(r.embedding)
                        except Exception:
                            emb = None
                if emb and len(emb) == self.vector_db.dimension:
                    embeddings.append(emb)
                else:
                    embeddings.append(None)

            # Fill any missing embeddings in one bounded-concurrency batch
            missing_idx = [i for i, e in enumerate(embeddings) if e is None]
            if missing_idx:
                generated = await self._embed_texts([texts[i] for i in missing_idx])
                for slot, emb in zip(missing_idx, generated):
                    embeddings[slot] = emb
                summary['embeddings_generated'] += len(missing_idx)
                # Persist the freshly generated embeddings back to Postgres
                with get_db_session() as db:
                    for slot in missing_idx:
                        db.execute(text("""
                            UPDATE document_chunks SET embedding = :e
                            WHERE document_id = :d AND chunk_index = :i
                        """), {'e': json.dumps(embeddings[slot]),
                               'd': document_id, 'i': rows[slot].chunk_index})
            summary['embeddings_reused'] += (len(rows) - len(missing_idx))

            # Stamp provenance so the next reindex can reuse these embeddings
            if not reuse_ok or missing_idx:
                meta['embedding_model'] = self.embedding_model
                meta['embedding_dim'] = self.vector_db.dimension
                with get_db_session() as db:
                    db.execute(text(
                        "UPDATE knowledge_documents SET document_metadata = :m WHERE id = :d"
                    ), {'m': json.dumps(meta), 'd': document_id})

            doc_metadata = {
                'title': doc.title,
                'document_type': doc.document_type,
                'machine_models': list(doc.machine_models or []),
                'tags': list(doc.tags or []),
                'language': doc.language,
                'version': doc.version,
                'embedding_model': self.embedding_model,
                'embedding_dim': self.vector_db.dimension,
            }
            self.vector_db.add_document(
                document_id, texts, embeddings, doc_metadata,
                chunk_metadata=None, save=False,
            )
            summary['documents'] += 1
            summary['chunks_indexed'] += len(rows)

        self.vector_db.save_index()
        stats = self.vector_db.get_stats()
        summary['vectors_in_index'] = stats.get('total_vectors', 0)
        logger.info(f"Reindex complete: {summary}")
        return summary

    async def _get_document_details(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get full document details from database."""
        try:
            with get_db_session() as db:
                result = db.execute(text("""
                    SELECT id, title, document_type, language, version, file_path, document_metadata, created_at, updated_at, machine_models, tags
                    FROM knowledge_documents
                    WHERE id = :document_id
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
                
                # Get content from document_chunks
                content_result = db.execute(text("""
                    SELECT content FROM document_chunks 
                    WHERE document_id = :document_id 
                    ORDER BY chunk_index
                """), {'document_id': document_id})
                
                content_chunks = [chunk_row.content for chunk_row in content_result]
                full_content = '\n\n'.join(content_chunks)
                
                return {
                    'document_id': str(row.id),
                    'title': row.title,
                    'content': full_content,
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
                    SELECT title, document_type, language, version, machine_models, tags
                    FROM knowledge_documents
                    WHERE id = :document_id
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