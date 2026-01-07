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

from app.llm_client import LLMClient, ConversationMessage, LLMResponse


def run_async_test(coro):
    """Helper to run async tests with Hypothesis."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestLLMClientReliability:
    """Property-based tests for LLM client network resilience."""
    
    @given(
        message_content=st.text(min_size=1, max_size=50).filter(lambda x: x.strip() and len(x.strip()) > 0),
        language=st.sampled_from(["en", "el", "es"])
    )
    @settings(max_examples=10, deadline=5000)
    def test_network_resilience_successful_response(self, message_content, language):
        """
        Property: For any valid message and language, when network is working,
        the LLM client should generate a successful response.
        
        **Validates: Requirements 9.2, 9.4, 9.5**
        """
        async def async_test():
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
                
                # Create a simple mock response
                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].message.content = f"Response in {language}: {message_content[:20]}"
                mock_response.model = "gpt-4"
                mock_response.usage.total_tokens = 30
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
        
        run_async_test(async_test())
    
    @given(
        message_content=st.text(min_size=1, max_size=50).filter(lambda x: x.strip() and len(x.strip()) > 0),
        error_type=st.sampled_from(["rate_limit", "api_error"])
    )
    @settings(max_examples=8, deadline=5000)
    def test_network_resilience_error_handling(self, message_content, error_type):
        """
        Property: For any valid message and network error,
        the LLM client should handle errors gracefully and provide fallback.
        
        **Validates: Requirements 9.2, 9.4, 9.5**
        """
        async def async_test():
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
                    mock_openai_client.chat.completions.create.side_effect = Exception("Rate limit exceeded")
                elif error_type == "api_error":
                    mock_openai_client.chat.completions.create.side_effect = Exception("API error")
                
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
        
        run_async_test(async_test())
    
    @given(
        message_content=st.text(min_size=1, max_size=50).filter(lambda x: x.strip() and len(x.strip()) > 0)
    )
    @settings(max_examples=5, deadline=5000)
    def test_network_resilience_model_fallback(self, message_content):
        """
        Property: For any valid message, when primary model fails,
        the client should attempt fallback model for resilience.
        
        **Validates: Requirements 9.2, 9.4, 9.5**
        """
        async def async_test():
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
                        raise Exception("Primary model error")
                    else:
                        # Second call (fallback model) succeeds
                        mock_response = MagicMock()
                        mock_response.choices = [MagicMock()]
                        mock_response.choices[0].message.content = "Fallback response"
                        mock_response.model = "gpt-3.5-turbo"
                        mock_response.usage.total_tokens = 25
                        return mock_response
                
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
        
        run_async_test(async_test())


# Simple unit tests for basic functionality
class TestBasicFunctionality:
    """Basic unit tests for LLM client functionality."""
    
    def test_client_initialization(self):
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
    
    def test_error_response_creation(self):
        """Test that error responses are created correctly."""
        with patch('app.llm_client.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_settings.OPENAI_MODEL = "gpt-4"
            mock_settings.OPENAI_FALLBACK_MODEL = "gpt-3.5-turbo"
            mock_settings.OPENAI_MAX_RETRIES = 3
            mock_settings.OPENAI_TIMEOUT = 30
            mock_settings.OPENAI_MAX_TOKENS = 1000
            mock_settings.OPENAI_TEMPERATURE = 0.7
            
            client = LLMClient()
            error_response = client._create_error_response("Test error", 1.5)
            
            assert isinstance(error_response, LLMResponse)
            assert error_response.success is False
            assert error_response.error_message == "Test error"
            assert error_response.model_used == "error"
            assert error_response.tokens_used == 0
            assert error_response.response_time == 1.5
            assert len(error_response.content) > 0
    
    def test_language_instruction_generation(self):
        """Test that language instructions are generated correctly."""
        with patch('app.llm_client.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_settings.OPENAI_MODEL = "gpt-4"
            mock_settings.OPENAI_FALLBACK_MODEL = "gpt-3.5-turbo"
            mock_settings.OPENAI_MAX_RETRIES = 3
            mock_settings.OPENAI_TIMEOUT = 30
            mock_settings.OPENAI_MAX_TOKENS = 1000
            mock_settings.OPENAI_TEMPERATURE = 0.7
            
            client = LLMClient()
            
            # Test different languages
            assert "Greek" in client._get_language_instruction("el")
            assert "Arabic" in client._get_language_instruction("ar")
            assert "Spanish" in client._get_language_instruction("es")
            assert "English" in client._get_language_instruction("en")
            assert "English" in client._get_language_instruction("unknown")  # Fallback