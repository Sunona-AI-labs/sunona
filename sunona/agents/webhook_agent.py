"""
Sunona Voice AI - Webhook Agent

Agent that triggers webhooks during conversations.
Sends real-time data to external systems.
"""

import asyncio
import logging
import json
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

# Try to import HTTP client
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class WebhookEvent(Enum):
    """Types of webhook events."""
    CALL_STARTED = "call.started"
    CALL_ENDED = "call.ended"
    MESSAGE_RECEIVED = "message.received"
    MESSAGE_SENT = "message.sent"
    TRANSFER_INITIATED = "transfer.initiated"
    DATA_EXTRACTED = "data.extracted"
    CUSTOM = "custom"


@dataclass
class WebhookTrigger:
    """Configuration for a webhook trigger."""
    event: WebhookEvent
    url: str
    method: str = "POST"
    headers: Dict[str, str] = field(default_factory=dict)
    include_conversation: bool = False
    retry_count: int = 3
    timeout: float = 10.0
    condition: Optional[Callable] = None  # Optional condition to check


@dataclass
class WebhookResult:
    """Result of a webhook call."""
    event: str
    url: str
    status_code: int
    success: bool
    response_data: Optional[Dict] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


from sunona.agents.base_agent import (
    BaseAgent, AgentConfig, AgentResponse, AgentCapability, AgentState
)


class WebhookAgent(BaseAgent):
    """
    Agent that sends webhooks during conversations.
    
    Features:
    - Configurable webhook triggers
    - Real-time event notifications
    - Custom event payloads
    - Retry on failure
    - Async (non-blocking) webhook calls
    
    Best for:
    - CRM integration
    - Real-time analytics
    - External system updates
    - Logging and monitoring
    
    Example:
        ```python
        agent = WebhookAgent()
        
        # Add webhook triggers
        agent.add_trigger(WebhookTrigger(
            event=WebhookEvent.CALL_STARTED,
            url="https://mycrm.com/webhooks/call-started",
        ))
        
        agent.add_trigger(WebhookTrigger(
            event=WebhookEvent.DATA_EXTRACTED,
            url="https://mycrm.com/webhooks/lead",
            include_conversation=True,
        ))
        
        # Start agent - triggers CALL_STARTED webhook
        await agent.start()
        
        # When data is extracted, triggers DATA_EXTRACTED webhook
        await agent.emit_event(WebhookEvent.DATA_EXTRACTED, {"email": "john@example.com"})
        ```
    """
    
    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        llm: Optional[Any] = None,
    ):
        super().__init__(config, llm)
        
        self._triggers: Dict[WebhookEvent, List[WebhookTrigger]] = {}
        self._webhook_history: List[WebhookResult] = []
        self._call_id: Optional[str] = None
        
        # Async webhook queue
        self._webhook_queue: List[asyncio.Task] = []
    
    @property
    def capabilities(self) -> List[AgentCapability]:
        return [AgentCapability.WEBHOOK, AgentCapability.CONVERSATION]
    
    def add_trigger(self, trigger: WebhookTrigger):
        """Add a webhook trigger."""
        if trigger.event not in self._triggers:
            self._triggers[trigger.event] = []
        self._triggers[trigger.event].append(trigger)
        logger.info(f"Added webhook trigger: {trigger.event.value} -> {trigger.url}")
    
    def add_triggers(self, triggers: List[WebhookTrigger]):
        """Add multiple triggers."""
        for trigger in triggers:
            self.add_trigger(trigger)
    
    async def start(self, call_id: Optional[str] = None):
        """Start agent and emit CALL_STARTED."""
        await super().start()
        self._call_id = call_id or f"call_{int(datetime.now().timestamp())}"
        
        await self.emit_event(WebhookEvent.CALL_STARTED, {
            "call_id": self._call_id,
            "agent_name": self.config.name,
            "started_at": datetime.now().isoformat(),
        })
    
    async def end(self, reason: str = "completed"):
        """End agent and emit CALL_ENDED."""
        await self.emit_event(WebhookEvent.CALL_ENDED, {
            "call_id": self._call_id,
            "reason": reason,
            "turns": self.turn_count,
            "ended_at": datetime.now().isoformat(),
        })
        
        # Wait for pending webhooks
        await self._wait_for_webhooks()
        
        await super().end(reason)
    
    async def process_message(self, message: str) -> AgentResponse:
        """Process message and emit webhooks."""
        self._set_state(AgentState.LISTENING)
        self.add_message("user", message)
        
        # Emit MESSAGE_RECEIVED webhook
        await self.emit_event(WebhookEvent.MESSAGE_RECEIVED, {
            "call_id": self._call_id,
            "message": message,
            "turn": self.turn_count,
        })
        
        # Generate response
        self._set_state(AgentState.THINKING)
        response = await self.generate_response()
        self.add_message("assistant", response)
        
        # Emit MESSAGE_SENT webhook
        await self.emit_event(WebhookEvent.MESSAGE_SENT, {
            "call_id": self._call_id,
            "message": response,
            "turn": self.turn_count,
        })
        
        self._set_state(AgentState.SPEAKING)
        
        return AgentResponse(
            text=response,
            data={
                "webhooks_sent": len([r for r in self._webhook_history if r.success]),
            },
        )
    
    async def emit_event(
        self,
        event: WebhookEvent,
        data: Dict[str, Any],
        include_conversation: Optional[bool] = None,
    ):
        """
        Emit a webhook event.
        
        Args:
            event: Event type
            data: Event data payload
            include_conversation: Override trigger setting
        """
        triggers = self._triggers.get(event, [])
        
        for trigger in triggers:
            # Check condition if present
            if trigger.condition:
                try:
                    if not trigger.condition(data):
                        continue
                except Exception:
                    continue
            
            # Build payload
            payload = {
                "event": event.value,
                "timestamp": datetime.now().isoformat(),
                "data": data,
            }
            
            # Include conversation if requested
            inc_conv = include_conversation if include_conversation is not None else trigger.include_conversation
            if inc_conv:
                payload["conversation"] = [
                    {"role": t.role, "content": t.content}
                    for t in self.conversation_history
                    if t.role != "system"
                ]
            
            # Send webhook (async)
            task = asyncio.create_task(
                self._send_webhook(trigger, payload)
            )
            self._webhook_queue.append(task)
    
    async def emit_custom_event(self, event_name: str, data: Dict[str, Any]):
        """Emit a custom webhook event."""
        # Look for custom triggers
        triggers = self._triggers.get(WebhookEvent.CUSTOM, [])
        
        for trigger in triggers:
            payload = {
                "event": event_name,
                "timestamp": datetime.now().isoformat(),
                "data": data,
            }
            
            task = asyncio.create_task(
                self._send_webhook(trigger, payload)
            )
            self._webhook_queue.append(task)
    
    async def _send_webhook(
        self,
        trigger: WebhookTrigger,
        payload: Dict[str, Any],
    ) -> WebhookResult:
        """Send a webhook with retries."""
        if not HTTPX_AVAILABLE:
            logger.warning("httpx not available for webhooks")
            return WebhookResult(
                event=payload.get("event", "unknown"),
                url=trigger.url,
                status_code=0,
                success=False,
                error="httpx not installed",
            )
        
        headers = {
            "Content-Type": "application/json",
            **trigger.headers,
        }
        
        for attempt in range(trigger.retry_count):
            try:
                async with httpx.AsyncClient(timeout=trigger.timeout) as client:
                    if trigger.method.upper() == "POST":
                        response = await client.post(
                            trigger.url,
                            json=payload,
                            headers=headers,
                        )
                    else:
                        response = await client.get(
                            trigger.url,
                            params=payload,
                            headers=headers,
                        )
                    
                    result = WebhookResult(
                        event=payload.get("event", "unknown"),
                        url=trigger.url,
                        status_code=response.status_code,
                        success=response.is_success,
                    )
                    
                    if response.is_success:
                        try:
                            result.response_data = response.json()
                        except Exception:
                            pass
                        
                        logger.info(f"Webhook sent: {trigger.url} ({result.status_code})")
                        self._webhook_history.append(result)
                        return result
                    
            except Exception as e:
                logger.warning(f"Webhook attempt {attempt+1} failed: {e}")
                
                if attempt < trigger.retry_count - 1:
                    await asyncio.sleep(1 * (attempt + 1))  # Backoff
        
        # All retries failed
        result = WebhookResult(
            event=payload.get("event", "unknown"),
            url=trigger.url,
            status_code=0,
            success=False,
            error="All retries failed",
        )
        self._webhook_history.append(result)
        logger.error(f"Webhook failed after {trigger.retry_count} attempts: {trigger.url}")
        
        return result
    
    async def _wait_for_webhooks(self):
        """Wait for all pending webhooks to complete."""
        if self._webhook_queue:
            await asyncio.gather(*self._webhook_queue, return_exceptions=True)
            self._webhook_queue = []
    
    def get_webhook_history(self) -> List[Dict[str, Any]]:
        """Get webhook call history."""
        return [
            {
                "event": r.event,
                "url": r.url,
                "status_code": r.status_code,
                "success": r.success,
                "error": r.error,
                "timestamp": r.timestamp.isoformat(),
            }
            for r in self._webhook_history
        ]
    
    def get_webhook_stats(self) -> Dict[str, Any]:
        """Get webhook statistics."""
        total = len(self._webhook_history)
        successful = len([r for r in self._webhook_history if r.success])
        
        return {
            "total_webhooks": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": successful / total if total > 0 else 0,
            "triggers_configured": sum(len(t) for t in self._triggers.values()),
        }


