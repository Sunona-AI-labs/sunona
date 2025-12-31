"""
Sunona Voice AI - Base Synthesizer

Abstract base class defining the synthesizer interface.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class BaseSynthesizer(ABC):
    """
    Abstract base class for all synthesizer implementations.
    
    Synthesizers convert text to audio using various Text-to-Speech APIs.
    """
    
    def __init__(
        self,
        voice: str = "Bella",
        voice_id: str = "EXAVITQu4vr4xnSDxMaL",
        model: str = "eleven_turbo_v2_5",
        stream: bool = True,
        audio_format: str = "pcm",
        sample_rate: int = 16000,
        buffer_size: int = 40,
        **kwargs
    ):
        """
        Initialize the base synthesizer.
        
        Args:
            voice: Voice name
            voice_id: Voice identifier
            model: TTS model to use
            stream: Whether to stream audio
            audio_format: Output audio format
            sample_rate: Audio sample rate in Hz
            buffer_size: Text buffer size before synthesis
            **kwargs: Additional provider-specific options
        """
        self.voice = voice
        self.voice_id = voice_id
        self.model = model
        self.stream = stream
        self.audio_format = audio_format
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.extra_config = kwargs
        
        self._is_connected = False
        self._text_buffer = ""
    
    @property
    def is_connected(self) -> bool:
        """Check if the synthesizer is connected."""
        return self._is_connected
    
    @abstractmethod
    async def connect(self) -> None:
        """
        Establish connection to the synthesis service.
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """
        Close the connection to the synthesis service.
        """
        pass
    
    @abstractmethod
    async def synthesize(self, text: str) -> bytes:
        """
        Synthesize text to audio.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio bytes
        """
        pass
    
    @abstractmethod
    async def synthesize_stream(
        self, 
        text_stream: AsyncIterator[str]
    ) -> AsyncIterator[bytes]:
        """
        Stream synthesis of text chunks.
        
        Args:
            text_stream: Async iterator of text chunks
            
        Yields:
            Audio bytes chunks
        """
        pass
    
    def add_to_buffer(self, text: str) -> Optional[str]:
        """
        Add text to buffer and return when ready.
        
        Args:
            text: Text chunk to add
            
        Returns:
            Buffered text if ready, None otherwise
        """
        self._text_buffer += text
        
        # Check if buffer is ready (ends with sentence or reached size)
        if len(self._text_buffer) >= self.buffer_size:
            # Find a good break point
            break_chars = ".!?;:"
            for i in range(len(self._text_buffer) - 1, -1, -1):
                if self._text_buffer[i] in break_chars:
                    result = self._text_buffer[:i + 1]
                    self._text_buffer = self._text_buffer[i + 1:]
                    return result.strip()
            
            # No break point found, return everything
            result = self._text_buffer
            self._text_buffer = ""
            return result.strip()
        
        return None
    
    def flush_buffer(self) -> Optional[str]:
        """
        Flush and return any remaining buffered text.
        
        Returns:
            Remaining text or None if empty
        """
        if self._text_buffer:
            result = self._text_buffer.strip()
            self._text_buffer = ""
            return result if result else None
        return None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
    
    def get_config(self) -> Dict[str, Any]:
        """Get the current synthesizer configuration."""
        return {
            "voice": self.voice,
            "voice_id": self.voice_id,
            "model": self.model,
            "stream": self.stream,
            "audio_format": self.audio_format,
            "sample_rate": self.sample_rate,
            "buffer_size": self.buffer_size,
            **self.extra_config,
        }
