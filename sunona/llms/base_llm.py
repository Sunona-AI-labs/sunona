"""
Sunona Voice AI - Base LLM

Abstract base class defining the LLM interface.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class BaseLLM(ABC):
    """
    Abstract base class for all LLM implementations.
    
    LLMs process conversation messages and generate responses.
    """
    
    def __init__(
        self,
        model: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        top_p: float = 0.9,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        stop: Optional[List[str]] = None,
        stream: bool = True,
        **kwargs
    ):
        """
        Initialize the base LLM.
        
        Args:
            model: The model identifier
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-2)
            top_p: Nucleus sampling parameter
            frequency_penalty: Frequency penalty (-2 to 2)
            presence_penalty: Presence penalty (-2 to 2)
            stop: Stop sequences
            stream: Whether to stream responses
            **kwargs: Additional provider-specific options
        """
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.stop = stop or []
        self.stream = stream
        self.extra_config = kwargs
        
        self._conversation_history: List[Dict[str, str]] = []
    
    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        Generate a response for the given messages (non-streaming).
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional generation options
            
        Returns:
            Generated response text
        """
        pass
    
    @abstractmethod
    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream a response for the given messages.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional generation options
            
        Yields:
            Response text chunks
        """
        pass
    
    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to conversation history.
        
        Args:
            role: Message role ('system', 'user', 'assistant')
            content: Message content
        """
        self._conversation_history.append({
            "role": role,
            "content": content
        })
    
    def set_system_prompt(self, prompt: str) -> None:
        """
        Set or update the system prompt.
        
        Args:
            prompt: System prompt text
        """
        # Remove existing system message if any
        self._conversation_history = [
            msg for msg in self._conversation_history
            if msg.get("role") != "system"
        ]
        # Add new system message at the beginning
        self._conversation_history.insert(0, {
            "role": "system",
            "content": prompt
        })
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get the current conversation history."""
        return self._conversation_history.copy()
    
    def clear_history(self, keep_system: bool = True) -> None:
        """
        Clear conversation history.
        
        Args:
            keep_system: Whether to keep the system prompt
        """
        if keep_system:
            system_msgs = [
                msg for msg in self._conversation_history
                if msg.get("role") == "system"
            ]
            self._conversation_history = system_msgs
        else:
            self._conversation_history = []
    
    async def chat(self, user_message: str, **kwargs) -> str:
        """
        Convenience method for single-turn chat.
        
        Args:
            user_message: User's message
            **kwargs: Additional generation options
            
        Returns:
            Assistant's response
        """
        self.add_message("user", user_message)
        
        if self.stream:
            response_chunks = []
            async for chunk in self.generate_stream(self._conversation_history, **kwargs):
                response_chunks.append(chunk)
            response = "".join(response_chunks)
        else:
            response = await self.generate(self._conversation_history, **kwargs)
        
        self.add_message("assistant", response)
        return response
    
    async def chat_stream(self, user_message: str, **kwargs) -> AsyncIterator[str]:
        """
        Stream a chat response.
        
        Args:
            user_message: User's message
            **kwargs: Additional generation options
            
        Yields:
            Response text chunks
        """
        self.add_message("user", user_message)
        
        response_chunks = []
        async for chunk in self.generate_stream(self._conversation_history, **kwargs):
            response_chunks.append(chunk)
            yield chunk
        
        response = "".join(response_chunks)
        self.add_message("assistant", response)
    
    def get_config(self) -> Dict[str, Any]:
        """Get the current LLM configuration."""
        return {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "stop": self.stop,
            "stream": self.stream,
            **self.extra_config,
        }
