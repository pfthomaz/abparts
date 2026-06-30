"""
Pydantic schemas for Support Cases API requests and responses.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class SupportCaseStatusEnum(str, Enum):
    """Support case status enumeration."""
    open = "open"
    investigating = "investigating"
    waiting_on_customer = "waiting_on_customer"
    resolved = "resolved"
    closed = "closed"


class SupportCasePriorityEnum(str, Enum):
    """Support case priority enumeration."""
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


# Request schemas

class CreateSupportCaseRequest(BaseModel):
    """Request to create a new support case."""
    title: str = Field(..., description="Brief title describing the issue")
    description: str = Field(..., description="Detailed description of the issue")
    machine_model: Optional[str] = Field(None, description="AutoBoss model (V4.0, V3.1B, V3.0, V2.0)")
    machine_id: Optional[str] = Field(None, description="Specific machine ID if known")
    symptoms: Optional[str] = Field(None, description="Observed symptoms")
    priority: SupportCasePriorityEnum = Field(SupportCasePriorityEnum.medium, description="Case priority")
    organization_id: Optional[str] = Field(None, description="Customer organization ID")
    assigned_to: Optional[str] = Field(None, description="Expert user ID to assign")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    related_parts: List[str] = Field(default_factory=list, description="Related part IDs")
    session_id: Optional[str] = Field(None, description="AI session ID if created from a chat session")


class UpdateSupportCaseRequest(BaseModel):
    """Request to update an existing support case."""
    title: Optional[str] = Field(None, description="Updated title")
    description: Optional[str] = Field(None, description="Updated description")
    machine_model: Optional[str] = Field(None, description="AutoBoss model")
    machine_id: Optional[str] = Field(None, description="Specific machine ID")
    symptoms: Optional[str] = Field(None, description="Observed symptoms")
    root_cause: Optional[str] = Field(None, description="Identified root cause")
    resolution: Optional[str] = Field(None, description="How the issue was resolved")
    status: Optional[SupportCaseStatusEnum] = Field(None, description="New status")
    priority: Optional[SupportCasePriorityEnum] = Field(None, description="Updated priority")
    assigned_to: Optional[str] = Field(None, description="Expert user ID to assign")
    tags: Optional[List[str]] = Field(None, description="Updated tags")
    related_parts: Optional[List[str]] = Field(None, description="Updated related part IDs")
    internal_notes: Optional[str] = Field(None, description="Internal notes (not visible to customer)")


class ResolveSupportCaseRequest(BaseModel):
    """Request to resolve a support case with root cause and resolution."""
    root_cause: str = Field(..., description="Identified root cause of the issue")
    resolution: str = Field(..., description="How the issue was resolved")
    internal_notes: Optional[str] = Field(None, description="Internal notes about the resolution")
    publish_to_knowledge_base: bool = Field(True, description="Whether to publish this resolution to the knowledge base")


class AddCommentRequest(BaseModel):
    """Request to add a comment to a support case."""
    content: str = Field(..., description="Comment content")
    is_internal: bool = Field(False, description="Whether this is an internal-only comment")


class ListSupportCasesRequest(BaseModel):
    """Query parameters for listing support cases."""
    status: Optional[SupportCaseStatusEnum] = Field(None, description="Filter by status")
    priority: Optional[SupportCasePriorityEnum] = Field(None, description="Filter by priority")
    machine_model: Optional[str] = Field(None, description="Filter by machine model")
    organization_id: Optional[str] = Field(None, description="Filter by organization")
    assigned_to: Optional[str] = Field(None, description="Filter by assigned expert")
    created_by: Optional[str] = Field(None, description="Filter by creator")
    search: Optional[str] = Field(None, description="Search in title, description, symptoms")
    limit: int = Field(50, description="Maximum results to return", ge=1, le=200)
    offset: int = Field(0, description="Offset for pagination", ge=0)


# Response schemas

class SupportCaseCommentResponse(BaseModel):
    """Response containing a support case comment."""
    id: str
    case_id: str
    author_id: str
    content: str
    is_internal: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SupportCaseResponse(BaseModel):
    """Response containing support case information."""
    id: str
    case_number: str
    title: str
    description: str
    machine_model: Optional[str] = None
    machine_id: Optional[str] = None
    symptoms: Optional[str] = None
    root_cause: Optional[str] = None
    resolution: Optional[str] = None
    status: SupportCaseStatusEnum
    priority: SupportCasePriorityEnum
    organization_id: Optional[str] = None
    created_by: str
    assigned_to: Optional[str] = None
    tags: Optional[List[str]] = None
    related_parts: Optional[List[str]] = None
    internal_notes: Optional[str] = None
    knowledge_doc_id: Optional[str] = None
    session_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    comments: List[SupportCaseCommentResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class SupportCaseListResponse(BaseModel):
    """Response containing a paginated list of support cases."""
    cases: List[SupportCaseResponse]
    total: int
    limit: int
    offset: int


class SupportCaseStatsResponse(BaseModel):
    """Response containing support case statistics."""
    total_cases: int
    open_cases: int
    investigating_cases: int
    waiting_cases: int
    resolved_cases: int
    closed_cases: int
    avg_resolution_time_hours: Optional[float] = None
    cases_by_machine_model: Dict[str, int] = Field(default_factory=dict)
    cases_by_priority: Dict[str, int] = Field(default_factory=dict)
