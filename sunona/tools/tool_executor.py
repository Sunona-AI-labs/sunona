"""
Sunona Voice AI - Tool Executor

Orchestrator for managing and executing tools from LLM function calls.
Handles tool registration, execution, and result formatting.

Features:
- Tool registry for managing available tools
- Async tool execution
- OpenAI function calling format support
- Parallel tool execution
- Result aggregation
"""

import json
import asyncio
import logging
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field

from sunona.tools.base_tool import BaseTool, ToolResult

logger = logging.getLogger(__name__)


@dataclass
class ToolCall:
    """
    Represents a tool call from an LLM.
    
    Attributes:
        id: Unique identifier for the tool call
        name: Tool name to execute
        arguments: Tool arguments as a dictionary
    """
    id: str
    name: str
    arguments: Dict[str, Any]
    
    @classmethod
    def from_openai_format(cls, tool_call: Dict[str, Any]) -> "ToolCall":
        """Create from OpenAI function calling format."""
        function = tool_call.get("function", {})
        
        # Parse arguments (may be JSON string)
        args = function.get("arguments", "{}")
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except json.JSONDecodeError:
                args = {}
        
        return cls(
            id=tool_call.get("id", ""),
            name=function.get("name", ""),
            arguments=args
        )


class ToolRegistry:
    """
    Registry for managing available tools.
    
    Provides tool lookup, validation, and OpenAI format generation.
    
    Example:
        ```python
        registry = ToolRegistry()
        registry.register(HTTPTool(name="fetch_data", ...))
        registry.register(SearchTool(name="web_search", ...))
        
        # Get tools in OpenAI format
        tools = registry.to_openai_format()
        ```
    """
    
    def __init__(self):
        """Initialize empty registry."""
        self._tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool) -> None:
        """
        Register a tool.
        
        Args:
            tool: Tool instance to register
        """
        if tool.name in self._tools:
            logger.warning(f"Overwriting existing tool: {tool.name}")
        
        self._tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name}")
    
    def unregister(self, name: str) -> bool:
        """
        Unregister a tool by name.
        
        Args:
            name: Tool name to remove
            
        Returns:
            True if tool was removed, False if not found
        """
        if name in self._tools:
            del self._tools[name]
            return True
        return False
    
    def get(self, name: str) -> Optional[BaseTool]:
        """
        Get a tool by name.
        
        Args:
            name: Tool name
            
        Returns:
            Tool instance or None if not found
        """
        return self._tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self._tools.keys())
    
    def to_openai_format(self) -> List[Dict[str, Any]]:
        """
        Convert all registered tools to OpenAI function format.
        
        Returns:
            List of tool definitions in OpenAI format
        """
        return [tool.to_openai_function() for tool in self._tools.values()]
    
    def __len__(self) -> int:
        return len(self._tools)
    
    def __contains__(self, name: str) -> bool:
        return name in self._tools
    
    def __iter__(self):
        return iter(self._tools.values())


class ToolExecutor:
    """
    Executes tool calls from LLM responses.
    
    Handles:
    - Single and parallel tool execution
    - Result formatting for LLM consumption
    - Error handling and recovery
    
    Example:
        ```python
        executor = ToolExecutor(registry)
        
        # Execute a single tool call
        result = await executor.execute(tool_call)
        
        # Execute multiple tools in parallel
        results = await executor.execute_all(tool_calls)
        ```
    """
    
    def __init__(
        self,
        registry: Optional[ToolRegistry] = None,
        parallel_execution: bool = True,
        max_concurrent: int = 5
    ):
        """
        Initialize the tool executor.
        
        Args:
            registry: Tool registry (created if not provided)
            parallel_execution: Whether to execute tools in parallel
            max_concurrent: Maximum concurrent executions
        """
        self.registry = registry or ToolRegistry()
        self.parallel_execution = parallel_execution
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)
    
    def register_tool(self, tool: BaseTool) -> None:
        """Register a tool with the executor."""
        self.registry.register(tool)
    
    def get_tools_for_llm(self) -> List[Dict[str, Any]]:
        """Get tools in OpenAI format for LLM calls."""
        return self.registry.to_openai_format()
    
    async def execute(self, tool_call: ToolCall) -> Dict[str, Any]:
        """
        Execute a single tool call.
        
        Args:
            tool_call: Tool call to execute
            
        Returns:
            Result formatted for LLM consumption
        """
        tool = self.registry.get(tool_call.name)
        
        if not tool:
            return {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "content": json.dumps({
                    "error": f"Unknown tool: {tool_call.name}"
                })
            }
        
        async with self._semaphore:
            result = await tool.safe_execute(**tool_call.arguments)
        
        return {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "content": result.to_json()
        }
    
    async def execute_all(
        self,
        tool_calls: List[ToolCall]
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple tool calls.
        
        Args:
            tool_calls: List of tool calls to execute
            
        Returns:
            List of results formatted for LLM consumption
        """
        if not tool_calls:
            return []
        
        if self.parallel_execution and len(tool_calls) > 1:
            # Execute in parallel
            tasks = [self.execute(tc) for tc in tool_calls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions
            processed_results = []
            for tc, result in zip(tool_calls, results):
                if isinstance(result, Exception):
                    processed_results.append({
                        "tool_call_id": tc.id,
                        "role": "tool",
                        "content": json.dumps({"error": str(result)})
                    })
                else:
                    processed_results.append(result)
            
            return processed_results
        else:
            # Execute sequentially
            return [await self.execute(tc) for tc in tool_calls]
    
    async def execute_from_openai_response(
        self,
        tool_calls: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Execute tool calls from OpenAI response format.
        
        Args:
            tool_calls: Tool calls in OpenAI format
            
        Returns:
            Results formatted for adding to message history
        """
        parsed_calls = [ToolCall.from_openai_format(tc) for tc in tool_calls]
        return await self.execute_all(parsed_calls)
    
    def has_tools(self) -> bool:
        """Check if any tools are registered."""
        return len(self.registry) > 0


async def execute_tool_loop(
    llm,
    messages: List[Dict[str, str]],
    executor: ToolExecutor,
    max_iterations: int = 10
) -> str:
    """
    Execute the full tool calling loop until completion.
    
    This function handles the back-and-forth between LLM and tools:
    1. LLM generates response (may include tool calls)
    2. If tool calls, execute them
    3. Add results to messages and call LLM again
    4. Repeat until LLM returns final response
    
    Args:
        llm: LLM instance with generate_with_tools method
        messages: Initial message history
        executor: Tool executor with registered tools
        max_iterations: Maximum tool calling iterations
        
    Returns:
        Final response text from LLM
    """
    tools = executor.get_tools_for_llm()
    current_messages = messages.copy()
    
    for iteration in range(max_iterations):
        # Call LLM with tools
        response = await llm.generate_with_tools(current_messages, tools)
        
        # Check for tool calls
        if response.get("tool_calls"):
            tool_calls = response["tool_calls"]
            
            # Add assistant message with tool calls
            current_messages.append({
                "role": "assistant",
                "content": response.get("content", ""),
                "tool_calls": tool_calls
            })
            
            # Execute tools
            results = await executor.execute_from_openai_response(tool_calls)
            
            # Add tool results
            current_messages.extend(results)
            
            logger.debug(f"Tool iteration {iteration + 1}: executed {len(tool_calls)} tools")
        else:
            # No tool calls, return final response
            return response.get("content", "")
    
    logger.warning(f"Tool loop reached max iterations ({max_iterations})")
    return response.get("content", "")
