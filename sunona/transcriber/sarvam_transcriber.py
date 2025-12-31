"""
Sunona Voice AI - Sarvam AI Transcriber

Indian language speech-to-text provider.
Specialized for Hindi, Tamil, Telugu, Bengali, and more.
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


class SarvamTranscriber(BaseTranscriber):
    """
    Sarvam AI Speech-to-Text Transcriber.
    
    Specialized for Indian languages:
    - Hindi (hi-IN)
    - Tamil (ta-IN)
    - Telugu (te-IN)
    - Bengali (bn-IN)
    - Kannada (kn-IN)
    - Malayalam (ml-IN)
    - Marathi (mr-IN)
    - Gujarati (gu-IN)
    - Punjabi (pa-IN)
    
    Example:
        ```python
        transcriber = SarvamTranscriber(
            api_key=None,  # Falls back to os.getenv("SARVAM_API_KEY")
            language="hi-IN",
        )
        
        async with transcriber:
            text = await transcriber.transcribe(audio_bytes)
        ```
    """
    
    BASE_URL = "https://api.sarvam.ai/v1/speech-to-text"
    
    SUPPORTED_LANGUAGES = [
        "hi-IN", "ta-IN", "te-IN", "bn-IN", "kn-IN",
        "ml-IN", "mr-IN", "gu-IN", "pa-IN", "en-IN"
    ]
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "saarika:v1",
        language: str = "hi-IN",
        stream: bool = False,
        sampling_rate: int = 16000,
        encoding: str = "linear16",
        endpointing: int = 500,
        with_timestamps: bool = False,
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
        self.api_key = api_key or os.getenv("SARVAM_API_KEY")
        self.with_timestamps = with_timestamps
        
        if language not in self.SUPPORTED_LANGUAGES:
            logger.warning(f"Language {language} may not be fully supported")
        
        if not HTTPX_AVAILABLE:
            logger.warning("httpx not available for Sarvam transcriber")
    
    async def connect(self) -> None:
        """Establish connection."""
        if not self.api_key:
            logger.warning("Sarvam API key not configured")
        self._is_connected = True
        logger.info(f"Sarvam transcriber connected (language: {self.language})")
    
    async def disconnect(self) -> None:
        """Close connection."""
        self._is_connected = False
        logger.info("Sarvam transcriber disconnected")
    
    async def transcribe(self, audio_chunk: bytes) -> Optional[str]:
        """
        Transcribe audio to text.
        
        Args:
            audio_chunk: Audio bytes
            
        Returns:
            Transcribed text or None
        """
        if not self.api_key:
            logger.error("Sarvam API key not configured")
            return None
        
        if not HTTPX_AVAILABLE:
            logger.error("httpx required for Sarvam transcriber")
            return None
        
        if not audio_chunk:
            return None
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        
        import base64
        audio_b64 = base64.b64encode(audio_chunk).decode()
        
        payload = {
            "audio_content": audio_b64,
            "model": self.model,
            "language_code": self.language,
            "with_timestamps": self.with_timestamps,
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.BASE_URL,
                    headers=headers,
                    json=payload,
                )
                
                if response.status_code == 200:
                    result = response.json()
                    text = result.get("transcript", "")
                    
                    await self._output_queue.put({
                        "text": text,
                        "is_final": True,
                        "confidence": result.get("confidence", 1.0),
                    })
                    
                    return text
                else:
                    logger.error(f"Sarvam API error: {response.status_code}")
                    return None
        
        except Exception as e:
            logger.error(f"Sarvam transcription error: {e}")
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
        return "sarvam"
    
    def supports_language(self, language: str) -> bool:
        """Check if language is supported."""
        return language in self.SUPPORTED_LANGUAGES
