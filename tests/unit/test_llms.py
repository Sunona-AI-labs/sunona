"""
Sunona Voice AI - Unit Tests for LLM Providers

Tests for LiteLLM universal provider including initialization,
generation, streaming, and provider detection.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestLiteLLMProviderInitialization:
    """Tests for LiteLLMProvider initialization."""
    
    def test_default_initialization(self):
        """Test default initialization with minimal parameters."""
        from sunona.llms.litellm_llm import LiteLLMProvider
        
        llm = LiteLLMProvider()
        
        assert llm.model is not None
        assert llm.temperature == 0.7
        assert llm.stream is True
    
    def test_custom_model(self):
        """Test initialization with custom model."""
        from sunona.llms.litellm_llm import LiteLLMProvider
        
        llm = LiteLLMProvider(
            model="gpt-4o-mini",
            temperature=0.5,
            max_tokens=500
        )
        
        assert llm.model == "gpt-4o-mini"
        assert llm.temperature == 0.5
        assert llm.max_tokens == 500
    
    def test_provider_detection_openai(self):
        """Test provider detection for OpenAI models."""
        from sunona.llms.litellm_llm import LiteLLMProvider
        
        llm = LiteLLMProvider(model="gpt-4o")
        assert llm.provider == "openai"
    
    def test_provider_detection_anthropic(self):
        """Test provider detection for Anthropic models."""
        from sunona.llms.litellm_llm import LiteLLMProvider
        
        llm = LiteLLMProvider(model="claude-3-5-sonnet-20241022")
        assert llm.provider == "anthropic"
    
    def test_provider_detection_groq(self):
        """Test provider detection for Groq models."""
        from sunona.llms.litellm_llm import LiteLLMProvider
        
        llm = LiteLLMProvider(model="groq/llama-3.1-70b-versatile")
        assert llm.provider == "groq"
    
    def test_provider_detection_openrouter(self):
        """Test provider detection for OpenRouter models."""
        from sunona.llms.litellm_llm import LiteLLMProvider
        
        llm = LiteLLMProvider(model="openrouter/mistralai/mistral-7b-instruct:free")
        assert llm.provider == "openrouter"


class TestLiteLLMProviderGeneration:
    """Tests for LiteLLMProvider text generation."""
    
    @pytest.mark.asyncio
    async def test_generate_basic(self, mock_llm_response):
        """Test basic non-streaming generation."""
        from sunona.llms.litellm_llm import LiteLLMProvider
        
        with patch("sunona.llms.litellm_llm.acompletion") as mock_completion:
            # Setup mock response
            mock_response = MagicMock()
            mock_response.choices = [
                MagicMock(message=MagicMock(content="Test response"))
            ]
            mock_completion.return_value = mock_response
            
            llm = LiteLLMProvider(model="gpt-4o-mini")
            
            messages = [
                {"role": "user", "content": "Hello"}
            ]
            
            response = await llm.generate(messages)
            
            assert response == "Test response"
            mock_completion.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_with_system_prompt(self, mock_llm_response):
        """Test generation with system prompt."""
        from sunona.llms.litellm_llm import LiteLLMProvider
        
        with patch("sunona.llms.litellm_llm.acompletion") as mock_completion:
            mock_response = MagicMock()
            mock_response.choices = [
                MagicMock(message=MagicMock(content="Assistant response"))
            ]
            mock_completion.return_value = mock_response
            
            llm = LiteLLMProvider(model="gpt-4o-mini")
            
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"}
            ]
            
            response = await llm.generate(messages)
            
            assert response == "Assistant response"
            
            # Verify messages were passed correctly
            call_args = mock_completion.call_args
            assert len(call_args.kwargs.get("messages", [])) == 2


class TestLiteLLMProviderStreaming:
    """Tests for LiteLLMProvider streaming generation."""
    
    @pytest.mark.asyncio
    async def test_generate_stream(self, mock_streaming_llm_response):
        """Test streaming generation."""
        from sunona.llms.litellm_llm import LiteLLMProvider
        
        with patch("sunona.llms.litellm_llm.acompletion") as mock_completion:
            # Create async generator mock
            async def mock_stream():
                for chunk in mock_streaming_llm_response:
                    mock_chunk = MagicMock()
                    mock_chunk.choices = [MagicMock(delta=MagicMock(
                        content=chunk.get("choices", [{}])[0].get("delta", {}).get("content")
                    ))]
                    yield mock_chunk
            
            mock_completion.return_value = mock_stream()
            
            llm = LiteLLMProvider(model="gpt-4o-mini", stream=True)
            
            messages = [{"role": "user", "content": "Hello"}]
            
            chunks = []
            async for chunk in llm.generate_stream(messages):
                if chunk:
                    chunks.append(chunk)
            
            assert len(chunks) > 0


class TestLiteLLMProviderTools:
    """Tests for LiteLLMProvider function calling."""
    
    @pytest.mark.asyncio
    async def test_generate_with_tools(self):
        """Test generation with tool definitions."""
        from sunona.llms.litellm_llm import LiteLLMProvider
        
        with patch("sunona.llms.litellm_llm.acompletion") as mock_completion:
            mock_response = MagicMock()
            mock_response.choices = [
                MagicMock(
                    message=MagicMock(
                        content=None,
                        tool_calls=[
                            MagicMock(
                                function=MagicMock(
                                    name="get_weather",
                                    arguments='{"location": "London"}'
                                )
                            )
                        ]
                    )
                )
            ]
            mock_completion.return_value = mock_response
            
            llm = LiteLLMProvider(model="gpt-4o-mini")
            
            messages = [
                {"role": "user", "content": "What's the weather in London?"}
            ]
            
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "description": "Get weather for a location",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {"type": "string"}
                            }
                        }
                    }
                }
            ]
            
            result = await llm.generate_with_tools(messages, tools)
            
            assert "tool_calls" in result
            assert len(result["tool_calls"]) > 0


class TestLiteLLMProviderContextManager:
    """Tests for async context manager support."""
    
    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test async context manager entry and exit."""
        from sunona.llms.litellm_llm import LiteLLMProvider
        
        async with LiteLLMProvider(model="gpt-4o-mini") as llm:
            assert llm is not None
            assert llm.model == "gpt-4o-mini"


class TestLiteLLMProviderHelpers:
    """Tests for helper methods."""
    
    def test_list_supported_providers(self):
        """Test listing supported providers."""
        from sunona.llms.litellm_llm import LiteLLMProvider
        
        providers = LiteLLMProvider.list_supported_providers()
        
        assert isinstance(providers, list)
        assert "openai" in providers
        assert "anthropic" in providers
        assert "groq" in providers
    
    def test_get_model_suggestions(self):
        """Test getting model suggestions for a provider."""
        from sunona.llms.litellm_llm import LiteLLMProvider
        
        suggestions = LiteLLMProvider.get_model_suggestions("openai")
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0


class TestLiteLLMProviderErrorHandling:
    """Tests for error handling."""
    
    @pytest.mark.asyncio
    async def test_handles_api_error(self):
        """Test handling of API errors."""
        from sunona.llms.litellm_llm import LiteLLMProvider
        
        with patch("sunona.llms.litellm_llm.acompletion") as mock_completion:
            mock_completion.side_effect = Exception("API Error")
            
            llm = LiteLLMProvider(model="gpt-4o-mini")
            
            messages = [{"role": "user", "content": "Hello"}]
            
            with pytest.raises(Exception) as exc_info:
                await llm.generate(messages)
            
            assert "API Error" in str(exc_info.value)
