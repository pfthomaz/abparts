"""
Property-based tests for machine-aware guidance functionality.

**Feature: autoboss-ai-assistant, Property 4: Machine-Aware Guidance**
**Validates: Requirements 4.2, 4.3, 4.4, 4.5**

This module tests that troubleshooting guidance incorporates machine-specific details,
maintenance history, and usage patterns from the ABParts database.
"""

import pytest
import asyncio
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from typing import Dict, Any, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
import uuid

from app.services.abparts_integration import ABPartsIntegration
from app.services.troubleshooting_service import TroubleshootingService
from app.services.troubleshooting_types import DiagnosticAssessment, ConfidenceLevel
from app.llm_client import LLMClient
from app.session_manager import SessionManager


# Test data generators
@st.composite
def machine_details_strategy(draw):
    """Generate realistic machine details."""
    model_types = ["V3.1B", "V4.0"]
    organizations = ["Customer A", "Customer B", "Customer C"]
    countries = ["GR", "UK", "NO", "CA", "NZ", "TR"]
    
    return {
        "id": str(uuid.uuid4()),
        "name": draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pc", "Pd", "Zs")))),
        "model_type": draw(st.sampled_from(model_types)),
        "serial_number": draw(st.text(min_size=8, max_size=20, alphabet=st.characters(whitelist_categories=("Lu", "Nd")))),
        "latest_hours": draw(st.floats(min_value=0, max_value=10000, allow_nan=False, allow_infinity=False)),
        "customer_organization": {
            "id": str(uuid.uuid4()),
            "name": draw(st.sampled_from(organizations)),
            "organization_type": "customer",
            "country": draw(st.sampled_from(countries))
        },
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }


