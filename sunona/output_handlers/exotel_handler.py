"""
Sunona Voice AI - Exotel Output Handler

Handles sending audio to Exotel streams.
"""

import asyncio
import base64
import json
import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)


class ExotelOutputHandler:
    """
    Exotel audio stream output handler.
    
    Sends audio data back to Exotel via WebSocket.
    
    Example:
        ```python
        handler = ExotelOutputHandler(stream_id="...")
        
        await handler.send_audio(websocket, audio_bytes)
        ```
    """
    
    def __init__(
        self,
        stream_id: Optional[str] = None,
        sample_rate: int = 8000,
        encoding: str = "linear16",
        **kwargs,
    ):
        self.stream_id = stream_id
        self.sample_rate = sample_rate
        self.encoding = encoding
    
    def set_stream_id(self, stream_id: str):
        """Set the stream ID."""
        self.stream_id = stream_id
    
    async def send_audio(
        self,
        websocket,
        audio_bytes: bytes,
    ):
        """
        Send audio data to Exotel.
        
        Args:
            websocket: WebSocket connection
            audio_bytes: Audio data to send
        """
        if not self.stream_id:
            logger.error("Stream ID not set")
            return
        
        if not audio_bytes:
            return
        
        # Encode audio to base64
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        
        # Build Exotel media message
        message = {
            "event": "media",
            "streamId": self.stream_id,
            "media": {
                "payload": audio_b64,
            },
        }
        
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending audio to Exotel: {e}")
    
    async def clear_audio(self, websocket):
        """
        Clear queued audio.
        
        Args:
            websocket: WebSocket connection
        """
        message = {
            "event": "clear",
            "streamId": self.stream_id,
        }
        
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error clearing Exotel audio: {e}")
    
    async def send_chunks(
        self,
        websocket,
        audio_generator,
        chunk_size: int = 640,
    ):
        """
        Send audio in chunks from a generator.
        
        Args:
            websocket: WebSocket connection
            audio_generator: Async generator yielding audio bytes
            chunk_size: Size of each chunk
        """
        try:
            async for audio_chunk in audio_generator:
                if audio_chunk:
                    for i in range(0, len(audio_chunk), chunk_size):
                        chunk = audio_chunk[i:i + chunk_size]
                        await self.send_audio(websocket, chunk)
        except Exception as e:
            logger.error(f"Error streaming audio: {e}")
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return "exotel"
