"""
Session management service for AI Assistant.
Handles session creation, retrieval, and Redis caching.
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import redis.asyncio as redis
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

from .config import settings
from .models import MessageData, MessageSender, MessageType
from .database import get_db_session

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages AI troubleshooting sessions with Redis caching."""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.session_ttl = 3600 * 24  # 24 hours
        
    async def initialize(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            await self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Session caching disabled.")
            self.redis_client = None
    
    async def cleanup(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
    
    async def create_session(
        self, 
        user_id: str, 
        machine_id: Optional[str] = None,
        language: str = "en",
        problem_description: Optional[str] = None
    ) -> str:
        """
        Create a new troubleshooting session.
        
        Args:
            user_id: ID of the user starting the session
            machine_id: Optional ID of the machine being diagnosed
            language: Language for the session (detected from user profile)
            problem_description: Initial problem description
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        
        # Create session in database
        with get_db_session() as db:
            query = text("""
                INSERT INTO ai_sessions (id, user_id, machine_id, status, problem_description, language, session_metadata)
                VALUES (:session_id, :user_id, :machine_id, 'active', :problem_description, :language, '{}')
            """)
            db.execute(query, {
                'session_id': session_id,
                'user_id': user_id,
                'machine_id': machine_id,
                'problem_description': problem_description,
                'language': language
            })
        
        # Cache session in Redis
        if self.redis_client:
            try:
                session_data = {
                    "session_id": session_id,
                    "user_id": user_id,
                    "machine_id": machine_id,
                    "status": "active",
                    "language": language,
                    "problem_description": problem_description,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                await self.redis_client.setex(
                    f"ai_session:{session_id}",
                    self.session_ttl,
                    json.dumps(session_data)
                )
            except Exception as e:
                logger.warning(f"Failed to cache session in Redis: {e}")
        
        logger.info(f"Created AI session {session_id} for user {user_id} in language {language}")
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session information.
        
        Args:
            session_id: ID of the session to retrieve
            
        Returns:
            Session data or None if not found
        """
        # Try Redis cache first
        if self.redis_client:
            try:
                cached_data = await self.redis_client.get(f"ai_session:{session_id}")
                if cached_data:
                    return json.loads(cached_data)
            except Exception as e:
                logger.warning(f"Failed to retrieve session from Redis: {e}")
        
        # Fallback to database
        with get_db_session() as db:
            query = text("""
                SELECT id, user_id, machine_id, status, problem_description, 
                       resolution_summary, language, session_metadata, created_at, updated_at
                FROM ai_sessions 
                WHERE id = :session_id
            """)
            result = db.execute(query, {'session_id': session_id}).fetchone()
            
            if not result:
                return None
            
            session_data = {
                "session_id": str(result.id),
                "user_id": str(result.user_id),
                "machine_id": str(result.machine_id) if result.machine_id else None,
                "status": result.status,
                "language": result.language,
                "problem_description": result.problem_description,
                "resolution_summary": result.resolution_summary,
                "created_at": result.created_at.isoformat(),
                "updated_at": result.updated_at.isoformat(),
                "metadata": json.loads(result.session_metadata or '{}')
            }
            
            # Update Redis cache
            if self.redis_client:
                try:
                    await self.redis_client.setex(
                        f"ai_session:{session_id}",
                        self.session_ttl,
                        json.dumps(session_data)
                    )
                except Exception as e:
                    logger.warning(f"Failed to update Redis cache: {e}")
            
            return session_data
    
    async def update_session_status(
        self, 
        session_id: str, 
        status: str,
        resolution_summary: Optional[str] = None
    ) -> bool:
        """
        Update session status.
        
        Args:
            session_id: ID of the session to update
            status: New status
            resolution_summary: Optional resolution summary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update database
            with get_db_session() as db:
                if resolution_summary:
                    query = text("""
                        UPDATE ai_sessions 
                        SET status = :status, resolution_summary = :resolution_summary, updated_at = NOW()
                        WHERE id = :session_id
                    """)
                    result = db.execute(query, {
                        'session_id': session_id,
                        'status': status,
                        'resolution_summary': resolution_summary
                    })
                else:
                    query = text("""
                        UPDATE ai_sessions 
                        SET status = :status, updated_at = NOW()
                        WHERE id = :session_id
                    """)
                    result = db.execute(query, {
                        'session_id': session_id,
                        'status': status
                    })
                
                if result.rowcount == 0:
                    return False
            
            # Update Redis cache
            if self.redis_client:
                try:
                    cached_data = await self.redis_client.get(f"ai_session:{session_id}")
                    if cached_data:
                        session_data = json.loads(cached_data)
                        session_data["status"] = status
                        session_data["updated_at"] = datetime.utcnow().isoformat()
                        if resolution_summary:
                            session_data["resolution_summary"] = resolution_summary
                        
                        await self.redis_client.setex(
                            f"ai_session:{session_id}",
                            self.session_ttl,
                            json.dumps(session_data)
                        )
                except Exception as e:
                    logger.warning(f"Failed to update session in Redis: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update session status: {e}")
            return False
    
    async def add_message(
        self,
        session_id: str,
        sender: str,
        content: str,
        message_type: str = "text",
        language: str = "en",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a message to a session.
        
        Args:
            session_id: ID of the session
            sender: Who sent the message
            content: Message content
            message_type: Type of message
            language: Message language
            metadata: Additional message metadata
            
        Returns:
            Message ID
        """
        message_id = str(uuid.uuid4())
        
        # Add to database
        with get_db_session() as db:
            query = text("""
                INSERT INTO ai_messages (message_id, session_id, sender, content, message_type, language, message_metadata)
                VALUES (:message_id, :session_id, :sender, :content, :message_type, :language, :metadata)
            """)
            db.execute(query, {
                'message_id': message_id,
                'session_id': session_id,
                'sender': sender,
                'content': content,
                'message_type': message_type,
                'language': language,
                'metadata': json.dumps(metadata or {})
            })
        
        # Update session timestamp
        await self.update_session_status(session_id, "active")
        
        logger.info(f"Added message {message_id} to session {session_id}")
        return message_id
    
    async def get_user_language(self, user_id: str) -> str:
        """
        Get user's preferred language from ABParts database.
        
        Args:
            user_id: ID of the user
            
        Returns:
            User's preferred language code (defaults to 'en' if not found)
        """
        try:
            with get_db_session() as db:
                # Query user's preferred language from ABParts users table
                query = text("""
                    SELECT preferred_language 
                    FROM users 
                    WHERE id = :user_id
                """)
                result = db.execute(query, {'user_id': user_id}).fetchone()
                
                if result and result.preferred_language:
                    # Map ABParts language codes to supported AI languages
                    language_mapping = {
                        'en': 'en',  # English
                        'el': 'el',  # Greek
                        'ar': 'ar',  # Arabic
                        'es': 'es',  # Spanish
                        'tr': 'tr',  # Turkish
                        'no': 'no'   # Norwegian
                    }
                    return language_mapping.get(result.preferred_language, 'en')
                
        except Exception as e:
            logger.warning(f"Failed to get user language for {user_id}: {e}")
        
        # Default to English if language detection fails
        return 'en'
    
    async def get_session_history(
        self, 
        session_id: str, 
        limit: int = 100
    ) -> List[MessageData]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: ID of the session
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of messages
        """
        messages = []
        
        with get_db_session() as db:
            query = text("""
                SELECT message_id, session_id, sender, content, message_type, language, message_metadata, created_at
                FROM ai_messages 
                WHERE session_id = :session_id 
                ORDER BY created_at ASC 
                LIMIT :limit
            """)
            results = db.execute(query, {'session_id': session_id, 'limit': limit}).fetchall()
            
            for row in results:
                message = MessageData(
                    message_id=str(row.message_id),
                    session_id=str(row.session_id),
                    sender=MessageSender(row.sender),
                    content=row.content,
                    message_type=MessageType(row.message_type),
                    timestamp=row.created_at,
                    language=row.language,
                    metadata=json.loads(row.message_metadata or '{}')
                )
                messages.append(message)
        
        return messages
    
    async def get_user_sessions(
        self, 
        user_id: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent sessions for a user.
        
        Args:
            user_id: ID of the user
            limit: Maximum number of sessions to retrieve
            
        Returns:
            List of session data
        """
        sessions = []
        
        with get_db_session() as db:
            query = text("""
                SELECT id, user_id, machine_id, status, problem_description, 
                       resolution_summary, language, session_metadata, created_at, updated_at
                FROM ai_sessions 
                WHERE user_id = :user_id 
                ORDER BY updated_at DESC 
                LIMIT :limit
            """)
            results = db.execute(query, {'user_id': user_id, 'limit': limit}).fetchall()
            
            for row in results:
                session_data = {
                    "session_id": str(row.id),
                    "user_id": str(row.user_id),
                    "machine_id": str(row.machine_id) if row.machine_id else None,
                    "status": row.status,
                    "language": row.language,
                    "problem_description": row.problem_description,
                    "resolution_summary": row.resolution_summary,
                    "created_at": row.created_at.isoformat(),
                    "updated_at": row.updated_at.isoformat(),
                    "metadata": json.loads(row.session_metadata or '{}')
                }
                sessions.append(session_data)
        
        return sessions


# Global session manager instance
session_manager = SessionManager()