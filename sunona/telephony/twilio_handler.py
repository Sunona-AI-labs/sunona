"""
Sunona Voice AI - Twilio Handler

Twilio integration for voice calls with WebSocket streaming.
"""

import os
import json
import base64
import asyncio
import logging
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass

try:
    from twilio.rest import Client as TwilioClient
    from twilio.twiml.voice_response import VoiceResponse, Connect, Stream
except ImportError:
    TwilioClient = None
    VoiceResponse = None

from sunona.helpers.audio_utils import convert_audio_format

logger = logging.getLogger(__name__)


@dataclass
class TwilioCallState:
    """State for an active Twilio call."""
    call_sid: str
    stream_sid: Optional[str] = None
    is_connected: bool = False
    is_speaking: bool = False


class TwilioHandler:
    """
    Handler for Twilio voice calls.
    
    Features:
        - Outbound call initiation
        - WebSocket media streaming
        - Audio format conversion (mulaw)
        - Call state management
    """
    
    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        phone_number: Optional[str] = None,
        webhook_base_url: Optional[str] = None,
    ):
        """
        Initialize Twilio handler.
        
        Args:
            account_sid: Twilio Account SID
            auth_token: Twilio Auth Token
            phone_number: Twilio phone number for outbound calls
            webhook_base_url: Base URL for webhooks (e.g., ngrok URL)
        """
        if TwilioClient is None:
            raise ImportError("twilio package required. Install with: pip install twilio")
        
        self.account_sid = account_sid or os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = auth_token or os.getenv("TWILIO_AUTH_TOKEN")
        self.phone_number = phone_number or os.getenv("TWILIO_PHONE_NUMBER")
        self.webhook_base_url = webhook_base_url or os.getenv("TWILIO_WEBHOOK_URL")
        
        if not self.account_sid or not self.auth_token:
            raise ValueError(
                "Twilio credentials required. Set TWILIO_ACCOUNT_SID and "
                "TWILIO_AUTH_TOKEN environment variables."
            )
        
        self._client = TwilioClient(self.account_sid, self.auth_token)
        self._active_calls: Dict[str, TwilioCallState] = {}
    
    def initiate_call(
        self,
        to_number: str,
        agent_id: str,
        twiml_url: Optional[str] = None,
    ) -> str:
        """
        Initiate an outbound call.
        
        Args:
            to_number: Phone number to call
            agent_id: Agent ID to use for the call
            twiml_url: URL returning TwiML (default: webhook_base_url/twiml/{agent_id})
            
        Returns:
            Call SID
        """
        if not self.phone_number:
            raise ValueError("Twilio phone number not configured")
        
        url = twiml_url or f"{self.webhook_base_url}/twiml/{agent_id}"
        
        call = self._client.calls.create(
            to=to_number,
            from_=self.phone_number,
            url=url,
            method="POST",
        )
        
        logger.info(f"Initiated call: {call.sid} to {to_number}")
        
        self._active_calls[call.sid] = TwilioCallState(call_sid=call.sid)
        
        return call.sid
    
    def generate_twiml(
        self,
        agent_id: str,
        websocket_url: Optional[str] = None,
    ) -> str:
        """
        Generate TwiML for a voice call.
        
        Args:
            agent_id: Agent ID for the call
            websocket_url: WebSocket URL for media streaming
            
        Returns:
            TwiML XML string
        """
        if VoiceResponse is None:
            raise ImportError("twilio package required")
        
        ws_url = websocket_url or f"{self.webhook_base_url.replace('https://', 'wss://')}/media/{agent_id}"
        
        response = VoiceResponse()
        
        # Connect to WebSocket for media streaming
        connect = Connect()
        stream = Stream(url=ws_url)
        stream.parameter(name="agent_id", value=agent_id)
        connect.append(stream)
        response.append(connect)
        
        return str(response)
    
    async def handle_media_websocket(
        self,
        websocket,
        agent_id: str,
        on_audio_received: Callable[[bytes], None],
        get_audio_to_send: Callable[[], Optional[bytes]],
    ):
        """
        Handle Twilio media WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            agent_id: Agent ID
            on_audio_received: Callback for received audio (mulaw)
            get_audio_to_send: Function to get audio to send (pcm)
        """
        call_state: Optional[TwilioCallState] = None
        
        try:
            async for message in websocket:
                if isinstance(message, str):
                    data = json.loads(message)
                    event = data.get("event")
                    
                    if event == "connected":
                        logger.info(f"Twilio WebSocket connected for agent {agent_id}")
                    
                    elif event == "start":
                        stream_sid = data.get("streamSid")
                        call_sid = data.get("start", {}).get("callSid")
                        
                        call_state = TwilioCallState(
                            call_sid=call_sid,
                            stream_sid=stream_sid,
                            is_connected=True,
                        )
                        
                        if call_sid:
                            self._active_calls[call_sid] = call_state
                        
                        logger.info(f"Twilio stream started: {stream_sid}")
                    
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
                        logger.info("Twilio stream stopped")
                        if call_state and call_state.call_sid in self._active_calls:
                            del self._active_calls[call_state.call_sid]
                        break
                
                # Send audio if available
                if call_state and call_state.is_connected:
                    audio_to_send = get_audio_to_send()
                    if audio_to_send:
                        # Convert PCM to mulaw for Twilio
                        audio_mulaw = convert_audio_format(
                            audio_to_send, "pcm", "mulaw"
                        )
                        
                        # Send as media event
                        media_message = {
                            "event": "media",
                            "streamSid": call_state.stream_sid,
                            "media": {
                                "payload": base64.b64encode(audio_mulaw).decode()
                            }
                        }
                        await websocket.send(json.dumps(media_message))
        
        except Exception as e:
            logger.error(f"Twilio WebSocket error: {e}")
        finally:
            if call_state and call_state.call_sid in self._active_calls:
                del self._active_calls[call_state.call_sid]
    
    async def send_audio(
        self,
        websocket,
        stream_sid: str,
        audio_pcm: bytes,
    ):
        """
        Send audio to Twilio WebSocket.
        
        Args:
            websocket: WebSocket connection
            stream_sid: Twilio stream SID
            audio_pcm: Audio bytes in PCM format
        """
        # Convert to mulaw
        audio_mulaw = convert_audio_format(audio_pcm, "pcm", "mulaw")
        
        # Send as media event
        message = {
            "event": "media",
            "streamSid": stream_sid,
            "media": {
                "payload": base64.b64encode(audio_mulaw).decode()
            }
        }
        
        await websocket.send(json.dumps(message))
    
    def hangup_call(self, call_sid: str) -> bool:
        """
        Hang up an active call.
        
        Args:
            call_sid: Call SID to hang up
            
        Returns:
            True if successful
        """
        try:
            call = self._client.calls(call_sid).update(status="completed")
            
            if call_sid in self._active_calls:
                del self._active_calls[call_sid]
            
            logger.info(f"Hung up call: {call_sid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to hang up call {call_sid}: {e}")
            return False
    
    def get_active_calls(self) -> Dict[str, TwilioCallState]:
        """Get all active calls."""
        return self._active_calls.copy()
