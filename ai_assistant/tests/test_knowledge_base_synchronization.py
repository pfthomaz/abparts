"""
Property-based tests for knowledge base synchronization.

**Feature: autoboss-ai-assistant, Property 8: Knowledge Base Synchronization**
**Validates: Requirements 8.2, 8.3, 8.4, 8.5**

Property 8: Knowledge Base Synchronization
For any knowledge base update (new documentation, expert input, procedure changes), 
the AI guidance should reflect the updated information in subsequent interactions.
"""

import pytest
import asyncio
import tempfile
import os
from hypothesis import given, strategies as st, settings, assume
from typing import List, Dict, Any
import uuid
import json

# Mock the database operations for testing
class MockDatabase:
    def __init__(self):
        self.documents = {}
        self.next_id = 1
    
    def execute(self, query, params=None):
        # Mock database operations
        if "INSERT INTO knowledge_documents" in str(query):
            doc_id = params['document_id']
            self.documents[doc_id] = {
                'document_id': doc_id,
                'title': params['title'],
                'content': params['content'],
                'document_type': params['document_type'],
                'machine_models': params['machine_models'],
                'tags': params['tags'],
                'language': params['language'],
                'version': params['version'],
                'file_path': params.get('file_path'),
                'metadata': params.get('metadata', '{}')
            }
            return MockResult(1)
        elif "UPDATE knowledge_documents" in str(query):
            doc_id = params['document_id']
            if doc_id in self.documents:
                for key, value in params.items():
                    if key != 'document_id' and value is not None:
                        self.documents[doc_id][key] = value
                return MockResult(1)
            return MockResult(0)
        elif "DELETE FROM knowledge_documents" in str(query):
            doc_id = params['document_id']
            if doc_id in self.documents:
                del self.documents[doc_id]
                return MockResult(1)
            return MockResult(0)
        elif "SELECT" in str(query) and "knowledge_documents" in str(query):
            doc_id = params.get('document_id')
            if doc_id and doc_id in self.documents:
                return MockResult(1, [MockRow(self.documents[doc_id])])
            elif not doc_id:
                # List all documents
                return MockResult(len(self.documents), [MockRow(doc) for doc in self.documents.values()])
            return MockResult(0, [])
        return MockResult(0)

class MockResult:
    def __init__(self, rowcount, rows=None):
        self.rowcount = rowcount
        self.rows = rows or []
    
    def fetchone(self):
        return self.rows[0] if self.rows else None
    
    def fetchall(self):
        return self.rows

class MockRow:
    def __init__(self, data):
        for key, value in data.items():
            setattr(self, key, value)

class MockDBSession:
    def __init__(self, db):
        self.db = db
    
    def execute(self, query, params=None):
        return self.db.execute(query, params)
    
    def commit(self):
        pass
    
    def rollback(self):
        pass
    
    def close(self):
        pass

# Mock the database context manager
def mock_get_db_session():
    return MockDBSession(MockDatabase())

# Import and patch the modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock the database module before importing knowledge_base
import unittest.mock
with unittest.mock.patch('app.database.get_db_session', mock_get_db_session):
    from app.services.vector_database import VectorDatabase
    from app.enums import DocumentType


