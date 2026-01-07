"""
Property-based tests for conversation persistence.

**Feature: autoboss-ai-assistant, Property 7: Conversation Persistence**
**Validates: Requirements 7.1, 7.2, 7.3, 7.5**

Tests that conversation history and context are preserved across interruptions,
browser sessions, and interface state changes.
"""

import pytest
import asyncio
import uuid
from datetime import datetime
from typing import List, Dict, Any
from hypothesis import given, strategies as st, settings
from hypothesis.strategies import composite

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.session_manager import SessionManager
from app.models import MessageSender, MessageType
from app.database import get_db_session
from sqlalchemy import text


# Test data generators
@composite
def session_data(draw):
    """Generate valid session data using actual database data."""
    # Get actual machine IDs from database
    with get_db_session() as db:
        result = db.execute(text("SELECT id FROM machines LIMIT 10")).fetchall()
        machine_ids = [str(row.id) for row in result] if result else []
    
    return {
        'user_id': "f6abc555-5b6c-6f7a-8b9c-0d123456789a",  # Use existing superadmin user
        'machine_id': draw(st.sampled_from(machine_ids)) if machine_ids and draw(st.booleans()) else None,
        'language': draw(st.sampled_from(['en', 'el', 'ar', 'es', 'tr', 'no'])),
        'problem_description': draw(st.text(min_size=10, max_size=200))
    }


@composite
def message_data(draw):
    """Generate valid message data."""
    return {
        'sender': draw(st.sampled_from(['user', 'assistant', 'system'])),
        'content': draw(st.text(min_size=1, max_size=500)),
        'message_type': draw(st.sampled_from(['text', 'voice', 'diagnostic_step'])),
        'language': draw(st.sampled_from(['en', 'el', 'ar', 'es', 'tr', 'no'])),
        'metadata': draw(st.dictionaries(st.text(min_size=1, max_size=20), st.text(max_size=100), max_size=3))
    }


@composite
def conversation_sequence(draw):
    """Generate a sequence of messages for a conversation."""
    num_messages = draw(st.integers(min_value=1, max_value=5))  # Reduced for faster testing
    messages = []
    for _ in range(num_messages):
        messages.append(draw(message_data()))
    return messages


async def cleanup_sessions(session_ids: List[str]):
    """Cleanup test sessions from database."""
    with get_db_session() as db:
        for session_id in session_ids:
            try:
                # Delete messages first (due to foreign key constraint)
                db.execute(text("DELETE FROM ai_messages WHERE session_id = :session_id"), 
                         {'session_id': session_id})
                # Delete session
                db.execute(text("DELETE FROM ai_sessions WHERE session_id = :session_id"), 
                         {'session_id': session_id})
            except Exception as e:
                print(f"Cleanup error for session {session_id}: {e}")


async def test_session_creation_and_retrieval_persistence_impl(session_data):
    """
    Property: For any valid session data, creating a session and then retrieving it
    should return the same session information.
    
    **Feature: autoboss-ai-assistant, Property 7: Conversation Persistence**
    **Validates: Requirements 7.1, 7.2**
    """
    session_manager = SessionManager()
    await session_manager.initialize()
    created_sessions = []
    
    try:
        # Create session
        session_id = await session_manager.create_session(
            user_id=session_data['user_id'],
            machine_id=session_data['machine_id'],
            language=session_data['language'],
            problem_description=session_data['problem_description']
        )
        
        created_sessions.append(session_id)
        
        # Retrieve session
        retrieved_session = await session_manager.get_session(session_id)
        
        # Verify persistence
        assert retrieved_session is not None
        assert retrieved_session['session_id'] == session_id
        assert retrieved_session['user_id'] == session_data['user_id']
        assert retrieved_session['machine_id'] == session_data['machine_id']
        assert retrieved_session['language'] == session_data['language']
        assert retrieved_session['problem_description'] == session_data['problem_description']
        assert retrieved_session['status'] == 'active'
        
    finally:
        await session_manager.cleanup()
        await cleanup_sessions(created_sessions)


async def test_conversation_history_persistence_impl(session_data, messages):
    """
    Property: For any session with a sequence of messages, the conversation history
    should be preserved and retrievable in the correct order.
    
    **Feature: autoboss-ai-assistant, Property 7: Conversation Persistence**
    **Validates: Requirements 7.1, 7.2, 7.3**
    """
    session_manager = SessionManager()
    await session_manager.initialize()
    created_sessions = []
    
    try:
        # Create session
        session_id = await session_manager.create_session(
            user_id=session_data['user_id'],
            machine_id=session_data['machine_id'],
            language=session_data['language'],
            problem_description=session_data['problem_description']
        )
        
        created_sessions.append(session_id)
        
        # Add messages to session
        message_ids = []
        for msg_data in messages:
            message_id = await session_manager.add_message(
                session_id=session_id,
                sender=msg_data['sender'],
                content=msg_data['content'],
                message_type=msg_data['message_type'],
                language=msg_data['language'],
                metadata=msg_data['metadata']
            )
            message_ids.append(message_id)
        
        # Retrieve conversation history
        history = await session_manager.get_session_history(session_id)
        
        # Verify persistence and order
        assert len(history) == len(messages)
        
        for i, (original_msg, retrieved_msg) in enumerate(zip(messages, history)):
            assert retrieved_msg.message_id == message_ids[i]
            assert retrieved_msg.session_id == session_id
            assert retrieved_msg.sender.value == original_msg['sender']
            assert retrieved_msg.content == original_msg['content']
            assert retrieved_msg.message_type.value == original_msg['message_type']
            assert retrieved_msg.language == original_msg['language']
            assert retrieved_msg.metadata == original_msg['metadata']
            
    finally:
        await session_manager.cleanup()
        await cleanup_sessions(created_sessions)


