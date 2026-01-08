"""
Property-based tests for LLM client reliability.

**Feature: autoboss-ai-assistant, Property 9: Network Resilience**
**Validates: Requirements 9.2, 9.4, 9.5**

This module tests the LLM client's ability to handle various network conditions,
API failures, and provide appropriate fallback behavior.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from hypothesis import given, strategies as st, settings, assume
import openai
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.completion_usage import CompletionUsage

from app.llm_client import LLMClient, ConversationMessage, LLMResponse
from app.config import Settings


# Test data generators
@st.composite
def conversation_messages(draw):
    """Generate valid conversation messages."""
    num_messages = draw(st.integers(min_value=1, max_value=10))
    messages = []
    
    for _ in range(num_messages):
        role = draw(st.sampled_from(["user", "assistant", "system"]))
        content = draw(st.text(min_size=1, max_size=500))
        # Filter out problematic characters that might cause API issues
        assume(content.strip())  # Ensure content is not just whitespace
        assume(not any(char in content for char in ['\x00', '\x01', '\x02']))  # No control chars
        
        messages.append(ConversationMessage(
            role=role,
            content=content.strip(),
            timestamp=draw(st.floats(min_value=0, max_value=2000000000))
        ))
    
    return messages


@st.composite
def language_codes(draw):
    """Generate valid language codes."""
    return draw(st.sampled_from(["en", "el", "ar", "es", "tr", "no"]))


@st.composite
def api_error_scenarios(draw):
    """Generate different API error scenarios."""
    error_type = draw(st.sampled_from([
        "rate_limit",
        "api_error", 
        "timeout",
        "connection_error",
        "invalid_response"
    ]))
    
    return error_type


class TestLLMClientReliability:
    """Property-based tests for LLM client network resilience."""
    
    def create_llm_client(self):
        """Create LLM client for testing."""
        # Mock settings to avoid requiring real API key
        with patch('app.llm_client.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_settings.OPENAI_MODEL = "gpt-4"
            mock_settings.OPENAI_FALLBACK_MODEL = "gpt-3.5-turbo"
            mock_settings.OPENAI_MAX_RETRIES = 3
            mock_settings.OPENAI_TIMEOUT = 30
            mock_settings.OPENAI_MAX_TOKENS = 1000
            mock_settings.OPENAI_TEMPERATURE = 0.7
            
            client = LLMClient()
            
            # Mock the OpenAI client
            mock_openai_client = AsyncMock()
            client.client = mock_openai_client
            
            return client, mock_openai_client
    
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
        messages=conversation_messages(),
        language=language_codes()
    )
    @settings(max_examples=50, deadline=10000)
    async def test_successful_response_generation(self, messages, language):
        """
        Property: For any valid conversation messages and language,
        the LLM client should generate a successful response when the API is working.
        """
        llm_client, mock_openai_client = self.create_llm_client()
        
        # Setup successful API response
        mock_response = self.create_mock_response("Test response in " + language)
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        # Generate response
        result = await llm_client.generate_response(messages, language=language)
        
        # Verify response properties
        assert isinstance(result, LLMResponse)
        assert result.success is True
        assert result.error_message is None
        assert isinstance(result.content, str)
        assert len(result.content) > 0
        assert result.model_used == "gpt-4"
        assert result.tokens_used == 30
        assert result.response_time >= 0
    
    @given(
        messages=conversation_messages(),
        error_scenario=api_error_scenarios()
    )
    @settings(max_examples=30, deadline=15000)
    async def test_error_handling_and_fallback(self, messages, error_scenario):
        """
        Property: For any valid messages and API error scenario,
        the LLM client should handle errors gracefully and provide appropriate fallback.
        """
        llm_client, mock_openai_client = self.create_llm_client()
        
        # Setup error scenarios
        if error_scenario == "rate_limit":
            mock_openai_client.chat.completions.create.side_effect = openai.RateLimitError(
                "Rate limit exceeded", response=MagicMock(), body={}
            )
        elif error_scenario == "api_error":
            mock_openai_client.chat.completions.create.side_effect = openai.APIError(
                "API error", response=MagicMock(), body={}
            )
        elif error_scenario == "timeout":
            mock_openai_client.chat.completions.create.side_effect = asyncio.TimeoutError()
        elif error_scenario == "connection_error":
            mock_openai_client.chat.completions.create.side_effect = ConnectionError("Connection failed")
        elif error_scenario == "invalid_response":
            mock_openai_client.chat.completions.create.side_effect = ValueError("Invalid response")
        
        # Generate response
        result = await llm_client.generate_response(messages, language="en")
        
        # Verify error handling properties
        assert isinstance(result, LLMResponse)
        assert result.success is False
        assert result.error_message is not None
        assert isinstance(result.content, str)
        assert len(result.content) > 0  # Should have fallback message
        assert result.model_used == "error"
        assert result.tokens_used == 0
        assert result.response_time >= 0
    
    @given(
        messages=conversation_messages(),
        language=language_codes()
    )
    @settings(max_examples=20, deadline=15000)
    async def test_model_fallback_mechanism(self, llm_client, messages, language):
        """
        Property: For any valid messages, when primary model fails,
        the client should attempt fallback model and succeed if possible.
        """
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
        
        llm_client.client.chat.completions.create.side_effect = side_effect
        
        # Generate response
        result = await llm_client.generate_response(messages, language=language)
        
        # Verify fallback behavior
        assert isinstance(result, LLMResponse)
        assert result.success is True
        assert result.model_used == "gpt-3.5-turbo"  # Should use fallback model
        assert call_count == 2  # Should have made 2 API calls
    
    @given(
        problem_description=st.text(min_size=10, max_size=200),
        language=language_codes()
    )
    @settings(max_examples=20, deadline=10000)
    async def test_problem_analysis_resilience(self, llm_client, problem_description, language):
        """
        Property: For any problem description and language,
        the problem analysis should handle network issues gracefully.
        """
        # Filter out problematic content
        assume(problem_description.strip())
        assume(not any(char in problem_description for char in ['\x00', '\x01', '\x02']))
        
        # Setup successful response
        mock_response = self.create_mock_response(f"Analysis of: {problem_description[:50]}...")
        llm_client.client.chat.completions.create.return_value = mock_response
        
        # Analyze problem
        result = await llm_client.analyze_problem(
            problem_description=problem_description.strip(),
            language=language
        )
        
        # Verify analysis properties
        assert isinstance(result, LLMResponse)
        assert result.success is True
        assert isinstance(result.content, str)
        assert len(result.content) > 0
        assert result.response_time >= 0
    
    @given(
        messages=conversation_messages()
    )
    @settings(max_examples=15, deadline=15000)
    async def test_retry_mechanism_with_exponential_backoff(self, llm_client, messages):
        """
        Property: For any messages, when API calls fail temporarily,
        the client should retry with exponential backoff and eventually succeed or fail gracefully.
        """
        call_count = 0
        retry_delays = []
        
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:  # Fail first 2 attempts
                raise openai.RateLimitError("Rate limit", response=MagicMock(), body={})
            else:  # Succeed on 3rd attempt
                return self.create_mock_response("Success after retries")
        
        llm_client.client.chat.completions.create.side_effect = side_effect
        
        # Mock sleep to track retry delays
        original_sleep = asyncio.sleep
        
        async def mock_sleep(delay):
            retry_delays.append(delay)
            # Don't actually sleep in tests
            pass
        
        with patch('asyncio.sleep', mock_sleep):
            result = await llm_client.generate_response(messages, language="en")
        
        # Verify retry behavior
        assert isinstance(result, LLMResponse)
        assert result.success is True
        assert call_count == 3  # Should have made 3 attempts
        assert len(retry_delays) == 2  # Should have 2 retry delays
        # Verify exponential backoff (delays should increase)
        if len(retry_delays) > 1:
            assert retry_delays[1] > retry_delays[0]
    
    @given(
        language=language_codes()
    )
    @settings(max_examples=10, deadline=5000)
    async def test_language_instruction_handling(self, llm_client, language):
        """
        Property: For any supported language, the client should include
        appropriate language instructions in the API call.
        """
        # Setup mock to capture API call arguments
        mock_response = self.create_mock_response("Response in " + language)
        llm_client.client.chat.completions.create.return_value = mock_response
        
        messages = [ConversationMessage(role="user", content="Test message")]
        
        # Generate response
        result = await llm_client.generate_response(messages, language=language)
        
        # Verify API call was made
        assert llm_client.client.chat.completions.create.called
        call_args = llm_client.client.chat.completions.create.call_args
        
        # Verify language instruction was added for non-English languages
        api_messages = call_args[1]['messages']
        if language != "en":
            # Should have system message with language instruction
            assert len(api_messages) >= 2
            assert api_messages[0]['role'] == 'system'
            assert language in api_messages[0]['content'] or "Respond in" in api_messages[0]['content']
        
        assert result.success is True


# Additional unit tests for edge cases
class TestLLMClientEdgeCases:
    """Unit tests for specific edge cases and error conditions."""
    
    @pytest.fixture
    async def llm_client(self):
        """Create LLM client for testing."""
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
            
            yield client
    
    async def test_empty_message_handling(self, llm_client):
        """Test handling of empty or whitespace-only messages."""
        messages = [ConversationMessage(role="user", content="   ")]
        
        mock_response = ChatCompletion(
            id="test-id",
            object="chat.completion", 
            created=1234567890,
            model="gpt-4",
            choices=[
                MagicMock(
                    message=ChatCompletionMessage(role="assistant", content="Please provide a valid message."),
                    finish_reason="stop",
                    index=0
                )
            ],
            usage=CompletionUsage(prompt_tokens=5, completion_tokens=10, total_tokens=15)
        )
        
        llm_client.client.chat.completions.create.return_value = mock_response
        
        result = await llm_client.generate_response(messages)
        
        assert result.success is True
        assert isinstance(result.content, str)
    
    async def test_client_not_initialized(self):
        """Test behavior when client is not properly initialized."""
        client = LLMClient()
        # Don't initialize the client
        
        messages = [ConversationMessage(role="user", content="test")]
        
        with pytest.raises(AttributeError):
            await client.generate_response(messages)