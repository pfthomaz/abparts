"""
Integration tests for the AI Assistant service.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock

from app.main import app


class TestServiceIntegration:
    """Integration tests for the AI Assistant service."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test the root endpoint returns service information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "AutoBoss AI Assistant"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
    
    def test_info_endpoint(self, client):
        """Test the info endpoint returns configuration information."""
        response = client.get("/info")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "AutoBoss AI Assistant"
        assert "supported_languages" in data
        assert len(data["supported_languages"]) == 6
    
    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get("/health/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "AutoBoss AI Assistant"
    
    def test_models_endpoint(self, client):
        """Test the models endpoint returns available models."""
        response = client.get("/api/ai/models")
        assert response.status_code == 200
        data = response.json()
        assert "primary_model" in data
        assert "fallback_model" in data
        assert "supported_languages" in data
    
    @patch('app.main.llm_client')
    def test_chat_endpoint_success(self, mock_llm_client, client):
        """Test the chat endpoint with successful response."""
        # Mock LLM client
        mock_response = MagicMock()
        mock_response.content = "Hello! How can I help you?"
        mock_response.model_used = "gpt-4"
        mock_response.tokens_used = 25
        mock_response.response_time = 1.2
        mock_response.success = True
        mock_response.error_message = None
        
        mock_llm_client.generate_response = AsyncMock(return_value=mock_response)
        app.state.llm_client = mock_llm_client
        
        # Make request
        response = client.post("/api/ai/chat", json={
            "message": "Hello",
            "language": "en"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["response"] == "Hello! How can I help you?"
        assert data["model_used"] == "gpt-4"
        assert data["tokens_used"] == 25
    
    @patch('app.main.llm_client')
    def test_analyze_problem_endpoint(self, mock_llm_client, client):
        """Test the analyze problem endpoint."""
        # Mock LLM client
        mock_response = MagicMock()
        mock_response.content = "Based on your description, this appears to be a mechanical issue..."
        mock_response.model_used = "gpt-4"
        mock_response.tokens_used = 45
        mock_response.response_time = 2.1
        mock_response.success = True
        mock_response.error_message = None
        
        mock_llm_client.analyze_problem = AsyncMock(return_value=mock_response)
        app.state.llm_client = mock_llm_client
        
        # Make request
        response = client.post("/api/ai/analyze-problem", json={
            "problem_description": "The machine is making strange noises",
            "language": "en"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "mechanical issue" in data["response"]
        assert data["model_used"] == "gpt-4"
    
    def test_session_status_endpoint(self, client):
        """Test the session status endpoint."""
        session_id = "test-session-123"
        response = client.get(f"/api/ai/session/{session_id}/status")
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["status"] == "active"