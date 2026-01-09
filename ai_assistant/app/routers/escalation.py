"""
API endpoints for escalation and expert knowledge management.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from ..schemas import (
    CreateSupportTicketRequest, CreateSupportTicketResponse,
    CreateExpertKnowledgeRequest, ExpertKnowledgeResponse,
    CreateExpertFeedbackRequest, ExpertFeedbackResponse,
    EscalationDecisionRequest, EscalationDecisionResponse,
    SupportTicketResponse, ErrorResponse,
    EscalationReasonEnum, TicketPriorityEnum, FeedbackTypeEnum
)
from ..services.escalation_service import escalation_service

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer(auto_error=False)  # Don't auto-error, handle manually


async def get_current_user_id(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> str:
    """
    Extract user ID from JWT token.
    For now, we'll use a mock implementation.
    In production, this should validate the JWT and extract user info.
    """
    # TODO: Implement proper JWT validation with ABParts auth
    # For now, return the superadmin user ID for testing
    # In a real implementation, we would decode the JWT token here
    try:
        if credentials:
            logger.info(f"Received authorization credentials: {credentials.scheme}")
            # If we have a token, try to extract user info from it
            # For now, just return a default user ID
            return "f6abc555-5b6c-6f7a-8b9c-0d123456789a"
        else:
            logger.warning("No authorization credentials provided, using default user ID")
            # Return default user ID for testing even without token
            return "f6abc555-5b6c-6f7a-8b9c-0d123456789a"
    except Exception as e:
        logger.warning(f"Failed to extract user ID from token: {e}")
        # Return default user ID for testing
        return "f6abc555-5b6c-6f7a-8b9c-0d123456789a"


@router.post(
    "/sessions/{session_id}/escalate",
    response_model=CreateSupportTicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Escalate a troubleshooting session to expert support"
)
async def escalate_session(
    session_id: str,
    request: CreateSupportTicketRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Escalate a troubleshooting session to expert support by creating a support ticket.
    
    - **session_id**: ID of the session to escalate
    - **escalation_reason**: Reason for escalation
    - **priority**: Ticket priority level
    - **additional_notes**: Additional notes from user
    """
    try:
        # Create support ticket
        ticket_data = await escalation_service.create_support_ticket(
            session_id=session_id,
            escalation_reason=request.escalation_reason,
            priority=request.priority,
            additional_notes=request.additional_notes
        )
        
        return CreateSupportTicketResponse(
            ticket_id=ticket_data["ticket_id"],
            ticket_number=ticket_data["ticket_number"],
            status="created",
            message="Support ticket created successfully. Expert will be contacted.",
            expert_contact_info=ticket_data.get("expert_contact_info")
        )
        
    except Exception as e:
        logger.error(f"Failed to escalate session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to escalate session: {str(e)}"
        )


