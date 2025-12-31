"""
Sunona Voice AI - Telnyx Telephony Handler

Telnyx integration for voice calls.
Low-latency carrier with WebRTC support.
"""

import os
import json
import asyncio
import logging
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Try to import telnyx
try:
    import telnyx
    TELNYX_AVAILABLE = True
except ImportError:
    TELNYX_AVAILABLE = False
    telnyx = None


@dataclass
class TelnyxCallState:
    """State for an active Telnyx call."""
    call_control_id: str
    call_leg_id: Optional[str] = None
    is_connected: bool = False


class TelnyxHandler:
    """
    Handler for Telnyx voice calls.
    
    Features:
        - Outbound call initiation
        - Call control commands
        - Real-time audio streaming
        - Transfer and bridging
    
    Example:
        ```python
        handler = TelnyxHandler()
        
        call_id = handler.make_call(
            to="+1234567890",
            webhook_url="https://example.com/telnyx/events"
        )
        ```
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        profile_name: Optional[str] = None,
        phone_number: Optional[str] = None,
    ):
        """
        Initialize Telnyx handler.
        
        Args:
            api_key: Telnyx API key
            profile_name: Connection profile name
            phone_number: Phone number for outbound
        """
        if not TELNYX_AVAILABLE:
            raise ImportError(
                "telnyx package required. Install with: pip install telnyx"
            )
        
        self.api_key = api_key or os.getenv("TELNYX_API_KEY")
        self.profile_name = profile_name or os.getenv("TELNYX_PROFILE_NAME")
        self.phone_number = phone_number or os.getenv("TELNYX_PHONE_NUMBER")
        
        if not self.api_key:
            raise ValueError(
                "Telnyx API key required. Set TELNYX_API_KEY."
            )
        
        telnyx.api_key = self.api_key
        
        self._active_calls: Dict[str, TelnyxCallState] = {}
        
        logger.info("Telnyx handler initialized")
    
    def make_call(
        self,
        to: str,
        webhook_url: str,
        client_state: Optional[str] = None,
    ) -> str:
        """
        Make an outbound call.
        
        Args:
            to: Phone number to call
            webhook_url: URL for call events
            client_state: Custom state data
            
        Returns:
            Call control ID
        """
        if not self.phone_number:
            raise ValueError("Phone number not configured")
        
        call = telnyx.Call.create(
            connection_id=self.profile_name,
            to=to,
            from_=self.phone_number,
            webhook_url=webhook_url,
            client_state=client_state,
        )
        
        call_id = call.call_control_id
        self._active_calls[call_id] = TelnyxCallState(call_control_id=call_id)
        
        logger.info(f"Made Telnyx call: {call_id} to {to}")
        
        return call_id
    
    def answer(self, call_control_id: str, webhook_url: str) -> bool:
        """Answer an incoming call."""
        try:
            call = telnyx.Call.retrieve(call_control_id)
            call.answer(webhook_url=webhook_url)
            
            self._active_calls[call_control_id] = TelnyxCallState(
                call_control_id=call_control_id,
                is_connected=True,
            )
            
            logger.info(f"Answered call: {call_control_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to answer: {e}")
            return False
    
    def start_streaming(
        self,
        call_control_id: str,
        websocket_url: str,
    ) -> bool:
        """Start audio streaming."""
        try:
            call = telnyx.Call.retrieve(call_control_id)
            call.streaming_start(
                stream_url=websocket_url,
                stream_track="both_tracks",
            )
            
            logger.info(f"Started streaming for: {call_control_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to start streaming: {e}")
            return False
    
    def stop_streaming(self, call_control_id: str) -> bool:
        """Stop audio streaming."""
        try:
            call = telnyx.Call.retrieve(call_control_id)
            call.streaming_stop()
            
            logger.info(f"Stopped streaming for: {call_control_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to stop streaming: {e}")
            return False
    
    def speak(
        self,
        call_control_id: str,
        text: str,
        voice: str = "female",
        language: str = "en-US",
    ) -> bool:
        """Use Telnyx TTS to speak."""
        try:
            call = telnyx.Call.retrieve(call_control_id)
            call.speak(
                payload=text,
                voice=voice,
                language=language,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to speak: {e}")
            return False
    
    def play_audio(
        self,
        call_control_id: str,
        audio_url: str,
    ) -> bool:
        """Play audio file."""
        try:
            call = telnyx.Call.retrieve(call_control_id)
            call.playback_start(audio_url=audio_url)
            return True
        except Exception as e:
            logger.error(f"Failed to play audio: {e}")
            return False
    
    def transfer(
        self,
        call_control_id: str,
        to: str,
    ) -> bool:
        """Transfer call."""
        try:
            call = telnyx.Call.retrieve(call_control_id)
            call.transfer(to=to)
            
            logger.info(f"Transferred call {call_control_id} to {to}")
            return True
        except Exception as e:
            logger.error(f"Failed to transfer: {e}")
            return False
    
    def hangup(self, call_control_id: str) -> bool:
        """Hang up call."""
        try:
            call = telnyx.Call.retrieve(call_control_id)
            call.hangup()
            
            if call_control_id in self._active_calls:
                del self._active_calls[call_control_id]
            
            logger.info(f"Hung up Telnyx call: {call_control_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to hang up: {e}")
            return False
    
    async def handle_event(self, event_data: Dict[str, Any]) -> None:
        """Handle Telnyx webhook event."""
        event_type = event_data.get("data", {}).get("event_type")
        payload = event_data.get("data", {}).get("payload", {})
        call_control_id = payload.get("call_control_id")
        
        logger.debug(f"Telnyx event: {event_type} for {call_control_id}")
        
        if event_type == "call.initiated":
            pass
        elif event_type == "call.answered":
            if call_control_id in self._active_calls:
                self._active_calls[call_control_id].is_connected = True
        elif event_type == "call.hangup":
            if call_control_id in self._active_calls:
                del self._active_calls[call_control_id]
