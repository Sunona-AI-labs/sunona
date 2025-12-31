"""
Sunona Voice AI - Cartesia Synthesizer

Cartesia Sonic TTS - fastest real-time voice synthesis.
"""

import os
import asyncio
import logging
import httpx
from typing import AsyncIterator, Optional

logger = logging.getLogger(__name__)


class CartesiaSynthesizer:
    """
    Cartesia Sonic ultra-low latency TTS.
    
    Sub-100ms latency for real-time conversations.
    
    Example:
        ```python
        synth = CartesiaSynthesizer()
        async for chunk in synth.synthesize_stream("Hello"):
            player.play(chunk)
        ```
    """
    
    VOICES = {
        "professional_male": "694f9389-aac1-45b6-b726-9d9369183238",
        "professional_female": "156fb8d2-335b-4950-9cb3-a2d33befec77",
        "friendly_male": "820a3788-2b37-4d21-847a-b65d8a68c99a",
        "friendly_female": "5345cf08-6f37-424d-a5d9-8ae1f1e5e303",
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        voice: str = "professional_female",
        model: str = "sonic-english",
        speed: float = 1.0,
        output_format: str = "pcm_16000",
    ):
        self.api_key = api_key or os.getenv("CARTESIA_API_KEY")
        if not self.api_key:
            raise ValueError("CARTESIA_API_KEY required")
        
        self.voice_id = self.VOICES.get(voice, voice)
        self.model = model
        self.speed = speed
        self.output_format = output_format
        
        self._client = httpx.AsyncClient(
            base_url="https://api.cartesia.ai",
            headers={
                "X-API-Key": self.api_key,
                "Cartesia-Version": "2024-06-10",
            },
            timeout=30.0,
        )
        
        logger.info("Cartesia synthesizer initialized")
    
    async def synthesize_stream(self, text: str) -> AsyncIterator[bytes]:
        """Ultra-low latency streaming synthesis."""
        async with self._client.stream(
            "POST",
            "/tts/bytes",
            json={
                "model_id": self.model,
                "transcript": text,
                "voice": {
                    "mode": "id",
                    "id": self.voice_id,
                },
                "output_format": {
                    "container": "raw",
                    "encoding": "pcm_s16le",
                    "sample_rate": 16000,
                },
            },
        ) as response:
            response.raise_for_status()
            async for chunk in response.aiter_bytes(chunk_size=1024):
                yield chunk
    
    async def synthesize(self, text: str) -> bytes:
        """Synthesize complete audio."""
        chunks = []
        async for chunk in self.synthesize_stream(text):
            chunks.append(chunk)
        return b"".join(chunks)
    
    async def close(self):
        """Close client."""
        await self._client.aclose()
