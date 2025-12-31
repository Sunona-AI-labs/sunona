"""
Sunona Voice AI - Plivo Handler

Plivo integration for voice calls with WebSocket streaming.
Alternative to Twilio with often better regional pricing.

Features:
- Outbound call initiation
- WebSocket media streaming
- Audio format conversion
- Call state management
- PHLO integration support
"""

import os
import json
import base64
import asyncio
import logging
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass

try:
    import plivo
    PLIVO_AVAILABLE = True
except ImportError:
    PLIVO_AVAILABLE = False
    plivo = None

from sunona.helpers.audio_utils import convert_audio_format

logger = logging.getLogger(__name__)


@dataclass
class PlivoCallState:
    """State for an active Plivo call."""
    call_uuid: str
    stream_id: Optional[str] = None
    is_connected: bool = False
    is_speaking: bool = False


class PlivoHandler:
    """
    Handler for Plivo voice calls.
    
    Features:
        - Outbound call initiation
        - WebSocket media streaming
        - Audio format conversion (mulaw/PCM)
        - Call state management
        - PHLO workflow support
    
    Example:
        ```python
        handler = PlivoHandler()
        
        # Initiate call
        call_uuid = handler.initiate_call(
            to_number="+1234567890",
            agent_id="my_agent"
        )
        
        # Generate XML response
        xml = handler.generate_xml(agent_id)
        ```
    """
    
    def __init__(
        self,
        auth_id: Optional[str] = None,
        auth_token: Optional[str] = None,
        phone_number: Optional[str] = None,
        webhook_base_url: Optional[str] = None,
    ):
        """
        Initialize Plivo handler.
        
        Args:
            auth_id: Plivo Auth ID
            auth_token: Plivo Auth Token
            phone_number: Plivo phone number for outbound calls
            webhook_base_url: Base URL for webhooks
        """
        if not PLIVO_AVAILABLE:
            raise ImportError(
                "plivo package required. Install with: pip install plivo"
            )
        
        self.auth_id = auth_id or os.getenv("PLIVO_AUTH_ID")
        self.auth_token = auth_token or os.getenv("PLIVO_AUTH_TOKEN")
        self.phone_number = phone_number or os.getenv("PLIVO_PHONE_NUMBER")
        self.webhook_base_url = webhook_base_url or os.getenv("PLIVO_WEBHOOK_URL")
        
        if not self.auth_id or not self.auth_token:
            raise ValueError(
                "Plivo credentials required. Set PLIVO_AUTH_ID and "
                "PLIVO_AUTH_TOKEN environment variables."
            )
        
        self._client = plivo.RestClient(self.auth_id, self.auth_token)
        self._active_calls: Dict[str, PlivoCallState] = {}
    
    def initiate_call(
        self,
        to_number: str,
        agent_id: str,
        answer_url: Optional[str] = None,
    ) -> str:
        """
        Initiate an outbound call.
        
        Args:
            to_number: Phone number to call (E.164 format)
            agent_id: Agent ID to use for the call
            answer_url: URL returning Plivo XML (default: webhook_base_url/plivo/answer/{agent_id})
            
        Returns:
            Call UUID
        """
        if not self.phone_number:
            raise ValueError("Plivo phone number not configured")
        
        url = answer_url or f"{self.webhook_base_url}/plivo/answer/{agent_id}"
        
        response = self._client.calls.create(
            from_=self.phone_number,
            to_=to_number,
            answer_url=url,
            answer_method="POST",
        )
        
        call_uuid = response[0].request_uuid
        logger.info(f"Initiated Plivo call: {call_uuid} to {to_number}")
        
        self._active_calls[call_uuid] = PlivoCallState(call_uuid=call_uuid)
        
        return call_uuid
    
    def generate_xml(
        self,
        agent_id: str,
        websocket_url: Optional[str] = None,
    ) -> str:
        """
        Generate Plivo XML for a voice call with streaming.
        
        Args:
            agent_id: Agent ID for the call
            websocket_url: WebSocket URL for media streaming
            
        Returns:
            Plivo XML string
        """
        ws_url = websocket_url or f"{self.webhook_base_url.replace('https://', 'wss://')}/plivo/media/{agent_id}"
        
        # Generate Plivo XML for WebSocket streaming
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Stream bidirectional="true" keepCallAlive="true">
        {ws_url}
    </Stream>
