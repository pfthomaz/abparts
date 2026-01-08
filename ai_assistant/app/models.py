"""
Data models for the AI Assistant service.
"""

import uuid
import enum
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, Text, Integer, Float, JSON, ForeignKey, Boolean, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY

Base = declarative_base()


class SessionStatus(enum.Enum):
    """Status of a troubleshooting session."""
    active = "active"
    completed = "completed"
    escalated = "escalated"
    abandoned = "abandoned"


class MessageSender(enum.Enum):
    """Who sent the message."""
    user = "user"
    assistant = "assistant"
    system = "system"


class MessageType(enum.Enum):
    """Type of message content."""
    text = "text"
    voice = "voice"
    image = "image"
    diagnostic_step = "diagnostic_step"
    escalation = "escalation"


class DocumentType(enum.Enum):
    """Type of knowledge document."""
    manual = "manual"
    procedure = "procedure"
    faq = "faq"
    expert_input = "expert_input"
    troubleshooting_guide = "troubleshooting_guide"


# SQLAlchemy database models
class AISession(Base):
    """AI troubleshooting session."""
    __tablename__ = "ai_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    machine_id = Column(String, nullable=True)
    status = Column(String, nullable=False, default="active")
    language = Column(String, nullable=False, default="en")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    session_metadata = Column(JSON, nullable=True)
    
    # Relationships
    messages = relationship("AIMessage", back_populates="session", cascade="all, delete-orphan")


class AIMessage(Base):
    """Individual message in an AI conversation."""
    __tablename__ = "ai_messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("ai_sessions.id"), nullable=False)
    sender = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    message_type = Column(String, nullable=False, default="text")
    language = Column(String, nullable=False, default="en")
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    message_metadata = Column(JSON, nullable=True)
    
    # Relationships
    session = relationship("AISession", back_populates="messages")


class KnowledgeDocument(Base):
    """Knowledge base document."""
    __tablename__ = "knowledge_documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    document_type = Column(String, nullable=False, default="manual")
    version = Column(String, nullable=True)  # AutoBoss version (V4.0, V3.1B, etc.)
    language = Column(String, nullable=False, default="en")
    file_path = Column(String, nullable=True)
    file_hash = Column(String, nullable=True, unique=True)  # For duplicate detection
    chunk_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    document_metadata = Column(JSON, nullable=True)
    
    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    """Individual chunk of a knowledge document with embedding."""
    __tablename__ = "document_chunks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("knowledge_documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True)  # Store as JSON array of floats
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    document = relationship("KnowledgeDocument", back_populates="chunks")


class TroubleshootingStep(Base):
    """Individual troubleshooting step."""
    __tablename__ = "troubleshooting_steps"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("ai_sessions.id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    instruction = Column(Text, nullable=False)
    expected_outcomes = Column(JSON, nullable=True)  # List of possible outcomes
    user_feedback = Column(Text, nullable=True)
    completed = Column(Boolean, nullable=False, default=False)
    success = Column(Boolean, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    session = relationship("AISession")


class ExpertKnowledge(Base):
    """Expert-contributed knowledge and corrections."""
    __tablename__ = "expert_knowledge"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    expert_user_id = Column(String, nullable=False)
    problem_description = Column(Text, nullable=False)
    solution = Column(Text, nullable=False)
    machine_version = Column(String, nullable=True)
    tags = Column(JSON, nullable=True)  # List of tags
    verified = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    expert_metadata = Column(JSON, nullable=True)


class SupportTicket(Base):
    """Support ticket for escalated troubleshooting sessions."""
    __tablename__ = "support_tickets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("ai_sessions.id"), nullable=False)
    ticket_number = Column(String, nullable=False, unique=True)
    priority = Column(String, nullable=False, default="medium")  # low, medium, high, urgent
    status = Column(String, nullable=False, default="open")  # open, in_progress, resolved, closed
    escalation_reason = Column(Text, nullable=False)
    session_summary = Column(Text, nullable=False)
    machine_context = Column(JSON, nullable=True)
    expert_contact_info = Column(JSON, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    assigned_expert_id = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    # Relationships
    session = relationship("AISession")


class EscalationTrigger(Base):
    """Escalation trigger configuration and history."""
    __tablename__ = "escalation_triggers"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("ai_sessions.id"), nullable=False)
    trigger_type = Column(String, nullable=False)  # confidence_low, steps_exceeded, user_request, expert_required
    trigger_value = Column(Float, nullable=True)  # confidence score or step count
    triggered_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    escalation_decision = Column(String, nullable=False)  # escalate, continue, expert_review
    decision_reason = Column(Text, nullable=True)
    
    # Relationships
    session = relationship("AISession")


class ExpertFeedback(Base):
    """Feedback from experts on AI responses and troubleshooting accuracy."""
    __tablename__ = "expert_feedback"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("ai_sessions.id"), nullable=False)
    message_id = Column(String, ForeignKey("ai_messages.id"), nullable=True)
    expert_user_id = Column(String, nullable=False)
    feedback_type = Column(String, nullable=False)  # accuracy, completeness, safety, improvement
    rating = Column(Integer, nullable=False)  # 1-5 scale
    feedback_text = Column(Text, nullable=True)
    suggested_improvement = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    session = relationship("AISession")
    message = relationship("AIMessage")


# Pydantic models for API requests/responses (keeping for compatibility)
from dataclasses import dataclass

@dataclass
class TroubleshootingStepData:
    """A single step in the troubleshooting process."""
    step_id: str
    instruction: str
    expected_outcomes: List[str]
    next_steps: Dict[str, str]  # outcome -> next_step_id
    requires_feedback: bool
    estimated_duration: Optional[int] = None


@dataclass
class Resolution:
    """Resolution information for a completed session."""
    resolution_id: str
    summary: str
    steps_taken: List[str]
    success: bool
    feedback_rating: Optional[int] = None
    feedback_comments: Optional[str] = None


@dataclass
class TroubleshootingSessionData:
    """Complete troubleshooting session data."""
    session_id: str
    user_id: str
    machine_id: Optional[str]
    status: SessionStatus
    created_at: datetime
    updated_at: datetime
    messages: List['MessageData']
    current_step: Optional[TroubleshootingStepData] = None
    resolution: Optional[Resolution] = None


@dataclass
class MessageData:
    """Individual message in a conversation."""
    message_id: str
    session_id: str
    sender: MessageSender
    content: str
    message_type: MessageType
    timestamp: datetime
    language: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class KnowledgeDocumentData:
    """Knowledge base document."""
    document_id: str
    title: str
    content: str
    document_type: DocumentType
    machine_models: List[str]
    tags: List[str]
    language: str
    version: str
    file_path: Optional[str]
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None