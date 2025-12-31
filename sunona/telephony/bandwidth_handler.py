"""
Sunona Voice AI - Bandwidth Telephony Handler

Bandwidth (Voxbone) integration for voice calls.
Enterprise-grade carrier with global coverage.
"""

import os
import json
import asyncio
import logging
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Try to import bandwidth
try:
    from bandwidth.bandwidth_client import BandwidthClient
    from bandwidth.voice.models.create_call_request import CreateCallRequest
    BANDWIDTH_AVAILABLE = True
except ImportError:
    BANDWIDTH_AVAILABLE = False
    BandwidthClient = None


@dataclass
class BandwidthCallState:
    """State for an active Bandwidth call."""
    call_id: str
    is_connected: bool = False


class BandwidthHandler:
    """
    Handler for Bandwidth voice calls.
    
    Features:
        - Outbound call initiation
        - BXML responses
        - Conference support
        - Call recording
    
    Example:
        ```python
        handler = BandwidthHandler()
        
        call_id = handler.make_call(
            to="+1234567890",
            answer_url="https://example.com/bxml/answer"
        )
        ```
    """
    
    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        account_id: Optional[str] = None,
        application_id: Optional[str] = None,
        phone_number: Optional[str] = None,
    ):
        """
        Initialize Bandwidth handler.
        
        Args:
            username: Bandwidth username
            password: Bandwidth password
            account_id: Bandwidth account ID
            application_id: Bandwidth application ID
            phone_number: Phone number for outbound
        """
        if not BANDWIDTH_AVAILABLE:
            raise ImportError(
                "bandwidth-sdk package required. Install with: pip install bandwidth-sdk"
            )
        
        self.username = username or os.getenv("BANDWIDTH_USERNAME")
        self.password = password or os.getenv("BANDWIDTH_PASSWORD")
        self.account_id = account_id or os.getenv("BANDWIDTH_ACCOUNT_ID")
        self.application_id = application_id or os.getenv("BANDWIDTH_APPLICATION_ID")
        self.phone_number = phone_number or os.getenv("BANDWIDTH_PHONE_NUMBER")
        
        if not all([self.username, self.password, self.account_id]):
            raise ValueError(
                "Bandwidth credentials required. Set BANDWIDTH_USERNAME, "
                "BANDWIDTH_PASSWORD, and BANDWIDTH_ACCOUNT_ID."
            )
        
        self._client = BandwidthClient(
            voice_basic_auth_user_name=self.username,
            voice_basic_auth_password=self.password,
        )
        
        self._voice_client = self._client.voice_client.client
        self._active_calls: Dict[str, BandwidthCallState] = {}
        
        logger.info("Bandwidth handler initialized")
    
    def make_call(
        self,
        to: str,
        answer_url: str,
        disconnect_url: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> str:
        """
        Make an outbound call.
        
        Args:
            to: Phone number to call
            answer_url: URL returning BXML
            disconnect_url: URL for disconnect events
            tag: Custom tag data
            
        Returns:
            Call ID
        """
        if not self.phone_number:
            raise ValueError("Phone number not configured")
        
        request = CreateCallRequest(
            to=to,
            from_=self.phone_number,
            application_id=self.application_id,
            answer_url=answer_url,
            disconnect_url=disconnect_url,
            tag=tag,
        )
        
        result = self._voice_client.create_call(self.account_id, request)
        call_id = result.body.call_id
        
        self._active_calls[call_id] = BandwidthCallState(call_id=call_id)
        
        logger.info(f"Made Bandwidth call: {call_id} to {to}")
        
        return call_id
    
    def generate_stream_bxml(
        self,
        websocket_url: str,
        agent_id: str,
    ) -> str:
        """
        Generate BXML for streaming.
        
        Args:
            websocket_url: WebSocket URL
            agent_id: Agent ID
            
        Returns:
            BXML XML string
        """
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <StartStream streamEventUrl="{websocket_url}" 
                 streamEventMethod="POST">
        <StreamParam name="agent_id" value="{agent_id}"/>
    </StartStream>
</Response>'''
    
    def generate_speak_bxml(
        self,
        text: str,
        voice: str = "kate",
        locale: str = "en_US",
    ) -> str:
        """
        Generate BXML for TTS.
        
        Args:
            text: Text to speak
            voice: Voice name
            locale: Language locale
            
        Returns:
            BXML XML string
        """
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <SpeakSentence voice="{voice}" locale="{locale}">{text}</SpeakSentence>
</Response>'''
    
    def generate_transfer_bxml(
        self,
        to: str,
        caller_id: Optional[str] = None,
    ) -> str:
        """
        Generate BXML for transfer.
        
        Args:
            to: Transfer destination
            caller_id: Caller ID to display
            
        Returns:
            BXML XML string
        """
        from_attr = f' callerId="{caller_id}"' if caller_id else ""
        
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Transfer{from_attr}>
        <PhoneNumber>{to}</PhoneNumber>
    </Transfer>
</Response>'''
    
    def hangup(self, call_id: str) -> bool:
        """Hang up a call."""
        try:
            self._voice_client.modify_call(
                self.account_id,
                call_id,
                {"state": "completed"}
            )
            
            if call_id in self._active_calls:
                del self._active_calls[call_id]
            
            logger.info(f"Hung up Bandwidth call: {call_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to hang up: {e}")
            return False
    
    def redirect(self, call_id: str, redirect_url: str) -> bool:
        """Redirect call to new BXML."""
        try:
            self._voice_client.modify_call(
                self.account_id,
                call_id,
                {"redirectUrl": redirect_url}
            )
            
            logger.info(f"Redirected call {call_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to redirect: {e}")
            return False
    
    async def handle_event(self, event_data: Dict[str, Any]) -> Optional[str]:
        """
        Handle Bandwidth webhook event.
        
        Returns:
            BXML response if needed
        """
        event_type = event_data.get("eventType")
        call_id = event_data.get("callId")
        
        logger.debug(f"Bandwidth event: {event_type} for {call_id}")
        
        if event_type == "answer":
            if call_id:
                if call_id not in self._active_calls:
                    self._active_calls[call_id] = BandwidthCallState(call_id=call_id)
                self._active_calls[call_id].is_connected = True
        
        elif event_type == "disconnect":
            if call_id and call_id in self._active_calls:
                del self._active_calls[call_id]
        
        return None
