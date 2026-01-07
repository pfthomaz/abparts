"""
Troubleshooting workflow endpoints for the AI Assistant service.
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import logging

from ..services.troubleshooting_service import TroubleshootingService
from ..services.troubleshooting_types import (
    DiagnosticAssessment, TroubleshootingStepData, WorkflowState,
    ConfidenceLevel, StepStatus
)
from ..llm_client import LLMClient
from ..session_manager import SessionManager, session_manager
from ..services.user_service import UserService

logger = logging.getLogger(__name__)
router = APIRouter()


def get_llm_client() -> LLMClient:
    """Dependency to get LLM client from app state."""
    from ..main import app
    if not hasattr(app.state, 'llm_client') or app.state.llm_client is None:
        raise HTTPException(status_code=503, detail="LLM client not initialized")
    return app.state.llm_client


def get_troubleshooting_service(
    llm_client: LLMClient = Depends(get_llm_client)
) -> TroubleshootingService:
    """Dependency to get troubleshooting service."""
    return TroubleshootingService(llm_client, session_manager)


def get_user_service() -> UserService:
    """Dependency to get user service."""
    return UserService()


# Request/Response models
class StartTroubleshootingRequest(BaseModel):
    """Request to start a troubleshooting workflow."""
    problem_description: str = Field(..., description="Description of the problem")
    machine_id: Optional[str] = Field(default=None, description="AutoBoss machine ID")
    user_id: Optional[str] = Field(default=None, description="User ID for language detection")
    language: Optional[str] = Field(default=None, description="Response language code (auto-detected if not provided)")


class DiagnosticAssessmentResponse(BaseModel):
    """Response containing diagnostic assessment."""
    problem_category: str
    likely_causes: List[str]
    confidence_level: str
    recommended_steps: List[str]
    safety_warnings: List[str]
    estimated_duration: int
    requires_expert: bool


class TroubleshootingStepResponse(BaseModel):
    """Response containing troubleshooting step information."""
    step_id: str
    step_number: int
    instruction: str
    expected_outcomes: List[str]
    user_feedback: Optional[str]
    status: str
    requires_feedback: bool
    estimated_duration: Optional[int]
    safety_warnings: List[str]
    created_at: str
    completed_at: Optional[str]


class WorkflowStateResponse(BaseModel):
    """Response containing complete workflow state."""
    session_id: str
    current_step: Optional[TroubleshootingStepResponse]
    completed_steps: List[TroubleshootingStepResponse]
    diagnostic_assessment: Optional[DiagnosticAssessmentResponse]
    workflow_status: str
    resolution_found: bool
    escalation_reason: Optional[str]


class SubmitFeedbackRequest(BaseModel):
    """Request to submit feedback for a troubleshooting step."""
    step_id: str = Field(..., description="ID of the troubleshooting step")
    user_feedback: str = Field(..., description="User's feedback on the step outcome")
    language: Optional[str] = Field(default="en", description="Response language code")


class StartTroubleshootingResponse(BaseModel):
    """Response after starting troubleshooting workflow."""
    session_id: str
    diagnostic_assessment: DiagnosticAssessmentResponse
    first_step: Optional[TroubleshootingStepResponse]
    status: str = "started"
    message: str = "Troubleshooting workflow started successfully"


class SubmitFeedbackResponse(BaseModel):
    """Response after submitting step feedback."""
    step_updated: bool
    next_step: Optional[TroubleshootingStepResponse]
    workflow_status: str
    message: str


@router.post("/troubleshooting/start", response_model=StartTroubleshootingResponse)
async def start_troubleshooting(
    request: StartTroubleshootingRequest,
    authorization: Optional[str] = Header(None),
    troubleshooting_service: TroubleshootingService = Depends(get_troubleshooting_service),
    user_service: UserService = Depends(get_user_service)
) -> StartTroubleshootingResponse:
    """
    Start a new troubleshooting workflow with problem analysis.
    
    This endpoint analyzes the problem description, generates a diagnostic assessment,
    and creates the first troubleshooting step if confidence is sufficient.
    """
    try:
        # Determine language to use
        language = request.language or "en"
        
        # Auto-detect language from user profile if user_id provided and no explicit language
        if request.user_id and not request.language and authorization:
            try:
                auth_token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
                detected_language = await user_service.get_user_language(request.user_id, auth_token)
                language = detected_language
                logger.info(f"Auto-detected language {language} for user {request.user_id}")
            except Exception as e:
                logger.warning(f"Failed to auto-detect language for user {request.user_id}: {e}")
        
        # Get machine context if machine_id provided
        machine_context = None
        if request.machine_id and authorization:
            try:
                auth_token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
                machine_context = await user_service.get_machine_context(request.machine_id, auth_token)
            except Exception as e:
                logger.warning(f"Failed to get machine context for machine {request.machine_id}: {e}")
        
        # Create new session
        session_id = await session_manager.create_session(
            user_id=request.user_id or "anonymous",
            machine_id=request.machine_id,
            language=language,
            problem_description=request.problem_description
        )
        
        # Start troubleshooting workflow
        diagnostic_assessment = await troubleshooting_service.start_troubleshooting_workflow(
            session_id=session_id,
            problem_description=request.problem_description,
            machine_context=machine_context,
            language=language
        )
        
        # Get workflow state to retrieve first step
        workflow_state = await troubleshooting_service.get_workflow_state(session_id)
        
        # Convert diagnostic assessment to response format
        assessment_response = DiagnosticAssessmentResponse(
            problem_category=diagnostic_assessment.problem_category,
            likely_causes=diagnostic_assessment.likely_causes,
            confidence_level=diagnostic_assessment.confidence_level.value,
            recommended_steps=diagnostic_assessment.recommended_steps,
            safety_warnings=diagnostic_assessment.safety_warnings,
            estimated_duration=diagnostic_assessment.estimated_duration,
            requires_expert=diagnostic_assessment.requires_expert
        )
        
        # Convert first step to response format if available
        first_step_response = None
        if workflow_state and workflow_state.current_step:
            step = workflow_state.current_step
            first_step_response = TroubleshootingStepResponse(
                step_id=step.step_id,
                step_number=step.step_number,
                instruction=step.instruction,
                expected_outcomes=step.expected_outcomes,
                user_feedback=step.user_feedback,
                status=step.status.value,
                requires_feedback=step.requires_feedback,
                estimated_duration=step.estimated_duration,
                safety_warnings=step.safety_warnings,
                created_at=step.created_at.isoformat(),
                completed_at=step.completed_at.isoformat() if step.completed_at else None
            )
        
        return StartTroubleshootingResponse(
            session_id=session_id,
            diagnostic_assessment=assessment_response,
            first_step=first_step_response
        )
        
    except Exception as e:
        logger.error(f"Start troubleshooting endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start troubleshooting: {str(e)}")


@router.post("/troubleshooting/feedback", response_model=SubmitFeedbackResponse)
async def submit_step_feedback(
    request: SubmitFeedbackRequest,
    troubleshooting_service: TroubleshootingService = Depends(get_troubleshooting_service)
) -> SubmitFeedbackResponse:
    """
    Submit feedback for a troubleshooting step and get the next step.
    
    This endpoint processes user feedback on a troubleshooting step,
    updates the step status, and generates the next step in the workflow.
    """
    try:
        # Get session ID from step
        step = await troubleshooting_service._get_troubleshooting_step(request.step_id)
        if not step:
            raise HTTPException(status_code=404, detail="Troubleshooting step not found")
        
        # Get session data to find session_id
        # Note: This is a simplified approach. In production, you might want to include session_id in the request
        with troubleshooting_service.session_manager.get_db_session() as db:
            from sqlalchemy import text
            query = text("SELECT session_id FROM troubleshooting_steps WHERE step_id = :step_id")
            result = db.execute(query, {'step_id': request.step_id}).fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Session not found for step")
            session_id = str(result.session_id)
        
        # Process feedback and get next step
        next_step = await troubleshooting_service.process_user_feedback(
            session_id=session_id,
            step_id=request.step_id,
            user_feedback=request.user_feedback,
            language=request.language
        )
        
        # Get updated workflow state
        workflow_state = await troubleshooting_service.get_workflow_state(session_id)
        workflow_status = workflow_state.workflow_status if workflow_state else "active"
        
        # Convert next step to response format if available
        next_step_response = None
        if next_step:
            next_step_response = TroubleshootingStepResponse(
                step_id=next_step.step_id,
                step_number=next_step.step_number,
                instruction=next_step.instruction,
                expected_outcomes=next_step.expected_outcomes,
                user_feedback=next_step.user_feedback,
                status=next_step.status.value,
                requires_feedback=next_step.requires_feedback,
                estimated_duration=next_step.estimated_duration,
                safety_warnings=next_step.safety_warnings,
                created_at=next_step.created_at.isoformat(),
                completed_at=next_step.completed_at.isoformat() if next_step.completed_at else None
            )
        
        # Determine response message
        if workflow_status == "completed":
            message = "Troubleshooting completed successfully"
        elif workflow_status == "escalated":
            message = "Issue escalated to expert support"
        elif next_step:
            message = "Next troubleshooting step generated"
        else:
            message = "Feedback processed"
        
        return SubmitFeedbackResponse(
            step_updated=True,
            next_step=next_step_response,
            workflow_status=workflow_status,
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Submit feedback endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process feedback: {str(e)}")


@router.get("/troubleshooting/{session_id}/state", response_model=WorkflowStateResponse)
async def get_troubleshooting_state(
    session_id: str,
    troubleshooting_service: TroubleshootingService = Depends(get_troubleshooting_service)
) -> WorkflowStateResponse:
    """
    Get the current state of a troubleshooting workflow.
    
    This endpoint returns the complete workflow state including diagnostic assessment,
    completed steps, current step, and overall workflow status.
    """
    try:
        workflow_state = await troubleshooting_service.get_workflow_state(session_id)
        
        if not workflow_state:
            raise HTTPException(status_code=404, detail="Troubleshooting session not found")
        
        # Convert diagnostic assessment to response format
        assessment_response = None
        if workflow_state.diagnostic_assessment:
            assessment = workflow_state.diagnostic_assessment
            assessment_response = DiagnosticAssessmentResponse(
                problem_category=assessment.problem_category,
                likely_causes=assessment.likely_causes,
                confidence_level=assessment.confidence_level.value,
                recommended_steps=assessment.recommended_steps,
                safety_warnings=assessment.safety_warnings,
                estimated_duration=assessment.estimated_duration,
                requires_expert=assessment.requires_expert
            )
        
        # Convert current step to response format
        current_step_response = None
        if workflow_state.current_step:
            step = workflow_state.current_step
            current_step_response = TroubleshootingStepResponse(
                step_id=step.step_id,
                step_number=step.step_number,
                instruction=step.instruction,
                expected_outcomes=step.expected_outcomes,
                user_feedback=step.user_feedback,
                status=step.status.value,
                requires_feedback=step.requires_feedback,
                estimated_duration=step.estimated_duration,
                safety_warnings=step.safety_warnings,
                created_at=step.created_at.isoformat(),
                completed_at=step.completed_at.isoformat() if step.completed_at else None
            )
        
        # Convert completed steps to response format
        completed_steps_response = []
        for step in workflow_state.completed_steps:
            step_response = TroubleshootingStepResponse(
                step_id=step.step_id,
                step_number=step.step_number,
                instruction=step.instruction,
                expected_outcomes=step.expected_outcomes,
                user_feedback=step.user_feedback,
                status=step.status.value,
                requires_feedback=step.requires_feedback,
                estimated_duration=step.estimated_duration,
                safety_warnings=step.safety_warnings,
                created_at=step.created_at.isoformat(),
                completed_at=step.completed_at.isoformat() if step.completed_at else None
            )
            completed_steps_response.append(step_response)
        
        return WorkflowStateResponse(
            session_id=workflow_state.session_id,
            current_step=current_step_response,
            completed_steps=completed_steps_response,
            diagnostic_assessment=assessment_response,
            workflow_status=workflow_state.workflow_status,
            resolution_found=workflow_state.resolution_found,
            escalation_reason=workflow_state.escalation_reason
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get troubleshooting state endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get workflow state: {str(e)}")


@router.get("/troubleshooting/{session_id}/steps", response_model=List[TroubleshootingStepResponse])
async def get_troubleshooting_steps(
    session_id: str,
    troubleshooting_service: TroubleshootingService = Depends(get_troubleshooting_service)
) -> List[TroubleshootingStepResponse]:
    """
    Get all troubleshooting steps for a session.
    
    This endpoint returns a list of all troubleshooting steps (completed and current)
    for the specified session, ordered by step number.
    """
    try:
        workflow_state = await troubleshooting_service.get_workflow_state(session_id)
        
        if not workflow_state:
            raise HTTPException(status_code=404, detail="Troubleshooting session not found")
        
        # Combine completed steps and current step
        all_steps = workflow_state.completed_steps.copy()
        if workflow_state.current_step:
            all_steps.append(workflow_state.current_step)
        
        # Sort by step number
        all_steps.sort(key=lambda x: x.step_number)
        
        # Convert to response format
        steps_response = []
        for step in all_steps:
            step_response = TroubleshootingStepResponse(
                step_id=step.step_id,
                step_number=step.step_number,
                instruction=step.instruction,
                expected_outcomes=step.expected_outcomes,
                user_feedback=step.user_feedback,
                status=step.status.value,
                requires_feedback=step.requires_feedback,
                estimated_duration=step.estimated_duration,
                safety_warnings=step.safety_warnings,
                created_at=step.created_at.isoformat(),
                completed_at=step.completed_at.isoformat() if step.completed_at else None
            )
            steps_response.append(step_response)
        
        return steps_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get troubleshooting steps endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get troubleshooting steps: {str(e)}")


@router.post("/troubleshooting/{session_id}/escalate")
async def escalate_troubleshooting(
    session_id: str,
    reason: str = Field(..., description="Reason for escalation"),
    troubleshooting_service: TroubleshootingService = Depends(get_troubleshooting_service)
) -> Dict[str, Any]:
    """
    Manually escalate a troubleshooting session to expert support.
    
    This endpoint allows users to escalate their troubleshooting session
    to human expert support when they need additional assistance.
    """
    try:
        # Update session status to escalated
        success = await session_manager.update_session_status(
            session_id=session_id,
            status="escalated",
            resolution_summary=f"Manually escalated: {reason}"
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Troubleshooting session not found")
        
        return {
            "session_id": session_id,
            "status": "escalated",
            "reason": reason,
            "message": "Session escalated to expert support successfully",
            "next_steps": [
                "A support ticket has been created with your troubleshooting history",
                "An expert technician will contact you within 24 hours",
                "Keep your machine accessible for remote diagnosis if needed"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Escalate troubleshooting endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to escalate session: {str(e)}")


@router.get("/troubleshooting/categories")
async def get_problem_categories() -> Dict[str, Any]:
    """
    Get available problem categories for troubleshooting.
    
    This endpoint returns the list of problem categories that the
    diagnostic system can identify and handle.
    """
    return {
        "categories": [
            {
                "id": "startup",
                "name": "Startup Issues",
                "description": "Problems with machine startup, initialization, or power-on procedures"
            },
            {
                "id": "cleaning_performance",
                "name": "Cleaning Performance",
                "description": "Issues with cleaning effectiveness, suction, or debris removal"
            },
            {
                "id": "mechanical",
                "name": "Mechanical Problems",
                "description": "Mechanical issues with moving parts, wheels, or physical components"
            },
            {
                "id": "electrical",
                "name": "Electrical Issues",
                "description": "Electrical problems, power issues, or control system malfunctions"
            },
            {
                "id": "hydraulic",
                "name": "Hydraulic Problems",
                "description": "Issues with hydraulic systems, pressure, or fluid circulation"
            },
            {
                "id": "remote_control",
                "name": "Remote Control Issues",
                "description": "Problems with remote control operation, connectivity, or responsiveness"
            },
            {
                "id": "maintenance",
                "name": "Maintenance Related",
                "description": "Issues related to routine maintenance, part replacement, or servicing"
            },
            {
                "id": "other",
                "name": "Other Issues",
                "description": "Problems that don't fit into standard categories or require expert analysis"
            }
        ],
        "confidence_levels": [
            {
                "level": "high",
                "range": "80-100%",
                "description": "High confidence in diagnosis and recommended steps"
            },
            {
                "level": "medium",
                "range": "50-79%",
                "description": "Moderate confidence, may require additional information"
            },
            {
                "level": "low",
                "range": "20-49%",
                "description": "Low confidence, generic troubleshooting steps recommended"
            },
            {
                "level": "very_low",
                "range": "0-19%",
                "description": "Very low confidence, expert consultation recommended"
            }
        ]
    }