"""
Sunona Voice AI - Vonage Telephony Handler

Vonage (formerly Nexmo) integration for voice calls.
Alternative telephony provider with global coverage.

Features:
- Outbound call initiation
- WebSocket audio streaming
- Call control (transfer, mute, hold)
- NCCO (Nexmo Call Control Object) support
- Multi-region support
"""

import os
import json
import base64
import asyncio
import logging
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Try to import vonage
try:
    import vonage
    VONAGE_AVAILABLE = True
except ImportError:
    VONAGE_AVAILABLE = False
    vonage = None

from sunona.helpers.audio_utils import convert_audio_format


@dataclass
class VonageCallState:
    """State for an active Vonage call."""
    uuid: str
    conversation_uuid: Optional[str] = None
    stream_id: Optional[str] = None
    is_connected: bool = False
    is_speaking: bool = False


class VonageHandler:
    """
    Handler for Vonage voice calls.
    
    Features:
        - Outbound call initiation
        - WebSocket media streaming
        - NCCO generation for call flow
        - Call transfer and control
    
    Example:
        ```python
        handler = VonageHandler()
        
        # Initiate call
        uuid = handler.initiate_call(
            to_number="+1234567890",
            agent_id="my_agent"
        )
        
        # Generate NCCO
        ncco = handler.generate_ncco(agent_id)
        ```
    
    Prerequisites:
        - pip install vonage
        - Vonage account credentials
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        application_id: Optional[str] = None,
        private_key: Optional[str] = None,
        phone_number: Optional[str] = None,
        webhook_base_url: Optional[str] = None,
    ):
        """
        Initialize Vonage handler.
        
        Args:
            api_key: Vonage API key
            api_secret: Vonage API secret
            application_id: Vonage application ID
            private_key: Path to private key file or key content
            phone_number: Vonage phone number for outbound calls
            webhook_base_url: Base URL for webhooks
        """
        if not VONAGE_AVAILABLE:
            raise ImportError(
                "vonage package required. Install with: pip install vonage"
            )
        
        self.api_key = api_key or os.getenv("VONAGE_API_KEY")
        self.api_secret = api_secret or os.getenv("VONAGE_API_SECRET")
        self.application_id = application_id or os.getenv("VONAGE_APPLICATION_ID")
        self.private_key = private_key or os.getenv("VONAGE_PRIVATE_KEY")
        self.phone_number = phone_number or os.getenv("VONAGE_PHONE_NUMBER")
        self.webhook_base_url = webhook_base_url or os.getenv("VONAGE_WEBHOOK_URL")
        
        if not self.api_key or not self.api_secret:
            raise ValueError(
                "Vonage credentials required. Set VONAGE_API_KEY and "
                "VONAGE_API_SECRET environment variables."
            )
        
        # Initialize client
        if self.private_key and self.application_id:
            self._client = vonage.Client(
                application_id=self.application_id,
                private_key=self.private_key
            )
        else:
            self._client = vonage.Client(
                key=self.api_key,
                secret=self.api_secret
            )
        
        self._voice = vonage.Voice(self._client)
        self._active_calls: Dict[str, VonageCallState] = {}
        
        logger.info("Vonage handler initialized")
    
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
            answer_url: URL returning NCCO (default: webhook_base_url/vonage/answer/{agent_id})
            
        Returns:
            Call UUID
        """
        if not self.phone_number:
            raise ValueError("Vonage phone number not configured")
        
        url = answer_url or f"{self.webhook_base_url}/vonage/answer/{agent_id}"
        
        response = self._voice.create_call({
            'to': [{'type': 'phone', 'number': to_number}],
            'from': {'type': 'phone', 'number': self.phone_number},
            'answer_url': [url],
        })
        
        call_uuid = response['uuid']
        logger.info(f"Initiated Vonage call: {call_uuid} to {to_number}")
        
        self._active_calls[call_uuid] = VonageCallState(uuid=call_uuid)
        
        return call_uuid
    
    def generate_ncco(
        self,
        agent_id: str,
        websocket_url: Optional[str] = None,
    ) -> list:
        """
        Generate NCCO for a voice call with WebSocket streaming.
        
        Args:
            agent_id: Agent ID for the call
            websocket_url: WebSocket URL for media streaming
            
        Returns:
            NCCO action list
        """
        ws_url = websocket_url or f"{self.webhook_base_url.replace('https://', 'wss://')}/vonage/media/{agent_id}"
        
        ncco = [
            {
                "action": "connect",
                "endpoint": [
                    {
                        "type": "websocket",
                        "uri": ws_url,
                        "content-type": "audio/l16;rate=16000",
                        "headers": {
                            "agent_id": agent_id
                        }
                    }
                ]
            }
        ]
        
        return ncco
    
    def generate_speak_ncco(
        self,
        text: str,
        voice_name: str = "Amy",
        language: str = "en-US",
    ) -> list:
        """
        Generate NCCO for TTS.
        
        Args:
            text: Text to speak
            voice_name: Voice to use
            language: Language code
            
        Returns:
            NCCO action list
        """
        ncco = [
            {
                "action": "talk",
                "text": text,
                "voiceName": voice_name,
                "language": language,
            }
        ]
        
        return ncco
    
    async def handle_media_websocket(
        self,
        websocket,
        agent_id: str,
        on_audio_received: Callable[[bytes], None],
        get_audio_to_send: Callable[[], Optional[bytes]],
    ):
        """
        Handle Vonage media WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            agent_id: Agent ID
            on_audio_received: Callback for received audio
            get_audio_to_send: Function to get audio to send
        """
        call_state: Optional[VonageCallState] = None
        
        try:
            async for message in websocket:
                if isinstance(message, bytes):
                    # Vonage sends raw L16 PCM audio
                    on_audio_received(message)
                
                elif isinstance(message, str):
                    data = json.loads(message)
                    event = data.get("event")
                    
                    if event == "websocket:connected":
                        call_uuid = data.get("call_uuid")
                        call_state = VonageCallState(
                            uuid=call_uuid,
                            is_connected=True,
                        )
                        
                        if call_uuid:
                            self._active_calls[call_uuid] = call_state
                        
                        logger.info(f"Vonage WebSocket connected: {call_uuid}")
                    
                    elif event == "websocket:disconnected":
                        logger.info("Vonage WebSocket disconnected")
                        break
                
                # Send audio if available
                if call_state and call_state.is_connected:
                    audio_to_send = get_audio_to_send()
                    if audio_to_send:
                        # Vonage expects L16 PCM at 16kHz
                        await websocket.send(audio_to_send)
        
        except Exception as e:
            logger.error(f"Vonage WebSocket error: {e}")
        finally:
            if call_state and call_state.uuid in self._active_calls:
                del self._active_calls[call_state.uuid]
    
    async def send_audio(
        self,
        websocket,
        audio_pcm: bytes,
    ):
        """
        Send audio to Vonage WebSocket.
        
        Args:
            websocket: WebSocket connection
            audio_pcm: Audio bytes in PCM format (L16, 16kHz)
        """
        await websocket.send(audio_pcm)
    
    def hangup_call(self, call_uuid: str) -> bool:
        """
        Hang up an active call.
        
        Args:
            call_uuid: Call UUID to hang up
            
        Returns:
            True if successful
        """
        try:
            self._voice.update_call(call_uuid, action='hangup')
            
            if call_uuid in self._active_calls:
                del self._active_calls[call_uuid]
            
            logger.info(f"Hung up Vonage call: {call_uuid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to hang up Vonage call {call_uuid}: {e}")
            return False
    
    def transfer_call(
        self,
        call_uuid: str,
        ncco_url: str,
    ) -> bool:
        """
        Transfer a call to a new NCCO.
        
        Args:
            call_uuid: Call UUID to transfer
            ncco_url: URL returning new NCCO
            
        Returns:
            True if successful
        """
        try:
            self._voice.update_call(
                call_uuid,
                action='transfer',
                destination={'type': 'ncco', 'url': [ncco_url]}
            )
            
            logger.info(f"Transferring call {call_uuid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to transfer call {call_uuid}: {e}")
            return False
    
    def mute_call(self, call_uuid: str) -> bool:
        """Mute a call."""
        try:
            self._voice.update_call(call_uuid, action='mute')
            return True
        except Exception as e:
            logger.error(f"Failed to mute call {call_uuid}: {e}")
            return False
    
    def unmute_call(self, call_uuid: str) -> bool:
        """Unmute a call."""
        try:
            self._voice.update_call(call_uuid, action='unmute')
            return True
        except Exception as e:
            logger.error(f"Failed to unmute call {call_uuid}: {e}")
            return False
    
    def get_active_calls(self) -> Dict[str, VonageCallState]:
        """Get all active calls."""
        return self._active_calls.copy()
