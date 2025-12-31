"""
Sunona Voice AI - Base Agent

The foundation class for all AI agents.
All specialized agents inherit from this base.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Agent lifecycle states."""
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    TRANSFERRING = "transferring"
    ENDED = "ended"


class AgentCapability(Enum):
    """Agent capabilities."""
    CONVERSATION = "conversation"
    EXTRACTION = "extraction"
    SUMMARIZATION = "summarization"
    KNOWLEDGE_BASE = "knowledge_base"
    WEBHOOK = "webhook"
    GRAPH_FLOW = "graph_flow"


@dataclass
class AgentConfig:
    """Configuration for an agent."""
    name: str = "AI Assistant"
    description: str = ""
    
    # LLM settings
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 500
    
    # System prompt
    system_prompt: str = "You are a helpful AI assistant."
    
    # Voice settings
    voice_id: str = "EXAVITQu4vr4xnSDxMaL"
    voice_speed: float = 1.0
    
    # Behavior
    max_conversation_turns: int = 50
    response_timeout: float = 30.0
    enable_interruption: bool = True
    
    # Transfer settings
    transfer_number: Optional[str] = None
    max_unknown_before_transfer: int = 2
    
    # Callback URLs
    webhook_url: Optional[str] = None
    
    # Custom data
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationTurn:
    """A single turn in the conversation."""
    role: str  # user, assistant, system
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    """Response from an agent."""
    text: str
    action: Optional[str] = None  # speak, transfer, end, etc.
    data: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    should_transfer: bool = False
    transfer_reason: Optional[str] = None