async def test_session_interruption_and_resume_impl(session_data, messages):
    """
    Property: For any session with messages, interrupting the session manager
    (simulating connection loss) and then resuming should preserve all data.
    
    **Feature: autoboss-ai-assistant, Property 7: Conversation Persistence**
    **Validates: Requirements 7.3, 7.5**
    """
    session_manager = SessionManager()
    await session_manager.initialize()
    created_sessions = []
    
    try:
        # Create session and add messages
        session_id = await session_manager.create_session(
            user_id=session_data['user_id'],
            machine_id=session_data['machine_id'],
            language=session_data['language'],
            problem_description=session_data['problem_description']
        )
        
        created_sessions.append(session_id)
        
        # Add half the messages
        mid_point = len(messages) // 2
        first_half = messages[:mid_point]
        second_half = messages[mid_point:]
        
        for msg_data in first_half:
            await session_manager.add_message(
                session_id=session_id,
                sender=msg_data['sender'],
                content=msg_data['content'],
                message_type=msg_data['message_type'],
                language=msg_data['language'],
                metadata=msg_data['metadata']
            )
        
        # Simulate interruption by creating a new session manager
        await session_manager.cleanup()
        new_session_manager = SessionManager()
        await new_session_manager.initialize()
        
        # Verify session still exists
        retrieved_session = await new_session_manager.get_session(session_id)
        assert retrieved_session is not None
        assert retrieved_session['session_id'] == session_id
        
        # Add remaining messages with new session manager
        for msg_data in second_half:
            await new_session_manager.add_message(
                session_id=session_id,
                sender=msg_data['sender'],
                content=msg_data['content'],
                message_type=msg_data['message_type'],
                language=msg_data['language'],
                metadata=msg_data['metadata']
            )
        
        # Verify complete conversation history is preserved
        history = await new_session_manager.get_session_history(session_id)
        assert len(history) == len(messages)
        
        # Verify message order and content
        for i, (original_msg, retrieved_msg) in enumerate(zip(messages, history)):
            assert retrieved_msg.sender.value == original_msg['sender']
            assert retrieved_msg.content == original_msg['content']
            assert retrieved_msg.message_type.value == original_msg['message_type']
            assert retrieved_msg.language == original_msg['language']
        
        await new_session_manager.cleanup()
        
    finally:
        await cleanup_sessions(created_sessions)


# Property-based test functions
@given(session_data())
@settings(max_examples=5, deadline=10000)
def test_session_persistence_property(session_data):
    """
    Property test for session persistence.
    
    **Feature: autoboss-ai-assistant, Property 7: Conversation Persistence**
    **Validates: Requirements 7.1, 7.2**
    """
    asyncio.run(test_session_creation_and_retrieval_persistence_impl(session_data))


@given(session_data(), conversation_sequence())
@settings(max_examples=3, deadline=15000)
def test_conversation_history_property(session_data, messages):
    """
    Property test for conversation history persistence.
    
    **Feature: autoboss-ai-assistant, Property 7: Conversation Persistence**
    **Validates: Requirements 7.1, 7.2, 7.3**
    """
    asyncio.run(test_conversation_history_persistence_impl(session_data, messages))


@given(session_data(), conversation_sequence())
@settings(max_examples=2, deadline=20000)
def test_session_interruption_property(session_data, messages):
    """
    Property test for session interruption and resume.
    
    **Feature: autoboss-ai-assistant, Property 7: Conversation Persistence**
    **Validates: Requirements 7.3, 7.5**
    """
    asyncio.run(test_session_interruption_and_resume_impl(session_data, messages))


# Simple unit test for basic functionality
def test_basic_session_persistence():
    """
    Basic test for session persistence functionality.
    
    **Feature: autoboss-ai-assistant, Property 7: Conversation Persistence**
    **Validates: Requirements 7.1, 7.2**
    """
    async def run_test():
        session_manager = SessionManager()
        await session_manager.initialize()
        created_sessions = []
        
        try:
            # Create a simple session
            session_id = await session_manager.create_session(
                user_id="f6abc555-5b6c-6f7a-8b9c-0d123456789a",
                machine_id=None,
                language="en",
                problem_description="Test problem description"
            )
            
            created_sessions.append(session_id)
            
            # Add a message
            message_id = await session_manager.add_message(
                session_id=session_id,
                sender="user",
                content="Test message content",
                message_type="text",
                language="en"
            )
            
            # Retrieve session and verify
            retrieved_session = await session_manager.get_session(session_id)
            assert retrieved_session is not None
            assert retrieved_session['session_id'] == session_id
            assert retrieved_session['status'] == 'active'
            
            # Retrieve history and verify
            history = await session_manager.get_session_history(session_id)
            assert len(history) == 1
            assert history[0].content == "Test message content"
            assert history[0].sender.value == "user"
            
        finally:
            await session_manager.cleanup()
            await cleanup_sessions(created_sessions)
    
    asyncio.run(run_test())


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])