</Response>"""
        
        return xml
    
    def generate_speak_xml(
        self,
        text: str,
        voice: str = "Polly.Joanna",
        language: str = "en-US",
    ) -> str:
        """
        Generate Plivo XML for TTS.
        
        Args:
            text: Text to speak
            voice: Voice to use (Polly voices supported)
            language: Language code
            
        Returns:
            Plivo XML string
        """
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Speak voice="{voice}" language="{language}">{text}</Speak>
</Response>"""
        
        return xml
    
    async def handle_media_websocket(
        self,
        websocket,
        agent_id: str,
        on_audio_received: Callable[[bytes], None],
        get_audio_to_send: Callable[[], Optional[bytes]],
    ):
        """
        Handle Plivo media WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            agent_id: Agent ID
            on_audio_received: Callback for received audio (mulaw)
            get_audio_to_send: Function to get audio to send (pcm)
        """
        call_state: Optional[PlivoCallState] = None
        
        try:
            async for message in websocket:
                if isinstance(message, str):
                    data = json.loads(message)
                    event = data.get("event")
                    
                    if event == "start":
                        stream_id = data.get("streamId")
                        call_uuid = data.get("callUUID")
                        
                        call_state = PlivoCallState(
                            call_uuid=call_uuid,
                            stream_id=stream_id,
                            is_connected=True,
                        )
                        
                        if call_uuid:
                            self._active_calls[call_uuid] = call_state
                        
                        logger.info(f"Plivo stream started: {stream_id}")
                    
                    elif event == "media":
                        # Received audio from caller
                        payload = data.get("media", {}).get("payload", "")
                        if payload:
                            audio_mulaw = base64.b64decode(payload)
                            # Convert to PCM for processing
                            audio_pcm = convert_audio_format(
                                audio_mulaw, "mulaw", "pcm"
                            )
                            on_audio_received(audio_pcm)
                    
                    elif event == "stop":
                        logger.info("Plivo stream stopped")
                        if call_state and call_state.call_uuid in self._active_calls:
                            del self._active_calls[call_state.call_uuid]
                        break
                
                # Send audio if available
                if call_state and call_state.is_connected:
                    audio_to_send = get_audio_to_send()
                    if audio_to_send:
                        # Convert PCM to mulaw for Plivo
                        audio_mulaw = convert_audio_format(
                            audio_to_send, "pcm", "mulaw"
                        )
                        
                        # Send as media event
                        media_message = {
                            "event": "playAudio",
                            "media": {
                                "payload": base64.b64encode(audio_mulaw).decode(),
                                "contentType": "audio/x-mulaw",
                                "sampleRate": 8000,
                            }
                        }
                        await websocket.send(json.dumps(media_message))
        
        except Exception as e:
            logger.error(f"Plivo WebSocket error: {e}")
        finally:
            if call_state and call_state.call_uuid in self._active_calls:
                del self._active_calls[call_state.call_uuid]
    
    async def send_audio(
        self,
        websocket,
        audio_pcm: bytes,
    ):
        """
        Send audio to Plivo WebSocket.
        
        Args:
            websocket: WebSocket connection
            audio_pcm: Audio bytes in PCM format
        """
        # Convert to mulaw
        audio_mulaw = convert_audio_format(audio_pcm, "pcm", "mulaw")
        
        # Send as media event
        message = {
            "event": "playAudio",
            "media": {
                "payload": base64.b64encode(audio_mulaw).decode(),
                "contentType": "audio/x-mulaw",
                "sampleRate": 8000,
            }
        }
        
        await websocket.send(json.dumps(message))
    
    def hangup_call(self, call_uuid: str) -> bool:
        """
        Hang up an active call.
        
        Args:
            call_uuid: Call UUID to hang up
            
        Returns:
            True if successful
        """
        try:
            self._client.calls.delete(call_uuid)
            
            if call_uuid in self._active_calls:
                del self._active_calls[call_uuid]
            
            logger.info(f"Hung up Plivo call: {call_uuid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to hang up Plivo call {call_uuid}: {e}")
            return False
    
    def transfer_call(
        self,
        call_uuid: str,
        to_number: str,
    ) -> bool:
        """
        Transfer a call to another number.
        
        Args:
            call_uuid: Call UUID to transfer
            to_number: Destination number
            
        Returns:
            True if successful
        """
        try:
            # Generate transfer XML
            transfer_url = f"{self.webhook_base_url}/plivo/transfer?to={to_number}"
            
            self._client.calls.update(
                call_uuid,
                legs="aleg",
                aleg_url=transfer_url,
                aleg_method="POST",
            )
            
            logger.info(f"Transferring call {call_uuid} to {to_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to transfer call {call_uuid}: {e}")
            return False
    
    def get_active_calls(self) -> Dict[str, PlivoCallState]:
        """Get all active calls."""
        return self._active_calls.copy()
