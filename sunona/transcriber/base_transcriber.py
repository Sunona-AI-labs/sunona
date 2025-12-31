"""
Sunona Voice AI - Base Transcriber

Abstract base class defining the transcriber interface.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class BaseTranscriber(ABC):
    """
    Abstract base class for all transcriber implementations.
    
    Transcribers convert audio input to text using various Speech-to-Text APIs.
    """
    
    def __init__(
        self,
        model: str = "nova-2",
        language: str = "en",
        stream: bool = True,
        sampling_rate: int = 16000,
        encoding: str = "linear16",
        endpointing: int = 500,
        **kwargs
    ):
        """
        Initialize the base transcriber.
        
        Args:
            model: The STT model to use
            language: Language code for transcription
            stream: Whether to use streaming transcription
            sampling_rate: Audio sample rate in Hz
            encoding: Audio encoding format
            endpointing: Silence duration (ms) before finalizing
            **kwargs: Additional provider-specific options
        """
        self.model = model
        self.language = language
        self.stream = stream
        self.sampling_rate = sampling_rate
        self.encoding = encoding
        self.endpointing = endpointing
        self.extra_config = kwargs
        
        self._is_connected = False
        self._connection = None
        self._input_queue: asyncio.Queue = asyncio.Queue()
        self._output_queue: asyncio.Queue = asyncio.Queue()
    
    @property
    def is_connected(self) -> bool:
        """Check if the transcriber is connected."""
        return self._is_connected
    
    @abstractmethod
    async def connect(self) -> None:
        """
        Establish connection to the transcription service.
        
        This should initialize WebSocket or API connections as needed.
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """
        Close the connection to the transcription service.
        
        This should cleanup any resources and close connections.
        """
        pass
    
    @abstractmethod
    async def transcribe(self, audio_chunk: bytes) -> Optional[str]:
        """
        Transcribe a single audio chunk.
        
        Args:
            audio_chunk: Raw audio bytes
            
        Returns:
            Transcribed text or None if not ready
        """
        pass
    
    @abstractmethod
    async def transcribe_stream(
        self, 
        audio_stream: AsyncIterator[bytes]
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Transcribe a stream of audio chunks.
        
        Args:
            audio_stream: Async iterator of audio bytes
            
        Yields:
            Dictionary with transcription results:
                - text: The transcribed text
                - is_final: Whether this is a final result
                - confidence: Confidence score (0-1)
        """
        pass
    
    async def send_audio(self, audio_chunk: bytes) -> None:
        """
        Send audio data to the transcriber.
        
        Args:
            audio_chunk: Raw audio bytes to transcribe
        """
        await self._input_queue.put(audio_chunk)
    
    async def get_transcription(self, timeout: float = 10.0) -> Optional[Dict[str, Any]]:
        """
        Get the next transcription result.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            Transcription result dict or None if timeout
        """
        try:
            result = await asyncio.wait_for(
                self._output_queue.get(),
                timeout=timeout
            )
            return result
        except asyncio.TimeoutError:
            logger.debug("Transcription timeout")
            return None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
    
    def get_config(self) -> Dict[str, Any]:
        """Get the current transcriber configuration."""
        return {
            "model": self.model,
            "language": self.language,
            "stream": self.stream,
            "sampling_rate": self.sampling_rate,
            "encoding": self.encoding,
            "endpointing": self.endpointing,
            **self.extra_config,
        }
