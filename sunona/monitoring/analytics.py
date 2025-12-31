"""
Sunona Voice AI - Analytics

Conversation and usage analytics for voice AI agents.
Tracks metrics for performance analysis and optimization.

Features:
- Conversation-level metrics
- Latency tracking (P50, P90, P99)
- Token usage tracking
- Success/failure rates
- Real-time aggregation
"""

import time
import asyncio
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from statistics import mean, median, quantiles
import json

logger = logging.getLogger(__name__)


@dataclass
class ConversationMetrics:
    """
    Metrics for a single conversation.
    
    Attributes:
        conversation_id: Unique conversation identifier
        agent_id: Agent handling the conversation
        start_time: Conversation start timestamp
        end_time: Conversation end timestamp
        turn_count: Number of conversation turns
        total_tokens: Total tokens used
        total_latency_ms: Total processing latency
        transcription_latency_ms: STT latency
        llm_latency_ms: LLM response latency
        synthesis_latency_ms: TTS latency
        successful: Whether conversation completed successfully
        error: Error message if failed
    """
    conversation_id: str
    agent_id: str
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    turn_count: int = 0
    total_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_latency_ms: float = 0.0
    transcription_latency_ms: float = 0.0
    llm_latency_ms: float = 0.0
    synthesis_latency_ms: float = 0.0
    successful: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration_seconds(self) -> float:
        """Get conversation duration in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return (datetime.now() - self.start_time).total_seconds()
    
    @property
    def avg_turn_latency_ms(self) -> float:
        """Get average latency per turn."""
        if self.turn_count == 0:
            return 0.0
        return self.total_latency_ms / self.turn_count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "conversation_id": self.conversation_id,
            "agent_id": self.agent_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "turn_count": self.turn_count,
            "total_tokens": self.total_tokens,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_latency_ms": self.total_latency_ms,
            "transcription_latency_ms": self.transcription_latency_ms,
            "llm_latency_ms": self.llm_latency_ms,
            "synthesis_latency_ms": self.synthesis_latency_ms,
            "avg_turn_latency_ms": self.avg_turn_latency_ms,
            "successful": self.successful,
            "error": self.error,
            "metadata": self.metadata,
        }


@dataclass
class TurnMetrics:
    """Metrics for a single conversation turn."""
    turn_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    user_input: str = ""
    assistant_output: str = ""
    transcription_latency_ms: float = 0.0
    llm_latency_ms: float = 0.0
    synthesis_latency_ms: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    
    @property
    def total_latency_ms(self) -> float:
        return self.transcription_latency_ms + self.llm_latency_ms + self.synthesis_latency_ms


class Analytics:
    """
    Analytics collector for voice AI conversations.
    
    Tracks and aggregates metrics for conversations, turns, and providers.
    Supports real-time querying and historical analysis.
    
    Example:
        ```python
        analytics = Analytics()
        
        # Start tracking conversation
        conv_id = analytics.start_conversation("agent_1")
        
        # Track turns
        analytics.record_turn(
            conv_id,
            transcription_latency_ms=150,
            llm_latency_ms=300,
            synthesis_latency_ms=100
        )
        
        # End conversation
        analytics.end_conversation(conv_id)
        
        # Get metrics
        summary = analytics.get_summary()
        ```
    """
    
    def __init__(
        self,
        retention_days: int = 30,
        enable_persistence: bool = False,
        persistence_path: Optional[str] = None,
    ):
        """
        Initialize analytics.
        
        Args:
            retention_days: Days to retain metrics
            enable_persistence: Whether to persist to disk
            persistence_path: Path for persistence file
        """
        self.retention_days = retention_days
        self.enable_persistence = enable_persistence
        self.persistence_path = persistence_path
        
        self._conversations: Dict[str, ConversationMetrics] = {}
        self._completed_conversations: List[ConversationMetrics] = []
        self._turns: Dict[str, List[TurnMetrics]] = defaultdict(list)
        
        # Aggregate counters
        self._total_conversations = 0
        self._total_turns = 0
        self._total_tokens = 0
        self._latencies: List[float] = []
        
        logger.info("Analytics initialized")
    
    def start_conversation(
        self,
        agent_id: str,
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Start tracking a new conversation.
        
        Args:
            agent_id: Agent handling the conversation
            conversation_id: Optional custom ID
            metadata: Additional metadata
            
        Returns:
            Conversation ID
        """
        import uuid
        
        conv_id = conversation_id or str(uuid.uuid4())
        
        metrics = ConversationMetrics(
            conversation_id=conv_id,
            agent_id=agent_id,
            metadata=metadata or {},
        )
        
        self._conversations[conv_id] = metrics
        self._total_conversations += 1
        
        logger.debug(f"Started conversation: {conv_id}")
        return conv_id
    
    def record_turn(
        self,
        conversation_id: str,
        transcription_latency_ms: float = 0.0,
        llm_latency_ms: float = 0.0,
        synthesis_latency_ms: float = 0.0,
        input_tokens: int = 0,
        output_tokens: int = 0,
        user_input: str = "",
        assistant_output: str = "",
    ) -> None:
        """
        Record metrics for a conversation turn.
        
        Args:
            conversation_id: Conversation to update
            transcription_latency_ms: STT latency in ms
            llm_latency_ms: LLM latency in ms
            synthesis_latency_ms: TTS latency in ms
            input_tokens: Input token count
            output_tokens: Output token count
            user_input: User's input text
            assistant_output: Assistant's response
        """
        if conversation_id not in self._conversations:
            logger.warning(f"Unknown conversation: {conversation_id}")
            return
        
        conv = self._conversations[conversation_id]
        
        # Update conversation metrics
        conv.turn_count += 1
        conv.transcription_latency_ms += transcription_latency_ms
        conv.llm_latency_ms += llm_latency_ms
        conv.synthesis_latency_ms += synthesis_latency_ms
        conv.total_latency_ms += (transcription_latency_ms + llm_latency_ms + synthesis_latency_ms)
        conv.input_tokens += input_tokens
        conv.output_tokens += output_tokens
        conv.total_tokens += (input_tokens + output_tokens)
        
        # Record turn
        turn = TurnMetrics(
            turn_id=f"{conversation_id}_{conv.turn_count}",
            user_input=user_input,
            assistant_output=assistant_output,
            transcription_latency_ms=transcription_latency_ms,
            llm_latency_ms=llm_latency_ms,
            synthesis_latency_ms=synthesis_latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
        
        self._turns[conversation_id].append(turn)
        
        # Update aggregates
        self._total_turns += 1
        self._total_tokens += (input_tokens + output_tokens)
        self._latencies.append(turn.total_latency_ms)
    
    def end_conversation(
        self,
        conversation_id: str,
        successful: bool = True,
        error: Optional[str] = None,
    ) -> Optional[ConversationMetrics]:
        """
        End a conversation and finalize metrics.
        
        Args:
            conversation_id: Conversation to end
            successful: Whether completed successfully
            error: Error message if failed
            
        Returns:
            Final conversation metrics
        """
        if conversation_id not in self._conversations:
            logger.warning(f"Unknown conversation: {conversation_id}")
            return None
        
        conv = self._conversations[conversation_id]
        conv.end_time = datetime.now()
        conv.successful = successful
        conv.error = error
        
        # Move to completed
        self._completed_conversations.append(conv)
        del self._conversations[conversation_id]
        
        logger.debug(f"Ended conversation: {conversation_id} (success={successful})")
        
        return conv
    
    def get_conversation_metrics(self, conversation_id: str) -> Optional[ConversationMetrics]:
        """Get metrics for a specific conversation."""
        if conversation_id in self._conversations:
            return self._conversations[conversation_id]
        
        for conv in self._completed_conversations:
            if conv.conversation_id == conversation_id:
                return conv
        
        return None
    
    def get_summary(
        self,
        agent_id: Optional[str] = None,
        since: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get summary analytics.
        
        Args:
            agent_id: Filter by agent
            since: Filter by start time
            
        Returns:
            Summary dictionary
        """
        # Combine active and completed conversations
        all_conversations = list(self._conversations.values()) + self._completed_conversations
        
        # Apply filters
        if agent_id:
            all_conversations = [c for c in all_conversations if c.agent_id == agent_id]
        if since:
            all_conversations = [c for c in all_conversations if c.start_time >= since]
        
        if not all_conversations:
            return {
                "total_conversations": 0,
                "total_turns": 0,
                "total_tokens": 0,
            }
        
        # Calculate aggregates
        total_turns = sum(c.turn_count for c in all_conversations)
        total_tokens = sum(c.total_tokens for c in all_conversations)
        successful = [c for c in all_conversations if c.successful]
        
        latencies = [c.total_latency_ms for c in all_conversations if c.total_latency_ms > 0]
        
        return {
            "total_conversations": len(all_conversations),
            "active_conversations": len(self._conversations),
            "completed_conversations": len(self._completed_conversations),
            "total_turns": total_turns,
            "total_tokens": total_tokens,
            "success_rate": len(successful) / len(all_conversations) if all_conversations else 0,
            "avg_turn_latency_ms": mean([c.avg_turn_latency_ms for c in all_conversations]) if all_conversations else 0,
            "latency_p50_ms": median(latencies) if latencies else 0,
            "latency_p90_ms": quantiles(latencies, n=10)[8] if len(latencies) >= 10 else max(latencies) if latencies else 0,
            "avg_turns_per_conversation": total_turns / len(all_conversations) if all_conversations else 0,
        }
    
    def get_agent_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get per-agent summary."""
        agents = defaultdict(list)
        
        for conv in list(self._conversations.values()) + self._completed_conversations:
            agents[conv.agent_id].append(conv)
        
        return {
            agent_id: {
                "conversation_count": len(convs),
                "total_turns": sum(c.turn_count for c in convs),
                "avg_turn_latency_ms": mean([c.avg_turn_latency_ms for c in convs]) if convs else 0,
            }
            for agent_id, convs in agents.items()
        }
    
    def export_metrics(self, format: str = "json") -> str:
        """Export all metrics."""
        data = {
            "summary": self.get_summary(),
            "agent_summary": self.get_agent_summary(),
            "conversations": [c.to_dict() for c in self._completed_conversations],
        }
        
        if format == "json":
            return json.dumps(data, indent=2, default=str)
        
        raise ValueError(f"Unsupported format: {format}")
    
    def clear(self) -> None:
        """Clear all metrics."""
        self._conversations.clear()
        self._completed_conversations.clear()
        self._turns.clear()
        self._latencies.clear()
        self._total_conversations = 0
        self._total_turns = 0
        self._total_tokens = 0
