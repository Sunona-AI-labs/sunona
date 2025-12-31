"""
Sunona Voice AI - Assistant

High-level interface for creating and running voice AI assistants.
"""

import asyncio
import logging
from typing import AsyncIterator, Dict, Any, Optional, List

from sunona.models import (
    Task,
    ToolsChainModel,
    ToolsConfig,
    LlmAgent,
    Transcriber,
    Synthesizer,
    IOModel,
)
from sunona.agent_manager import AssistantManager

logger = logging.getLogger(__name__)


class Assistant:
    """
    High-level interface for creating and running voice AI assistants.
    
    Example:
        ```python
        assistant = Assistant(name="my_agent")
        
        # Add a conversation task
        assistant.add_task(
            task_type="conversation",
            llm_agent=llm_agent,
            transcriber=transcriber,
            synthesizer=synthesizer,
        )
        
        # Run and process results
        async for chunk in assistant.execute():
            print(chunk)
        ```
    """
    
    def __init__(
        self,
        name: str = "sunona_agent",
        welcome_message: Optional[str] = None,
        organization_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ):
        """
        Initialize the assistant.
        
        Args:
            name: Agent name
            welcome_message: Welcome message for conversations
            organization_id: Organization ID for multi-tenancy
            user_id: User ID for multi-tenancy
        """
        self.name = name
        self.welcome_message = welcome_message
        self.organization_id = organization_id
        self.user_id = user_id
        self.tasks: List[Dict[str, Any]] = []
        self.prompts: Dict[str, Dict[str, str]] = {}
        
        self._manager: Optional[AssistantManager] = None
        self._input_queue: asyncio.Queue = asyncio.Queue()
        self._output_queue: asyncio.Queue = asyncio.Queue()
    
    def add_task(
        self,
        task_type: str = "conversation",
        llm_agent: Optional[LlmAgent] = None,
        transcriber: Optional[Transcriber] = None,
        synthesizer: Optional[Synthesizer] = None,
        enable_textual_input: bool = False,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Add a task to the assistant.
        
        Args:
            task_type: Type of task ('conversation', 'extraction', etc.)
            llm_agent: LLM agent configuration
            transcriber: Transcriber configuration
            synthesizer: Synthesizer configuration
            enable_textual_input: Enable text input mode
            system_prompt: System prompt for the task
            **kwargs: Additional task configuration
        """
        # Build pipelines based on components
        pipelines = []
        tools_config_args = {}
        
        # Set up LLM agent (required)
        if llm_agent:
            tools_config_args["llm_agent"] = llm_agent.model_dump() if hasattr(llm_agent, 'model_dump') else llm_agent
        else:
            # Default LLM config
            tools_config_args["llm_agent"] = LlmAgent().model_dump()
        
        # Set up input/output
        tools_config_args["input"] = {"format": "wav", "provider": "default"}
        tools_config_args["output"] = {"format": "wav", "provider": "default"}
        
        # Set up pipeline based on components
        if transcriber is not None:
            tools_config_args["transcriber"] = (
                transcriber.model_dump() if hasattr(transcriber, 'model_dump') else transcriber
            )
            
            pipeline = ["transcriber", "llm"]
            
            if synthesizer is not None:
                tools_config_args["synthesizer"] = (
                    synthesizer.model_dump() if hasattr(synthesizer, 'model_dump') else synthesizer
                )
                pipeline.append("synthesizer")
            
            pipelines.append(pipeline)
        else:
            # Text-only pipeline
            pipelines.append(["llm"])
            
            if synthesizer is not None:
                tools_config_args["synthesizer"] = (
                    synthesizer.model_dump() if hasattr(synthesizer, 'model_dump') else synthesizer
                )
                pipelines[-1].append("synthesizer")
        
        # Add text input pipeline if enabled
        if enable_textual_input:
            text_pipeline = ["llm"]
            if synthesizer is not None and "synthesizer" not in pipelines[0]:
                text_pipeline.append("synthesizer")
            if text_pipeline not in pipelines:
                pipelines.append(text_pipeline)
        
        # Build toolchain
        toolchain = ToolsChainModel(execution="parallel", pipelines=pipelines)
        
        # Build task config
        task_config = {
            "task_id": f"task_{len(self.tasks) + 1}",
            "task_type": task_type,
            "toolchain": toolchain.model_dump(),
            "tools_config": tools_config_args,
            "task_config": {
                "hangup_after_silence": kwargs.get("hangup_after_silence", 30.0),
                **{k: v for k, v in kwargs.items() if k != "hangup_after_silence"}
            },
        }
        
        self.tasks.append(task_config)
        
        # Store system prompt
        task_id = task_config["task_id"]
        if system_prompt:
            self.prompts[task_id] = {"system_prompt": system_prompt}
    
    def set_system_prompt(self, prompt: str, task_index: int = 0) -> None:
        """
        Set the system prompt for a specific task.
        
        Args:
            prompt: System prompt text
            task_index: Task index (0-based)
        """
        task_id = f"task_{task_index + 1}"
        if task_id not in self.prompts:
            self.prompts[task_id] = {}
        self.prompts[task_id]["system_prompt"] = prompt
    
    async def execute(self) -> AsyncIterator[Dict[str, Any]]:
        """
        Execute the assistant and yield results.
        
        Yields:
            Dictionary with result data from pipeline execution
        """
        agent_config = {
            "agent_name": self.name,
            "tasks": self.tasks,
            "agent_welcome_message": self.welcome_message or "",
        }
        
        self._manager = AssistantManager(
            agent_config=agent_config,
            prompts=self.prompts,
            ws=None,
            input_queue=self._input_queue,
            output_queue=self._output_queue,
            organization_id=self.organization_id,
            user_id=self.user_id,
        )
        
        try:
            async for task_index, result in self._manager.run():
                yield {
                    "task_index": task_index,
                    "type": result.type,
                    "data": result.data,
                    "is_final": result.is_final,
                    "metadata": result.metadata,
                }
        finally:
            await self.stop()
    
    async def send_input(self, data: Any) -> None:
        """
        Send input data to the assistant.
        
        Args:
            data: Input data (text or audio bytes)
        """
        await self._input_queue.put(data)
    
    async def end_conversation(self) -> None:
        """Signal end of conversation."""
        await self._input_queue.put(None)
    
    async def stop(self) -> None:
        """Stop the assistant."""
        if self._manager:
            await self._manager.stop()
            self._manager = None
    
    def get_config(self) -> Dict[str, Any]:
        """Get the assistant configuration."""
        return {
            "agent_name": self.name,
            "tasks": self.tasks,
            "agent_welcome_message": self.welcome_message,
            "prompts": self.prompts,
        }
