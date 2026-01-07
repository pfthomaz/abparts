"""
Knowledge base management API endpoints.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse

from ..schemas import (
    CreateKnowledgeDocumentRequest,
    UpdateKnowledgeDocumentRequest,
    SearchKnowledgeRequest,
    KnowledgeDocumentResponse,
    KnowledgeSearchResponse,
    ErrorResponse
)
from ..services.knowledge_base import KnowledgeBaseService
from ..services.vector_database import VectorDatabase
from ..llm_client import LLMClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/knowledge", tags=["knowledge_base"])

# Initialize services (these will be dependency injected in production)
llm_client = LLMClient()
vector_db = VectorDatabase()
knowledge_service = KnowledgeBaseService(llm_client, vector_db)


async def get_knowledge_service() -> KnowledgeBaseService:
    """Dependency to get knowledge base service."""
    return knowledge_service


@router.post("/documents", response_model=KnowledgeDocumentResponse)
async def create_document(
    request: CreateKnowledgeDocumentRequest,
    service: KnowledgeBaseService = Depends(get_knowledge_service)
):
    """
    Create a new knowledge document.
    
    Args:
        request: Document creation request
        service: Knowledge base service
        
    Returns:
        Created document details
    """
    try:
        document_id = await service.create_document(
            title=request.title,
            content=request.content,
            document_type=request.document_type,
            machine_models=request.machine_models,
            tags=request.tags,
            language=request.language,
            version=request.version,
            metadata=request.metadata
        )
        
        # Get the created document
        document = await service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=500, detail="Failed to retrieve created document")
        
        return KnowledgeDocumentResponse(**document)
        
    except Exception as e:
        logger.error(f"Failed to create document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/upload", response_model=KnowledgeDocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    document_type: str = Form(...),
    machine_models: str = Form(""),  # Comma-separated list
    tags: str = Form(""),  # Comma-separated list
    language: str = Form("en"),
    version: str = Form("1.0"),
    service: KnowledgeBaseService = Depends(get_knowledge_service)
):
    """
    Upload and process a document file (PDF or text).
    
    Args:
        file: Uploaded file
        title: Document title
        document_type: Type of document
        machine_models: Comma-separated machine models
        tags: Comma-separated tags
        language: Document language
        version: Document version
        service: Knowledge base service
        
    Returns:
        Created document details
    """
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_extension = file.filename.lower().split('.')[-1]
        if file_extension not in ['pdf', 'txt']:
            raise HTTPException(
                status_code=400, 
                detail="Only PDF and TXT files are supported"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Process file based on type
        if file_extension == 'pdf':
            content = await service.process_pdf_file(file_content, file.filename)
        else:
            content = file_content.decode('utf-8')
        
        # Parse comma-separated lists
        machine_models_list = [m.strip() for m in machine_models.split(',') if m.strip()]
        tags_list = [t.strip() for t in tags.split(',') if t.strip()]
        
        # Create document
        document_id = await service.create_document(
            title=title,
            content=content,
            document_type=document_type,
            machine_models=machine_models_list,
            tags=tags_list,
            language=language,
            version=version,
            file_path=file.filename
        )
        
        # Get the created document
        document = await service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=500, detail="Failed to retrieve created document")
        
        return KnowledgeDocumentResponse(**document)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/bulk-upload", response_model=List[KnowledgeDocumentResponse])
async def bulk_upload_documents(
    files: List[UploadFile] = File(...),
    document_type: str = Form(...),
    machine_models: str = Form(""),
    tags: str = Form(""),
    language: str = Form("en"),
    service: KnowledgeBaseService = Depends(get_knowledge_service)
):
    """
    Bulk upload multiple document files.
    
    Args:
        files: List of uploaded files
        document_type: Type of documents
        machine_models: Comma-separated machine models
        tags: Comma-separated tags
        language: Document language
        service: Knowledge base service
        
    Returns:
        List of created document details
    """
    try:
        if len(files) > 20:  # Limit bulk uploads
            raise HTTPException(status_code=400, detail="Maximum 20 files allowed per bulk upload")
        
        # Parse comma-separated lists
        machine_models_list = [m.strip() for m in machine_models.split(',') if m.strip()]
        tags_list = [t.strip() for t in tags.split(',') if t.strip()]
        
        created_documents = []
        
        for file in files:
            try:
                if not file.filename:
                    continue
                
                file_extension = file.filename.lower().split('.')[-1]
                if file_extension not in ['pdf', 'txt']:
                    logger.warning(f"Skipping unsupported file: {file.filename}")
                    continue
                
                # Read and process file
                file_content = await file.read()
                
                if file_extension == 'pdf':
                    content = await service.process_pdf_file(file_content, file.filename)
                else:
                    content = file_content.decode('utf-8')
                
                # Use filename as title (without extension)
                title = file.filename.rsplit('.', 1)[0]
                
                # Create document
                document_id = await service.create_document(
                    title=title,
                    content=content,
                    document_type=document_type,
                    machine_models=machine_models_list,
                    tags=tags_list,
                    language=language,
                    version="1.0",
                    file_path=file.filename
                )
                
                # Get the created document
                document = await service.get_document(document_id)
                if document:
                    created_documents.append(KnowledgeDocumentResponse(**document))
                
            except Exception as e:
                logger.error(f"Failed to process file {file.filename}: {e}")
                # Continue with other files
                continue
        
        return created_documents
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to bulk upload documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{document_id}", response_model=KnowledgeDocumentResponse)
async def get_document(
    document_id: str,
    service: KnowledgeBaseService = Depends(get_knowledge_service)
):
    """
    Get a specific document by ID.
    
    Args:
        document_id: Document ID
        service: Knowledge base service
        
    Returns:
        Document details
    """
    try:
        document = await service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return KnowledgeDocumentResponse(**document)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/documents/{document_id}", response_model=KnowledgeDocumentResponse)
async def update_document(
    document_id: str,
    request: UpdateKnowledgeDocumentRequest,
    service: KnowledgeBaseService = Depends(get_knowledge_service)
):
    """
    Update an existing document.
    
    Args:
        document_id: Document ID
        request: Update request
        service: Knowledge base service
        
    Returns:
        Updated document details
    """
    try:
        # Build update dictionary
        updates = {}
        if request.title is not None:
            updates['title'] = request.title
        if request.content is not None:
            updates['content'] = request.content
        if request.document_type is not None:
            updates['document_type'] = request.document_type
        if request.machine_models is not None:
            updates['machine_models'] = request.machine_models
        if request.tags is not None:
            updates['tags'] = request.tags
        if request.version is not None:
            updates['version'] = request.version
        if request.metadata is not None:
            updates['metadata'] = request.metadata
        
        success = await service.update_document(document_id, **updates)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get updated document
        document = await service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=500, detail="Failed to retrieve updated document")
        
        return KnowledgeDocumentResponse(**document)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    service: KnowledgeBaseService = Depends(get_knowledge_service)
):
    """
    Delete a document.
    
    Args:
        document_id: Document ID
        service: Knowledge base service
        
    Returns:
        Success message
    """
    try:
        success = await service.delete_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents", response_model=List[KnowledgeDocumentResponse])
async def list_documents(
    document_type: Optional[str] = None,
    machine_model: Optional[str] = None,
    language: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    service: KnowledgeBaseService = Depends(get_knowledge_service)
):
    """
    List documents with optional filters.
    
    Args:
        document_type: Filter by document type
        machine_model: Filter by machine model
        language: Filter by language
        limit: Maximum number of results
        offset: Offset for pagination
        service: Knowledge base service
        
    Returns:
        List of documents
    """
    try:
        documents = await service.list_documents(
            document_type=document_type,
            machine_model=machine_model,
            language=language,
            limit=min(limit, 100),  # Cap at 100
            offset=offset
        )
        
        return [KnowledgeDocumentResponse(**doc) for doc in documents]
        
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=KnowledgeSearchResponse)
async def search_documents(
    request: SearchKnowledgeRequest,
    service: KnowledgeBaseService = Depends(get_knowledge_service)
):
    """
    Search knowledge base documents.
    
    Args:
        request: Search request
        service: Knowledge base service
        
    Returns:
        Search results
    """
    try:
        results = await service.search_documents(
            query=request.query,
            machine_model=request.machine_model,
            document_type=request.document_type,
            language=request.language,
            limit=request.limit
        )
        
        return KnowledgeSearchResponse(
            query=request.query,
            results=results,
            total_results=len(results)
        )
        
    except Exception as e:
        logger.error(f"Failed to search documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_knowledge_base_stats(
    service: KnowledgeBaseService = Depends(get_knowledge_service)
):
    """
    Get knowledge base statistics.
    
    Args:
        service: Knowledge base service
        
    Returns:
        Statistics about the knowledge base
    """
    try:
        # Get vector database stats
        vector_stats = service.vector_db.get_stats()
        
        # Get document counts from database
        from ..database import get_db_session
        from sqlalchemy import text
        
        with get_db_session() as db:
            # Count documents by type
            type_counts = db.execute(text("""
                SELECT document_type, COUNT(*) as count
                FROM knowledge_documents
                GROUP BY document_type
            """)).fetchall()
            
            # Count documents by language
            language_counts = db.execute(text("""
                SELECT language, COUNT(*) as count
                FROM knowledge_documents
                GROUP BY language
            """)).fetchall()
            
            # Total documents
            total_docs = db.execute(text("""
                SELECT COUNT(*) as count FROM knowledge_documents
            """)).fetchone()
        
        return {
            "total_documents": total_docs.count if total_docs else 0,
            "documents_by_type": {row.document_type: row.count for row in type_counts},
            "documents_by_language": {row.language: row.count for row in language_counts},
            "vector_database": vector_stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get knowledge base stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rebuild-index")
async def rebuild_vector_index(
    service: KnowledgeBaseService = Depends(get_knowledge_service)
):
    """
    Rebuild the vector index (admin operation).
    
    Args:
        service: Knowledge base service
        
    Returns:
        Success message
    """
    try:
        service.vector_db.rebuild_index()
        return {"message": "Vector index rebuilt successfully"}
        
    except Exception as e:
        logger.error(f"Failed to rebuild vector index: {e}")
        raise HTTPException(status_code=500, detail=str(e))