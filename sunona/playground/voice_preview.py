"""
Sunona Voice AI - Voice Preview

Browser-based agent testing without making real calls.
Enables users to test their agents before deployment.

Features:
- WebSocket-based audio streaming
- Text-to-speech preview
- Simulated conversations
- Audio recording/playback
"""

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Awaitable

logger = logging.getLogger(__name__)


class PreviewMode(Enum):
    """Preview modes."""
    TEXT = "text"          # Text-based (no audio)
    TTS_ONLY = "tts_only"  # Listen to TTS output
    FULL_VOICE = "full_voice"  # Full voice interaction


class PreviewState(Enum):
    """Preview session states."""
    IDLE = "idle"
    CONNECTING = "connecting"
    READY = "ready"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ENDED = "ended"


@dataclass
class PreviewMessage:
    """A message in the preview conversation."""
    id: str
    role: str  # "user" or "assistant"
    content: str
    audio_url: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "audio_url": self.audio_url,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class PreviewSession:
    """An active preview session."""
    id: str
    agent_id: str
    user_id: Optional[str] = None
    mode: PreviewMode = PreviewMode.TEXT
    state: PreviewState = PreviewState.IDLE
    
    # Conversation
    messages: List[PreviewMessage] = field(default_factory=list)
    
    # Configuration override
    config_override: Dict[str, Any] = field(default_factory=dict)
    
    # Metrics
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    message_count: int = 0
    total_latency_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "mode": self.mode.value,
            "state": self.state.value,
            "messages": [m.to_dict() for m in self.messages],
            "started_at": self.started_at.isoformat(),
            "message_count": self.message_count,
            "avg_latency_ms": self.total_latency_ms / max(1, self.message_count),
        }


