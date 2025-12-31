"""
Sunona Voice AI - SignalWire Telephony Handler

SignalWire integration for voice calls. High-performance
alternative to Twilio with similar API.
"""

import os
import json
import asyncio
import logging
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Try to import signalwire
try:
    from signalwire.rest import Client as SignalWireClient
    from signalwire.voice_response import VoiceResponse, Connect, Stream
    SIGNALWIRE_AVAILABLE = True
except ImportError:
    SIGNALWIRE_AVAILABLE = False
    SignalWireClient = None


@dataclass
class SignalWireCallState:
    """State for an active SignalWire call."""
    call_sid: str
    stream_sid: Optional[str] = None
    is_connected: bool = False


class SignalWireHandler:
    """
    Handler for SignalWire voice calls.
    
    Features:
        - Outbound call initiation
        - WebSocket media streaming
        - TwiML-compatible responses
        - Call control operations
    
    Example:
        ```python
        handler = SignalWireHandler()
        
        # Make call
        call_sid = handler.make_call(
            to="+1234567890",
            twiml_url="https://example.com/voice"
        )
        
        # Generate streaming response
        response = handler.generate_stream_response(
            websocket_url="wss://example.com/media",
            agent_id="my_agent"
        )
        ```
    """
    
    def __init__(
        self,
        project_id: Optional[str] = None,
        token: Optional[str] = None,
        space_url: Optional[str] = None,
        phone_number: Optional[str] = None,
    ):
        """
        Initialize SignalWire handler.
        
        Args:
            project_id: SignalWire project ID
            token: SignalWire API token
            space_url: SignalWire space URL
            phone_number: Phone number for outbound calls
        """
        if not SIGNALWIRE_AVAILABLE:
            raise ImportError(
                "signalwire package required. Install with: pip install signalwire"
            )
        
        self.project_id = project_id or os.getenv("SIGNALWIRE_PROJECT_ID")
        self.token = token or os.getenv("SIGNALWIRE_TOKEN")
        self.space_url = space_url or os.getenv("SIGNALWIRE_SPACE_URL")
        self.phone_number = phone_number or os.getenv("SIGNALWIRE_PHONE_NUMBER")
        
        if not all([self.project_id, self.token, self.space_url]):
            raise ValueError(
                "SignalWire credentials required. Set SIGNALWIRE_PROJECT_ID, "
                "SIGNALWIRE_TOKEN, and SIGNALWIRE_SPACE_URL."
            )
        
        self._client = SignalWireClient(
            self.project_id,
            self.token,
            signalwire_space_url=self.space_url,
        )
        
        self._active_calls: Dict[str, SignalWireCallState] = {}
        
        logger.info("SignalWire handler initialized")
    
    def make_call(
        self,
        to: str,
        twiml_url: Optional[str] = None,
        twiml: Optional[str] = None,
        status_callback: Optional[str] = None,
    ) -> str:
        """
        Make an outbound call.
        
        Args:
            to: Phone number to call (E.164)
            twiml_url: URL returning TwiML
            twiml: TwiML string (if no url)
            status_callback: URL for status updates
            
        Returns:
            Call SID
        """
        if not self.phone_number:
            raise ValueError("Phone number not configured")
        
        call_params = {
            "to": to,
            "from_": self.phone_number,
        }
        
        if twiml_url:
            call_params["url"] = twiml_url
        elif twiml:
            call_params["twiml"] = twiml
        else:
            raise ValueError("Either twiml_url or twiml required")
        
        if status_callback:
            call_params["status_callback"] = status_callback
        
        call = self._client.calls.create(**call_params)
        
        self._active_calls[call.sid] = SignalWireCallState(call_sid=call.sid)
        
        logger.info(f"Made SignalWire call: {call.sid} to {to}")
        
        return call.sid
    
    def generate_stream_response(
        self,
        websocket_url: str,
        agent_id: str,
    ) -> str:
        """
        Generate TwiML for WebSocket streaming.
        
        Args:
            websocket_url: WebSocket URL for media
            agent_id: Agent ID
            
        Returns:
            TwiML XML string
        """
        response = VoiceResponse()
        
        connect = Connect()
        stream = Stream(url=websocket_url)
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
        Handle SignalWire media WebSocket.
        
        Similar to Twilio's media streams protocol.
        """
        call_state: Optional[SignalWireCallState] = None
        
        try:
            async for message in websocket:
                data = json.loads(message)
                event = data.get("event")
                
                if event == "connected":
                    logger.info("SignalWire media connected")
                
                elif event == "start":
                    call_sid = data.get("start", {}).get("callSid")
                    stream_sid = data.get("start", {}).get("streamSid")
                    
                    call_state = SignalWireCallState(
                        call_sid=call_sid,
                        stream_sid=stream_sid,
                        is_connected=True,
                    )
                    
                    if call_sid:
                        self._active_calls[call_sid] = call_state
                    
                    logger.info(f"SignalWire stream started: {stream_sid}")
                
                elif event == "media":
                    # Audio data (base64 mulaw)
                    import base64
                    audio_b64 = data.get("media", {}).get("payload", "")
                    audio_bytes = base64.b64decode(audio_b64)
                    on_audio_received(audio_bytes)
                
                elif event == "stop":
                    logger.info("SignalWire stream stopped")
                    break
                
                # Send audio if available
                if call_state and call_state.is_connected:
                    audio = get_audio_to_send()
                    if audio:
                        import base64
                        media_msg = {
                            "event": "media",
                            "streamSid": call_state.stream_sid,
                            "media": {
                                "payload": base64.b64encode(audio).decode()
                            }
                        }
                        await websocket.send(json.dumps(media_msg))
        
        except Exception as e:
            logger.error(f"SignalWire WebSocket error: {e}")
        
        finally:
            if call_state and call_state.call_sid in self._active_calls:
                del self._active_calls[call_state.call_sid]
    
    def hangup(self, call_sid: str) -> bool:
        """Hang up a call."""
        try:
            self._client.calls(call_sid).update(status="completed")
            
            if call_sid in self._active_calls:
                del self._active_calls[call_sid]
            
            logger.info(f"Hung up SignalWire call: {call_sid}")
            return True
        except Exception as e:
            logger.error(f"Failed to hang up: {e}")
            return False
    
    def transfer(self, call_sid: str, to: str) -> bool:
        """Transfer a call."""
        try:
            twiml = f'<Response><Dial>{to}</Dial></Response>'
            self._client.calls(call_sid).update(twiml=twiml)
            logger.info(f"Transferred call {call_sid} to {to}")
            return True
        except Exception as e:
            logger.error(f"Failed to transfer: {e}")
            return False
