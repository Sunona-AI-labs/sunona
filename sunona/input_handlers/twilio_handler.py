"""
Sunona Voice AI - Twilio Input Handler

Handles incoming audio from Twilio Media Streams.
"""

import asyncio
import base64
import json
import logging
from typing import AsyncGenerator, Callable, Dict, Optional, Any

logger = logging.getLogger(__name__)


class TwilioInputHandler:
    """
    Twilio Media Streams input handler.
    
    Processes incoming WebSocket messages from Twilio
    and extracts audio data for transcription.
    
    Example:
        ```python
        handler = TwilioInputHandler()
        
        async for audio_chunk in handler.process_stream(websocket):
            # Process audio chunk
            pass
        ```
    """
    
    def __init__(
        self,
        sample_rate: int = 8000,
        encoding: str = "mulaw",
        **kwargs,
    ):
        self.sample_rate = sample_rate
        self.encoding = encoding
        
        self.stream_sid: Optional[str] = None
        self.call_sid: Optional[str] = None
        
        self._is_running = False
        self._on_audio: Optional[Callable] = None
        self._on_start: Optional[Callable] = None
        self._on_stop: Optional[Callable] = None
        self._on_dtmf: Optional[Callable] = None
    
    def set_audio_callback(self, callback: Callable):
        """Set callback for audio data."""
        self._on_audio = callback
    
    def set_start_callback(self, callback: Callable):
        """Set callback for stream start."""
        self._on_start = callback
    
    def set_stop_callback(self, callback: Callable):
        """Set callback for stream stop."""
        self._on_stop = callback
    
    def set_dtmf_callback(self, callback: Callable):
        """Set callback for DTMF input."""
        self._on_dtmf = callback
    
    async def process_message(self, message: str) -> Optional[bytes]:
        """
        Process a single WebSocket message from Twilio.
        
        Args:
            message: JSON message from Twilio
            
        Returns:
            Audio bytes if media message, None otherwise
        """
        try:
            data = json.loads(message)
            event = data.get("event")
            
            if event == "connected":
                logger.info("Twilio connected")
                return None
            
            elif event == "start":
                self.stream_sid = data.get("streamSid")
                self.call_sid = data.get("start", {}).get("callSid")
                self._is_running = True
                
                logger.info(f"Twilio stream started: {self.stream_sid}")
                
                if self._on_start:
                    await self._on_start(data)
                
                return None
            
            elif event == "media":
                # Extract audio from media payload
                media = data.get("media", {})
                payload = media.get("payload", "")
                
                if payload:
                    audio_bytes = base64.b64decode(payload)
                    
                    if self._on_audio:
                        await self._on_audio(audio_bytes)
                    
                    return audio_bytes
                
                return None
            
            elif event == "stop":
                self._is_running = False
                logger.info("Twilio stream stopped")
                
                if self._on_stop:
                    await self._on_stop(data)
                
                return None
            
            elif event == "dtmf":
                digit = data.get("dtmf", {}).get("digit")
                logger.info(f"DTMF received: {digit}")
                
                if self._on_dtmf:
                    await self._on_dtmf(digit)
                
                return None
            
            else:
                logger.debug(f"Unknown Twilio event: {event}")
                return None
        
        except json.JSONDecodeError:
            logger.error("Invalid JSON from Twilio")
            return None
        except Exception as e:
            logger.error(f"Error processing Twilio message: {e}")
            return None
    
    async def process_stream(
        self,
        websocket,
    ) -> AsyncGenerator[bytes, None]:
        """
        Process incoming Twilio media stream.
        
        Args:
            websocket: WebSocket connection
            
        Yields:
            Audio chunks as bytes
        """
        self._is_running = True
        
        try:
            async for message in websocket:
                if not self._is_running:
                    break
                
                audio = await self.process_message(message)
                
                if audio:
                    yield audio
        
        except Exception as e:
            logger.error(f"Stream error: {e}")
        
        finally:
            self._is_running = False
    
    def stop(self):
        """Stop processing."""
        self._is_running = False
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return "twilio"
