"""
Property-based test for escalation data completeness.

**Feature: autoboss-ai-assistant, Property 6: Escalation Data Completeness**
**Validates: Requirements 6.2, 6.3, 6.5**

This test verifies that when escalation occurs, all necessary session data,
machine context, and troubleshooting history is compiled into the support ticket.
"""

import pytest
import json
import uuid
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings, assume
from typing import Dict, Any, List, Optional

from app.services.escalation_service import escalation_service
from app.services.troubleshooting_service import TroubleshootingService
from app.session_manager import session_manager
from app.llm_client import LLMClient
from app.schemas import EscalationReasonEnum, TicketPriorityEnum
from app.database import get_db_session
from sqlalchemy import text


# Test data generators
@st.composite
def generate_session_data(draw):
    """Generate realistic session data for testing."""
    session_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    machine_id = draw(st.one_of(st.none(), st.text(min_size=10, max_size=50)))
    
    # Generate diagnostic assessment
    problem_categories = ["startup", "cleaning_performance", "mechanical", "electrical", "hydraulic"]
    confidence_levels = ["high", "medium", "low", "very_low"]
    
    diagnostic_assessment = {
        "problem_category": draw(st.sampled_from(problem_categories)),
        "likely_causes": draw(st.lists(st.text(min_size=5, max_size=100), min_size=1, max_size=5)),
        "confidence_level": draw(st.sampled_from(confidence_levels)),
        "recommended_steps": draw(st.lists(st.text(min_size=10, max_size=200), min_size=1, max_size=5)),
        "safety_warnings": draw(st.lists(st.text(min_size=10, max_size=100), min_size=0, max_size=3)),
        "estimated_duration": draw(st.integers(min_value=5, max_value=180)),
        "requires_expert": draw(st.booleans())
    }
    
    # Generate messages
    num_messages = draw(st.integers(min_value=2, max_value=20))
    messages = []
    
    for i in range(num_messages):
        sender = draw(st.sampled_from(["user", "assistant", "system"]))
        content = draw(st.text(min_size=10, max_size=500))
        message_type = draw(st.sampled_from(["text", "voice", "diagnostic_step"]))
        
        messages.append({
            "message_id": str(uuid.uuid4()),
            "sender": sender,
            "content": content,
            "message_type": message_type,
            "timestamp": datetime.utcnow() - timedelta(minutes=i),
            "language": "en"
        })
    
    # Generate troubleshooting steps
    num_steps = draw(st.integers(min_value=0, max_value=10))
    troubleshooting_steps = []
    
    for i in range(num_steps):
        step = {
            "step_id": str(uuid.uuid4()),
            "step_number": i + 1,
            "instruction": draw(st.text(min_size=20, max_size=300)),
            "expected_outcomes": draw(st.lists(st.text(min_size=5, max_size=100), min_size=1, max_size=4)),
            "user_feedback": draw(st.one_of(st.none(), st.text(min_size=5, max_size=200))),
            "completed": draw(st.booleans()),
            "success": draw(st.booleans()) if draw(st.booleans()) else None,
            "created_at": datetime.utcnow() - timedelta(minutes=num_messages + i)
        }
        troubleshooting_steps.append(step)
    
    # Generate machine context (if machine_id exists)
    machine_context = None
    if machine_id:
        machine_context = {
            "machine_details": {
                "id": machine_id,
                "name": draw(st.text(min_size=5, max_size=50)),
                "model_type": draw(st.sampled_from(["V4.0", "V3.1B", "V3.0", "V2.0"])),
                "serial_number": draw(st.text(min_size=8, max_size=20)),
                "latest_hours": draw(st.floats(min_value=0, max_value=10000)),
                "customer_organization": {
                    "name": draw(st.text(min_size=5, max_size=100))
                }
            },
            "recent_maintenance": draw(st.lists(
                st.fixed_dictionaries({
                    "maintenance_date": st.just(datetime.utcnow().isoformat()),
                    "maintenance_type": st.sampled_from(["preventive", "corrective", "emergency"]),
                    "description": st.text(min_size=10, max_size=200)
                }),
                min_size=0, max_size=5
            )),
            "recent_parts_usage": draw(st.lists(
                st.fixed_dictionaries({
                    "part_name": st.text(min_size=5, max_size=50),
                    "quantity": st.floats(min_value=0.1, max_value=100),
                    "usage_date": st.just(datetime.utcnow().isoformat())
                }),
                min_size=0, max_size=10
            ))
        }
    
    return {
        "session_id": session_id,
        "user_id": user_id,
        "machine_id": machine_id,
        "diagnostic_assessment": diagnostic_assessment,
        "messages": messages,
        "troubleshooting_steps": troubleshooting_steps,
        "machine_context": machine_context,
        "language": "en",
        "status": "active"
    }


