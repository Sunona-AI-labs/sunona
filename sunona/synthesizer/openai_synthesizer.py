"""
Sunona Voice AI - OpenAI TTS Synthesizer

High-quality text-to-speech using OpenAI's TTS API.
Optimized for low-latency streaming voice synthesis.

Features:
- HD quality with tts-1-hd model
- Multiple voice options (alloy, echo, fable, onyx, nova, shimmer)
- Real-time streaming output
- Speed control (0.25x to 4.0x)
- Multiple output formats (mp3, opus, aac, flac, wav, pcm)
"""

import os
import asyncio
import logging
from typing import AsyncIterator, Optional, Dict, Any

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncOpenAI = None

from sunona.synthesizer.base_synthesizer import BaseSynthesizer

logger = logging.getLogger(__name__)


class OpenAISynthesizer(BaseSynthesizer):
    """
    OpenAI TTS synthesizer for high-quality voice synthesis.
    
    Supports streaming output in multiple formats with configurable
    voice and speed settings.
    
    Example:
        ```python
        synth = OpenAISynthesizer(voice="nova")
        
        async with synth:
            async for audio_chunk in synth.synthesize_stream(text_stream):
                play_audio(audio_chunk)
        ```
    """
    
    # Available voices with characteristics
    VOICES = {
        "alloy": {"gender": "neutral", "description": "Balanced and versatile"},
        "echo": {"gender": "male", "description": "Warm and engaging"},
        "fable": {"gender": "neutral", "description": "Storytelling quality"},
        "onyx": {"gender": "male", "description": "Deep and authoritative"},
        "nova": {"gender": "female", "description": "Friendly and conversational"},
        "shimmer": {"gender": "female", "description": "Clear and expressive"},
    }
    
    MODELS = {
        "tts-1": {"quality": "standard", "latency": "low"},
        "tts-1-hd": {"quality": "high", "latency": "higher"},
    }
    
    SUPPORTED_FORMATS = ["mp3", "opus", "aac", "flac", "wav", "pcm"]
    
    def __init__(
        self,
        voice: str = "nova",
        voice_id: str = "nova",
        model: str = "tts-1",
        stream: bool = True,
        audio_format: str = "pcm",
        sample_rate: int = 24000,
        buffer_size: int = 40,
        api_key: Optional[str] = None,
        speed: float = 1.0,
        **kwargs
    ):
        """
        Initialize the OpenAI TTS synthesizer.
        
        Args:
            voice: Voice name (alloy, echo, fable, onyx, nova, shimmer)
            voice_id: Voice identifier (same as voice for OpenAI)
            model: TTS model (tts-1, tts-1-hd)
            stream: Whether to stream audio output
            audio_format: Output format (mp3, opus, aac, flac, wav, pcm)
            sample_rate: Output sample rate (only for pcm)
            buffer_size: Text buffer size before synthesis
            api_key: OpenAI API key (or OPENAI_API_KEY env var)
            speed: Speech speed (0.25 to 4.0)
            **kwargs: Additional options
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "openai is required for OpenAISynthesizer. "
                "Install with: pip install openai"
            )
        
        # Normalize voice
        voice = voice.lower()
        if voice not in self.VOICES:
            logger.warning(f"Unknown voice '{voice}', defaulting to 'nova'")
            voice = "nova"
        
        super().__init__(
            voice=voice,
            voice_id=voice,
            model=model,
            stream=stream,
            audio_format=audio_format,
            sample_rate=sample_rate,
            buffer_size=buffer_size,
            **kwargs
        )
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.speed = max(0.25, min(4.0, speed))  # Clamp to valid range
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        # Validate audio format
        if audio_format not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported audio format: {audio_format}. "
                f"Supported: {self.SUPPORTED_FORMATS}"
            )
        
        self._client: Optional[AsyncOpenAI] = None
        
        logger.info(f"OpenAI TTS initialized (voice: {voice}, model: {model})")
    
    async def connect(self) -> None:
        """Initialize the OpenAI client."""
        if not self._is_connected:
            self._client = AsyncOpenAI(api_key=self.api_key)
            self._is_connected = True
            logger.debug("OpenAI TTS connected")
    
    async def disconnect(self) -> None:
        """Close the OpenAI client."""
        if self._is_connected:
            if self._client:
                await self._client.close()
                self._client = None
            self._is_connected = False
            logger.debug("OpenAI TTS disconnected")
    
    async def synthesize(self, text: str) -> bytes:
        """
        Synthesize text to audio.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio bytes in configured format
        """
        if not self._is_connected:
            await self.connect()
        
        if not text or not text.strip():
            return b""
        
        try:
            response = await self._client.audio.speech.create(
                model=self.model,
                voice=self.voice,
                input=text,
                response_format=self.audio_format,
                speed=self.speed,
            )
            
            # Read all audio data
            audio_data = b""
            async for chunk in response.iter_bytes():
                audio_data += chunk
            
            return audio_data
            
        except Exception as e:
            logger.error(f"OpenAI TTS synthesis error: {e}")
            return b""
    
    async def synthesize_stream(
        self, 
        text_stream: AsyncIterator[str]
    ) -> AsyncIterator[bytes]:
        """
        Stream synthesis of text chunks.
        
        Uses buffering to optimize API calls while maintaining low latency.
        
        Args:
            text_stream: Async iterator of text chunks
            
        Yields:
            Audio bytes chunks
        """
        if not self._is_connected:
            await self.connect()
        
        async for text_chunk in text_stream:
            # Add to buffer and check if ready
            buffered = self.add_to_buffer(text_chunk)
            
            if buffered:
                # Synthesize buffered text
                async for audio in self._synthesize_with_streaming(buffered):
                    yield audio
        
        # Flush remaining buffer
        remaining = self.flush_buffer()
        if remaining:
            async for audio in self._synthesize_with_streaming(remaining):
                yield audio
    
    async def _synthesize_with_streaming(self, text: str) -> AsyncIterator[bytes]:
        """Synthesize text and stream audio chunks."""
        if not text or not text.strip():
            return
        
        try:
            response = await self._client.audio.speech.create(
                model=self.model,
                voice=self.voice,
                input=text,
                response_format=self.audio_format,
                speed=self.speed,
            )
            
            # Stream response bytes
            async for chunk in response.iter_bytes(chunk_size=4096):
                if chunk:
                    yield chunk
                    
        except Exception as e:
            logger.error(f"OpenAI TTS streaming error: {e}")
    
    async def synthesize_to_file(self, text: str, file_path: str) -> None:
        """
        Synthesize text and save to file.
        
        Args:
            text: Text to synthesize
            file_path: Output file path
        """
        audio_data = await self.synthesize(text)
        
        with open(file_path, "wb") as f:
            f.write(audio_data)
        
        logger.info(f"Audio saved to {file_path}")
    
    def set_speed(self, speed: float) -> None:
        """Set speech speed (0.25 to 4.0)."""
        self.speed = max(0.25, min(4.0, speed))
    
    @classmethod
    def list_voices(cls) -> Dict[str, Dict[str, str]]:
        """List available voices with descriptions."""
        return cls.VOICES.copy()
    
    @classmethod
    def list_models(cls) -> Dict[str, Dict[str, str]]:
        """List available models with characteristics."""
        return cls.MODELS.copy()
