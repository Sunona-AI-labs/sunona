"""
Sunona Voice AI - Pixa Transcriber

Pixa transcription provider.
"""

import asyncio
import logging
import os
from typing import AsyncGenerator, Dict, Optional, Any, Callable

logger = logging.getLogger(__name__)

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class PixaTranscriber:
    """
    Pixa Speech-to-Text Transcriber.
    
    Example:
        ```python
        transcriber = PixaTranscriber(
            api_key=None,  # Falls back to os.getenv("PIXA_API_KEY")
        )
        
        result = await transcriber.transcribe(audio_data)
        ```
    """
    
    BASE_URL = "https://api.pixa.ai/v1/transcribe"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        language: str = "en",
        model: str = "default",
        sample_rate: int = 16000,
        encoding: str = "linear16",
        **kwargs,
    ):
        self.api_key = api_key or os.getenv("PIXA_API_KEY")
        self.language = language
        self.model = model
        self.sample_rate = sample_rate
        self.encoding = encoding
        
        self._callback: Optional[Callable] = None
        self._is_running = False
    
    def set_callback(self, callback: Callable):
        """Set callback for transcription results."""
        self._callback = callback
    
    async def transcribe(
        self,
        audio_data: bytes,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Transcribe audio data.
        
        Args:
            audio_data: Audio bytes to transcribe
            
        Returns:
            Transcription result
        """
        if not self.api_key:
            logger.error("Pixa API key not configured")
            return {"text": "", "error": "API key not configured"}
        
        if not HTTPX_AVAILABLE:
            logger.error("httpx required for Pixa transcriber")
            return {"text": "", "error": "httpx not installed"}
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        
        files = {
            "audio": ("audio.wav", audio_data, "audio/wav"),
        }
        
        data = {
            "language": self.language,
            "model": self.model,
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.BASE_URL,
                    headers=headers,
                    files=files,
                    data=data,
                )
                
                if response.status_code == 200:
                    result = response.json()
                    text = result.get("text", result.get("transcription", ""))
                    
                    return {
                        "text": text,
                        "language": self.language,
                        "is_final": True,
                    }
                else:
                    logger.error(f"Pixa API error: {response.status_code}")
                    return {"text": "", "error": f"API error: {response.status_code}"}
        
        except Exception as e:
            logger.error(f"Pixa transcription error: {e}")
            return {"text": "", "error": str(e)}
    
    async def start_streaming(self):
        """Start streaming mode."""
        self._is_running = True
        logger.info("Pixa transcriber started")
    
    async def stop_streaming(self):
        """Stop streaming mode."""
        self._is_running = False
        logger.info("Pixa transcriber stopped")
    
    async def process_audio(self, audio_chunk: bytes):
        """Process audio chunk."""
        if not self._is_running:
            return
        
        result = await self.transcribe(audio_chunk)
        
        if self._callback and result.get("text"):
            await self._callback(result)
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return "pixa"
