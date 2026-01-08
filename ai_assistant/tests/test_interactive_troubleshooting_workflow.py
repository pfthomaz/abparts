"""
Property-based tests for interactive troubleshooting workflow.

**Feature: autoboss-ai-assistant, Property 3: Interactive Troubleshooting Workflow**
**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

Property 3: Interactive Troubleshooting Workflow
For any troubleshooting session, the system should provide diagnostic assessment, 
present actionable steps, request feedback, and adapt subsequent guidance based on user responses.
"""

import pytest
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, List
from unittest.mock import AsyncMock, MagicMock, patch

from hypothesis import given, strategies as st, settings, assume, HealthCheck
from hypothesis.strategies import composite

from app.services.troubleshooting_service import TroubleshootingService
from app.services.troubleshooting_types import (
    DiagnosticAssessment, TroubleshootingStepData, ConfidenceLevel, StepStatus
)
from app.services.problem_analyzer import ProblemAnalyzer, ProblemType
from app.llm_client import LLMClient, LLMResponse
from app.session_manager import SessionManager


def run_async(coro):
    """Helper function to run async functions in sync context."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# Test data generators
@composite
def problem_descriptions(draw):
    """Generate realistic problem descriptions for testing."""
    problem_types = [
        "machine won't start",
        "poor cleaning performance", 
        "strange noise from wheels",
        "remote control not responding",
        "hydraulic pressure low",
        "electrical fault detected",
        "maintenance overdue"
    ]
    
    base_problem = draw(st.sampled_from(problem_types))
    
    # Add optional details
    details = draw(st.lists(
        st.sampled_from([
            "after 2 hours of operation",
            "when starting up",
            "intermittent issue",
            "happens every time",
            "started yesterday",
            "getting worse",
            "only in deep water"
        ]),
        min_size=0,
        max_size=2
    ))
    
    if details:
        return f"{base_problem} {' '.join(details)}"
    return base_problem


@composite
def machine_contexts(draw):
    """Generate machine context data for testing."""
    return {
        "model": draw(st.sampled_from(["AutoBoss V4.0", "AutoBoss V3.1B", "AutoBoss V2.5"])),
        "serial_number": draw(st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", min_size=8, max_size=12)),
        "operating_hours": draw(st.integers(min_value=0, max_value=10000)),
        "last_maintenance": draw(st.sampled_from(["2024-01-15", "2023-12-20", "2024-02-10", "Unknown"])),
        "installation_date": draw(st.sampled_from(["2023-06-15", "2022-11-30", "2024-01-05"]))
    }


@composite
def user_feedback_responses(draw):
    """Generate realistic user feedback responses."""
    positive_responses = [
        "problem fixed", "working now", "that solved it", "much better",
        "resolved", "good", "working perfectly", "issue gone"
    ]
    
    negative_responses = [
        "still not working", "problem persists", "no change", "worse now",
        "didn't help", "same issue", "still broken", "not fixed"
    ]
    
    neutral_responses = [
        "partially better", "some improvement", "not sure", "maybe better",
        "hard to tell", "slight improvement", "need more time"
    ]
    
    response_type = draw(st.sampled_from(["positive", "negative", "neutral"]))
    
    if response_type == "positive":
        return draw(st.sampled_from(positive_responses))
    elif response_type == "negative":
        return draw(st.sampled_from(negative_responses))
    else:
        return draw(st.sampled_from(neutral_responses))


@composite
def languages(draw):
    """Generate supported language codes."""
    return draw(st.sampled_from(["en", "el", "ar", "es", "tr", "no"]))


class TestInteractiveTroubleshootingWorkflow:
    """Property-based tests for interactive troubleshooting workflow."""
    
    @pytest.fixture
    def mock_llm_client(self):
        """Create mock LLM client for testing."""
        mock_client = AsyncMock(spec=LLMClient)
        
        # Mock successful LLM responses
        mock_client.generate_response.return_value = LLMResponse(
            content='{"problem_category": "startup", "likely_causes": ["power issue"], "confidence_level": "medium", "recommended_steps": ["check power"], "safety_warnings": ["turn off power"], "estimated_duration": 30, "requires_expert": false}',
            model_used="gpt-4",
            tokens_used=150,
            response_time=1.2,
            success=True
        )
        
        return mock_client
    
    @pytest.fixture
    def mock_session_manager(self):
        """Create mock session manager for testing."""
        mock_manager = AsyncMock(spec=SessionManager)
        
        # Mock session creation
        mock_manager.create_session.return_value = str(uuid.uuid4())
        
        # Mock session data
        mock_manager.get_session.return_value = {
            "session_id": str(uuid.uuid4()),
            "user_id": "test_user",
            "machine_id": "test_machine",
            "status": "active",
            "language": "en",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "metadata": {}
        }
        
        return mock_manager
    
    @pytest.fixture
    def troubleshooting_service(self, mock_llm_client, mock_session_manager):
        """Create troubleshooting service with mocked dependencies."""
        with patch('app.services.troubleshooting_service.get_db_session'):
            service = TroubleshootingService(mock_llm_client, mock_session_manager)
            return service
    
    @given(
        problem_description=problem_descriptions(),
        machine_context=st.one_of(st.none(), machine_contexts()),
        language=languages()
    )
    @settings(max_examples=50, deadline=10000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_diagnostic_assessment_generation(
        self, 
        troubleshooting_service,
        problem_description: str,
        machine_context: Dict[str, Any],
        language: str
    ):
        """
        Property: For any problem description, the system should generate a diagnostic assessment.
        
        This test verifies that the troubleshooting service can analyze any problem description
        and produce a structured diagnostic assessment with all required fields.
        """
        assume(len(problem_description.strip()) > 0)
        
        async def run_test():
            # Mock database operations
            with patch('app.services.troubleshooting_service.get_db_session') as mock_db:
                mock_db.return_value.__enter__.return_value.execute.return_value = None
                
                # Start troubleshooting workflow
                session_id = str(uuid.uuid4())
                assessment = await troubleshooting_service.start_troubleshooting_workflow(
                    session_id=session_id,
                    problem_description=problem_description,
                    machine_context=machine_context,
                    language=language
                )
                
                # Verify diagnostic assessment properties
                assert isinstance(assessment, DiagnosticAssessment)
                assert assessment.problem_category is not None
                assert len(assessment.problem_category) > 0
                assert isinstance(assessment.likely_causes, list)
                assert len(assessment.likely_causes) > 0
                assert isinstance(assessment.confidence_level, ConfidenceLevel)
                assert isinstance(assessment.recommended_steps, list)
                assert len(assessment.recommended_steps) > 0
                assert isinstance(assessment.safety_warnings, list)
                assert isinstance(assessment.estimated_duration, int)
                assert assessment.estimated_duration > 0
                assert isinstance(assessment.requires_expert, bool)
        
        run_async(run_test())
    
    @given(
        problem_description=problem_descriptions(),
        language=languages()
    )
    @settings(max_examples=30, deadline=10000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_actionable_steps_generation(
        self,
        troubleshooting_service,
        problem_description: str,
        language: str
    ):
        """
        Property: For any diagnostic assessment, the system should generate actionable troubleshooting steps.
        
        This test verifies that troubleshooting steps are specific, actionable, and properly structured.
        """
        assume(len(problem_description.strip()) > 0)
        
        with patch('app.services.troubleshooting_service.get_db_session') as mock_db:
            mock_db.return_value.__enter__.return_value.execute.return_value = None
            
            session_id = str(uuid.uuid4())
            assessment = await troubleshooting_service.start_troubleshooting_workflow(
                session_id=session_id,
                problem_description=problem_description,
                language=language
            )
            
            # Verify that recommended steps are actionable
            for step in assessment.recommended_steps:
                assert isinstance(step, str)
                assert len(step.strip()) > 0
                # Steps should contain action verbs or instructions
                action_indicators = [
                    "check", "verify", "inspect", "test", "examine", "ensure",
                    "turn", "press", "connect", "disconnect", "replace", "clean",
                    "ελέγξτε", "επαληθεύστε", "εξετάστε",  # Greek
                    "تحقق", "افحص", "تأكد",  # Arabic
                    "verificar", "inspeccionar", "comprobar",  # Spanish
                    "kontrol", "doğrula", "incele",  # Turkish
                    "sjekk", "kontroller", "inspiser"  # Norwegian
                ]
                
                step_lower = step.lower()
                has_action = any(indicator in step_lower for indicator in action_indicators)
                
                # Either contains action words or is a clear instruction
                assert has_action or len(step) > 10, f"Step '{step}' should be more actionable"
    
    @given(
        user_feedback=user_feedback_responses(),
        language=languages()
    )
    @settings(max_examples=30, deadline=10000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_feedback_processing_and_adaptation(
        self,
        troubleshooting_service,
        user_feedback: str,
        language: str
    ):
        """
        Property: For any user feedback, the system should process it and adapt subsequent guidance.
        
        This test verifies that the system can process user feedback and generate appropriate
        next steps or workflow state changes.
        """
        with patch('app.services.troubleshooting_service.get_db_session') as mock_db:
            # Mock database queries for step retrieval
            mock_result = MagicMock()
            mock_result.session_id = str(uuid.uuid4())
            mock_result.step_number = 1
            mock_result.instruction = "Test step"
            mock_result.expected_outcomes = '["outcome1", "outcome2"]'
            mock_result.user_feedback = None
            mock_result.completed = False
            mock_result.success = None
            mock_result.created_at = datetime.utcnow()
            mock_result.completed_at = None
            
            mock_db.return_value.__enter__.return_value.execute.return_value.fetchone.return_value = mock_result
            mock_db.return_value.__enter__.return_value.execute.return_value.rowcount = 1
            
            # Process user feedback
            session_id = str(uuid.uuid4())
            step_id = str(uuid.uuid4())
            
            result = await troubleshooting_service.process_user_feedback(
                session_id=session_id,
                step_id=step_id,
                user_feedback=user_feedback,
                language=language
            )
            
            # Verify feedback processing results
            # The system should either:
            # 1. Generate a next step (TroubleshootingStepData)
            # 2. Complete the workflow (None returned)
            # 3. Escalate the issue (None returned with session status change)
            
            if result is not None:
                # Next step generated
                assert isinstance(result, TroubleshootingStepData)
                assert result.step_id is not None
                assert result.step_number > 0
                assert len(result.instruction) > 0
                assert isinstance(result.expected_outcomes, list)
                assert result.status == StepStatus.pending
                assert result.requires_feedback is True
            
            # Verify that feedback was processed (database update should be called)
            mock_db.return_value.__enter__.return_value.execute.assert_called()
    
    @given(
        problem_description=problem_descriptions(),
        feedback_sequence=st.lists(user_feedback_responses(), min_size=1, max_size=5),
        language=languages()
    )
    @settings(max_examples=20, deadline=15000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_complete_workflow_progression(
        self,
        troubleshooting_service,
        problem_description: str,
        feedback_sequence: List[str],
        language: str
    ):
        """
        Property: For any troubleshooting session, the workflow should progress logically through steps.
        
        This test verifies that a complete troubleshooting workflow maintains consistency
        and progresses logically from initial assessment through user feedback cycles.
        """
        assume(len(problem_description.strip()) > 0)
        assume(len(feedback_sequence) > 0)
        
        with patch('app.services.troubleshooting_service.get_db_session') as mock_db:
            mock_db.return_value.__enter__.return_value.execute.return_value = None
            
            # Start workflow
            session_id = str(uuid.uuid4())
            initial_assessment = await troubleshooting_service.start_troubleshooting_workflow(
                session_id=session_id,
                problem_description=problem_description,
                language=language
            )
            
            # Verify initial state
            assert isinstance(initial_assessment, DiagnosticAssessment)
            
            # Simulate workflow progression through feedback
            current_step_number = 1
            
            for i, feedback in enumerate(feedback_sequence):
                # Mock step retrieval for feedback processing
                mock_result = MagicMock()
                mock_result.session_id = session_id
                mock_result.step_number = current_step_number
                mock_result.instruction = f"Step {current_step_number} instruction"
                mock_result.expected_outcomes = '["outcome1", "outcome2"]'
                mock_result.user_feedback = None
                mock_result.completed = False
                mock_result.success = None
                mock_result.created_at = datetime.utcnow()
                mock_result.completed_at = None
                
                mock_db.return_value.__enter__.return_value.execute.return_value.fetchone.return_value = mock_result
                mock_db.return_value.__enter__.return_value.execute.return_value.rowcount = 1
                
                # Process feedback
                step_id = str(uuid.uuid4())
                next_step = await troubleshooting_service.process_user_feedback(
                    session_id=session_id,
                    step_id=step_id,
                    user_feedback=feedback,
                    language=language
                )
                
                if next_step is not None:
                    # Verify step progression
                    assert isinstance(next_step, TroubleshootingStepData)
                    assert next_step.step_number > current_step_number
                    current_step_number = next_step.step_number
                    
                    # Verify step consistency
                    assert len(next_step.instruction) > 0
                    assert isinstance(next_step.expected_outcomes, list)
                    assert next_step.status == StepStatus.pending
                else:
                    # Workflow completed or escalated - this is valid
                    break
    
    @given(
        confidence_level=st.sampled_from([ConfidenceLevel.high, ConfidenceLevel.medium, ConfidenceLevel.low, ConfidenceLevel.very_low]),
        language=languages()
    )
    @settings(max_examples=20, deadline=5000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_confidence_based_workflow_adaptation(
        self,
        troubleshooting_service,
        confidence_level: ConfidenceLevel,
        language: str
    ):
        """
        Property: For any confidence level, the system should adapt its workflow appropriately.
        
        This test verifies that the system adjusts its behavior based on diagnostic confidence,
        with lower confidence leading to more conservative approaches or expert escalation.
        """
        # Create a mock assessment with specific confidence level
        mock_assessment = DiagnosticAssessment(
            problem_category="test_category",
            likely_causes=["test cause"],
            confidence_level=confidence_level,
            recommended_steps=["test step"],
            safety_warnings=["test warning"],
            estimated_duration=30,
            requires_expert=(confidence_level == ConfidenceLevel.very_low)
        )
        
        # Mock the problem analyzer to return our controlled assessment
        with patch.object(troubleshooting_service.problem_analyzer, 'analyze_problem_with_confidence') as mock_analyze:
            mock_analyze.return_value = (mock_assessment, 0.9 if confidence_level == ConfidenceLevel.high else 0.3)
            
            with patch('app.services.troubleshooting_service.get_db_session') as mock_db:
                mock_db.return_value.__enter__.return_value.execute.return_value = None
                
                session_id = str(uuid.uuid4())
                result_assessment = await troubleshooting_service.start_troubleshooting_workflow(
                    session_id=session_id,
                    problem_description="test problem",
                    language=language
                )
                
                # Verify confidence-based adaptations
                assert result_assessment.confidence_level == confidence_level
                
                if confidence_level == ConfidenceLevel.very_low:
                    # Very low confidence should require expert
                    assert result_assessment.requires_expert is True
                elif confidence_level == ConfidenceLevel.high:
                    # High confidence should provide specific guidance
                    assert len(result_assessment.recommended_steps) > 0
                    assert len(result_assessment.likely_causes) > 0
    
    @given(
        problem_description=problem_descriptions(),
        language=languages()
    )
    @settings(max_examples=20, deadline=10000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_safety_warnings_inclusion(
        self,
        troubleshooting_service,
        problem_description: str,
        language: str
    ):
        """
        Property: For any troubleshooting workflow, safety warnings should be included when appropriate.
        
        This test verifies that the system consistently includes safety considerations
        in its troubleshooting guidance.
        """
        assume(len(problem_description.strip()) > 0)
        
        with patch('app.services.troubleshooting_service.get_db_session') as mock_db:
            mock_db.return_value.__enter__.return_value.execute.return_value = None
            
            session_id = str(uuid.uuid4())
            assessment = await troubleshooting_service.start_troubleshooting_workflow(
                session_id=session_id,
                problem_description=problem_description,
                language=language
            )
            
            # Verify safety warnings are present and meaningful
            assert isinstance(assessment.safety_warnings, list)
            
            # For electrical or hydraulic problems, safety warnings should be present
            if any(keyword in problem_description.lower() for keyword in ["electrical", "power", "hydraulic", "pressure"]):
                assert len(assessment.safety_warnings) > 0
                
                # Safety warnings should contain safety-related terms
                safety_terms = [
                    "power", "off", "safety", "caution", "warning", "danger", "risk",
                    "ασφάλεια", "προσοχή", "κίνδυνος",  # Greek
                    "أمان", "تحذير", "خطر",  # Arabic  
                    "seguridad", "precaución", "peligro",  # Spanish
                    "güvenlik", "dikkat", "tehlike",  # Turkish
                    "sikkerhet", "forsiktighet", "fare"  # Norwegian
                ]
                
                for warning in assessment.safety_warnings:
                    warning_lower = warning.lower()
                    has_safety_term = any(term in warning_lower for term in safety_terms)
                    assert has_safety_term or len(warning) > 15, f"Warning '{warning}' should be more safety-focused"


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])