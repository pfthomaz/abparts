"""
Shared data types for troubleshooting services.

This module contains data classes and enums used by both the troubleshooting service
and problem analyzer to avoid circular imports.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any


class StepStatus(Enum):
    """Status of a troubleshooting step."""
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    skipped = "skipped"
    failed = "failed"


class ConfidenceLevel(Enum):
    """Confidence level for diagnostic recommendations."""
    high = "high"      # 80-100%
    medium = "medium"  # 50-79%
    low = "low"        # 20-49%
    very_low = "very_low"  # 0-19%


@dataclass
class DiagnosticAssessment:
    """Initial diagnostic assessment of a problem."""
    problem_category: str
    likely_causes: List[str]
    confidence_level: ConfidenceLevel
    recommended_steps: List[str]
    safety_warnings: List[str]
    estimated_duration: int  # minutes
    requires_expert: bool


@dataclass
class TroubleshootingStepData:
    """Enhanced troubleshooting step with workflow logic."""
    step_id: str
    step_number: int
    instruction: str
    expected_outcomes: List[str]
    user_feedback: Optional[str]
    status: StepStatus
    confidence_score: float
    next_steps: Dict[str, str]  # outcome -> next_step_id
    requires_feedback: bool
    estimated_duration: Optional[int]
    safety_warnings: List[str]
    created_at: datetime
    completed_at: Optional[datetime]


@dataclass
class WorkflowState:
    """Current state of the troubleshooting workflow."""
    session_id: str
    current_step: Optional[TroubleshootingStepData]
    completed_steps: List[TroubleshootingStepData]
    diagnostic_assessment: Optional[DiagnosticAssessment]
    workflow_status: str  # active, completed, escalated, abandoned
    resolution_found: bool
    escalation_reason: Optional[str]