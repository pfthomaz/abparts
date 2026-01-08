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


class EscalationReasonEnum(str, Enum):
    """Escalation reason enumeration."""
    low_confidence = "low_confidence"
    steps_exceeded = "steps_exceeded"
    user_request = "user_request"
    expert_required = "expert_required"
    safety_concern = "safety_concern"
    complex_issue = "complex_issue"


class TicketPriorityEnum(str, Enum):
    """Support ticket priority enumeration."""
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class TicketStatusEnum(str, Enum):
    """Support ticket status enumeration."""
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class FeedbackTypeEnum(str, Enum):
    """Expert feedback type enumeration."""
    accuracy = "accuracy"
    completeness = "completeness"
    safety = "safety"
    improvement = "improvement"


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


class CreateExpertKnowledgeRequest(BaseModel):
    """Request to create expert knowledge entry."""
    problem_description: str = Field(..., description="Description of the problem")
    solution: str = Field(..., description="Expert solution")
    machine_version: Optional[str] = Field(None, description="Applicable machine version")
    tags: List[str] = Field(default_factory=list, description="Knowledge tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class CreateSupportTicketRequest(BaseModel):
    """Request to create a support ticket."""
    escalation_reason: EscalationReasonEnum = Field(..., description="Reason for escalation")
    priority: TicketPriorityEnum = Field(TicketPriorityEnum.medium, description="Ticket priority")
    additional_notes: Optional[str] = Field(None, description="Additional notes from user")


class UpdateSupportTicketRequest(BaseModel):
    """Request to update a support ticket."""
    status: Optional[TicketStatusEnum] = Field(None, description="New ticket status")
    resolution_notes: Optional[str] = Field(None, description="Resolution notes")
    assigned_expert_id: Optional[str] = Field(None, description="Assigned expert user ID")


class CreateExpertFeedbackRequest(BaseModel):
    """Request to create expert feedback."""
    message_id: Optional[str] = Field(None, description="ID of the AI message being reviewed")
    feedback_type: FeedbackTypeEnum = Field(..., description="Type of feedback")
    rating: int = Field(..., description="Rating from 1-5", ge=1, le=5)
    feedback_text: Optional[str] = Field(None, description="Detailed feedback text")
    suggested_improvement: Optional[str] = Field(None, description="Suggested improvement")


class EscalationDecisionRequest(BaseModel):
    """Request for escalation decision."""
    confidence_threshold: Optional[float] = Field(0.3, description="Confidence threshold for escalation")
    max_steps: Optional[int] = Field(10, description="Maximum troubleshooting steps before escalation")
    force_escalation: bool = Field(False, description="Force escalation regardless of other factors")


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


class ExpertKnowledgeResponse(BaseModel):
    """Response containing expert knowledge information."""
    knowledge_id: str
    expert_user_id: str
    problem_description: str
    solution: str
    machine_version: Optional[str] = None
    tags: List[str]
    verified: bool
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class SupportTicketResponse(BaseModel):
    """Response containing support ticket information."""
    ticket_id: str
    session_id: str
    ticket_number: str
    priority: TicketPriorityEnum
    status: TicketStatusEnum
    escalation_reason: str
    session_summary: str
    machine_context: Optional[Dict[str, Any]] = None
    expert_contact_info: Optional[Dict[str, Any]] = None
    resolution_notes: Optional[str] = None
    assigned_expert_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ExpertFeedbackResponse(BaseModel):
    """Response containing expert feedback information."""
    feedback_id: str
    session_id: str
    message_id: Optional[str] = None
    expert_user_id: str
    feedback_type: FeedbackTypeEnum
    rating: int
    feedback_text: Optional[str] = None
    suggested_improvement: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class EscalationDecisionResponse(BaseModel):
    """Response containing escalation decision."""
    should_escalate: bool
    escalation_reason: Optional[EscalationReasonEnum] = None
    confidence_score: float
    steps_completed: int
    decision_factors: Dict[str, Any]
    recommended_action: str


class CreateSupportTicketResponse(BaseModel):
    """Response after creating a support ticket."""
    ticket_id: str
    ticket_number: str
    status: str = "created"
    message: str = "Support ticket created successfully"
    expert_contact_info: Optional[Dict[str, Any]] = None