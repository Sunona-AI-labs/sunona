"""
Sunona Voice AI - PlayHT Synthesizer

PlayHT TTS with ultra-realistic voice cloning.
"""

import os
import asyncio
import logging
from typing import AsyncIterator, Optional

logger = logging.getLogger(__name__)

try:
    from pyht import Client as PlayHTClient
    from pyht.client import TTSOptions
    PLAYHT_AVAILABLE = True
except ImportError:
    PLAYHT_AVAILABLE = False


class PlayHTSynthesizer:
    """
    PlayHT TTS with voice cloning and streaming.
    
    Features:
        - Ultra-realistic voices
        - Voice cloning
        - Streaming output
        - Multiple formats
    
    Example:
        ```python
        synth = PlayHTSynthesizer()
        async for chunk in synth.synthesize_stream("Hello world"):
            audio_player.play(chunk)
        ```
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        user_id: Optional[str] = None,
        voice: str = "s3://voice-cloning-zero-shot/775ae416-49bb-4fb6-bd45-740f205d0a29/sadfasdf/manifest.json",
        speed: float = 1.0,
        quality: str = "high",
    ):
        if not PLAYHT_AVAILABLE:
            raise ImportError("pyht package required: pip install pyht")
        
        self.api_key = api_key or os.getenv("PLAYHT_API_KEY")
        self.user_id = user_id or os.getenv("PLAYHT_USER_ID")
        
        if not self.api_key or not self.user_id:
            raise ValueError("PLAYHT_API_KEY and PLAYHT_USER_ID required")
        
        self._client = PlayHTClient(self.user_id, self.api_key)
        self.voice = voice
        self.speed = speed
        self.quality = quality
        
        logger.info("PlayHT synthesizer initialized")
    
    async def synthesize_stream(self, text: str) -> AsyncIterator[bytes]:
        """Stream synthesize text to audio."""
        options = TTSOptions(
            voice=self.voice,
            speed=self.speed,
            quality=self.quality,
        )
        
        loop = asyncio.get_event_loop()
        
        def _generate():
            return list(self._client.tts(text, options))
        
        chunks = await loop.run_in_executor(None, _generate)
        for chunk in chunks:
            yield chunk
    
    async def synthesize(self, text: str) -> bytes:
        """Synthesize text to complete audio."""
        chunks = []
        async for chunk in self.synthesize_stream(text):
            chunks.append(chunk)
        return b"".join(chunks)
    
    async def clone_voice(self, audio_file: str, voice_name: str) -> str:
        """Clone a voice from audio sample."""
        # PlayHT voice cloning API
        loop = asyncio.get_event_loop()
        
        def _clone():
            return self._client.clone_voice(audio_file, voice_name)
        
        voice_id = await loop.run_in_executor(None, _clone)
        return voice_id