@st.composite
def generate_escalation_request(draw):
    """Generate escalation request data."""
    return {
        "escalation_reason": draw(st.sampled_from(list(EscalationReasonEnum))),
        "priority": draw(st.sampled_from(list(TicketPriorityEnum))),
        "additional_notes": draw(st.one_of(st.none(), st.text(min_size=10, max_size=500)))
    }


class TestEscalationDataCompleteness:
    """Test escalation data completeness property."""
    
    async def setup_method(self):
        """Set up test data before each test method."""
        self.created_sessions = []
        self.created_tickets = []
    
    async def teardown_method(self):
        """Clean up test data after each test method."""
        await self._cleanup_test_data()
    
    async def _cleanup_test_data(self):
        """Clean up test data from database."""
        try:
            with get_db_session() as db:
                # Clean up support tickets
                for ticket_id in self.created_tickets:
                    try:
                        db.execute(text("DELETE FROM support_tickets WHERE id = :id"), {"id": ticket_id})
                    except Exception as e:
                        print(f"Error cleaning support ticket {ticket_id}: {e}")
                
                # Clean up troubleshooting steps (if table exists)
                for session_id in self.created_sessions:
                    try:
                        db.execute(text("DELETE FROM troubleshooting_steps WHERE session_id = :session_id"), 
                                 {"session_id": session_id})
                    except Exception as e:
                        print(f"Error cleaning troubleshooting steps for {session_id}: {e}")
                
                # Clean up messages
                for session_id in self.created_sessions:
                    try:
                        db.execute(text("DELETE FROM ai_messages WHERE session_id = :session_id"), 
                                 {"session_id": session_id})
                    except Exception as e:
                        print(f"Error cleaning messages for {session_id}: {e}")
                
                # Clean up sessions
                for session_id in self.created_sessions:
                    try:
                        db.execute(text("DELETE FROM ai_sessions WHERE session_id = :session_id"), 
                                 {"session_id": session_id})
                    except Exception as e:
                        print(f"Error cleaning session {session_id}: {e}")
                
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    async def _create_test_session(self, session_data: Dict[str, Any]) -> str:
        """Create a test session with all associated data."""
        session_id = session_data["session_id"]
        self.created_sessions.append(session_id)
        
        try:
            with get_db_session() as db:
                # Create session
                session_metadata = {
                    "diagnostic_assessment": session_data["diagnostic_assessment"],
                    "machine_context": session_data["machine_context"]
                }
                
                db.execute(text("""
                    INSERT INTO ai_sessions 
                    (session_id, user_id, machine_id, status, language, session_metadata, created_at, updated_at)
                    VALUES (:session_id, :user_id, :machine_id, :status, :language, :metadata, :created_at, :updated_at)
                """), {
                    "session_id": session_id,
                    "user_id": session_data["user_id"],
                    "machine_id": session_data["machine_id"],
                    "status": session_data["status"],
                    "language": session_data["language"],
                    "metadata": json.dumps(session_metadata),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                })
                
                # Create messages
                for msg in session_data["messages"]:
                    db.execute(text("""
                        INSERT INTO ai_messages 
                        (message_id, session_id, sender, content, message_type, language, timestamp, message_metadata)
                        VALUES (:message_id, :session_id, :sender, :content, :message_type, :language, :timestamp, :metadata)
                    """), {
                        "message_id": msg["message_id"],
                        "session_id": session_id,
                        "sender": msg["sender"],
                        "content": msg["content"],
                        "message_type": msg["message_type"],
                        "language": msg["language"],
                        "timestamp": msg["timestamp"],
                        "metadata": json.dumps({})
                    })
                
                # Create troubleshooting steps (only if table exists)
                try:
                    for step in session_data["troubleshooting_steps"]:
                        db.execute(text("""
                            INSERT INTO troubleshooting_steps 
                            (step_id, session_id, step_number, instruction, expected_outcomes, 
                             user_feedback, completed, success, created_at)
                            VALUES (:step_id, :session_id, :step_number, :instruction, :expected_outcomes,
                                    :user_feedback, :completed, :success, :created_at)
                        """), {
                            "step_id": step["step_id"],
                            "session_id": session_id,
                            "step_number": step["step_number"],
                            "instruction": step["instruction"],
                            "expected_outcomes": json.dumps(step["expected_outcomes"]),
                            "user_feedback": step["user_feedback"],
                            "completed": step["completed"],
                            "success": step["success"],
                            "created_at": step["created_at"]
                        })
                except Exception as e:
                    # Troubleshooting steps table might not exist, skip
                    print(f"Skipping troubleshooting steps: {e}")
                
        except Exception as e:
            print(f"Error creating test session: {e}")
            raise
        
        return session_id
    
    def _validate_session_summary_completeness(self, session_summary: str, session_data: Dict[str, Any]) -> bool:
        """Validate that session summary contains all essential information."""
        required_elements = [
            session_data["session_id"],  # Session ID should be present
            "TROUBLESHOOTING SESSION SUMMARY",  # Header should be present
            "INITIAL DIAGNOSTIC ASSESSMENT"  # Diagnostic section should be present
        ]
        
        # Check for required elements
        for element in required_elements:
            if element not in session_summary:
                return False
        
        # Check diagnostic assessment information
        diagnostic = session_data["diagnostic_assessment"]
        diagnostic_elements = [
            diagnostic["problem_category"],
            diagnostic["confidence_level"]
        ]
        
        for element in diagnostic_elements:
            if element not in session_summary:
                return False
        
        # Check for troubleshooting steps if any exist
        if session_data["troubleshooting_steps"]:
            if "TROUBLESHOOTING STEPS ATTEMPTED" not in session_summary:
                return False
            
            # Check that at least some steps are mentioned
            step_count = 0
            for step in session_data["troubleshooting_steps"]:
                if f"Step {step['step_number']}" in session_summary:
                    step_count += 1
            
            if step_count == 0:
                return False
        
        # Check for conversation highlights if messages exist
        user_messages = [msg for msg in session_data["messages"] if msg["sender"] == "user"]
        if user_messages and "CONVERSATION HIGHLIGHTS" not in session_summary:
            return False
        
        return True
    
    def _validate_machine_context_completeness(self, machine_context: Optional[Dict[str, Any]], 
                                             expected_context: Optional[Dict[str, Any]]) -> bool:
        """Validate that machine context contains expected information."""
        if expected_context is None:
            return machine_context is None
        
        if machine_context is None:
            return False
        
        # Check machine details
        if "machine_details" not in machine_context:
            return False
        
        expected_details = expected_context["machine_details"]
        actual_details = machine_context["machine_details"]
        
        required_fields = ["id", "name", "model_type", "serial_number"]
        for field in required_fields:
            if field not in actual_details or actual_details[field] != expected_details[field]:
                return False
        
        # Check that maintenance and parts data are included
        if "maintenance_history" not in machine_context:
            return False
        
        if "parts_usage" not in machine_context:
            return False
        
        return True
    
    def _validate_expert_contact_completeness(self, expert_contact_info: Dict[str, Any], 
                                            escalation_reason: EscalationReasonEnum) -> bool:
        """Validate that expert contact information is complete and appropriate."""
        if "primary_contact" not in expert_contact_info:
            return False
        
        primary_contact = expert_contact_info["primary_contact"]
        required_contact_fields = ["name", "email", "phone", "hours", "specialization"]
        
        for field in required_contact_fields:
            if field not in primary_contact or not primary_contact[field]:
                return False
        
        # Check that alternative contacts are provided
        if "alternative_contacts" not in expert_contact_info:
            return False
        
        if len(expert_contact_info["alternative_contacts"]) < 1:
            return False
        
        # Check escalation-specific contact selection
        if escalation_reason == EscalationReasonEnum.safety_concern:
            if "Emergency" not in primary_contact["name"]:
                return False
        
        return True
    
    @given(
        session_data=generate_session_data(),
        escalation_request=generate_escalation_request()
    )
    @settings(max_examples=50, deadline=30000)  # 30 second timeout
    @pytest.mark.asyncio
    async def test_escalation_data_completeness_property(self, session_data, escalation_request):
        """
        Property: For any escalation request, the system should compile complete session data,
        machine details, attempted solutions, and user responses into the support ticket.
        
        **Feature: autoboss-ai-assistant, Property 6: Escalation Data Completeness**
        **Validates: Requirements 6.2, 6.3, 6.5**
        """
        await self.setup_method()
        
        try:
            # Arrange: Create test session with all data
            session_id = await self._create_test_session(session_data)
            
            # Act: Create support ticket through escalation
            ticket_data = await escalation_service.create_support_ticket(
                session_id=session_id,
                escalation_reason=escalation_request["escalation_reason"],
                priority=escalation_request["priority"],
                additional_notes=escalation_request["additional_notes"]
            )
            
            # Track created ticket for cleanup
            self.created_tickets.append(ticket_data["ticket_id"])
            
            # Assert: Validate completeness of compiled data
            
            # 1. Session summary should contain all essential troubleshooting information
            session_summary = ticket_data["session_summary"]
            assert self._validate_session_summary_completeness(session_summary, session_data), \
                f"Session summary missing essential information. Summary: {session_summary[:200]}..."
            
            # 2. Machine context should be complete if machine was selected
            machine_context = ticket_data.get("machine_context")
            assert self._validate_machine_context_completeness(machine_context, session_data["machine_context"]), \
                f"Machine context incomplete. Expected: {session_data['machine_context'] is not None}, Got: {machine_context is not None}"
            
            # 3. Expert contact information should be complete and appropriate
            expert_contact_info = ticket_data.get("expert_contact_info")
            assert expert_contact_info is not None, "Expert contact information missing"
            assert self._validate_expert_contact_completeness(expert_contact_info, escalation_request["escalation_reason"]), \
                f"Expert contact information incomplete: {expert_contact_info}"
            
            # 4. Ticket should have all required metadata
            required_ticket_fields = ["ticket_id", "ticket_number", "priority", "session_summary"]
            for field in required_ticket_fields:
                assert field in ticket_data and ticket_data[field], f"Missing required ticket field: {field}"
            
            # 5. Escalation reason should be preserved
            assert "escalation_reason" in ticket_data or escalation_request["escalation_reason"].value in session_summary, \
                "Escalation reason not preserved in ticket data"
            
            # 6. All user messages should be represented in the summary
            user_messages = [msg for msg in session_data["messages"] if msg["sender"] == "user"]
            if user_messages:
                # At least some user message content should appear in the summary
                user_content_found = False
                for msg in user_messages[-3:]:  # Check last 3 user messages
                    # Look for partial content (first 50 chars) in summary
                    content_snippet = msg["content"][:50]
                    if content_snippet in session_summary or any(word in session_summary for word in content_snippet.split()[:3]):
                        user_content_found = True
                        break
                
                assert user_content_found, "No user message content found in session summary"
            
            # 7. Troubleshooting steps should be documented
            if session_data["troubleshooting_steps"]:
                completed_steps = [step for step in session_data["troubleshooting_steps"] if step["completed"]]
                if completed_steps:
                    # At least one completed step should be mentioned
                    step_mentioned = False
                    for step in completed_steps:
                        if f"Step {step['step_number']}" in session_summary:
                            step_mentioned = True
                            break
                    
                    assert step_mentioned, "No completed troubleshooting steps mentioned in summary"
            
            # 8. Diagnostic assessment should be included
            diagnostic = session_data["diagnostic_assessment"]
            assert diagnostic["problem_category"] in session_summary, "Problem category missing from summary"
            assert diagnostic["confidence_level"] in session_summary, "Confidence level missing from summary"
        
        finally:
            await self.teardown_method()


