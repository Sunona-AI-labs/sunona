"""
Sunona Voice AI - Rime Synthesizer

Rime AI text-to-speech provider.
High-quality, low-latency voice synthesis.
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


class RimeSynthesizer(BaseSynthesizer):
    """
    Rime AI Text-to-Speech Synthesizer.
    
    Features:
    - High-quality neural voices
    - Low latency streaming
    - Multiple voice options
    
    Example:
        ```python
        synth = RimeSynthesizer(
            api_key=None,  # Falls back to os.getenv("RIME_API_KEY")
            voice_id="mist_v1",
        )
        
        async for chunk in synth.synthesize_stream(text_iter):
            # Process audio chunk
            pass
        ```
    """
    
    BASE_URL = "https://api.rime.ai/v1/tts"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        voice_id: str = "mist_v1",
        voice: str = "mist",
        model: str = "mist",
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
        self.api_key = api_key or os.getenv("RIME_API_KEY")
        self.language = language
        self.speed = speed
        
        if not HTTPX_AVAILABLE:
            logger.warning("httpx not available for Rime synthesizer")
    
    async def connect(self) -> None:
        """Establish connection."""
        if not self.api_key:
            logger.warning("Rime API key not configured")
        self._is_connected = True
        logger.info("Rime synthesizer connected")
    
    async def disconnect(self) -> None:
        """Close connection."""
        self._is_connected = False
        logger.info("Rime synthesizer disconnected")
    
    async def synthesize(self, text: str) -> bytes:
        """
        Synthesize text to speech.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio bytes
        """
        if not self.api_key:
            logger.error("Rime API key not configured")
            return b""
        
        if not HTTPX_AVAILABLE:
            logger.error("httpx required for Rime synthesizer")
            return b""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "text": text,
            "voice": self.voice_id,
            "model": self.model,
            "language": self.language,
            "speed": self.speed,
            "output_format": self.audio_format,
            "sample_rate": self.sample_rate,
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
                    logger.error(f"Rime API error: {response.status_code}")
                    return b""
        
        except Exception as e:
            logger.error(f"Rime synthesis error: {e}")
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
        if not self.api_key or not HTTPX_AVAILABLE:
            return
        
        async for text in text_stream:
            audio = await self.synthesize(text)
            if audio:
                yield audio
    
    async def speak(self, text: str) -> AsyncIterator[bytes]:
        """
        Convenience method to speak text with streaming.
        
        Args:
            text: Text to speak
            
        Yields:
            Audio chunks
        """
        if not self.api_key or not HTTPX_AVAILABLE:
            return
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "text": text,
            "voice": self.voice_id,
            "model": self.model,
            "language": self.language,
            "speed": self.speed,
            "output_format": self.audio_format,
            "sample_rate": self.sample_rate,
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if self.stream:
                    async with client.stream(
                        "POST",
                        self.BASE_URL,
                        headers=headers,
                        json=payload,
                    ) as response:
                        if response.status_code != 200:
                            logger.error(f"Rime API error: {response.status_code}")
                            return
                        
                        async for chunk in response.aiter_bytes(chunk_size=1024):
                            yield chunk
                else:
                    audio = await self.synthesize(text)
                    if audio:
                        yield audio
        
        except Exception as e:
            logger.error(f"Rime streaming error: {e}")
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return "rime"
