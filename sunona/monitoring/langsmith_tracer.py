"""
Sunona Voice AI - LangSmith Integration

LangSmith observability for LLM tracing and debugging.
Provides detailed traces of LLM calls for optimization.

Features:
- LLM call tracing
- Latency tracking
- Token usage logging
- Error logging
- Feedback collection
"""

import os
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

# Try to import langsmith
try:
    from langsmith import Client as LangSmithClient
    from langsmith.run_trees import RunTree
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    LangSmithClient = None
    RunTree = None


@dataclass
class LLMTrace:
    """An LLM call trace."""
    run_id: str
    name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    input_messages: List[Dict[str, str]] = None
    output_message: Optional[str] = None
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = None


class LangSmithTracer:
    """
    LangSmith integration for LLM observability.
    
    Provides tracing for LLM calls to help debug and optimize
    voice AI conversations.
    
    Example:
        ```python
        tracer = LangSmithTracer(project_name="sunona-voice")
        
        async with tracer.trace_llm(
            name="chat_completion",
            model="gpt-4o-mini"
        ) as trace:
            response = await llm.generate(messages)
            trace.set_output(response)
        ```
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        project_name: str = "sunona-voice",
        enabled: bool = True,
    ):
        """
        Initialize LangSmith tracer.
        
        Args:
            api_key: LangSmith API key (or LANGSMITH_API_KEY env var)
            project_name: LangSmith project name
            enabled: Whether tracing is enabled
        """
        self.api_key = api_key or os.getenv("LANGSMITH_API_KEY")
        self.project_name = project_name
        self.enabled = enabled and LANGSMITH_AVAILABLE and self.api_key
        
        self._client: Optional[LangSmithClient] = None
        self._current_traces: Dict[str, Any] = {}
        
        if self.enabled:
            try:
                self._client = LangSmithClient(api_key=self.api_key)
                logger.info(f"LangSmith enabled for project: {project_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize LangSmith: {e}")
                self.enabled = False
        else:
            if not LANGSMITH_AVAILABLE:
                logger.info("LangSmith not available (install with: pip install langsmith)")
            elif not self.api_key:
                logger.info("LangSmith disabled (no API key)")
    
    @asynccontextmanager
    async def trace_llm(
        self,
        name: str,
        model: str,
        messages: Optional[List[Dict[str, str]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Trace an LLM call.
        
        Args:
            name: Trace name
            model: Model being used
            messages: Input messages
            metadata: Additional metadata
            
        Yields:
            Trace object for adding outputs
        """
        import uuid
        
        run_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        trace = LLMTrace(
            run_id=run_id,
            name=name,
            start_time=start_time,
            input_messages=messages or [],
            model=model,
            metadata=metadata or {},
        )
        
        try:
            # Start trace in LangSmith
            if self.enabled and self._client:
                try:
                    self._client.create_run(
                        name=name,
                        run_type="llm",
                        inputs={"messages": messages},
                        project_name=self.project_name,
                        id=run_id,
                        extra={"model": model, **(metadata or {})},
                    )
                except Exception as e:
                    logger.debug(f"LangSmith trace start error: {e}")
            
            yield trace
            
        except Exception as e:
            trace.error = str(e)
            raise
            
        finally:
            trace.end_time = datetime.now()
            trace.latency_ms = (trace.end_time - trace.start_time).total_seconds() * 1000
            
            # End trace in LangSmith
            if self.enabled and self._client:
                try:
                    self._client.update_run(
                        run_id=run_id,
                        end_time=trace.end_time,
                        outputs={"response": trace.output_message},
                        error=trace.error,
                        extra={
                            "input_tokens": trace.input_tokens,
                            "output_tokens": trace.output_tokens,
                            "latency_ms": trace.latency_ms,
                        },
                    )
                except Exception as e:
                    logger.debug(f"LangSmith trace end error: {e}")
    
    @asynccontextmanager
    async def trace_chain(
        self,
        name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Trace a chain/pipeline.
        
        Args:
            name: Chain name
            metadata: Additional metadata
        """
        import uuid
        
        run_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            if self.enabled and self._client:
                try:
                    self._client.create_run(
                        name=name,
                        run_type="chain",
                        inputs=metadata or {},
                        project_name=self.project_name,
                        id=run_id,
                    )
                except Exception as e:
                    logger.debug(f"LangSmith chain trace error: {e}")
            
            yield run_id
            
        finally:
            if self.enabled and self._client:
                try:
                    self._client.update_run(
                        run_id=run_id,
                        end_time=datetime.now(),
                    )
                except Exception as e:
                    logger.debug(f"LangSmith chain end error: {e}")
    
    def log_feedback(
        self,
        run_id: str,
        key: str,
        score: float,
        comment: Optional[str] = None,
    ) -> None:
        """
        Log feedback for a run.
        
        Args:
            run_id: Run ID to provide feedback for
            key: Feedback key (e.g., "user_satisfaction")
            score: Score (0-1)
            comment: Optional comment
        """
        if not self.enabled or not self._client:
            return
        
        try:
            self._client.create_feedback(
                run_id=run_id,
                key=key,
                score=score,
                comment=comment,
            )
        except Exception as e:
            logger.debug(f"LangSmith feedback error: {e}")
    
    def is_enabled(self) -> bool:
        """Check if tracing is enabled."""
        return self.enabled


class ConversationLogger:
    """
    Simple conversation logger for debugging.
    
    Logs all conversation turns with timing information.
    """
    
    def __init__(
        self,
        log_dir: Optional[str] = None,
        enabled: bool = True,
    ):
        """
        Initialize conversation logger.
        
        Args:
            log_dir: Directory for log files
            enabled: Whether logging is enabled
        """
        self.log_dir = log_dir or "./logs"
        self.enabled = enabled
        
        self._conversations: Dict[str, List[Dict[str, Any]]] = {}
    
    def log_turn(
        self,
        conversation_id: str,
        role: str,
        content: str,
        latency_ms: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log a conversation turn.
        
        Args:
            conversation_id: Conversation ID
            role: Speaker role (user, assistant, system)
            content: Message content
            latency_ms: Processing latency
            metadata: Additional metadata
        """
        if not self.enabled:
            return
        
        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = []
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content,
            "latency_ms": latency_ms,
            "metadata": metadata or {},
        }
        
        self._conversations[conversation_id].append(entry)
        logger.debug(f"[{conversation_id}] {role}: {content[:50]}...")
    
    def get_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get conversation history."""
        return self._conversations.get(conversation_id, [])
    
    def export_conversation(self, conversation_id: str) -> str:
        """Export conversation as formatted string."""
        turns = self.get_conversation(conversation_id)
        
        lines = [f"=== Conversation: {conversation_id} ===\n"]
        for turn in turns:
            lines.append(f"[{turn['timestamp']}] {turn['role'].upper()}:")
            lines.append(f"  {turn['content']}")
            if turn['latency_ms']:
                lines.append(f"  (latency: {turn['latency_ms']:.1f}ms)")
            lines.append("")
        
        return "\n".join(lines)
    
    def clear(self, conversation_id: Optional[str] = None) -> None:
        """Clear conversation logs."""
        if conversation_id:
            self._conversations.pop(conversation_id, None)
        else:
            self._conversations.clear()
