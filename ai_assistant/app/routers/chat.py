"""
Chat endpoints for the AI Assistant service.
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from sqlalchemy import text
import logging
import uuid
import time
from datetime import datetime, timedelta

from ..llm_client import LLMClient, ConversationMessage
from ..services.user_service import UserService
from ..services.security_service import get_security_service, SecurityService
from ..services.audit_service import get_audit_service, AuditService, AuditEventType, AuditSeverity
from ..services.troubleshooting_service import TroubleshootingService
from ..services.learning_service import learning_service
from ..session_manager import SessionManager
from ..database import get_db_session
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


def get_llm_client() -> LLMClient:
    """Dependency to get LLM client from app state."""
    from ..main import app
    if not hasattr(app.state, 'llm_client') or app.state.llm_client is None:
        raise HTTPException(status_code=503, detail="LLM client not initialized")
    return app.state.llm_client


def get_user_service() -> UserService:
    """Dependency to get user service."""
    return UserService()


def get_troubleshooting_service(
    llm_client: LLMClient = Depends(get_llm_client)
) -> TroubleshootingService:
    """Dependency to get troubleshooting service."""
    from ..main import app
    if not hasattr(app.state, 'session_manager') or app.state.session_manager is None:
        raise HTTPException(status_code=503, detail="Session manager not initialized")
    return TroubleshootingService(llm_client, app.state.session_manager)


def _detect_troubleshooting_intent(message: str) -> bool:
    """Detect if user message indicates a troubleshooting scenario."""
    troubleshooting_keywords = [
        # English - Problem words
        'problem', 'issue', 'not working', 'not start', 'does not', 'broken', 'error', 'trouble', 'help',
        'won\'t', 'doesn\'t', 'can\'t', 'failed', 'stopped', 'wrong', 'wont start', 'doesnt start',
        # English - Symptom words (gauges, indicators, performance issues)
        'gauge', 'red', 'low pressure', 'high pressure', 'leak', 'noise', 'vibration', 'smell',
        'smoke', 'overheating', 'slow', 'weak', 'poor', 'bad', 'strange', 'unusual',
        # Greek
        'πρόβλημα', 'ζήτημα', 'δεν λειτουργεί', 'χαλασμένο', 'σφάλμα',
        # Arabic
        'مشكلة', 'خطأ', 'لا يعمل', 'معطل',
        # Spanish
        'problema', 'error', 'no funciona', 'roto',
        # Turkish
        'sorun', 'hata', 'çalışmıyor', 'bozuk',
        # Norwegian
        'problem', 'feil', 'fungerer ikke', 'ødelagt'
    ]
    
    message_lower = message.lower()
    detected = any(keyword in message_lower for keyword in troubleshooting_keywords)
    
    # DEBUG: Log detection result
    print(f"[DETECTION] Message: '{message}' -> Detected: {detected}")
    logger.info(f"[DETECTION] Message: '{message}' -> Detected: {detected}")
    
    return detected


# Request/Response models
class ChatMessage(BaseModel):
    """Chat message model."""
    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content")
    timestamp: Optional[float] = Field(default=None, description="Message timestamp")


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(default=None, description="Session ID for conversation continuity")
    language: Optional[str] = Field(default=None, description="Response language code (auto-detected if not provided)")
    user_id: Optional[str] = Field(default=None, description="User ID for language detection")
    machine_id: Optional[str] = Field(default=None, description="AutoBoss machine ID for context")
    conversation_history: List[ChatMessage] = Field(default=[], description="Previous conversation messages")


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str = Field(..., description="AI assistant response")
    session_id: str = Field(..., description="Session ID")
    model_used: str = Field(..., description="LLM model used for response")
    tokens_used: int = Field(..., description="Number of tokens consumed")
    response_time: float = Field(..., description="Response generation time in seconds")
    success: bool = Field(..., description="Whether the response was generated successfully")
    error_message: Optional[str] = Field(default=None, description="Error message if generation failed")
    message_type: Optional[str] = Field(default="text", description="Message type: text, diagnostic_step, completion")
    step_data: Optional[Dict[str, Any]] = Field(default=None, description="Troubleshooting step data if applicable")


class StepFeedbackRequest(BaseModel):
    """Step feedback request model."""
    session_id: str = Field(..., description="Troubleshooting session ID")
    step_id: str = Field(..., description="ID of the step being responded to")
    feedback: str = Field(..., description="User feedback: worked, didnt_work, partially_worked, or free text")
    language: Optional[str] = Field(default="en", description="Response language code")
    user_id: Optional[str] = Field(default=None, description="User ID for context")


class StepFeedbackResponse(BaseModel):
    """Step feedback response model."""
    feedback_received: bool = Field(..., description="Whether feedback was successfully processed")
    workflow_status: str = Field(..., description="Workflow status: in_progress, completed, escalated")
    next_step: Optional[ChatResponse] = Field(default=None, description="Next troubleshooting step if workflow continues")
    completion_message: Optional[str] = Field(default=None, description="Completion message if workflow is done")


class ProblemAnalysisRequest(BaseModel):
    """Problem analysis request model."""
    problem_description: str = Field(..., description="Description of the problem")
    machine_id: Optional[str] = Field(default=None, description="AutoBoss machine ID")
    language: Optional[str] = Field(default=None, description="Response language code (auto-detected if not provided)")
    user_id: Optional[str] = Field(default=None, description="User ID for language detection")
    machine_context: Optional[Dict[str, Any]] = Field(default=None, description="Machine-specific context")


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    authorization: Optional[str] = Header(None),
    x_forwarded_for: Optional[str] = Header(None),
    user_agent: Optional[str] = Header(None),
    llm_client: LLMClient = Depends(get_llm_client),
    user_service: UserService = Depends(get_user_service),
    security_service: SecurityService = Depends(get_security_service),
    audit_service: AuditService = Depends(get_audit_service)
) -> ChatResponse:
    """
    Process a chat message and generate AI response.
    
    This endpoint handles general chat interactions with the AI assistant,
    maintaining conversation context and providing responses in the requested language.
    
    Automatically detects troubleshooting scenarios and initiates interactive
    step-by-step workflows when appropriate.
    """
    # CRITICAL: Log at entry point
    print(f"[ENTRY] Chat endpoint called - message: {request.message[:50]}, machine_id: {request.machine_id}, user_id: {request.user_id}")
    logger.info(f"[ENTRY] Chat endpoint - message: {request.message[:50]}, machine_id: {request.machine_id}")
    
    try:
        # Track response time
        start_time = time.time()
        
        # Generate or use provided session ID
        session_id = request.session_id or str(uuid.uuid4())
        
        # Check for sensitive data in user message
        filtered_message, detections = security_service.filter_sensitive_data(
            request.message,
            redact=True
        )
        
        # Log sensitive data detection if found
        if detections:
            logger.warning(f"Sensitive data detected in message for session {session_id}: {len(detections)} pattern(s)")
            # Store detection in database for audit
            try:
                with get_db_session() as db:
                    from sqlalchemy import text
                    db.execute(text("""
                        INSERT INTO sensitive_data_detections 
                        (id, session_id, detection_type, detected_at, action_taken, details)
                        VALUES (:id, :session_id, :detection_type, NOW(), :action_taken, :details)
                    """), {
                        'id': str(uuid.uuid4())[:32],
                        'session_id': session_id,
                        'detection_type': ','.join([d['type'] for d in detections]),
                        'action_taken': 'redacted',
                        'details': str({'count': len(detections)})
                    })
            except Exception as e:
                logger.error(f"Failed to log sensitive data detection: {e}")
        
        # Use filtered message for processing
        message_to_process = filtered_message
        
        # Create or update session record if user_id is provided
        if request.user_id:
            try:
                from ..database import get_db_session
                from sqlalchemy import text
                
                with get_db_session() as db:
                    # Check if session exists
                    existing_session = db.execute(
                        text("SELECT id FROM ai_sessions WHERE id = :session_id"),
                        {'session_id': session_id}
                    ).fetchone()
                    
                    if not existing_session:
                        # Create new session
                        db.execute(text("""
                            INSERT INTO ai_sessions (id, user_id, machine_id, status, language, created_at, updated_at)
                            VALUES (:session_id, :user_id, :machine_id, :status, :language, NOW(), NOW())
                        """), {
                            'session_id': session_id,
                            'user_id': request.user_id,
                            'machine_id': request.machine_id,
                            'status': 'active',
                            'language': request.language or 'en'
                        })
                        logger.info(f"Created new AI session {session_id} for user {request.user_id}")
                    else:
                        # Update existing session
                        db.execute(text("""
                            UPDATE ai_sessions 
                            SET updated_at = NOW(), machine_id = :machine_id, language = :language
                            WHERE id = :session_id
                        """), {
                            'session_id': session_id,
                            'machine_id': request.machine_id,
                            'language': request.language or 'en'
                        })
                    
                    # Store user message
                    db.execute(text("""
                        INSERT INTO ai_messages (id, session_id, sender, content, message_type, language, timestamp)
                        VALUES (:id, :session_id, :sender, :content, :message_type, :language, NOW())
                    """), {
                        'id': str(uuid.uuid4()),
                        'session_id': session_id,
                        'sender': 'user',
                        'content': message_to_process,
                        'message_type': 'text',
                        'language': request.language or 'en'
                    })
                        
            except Exception as e:
                logger.warning(f"Failed to create/update session record: {e}")
                # Continue without session record - escalation won't work but chat will
        
        # Determine language to use
        language = request.language or "en"
        
        # Auto-detect language from user profile if user_id provided and no explicit language
        if request.user_id and not request.language:
            try:
                detected_language = await user_service.get_user_language(request.user_id)
                language = detected_language
                logger.info(f"Auto-detected language {language} for user {request.user_id}")
            except Exception as e:
                logger.warning(f"Failed to auto-detect language for user {request.user_id}: {e}")
                # Continue with default language
        
        # WORKAROUND: If no session_id provided, try to find RECENT active troubleshooting session
        # This handles cases where frontend doesn't maintain session_id
        # Only reuse session if it was updated in the last 5 minutes (active conversation)
        if not request.session_id and request.user_id and request.machine_id:
            try:
                with get_db_session() as db:
                    # Look for ANY active session, not just ones with uncompleted steps
                    # This allows clarifications to work even after steps are marked complete
                    query = text("""
                        SELECT s.id, s.updated_at
                        FROM ai_sessions s
                        WHERE s.user_id = :user_id 
                          AND s.machine_id = :machine_id
                          AND s.status = 'active'
                          AND s.updated_at > NOW() - INTERVAL '5 minutes'
                        ORDER BY s.updated_at DESC
                        LIMIT 1
                    """)
                    result = db.execute(query, {
                        'user_id': request.user_id,
                        'machine_id': request.machine_id
                    }).fetchone()
                    
                    if result:
                        request.session_id = str(result[0])
                        session_id = request.session_id
                        logger.info(f"Found recent active session: {request.session_id} (updated: {result[1]})")
                        print(f"[DEBUG] Reusing recent session for user {request.user_id}, machine {request.machine_id}: {request.session_id}")
                    else:
                        # No recent session found - will start fresh
                        logger.info(f"No recent active session found for user {request.user_id}, machine {request.machine_id} - will start fresh")
            except Exception as e:
                logger.warning(f"Failed to find active session: {e}")
        
        # FIRST: Check if session is already in active troubleshooting mode
        # This must happen BEFORE checking if troubleshooting should start
        if request.session_id:
            try:
                from ..session_manager import session_manager
                troubleshooting_service = TroubleshootingService(llm_client, session_manager)
                workflow_state = await troubleshooting_service.get_workflow_state(request.session_id)
                
                # DEBUG: Log workflow state details
                if workflow_state:
                    print(f"[DEBUG] Workflow state found for session {request.session_id}")
                    print(f"[DEBUG] Current step: {workflow_state.current_step}")
                    print(f"[DEBUG] Workflow status: {workflow_state.workflow_status}")
                    print(f"[DEBUG] Completed steps: {len(workflow_state.completed_steps)}")
                    logger.info(f"[DEBUG] Workflow state - current_step: {workflow_state.current_step is not None}, status: {workflow_state.workflow_status}")
                else:
                    print(f"[DEBUG] No workflow state found for session {request.session_id}")
                    logger.info(f"[DEBUG] No workflow state found for session {request.session_id}")
                
                if workflow_state and workflow_state.current_step is not None:
                    logger.info(f"Session {request.session_id} is in active troubleshooting - processing clarification")
                    print(f"[DEBUG] Active troubleshooting detected - processing clarification")
                    
                    # Process as clarification
                    next_step = await troubleshooting_service.process_clarification(
                        session_id=request.session_id,
                        clarification=message_to_process,
                        language=language
                    )
                    
                    if next_step:
                        # Store user message
                        if request.user_id:
                            try:
                                with get_db_session() as db:
                                    db.execute(text("""
                                        INSERT INTO ai_messages (id, session_id, sender, content, message_type, language, timestamp)
                                        VALUES (:id, :session_id, :sender, :content, :message_type, :language, NOW())
                                    """), {
                                        'id': str(uuid.uuid4()),
                                        'session_id': request.session_id,
                                        'sender': 'user',
                                        'content': message_to_process,
                                        'message_type': 'text',
                                        'language': language
                                    })
                                    
                                    # Store assistant response
                                    db.execute(text("""
                                        INSERT INTO ai_messages (id, session_id, sender, content, message_type, language, timestamp)
                                        VALUES (:id, :session_id, :sender, :content, :message_type, :language, NOW())
                                    """), {
                                        'id': str(uuid.uuid4()),
                                        'session_id': request.session_id,
                                        'sender': 'assistant',
                                        'content': next_step.instruction,
                                        'message_type': 'diagnostic_step',
                                        'language': language
                                    })
                            except Exception as e:
                                logger.warning(f"Failed to store messages: {e}")
                        
                        return ChatResponse(
                            response=next_step.instruction,
                            session_id=request.session_id,
                            model_used="troubleshooting-engine",
                            tokens_used=0,
                            response_time=time.time() - start_time,
                            success=True,
                            message_type="diagnostic_step",
                            step_data={
                                "step_id": next_step.step_id,
                                "step_number": next_step.step_number,
                                "estimated_duration": next_step.estimated_duration,
                                "confidence_score": next_step.confidence_score,
                                "requires_feedback": next_step.requires_feedback,
                                "safety_warnings": next_step.safety_warnings,
                                "expected_outcomes": next_step.expected_outcomes
                            }
                        )
            except Exception as e:
                logger.warning(f"Failed to check troubleshooting state: {e}")
                import traceback
                traceback.print_exc()
                # Continue to regular chat handling
        
        # THEN: Detect if this is a troubleshooting scenario
        is_troubleshooting = _detect_troubleshooting_intent(message_to_process)
        
        # CRITICAL DEBUG LOGGING
        print(f"[DEBUG] Troubleshooting detection: is_troubleshooting={is_troubleshooting}, machine_id={request.machine_id}, history_len={len(request.conversation_history)}")
        logger.info(f"[DEBUG] Troubleshooting detection: is_troubleshooting={is_troubleshooting}, machine_id={request.machine_id}, history_len={len(request.conversation_history)}")
        print(f"[DEBUG] Message: {message_to_process[:50]}")
        logger.info(f"[DEBUG] Message: {message_to_process[:50]}")
        
        # Check if we should start interactive troubleshooting workflow
        # Count only user messages to exclude system messages
        user_messages = [msg for msg in request.conversation_history if msg.role == 'user']
        
        # IMPORTANT: Step-by-step troubleshooting should be the DEFAULT for ALL troubleshooting scenarios
        # Machine ID is optional - if provided, we get machine-specific context
        # If not provided, we still do step-by-step troubleshooting, just more generic
        if is_troubleshooting and len(user_messages) <= 1:
            print(f"[DEBUG] TRIGGERING TROUBLESHOOTING WORKFLOW for session {session_id} (machine_id: {request.machine_id or 'None'})")
            logger.info(f"[DEBUG] Starting interactive troubleshooting workflow for session {session_id}")
            
            # IMPORTANT: Auto-complete any old active sessions for this user+machine
            # This prevents old sessions from interfering with new troubleshooting
            if request.user_id and request.machine_id:
                try:
                    with get_db_session() as db:
                        # Find and complete old active sessions
                        old_sessions_query = text("""
                            UPDATE ai_sessions 
                            SET status = 'abandoned', 
                                resolution_summary = 'Auto-completed: New troubleshooting session started',
                                updated_at = NOW()
                            WHERE user_id = :user_id 
                              AND machine_id = :machine_id
                              AND status = 'active'
                              AND id != :current_session_id
                            RETURNING id
                        """)
                        old_sessions = db.execute(old_sessions_query, {
                            'user_id': request.user_id,
                            'machine_id': request.machine_id,
                            'current_session_id': session_id
                        }).fetchall()
                        
                        if old_sessions:
                            old_session_ids = [str(row[0]) for row in old_sessions]
                            logger.info(f"Auto-completed {len(old_session_ids)} old sessions: {old_session_ids}")
                            print(f"[DEBUG] Auto-completed old sessions: {old_session_ids}")
                except Exception as e:
                    logger.warning(f"Failed to auto-complete old sessions: {e}")
            
            # Start interactive troubleshooting workflow
            try:
                from ..session_manager import session_manager
                troubleshooting_service = TroubleshootingService(llm_client, session_manager)
                
                # Start the workflow
                diagnostic_assessment = await troubleshooting_service.start_troubleshooting_workflow(
                    session_id=session_id,
                    problem_description=message_to_process,
                    machine_id=request.machine_id,
                    user_id=request.user_id,
                    language=language
                )
                
                # Get the first step
                workflow_state = await troubleshooting_service.get_workflow_state(session_id)
                print(f"[DEBUG] Workflow state retrieved: {workflow_state}")
                logger.info(f"[DEBUG] Workflow state: {workflow_state}")
                
                if workflow_state and workflow_state.current_step:
                    print(f"[DEBUG] Returning troubleshooting step")
                    # Return first step with special formatting
                    step = workflow_state.current_step
                    
                    # Store encrypted AI response if user_id provided
                    if request.user_id:
                        try:
                            with get_db_session() as db:
                                db.execute(text("""
                                    INSERT INTO ai_messages (id, session_id, sender, content, message_type, language, timestamp)
                                    VALUES (:id, :session_id, :sender, :content, :message_type, :language, NOW())
                                """), {
                                    'id': str(uuid.uuid4()),
                                    'session_id': session_id,
                                    'sender': 'assistant',
                                    'content': step.instruction,
                                    'message_type': 'diagnostic_step',
                                    'language': language
                                })
                        except Exception as e:
                            logger.warning(f"Failed to store AI response: {e}")
                    
                    return ChatResponse(
                        response=step.instruction,
                        session_id=session_id,
                        model_used="troubleshooting-engine",
                        tokens_used=0,
                        response_time=time.time() - start_time,
                        success=True,
                        message_type="diagnostic_step",
                        step_data={
                            "step_id": step.step_id,
                            "step_number": step.step_number,
                            "estimated_duration": step.estimated_duration,
                            "confidence_score": step.confidence_score,
                            "requires_feedback": step.requires_feedback,
                            "safety_warnings": step.safety_warnings,
                            "expected_outcomes": step.expected_outcomes
                        }
                    )
                    
            except Exception as e:
                print(f"[DEBUG] Exception in troubleshooting workflow: {e}")
                import traceback
                traceback.print_exc()
                logger.warning(f"Failed to start troubleshooting workflow: {e}")
                # Fall through to regular chat if troubleshooting fails
        
        # Get machine context if machine_id provided
        machine_context = None
        if request.machine_id:
            try:
                machine_context = await user_service.get_machine_context(request.machine_id)
            except Exception as e:
                logger.warning(f"Failed to get machine context for machine {request.machine_id}: {e}")
        
        # Build conversation messages
        messages = []
        
        # Add conversation history
        for msg in request.conversation_history:
            messages.append(ConversationMessage(
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp
            ))
        
        # Add current user message
        messages.append(ConversationMessage(
            role="user",
            content=message_to_process,
            timestamp=time.time()
        ))
        
        # Generate response
        llm_response = await llm_client.generate_response(
            messages=messages,
            language=language
        )
        
        # Store encrypted AI response if user_id provided
        if request.user_id:
            try:
                with get_db_session() as db:
                    db.execute(text("""
                        INSERT INTO ai_messages (id, session_id, sender, content, message_type, language, timestamp)
                        VALUES (:id, :session_id, :sender, :content, :message_type, :language, NOW())
                    """), {
                        'id': str(uuid.uuid4()),
                        'session_id': session_id,
                        'sender': 'assistant',
                        'content': llm_response.content,
                        'message_type': 'text',
                        'language': language
                    })
            except Exception as e:
                logger.warning(f"Failed to store AI response: {e}")
        
        return ChatResponse(
            response=llm_response.content,
            session_id=session_id,
            model_used=llm_response.model_used,
            tokens_used=llm_response.tokens_used,
            response_time=llm_response.response_time,
            success=llm_response.success,
            error_message=llm_response.error_message
        )
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process chat message: {str(e)}")


@router.post("/analyze-problem", response_model=ChatResponse)
async def analyze_problem(
    request: ProblemAnalysisRequest,
    authorization: Optional[str] = Header(None),
    llm_client: LLMClient = Depends(get_llm_client),
    user_service: UserService = Depends(get_user_service)
) -> ChatResponse:
    """
    Analyze a problem description and provide diagnostic assessment.
    
    This endpoint is specifically designed for troubleshooting workflows,
    providing structured diagnostic analysis and troubleshooting steps.
    """
    try:
        # Generate session ID for this analysis
        session_id = str(uuid.uuid4())
        
        # Determine language to use
        language = request.language or "en"
        
        # Auto-detect language from user profile if user_id provided and no explicit language
        if request.user_id and not request.language:
            try:
                detected_language = await user_service.get_user_language(request.user_id)
                language = detected_language
                logger.info(f"Auto-detected language {language} for user {request.user_id}")
            except Exception as e:
                logger.warning(f"Failed to auto-detect language for user {request.user_id}: {e}")
                # Continue with default language
        
        # Get machine context if machine_id provided
        machine_context = request.machine_context
        if request.machine_id and not machine_context:
            try:
                machine_context = await user_service.get_machine_context(request.machine_id)
            except Exception as e:
                logger.warning(f"Failed to get machine context for machine {request.machine_id}: {e}")
        
        # Analyze the problem
        llm_response = await llm_client.analyze_problem(
            problem_description=request.problem_description,
            machine_context=machine_context,
            language=language
        )
        
        return ChatResponse(
            response=llm_response.content,
            session_id=session_id,
            model_used=llm_response.model_used,
            tokens_used=llm_response.tokens_used,
            response_time=llm_response.response_time,
            success=llm_response.success,
            error_message=llm_response.error_message
        )
        
    except Exception as e:
        logger.error(f"Problem analysis endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze problem: {str(e)}")


@router.post("/chat/step-feedback", response_model=StepFeedbackResponse)
async def submit_step_feedback(
    request: StepFeedbackRequest,
    authorization: Optional[str] = Header(None),
    troubleshooting_service: TroubleshootingService = Depends(get_troubleshooting_service)
) -> StepFeedbackResponse:
    """
    Submit feedback for a troubleshooting step and receive the next step.
    
    This endpoint processes user feedback on a troubleshooting step and either:
    - Returns the next step if troubleshooting should continue
    - Marks the workflow as completed if problem is resolved
    - Escalates to expert support if needed
    """
    try:
        # Process the feedback and get next step
        next_step = await troubleshooting_service.process_user_feedback(
            session_id=request.session_id,
            step_id=request.step_id,
            user_feedback=request.feedback,
            language=request.language
        )
        
        if next_step is None:
            # Workflow is complete or escalated
            # Check session status to determine which
            workflow_state = await troubleshooting_service.get_workflow_state(request.session_id)
            
            if workflow_state and workflow_state.workflow_status == "completed":
                return StepFeedbackResponse(
                    feedback_received=True,
                    workflow_status="completed",
                    next_step=None,
                    completion_message="Problem resolved! The troubleshooting workflow is complete."
                )
            elif workflow_state and workflow_state.workflow_status == "escalated":
                return StepFeedbackResponse(
                    feedback_received=True,
                    workflow_status="escalated",
                    next_step=None,
                    completion_message="This issue requires expert assistance. Please use the escalation button to contact support."
                )
            else:
                return StepFeedbackResponse(
                    feedback_received=True,
                    workflow_status="completed",
                    next_step=None,
                    completion_message="Troubleshooting workflow ended."
                )
        
        # Format next step as ChatResponse
        next_step_response = ChatResponse(
            response=next_step.instruction,
            session_id=request.session_id,
            model_used="troubleshooting-engine",
            tokens_used=0,
            response_time=0.0,
            success=True,
            message_type="diagnostic_step",
            step_data={
                "step_id": next_step.step_id,
                "step_number": next_step.step_number,
                "estimated_duration": next_step.estimated_duration,
                "confidence_score": next_step.confidence_score,
                "requires_feedback": next_step.requires_feedback,
                "safety_warnings": next_step.safety_warnings,
                "expected_outcomes": next_step.expected_outcomes
            }
        )
        
        return StepFeedbackResponse(
            feedback_received=True,
            workflow_status="in_progress",
            next_step=next_step_response,
            completion_message=None
        )
        
    except Exception as e:
        logger.error(f"Step feedback endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process step feedback: {str(e)}")


@router.get("/users/{user_id}/machines")
async def get_user_machines(
    user_id: str,
    authorization: Optional[str] = Header(None),
    user_service: UserService = Depends(get_user_service)
) -> Dict[str, Any]:
    """
    Get all machines accessible to a user.
    
    This endpoint returns all AutoBoss machines that the user can access
    based on their organization and role permissions.
    """
    try:
        # Extract token from Authorization header if provided
        auth_token = None
        if authorization:
            auth_token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
        
        machines = await user_service.get_user_machines(user_id)
        
        return {
            "user_id": user_id,
            "machines": machines,
            "count": len(machines)
        }
        
    except Exception as e:
        logger.error(f"Get user machines endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve user machines: {str(e)}")


@router.get("/machines/{machine_id}/context")
async def get_machine_context(
    machine_id: str,
    authorization: Optional[str] = Header(None),
    user_service: UserService = Depends(get_user_service)
) -> Dict[str, Any]:
    """
    Get comprehensive machine context for troubleshooting.
    
    This endpoint returns detailed machine information including maintenance history,
    parts usage, and preventive maintenance suggestions.
    """
    try:
        # Extract token from Authorization header if provided
        auth_token = None
        if authorization:
            auth_token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
        
        machine_context = await user_service.get_machine_context(machine_id)
        
        if not machine_context:
            raise HTTPException(status_code=404, detail=f"Machine not found: {machine_id}")
        
        return {
            "machine_id": machine_id,
            "context": machine_context
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get machine context endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve machine context: {str(e)}")


@router.get("/models")
async def get_available_models() -> Dict[str, Any]:
    """Get information about available LLM models."""
    return {
        "primary_model": settings.OPENAI_MODEL,
        "fallback_model": settings.OPENAI_FALLBACK_MODEL,
        "supported_languages": [
            {"code": "en", "name": "English"},
            {"code": "el", "name": "Greek (Ελληνικά)"},
            {"code": "ar", "name": "Arabic (العربية)"},
            {"code": "es", "name": "Spanish (Español)"},
            {"code": "tr", "name": "Turkish (Türkçe)"},
            {"code": "no", "name": "Norwegian (Norsk)"}
        ],
        "max_tokens": settings.OPENAI_MAX_TOKENS,
        "temperature": settings.OPENAI_TEMPERATURE
    }


@router.get("/session/{session_id}/status")
async def get_session_status(session_id: str) -> Dict[str, Any]:
    """
    Get status information for a chat session.
    
    Note: This is a placeholder endpoint. In a full implementation,
    this would retrieve session data from Redis or database.
    """
    return {
        "session_id": session_id,
        "status": "active",
        "created_at": time.time(),
        "message_count": 0,
        "last_activity": time.time()
    }