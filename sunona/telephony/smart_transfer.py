"""
Sunona Voice AI - Smart Call Transfer

Intelligently transfers calls to human agents when:
- AI cannot answer the question (out of context)
- Customer requests human assistance
- High-value or sensitive conversations

Seamless transfer without awkward announcements.
"""

import asyncio
import logging
import re
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class TransferReason(Enum):
    """Why the call is being transferred."""
    OUT_OF_CONTEXT = "out_of_context"        # AI doesn't know the answer
    CUSTOMER_REQUEST = "customer_request"     # Customer asked for human
    SENSITIVE_TOPIC = "sensitive_topic"       # Billing, complaints, etc.
    HIGH_VALUE = "high_value"                 # Sales opportunity
    ESCALATION = "escalation"                  # Issue needs escalation
    TIMEOUT = "timeout"                        # AI taking too long


@dataclass
class TransferConfig:
    """Configuration for call transfers."""
    # Phone number to transfer to
    transfer_number: str
    
    # Business owner/manager name
    agent_name: str = "our specialist"
    
    # Transfer messages (seamless, no awkward announcements)
    connecting_message: str = "One moment please..."
    
    # Topics that trigger transfer
    sensitive_topics: List[str] = field(default_factory=lambda: [
        "refund", "complaint", "cancel", "lawsuit", "legal",
        "billing issue", "payment problem", "fraud", "scam",
    ])
    
    # Phrases that indicate customer wants human
    human_request_phrases: List[str] = field(default_factory=lambda: [
        "speak to human", "talk to person", "real person",
        "human agent", "manager", "supervisor", "representative",
        "someone else", "actual person", "not a robot",
    ])
    
    # Confidence threshold - below this, consider transfer
    confidence_threshold: float = 0.5
    
    # Max consecutive "I don't know" before transfer
    max_unknown_responses: int = 2


