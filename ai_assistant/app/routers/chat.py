"""
Chat endpoints for the AI Assistant service.
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import logging
import uuid
import time

from ..llm_client import LLMClient, ConversationMessage
from ..services.user_service import UserService
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
    llm_client: LLMClient = Depends(get_llm_client),
    user_service: UserService = Depends(get_user_service)
) -> ChatResponse:
    """
    Process a chat message and generate AI response.
    
    This endpoint handles general chat interactions with the AI assistant,
    maintaining conversation context and providing responses in the requested language.
    """
    try:
        # Generate or use provided session ID
        session_id = request.session_id or str(uuid.uuid4())
        
        # Create or update session record if user_id is provided
        if request.user_id:
            try:
                from ..database import get_db_session
                from sqlalchemy import text
                
                with get_db_session() as db:
                    # Check if session exists
                    existing_session = db.execute(
                        text("SELECT session_id FROM ai_sessions WHERE session_id = :session_id"),
                        {'session_id': session_id}
                    ).fetchone()
                    
                    if not existing_session:
                        # Create new session
                        db.execute(text("""
                            INSERT INTO ai_sessions (session_id, user_id, machine_id, status, language, created_at, updated_at)
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
                            WHERE session_id = :session_id
                        """), {
                            'session_id': session_id,
                            'machine_id': request.machine_id,
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
            content=request.message,
            timestamp=time.time()
        ))
        
        # Generate response
        llm_response = await llm_client.generate_response(
            messages=messages,
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