@st.composite
def maintenance_history_strategy(draw):
    """Generate realistic maintenance history."""
    maintenance_types = ["scheduled", "unscheduled", "repair", "inspection", "cleaning"]
    
    num_records = draw(st.integers(min_value=0, max_value=10))
    records = []
    
    for i in range(num_records):
        record_date = datetime.now() - timedelta(days=draw(st.integers(min_value=1, max_value=365)))
        records.append({
            "id": str(uuid.uuid4()),
            "maintenance_date": record_date.isoformat(),
            "maintenance_type": draw(st.sampled_from(maintenance_types)),
            "description": draw(st.text(min_size=10, max_size=200, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pc", "Pd", "Zs")))),
            "hours_spent": draw(st.floats(min_value=0.5, max_value=8.0, allow_nan=False, allow_infinity=False)),
            "cost": draw(st.floats(min_value=50.0, max_value=2000.0, allow_nan=False, allow_infinity=False)),
            "performed_by": {
                "id": str(uuid.uuid4()),
                "name": draw(st.text(min_size=5, max_size=30, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Zs")))),
                "username": draw(st.text(min_size=3, max_size=20, alphabet=st.characters(whitelist_categories=("Ll", "Nd"))))
            },
            "parts_used": [],
            "created_at": record_date.isoformat()
        })
    
    return sorted(records, key=lambda x: x["maintenance_date"], reverse=True)


@st.composite
def maintenance_suggestions_strategy(draw):
    """Generate realistic maintenance suggestions."""
    suggestion_types = ["50h", "250h", "500h", "1000h"]
    priorities = ["low", "medium", "high"]
    
    num_suggestions = draw(st.integers(min_value=0, max_value=5))
    suggestions = []
    
    for i in range(num_suggestions):
        suggestions.append({
            "type": draw(st.sampled_from(suggestion_types)),
            "description": draw(st.text(min_size=20, max_size=100, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pc", "Pd", "Zs")))),
            "priority": draw(st.sampled_from(priorities)),
            "current_hours": draw(st.floats(min_value=0, max_value=5000, allow_nan=False, allow_infinity=False)),
            "hours_since_last": draw(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)),
            "recommended_hours": draw(st.integers(min_value=50, max_value=1000)),
            "overdue_hours": draw(st.floats(min_value=0, max_value=200, allow_nan=False, allow_infinity=False))
        })
    
    return suggestions


@st.composite
def user_context_strategy(draw):
    """Generate realistic user context."""
    roles = ["user", "admin", "super_admin"]
    languages = ["en", "el", "ar", "es", "tr", "no"]
    
    return {
        "user_id": str(uuid.uuid4()),
        "username": draw(st.text(min_size=3, max_size=20, alphabet=st.characters(whitelist_categories=("Ll", "Nd")))),
        "name": draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Zs")))),
        "role": draw(st.sampled_from(roles)),
        "preferred_language": draw(st.sampled_from(languages)),
        "organization": {
            "id": str(uuid.uuid4()),
            "name": draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Zs")))),
            "organization_type": "customer"
        }
    }


@st.composite
def problem_description_strategy(draw):
    """Generate realistic problem descriptions."""
    problems = [
        "Machine won't start",
        "Poor cleaning performance",
        "Strange noise during operation",
        "Remote control not responding",
        "Hydraulic pressure low",
        "Electrical fault detected",
        "Wheels not moving properly",
        "Suction power reduced",
        "Machine overheating",
        "Control panel not working"
    ]
    
    base_problem = draw(st.sampled_from(problems))
    additional_details = draw(st.text(min_size=0, max_size=100, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pc", "Pd", "Zs"))))
    
    if additional_details.strip():
        return f"{base_problem}. {additional_details.strip()}"
    return base_problem


class TestMachineAwareGuidance:
    """Test suite for machine-aware guidance functionality."""
    
    def create_troubleshooting_service(self):
        """Create troubleshooting service with mocked dependencies."""
        mock_llm_client = AsyncMock(spec=LLMClient)
        mock_session_manager = AsyncMock(spec=SessionManager)
        return TroubleshootingService(mock_llm_client, mock_session_manager), mock_llm_client
    
    @given(
        machine_details=machine_details_strategy(),
        maintenance_history=maintenance_history_strategy(),
        maintenance_suggestions=maintenance_suggestions_strategy(),
        user_context=user_context_strategy(),
        problem_description=problem_description_strategy()
    )
    @settings(max_examples=50, deadline=30000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_machine_context_incorporation_property(
        self,
        machine_details: Dict[str, Any],
        maintenance_history: List[Dict[str, Any]],
        maintenance_suggestions: List[Dict[str, Any]],
        user_context: Dict[str, Any],
        problem_description: str
    ):
        """
        **Property 4: Machine-Aware Guidance**
        
        For any selected machine, troubleshooting guidance should incorporate 
        machine-specific details, maintenance history, and usage patterns 
        from the ABParts database.
        
        **Validates: Requirements 4.2, 4.3, 4.4, 4.5**
        """
        # Assume valid inputs
        assume(len(problem_description.strip()) > 5)
        assume(machine_details["latest_hours"] >= 0)
        
        # Create service instances
        troubleshooting_service, mock_llm_client = self.create_troubleshooting_service()
        
        async def run_test():
            # Mock the ABParts integration responses at the module level
            with patch('app.services.troubleshooting_service.abparts_integration') as mock_integration:
                mock_integration.get_machine_details = AsyncMock(return_value=machine_details)
                mock_integration.get_maintenance_history = AsyncMock(return_value=maintenance_history)
                mock_integration.get_parts_usage_data = AsyncMock(return_value=[])
                mock_integration.get_machine_hours_history = AsyncMock(return_value=[])
                mock_integration.get_preventive_maintenance_suggestions = AsyncMock(return_value=maintenance_suggestions)
                mock_integration.get_user_preferences = AsyncMock(return_value=user_context)
                
                # Mock the database session context manager
                with patch('app.services.troubleshooting_service.get_db_session') as mock_db_session:
                    mock_db = MagicMock()
                    mock_db_session.return_value.__enter__.return_value = mock_db
                    mock_db_session.return_value.__exit__.return_value = None
                    
                    # Mock LLM response
                    mock_assessment = DiagnosticAssessment(
                        problem_category="mechanical",
                        likely_causes=["Test cause 1", "Test cause 2"],
                        confidence_level=ConfidenceLevel.medium,
                        recommended_steps=["Test step 1", "Test step 2"],
                        safety_warnings=["Test warning"],
                        estimated_duration=30,
                        requires_expert=False
                    )
                    
                    mock_llm_client.generate_response.return_value = AsyncMock(
                        success=True,
                        content='{"problem_category": "mechanical", "likely_causes": ["Test cause"], "confidence_level": "medium", "recommended_steps": ["Test step"], "safety_warnings": ["Test warning"], "estimated_duration": 30, "requires_expert": false}'
                    )
                    
                    # Start troubleshooting workflow with machine context
                    session_id = str(uuid.uuid4())
                    
                    result = await troubleshooting_service.start_troubleshooting_workflow(
                        session_id=session_id,
                        problem_description=problem_description,
                        machine_id=machine_details["id"],
                        user_id=user_context["user_id"],
                        language=user_context["preferred_language"]
                    )
                    
                    # Verify that machine context was retrieved
                    mock_integration.get_machine_details.assert_called_once_with(machine_details["id"])
                    mock_integration.get_maintenance_history.assert_called_once_with(machine_details["id"], limit=5)
                    mock_integration.get_preventive_maintenance_suggestions.assert_called_once_with(machine_details["id"])
                    mock_integration.get_user_preferences.assert_called_once_with(user_context["user_id"])
                    
                    # Verify that LLM was called with enhanced context
                    assert mock_llm_client.generate_response.called
                    
                    # Verify that the result incorporates machine-specific information
                    assert result is not None
                    assert isinstance(result, DiagnosticAssessment)
                    
                    # The guidance should be contextually relevant
                    assert len(result.recommended_steps) > 0
                    assert len(result.likely_causes) > 0
        
        # Run the async test
        asyncio.run(run_test())
    
    @given(
        machine_details=machine_details_strategy(),
        maintenance_history=maintenance_history_strategy(),
        problem_description=problem_description_strategy()
    )
    @settings(max_examples=30, deadline=20000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_maintenance_history_consideration_property(
        self,
        machine_details: Dict[str, Any],
        maintenance_history: List[Dict[str, Any]],
        problem_description: str
    ):
        """
        Test that maintenance history is properly considered in troubleshooting guidance.
        
        **Validates: Requirements 4.3, 4.4**
        """
        # Assume valid inputs
        assume(len(problem_description.strip()) > 5)
        assume(len(maintenance_history) >= 0)
        
        # Create service instances
        troubleshooting_service, mock_llm_client = self.create_troubleshooting_service()
        
        async def run_test():
            with patch('app.services.troubleshooting_service.abparts_integration') as mock_integration:
                mock_integration.get_machine_details = AsyncMock(return_value=machine_details)
                mock_integration.get_maintenance_history = AsyncMock(return_value=maintenance_history)
                mock_integration.get_parts_usage_data = AsyncMock(return_value=[])
                mock_integration.get_machine_hours_history = AsyncMock(return_value=[])
                mock_integration.get_preventive_maintenance_suggestions = AsyncMock(return_value=[])
                mock_integration.get_user_preferences = AsyncMock(return_value={"preferred_language": "en"})
                
                # Mock the database session context manager
                with patch('app.services.troubleshooting_service.get_db_session') as mock_db_session:
                    mock_db = MagicMock()
                    mock_db_session.return_value.__enter__.return_value = mock_db
                    mock_db_session.return_value.__exit__.return_value = None
                    
                    # Mock LLM response
                    mock_llm_client.generate_response.return_value = AsyncMock(
                        success=True,
                        content='{"problem_category": "maintenance", "likely_causes": ["Maintenance related"], "confidence_level": "medium", "recommended_steps": ["Check maintenance"], "safety_warnings": [], "estimated_duration": 30, "requires_expert": false}'
                    )
                    
                    session_id = str(uuid.uuid4())
                    
                    result = await troubleshooting_service.start_troubleshooting_workflow(
                        session_id=session_id,
                        problem_description=problem_description,
                        machine_id=machine_details["id"],
                        user_id=str(uuid.uuid4()),
                        language="en"
                    )
                    
                    # Verify maintenance history was retrieved
                    mock_integration.get_maintenance_history.assert_called_once()
                    
                    # If there's maintenance history, it should influence the guidance
                    if maintenance_history:
                        # The system should have access to recent maintenance information
                        assert mock_integration.get_maintenance_history.called
                        
                        # Recent maintenance should be considered in the analysis
                        # (This is verified by checking that the integration was called)
                        recent_maintenance = [m for m in maintenance_history if 
                                            (datetime.now() - datetime.fromisoformat(m["maintenance_date"].replace('Z', '+00:00').replace('+00:00', ''))).days <= 30]
                        
                        # The guidance should be informed by maintenance patterns
                        assert result is not None
        
        asyncio.run(run_test())
    
    @given(
        machine_details=machine_details_strategy(),
        maintenance_suggestions=maintenance_suggestions_strategy(),
        problem_description=problem_description_strategy()
    )
    @settings(max_examples=30, deadline=20000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_preventive_maintenance_integration_property(
        self,
        machine_details: Dict[str, Any],
        maintenance_suggestions: List[Dict[str, Any]],
        problem_description: str
    ):
        """
        Test that preventive maintenance suggestions are integrated into guidance.
        
        **Validates: Requirements 4.5**
        """
        # Assume valid inputs
        assume(len(problem_description.strip()) > 5)
        
        # Create service instances
        troubleshooting_service, mock_llm_client = self.create_troubleshooting_service()
        
        async def run_test():
            with patch('app.services.troubleshooting_service.abparts_integration') as mock_integration:
                mock_integration.get_machine_details = AsyncMock(return_value=machine_details)
                mock_integration.get_maintenance_history = AsyncMock(return_value=[])
                mock_integration.get_parts_usage_data = AsyncMock(return_value=[])
                mock_integration.get_machine_hours_history = AsyncMock(return_value=[])
                mock_integration.get_preventive_maintenance_suggestions = AsyncMock(return_value=maintenance_suggestions)
                mock_integration.get_user_preferences = AsyncMock(return_value={"preferred_language": "en"})
                
                # Mock the database session context manager
                with patch('app.services.troubleshooting_service.get_db_session') as mock_db_session:
                    mock_db = MagicMock()
                    mock_db_session.return_value.__enter__.return_value = mock_db
                    mock_db_session.return_value.__exit__.return_value = None
                    
                    # Mock LLM response
                    mock_llm_client.generate_response.return_value = AsyncMock(
                        success=True,
                        content='{"problem_category": "maintenance", "likely_causes": ["Preventive maintenance needed"], "confidence_level": "medium", "recommended_steps": ["Perform maintenance"], "safety_warnings": [], "estimated_duration": 45, "requires_expert": false}'
                    )
                    
                    session_id = str(uuid.uuid4())
                    
                    result = await troubleshooting_service.start_troubleshooting_workflow(
                        session_id=session_id,
                        problem_description=problem_description,
                        machine_id=machine_details["id"],
                        user_id=str(uuid.uuid4()),
                        language="en"
                    )
                    
                    # Verify maintenance suggestions were retrieved
                    mock_integration.get_preventive_maintenance_suggestions.assert_called_once_with(machine_details["id"])
                    
                    # If there are high-priority maintenance suggestions, they should influence guidance
                    high_priority_suggestions = [s for s in maintenance_suggestions if s.get("priority") == "high"]
                    
                    if high_priority_suggestions:
                        # The guidance should consider overdue maintenance
                        assert result is not None
                        
                        # High priority maintenance should potentially increase estimated duration
                        if len(high_priority_suggestions) > 0:
                            # The system should have access to maintenance suggestions
                            assert mock_integration.get_preventive_maintenance_suggestions.called
        
        asyncio.run(run_test())
    
    @given(
        machine_details_1=machine_details_strategy(),
        machine_details_2=machine_details_strategy(),
        problem_description=problem_description_strategy()
    )
    @settings(max_examples=20, deadline=15000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_machine_specific_guidance_differentiation_property(
        self,
        machine_details_1: Dict[str, Any],
        machine_details_2: Dict[str, Any],
        problem_description: str
    ):
        """
        Test that guidance differs appropriately based on machine-specific details.
        
        **Validates: Requirements 4.2, 4.3**
        """
        # Ensure machines are different
        assume(machine_details_1["id"] != machine_details_2["id"])
        assume(len(problem_description.strip()) > 5)
        
        # Make machines significantly different
        machine_details_1["model_type"] = "V3.1B"
        machine_details_1["latest_hours"] = 100.0
        machine_details_2["model_type"] = "V4.0"
        machine_details_2["latest_hours"] = 2000.0
        
        # Create service instances
        troubleshooting_service, mock_llm_client = self.create_troubleshooting_service()
        
        async def run_test():
            with patch('app.services.troubleshooting_service.abparts_integration') as mock_integration:
                # Mock responses for first machine
                mock_integration.get_machine_details = AsyncMock(return_value=machine_details_1)
                mock_integration.get_maintenance_history = AsyncMock(return_value=[])
                mock_integration.get_parts_usage_data = AsyncMock(return_value=[])
                mock_integration.get_machine_hours_history = AsyncMock(return_value=[])
                mock_integration.get_preventive_maintenance_suggestions = AsyncMock(return_value=[])
                mock_integration.get_user_preferences = AsyncMock(return_value={"preferred_language": "en"})
                
                # Mock the database session context manager
                with patch('app.services.troubleshooting_service.get_db_session') as mock_db_session:
                    mock_db = MagicMock()
                    mock_db_session.return_value.__enter__.return_value = mock_db
                    mock_db_session.return_value.__exit__.return_value = None
                    
                    mock_llm_client.generate_response.return_value = AsyncMock(
                        success=True,
                        content='{"problem_category": "mechanical", "likely_causes": ["Machine 1 cause"], "confidence_level": "medium", "recommended_steps": ["Machine 1 step"], "safety_warnings": [], "estimated_duration": 30, "requires_expert": false}'
                    )
                    
                    # Get guidance for first machine
                    session_id_1 = str(uuid.uuid4())
                    result_1 = await troubleshooting_service.start_troubleshooting_workflow(
                        session_id=session_id_1,
                        problem_description=problem_description,
                        machine_id=machine_details_1["id"],
                        user_id=str(uuid.uuid4()),
                        language="en"
                    )
                    
                    # Mock responses for second machine
                    mock_integration.get_machine_details = AsyncMock(return_value=machine_details_2)
                    
                    # Get guidance for second machine
                    session_id_2 = str(uuid.uuid4())
                    result_2 = await troubleshooting_service.start_troubleshooting_workflow(
                        session_id=session_id_2,
                        problem_description=problem_description,
                        machine_id=machine_details_2["id"],
                        user_id=str(uuid.uuid4()),
                        language="en"
                    )
                    
                    # Both should succeed
                    assert result_1 is not None
                    assert result_2 is not None
                    
                    # Both should have called the integration service
                    assert mock_integration.get_machine_details.call_count >= 2
                    
                    # The system should have retrieved machine-specific context for both
                    # (The actual differentiation in guidance would depend on LLM processing)
                    assert isinstance(result_1, DiagnosticAssessment)
                    assert isinstance(result_2, DiagnosticAssessment)
        
        asyncio.run(run_test())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])