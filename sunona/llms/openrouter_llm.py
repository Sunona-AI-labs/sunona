"""
Sunona Voice AI - OpenRouter LLM

LLM provider using OpenRouter API with NVIDIA Nemotron and other models.
"""

import os
import json
import logging
from typing import AsyncIterator, Optional, Dict, Any, List

try:
    import httpx
except ImportError:
    httpx = None

from sunona.llms.base_llm import BaseLLM

logger = logging.getLogger(__name__)


class OpenRouterLLM(BaseLLM):
    """
    OpenRouter LLM provider with support for NVIDIA Nemotron and other models.
    
    Features:
        - OpenAI-compatible API
        - Streaming responses
        - NVIDIA Nemotron 30B free model (default)
        - Support for multiple model providers
    """
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "mistralai/mistral-7b-instruct:free",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        top_p: float = 0.9,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        stop: Optional[List[str]] = None,
        stream: bool = True,
        site_url: Optional[str] = None,
        site_name: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize OpenRouter LLM.
        
        Args:
            api_key: OpenRouter API key (or set OPENROUTER_API_KEY env var)
            model: Model identifier (default: nvidia/nemotron-3-nano-30b-a3b:free)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            frequency_penalty: Frequency penalty
            presence_penalty: Presence penalty
            stop: Stop sequences
            stream: Whether to stream responses
            site_url: Your site URL for OpenRouter rankings
            site_name: Your site name for OpenRouter rankings
        """
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
        
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key required. Set OPENROUTER_API_KEY env var or pass api_key."
            )
        
        self.site_url = site_url or os.getenv("OPENROUTER_SITE_URL", "https://sunona.ai")
        self.site_name = site_name or os.getenv("OPENROUTER_SITE_NAME", "Sunona AI")
        
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if httpx is None:
            raise ImportError("httpx package required. Install with: pip install httpx")
        
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers=self._get_headers(),
                timeout=httpx.Timeout(60.0, connect=10.0),
            )
        return self._client
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.site_url,
            "X-Title": self.site_name,
        }
        return headers
    
    def _build_request_body(
        self,
        messages: List[Dict[str, str]],
        stream: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Build the API request body."""
        body = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
            "top_p": kwargs.get("top_p", self.top_p),
            "frequency_penalty": kwargs.get("frequency_penalty", self.frequency_penalty),
            "presence_penalty": kwargs.get("presence_penalty", self.presence_penalty),
            "stream": stream,
        }
        
        stop = kwargs.get("stop", self.stop)
        if stop:
            body["stop"] = stop
        
        return body
    
    async def generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        Generate a response (non-streaming).
        
        Args:
            messages: List of message dicts
            **kwargs: Additional options
            
        Returns:
            Generated response text
        """
        client = await self._get_client()
        body = self._build_request_body(messages, stream=False, **kwargs)
        
        try:
            response = await client.post("/chat/completions", json=body)
            response.raise_for_status()
            
            data = response.json()
            choices = data.get("choices", [])
            
            if not choices:
                logger.warning("No choices in OpenRouter response")
                return ""
            
            content = choices[0].get("message", {}).get("content", "")
            return content
            
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenRouter HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"OpenRouter error: {e}")
            raise
    
    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream a response.
        
        Args:
            messages: List of message dicts
            **kwargs: Additional options
            
        Yields:
            Response text chunks
        """
        client = await self._get_client()
        body = self._build_request_body(messages, stream=True, **kwargs)
        
        try:
            async with client.stream("POST", "/chat/completions", json=body) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    
                    # Handle SSE format
                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove "data: " prefix
                        
                        if data_str.strip() == "[DONE]":
                            break
                        
                        try:
                            data = json.loads(data_str)
                            choices = data.get("choices", [])
                            
                            if choices:
                                delta = choices[0].get("delta", {})
                                content = delta.get("content", "")
                                
                                if content:
                                    # Filter out special tokens from various models
                                    content = content.replace("<s>", "").replace("</s>", "")
                                    content = content.replace("<|im_start|>", "").replace("<|im_end|>", "")
                                    if content.strip():
                                        yield content
                        
                        except json.JSONDecodeError:
                            logger.debug(f"Could not parse SSE data: {data_str}")
                            continue
        
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenRouter stream error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"OpenRouter stream error: {e}")
            raise
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    @staticmethod
    def list_free_models() -> List[str]:
        """List available free models on OpenRouter."""
        return [
            "nvidia/nemotron-3-nano-30b-a3b:free",
            "meta-llama/llama-3.1-8b-instruct:free",
            "google/gemma-2-9b-it:free",
            "mistralai/mistral-7b-instruct:free",
            "qwen/qwen-2-7b-instruct:free",
        ]
