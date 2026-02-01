"""
API endpoints for AI session management.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
import uuid

from ..schemas import (
    CreateSessionRequest, CreateSessionResponse,
    SendMessageRequest, SendMessageResponse,
    UpdateSessionRequest, SessionResponse,
    SessionHistoryResponse, UserSessionsResponse,
    ErrorResponse, MessageResponse, SessionStatusEnum
)
from ..session_manager import session_manager
from ..models import MessageSender, MessageType
from ..llm_client import LLMClient
from ..services.security_service import get_security_service, SecurityService

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extract user ID from JWT token.
    For now, we'll use a mock implementation.
    In production, this should validate the JWT and extract user info.
    """
    # TODO: Implement proper JWT validation with ABParts auth
    # For now, return the superadmin user ID for testing
    return "f6abc555-5b6c-6f7a-8b9c-0d123456789a"


async def get_llm_client() -> LLMClient:
    """Get LLM client instance."""
    # This should be injected from the main app
    from ..main import app
    return app.state.llm_client


@router.post(
    "/sessions",
    response_model=CreateSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new AI troubleshooting session"
)
async def create_session(
    request: CreateSessionRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Create a new AI troubleshooting session.
    
    - **machine_id**: Optional ID of the machine being diagnosed
    - **language**: Language for the session (auto-detected from user profile if not provided)
    - **problem_description**: Initial problem description
    """
    try:
        # Auto-detect user language if not provided
        language = request.language
        if not language or language == "auto":
            language = await session_manager.get_user_language(user_id)
            logger.info(f"Auto-detected language '{language}' for user {user_id}")
        
        session_id = await session_manager.create_session(
            user_id=user_id,
            machine_id=request.machine_id,
            language=language,
            problem_description=request.problem_description
        )
        
        # Add initial system message if problem description provided
        if request.problem_description:
            await session_manager.add_message(
                session_id=session_id,
                sender="system",
                content=f"Session started. Problem: {request.problem_description}",
                language=language
            )
        
        return CreateSessionResponse(
            session_id=session_id,
            status="created",
            message="AI troubleshooting session created successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )


@router.post(
    "/sessions/{session_id}/messages",
    response_model=SendMessageResponse,
    summary="Send a message in an AI session"
)
async def send_message(
    session_id: str,
    request: SendMessageRequest,
    user_id: str = Depends(get_current_user_id),
    llm_client: LLMClient = Depends(get_llm_client)
):
    """
    Send a message in an AI troubleshooting session and get AI response.
    
    - **session_id**: ID of the session
    - **content**: Message content
    - **message_type**: Type of message (text, voice, etc.)
    - **language**: Message language
    - **metadata**: Additional message metadata
    """
    try:
        # Validate session exists and belongs to user
        session_data = await session_manager.get_session(session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        if session_data["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this session"
            )
        
        # Use session language if not provided in request
        message_language = request.language
        if not message_language or message_language == "auto":
            message_language = session_data.get("language", "en")
        
        # Add user message
        message_id = await session_manager.add_message(
            session_id=session_id,
            sender="user",
            content=request.content,
            message_type=request.message_type.value,
            language=message_language,
            metadata=request.metadata
        )
        
        # Generate AI response
        ai_response = None
        try:
            # Get conversation history for context
            history = await session_manager.get_session_history(session_id, limit=10)
            
            # Build context for LLM
            context = {
                "session_id": session_id,
                "machine_id": session_data.get("machine_id"),
                "language": message_language,
                "conversation_history": [
                    {"sender": msg.sender.value, "content": msg.content}
                    for msg in history[-5:]  # Last 5 messages for context
                ]
            }
            
            # Generate AI response
            ai_content = await llm_client.generate_simple_response(
                prompt=request.content,
                context=context,
                language=message_language
            )
            
            # Add AI response to session
            ai_message_id = await session_manager.add_message(
                session_id=session_id,
                sender="assistant",
                content=ai_content,
                message_type="text",
                language=message_language
            )
            
            ai_response = MessageResponse(
                message_id=ai_message_id,
                session_id=session_id,
                sender=MessageSenderEnum.assistant,
                content=ai_content,
                message_type=MessageTypeEnum.text,
                language=message_language,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Failed to generate AI response: {e}")
            # Continue without AI response - user message was still saved
        
        return SendMessageResponse(
            message_id=message_id,
            ai_response=ai_response,
            status="sent",
            message="Message sent successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@router.get(
    "/sessions/{session_id}/history",
    response_model=SessionHistoryResponse,
    summary="Get conversation history for a session"
)
async def get_session_history(
    session_id: str,
    limit: int = 100,
    user_id: str = Depends(get_current_user_id),
    security_service: SecurityService = Depends(get_security_service)
):
    """
    Get conversation history for an AI troubleshooting session.
    
    Messages are automatically decrypted before being returned.
    
    - **session_id**: ID of the session
    - **limit**: Maximum number of messages to retrieve (default: 100)
    """
    try:
        # Validate session exists and belongs to user
        session_data = await session_manager.get_session(session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        if session_data["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this session"
            )
        
        # Get message history
        messages = await session_manager.get_session_history(session_id, limit)
        
        # Convert to response format and decrypt messages
        message_responses = []
        for msg in messages:
            # Decrypt message content if encrypted
            content = msg.content
            try:
                # Attempt to decrypt - if it fails, content is not encrypted
                content = security_service.decrypt_message(msg.content)
            except Exception as e:
                logger.debug(f"Message {msg.message_id} not encrypted or decryption failed: {e}")
            
            message_responses.append(MessageResponse(
                message_id=msg.message_id,
                session_id=msg.session_id,
                sender=msg.sender,
                content=content,
                message_type=msg.message_type,
                language=msg.language,
                timestamp=msg.timestamp,
                metadata=msg.metadata
            ))
        
        return SessionHistoryResponse(
            session_id=session_id,
            messages=message_responses,
            total_messages=len(message_responses)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session history: {str(e)}"
        )


@router.get(
    "/sessions/{session_id}",
    response_model=SessionResponse,
    summary="Get session information"
)
async def get_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Get information about an AI troubleshooting session.
    
    - **session_id**: ID of the session
    """
    try:
        session_data = await session_manager.get_session(session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        if session_data["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this session"
            )
        
        return SessionResponse(
            session_id=session_data["session_id"],
            user_id=session_data["user_id"],
            machine_id=session_data.get("machine_id"),
            status=SessionStatusEnum(session_data["status"]),
            language=session_data["language"],
            problem_description=session_data.get("problem_description"),
            resolution_summary=session_data.get("resolution_summary"),
            created_at=datetime.fromisoformat(session_data["created_at"]),
            updated_at=datetime.fromisoformat(session_data["updated_at"]),
            metadata=session_data.get("metadata")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session: {str(e)}"
        )


@router.put(
    "/sessions/{session_id}",
    response_model=SessionResponse,
    summary="Update session status"
)
async def update_session(
    session_id: str,
    request: UpdateSessionRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Update the status of an AI troubleshooting session.
    
    - **session_id**: ID of the session
    - **status**: New session status
    - **resolution_summary**: Optional resolution summary
    """
    try:
        # Validate session exists and belongs to user
        session_data = await session_manager.get_session(session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        if session_data["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this session"
            )
        
        # Update session
        success = await session_manager.update_session_status(
            session_id=session_id,
            status=request.status.value,
            resolution_summary=request.resolution_summary
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update session"
            )
        
        # Return updated session data
        updated_session = await session_manager.get_session(session_id)
        return SessionResponse(
            session_id=updated_session["session_id"],
            user_id=updated_session["user_id"],
            machine_id=updated_session.get("machine_id"),
            status=SessionStatusEnum(updated_session["status"]),
            language=updated_session["language"],
            problem_description=updated_session.get("problem_description"),
            resolution_summary=updated_session.get("resolution_summary"),
            created_at=datetime.fromisoformat(updated_session["created_at"]),
            updated_at=datetime.fromisoformat(updated_session["updated_at"]),
            metadata=updated_session.get("metadata")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update session: {str(e)}"
        )


@router.get(
    "/users/{user_id}/sessions",
    response_model=UserSessionsResponse,
    summary="Get user's recent sessions"
)
async def get_user_sessions(
    user_id: str,
    limit: int = 10,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get recent AI troubleshooting sessions for a user.
    
    - **user_id**: ID of the user
    - **limit**: Maximum number of sessions to retrieve (default: 10)
    """
    try:
        # Users can only access their own sessions
        if user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to other user's sessions"
            )
        
        sessions_data = await session_manager.get_user_sessions(user_id, limit)
        
        sessions = [
            SessionResponse(
                session_id=session["session_id"],
                user_id=session["user_id"],
                machine_id=session.get("machine_id"),
                status=SessionStatusEnum(session["status"]),
                language=session["language"],
                problem_description=session.get("problem_description"),
                resolution_summary=session.get("resolution_summary"),
                created_at=datetime.fromisoformat(session["created_at"]),
                updated_at=datetime.fromisoformat(session["updated_at"]),
                metadata=session.get("metadata")
            )
            for session in sessions_data
        ]
        
        return UserSessionsResponse(
            user_id=user_id,
            sessions=sessions,
            total_sessions=len(sessions)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user sessions: {str(e)}"
        )