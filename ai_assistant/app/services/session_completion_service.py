"""
Service for handling session completion and learning extraction.
"""

import json
import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy import text

from ..database import get_db_session
from ..llm_client import LLMClient, ConversationMessage

logger = logging.getLogger(__name__)


class SessionCompletionService:
    """Service for processing completed sessions and extracting learnings."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    async def complete_session(
        self,
        session_id: str,
        outcome_type: str,  # 'resolved', 'escalated', 'abandoned'
        resolution_summary: Optional[str] = None
    ) -> None:
        """
        Mark session as complete and extract learnings.
        
        Args:
            session_id: ID of the session to complete
            outcome_type: Type of outcome
            resolution_summary: Optional summary of resolution
        """
        logger.info(f"Completing session {session_id} with outcome: {outcome_type}")
        
        # Get session data
        session_data = await self._get_session_data(session_id)
        if not session_data:
            logger.error(f"Session {session_id} not found")
            return
        
        # Calculate metrics
        steps_taken = session_data['step_count']
        resolution_time = self._calculate_resolution_time(session_data)
        
        # Extract learnings from session
        key_learnings = await self._extract_learnings(session_data)
        
        # Store session outcome
        await self._store_session_outcome(
            session_id=session_id,
            outcome_type=outcome_type,
            resolution_time_minutes=resolution_time,
            steps_taken=steps_taken,
            key_learnings=key_learnings
        )
        
        # Update session status
        await self._update_session_status(session_id, outcome_type, resolution_summary)
        
        # Process learnings
        if key_learnings:
            await self._process_learnings(session_data, key_learnings)
        
        logger.info(f"Session {session_id} completed successfully")
    
    async def _get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get complete session data including messages and steps."""
        try:
            with get_db_session() as db:
                # Get session
                session_query = text("""
                    SELECT id, user_id, machine_id, status, problem_description,
                           language, session_metadata, created_at
                    FROM ai_sessions
                    WHERE id = :session_id
                """)
                session = db.execute(session_query, {'session_id': session_id}).fetchone()
                
                if not session:
                    return None
                
                # Get messages
                messages_query = text("""
                    SELECT sender, content, message_type, timestamp
                    FROM ai_messages
                    WHERE session_id = :session_id
                    ORDER BY timestamp ASC
                """)
                messages = db.execute(messages_query, {'session_id': session_id}).fetchall()
                
                # Get steps
                steps_query = text("""
                    SELECT step_number, instruction, user_feedback, completed, success
                    FROM troubleshooting_steps
                    WHERE session_id = :session_id
                    ORDER BY step_number ASC
                """)
                steps = db.execute(steps_query, {'session_id': session_id}).fetchall()
                
                return {
                    'session_id': str(session.id),
                    'user_id': str(session.user_id),
                    'machine_id': str(session.machine_id) if session.machine_id else None,
                    'problem_description': session.problem_description,
                    'language': session.language,
                    'metadata': session.session_metadata if isinstance(session.session_metadata, dict) else {},
                    'created_at': session.created_at,
                    'messages': [dict(m._mapping) for m in messages],
                    'steps': [dict(s._mapping) for s in steps],
                    'step_count': len(steps)
                }
        except Exception as e:
            logger.error(f"Failed to get session data: {e}")
            return None
    
    def _calculate_resolution_time(self, session_data: Dict[str, Any]) -> int:
        """Calculate resolution time in minutes."""
        if not session_data.get('messages'):
            return 0
        
        first_msg = session_data['messages'][0]
        last_msg = session_data['messages'][-1]
        
        time_diff = last_msg['timestamp'] - first_msg['timestamp']
        return int(time_diff.total_seconds() / 60)
    
    async def _extract_learnings(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key learnings from session using LLM."""
        
        # Build conversation summary
        conversation = "\n".join([
            f"{msg['sender']}: {msg['content']}"
            for msg in session_data['messages']
        ])
        
        system_prompt = """You are analyzing a troubleshooting session to extract key learnings.
Focus on:
1. Machine-specific facts mentioned by the user (e.g., "AutoBoss uses diesel engine, not power cord")
2. Successful troubleshooting approaches
3. Failed approaches that should be avoided
4. Important clarifications about the machine

Return a JSON object with:
{
    "machine_facts": [{"type": "power_source|component|procedure|specification", "key": "brief_key", "value": "fact_value"}],
    "successful_approaches": ["approach 1", "approach 2"],
    "failed_approaches": ["approach 1", "approach 2"],
    "key_insights": ["insight 1", "insight 2"]
}"""
        
        user_prompt = f"""Analyze this troubleshooting session and extract learnings:

Machine: {session_data.get('machine_id', 'Unknown')}
Problem: {session_data.get('problem_description', 'Unknown')}

Conversation:
{conversation}

Extract key learnings in JSON format."""
        
        try:
            messages = [
                ConversationMessage(role="system", content=system_prompt),
                ConversationMessage(role="user", content=user_prompt)
            ]
            
            response = await self.llm_client.generate_response(messages, language="en")
            
            if response.success:
                # Parse JSON from response
                content = response.content.strip()
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_content = content[start_idx:end_idx]
                    return json.loads(json_content)
            
            return {}
        except Exception as e:
            logger.error(f"Failed to extract learnings: {e}")
            return {}
    
    async def _store_session_outcome(
        self,
        session_id: str,
        outcome_type: str,
        resolution_time_minutes: int,
        steps_taken: int,
        key_learnings: Dict[str, Any]
    ) -> None:
        """Store session outcome in database."""
        try:
            with get_db_session() as db:
                query = text("""
                    INSERT INTO session_outcomes 
                    (id, session_id, outcome_type, resolution_time_minutes, steps_taken, key_learnings)
                    VALUES (:id, :session_id, :outcome_type, :resolution_time, :steps_taken, :learnings)
                """)
                db.execute(query, {
                    'id': str(uuid.uuid4()),
                    'session_id': session_id,
                    'outcome_type': outcome_type,
                    'resolution_time': resolution_time_minutes,
                    'steps_taken': steps_taken,
                    'learnings': json.dumps(key_learnings) if key_learnings else '{}'
                })
        except Exception as e:
            logger.error(f"Failed to store session outcome: {e}")
    
    async def _update_session_status(
        self,
        session_id: str,
        outcome_type: str,
        resolution_summary: Optional[str]
    ) -> None:
        """Update session status to completed/escalated/abandoned."""
        try:
            with get_db_session() as db:
                query = text("""
                    UPDATE ai_sessions
                    SET status = :status, resolution_summary = :summary, updated_at = NOW()
                    WHERE id = :session_id
                """)
                db.execute(query, {
                    'session_id': session_id,
                    'status': outcome_type,
                    'summary': resolution_summary
                })
        except Exception as e:
            logger.error(f"Failed to update session status: {e}")
    
    async def _process_learnings(
        self,
        session_data: Dict[str, Any],
        key_learnings: Dict[str, Any]
    ) -> None:
        """Process and store extracted learnings."""
        
        # Extract machine model from machine_id
        machine_model = await self._get_machine_model(session_data.get('machine_id'))
        
        # Store machine facts
        if key_learnings.get('machine_facts'):
            for fact in key_learnings['machine_facts']:
                await self._store_or_update_machine_fact(
                    machine_model=machine_model,
                    fact_type=fact.get('type', 'general'),
                    fact_key=fact.get('key', ''),
                    fact_value=fact.get('value', ''),
                    session_id=session_data['session_id']
                )
        
        logger.info(f"Processed {len(key_learnings.get('machine_facts', []))} machine facts")
    
    async def _get_machine_model(self, machine_id: Optional[str]) -> str:
        """Get machine model from machine_id."""
        if not machine_id:
            return "unknown"
        
        try:
            with get_db_session() as db:
                query = text("""
                    SELECT model_type FROM machines WHERE id = :machine_id
                """)
                result = db.execute(query, {'machine_id': machine_id}).fetchone()
                return result[0] if result else "unknown"
        except:
            return "unknown"
    
    async def _store_or_update_machine_fact(
        self,
        machine_model: str,
        fact_type: str,
        fact_key: str,
        fact_value: str,
        session_id: str
    ) -> None:
        """Store or update a machine fact."""
        try:
            with get_db_session() as db:
                # Check if fact exists
                check_query = text("""
                    SELECT id, times_confirmed, source_sessions
                    FROM machine_facts
                    WHERE machine_model = :model AND fact_type = :type AND fact_key = :key
                """)
                existing = db.execute(check_query, {
                    'model': machine_model,
                    'type': fact_type,
                    'key': fact_key
                }).fetchone()
                
                if existing:
                    # Update existing fact
                    update_query = text("""
                        UPDATE machine_facts
                        SET times_confirmed = times_confirmed + 1,
                            source_sessions = array_append(source_sessions, :session_id::UUID),
                            updated_at = NOW()
                        WHERE id = :id
                    """)
                    db.execute(update_query, {
                        'id': existing.id,
                        'session_id': session_id
                    })
                else:
                    # Insert new fact
                    insert_query = text("""
                        INSERT INTO machine_facts
                        (id, machine_model, fact_type, fact_key, fact_value, source_sessions)
                        VALUES (:id, :model, :type, :key, :value, ARRAY[:session_id]::UUID[])
                    """)
                    db.execute(insert_query, {
                        'id': str(uuid.uuid4()),
                        'model': machine_model,
                        'type': fact_type,
                        'key': fact_key,
                        'value': fact_value,
                        'session_id': session_id
                    })
        except Exception as e:
            logger.error(f"Failed to store machine fact: {e}")
