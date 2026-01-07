"""
Property-based tests for LLM client network resilience.

**Feature: autoboss-ai-assistant, Property 9: Network Resilience**
**Validates: Requirements 9.2, 9.4, 9.5**

This module tests the LLM client's ability to handle various network conditions,
API failures, and provide appropriate fallback behavior.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from hypothesis import given, strategies as st, settings
import openai
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.completion_usage import CompletionUsage

from app.llm_client import LLMClient, ConversationMessage, LLMResponse


class TestNetworkResilience:
    """Property-based tests for LLM client network resilience."""
    
    def create_mock_response(self, content: str = "Test response", model: str = "gpt-4"):
        """Create a mock OpenAI response."""
        return ChatCompletion(
            id="test-id",
            object="chat.completion",
            created=1234567890,
            model=model,
            choices=[
                MagicMock(
                    message=ChatCompletionMessage(
                        role="assistant",
                        content=content
                    ),
                    finish_reason="stop",
                    index=0
                )
            ],
            usage=CompletionUsage(
                prompt_tokens=10,
                completion_tokens=20,
                total_tokens=30
            )
        )
    
    @given(
        message_content=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
        language=st.sampled_from(["en", "el", "ar", "es", "tr", "no"])
    )
    @settings(max_examples=20, deadline=5000)
    async def test_successful_response_with_network_conditions(self, message_content, language):
        """
        Property: For any valid message and language, when network is working,
        the LLM client should generate a successful response.
        
        **Validates: Requirements 9.2, 9.4, 9.5**
        """
        with patch('app.llm_client.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_settings.OPENAI_MODEL = "gpt-4"
            mock_settings.OPENAI_FALLBACK_MODEL = "gpt-3.5-turbo"
            mock_settings.OPENAI_MAX_RETRIES = 3
            mock_settings.OPENAI_TIMEOUT = 30
            mock_settings.OPENAI_MAX_TOKENS = 1000
            mock_settings.OPENAI_TEMPERATURE = 0.7
            
            client = LLMClient()
            mock_openai_client = AsyncMock()
            client.client = mock_openai_client
            
            # Setup successful API response
            mock_response = self.create_mock_response(f"Response in {language}")
            mock_openai_client.chat.completions.create.return_value = mock_response
            
            # Create message
            messages = [ConversationMessage(role="user", content=message_content)]
            
            # Generate response
            result = await client.generate_response(messages, language=language)
            
            # Verify response properties for network resilience
            assert isinstance(result, LLMResponse)
            assert result.success is True
            assert result.error_message is None
            assert isinstance(result.content, str)
            assert len(result.content) > 0
            assert result.response_time >= 0
            assert result.tokens_used > 0
    
    @given(
        message_content=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
        error_type=st.sampled_from(["rate_limit", "api_error", "timeout", "connection_error"])
    )
    @settings(max_examples=15, deadline=8000)
    async def test_graceful_error_handling(self, message_content, error_type):
        """
        Property: For any valid message and network error,
        the LLM client should handle errors gracefully and provide fallback.
        
        **Validates: Requirements 9.2, 9.4, 9.5**
        """
        with patch('app.llm_client.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_settings.OPENAI_MODEL = "gpt-4"
            mock_settings.OPENAI_FALLBACK_MODEL = "gpt-3.5-turbo"
            mock_settings.OPENAI_MAX_RETRIES = 3
            mock_settings.OPENAI_TIMEOUT = 30
            mock_settings.OPENAI_MAX_TOKENS = 1000
            mock_settings.OPENAI_TEMPERATURE = 0.7
            
            client = LLMClient()
            mock_openai_client = AsyncMock()
            client.client = mock_openai_client
            
            # Setup error scenarios
            if error_type == "rate_limit":
                mock_openai_client.chat.completions.create.side_effect = openai.RateLimitError(
                    "Rate limit exceeded", response=MagicMock(), body={}
                )
            elif error_type == "api_error":
                mock_openai_client.chat.completions.create.side_effect = openai.APIError(
                    "API error", response=MagicMock(), body={}
                )
            elif error_type == "timeout":
                mock_openai_client.chat.completions.create.side_effect = asyncio.TimeoutError()
            elif error_type == "connection_error":
                mock_openai_client.chat.completions.create.side_effect = ConnectionError("Connection failed")
            
            # Create message
            messages = [ConversationMessage(role="user", content=message_content)]
            
            # Generate response
            result = await client.generate_response(messages, language="en")
            
            # Verify graceful error handling
            assert isinstance(result, LLMResponse)
            assert result.success is False
            assert result.error_message is not None
            assert isinstance(result.content, str)
            assert len(result.content) > 0  # Should have fallback message
            assert result.model_used == "error"
            assert result.tokens_used == 0
            assert result.response_time >= 0
    
    @given(
        message_content=st.text(min_size=1, max_size=100).filter(lambda x: x.strip())
    )
    @settings(max_examples=10, deadline=8000)
    async def test_model_fallback_resilience(self, message_content):
        """
        Property: For any valid message, when primary model fails,
        the client should attempt fallback model for resilience.
        
        **Validates: Requirements 9.2, 9.4, 9.5**
        """
        with patch('app.llm_client.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_settings.OPENAI_MODEL = "gpt-4"
            mock_settings.OPENAI_FALLBACK_MODEL = "gpt-3.5-turbo"
            mock_settings.OPENAI_MAX_RETRIES = 3
            mock_settings.OPENAI_TIMEOUT = 30
            mock_settings.OPENAI_MAX_TOKENS = 1000
            mock_settings.OPENAI_TEMPERATURE = 0.7
            
            client = LLMClient()
            mock_openai_client = AsyncMock()
            client.client = mock_openai_client
            
            # Setup primary model failure, fallback success
            call_count = 0
            
            def side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    # First call (primary model) fails
                    raise openai.APIError("Primary model error", response=MagicMock(), body={})
                else:
                    # Second call (fallback model) succeeds
                    return self.create_mock_response("Fallback response", "gpt-3.5-turbo")
            
            mock_openai_client.chat.completions.create.side_effect = side_effect
            
            # Create message
            messages = [ConversationMessage(role="user", content=message_content)]
            
            # Generate response
            result = await client.generate_response(messages, language="en")
            
            # Verify fallback resilience
            assert isinstance(result, LLMResponse)
            assert result.success is True
            assert result.model_used == "gpt-3.5-turbo"  # Should use fallback model
            assert call_count == 2  # Should have made 2 API calls
            assert result.response_time >= 0


# Simple unit test to verify basic functionality
class TestBasicFunctionality:
    """Basic unit tests for LLM client functionality."""
    
    async def test_client_initialization(self):
        """Test that client can be initialized properly."""
        with patch('app.llm_client.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_settings.OPENAI_MODEL = "gpt-4"
            mock_settings.OPENAI_FALLBACK_MODEL = "gpt-3.5-turbo"
            mock_settings.OPENAI_MAX_RETRIES = 3
            mock_settings.OPENAI_TIMEOUT = 30
            mock_settings.OPENAI_MAX_TOKENS = 1000
            mock_settings.OPENAI_TEMPERATURE = 0.7
            
            client = LLMClient()
            assert client.primary_model == "gpt-4"
            assert client.fallback_model == "gpt-3.5-turbo"
            assert client.max_retries == 3