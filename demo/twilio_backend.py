"""
Twilio Phone Call Backend

Handles phone call initiation and webhook management for Twilio integration.
"""

import os
import asyncio
import logging
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TwilioConfig:
    """Twilio configuration."""
    account_sid: str
    auth_token: str
    phone_number: str
    
    @classmethod
    def from_env(cls) -> Optional["TwilioConfig"]:
        """Create config from environment variables."""
        sid = os.getenv("TWILIO_ACCOUNT_SID")
        token = os.getenv("TWILIO_AUTH_TOKEN")
        number = os.getenv("TWILIO_PHONE_NUMBER")
        
        if all([sid, token, number]):
            return cls(account_sid=sid, auth_token=token, phone_number=number)
        return None


@dataclass
class CallConfig:
    """Call configuration."""
    stt_provider: str = "Deepgram"
    stt_api_key: Optional[str] = None
    llm_provider: str = "Gemini"
    llm_api_key: Optional[str] = None
    tts_provider: str = "Edge TTS (Free)"
    tts_api_key: Optional[str] = None
    tts_voice: Optional[str] = None
    system_prompt: str = "You are a helpful AI phone assistant."


class TwilioBackend:
    """
    Twilio phone call backend.
    
    Features:
    - Phone call initiation
    - TwiML generation for call handling
    - Webhook management
    - Error handling with specific messages
    """
    
    def __init__(
        self,
        twilio_config: Optional[TwilioConfig] = None,
        call_config: Optional[CallConfig] = None,
    ):
        """
        Initialize Twilio backend.
        
        Args:
            twilio_config: Twilio credentials
            call_config: Call handling configuration
        """
        self.twilio_config = twilio_config or TwilioConfig.from_env()
        self.call_config = call_config or CallConfig()
        self._client = None
    
    @property
    def is_configured(self) -> bool:
        """Check if Twilio is configured."""
        return self.twilio_config is not None
    
    def _get_client(self):
        """Get or create Twilio client."""
        if not self.is_configured:
            raise ValueError("Twilio not configured")
        
        if self._client is None:
            from twilio.rest import Client
            self._client = Client(
                self.twilio_config.account_sid,
                self.twilio_config.auth_token
            )
        
        return self._client
    
    async def make_call(
        self,
        to_number: str,
        webhook_url: Optional[str] = None,
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Initiate a phone call.
        
        Args:
            to_number: Phone number to call (E.164 format)
            webhook_url: URL for call handling webhooks
            
        Returns:
            Tuple of (call_sid, error_message)
        """
        if not self.is_configured:
            return None, "📞 Twilio: Credentials not configured. Add your Twilio credentials."
        
        if not to_number:
            return None, "📞 Please enter a phone number to call."
        
        # Validate phone number format
        if not to_number.startswith("+"):
            return None, "📞 Phone number must include country code (e.g., +1234567890)"
        
        try:
            client = self._get_client()
            
            # Generate TwiML for the call
            twiml = self._generate_twiml(webhook_url)
            
            # Initiate call
            call = client.calls.create(
                to=to_number,
                from_=self.twilio_config.phone_number,
                twiml=twiml,
            )
            
            logger.info(f"Call initiated: {call.sid} to {to_number}")
            return call.sid, None
            
        except Exception as e:
            error = self._parse_error(e)
            logger.error(f"Twilio call error: {e}")
            return None, error
    
    def _generate_twiml(self, webhook_url: Optional[str] = None) -> str:
        """
        Generate TwiML for call handling.
        
        Args:
            webhook_url: URL for handling conversation
            
        Returns:
            TwiML XML string
        """
        if webhook_url:
            # Use webhook for full conversation
            return f"""
            <Response>
                <Say voice="Polly.Joanna">Hello! I'm Sunona, your AI assistant. How can I help you today?</Say>
                <Gather input="speech" action="{webhook_url}" method="POST" speechTimeout="auto">
                    <Say>Please speak after the tone.</Say>
                </Gather>
            </Response>
            """
        else:
            # Simple demo response
            return """
            <Response>
                <Say voice="Polly.Joanna">Hello! This is Sunona, your AI voice assistant. Thank you for trying our demo. Your call has been connected successfully. Goodbye!</Say>
            </Response>
            """
    
    async def get_call_status(self, call_sid: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Get status of a call.
        
        Args:
            call_sid: Call SID to check
            
        Returns:
            Tuple of (call_info, error_message)
        """
        if not self.is_configured:
            return None, "📞 Twilio not configured"
        
        try:
            client = self._get_client()
            call = client.calls(call_sid).fetch()
            
            return {
                "sid": call.sid,
                "status": call.status,
                "to": call.to,
                "from": call.from_,
                "duration": call.duration,
                "direction": call.direction,
            }, None
            
        except Exception as e:
            return None, f"📞 Error: {str(e)[:100]}"
    
    async def end_call(self, call_sid: str) -> Tuple[bool, Optional[str]]:
        """
        End an active call.
        
        Args:
            call_sid: Call SID to end
            
        Returns:
            Tuple of (success, error_message)
        """
        if not self.is_configured:
            return False, "📞 Twilio not configured"
        
        try:
            client = self._get_client()
            call = client.calls(call_sid).update(status="completed")
            
            logger.info(f"Call ended: {call_sid}")
            return True, None
            
        except Exception as e:
            return False, f"📞 Error ending call: {str(e)[:100]}"
    
    def _parse_error(self, e: Exception) -> str:
        """Parse Twilio error and return user-friendly message."""
        error_msg = str(e).lower()
        
        if "authenticate" in error_msg or "401" in error_msg:
            return "📞 Twilio: Authentication failed. Check your Account SID and Auth Token."
        elif "balance" in error_msg or "credit" in error_msg or "insufficient" in error_msg:
            return "📞 Twilio: Insufficient balance. Add funds to your Twilio account."
        elif "21211" in str(e) or "invalid" in error_msg and "number" in error_msg:
            return "📞 Twilio: Invalid phone number format. Use E.164 format (+1234567890)."
        elif "21214" in str(e) or "not verified" in error_msg:
            return "📞 Twilio: Trial account can only call verified numbers. Verify the number in Twilio console."
        elif "21608" in str(e) or "unverified" in error_msg:
            return "📞 Twilio: The 'From' number is not verified. Check your Twilio phone number."
        elif "rate limit" in error_msg or "429" in error_msg:
            return "📞 Twilio: Rate limit exceeded. Wait a moment and try again."
        else:
            return f"📞 Twilio Error: {str(e)[:100]}"
    
    def validate_config(self) -> Tuple[bool, Optional[str]]:
        """
        Validate Twilio configuration.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.twilio_config:
            return False, "📞 Twilio credentials not configured"
        
        if not self.twilio_config.account_sid:
            return False, "📞 Twilio Account SID is missing"
        
        if not self.twilio_config.auth_token:
            return False, "📞 Twilio Auth Token is missing"
        
        if not self.twilio_config.phone_number:
            return False, "📞 Twilio Phone Number is missing"
        
        # Validate format
        if not self.twilio_config.account_sid.startswith("AC"):
            return False, "📞 Invalid Account SID format (should start with 'AC')"
        
        if not self.twilio_config.phone_number.startswith("+"):
            return False, "📞 Phone number should include country code (e.g., +1...)"
        
        return True, None


# Convenience functions

def make_call_sync(
    to_number: str,
    account_sid: Optional[str] = None,
    auth_token: Optional[str] = None,
    from_number: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Synchronous wrapper for making a call.
    
    Args:
        to_number: Phone number to call
        account_sid: Twilio Account SID
        auth_token: Twilio Auth Token
        from_number: Twilio phone number
        
    Returns:
        Dict with 'success', 'call_sid' or 'error'
    """
    config = None
    if all([account_sid, auth_token, from_number]):
        config = TwilioConfig(
            account_sid=account_sid,
            auth_token=auth_token,
            phone_number=from_number,
        )
    
    backend = TwilioBackend(twilio_config=config)
    
    # Run async in sync context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        call_sid, error = loop.run_until_complete(backend.make_call(to_number))
    finally:
        loop.close()
    
    if error:
        return {"success": False, "error": error}
    return {"success": True, "call_sid": call_sid, "message": f"📞 Calling {to_number}..."}


async def initiate_call(
    to_number: str,
    account_sid: Optional[str] = None,
    auth_token: Optional[str] = None,
    from_number: Optional[str] = None,
    system_prompt: Optional[str] = None,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Initiate a phone call.
    
    Args:
        to_number: Phone number to call
        account_sid: Twilio Account SID
        auth_token: Twilio Auth Token
        from_number: Twilio phone number
        system_prompt: System prompt for the AI
        
    Returns:
        Tuple of (status_message, error_message)
    """
    config = None
    if all([account_sid, auth_token, from_number]):
        config = TwilioConfig(
            account_sid=account_sid,
            auth_token=auth_token,
            phone_number=from_number,
        )
    
    call_config = CallConfig(system_prompt=system_prompt or "You are a helpful AI phone assistant.")
    backend = TwilioBackend(twilio_config=config, call_config=call_config)
    
    # Validate first
    is_valid, validation_error = backend.validate_config()
    if not is_valid:
        return None, validation_error
    
    # Make the call
    call_sid, error = await backend.make_call(to_number)
    
    if error:
        return None, error
    
    return f"📞 Calling {to_number}... (Call ID: {call_sid})", None
