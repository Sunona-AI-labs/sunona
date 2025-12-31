"""
Sunona Voice AI - LiteLLM Universal Provider

High-performance LLM provider supporting 100+ models via LiteLLM.
Includes OpenAI, Anthropic, Gemini, Azure, Groq, Mistral, and more.

Features:
- Unified interface for all providers
- Native async streaming
- Function/tool calling support
- Automatic fallback handling
- Low-latency optimizations
"""

import os
import logging
from typing import AsyncIterator, Optional, Dict, Any, List, Union

try:
    import litellm
    from litellm import acompletion
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    litellm = None
    acompletion = None

from sunona.llms.base_llm import BaseLLM

logger = logging.getLogger(__name__)

# Disable LiteLLM's verbose logging for production
if LITELLM_AVAILABLE:
    litellm.set_verbose = False


class LiteLLMProvider(BaseLLM):
    """
    Universal LLM provider via LiteLLM.
    
    Supports 100+ models with a unified interface:
    - OpenAI: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo
    - Anthropic: claude-3-5-sonnet-20241022, claude-3-opus, claude-3-haiku
    - Google: gemini/gemini-1.5-pro, gemini/gemini-1.5-flash
    - Azure: azure/gpt-4, azure/gpt-35-turbo
    - Groq: groq/llama-3.1-70b-versatile, groq/mixtral-8x7b-32768
    - Mistral: mistral/mistral-large-latest
    - Together: together_ai/meta-llama/Llama-3-70b-chat-hf
    
    Example:
        ```python
        llm = LiteLLMProvider(model="gpt-4o-mini")
        llm.set_system_prompt("You are a helpful assistant.")
        
        async for chunk in llm.chat_stream("Hello!"):
            print(chunk, end="", flush=True)
        ```
    """
    
    # Model to provider mapping for auto-detection
    PROVIDER_PREFIXES = {
        "gpt-": "openai",
        "claude-": "anthropic",
        "gemini/": "google",
        "azure/": "azure",
        "groq/": "groq",
        "mistral/": "mistral",
        "together_ai/": "together",
        "anthropic/": "anthropic",
        "openai/": "openai",
    }
    
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        top_p: float = 0.9,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        stop: Optional[List[str]] = None,
        stream: bool = True,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        timeout: float = 30.0,
        num_retries: int = 2,
        **kwargs
    ):
        """
        Initialize the LiteLLM provider.
        
        Args:
            model: Model identifier (e.g., "gpt-4o-mini", "claude-3-5-sonnet-20241022")
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-2)
            top_p: Nucleus sampling parameter
            frequency_penalty: Frequency penalty (-2 to 2)
            presence_penalty: Presence penalty (-2 to 2)
            stop: Stop sequences
            stream: Whether to stream responses
            api_key: API key (auto-detected from env if not provided)
            api_base: Custom API base URL
            timeout: Request timeout in seconds
            num_retries: Number of retries on failure
            **kwargs: Additional provider-specific options
        """
        if not LITELLM_AVAILABLE:
            raise ImportError(
                "litellm is required for LiteLLMProvider. "
                "Install with: pip install litellm"
            )
        
        super().__init__(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
            stream=stream,
            **kwargs
        )
        
        self.api_key = api_key
        self.api_base = api_base
        self.timeout = timeout
        self.num_retries = num_retries
        
        # Detect provider from model name
        self.provider = self._detect_provider(model)
        
        # Set API key based on provider if not explicitly provided
        if not self.api_key:
            self._auto_configure_api_key()
        
        logger.info(f"LiteLLM initialized with model: {model} (provider: {self.provider})")
    
    def _detect_provider(self, model: str) -> str:
        """Detect the provider from model name."""
        model_lower = model.lower()
        for prefix, provider in self.PROVIDER_PREFIXES.items():
            if model_lower.startswith(prefix):
                return provider
        # Default to OpenAI for unrecognized models
        return "openai"
    
    def _auto_configure_api_key(self) -> None:
        """Auto-configure API key from environment variables."""
        env_key_mapping = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "google": "GOOGLE_API_KEY",
            "azure": "AZURE_API_KEY",
            "groq": "GROQ_API_KEY",
            "mistral": "MISTRAL_API_KEY",
            "together": "TOGETHER_API_KEY",
        }
        
        env_var = env_key_mapping.get(self.provider, "OPENAI_API_KEY")
        self.api_key = os.getenv(env_var)
        
        if not self.api_key:
            logger.warning(f"No API key found for {self.provider}. Set {env_var} environment variable.")
    
    def _build_params(
        self,
        messages: List[Dict[str, str]],
        stream: bool = True,
        tools: Optional[List[Dict]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Build parameters for LiteLLM API call."""
        params = {
            "model": self.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
            "top_p": kwargs.get("top_p", self.top_p),
            "stream": stream,
            "timeout": self.timeout,
            "num_retries": self.num_retries,
        }
        
        # Add API key if provided
        if self.api_key:
            params["api_key"] = self.api_key
        
        # Add API base if provided
        if self.api_base:
            params["api_base"] = self.api_base
        
        # Add stop sequences
        if self.stop:
            params["stop"] = self.stop
        
        # Add frequency/presence penalties (not all providers support)
        if self.frequency_penalty != 0.0:
            params["frequency_penalty"] = self.frequency_penalty
        if self.presence_penalty != 0.0:
            params["presence_penalty"] = self.presence_penalty
        
        # Add tools for function calling
        if tools:
            params["tools"] = tools
            params["tool_choice"] = kwargs.get("tool_choice", "auto")
        
        return params
    
    async def generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        Generate a response (non-streaming).
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional generation options
            
        Returns:
            Generated response text
        """
        params = self._build_params(messages, stream=False, **kwargs)
        
        try:
            response = await acompletion(**params)
            
            if response.choices and len(response.choices) > 0:
                choice = response.choices[0]
                if hasattr(choice, 'message') and choice.message:
                    return choice.message.content or ""
            
            return ""
            
        except Exception as e:
            logger.error(f"LiteLLM generation error: {e}")
            raise
    
    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream a response.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional generation options
            
        Yields:
            Response text chunks
        """
        params = self._build_params(messages, stream=True, **kwargs)
        
        try:
            response = await acompletion(**params)
            
            async for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        yield delta.content
                        
        except Exception as e:
            logger.error(f"LiteLLM streaming error: {e}")
            raise
    
    async def generate_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response with function calling support.
        
        Args:
            messages: List of message dicts
            tools: List of tool definitions in OpenAI format
            **kwargs: Additional options
            
        Returns:
            Dict with 'content' and/or 'tool_calls'
        """
        params = self._build_params(messages, stream=False, tools=tools, **kwargs)
        
        try:
            response = await acompletion(**params)
            
            if response.choices and len(response.choices) > 0:
                message = response.choices[0].message
                
                result = {
                    "content": message.content or "",
                    "tool_calls": None,
                }
                
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    result["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            }
                        }
                        for tc in message.tool_calls
                    ]
                
                return result
            
            return {"content": "", "tool_calls": None}
            
        except Exception as e:
            logger.error(f"LiteLLM tool calling error: {e}")
            raise
    
    async def close(self) -> None:
        """Cleanup resources (no persistent connections in LiteLLM)."""
        pass
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    @staticmethod
    def list_supported_providers() -> List[str]:
        """List all supported providers."""
        return [
            "openai", "anthropic", "google", "azure", "groq",
            "mistral", "together", "cohere", "replicate", "huggingface",
            "bedrock", "sagemaker", "vertex_ai", "palm", "ollama",
        ]
    
    @staticmethod
    def get_model_suggestions(provider: str) -> List[str]:
        """Get suggested models for a provider."""
        suggestions = {
            "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
            "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"],
            "google": ["gemini/gemini-1.5-pro", "gemini/gemini-1.5-flash"],
            "groq": ["groq/llama-3.1-70b-versatile", "groq/mixtral-8x7b-32768"],
            "mistral": ["mistral/mistral-large-latest", "mistral/mistral-medium-latest"],
            "together": ["together_ai/meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"],
        }
        return suggestions.get(provider, [])
