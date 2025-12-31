"""
Sunona Voice AI - Direct OpenAI LLM Provider

High-performance native OpenAI provider with optimized streaming.
Provides the lowest latency for OpenAI models by using the official SDK directly.

Features:
- Native OpenAI SDK integration
- Optimized async streaming
- Full function/tool calling support
- Response format control (JSON mode)
- Vision support for GPT-4V
"""

import os
import logging
from typing import AsyncIterator, Optional, Dict, Any, List

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncOpenAI = None

from sunona.llms.base_llm import BaseLLM

logger = logging.getLogger(__name__)


class OpenAILLM(BaseLLM):
    """
    Direct OpenAI LLM provider for lowest latency.
    
    Uses the official OpenAI Python SDK with async support for 
    optimal performance with GPT-4o, GPT-4o-mini, and other OpenAI models.
    
    Example:
        ```python
        llm = OpenAILLM(model="gpt-4o-mini")
        llm.set_system_prompt("You are a helpful voice assistant.")
        
        async for chunk in llm.chat_stream("What's the weather like?"):
            print(chunk, end="", flush=True)
        ```
    """
    
    # Available models with their characteristics
    MODELS = {
        "gpt-4o": {"context": 128000, "output": 16384, "vision": True},
        "gpt-4o-mini": {"context": 128000, "output": 16384, "vision": True},
        "gpt-4-turbo": {"context": 128000, "output": 4096, "vision": True},
        "gpt-4-turbo-preview": {"context": 128000, "output": 4096, "vision": False},
        "gpt-4": {"context": 8192, "output": 8192, "vision": False},
        "gpt-3.5-turbo": {"context": 16385, "output": 4096, "vision": False},
        "gpt-3.5-turbo-16k": {"context": 16385, "output": 4096, "vision": False},
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
        organization: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        **kwargs
    ):
        """
        Initialize the OpenAI LLM provider.
        
        Args:
            model: Model identifier (e.g., "gpt-4o-mini", "gpt-4o")
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-2)
            top_p: Nucleus sampling parameter
            frequency_penalty: Frequency penalty (-2 to 2)
            presence_penalty: Presence penalty (-2 to 2)
            stop: Stop sequences
            stream: Whether to stream responses
            api_key: OpenAI API key (or OPENAI_API_KEY env var)
            organization: OpenAI organization ID
            base_url: Custom API base URL
            timeout: Request timeout in seconds
            **kwargs: Additional options
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "openai is required for OpenAILLM. "
                "Install with: pip install openai"
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
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.organization = organization or os.getenv("OPENAI_ORG_ID")
        self.base_url = base_url
        self.timeout = timeout
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        # Initialize async client
        self._client = AsyncOpenAI(
            api_key=self.api_key,
            organization=self.organization,
            base_url=self.base_url,
            timeout=self.timeout,
        )
        
        logger.info(f"OpenAI LLM initialized with model: {model}")
    
    def _build_params(
        self,
        messages: List[Dict[str, str]],
        stream: bool = True,
        tools: Optional[List[Dict]] = None,
        response_format: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Build parameters for OpenAI API call."""
        params = {
            "model": self.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
            "top_p": kwargs.get("top_p", self.top_p),
            "frequency_penalty": kwargs.get("frequency_penalty", self.frequency_penalty),
            "presence_penalty": kwargs.get("presence_penalty", self.presence_penalty),
            "stream": stream,
        }
        
        # Add stop sequences
        if self.stop:
            params["stop"] = self.stop
        
        # Add tools for function calling
        if tools:
            params["tools"] = tools
            params["tool_choice"] = kwargs.get("tool_choice", "auto")
        
        # Add response format (JSON mode)
        if response_format:
            params["response_format"] = response_format
        
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
            response = await self._client.chat.completions.create(**params)
            
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content or ""
            
            return ""
            
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            raise
    
    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream a response with minimal latency.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional generation options
            
        Yields:
            Response text chunks
        """
        params = self._build_params(messages, stream=True, **kwargs)
        
        try:
            stream = await self._client.chat.completions.create(**params)
            
            async for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield delta.content
                        
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
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
            response = await self._client.chat.completions.create(**params)
            
            if response.choices and len(response.choices) > 0:
                message = response.choices[0].message
                
                result = {
                    "content": message.content or "",
                    "tool_calls": None,
                }
                
                if message.tool_calls:
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
            logger.error(f"OpenAI tool calling error: {e}")
            raise
    
    async def generate_json(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        Generate a JSON response using structured output mode.
        
        Args:
            messages: List of message dicts
            **kwargs: Additional options
            
        Returns:
            JSON string response
        """
        return await self.generate(
            messages,
            response_format={"type": "json_object"},
            **kwargs
        )
    
    async def close(self) -> None:
        """Close the OpenAI client."""
        if self._client:
            await self._client.close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    @classmethod
    def list_models(cls) -> List[str]:
        """List available OpenAI models."""
        return list(cls.MODELS.keys())
    
    @classmethod
    def get_model_info(cls, model: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model."""
        return cls.MODELS.get(model)
