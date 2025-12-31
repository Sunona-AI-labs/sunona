"""
Sunona Voice AI - Smallest AI Synthesizer

Ultra-fast, low-cost text-to-speech provider.
"""

import asyncio
import logging
import os
from typing import AsyncIterator, Dict, Optional, Any

from sunona.synthesizer.base_synthesizer import BaseSynthesizer

logger = logging.getLogger(__name__)

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class SmallestSynthesizer(BaseSynthesizer):
    """
    Smallest AI Text-to-Speech Synthesizer.
    
    Features:
    - Ultra-fast synthesis
    - Low cost
    - Multiple voice options
    
    Example:
        ```python
        synth = SmallestSynthesizer(
            api_key=None,  # Falls back to os.getenv("SMALLEST_API_KEY")
            voice_id="emily",
        )
        
        audio = await synth.synthesize("Hello world")
        ```
    """
    
    BASE_URL = "https://api.smallest.ai/v1/tts"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        voice_id: str = "emily",
        voice: str = "emily",
        model: str = "lightning",
        language: str = "en",
        speed: float = 1.0,
        stream: bool = True,
        audio_format: str = "pcm",
        sample_rate: int = 16000,
        **kwargs,
    ):
        super().__init__(
            voice=voice,
            voice_id=voice_id,
            model=model,
            stream=stream,
            audio_format=audio_format,
            sample_rate=sample_rate,
            **kwargs,
        )
        self.api_key = api_key or os.getenv("SMALLEST_API_KEY")
        self.language = language
        self.speed = speed
        
        if not HTTPX_AVAILABLE:
            logger.warning("httpx not available for Smallest synthesizer")
    
    async def connect(self) -> None:
        """Establish connection."""
        if not self.api_key:
            logger.warning("Smallest API key not configured")
        self._is_connected = True
        logger.info("Smallest synthesizer connected")
    
    async def disconnect(self) -> None:
        """Close connection."""
        self._is_connected = False
        logger.info("Smallest synthesizer disconnected")
    
    async def synthesize(self, text: str) -> bytes:
        """
        Synthesize text to speech.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio bytes
        """
        if not self.api_key:
            logger.error("Smallest API key not configured")
            return b""
        
        if not HTTPX_AVAILABLE:
            logger.error("httpx required for Smallest synthesizer")
            return b""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "text": text,
            "voice_id": self.voice_id,
            "model": self.model,
            "language": self.language,
            "speed": self.speed,
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.BASE_URL,
                    headers=headers,
                    json=payload,
                )
                
                if response.status_code == 200:
                    return response.content
                else:
                    logger.error(f"Smallest API error: {response.status_code}")
                    return b""
        
        except Exception as e:
            logger.error(f"Smallest synthesis error: {e}")
            return b""
    
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
        async for text in text_stream:
            audio = await self.synthesize(text)
            if audio:
                yield audio
    
    async def speak(self, text: str) -> AsyncIterator[bytes]:
        """
        Convenience method to speak text.
        
        Args:
            text: Text to speak
            
        Yields:
            Audio chunks
        """
        audio = await self.synthesize(text)
        if audio:
            yield audio
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return "smallest"
