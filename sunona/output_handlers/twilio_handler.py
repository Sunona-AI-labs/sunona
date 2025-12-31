"""
Sunona Voice AI - Twilio Output Handler

Handles sending audio to Twilio Media Streams.
"""

import asyncio
import base64
import json
import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)


class TwilioOutputHandler:
    """
    Twilio Media Streams output handler.
    
    Sends audio data back to Twilio via WebSocket.
    
    Example:
        ```python
        handler = TwilioOutputHandler(stream_sid="MS...")
        
        await handler.send_audio(websocket, audio_bytes)
        ```
    """
    
    def __init__(
        self,
        stream_sid: Optional[str] = None,
        sample_rate: int = 8000,
        encoding: str = "mulaw",
        **kwargs,
    ):
        self.stream_sid = stream_sid
        self.sample_rate = sample_rate
        self.encoding = encoding
    
    def set_stream_sid(self, stream_sid: str):
        """Set the stream SID."""
        self.stream_sid = stream_sid
    
    async def send_audio(
        self,
        websocket,
        audio_bytes: bytes,
    ):
        """
        Send audio data to Twilio.
        
        Args:
            websocket: WebSocket connection
            audio_bytes: Audio data to send
        """
        if not self.stream_sid:
            logger.error("Stream SID not set")
            return
        
        if not audio_bytes:
            return
        
        # Encode audio to base64
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        
        # Build Twilio media message
        message = {
            "event": "media",
            "streamSid": self.stream_sid,
            "media": {
                "payload": audio_b64,
            },
        }
        
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending audio to Twilio: {e}")
    
    async def send_mark(
        self,
        websocket,
        name: str,
    ):
        """
        Send a mark message to Twilio.
        
        Marks are used to track when audio playback reaches a certain point.
        
        Args:
            websocket: WebSocket connection
            name: Mark name for tracking
        """
        if not self.stream_sid:
            logger.error("Stream SID not set")
            return
        
        message = {
            "event": "mark",
            "streamSid": self.stream_sid,
            "mark": {
                "name": name,
            },
        }
        
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending mark to Twilio: {e}")
    
    async def clear_audio(self, websocket):
        """
        Clear queued audio (stop current playback).
        
        Args:
            websocket: WebSocket connection
        """
        if not self.stream_sid:
            logger.error("Stream SID not set")
            return
        
        message = {
            "event": "clear",
            "streamSid": self.stream_sid,
        }
        
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error clearing Twilio audio: {e}")
    
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
                    # Split into smaller chunks if needed
                    for i in range(0, len(audio_chunk), chunk_size):
                        chunk = audio_chunk[i:i + chunk_size]
                        await self.send_audio(websocket, chunk)
        except Exception as e:
            logger.error(f"Error streaming audio: {e}")
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return "twilio"