class SmartCallTransfer:
    """
    Intelligently detects when to transfer calls to humans.
    
    Features:
    - Detects out-of-context questions
    - Recognizes customer frustration
    - Seamless transfer without awkward messaging
    - Tracks conversation context
    
    Example:
        ```python
        transfer = SmartCallTransfer(
            config=TransferConfig(
                transfer_number="+1234567890",
                agent_name="John",
            )
        )
        
        # Check if response should trigger transfer
        should_transfer, reason = transfer.should_transfer(
            user_message="I want to speak to a manager",
            ai_response="I can help you with that...",
            confidence=0.3,
        )
        
        if should_transfer:
            # Execute seamless transfer
            transfer_response = transfer.execute_transfer(reason)
        ```
    """
    
    # Phrases indicating AI doesn't know
    UNKNOWN_INDICATORS = [
        "i don't have information",
        "i'm not sure about",
        "i don't know",
        "i cannot answer",
        "outside my knowledge",
        "i'm unable to",
        "let me connect you",
        "i'd recommend speaking",
    ]
    
    def __init__(
        self,
        config: TransferConfig,
        knowledge_base: Optional[Any] = None,
    ):
        self.config = config
        self.knowledge_base = knowledge_base
        
        # Conversation tracking
        self._unknown_count = 0
        self._conversation_history: List[Dict] = []
        self._transfer_initiated = False
    
    def should_transfer(
        self,
        user_message: str,
        ai_response: str,
        confidence: float = 1.0,
    ) -> tuple[bool, Optional[TransferReason]]:
        """
        Determine if call should be transferred.
        
        Args:
            user_message: What the customer said
            ai_response: What the AI responded
            confidence: AI's confidence in its response (0-1)
            
        Returns:
            (should_transfer, reason)
        """
        user_lower = user_message.lower()
        response_lower = ai_response.lower()
        
        # Track conversation
        self._conversation_history.append({
            "user": user_message,
            "ai": ai_response,
            "confidence": confidence,
            "timestamp": datetime.now(),
        })
        
        # Check 1: Customer explicitly wants human
        for phrase in self.config.human_request_phrases:
            if phrase in user_lower:
                logger.info(f"Transfer triggered: Customer requested human ({phrase})")
                return True, TransferReason.CUSTOMER_REQUEST
        
        # Check 2: Sensitive topic
        for topic in self.config.sensitive_topics:
            if topic in user_lower:
                logger.info(f"Transfer triggered: Sensitive topic ({topic})")
                return True, TransferReason.SENSITIVE_TOPIC
        
        # Check 3: AI doesn't know the answer
        for indicator in self.UNKNOWN_INDICATORS:
            if indicator in response_lower:
                self._unknown_count += 1
                logger.info(f"Unknown response detected ({self._unknown_count})")
                
                if self._unknown_count >= self.config.max_unknown_responses:
                    return True, TransferReason.OUT_OF_CONTEXT
        
        # Check 4: Low confidence
        if confidence < self.config.confidence_threshold:
            self._unknown_count += 1
            if self._unknown_count >= self.config.max_unknown_responses:
                logger.info("Transfer triggered: Low confidence repeated")
                return True, TransferReason.OUT_OF_CONTEXT
        else:
            # Reset unknown count on confident response
            self._unknown_count = 0
        
        # Check 5: Escalation phrases
        escalation_phrases = [
            "not helpful", "useless", "frustrated", "angry",
            "this is ridiculous", "worst service", "terrible",
        ]
        for phrase in escalation_phrases:
            if phrase in user_lower:
                logger.info(f"Transfer triggered: Escalation ({phrase})")
                return True, TransferReason.ESCALATION
        
        return False, None
    
    def execute_transfer(
        self,
        reason: TransferReason,
        twilio_handler: Optional[Any] = None,
        call_sid: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute the call transfer seamlessly.
        
        Returns transfer actions to perform.
        """
        self._transfer_initiated = True
        
        # Get appropriate message based on reason
        message = self._get_transfer_message(reason)
        
        transfer_action = {
            "action": "transfer",
            "reason": reason.value,
            "transfer_to": self.config.transfer_number,
            "message_to_speak": message,
            "context": self._build_context_summary(),
        }
        
        # If Twilio handler provided, execute transfer
        if twilio_handler and call_sid:
            try:
                self._execute_twilio_transfer(
                    twilio_handler,
                    call_sid,
                    message,
                )
            except Exception as e:
                logger.error(f"Transfer execution error: {e}")
        
        logger.info(f"Transfer initiated: {reason.value} -> {self.config.transfer_number}")
        
        return transfer_action
    
    def _get_transfer_message(self, reason: TransferReason) -> str:
        """Get the message to speak before transfer (seamless, brief)."""
        messages = {
            TransferReason.OUT_OF_CONTEXT: "One moment, let me connect you with someone who can help.",
            TransferReason.CUSTOMER_REQUEST: "Of course. Connecting you now.",
            TransferReason.SENSITIVE_TOPIC: "I'll connect you with our team right away.",
            TransferReason.HIGH_VALUE: "Let me get our specialist for you.",
            TransferReason.ESCALATION: "I understand. Let me connect you with my colleague.",
            TransferReason.TIMEOUT: "Please hold while I connect you.",
        }
        return messages.get(reason, self.config.connecting_message)
    
    def _build_context_summary(self) -> str:
        """Build a summary of the conversation for the human agent."""
        if not self._conversation_history:
            return "No conversation history."
        
        # Last 5 exchanges
        recent = self._conversation_history[-5:]
        
        summary_lines = ["CONVERSATION SUMMARY:"]
        for entry in recent:
            summary_lines.append(f"Customer: {entry['user'][:100]}")
            summary_lines.append(f"AI: {entry['ai'][:100]}")
            summary_lines.append("")
        
        return "\n".join(summary_lines)
    
    def _execute_twilio_transfer(
        self,
        twilio_handler: Any,
        call_sid: str,
        message: str,
    ):
        """Execute actual Twilio call transfer."""
        # This would use Twilio's API to conference or transfer the call
        # For now, return the TwiML needed
        
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">{message}</Say>
    <Dial timeout="30" callerId="{twilio_handler.phone_number}">
        <Number>{self.config.transfer_number}</Number>
    </Dial>
</Response>"""
        
        return twiml
    
    def get_pre_transfer_response(self, reason: TransferReason) -> str:
        """
        Get AI response to say BEFORE initiating transfer.
        
        This makes the transition seamless without awkward pauses.
        """
        responses = {
            TransferReason.OUT_OF_CONTEXT: 
                "That's a great question. Let me connect you with someone "
                "from our team who specializes in this area.",
            
            TransferReason.CUSTOMER_REQUEST:
                "Absolutely. I'll connect you with a member of our team right away.",
            
            TransferReason.SENSITIVE_TOPIC:
                "I understand this is important. Let me get one of our specialists "
                "to assist you with this directly.",
            
            TransferReason.HIGH_VALUE:
                "This sounds like something where you'd benefit from speaking with "
                "one of our experts. Let me connect you.",
            
            TransferReason.ESCALATION:
                "I apologize for any frustration. Let me connect you with someone "
                "who can help resolve this for you right away.",
            
            TransferReason.TIMEOUT:
                "Please hold for just a moment while I connect you.",
        }
        
        return responses.get(reason, "One moment please, connecting you now.")
    
    def reset(self):
        """Reset conversation tracking for new call."""
        self._unknown_count = 0
        self._conversation_history = []
        self._transfer_initiated = False


class CallHandler:
    """
    Complete call handler with knowledge base and smart transfer.
    
    Combines:
    - Knowledge base for answering questions
    - Smart transfer for out-of-context
    - Seamless handoff to humans
    
    Example:
        ```python
        handler = CallHandler(
            knowledge_base=website_knowledge,
            transfer_config=TransferConfig(
                transfer_number="+1234567890"
            ),
        )
        
        # Process each message in conversation
        response = await handler.process_message(
            "What are your business hours?"
        )
        
        # If transfer needed, response includes transfer action
        if response.get("transfer"):
            # Execute transfer...
        ```
    """
    
    def __init__(
        self,
        knowledge_base: Any,
        transfer_config: TransferConfig,
        llm: Optional[Any] = None,
    ):
        self.knowledge_base = knowledge_base
        self.transfer = SmartCallTransfer(transfer_config, knowledge_base)
        self.llm = llm
    
    async def process_message(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """
        Process a message from the caller.
        
        Returns response with potential transfer action.
        """
        # Generate AI response
        ai_response, confidence = await self._generate_response(
            user_message,
            conversation_history,
        )
        
        # Check if transfer needed
        should_transfer, reason = self.transfer.should_transfer(
            user_message,
            ai_response,
            confidence,
        )
        
        result = {
            "response": ai_response,
            "confidence": confidence,
            "transfer": False,
        }
        
        if should_transfer and reason:
            # Get seamless pre-transfer response
            transfer_response = self.transfer.get_pre_transfer_response(reason)
            transfer_action = self.transfer.execute_transfer(reason)
            
            result.update({
                "response": transfer_response,
                "transfer": True,
                "transfer_reason": reason.value,
                "transfer_action": transfer_action,
            })
        
        return result
    
    async def _generate_response(
        self,
        message: str,
        history: Optional[List[Dict]],
    ) -> tuple[str, float]:
        """Generate AI response with confidence score."""
        # This would use the actual LLM
        # For now, return placeholder
        
        if self.llm:
            try:
                response = await self.llm.generate([
                    {"role": "user", "content": message}
                ])
                # Estimate confidence based on response content
                confidence = self._estimate_confidence(response)
                return response, confidence
            except Exception as e:
                logger.error(f"LLM error: {e}")
        
        return "I'm here to help. How can I assist you?", 0.8
    
    def _estimate_confidence(self, response: str) -> float:
        """Estimate confidence based on response content."""
        lower_response = response.lower()
        
        # Low confidence indicators
        low_indicators = [
            "i'm not sure", "i don't know", "i cannot",
            "sorry", "unfortunately", "might be", "could be",
        ]
        
        for indicator in low_indicators:
            if indicator in lower_response:
                return 0.4
        
        # High confidence if response is direct
        if len(response) > 50 and "?" not in response:
            return 0.9
        
        return 0.7


# Convenience function
def create_call_handler(
    transfer_number: str,
    knowledge_base: Any = None,
    agent_name: str = "our team",
) -> CallHandler:
    """
    Create a call handler with smart transfer.
    
    Args:
        transfer_number: Number to transfer to when needed
        knowledge_base: Optional knowledge base for answering questions
        agent_name: Name to use when referring to human agents
        
    Returns:
        Configured CallHandler
    """
    config = TransferConfig(
        transfer_number=transfer_number,
        agent_name=agent_name,
    )
    
    return CallHandler(
        knowledge_base=knowledge_base,
        transfer_config=config,
    )
