"""
Pydantic schemas for AI Assistant API requests and responses.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class SessionStatusEnum(str, Enum):
    """Session status enumeration."""
    active = "active"
    completed = "completed"
    escalated = "escalated"
    abandoned = "abandoned"


class MessageSenderEnum(str, Enum):
    """Message sender enumeration."""
    user = "user"
    assistant = "assistant"
    system = "system"


class MessageTypeEnum(str, Enum):
    """Message type enumeration."""
    text = "text"
    voice = "voice"
    image = "image"
    diagnostic_step = "diagnostic_step"
    escalation = "escalation"


class DocumentTypeEnum(str, Enum):
    """Document type enumeration."""
    manual = "manual"
    procedure = "procedure"
    faq = "faq"
    expert_input = "expert_input"
    troubleshooting_guide = "troubleshooting_guide"


# Request schemas
class CreateSessionRequest(BaseModel):
    """Request to create a new AI session."""
    machine_id: Optional[str] = Field(None, description="ID of the machine being diagnosed")
    language: str = Field("en", description="Language for the session")
    problem_description: Optional[str] = Field(None, description="Initial problem description")


class SendMessageRequest(BaseModel):
    """Request to send a message in a session."""
    content: str = Field(..., description="Message content")
    message_type: MessageTypeEnum = Field(MessageTypeEnum.text, description="Type of message")
    language: str = Field("en", description="Message language")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional message metadata")


class UpdateSessionRequest(BaseModel):
    """Request to update session status."""
    status: SessionStatusEnum = Field(..., description="New session status")
    resolution_summary: Optional[str] = Field(None, description="Resolution summary if completed")


class CreateKnowledgeDocumentRequest(BaseModel):
    """Request to create a new knowledge document."""
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document content")
    document_type: DocumentTypeEnum = Field(..., description="Type of document")
    machine_models: List[str] = Field(default_factory=list, description="Applicable machine models")
    tags: List[str] = Field(default_factory=list, description="Document tags")
    language: str = Field("en", description="Document language")
    version: str = Field("1.0", description="Document version")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class UpdateKnowledgeDocumentRequest(BaseModel):
    """Request to update a knowledge document."""
    title: Optional[str] = Field(None, description="Document title")
    content: Optional[str] = Field(None, description="Document content")
    document_type: Optional[DocumentTypeEnum] = Field(None, description="Type of document")
    machine_models: Optional[List[str]] = Field(None, description="Applicable machine models")
    tags: Optional[List[str]] = Field(None, description="Document tags")
    version: Optional[str] = Field(None, description="Document version")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class SearchKnowledgeRequest(BaseModel):
    """Request to search knowledge base."""
    query: str = Field(..., description="Search query")
    machine_model: Optional[str] = Field(None, description="Filter by machine model")
    document_type: Optional[DocumentTypeEnum] = Field(None, description="Filter by document type")
    language: str = Field("en", description="Search language")
    limit: int = Field(10, description="Maximum number of results", ge=1, le=50)


# Response schemas
class MessageResponse(BaseModel):
    """Response containing message information."""
    message_id: str
    session_id: str
    sender: MessageSenderEnum
    content: str
    message_type: MessageTypeEnum
    language: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class SessionResponse(BaseModel):
    """Response containing session information."""
    session_id: str
    user_id: str
    machine_id: Optional[str] = None
    status: SessionStatusEnum
    language: str
    problem_description: Optional[str] = None
    resolution_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class KnowledgeDocumentResponse(BaseModel):
    """Response containing knowledge document information."""
    document_id: str
    title: str
    content: str
    document_type: DocumentTypeEnum
    machine_models: List[str]
    tags: List[str]
    language: str
    version: str
    file_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class SearchResultResponse(BaseModel):
    """Response containing search result with relevance score."""
    document: KnowledgeDocumentResponse
    relevance_score: float
    matched_content: str


class SessionHistoryResponse(BaseModel):
    """Response containing session conversation history."""
    session_id: str
    messages: List[MessageResponse]
    total_messages: int


class CreateSessionResponse(BaseModel):
    """Response after creating a new session."""
    session_id: str
    status: str = "created"
    message: str = "Session created successfully"


class SendMessageResponse(BaseModel):
    """Response after sending a message."""
    message_id: str
    ai_response: Optional[MessageResponse] = None
    status: str = "sent"
    message: str = "Message sent successfully"


class UserSessionsResponse(BaseModel):
    """Response containing user's recent sessions."""
    user_id: str
    sessions: List[SessionResponse]
    total_sessions: int


class KnowledgeSearchResponse(BaseModel):
    """Response containing knowledge search results."""
    query: str
    results: List[SearchResultResponse]
    total_results: int


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    services: Dict[str, str]