# Additional focused tests for edge cases
class TestEscalationEdgeCases:
    """Test edge cases for escalation data completeness."""
    
    async def setup_method(self):
        """Set up test database."""
        self.created_sessions = []
        self.created_tickets = []
    
    async def teardown_method(self):
        """Clean up test data."""
        try:
            with get_db_session() as db:
                for ticket_id in self.created_tickets:
                    db.execute(text("DELETE FROM support_tickets WHERE id = :id"), {"id": ticket_id})
                for session_id in self.created_sessions:
                    db.execute(text("DELETE FROM troubleshooting_steps WHERE session_id = :session_id"), 
                             {"session_id": session_id})
                    db.execute(text("DELETE FROM ai_messages WHERE session_id = :session_id"), 
                             {"session_id": session_id})
                    db.execute(text("DELETE FROM ai_sessions WHERE session_id = :session_id"), 
                             {"session_id": session_id})
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    @pytest.mark.asyncio
    async def test_escalation_with_minimal_data(self):
        """Test escalation with minimal session data still produces complete ticket."""
        await self.setup_method()
        
        try:
            # Create minimal session
            session_id = str(uuid.uuid4())
            self.created_sessions.append(session_id)
            
            with get_db_session() as db:
                db.execute(text("""
                    INSERT INTO ai_sessions 
                    (session_id, user_id, status, language, created_at, updated_at)
                    VALUES (:session_id, :user_id, :status, :language, :created_at, :updated_at)
                """), {
                    "session_id": session_id,
                    "user_id": str(uuid.uuid4()),
                    "status": "active",
                    "language": "en",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                })
            
            # Create support ticket
            ticket_data = await escalation_service.create_support_ticket(
                session_id=session_id,
                escalation_reason=EscalationReasonEnum.user_request,
                priority=TicketPriorityEnum.medium
            )
            
            self.created_tickets.append(ticket_data["ticket_id"])
            
            # Verify ticket has required fields even with minimal data
            assert ticket_data["ticket_id"]
            assert ticket_data["ticket_number"]
            assert ticket_data["session_summary"]
            assert ticket_data.get("expert_contact_info") is not None
            
            # Summary should handle missing data gracefully
            assert "Session data not found" not in ticket_data["session_summary"]
            assert session_id in ticket_data["session_summary"]
        
        finally:
            await self.teardown_method()
    
    @pytest.mark.asyncio
    async def test_escalation_with_safety_concern_selects_emergency_contact(self):
        """Test that safety concerns are routed to emergency support."""
        await self.setup_method()
        
        try:
            session_id = str(uuid.uuid4())
            self.created_sessions.append(session_id)
            
            with get_db_session() as db:
                db.execute(text("""
                    INSERT INTO ai_sessions 
                    (session_id, user_id, status, language, created_at, updated_at)
                    VALUES (:session_id, :user_id, :status, :language, :created_at, :updated_at)
                """), {
                    "session_id": session_id,
                    "user_id": str(uuid.uuid4()),
                    "status": "active",
                    "language": "en",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                })
            
            # Create support ticket with safety concern
            ticket_data = await escalation_service.create_support_ticket(
                session_id=session_id,
                escalation_reason=EscalationReasonEnum.safety_concern,
                priority=TicketPriorityEnum.urgent
            )
            
            self.created_tickets.append(ticket_data["ticket_id"])
            
            # Verify emergency contact is selected
            expert_contact = ticket_data.get("expert_contact_info", {})
            primary_contact = expert_contact.get("primary_contact", {})
            
            assert "Emergency" in primary_contact.get("name", ""), \
                f"Safety concern should route to emergency contact, got: {primary_contact.get('name')}"
            assert "24/7" in primary_contact.get("hours", ""), \
                "Emergency contact should have 24/7 availability"
        
        finally:
            await self.teardown_method()