class VoicePreviewService:
    """
    Voice preview service for testing agents.
    
    Allows users to test agent configurations in the browser
    without making actual phone calls.
    
    Example:
        preview = VoicePreviewService()
        
        # Start text preview
        session = await preview.start_session(
            agent_id="agent_123",
            mode=PreviewMode.TEXT
        )
        
        # Send message
        response = await preview.send_message(session.id, "Hello there!")
        
        # Get TTS audio
        audio = await preview.get_audio(session.id, response.id)
    """
    
    def __init__(
        self,
        agent_manager: Optional[Any] = None,
        synthesizer_factory: Optional[Callable] = None,
    ):
        """
        Initialize voice preview service.
        
        Args:
            agent_manager: Agent manager for loading agents
            synthesizer_factory: Factory for creating TTS synthesizers
        """
        self.agent_manager = agent_manager
        self.synthesizer_factory = synthesizer_factory
        
        self._sessions: Dict[str, PreviewSession] = {}
        self._agents: Dict[str, Any] = {}  # Cached agent instances
    
    async def start_session(
        self,
        agent_id: str,
        user_id: Optional[str] = None,
        mode: PreviewMode = PreviewMode.TEXT,
        config_override: Optional[Dict[str, Any]] = None,
    ) -> PreviewSession:
        """
        Start a new preview session.
        
        Args:
            agent_id: Agent to preview
            user_id: User ID for tracking
            mode: Preview mode
            config_override: Override agent config for testing
        
        Returns:
            PreviewSession
        """
        session_id = f"preview_{uuid.uuid4().hex[:12]}"
        
        session = PreviewSession(
            id=session_id,
            agent_id=agent_id,
            user_id=user_id,
            mode=mode,
            state=PreviewState.READY,
            config_override=config_override or {},
        )
        
        self._sessions[session_id] = session
        
        # Add welcome message if configured
        welcome = config_override.get("welcome_message") if config_override else None
        if welcome:
            msg = PreviewMessage(
                id=f"msg_{uuid.uuid4().hex[:8]}",
                role="assistant",
                content=welcome,
            )
            session.messages.append(msg)
            session.message_count += 1
        
        logger.info(f"Started preview session {session_id} for agent {agent_id}")
        return session
    
    async def send_message(
        self,
        session_id: str,
        text: str,
    ) -> Optional[PreviewMessage]:
        """
        Send a text message to the agent.
        
        Args:
            session_id: Session ID
            text: User message text
        
        Returns:
            Agent's response message
        """
        session = self._sessions.get(session_id)
        if not session:
            return None
        
        # Record user message
        user_msg = PreviewMessage(
            id=f"msg_{uuid.uuid4().hex[:8]}",
            role="user",
            content=text,
        )
        session.messages.append(user_msg)
        
        session.state = PreviewState.PROCESSING
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Get agent response
            response_text = await self._get_agent_response(session, text)
            
            latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            session.total_latency_ms += latency_ms
            
            # Create response message
            response_msg = PreviewMessage(
                id=f"msg_{uuid.uuid4().hex[:8]}",
                role="assistant",
                content=response_text,
            )
            session.messages.append(response_msg)
            session.message_count += 1
            
            session.state = PreviewState.READY
            
            return response_msg
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            session.state = PreviewState.READY
            
            # Return error message
            error_msg = PreviewMessage(
                id=f"msg_{uuid.uuid4().hex[:8]}",
                role="assistant",
                content=f"Sorry, I encountered an error: {str(e)}",
            )
            session.messages.append(error_msg)
            return error_msg
    
    async def send_audio(
        self,
        session_id: str,
        audio_data: bytes,
    ) -> Optional[PreviewMessage]:
        """
        Send audio data to the agent (for full voice mode).
        
        Args:
            session_id: Session ID
            audio_data: Audio bytes (PCM or WAV)
        
        Returns:
            Agent's response message with audio
        """
        session = self._sessions.get(session_id)
        if not session:
            return None
        
        if session.mode != PreviewMode.FULL_VOICE:
            return None
        
        session.state = PreviewState.LISTENING
        
        # Transcribe audio
        transcript = await self._transcribe_audio(session, audio_data)
        
        if not transcript:
            session.state = PreviewState.READY
            return None
        
        # Process as text message
        return await self.send_message(session_id, transcript)
    
    async def get_audio(
        self,
        session_id: str,
        message_id: str,
    ) -> Optional[bytes]:
        """
        Get TTS audio for a message.
        
        Args:
            session_id: Session ID
            message_id: Message ID
        
        Returns:
            Audio bytes (WAV format)
        """
        session = self._sessions.get(session_id)
        if not session:
            return None
        
        # Find message
        message = None
        for msg in session.messages:
            if msg.id == message_id:
                message = msg
                break
        
        if not message or message.role != "assistant":
            return None
        
        # Generate TTS
        audio = await self._synthesize_audio(session, message.content)
        return audio
    
    async def get_session(self, session_id: str) -> Optional[PreviewSession]:
        """Get session by ID."""
        return self._sessions.get(session_id)
    
    async def get_history(self, session_id: str) -> List[PreviewMessage]:
        """Get conversation history."""
        session = self._sessions.get(session_id)
        if not session:
            return []
        return session.messages.copy()
    
    async def end_session(self, session_id: str) -> bool:
        """End a preview session."""
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        session.state = PreviewState.ENDED
        
        # Clean up
        del self._sessions[session_id]
        
        logger.info(f"Ended preview session {session_id}")
        return True
    
    async def _get_agent_response(
        self,
        session: PreviewSession,
        user_message: str,
    ) -> str:
        """Get response from agent."""
        # Build conversation history
        messages = []
        
        # Add system prompt from config
        system_prompt = session.config_override.get("system_prompt")
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt,
            })
        
        # Add conversation history
        for msg in session.messages[-10:]:  # Last 10 messages
            messages.append({
                "role": msg.role,
                "content": msg.content,
            })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": user_message,
        })
        
        # Use agent manager if available
        if self.agent_manager:
            try:
                response = await self.agent_manager.process_message(
                    session.agent_id,
                    user_message,
                    session_id=session.id,
                )
                return response
            except Exception as e:
                logger.error(f"Agent manager error: {e}")
        
        # Fallback: simple echo response for testing
        return f"[Preview] You said: {user_message}"
    
    async def _transcribe_audio(
        self,
        session: PreviewSession,
        audio_data: bytes,
    ) -> Optional[str]:
        """Transcribe audio to text."""
        # This would use the configured transcriber
        # For now, return placeholder
        return None
    
    async def _synthesize_audio(
        self,
        session: PreviewSession,
        text: str,
    ) -> Optional[bytes]:
        """Synthesize text to audio."""
        if not self.synthesizer_factory:
            return None
        
        try:
            # Get synthesizer config from override
            tts_config = session.config_override.get("tts", {})
            
            synthesizer = self.synthesizer_factory(
                provider=tts_config.get("provider", "openai"),
                voice=tts_config.get("voice", "alloy"),
            )
            
            audio = await synthesizer.synthesize(text)
            return audio
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        return {
            "active_sessions": len(self._sessions),
            "total_messages": sum(s.message_count for s in self._sessions.values()),
        }


# Global preview service
_global_preview: Optional[VoicePreviewService] = None


def get_voice_preview() -> VoicePreviewService:
    """Get or create global voice preview service."""
    global _global_preview
    if _global_preview is None:
        _global_preview = VoicePreviewService()
    return _global_preview
