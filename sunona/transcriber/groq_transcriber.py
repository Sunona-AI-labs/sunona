"""
Sunona Voice AI - Groq Whisper Transcriber

Ultra-fast Groq Whisper transcription provider.
Uses Groq's optimized Whisper models for low-latency transcription.
"""

import asyncio
import logging
import os
from typing import AsyncIterator, Dict, Optional, Any

from sunona.transcriber.base_transcriber import BaseTranscriber

logger = logging.getLogger(__name__)

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class GroqTranscriber(BaseTranscriber):
    """
    Groq Whisper Speech-to-Text Transcriber.
    
    Features:
    - Ultra-fast transcription via Groq
    - Whisper model accuracy
    - Multi-language support
    
    Example:
        ```python
        transcriber = GroqTranscriber(
        if not api_key:
            api_key = os.getenv("GROQ_API_KEY", "")
            model="whisper-large-v3",
        )
        
        async with transcriber:
            text = await transcriber.transcribe(audio_bytes)
        ```
    """
    
    BASE_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
    
    # Available models
    MODELS = {
        "whisper-large-v3": "High accuracy, slower",
        "whisper-large-v3-turbo": "Fast, good accuracy (recommended)",
        "distil-whisper-large-v3-en": "Fastest, English only",
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "whisper-large-v3-turbo",
        language: str = "en",
        stream: bool = False,  # Groq doesn't support streaming
        sampling_rate: int = 16000,
        encoding: str = "linear16",
        endpointing: int = 500,
        **kwargs,
    ):
        super().__init__(
            model=model,
            language=language,
            stream=stream,
            sampling_rate=sampling_rate,
            encoding=encoding,
            endpointing=endpointing,
            **kwargs,
        )
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        
        if not HTTPX_AVAILABLE:
            logger.warning("httpx not available for Groq transcriber")
    
    async def connect(self) -> None:
        """Establish connection."""
        if not self.api_key:
            logger.warning("Groq API key not configured")
        self._is_connected = True
        logger.info(f"Groq transcriber connected (model: {self.model})")
    
    async def disconnect(self) -> None:
        """Close connection."""
        self._is_connected = False
        logger.info("Groq transcriber disconnected")
    
    async def transcribe(self, audio_chunk: bytes) -> Optional[str]:
        """
        Transcribe audio to text.
        
        Args:
            audio_chunk: Audio bytes (WAV format preferred)
            
        Returns:
            Transcribed text or None
        """
        if not self.api_key:
            logger.error("Groq API key not configured")
            return None
        
        if not HTTPX_AVAILABLE:
            logger.error("httpx required for Groq transcriber")
            return None
        
        if not audio_chunk:
            return None
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        
        # Prepare multipart form data
        files = {
            "file": ("audio.wav", audio_chunk, "audio/wav"),
            "model": (None, self.model),
            "language": (None, self.language),
            "response_format": (None, "json"),
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.BASE_URL,
                    headers=headers,
                    files=files,
                )
                
                if response.status_code == 200:
                    result = response.json()
                    text = result.get("text", "")
                    
                    # Add to output queue
                    await self._output_queue.put({
                        "text": text,
                        "is_final": True,
                        "confidence": 1.0,
                    })
                    
                    return text
                else:
                    logger.error(f"Groq API error: {response.status_code} - {response.text}")
                    return None
        
        except Exception as e:
            logger.error(f"Groq transcription error: {e}")
            return None
    
    async def transcribe_stream(
        self, 
        audio_stream: AsyncIterator[bytes]
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Transcribe a stream of audio chunks.
        
        Note: Groq doesn't support true streaming, so this buffers and processes.
        
        Args:
            audio_stream: Async iterator of audio bytes
            
        Yields:
            Transcription result dicts
        """
        audio_buffer = b""
        buffer_duration_ms = 0
        chunk_size_ms = 100  # Assuming 100ms per chunk
        
        async for chunk in audio_stream:
            audio_buffer += chunk
            buffer_duration_ms += chunk_size_ms
            
            # Process when buffer reaches threshold (e.g., 2 seconds)
            if buffer_duration_ms >= 2000:
                text = await self.transcribe(audio_buffer)
                if text:
                    yield {
                        "text": text,
                        "is_final": True,
                        "confidence": 1.0,
                    }
                audio_buffer = b""
                buffer_duration_ms = 0
        
        # Process remaining audio
        if audio_buffer:
            text = await self.transcribe(audio_buffer)
            if text:
                yield {
                    "text": text,
                    "is_final": True,
                    "confidence": 1.0,
                }
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return "groq"