class BaseAgent(ABC):
    """
    Base class for all Sunona AI agents.
    
    Provides:
    - Conversation history management
    - LLM integration
    - State management
    - Event hooks
    
    Override:
    - process_message() - Handle incoming messages
    - generate_response() - Generate AI responses
    
    Example:
        ```python
        class MyAgent(BaseAgent):
            async def process_message(self, message: str) -> AgentResponse:
                # Custom processing logic
                response = await self.generate_response(message)
                return AgentResponse(text=response)
        
        agent = MyAgent(config)
        response = await agent.process_message("Hello!")
        ```
    """
    
    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        llm: Optional[Any] = None,
    ):
        self.config = config or AgentConfig()
        self.llm = llm
        
        # State
        self._state = AgentState.IDLE
        self._conversation: List[ConversationTurn] = []
        self._turn_count = 0
        self._unknown_count = 0
        
        # Callbacks
        self._on_state_change: Optional[Callable] = None
        self._on_response: Optional[Callable] = None
        self._on_transfer: Optional[Callable] = None
        self._on_end: Optional[Callable] = None
        
        # Initialize with system prompt
        if self.config.system_prompt:
            self._conversation.append(ConversationTurn(
                role="system",
                content=self.config.system_prompt,
            ))
    
    # ==================== Properties ====================
    
    @property
    def state(self) -> AgentState:
        """Current agent state."""
        return self._state
    
    @property
    def conversation_history(self) -> List[ConversationTurn]:
        """Full conversation history."""
        return self._conversation
    
    @property
    def turn_count(self) -> int:
        """Number of conversation turns."""
        return self._turn_count
    
    @property
    def capabilities(self) -> List[AgentCapability]:
        """Agent capabilities (override in subclasses)."""
        return [AgentCapability.CONVERSATION]
    
    # ==================== State Management ====================
    
    def _set_state(self, new_state: AgentState):
        """Update agent state."""
        old_state = self._state
        self._state = new_state
        
        if self._on_state_change:
            self._on_state_change(old_state, new_state)
        
        logger.debug(f"Agent state: {old_state.value} -> {new_state.value}")
    
    # ==================== Conversation ====================
    
    def add_message(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict] = None,
    ):
        """Add a message to conversation history."""
        self._conversation.append(ConversationTurn(
            role=role,
            content=content,
            metadata=metadata or {},
        ))
        
        if role == "user":
            self._turn_count += 1
    
    def get_messages_for_llm(self, max_messages: int = 20) -> List[Dict[str, str]]:
        """Get conversation in LLM format."""
        messages = []
        
        # Always include system prompt
        for turn in self._conversation:
            if turn.role == "system":
                messages.append({"role": "system", "content": turn.content})
                break
        
        # Add recent messages
        recent = [t for t in self._conversation if t.role != "system"][-max_messages:]
        for turn in recent:
            messages.append({"role": turn.role, "content": turn.content})
        
        return messages
    
    def clear_history(self):
        """Clear conversation history (keep system prompt)."""
        system_turns = [t for t in self._conversation if t.role == "system"]
        self._conversation = system_turns
        self._turn_count = 0
        self._unknown_count = 0
    
    # ==================== Core Methods (Override These) ====================
    
    @abstractmethod
    async def process_message(self, message: str) -> AgentResponse:
        """
        Process an incoming message and generate response.
        
        Override this in subclasses.
        
        Args:
            message: User's message
            
        Returns:
            AgentResponse with text and optional actions
        """
        pass
    
    async def generate_response(
        self,
        messages: Optional[List[Dict]] = None,
    ) -> str:
        """
        Generate LLM response.
        
        Args:
            messages: Optional custom messages, uses conversation if not provided
            
        Returns:
            Generated text response
        """
        if not self.llm:
            return "I'm here to help. How can I assist you?"
        
        self._set_state(AgentState.THINKING)
        
        try:
            llm_messages = messages or self.get_messages_for_llm()
            response = await self.llm.generate(llm_messages)
            return response
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return "I apologize, I'm having trouble processing that. Could you repeat?"
        finally:
            self._set_state(AgentState.IDLE)
    
    # ==================== Lifecycle ====================
    
    async def start(self):
        """Start the agent (called at beginning of call/session)."""
        self._set_state(AgentState.IDLE)
        logger.info(f"Agent started: {self.config.name}")
    
    async def end(self, reason: str = "completed"):
        """End the agent session."""
        self._set_state(AgentState.ENDED)
        
        if self._on_end:
            await self._on_end(reason)
        
        logger.info(f"Agent ended: {self.config.name} ({reason})")
    
    async def transfer(self, reason: str = "unknown"):
        """Transfer to human agent."""
        self._set_state(AgentState.TRANSFERRING)
        
        if self._on_transfer:
            await self._on_transfer(reason)
        
        logger.info(f"Agent transferring: {reason}")
        
        return AgentResponse(
            text="Let me connect you with someone who can help.",
            action="transfer",
            should_transfer=True,
            transfer_reason=reason,
        )
    
    # ==================== Callbacks ====================
    
    def on_state_change(self, callback: Callable):
        """Register state change callback."""
        self._on_state_change = callback
    
    def on_response(self, callback: Callable):
        """Register response callback."""
        self._on_response = callback
    
    def on_transfer(self, callback: Callable):
        """Register transfer callback."""
        self._on_transfer = callback
    
    def on_end(self, callback: Callable):
        """Register end callback."""
        self._on_end = callback
    
    # ==================== Utilities ====================
    
    def should_transfer_due_to_unknowns(self) -> bool:
        """Check if accumulated unknowns warrant transfer."""
        return self._unknown_count >= self.config.max_unknown_before_transfer
    
    def record_unknown(self):
        """Record that agent didn't know an answer."""
        self._unknown_count += 1
    
    def reset_unknown_count(self):
        """Reset unknown counter (after successful response)."""
        self._unknown_count = 0
    
    def get_summary(self) -> Dict[str, Any]:
        """Get agent session summary."""
        return {
            "name": self.config.name,
            "state": self._state.value,
            "turns": self._turn_count,
            "unknowns": self._unknown_count,
            "capabilities": [c.value for c in self.capabilities],
        }