@router.post(
    "/sessions/{session_id}/evaluate-escalation",
    response_model=EscalationDecisionResponse,
    summary="Evaluate whether a session should be escalated"
)
async def evaluate_escalation(
    session_id: str,
    request: EscalationDecisionRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Evaluate whether a troubleshooting session should be escalated based on various factors.
    
    - **session_id**: ID of the session to evaluate
    - **confidence_threshold**: Confidence threshold for escalation
    - **max_steps**: Maximum troubleshooting steps before escalation
    - **force_escalation**: Force escalation regardless of other factors
    """
    try:
        if request.force_escalation:
            return EscalationDecisionResponse(
                should_escalate=True,
                escalation_reason=EscalationReasonEnum.user_request,
                confidence_score=0.0,
                steps_completed=0,
                decision_factors={"force_escalation": True},
                recommended_action="Create support ticket immediately"
            )
        
        # Get current session state for evaluation
        # This would typically come from the troubleshooting service
        current_confidence = 0.5  # Placeholder - should be retrieved from session
        steps_completed = 3  # Placeholder - should be retrieved from session
        
        should_escalate, escalation_reason, decision_factors = await escalation_service.evaluate_escalation_need(
            session_id=session_id,
            current_confidence=current_confidence,
            steps_completed=steps_completed
        )
        
        recommended_action = "Create support ticket" if should_escalate else "Continue troubleshooting"
        
        return EscalationDecisionResponse(
            should_escalate=should_escalate,
            escalation_reason=escalation_reason,
            confidence_score=current_confidence,
            steps_completed=steps_completed,
            decision_factors=decision_factors,
            recommended_action=recommended_action
        )
        
    except Exception as e:
        logger.error(f"Failed to evaluate escalation for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate escalation: {str(e)}"
        )


@router.post(
    "/expert-knowledge",
    response_model=ExpertKnowledgeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new expert knowledge entry"
)
async def create_expert_knowledge(
    request: CreateExpertKnowledgeRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Create a new expert knowledge entry for integration into troubleshooting responses.
    
    - **problem_description**: Description of the problem
    - **solution**: Expert solution
    - **machine_version**: Applicable machine version
    - **tags**: Knowledge tags for categorization
    - **metadata**: Additional metadata
    """
    try:
        knowledge_data = await escalation_service.create_expert_knowledge(
            expert_user_id=user_id,
            problem_description=request.problem_description,
            solution=request.solution,
            machine_version=request.machine_version,
            tags=request.tags,
            metadata=request.metadata
        )
        
        return ExpertKnowledgeResponse(
            knowledge_id=knowledge_data["knowledge_id"],
            expert_user_id=knowledge_data["expert_user_id"],
            problem_description=knowledge_data["problem_description"],
            solution=knowledge_data["solution"],
            machine_version=knowledge_data["machine_version"],
            tags=knowledge_data["tags"],
            verified=knowledge_data["verified"],
            created_at=datetime.fromisoformat(knowledge_data["created_at"]),
            updated_at=datetime.fromisoformat(knowledge_data["created_at"]),  # Same as created_at initially
            metadata=request.metadata
        )
        
    except Exception as e:
        logger.error(f"Failed to create expert knowledge: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create expert knowledge: {str(e)}"
        )


@router.post(
    "/sessions/{session_id}/expert-feedback",
    response_model=ExpertFeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create expert feedback on AI responses"
)
async def create_expert_feedback(
    session_id: str,
    request: CreateExpertFeedbackRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Create expert feedback on AI responses and troubleshooting accuracy.
    
    - **session_id**: ID of the session being reviewed
    - **message_id**: ID of the specific AI message (optional)
    - **feedback_type**: Type of feedback (accuracy, completeness, safety, improvement)
    - **rating**: Rating from 1-5
    - **feedback_text**: Detailed feedback text
    - **suggested_improvement**: Suggested improvement
    """
    try:
        feedback_data = await escalation_service.create_expert_feedback(
            session_id=session_id,
            expert_user_id=user_id,
            feedback_type=request.feedback_type,
            rating=request.rating,
            message_id=request.message_id,
            feedback_text=request.feedback_text,
            suggested_improvement=request.suggested_improvement
        )
        
        return ExpertFeedbackResponse(
            feedback_id=feedback_data["feedback_id"],
            session_id=feedback_data["session_id"],
            message_id=feedback_data["message_id"],
            expert_user_id=feedback_data["expert_user_id"],
            feedback_type=FeedbackTypeEnum(feedback_data["feedback_type"]),
            rating=feedback_data["rating"],
            feedback_text=feedback_data["feedback_text"],
            suggested_improvement=feedback_data["suggested_improvement"],
            created_at=datetime.fromisoformat(feedback_data["created_at"])
        )
        
    except Exception as e:
        logger.error(f"Failed to create expert feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create expert feedback: {str(e)}"
        )


@router.get(
    "/expert-knowledge/search",
    response_model=List[ExpertKnowledgeResponse],
    summary="Search expert knowledge for troubleshooting integration"
)
async def search_expert_knowledge(
    keywords: str,
    machine_version: Optional[str] = None,
    limit: int = 5,
    user_id: str = Depends(get_current_user_id)
):
    """
    Search expert knowledge for integration into troubleshooting responses.
    
    - **keywords**: Keywords to search for (comma-separated)
    - **machine_version**: Filter by machine version
    - **limit**: Maximum number of results (default: 5)
    """
    try:
        # Parse keywords
        keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
        
        knowledge_entries = await escalation_service.get_expert_knowledge_for_integration(
            problem_keywords=keyword_list,
            machine_version=machine_version,
            limit=limit
        )
        
        responses = []
        for entry in knowledge_entries:
            responses.append(ExpertKnowledgeResponse(
                knowledge_id=entry["knowledge_id"],
                expert_user_id=entry["expert_user_id"],
                problem_description=entry["problem_description"],
                solution=entry["solution"],
                machine_version=entry["machine_version"],
                tags=entry["tags"],
                verified=True,  # Only verified knowledge is returned
                created_at=datetime.fromisoformat(entry["created_at"]),
                updated_at=datetime.fromisoformat(entry["updated_at"]),
                metadata={}
            ))
        
        return responses
        
    except Exception as e:
        logger.error(f"Failed to search expert knowledge: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search expert knowledge: {str(e)}"
        )


@router.get(
    "/sessions/{session_id}/escalation-history",
    response_model=List[dict],
    summary="Get escalation history for a session"
)
async def get_escalation_history(
    session_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Get escalation trigger history for a troubleshooting session.
    
    - **session_id**: ID of the session
    """
    try:
        # This would retrieve escalation triggers from the database
        # For now, return empty list as placeholder
        return []
        
    except Exception as e:
        logger.error(f"Failed to get escalation history for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get escalation history: {str(e)}"
        )