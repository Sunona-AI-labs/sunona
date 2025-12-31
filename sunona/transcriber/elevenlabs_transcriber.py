"""
Sunona Voice AI - ElevenLabs Transcriber

ElevenLabs speech-to-text provider.
High-quality transcription with voice detection.
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


class ElevenLabsTranscriber(BaseTranscriber):
    """
    ElevenLabs Speech-to-Text Transcriber.
    
    Features:
    - High-quality transcription
    - Speaker diarization
    - Multiple language support
    
    Example:
        ```python
        transcriber = ElevenLabsTranscriber(
            api_key=None,  # Falls back to os.getenv("ELEVEN_LABS_API_KEY")
        )
        
        async with transcriber:
            text = await transcriber.transcribe(audio_bytes)
        ```
    """
    
    BASE_URL = "https://api.elevenlabs.io/v1/speech-to-text"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "scribe_v1",
        language: str = "en",
        stream: bool = False,
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
        self.api_key = api_key or os.getenv("ELEVEN_LABS_API_KEY")
        
        if not HTTPX_AVAILABLE:
            logger.warning("httpx not available for ElevenLabs transcriber")
    
    async def connect(self) -> None:
        """Establish connection."""
        if not self.api_key:
            logger.warning("ElevenLabs API key not configured")
        self._is_connected = True
        logger.info("ElevenLabs transcriber connected")
    
    async def disconnect(self) -> None:
        """Close connection."""
        self._is_connected = False
        logger.info("ElevenLabs transcriber disconnected")
    
    async def transcribe(self, audio_chunk: bytes) -> Optional[str]:
        """
        Transcribe audio to text.
        
        Args:
            audio_chunk: Audio bytes
            
        Returns:
            Transcribed text or None
        """
        if not self.api_key:
            logger.error("ElevenLabs API key not configured")
            return None
        
        if not HTTPX_AVAILABLE:
            logger.error("httpx required for ElevenLabs transcriber")
            return None
        
        if not audio_chunk:
            return None
        
        headers = {
            "xi-api-key": self.api_key,
        }
        
        files = {
            "file": ("audio.wav", audio_chunk, "audio/wav"),
            "model_id": (None, self.model),
            "language_code": (None, self.language),
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
                    
                    await self._output_queue.put({
                        "text": text,
                        "is_final": True,
                        "confidence": 1.0,
                    })
                    
                    return text
                else:
                    logger.error(f"ElevenLabs API error: {response.status_code}")
                    return None
        
        except Exception as e:
            logger.error(f"ElevenLabs transcription error: {e}")
            return None
    
    async def transcribe_stream(
        self, 
        audio_stream: AsyncIterator[bytes]
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Transcribe a stream of audio chunks.
        
        Args:
            audio_stream: Async iterator of audio bytes
            
        Yields:
            Transcription result dicts
        """
        audio_buffer = b""
        buffer_duration_ms = 0
        
        async for chunk in audio_stream:
            audio_buffer += chunk
            buffer_duration_ms += 100
            
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
        return "elevenlabs"