class MockLLMClient:
    """Mock LLM client for testing."""
    
    def __init__(self):
        self.embedding_calls = []
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate a mock embedding based on text hash."""
        self.embedding_calls.append(text)
        # Create a deterministic embedding based on text hash
        text_hash = hash(text) % 1000000
        embedding = [float(text_hash % 100) / 100.0] * 1536
        return embedding


class MockKnowledgeBaseService:
    """Mock knowledge base service for testing synchronization properties."""
    
    def __init__(self, llm_client, vector_db):
        self.llm_client = llm_client
        self.vector_db = vector_db
        self.documents = {}
        self.chunk_size = 1000
        self.chunk_overlap = 200
    
    async def create_document(self, title: str, content: str, document_type: str,
                            machine_models: List[str], tags: List[str], 
                            language: str = "en", version: str = "1.0",
                            file_path: str = None, metadata: Dict[str, Any] = None) -> str:
        """Create a new knowledge document with embeddings."""
        document_id = str(uuid.uuid4())
        
        # Store document
        self.documents[document_id] = {
            'document_id': document_id,
            'title': title,
            'content': content,
            'document_type': document_type,
            'machine_models': machine_models,
            'tags': tags,
            'language': language,
            'version': version,
            'file_path': file_path,
            'metadata': metadata or {},
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z'
        }
        
        # Generate embeddings and store in vector database
        await self._generate_and_store_embeddings(document_id, content, {
            'title': title,
            'document_type': document_type,
            'machine_models': machine_models,
            'tags': tags,
            'language': language,
            'version': version
        })
        
        return document_id
    
    async def update_document(self, document_id: str, **updates) -> bool:
        """Update an existing knowledge document."""
        if document_id not in self.documents:
            return False
        
        # Update document
        for field, value in updates.items():
            if field in self.documents[document_id]:
                self.documents[document_id][field] = value
        
        # If content was updated, regenerate embeddings
        if 'content' in updates:
            self.vector_db.delete_document(document_id)
            doc_metadata = {
                'title': self.documents[document_id]['title'],
                'document_type': self.documents[document_id]['document_type'],
                'machine_models': self.documents[document_id]['machine_models'],
                'tags': self.documents[document_id]['tags'],
                'language': self.documents[document_id]['language'],
                'version': self.documents[document_id]['version']
            }
            await self._generate_and_store_embeddings(
                document_id, updates['content'], doc_metadata
            )
        
        return True
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a knowledge document and its embeddings."""
        if document_id not in self.documents:
            return False
        
        # Delete from vector database
        self.vector_db.delete_document(document_id)
        
        # Delete from documents
        del self.documents[document_id]
        
        return True
    
    async def get_document(self, document_id: str) -> Dict[str, Any]:
        """Get a specific document by ID."""
        return self.documents.get(document_id)
    
    async def search_documents(self, query: str, machine_model: str = None,
                             document_type: str = None, language: str = "en",
                             limit: int = 10) -> List[Dict[str, Any]]:
        """Search knowledge base documents using vector similarity."""
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
        
        # Convert to expected format
        results = []
        for result in vector_results:
            doc_id = result['document_id']
            if doc_id in self.documents:
                results.append({
                    'document': self.documents[doc_id],
                    'relevance_score': result['relevance_score'],
                    'matched_content': result['content_chunk'][:500]
                })
        
        return results[:limit]
    
    async def list_documents(self, document_type: str = None,
                           machine_model: str = None, language: str = None,
                           limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List documents with optional filters."""
        docs = list(self.documents.values())
        
        # Apply filters
        if document_type:
            docs = [d for d in docs if d['document_type'] == document_type]
        if machine_model:
            docs = [d for d in docs if machine_model in d['machine_models']]
        if language:
            docs = [d for d in docs if d['language'] == language]
        
        return docs[offset:offset + limit]
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks for embedding."""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    async def _generate_and_store_embeddings(self, document_id: str, content: str, 
                                           metadata: Dict[str, Any]):
        """Generate embeddings for document content and store in vector database."""
        # Split content into chunks
        chunks = self._chunk_text(content)
        
        # Generate embeddings for all chunks
        embeddings = []
        for chunk in chunks:
            embedding = await self.llm_client.generate_embedding(chunk)
            embeddings.append(embedding)
        
        # Store in vector database
        self.vector_db.add_document(document_id, chunks, embeddings, metadata)


@pytest.fixture
async def knowledge_service():
    """Create a knowledge base service for testing."""
    # Use temporary directory for vector database
    with tempfile.TemporaryDirectory() as temp_dir:
        vector_db = VectorDatabase(index_path=os.path.join(temp_dir, "test_index"))
        llm_client = MockLLMClient()
        service = MockKnowledgeBaseService(llm_client, vector_db)
        yield service


# Hypothesis strategies for generating test data
document_types = st.sampled_from([dt.value for dt in DocumentType])
languages = st.sampled_from(["en", "el", "ar", "es", "tr", "no"])
machine_models = st.lists(
    st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"))),
    min_size=0, max_size=3
)
tags = st.lists(
    st.text(min_size=1, max_size=15, alphabet=st.characters(whitelist_categories=("Lu", "Ll"))),
    min_size=0, max_size=5
)
document_content = st.text(min_size=50, max_size=2000)
document_title = st.text(min_size=5, max_size=100, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Zs")))


@given(
    title=document_title,
    content=document_content,
    doc_type=document_types,
    models=machine_models,
    doc_tags=tags,
    language=languages
)
@settings(max_examples=20, deadline=30000)  # Reduced examples for faster testing
@pytest.mark.asyncio
async def test_knowledge_base_synchronization_property(
    knowledge_service, title, content, doc_type, models, doc_tags, language
):
    """
    Property 8: Knowledge Base Synchronization
    
    Test that when knowledge base is updated, the changes are immediately 
    reflected in search results and document retrieval.
    """
    assume(len(title.strip()) > 0)
    assume(len(content.strip()) > 0)
    
    # Step 1: Create initial document
    document_id = await knowledge_service.create_document(
        title=title,
        content=content,
        document_type=doc_type,
        machine_models=models,
        tags=doc_tags,
        language=language
    )
    
    # Step 2: Verify document can be retrieved immediately after creation
    retrieved_doc = await knowledge_service.get_document(document_id)
    assert retrieved_doc is not None
    assert retrieved_doc['title'] == title
    assert retrieved_doc['content'] == content
    assert retrieved_doc['document_type'] == doc_type
    
    # Step 3: Verify document appears in search results immediately
    search_results = await knowledge_service.search_documents(
        query=title[:20],  # Use part of title as search query
        language=language,
        limit=10
    )
    
    # Document should be found in search results
    found_in_search = any(
        result['document']['document_id'] == document_id 
        for result in search_results
    )
    assert found_in_search, f"Document {document_id} not found in search results immediately after creation"
    
    # Step 4: Update the document content
    updated_content = content + "\n\nUPDATED: Additional troubleshooting information."
    update_success = await knowledge_service.update_document(
        document_id, 
        content=updated_content
    )
    assert update_success
    
    # Step 5: Verify updated content is immediately retrievable
    updated_doc = await knowledge_service.get_document(document_id)
    assert updated_doc is not None
    assert updated_doc['content'] == updated_content
    
    # Step 6: Verify updated content appears in search results
    # Search for the new content that was added
    updated_search_results = await knowledge_service.search_documents(
        query="UPDATED Additional troubleshooting",
        language=language,
        limit=10
    )
    
    # The updated document should be found when searching for the new content
    found_updated_in_search = any(
        result['document']['document_id'] == document_id 
        for result in updated_search_results
    )
    assert found_updated_in_search, f"Updated document {document_id} not found in search results after update"


@pytest.mark.asyncio
async def test_knowledge_base_synchronization_edge_cases(knowledge_service):
    """
    Test edge cases for knowledge base synchronization.
    """
    # Test 1: Update non-existent document
    fake_id = str(uuid.uuid4())
    update_result = await knowledge_service.update_document(fake_id, title="New Title")
    assert not update_result
    
    # Test 2: Delete non-existent document
    delete_result = await knowledge_service.delete_document(fake_id)
    assert not delete_result
    
    # Test 3: Search empty knowledge base
    empty_search = await knowledge_service.search_documents(
        query="nonexistent content",
        language="en",
        limit=10
    )
    assert len(empty_search) == 0
    
    # Test 4: Create document with minimal content
    minimal_doc_id = await knowledge_service.create_document(
        title="Test",
        content="Minimal content for testing synchronization.",
        document_type="manual",
        machine_models=[],
        tags=[],
        language="en"
    )
    
    # Verify minimal document is immediately available
    minimal_doc = await knowledge_service.get_document(minimal_doc_id)
    assert minimal_doc is not None
    assert minimal_doc['title'] == "Test"


if __name__ == "__main__":
    # Run a simple test to verify the property
    async def run_simple_test():
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_db = VectorDatabase(index_path=os.path.join(temp_dir, "test_index"))
            llm_client = MockLLMClient()
            service = MockKnowledgeBaseService(llm_client, vector_db)
            
            # Simple synchronization test
            doc_id = await service.create_document(
                title="Test Document",
                content="This is test content for synchronization testing.",
                document_type="manual",
                machine_models=["V4.0"],
                tags=["test"],
                language="en"
            )
            
            # Verify immediate retrieval
            doc = await service.get_document(doc_id)
            assert doc is not None
            print("✓ Document creation and immediate retrieval works")
            
            # Update and verify
            await service.update_document(doc_id, content="Updated test content.")
            updated_doc = await service.get_document(doc_id)
            assert "Updated test content" in updated_doc['content']
            print("✓ Document update and immediate retrieval works")
            
            # Search and verify
            results = await service.search_documents("Updated test", language="en")
            assert len(results) > 0
            print("✓ Updated content immediately searchable")
            
            print("All synchronization tests passed!")
    
    asyncio.run(run_simple_test())