# ==================== Pre-built Webhook Configurations ====================

def create_crm_webhook_agent(
    crm_base_url: str,
    api_key: Optional[str] = None,
    config: Optional[AgentConfig] = None,
) -> WebhookAgent:
    """Create an agent with CRM webhook integration."""
    agent = WebhookAgent(config=config)
    
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    agent.add_triggers([
        WebhookTrigger(
            event=WebhookEvent.CALL_STARTED,
            url=f"{crm_base_url}/api/calls/started",
            headers=headers,
        ),
        WebhookTrigger(
            event=WebhookEvent.CALL_ENDED,
            url=f"{crm_base_url}/api/calls/ended",
            headers=headers,
            include_conversation=True,
        ),
        WebhookTrigger(
            event=WebhookEvent.DATA_EXTRACTED,
            url=f"{crm_base_url}/api/leads",
            headers=headers,
        ),
    ])
    
    return agent


def create_analytics_webhook_agent(
    analytics_url: str,
    config: Optional[AgentConfig] = None,
) -> WebhookAgent:
    """Create an agent with analytics webhook integration."""
    agent = WebhookAgent(config=config)
    
    agent.add_triggers([
        WebhookTrigger(
            event=WebhookEvent.CALL_STARTED,
            url=analytics_url,
        ),
        WebhookTrigger(
            event=WebhookEvent.CALL_ENDED,
            url=analytics_url,
        ),
        WebhookTrigger(
            event=WebhookEvent.MESSAGE_RECEIVED,
            url=analytics_url,
        ),
        WebhookTrigger(
            event=WebhookEvent.MESSAGE_SENT,
            url=analytics_url,
        ),
    ])
    
    return agent
