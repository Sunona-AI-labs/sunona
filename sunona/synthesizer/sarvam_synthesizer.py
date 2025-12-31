"""
Sunona Voice AI - Sarvam AI Synthesizer

Indian language text-to-speech provider.
Specialized for Hindi, Tamil, Telugu, Bengali, and more.
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


class SarvamSynthesizer(BaseSynthesizer):
    """
    Sarvam AI Text-to-Speech Synthesizer.
    
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
        synth = SarvamSynthesizer(
            api_key=None,  # Falls back to os.getenv("SARVAM_API_KEY")
            language="hi-IN",
        )
        
        audio = await synth.synthesize("नमस्ते")
        ```
    """
    
    BASE_URL = "https://api.sarvam.ai/v1/text-to-speech"
    
    # Supported languages
    SUPPORTED_LANGUAGES = [
        "hi-IN", "ta-IN", "te-IN", "bn-IN", "kn-IN",
        "ml-IN", "mr-IN", "gu-IN", "pa-IN", "en-IN"
    ]
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        voice_id: str = "meera",
        voice: str = "meera",
        model: str = "bulbul:v1",
        language: str = "hi-IN",
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
        self.api_key = api_key or os.getenv("SARVAM_API_KEY")
        self.language = language
        self.speed = speed
        
        if language not in self.SUPPORTED_LANGUAGES:
            logger.warning(f"Language {language} may not be fully supported")
        
        if not HTTPX_AVAILABLE:
            logger.warning("httpx not available for Sarvam synthesizer")
    
    async def connect(self) -> None:
        """Establish connection."""
        if not self.api_key:
            logger.warning("Sarvam API key not configured")
        self._is_connected = True
        logger.info(f"Sarvam synthesizer connected (language: {self.language})")
    
    async def disconnect(self) -> None:
        """Close connection."""
        self._is_connected = False
        logger.info("Sarvam synthesizer disconnected")
    
    async def synthesize(self, text: str) -> bytes:
        """
        Synthesize text to speech.
        
        Args:
            text: Text to synthesize (in supported language)
            
        Returns:
            Audio bytes
        """
        if not self.api_key:
            logger.error("Sarvam API key not configured")
            return b""
        
        if not HTTPX_AVAILABLE:
            logger.error("httpx required for Sarvam synthesizer")
            return b""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "text": text,
            "target_language_code": self.language,
            "speaker": self.voice_id,
            "model": self.model,
            "speed": self.speed,
            "enable_preprocessing": True,
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
                    # Sarvam returns base64 encoded audio
                    import base64
                    audio_b64 = result.get("audio", "")
                    return base64.b64decode(audio_b64)
                else:
                    logger.error(f"Sarvam API error: {response.status_code}")
                    return b""
        
        except Exception as e:
            logger.error(f"Sarvam synthesis error: {e}")
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
        return "sarvam"
    
    def supports_language(self, language: str) -> bool:
        """Check if language is supported."""
        return language in self.SUPPORTED_LANGUAGES
