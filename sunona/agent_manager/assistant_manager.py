"""
Sunona Voice AI - Assistant Manager

High-level manager for coordinating multiple tasks within an agent.
"""

import asyncio
import logging
import uuid
from typing import AsyncIterator, Dict, Any, Optional, List

from sunona.agent_manager.base_manager import BaseManager
from sunona.agent_manager.task_manager import TaskManager, PipelineResult
from sunona.core import LogContext, SunonaError
try:
    from sunona.billing.usage_tracker import get_usage_tracker
    from sunona.billing.middleware import get_billing_manager
    HAS_BILLING = True
except ImportError:
    HAS_BILLING = False
    def get_usage_tracker(): return None
    def get_billing_manager(): return None

logger = logging.getLogger(__name__)


class AssistantManager(BaseManager):
    """
    Manages the execution of a complete voice AI assistant with multi-tenant support.
    
    Features:
        - Multi-task coordination
        - State management
        - WebSocket/queue integration
        - Event streaming
        - Multi-tenant traceability (org_id, user_id)
    """
    
    def __init__(
        self,
        agent_config: Dict[str, Any],
        prompts: Optional[Dict[str, Dict[str, str]]] = None,
        ws=None,
        input_queue: Optional[asyncio.Queue] = None,
        output_queue: Optional[asyncio.Queue] = None,
        organization_id: Optional[str] = None,
        user_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the assistant manager.
        """
        super().__init__(agent_config, **kwargs)
        
        self.prompts = prompts or {}
        self.ws = ws
        self.input_queue = input_queue or asyncio.Queue()
        self.output_queue = output_queue or asyncio.Queue()
        self.organization_id = organization_id
        self.user_id = user_id
        self.call_id = f"call_{uuid.uuid4().hex[:12]}" if not kwargs.get("call_id") else kwargs.get("call_id")
        
        self.billing_manager = get_billing_manager()
        self.usage_tracker = get_usage_tracker()
        
        # Extract task configurations
        self.tasks_config = agent_config.get("tasks", [])
        self.welcome_message = agent_config.get("agent_welcome_message", "")
        
        # Task managers
        self._task_managers: List[TaskManager] = []
        
        # Log context
        self.log_context = LogContext(
            organization_id=organization_id,
            user_id=user_id,
        )
        
    async def run(self) -> AsyncIterator[tuple]:
        """
        Run all tasks and yield results.
        
        Yields:
            Tuple of (task_index, PipelineResult)
        """
        self._is_running = True
        
        with self.log_context:
            try:
                # Initialize task managers
                for i, task_config in enumerate(self.tasks_config):
                    task_id = f"task_{i + 1}"
                    task_prompts = self.prompts.get(task_id, {})
                    
                    manager = TaskManager(
                        task_config=task_config,
                        prompts=task_prompts,
                        input_queue=self.input_queue,
                        output_queue=self.output_queue,
                        task_index=i,
                        organization_id=self.organization_id,
                        user_id=self.user_id,
                        call_id=self.call_id,
                    )
                    self._task_managers.append(manager)
                
                # Register call in usage tracker
                account = self.billing_manager.get_account_by_org(self.organization_id)
                account_id = account.account_id if account else self.organization_id
                
                # Determine providers from config (simplified for now)
                stt_p = self.agent_config.get("tasks", [{}])[0].get("tools_config", {}).get("transcriber", {}).get("provider", "deepgram")
                tts_p = self.agent_config.get("tasks", [{}])[0].get("tools_config", {}).get("synthesizer", {}).get("provider", "elevenlabs")
                
                self.usage_tracker.start_call(
                    call_id=self.call_id,
                    account_id=account_id,
                    stt_provider=stt_p,
                    tts_provider=tts_p,
                )
                
                logger.info(f"Starting assistant session {self.call_id} with {len(self._task_managers)} tasks")
                
                # Run tasks
                for i, manager in enumerate(self._task_managers):
                    async for result in manager.run():
                        yield (i, result)
                        
                        if self.output_queue:
                            await self.output_queue.put((i, result))
                            
            except Exception as e:
                logger.error(f"Assistant manager error: {e}")
                error_result = PipelineResult(
                    type="error",
                    data=str(e),
                    is_final=True,
                )
                yield (0, error_result)
            finally:
                self._is_running = False
                await self.finalize_billing()
                await self.stop()

    async def finalize_billing(self) -> None:
        """Calculate final costs and charge the account."""
        try:
            usage = self.usage_tracker.end_call(self.call_id)
            if usage:
                account = self.billing_manager.get_account_by_org(self.organization_id)
                if account:
                    self.billing_manager.charge_usage(
                        account_id=account.account_id,
                        amount=float(usage.total_cost),
                        description=f"Audio Session {self.call_id}"
                    )
                    logger.info(f"Finalized billing for {self.call_id}: ${usage.total_cost:.4f}")
        except Exception as e:
            logger.error(f"Error finalizing billing for {self.call_id}: {e}")
    
    async def stop(self) -> None:
        """Stop all task managers."""
        self._is_running = False
        
        for manager in self._task_managers:
            try:
                await manager.stop()
            except Exception:
                pass
        
        self._task_managers = []
        logger.info("Assistant manager stopped")
    
    async def send_input(self, data: Any) -> None:
        """Send input to the assistant."""
        await self.input_queue.put(data)
    
    async def end_conversation(self) -> None:
        """Signal end of conversation."""
        await self.input_queue.put(None)
    
    def get_welcome_message(self) -> str:
        """Get the welcome message for the agent."""
        return self.welcome_message

