"""
Sunona Voice AI - Deepgram Aura TTS Synthesizer

High-performance text-to-speech using Deepgram's Aura API.
Optimized for real-time streaming with ultra-low latency.

Features:
- Ultra-low latency streaming
- Multiple voice models
- Natural-sounding speech
- WebSocket streaming support
- PCM audio output
"""

import os
import asyncio
import logging
from typing import AsyncIterator, Optional, Dict, Any

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    httpx = None

from sunona.synthesizer.base_synthesizer import BaseSynthesizer

logger = logging.getLogger(__name__)


class DeepgramSynthesizer(BaseSynthesizer):
    """
    Deepgram Aura TTS synthesizer for ultra-low latency synthesis.
    
    Uses Deepgram's streaming TTS API for real-time voice synthesis
    with minimal delay.
    
    Example:
        ```python
        synth = DeepgramSynthesizer(voice_id="aura-asteria-en")
        
        async with synth:
            audio = await synth.synthesize("Hello, world!")
            play_audio(audio)
        ```
    """
    
    # Available Aura voices
    VOICES = {
        "aura-asteria-en": {"gender": "female", "accent": "US", "description": "Warm and conversational"},
        "aura-luna-en": {"gender": "female", "accent": "US", "description": "Friendly and bright"},
        "aura-stella-en": {"gender": "female", "accent": "US", "description": "Professional and clear"},
        "aura-athena-en": {"gender": "female", "accent": "UK", "description": "Refined British accent"},
        "aura-hera-en": {"gender": "female", "accent": "US", "description": "Authoritative and confident"},
        "aura-orion-en": {"gender": "male", "accent": "US", "description": "Deep and engaging"},
        "aura-arcas-en": {"gender": "male", "accent": "US", "description": "Warm and approachable"},
        "aura-perseus-en": {"gender": "male", "accent": "US", "description": "Energetic and dynamic"},
        "aura-angus-en": {"gender": "male", "accent": "Ireland", "description": "Gentle Irish accent"},
        "aura-orpheus-en": {"gender": "male", "accent": "US", "description": "Smooth and calming"},
        "aura-helios-en": {"gender": "male", "accent": "UK", "description": "Classic British accent"},
        "aura-zeus-en": {"gender": "male", "accent": "US", "description": "Commanding and powerful"},
    }
    
    BASE_URL = "https://api.deepgram.com/v1/speak"
    
    def __init__(
        self,
        voice: str = "asteria",
        voice_id: str = "aura-asteria-en",
        model: str = "aura",
        stream: bool = True,
        audio_format: str = "linear16",
        sample_rate: int = 24000,
        buffer_size: int = 40,
        api_key: Optional[str] = None,
        encoding: str = "linear16",
        container: str = "none",
        **kwargs
    ):
        """
        Initialize the Deepgram TTS synthesizer.
        
        Args:
            voice: Voice name shorthand
            voice_id: Full voice ID (e.g., "aura-asteria-en")
            model: Model name (aura)
            stream: Whether to stream audio output
            audio_format: Output format (linear16, mp3, opus, flac)
            sample_rate: Output sample rate
            buffer_size: Text buffer size before synthesis
            api_key: Deepgram API key (or DEEPGRAM_API_KEY env var)
            encoding: Audio encoding (linear16, mulaw, alaw, mp3, opus, flac)
            container: Container format (none, wav, mp3, ogg)
            **kwargs: Additional options
        """
        if not HTTPX_AVAILABLE:
            raise ImportError(
                "httpx is required for DeepgramSynthesizer. "
                "Install with: pip install httpx"
            )
        
        # Build voice_id from voice name if needed
        if not voice_id.startswith("aura-"):
            voice_id = f"aura-{voice}-en"
        
        super().__init__(
            voice=voice,
            voice_id=voice_id,
            model=model,
            stream=stream,
            audio_format=audio_format,
            sample_rate=sample_rate,
            buffer_size=buffer_size,
            **kwargs
        )
        
        self.api_key = api_key or os.getenv("DEEPGRAM_API_KEY")
        self.encoding = encoding
        self.container = container
        
        if not self.api_key:
            raise ValueError(
                "Deepgram API key required. Set DEEPGRAM_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self._client: Optional[httpx.AsyncClient] = None
        
        logger.info(f"Deepgram TTS initialized (voice: {voice_id})")
    
    async def connect(self) -> None:
        """Initialize the HTTP client."""
        if not self._is_connected:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                limits=httpx.Limits(max_keepalive_connections=5)
            )
            self._is_connected = True
            logger.debug("Deepgram TTS connected")
    
    async def disconnect(self) -> None:
        """Close the HTTP client."""
        if self._is_connected:
            if self._client:
                await self._client.aclose()
                self._client = None
            self._is_connected = False
            logger.debug("Deepgram TTS disconnected")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        return {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json",
        }
    
    def _build_url(self) -> str:
        """Build the API URL with query parameters."""
        params = [
            f"model={self.voice_id}",
            f"encoding={self.encoding}",
            f"sample_rate={self.sample_rate}",
        ]
        
        if self.container != "none":
            params.append(f"container={self.container}")
        
        return f"{self.BASE_URL}?{'&'.join(params)}"
    
    async def synthesize(self, text: str) -> bytes:
        """
        Synthesize text to audio.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio bytes
        """
        if not self._is_connected:
            await self.connect()
        
        if not text or not text.strip():
            return b""
        
        try:
            url = self._build_url()
            
            response = await self._client.post(
                url,
                headers=self._get_headers(),
                json={"text": text},
            )
            
            if response.status_code != 200:
                logger.error(f"Deepgram TTS error: {response.status_code} - {response.text}")
                return b""
            
            return response.content
            
        except Exception as e:
            logger.error(f"Deepgram TTS synthesis error: {e}")
            return b""
    
    async def synthesize_stream(
        self, 
        text_stream: AsyncIterator[str]
    ) -> AsyncIterator[bytes]:
        """
        Stream synthesis of text chunks.
        
        Buffers text and streams audio for optimal latency.
        
        Args:
            text_stream: Async iterator of text chunks
            
        Yields:
            Audio bytes chunks
        """
        if not self._is_connected:
            await self.connect()
        
        async for text_chunk in text_stream:
            buffered = self.add_to_buffer(text_chunk)
            
            if buffered:
                async for audio in self._synthesize_streaming(buffered):
                    yield audio
        
        remaining = self.flush_buffer()
        if remaining:
            async for audio in self._synthesize_streaming(remaining):
                yield audio
    
    async def _synthesize_streaming(self, text: str) -> AsyncIterator[bytes]:
        """Synthesize text and stream chunks."""
        if not text or not text.strip():
            return
        
        try:
            url = self._build_url()
            
            async with self._client.stream(
                "POST",
                url,
                headers=self._get_headers(),
                json={"text": text},
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    logger.error(f"Deepgram TTS streaming error: {response.status_code} - {error_text}")
                    return
                
                async for chunk in response.aiter_bytes(chunk_size=4096):
                    if chunk:
                        yield chunk
                        
        except Exception as e:
            logger.error(f"Deepgram TTS streaming error: {e}")
    
    @classmethod
    def list_voices(cls) -> Dict[str, Dict[str, str]]:
        """List available voices with descriptions."""
        return cls.VOICES.copy()
    
    @classmethod
    def get_voice_info(cls, voice_id: str) -> Optional[Dict[str, str]]:
        """Get information about a specific voice."""
        return cls.VOICES.get(voice_id)
