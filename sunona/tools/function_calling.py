"""
Sunona Voice AI - Real-time Function Calling

Production-grade function calling system for executing tools
during live conversations. Enables AI agents to interact with
external systems in real-time.

Features:
- Tool definition with JSON Schema
- Built-in tools (calendar, CRM, database)
- Custom tool registration
- Parallel tool execution
- Error handling and retries
- Streaming tool results
"""

import asyncio
import inspect
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from functools import wraps
from typing import (
    Any, Awaitable, Callable, Dict, List, Optional, 
    Type, TypeVar, Union, get_type_hints
)

from pydantic import BaseModel, Field, ValidationError

from sunona.core.exceptions import SunonaError, ValidationError as SunonaValidationError
from sunona.core.retry import retry_async, RetryConfig
from sunona.core.circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ToolExecutionError(SunonaError):
    """Raised when a tool execution fails."""
    default_message = "Tool execution failed"
    default_error_code = "TOOL_EXECUTION_ERROR"
    

class ToolNotFoundError(SunonaError):
    """Raised when a requested tool is not found."""
    default_message = "Tool not found"
    default_error_code = "TOOL_NOT_FOUND"


class ToolCategory(Enum):
    """Categories for organizing tools."""
    COMMUNICATION = "communication"
    CALENDAR = "calendar"
    CRM = "crm"
    DATABASE = "database"
    UTILITY = "utility"
    CUSTOM = "custom"


@dataclass
class ToolParameter:
    """Definition of a tool parameter."""
    name: str
    type: str  # "string", "number", "boolean", "array", "object"
    description: str
    required: bool = True
    default: Any = None
    enum: Optional[List[Any]] = None
    
    def to_json_schema(self) -> Dict[str, Any]:
        """Convert to JSON Schema format."""
        schema: Dict[str, Any] = {
            "type": self.type,
            "description": self.description,
        }
        
        if self.enum:
            schema["enum"] = self.enum
        
        if self.default is not None:
            schema["default"] = self.default
        
        return schema


@dataclass
class ToolDefinition:
    """
    Complete definition of a callable tool.
    
    Attributes:
        name: Unique tool identifier
        description: What the tool does
        parameters: List of parameters
        category: Tool category
        handler: Async function to execute
        requires_confirmation: Whether to confirm before execution
        timeout: Execution timeout in seconds
        retries: Number of retry attempts
        circuit_breaker: Optional circuit breaker name
    """
    name: str
    description: str
    parameters: List[ToolParameter] = field(default_factory=list)
    category: ToolCategory = ToolCategory.CUSTOM
    handler: Optional[Callable[..., Awaitable[Any]]] = None
    requires_confirmation: bool = False
    timeout: float = 30.0
    retries: int = 1
    circuit_breaker: Optional[str] = None
    
    def to_openai_schema(self) -> Dict[str, Any]:
        """
        Convert to OpenAI function calling schema.
        
        Returns format compatible with OpenAI's tools parameter.
        """
        properties = {}
        required = []
        
        for param in self.parameters:
            properties[param.name] = param.to_json_schema()
            if param.required:
                required.append(param.name)
        
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }


@dataclass
class ToolCall:
    """Represents a tool call request from the LLM."""
    id: str
    name: str
    arguments: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ToolResult:
    """Result of a tool execution."""
    tool_call_id: str
    tool_name: str
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for LLM consumption."""
        return {
            "tool_call_id": self.tool_call_id,
            "role": "tool",
            "content": json.dumps(self.result) if self.success else f"Error: {self.error}",
        }


class BaseTool(ABC):
    """
    Abstract base class for tools.
    
    Extend this class to create custom tools with full control.
    
    Example:
        class WeatherTool(BaseTool):
            name = "get_weather"
            description = "Get current weather for a location"
            
            @property
            def parameters(self):
                return [
                    ToolParameter("location", "string", "City name", required=True),
                ]
            
            async def execute(self, location: str) -> Dict:
                # Call weather API
                return {"temperature": 72, "condition": "sunny"}
    """
    
    name: str = "base_tool"
    description: str = "Base tool"
    category: ToolCategory = ToolCategory.CUSTOM
    requires_confirmation: bool = False
    timeout: float = 30.0
    retries: int = 1
    
    @property
    @abstractmethod
    def parameters(self) -> List[ToolParameter]:
        """Define tool parameters."""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given arguments."""
        pass
    
    def to_definition(self) -> ToolDefinition:
        """Convert to ToolDefinition."""
        return ToolDefinition(
            name=self.name,
            description=self.description,
            parameters=self.parameters,
            category=self.category,
            handler=self.execute,
            requires_confirmation=self.requires_confirmation,
            timeout=self.timeout,
            retries=self.retries,
        )


class ToolRegistry:
    """
    Central registry for all available tools.
    
    Features:
    - Tool registration and lookup
    - Category-based filtering
    - Schema generation
    - Tool validation
    
    Example:
        registry = ToolRegistry()
        
        # Register a tool
        registry.register(ToolDefinition(
            name="send_email",
            description="Send an email",
            parameters=[...],
            handler=send_email_func,
        ))
        
        # Get all tools for LLM
        schema = registry.get_openai_schema()
    """
    
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._categories: Dict[ToolCategory, List[str]] = {}
    
    def register(self, tool: Union[ToolDefinition, BaseTool]) -> None:
        """
        Register a tool.
        
        Args:
            tool: Tool definition or BaseTool instance
        """
        if isinstance(tool, BaseTool):
            definition = tool.to_definition()
        else:
            definition = tool
        
        self._tools[definition.name] = definition
        
        # Add to category index
        if definition.category not in self._categories:
            self._categories[definition.category] = []
        self._categories[definition.category].append(definition.name)
        
        logger.debug(f"Registered tool: {definition.name}")
    
    def unregister(self, name: str) -> None:
        """Remove a tool from the registry."""
        if name in self._tools:
            tool = self._tools.pop(name)
            if tool.category in self._categories:
                self._categories[tool.category].remove(name)
    
    def get(self, name: str) -> Optional[ToolDefinition]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def get_by_category(self, category: ToolCategory) -> List[ToolDefinition]:
        """Get all tools in a category."""
        names = self._categories.get(category, [])
        return [self._tools[name] for name in names if name in self._tools]
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self._tools.keys())
    
    def get_openai_schema(
        self,
        tool_names: Optional[List[str]] = None,
        categories: Optional[List[ToolCategory]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get OpenAI-compatible tool schema.
        
        Args:
            tool_names: Filter to specific tools
            categories: Filter to specific categories
        
        Returns:
            List of tool schemas for OpenAI API
        """
        tools = []
        
        for name, tool in self._tools.items():
            # Apply filters
            if tool_names and name not in tool_names:
                continue
            if categories and tool.category not in categories:
                continue
            
            tools.append(tool.to_openai_schema())
        
        return tools


class FunctionCallingAgent:
    """
    Agent capable of executing functions during conversations.
    
    Features:
    - Tool execution with retries
    - Parallel tool execution
    - Error handling
    - Confirmation flow
    - Execution history
    
    Example:
        agent = FunctionCallingAgent(llm=my_llm)
        
        # Register tools
        agent.register_tool(SendEmailTool())
        agent.register_tool(CalendarTool())
        
        # Process message with potential tool calls
        response = await agent.process("Schedule a meeting for tomorrow at 2pm")
        
        # If tools were called
        if response.tool_calls:
            print(f"Executed {len(response.tool_calls)} tools")
    """
    
    def __init__(
        self,
        llm: Any,
        registry: Optional[ToolRegistry] = None,
        max_parallel_calls: int = 5,
        confirmation_callback: Optional[Callable[[ToolCall], Awaitable[bool]]] = None,
    ):
        """
        Initialize function calling agent.
        
        Args:
            llm: LLM instance with tool support
            registry: Tool registry (creates new if not provided)
            max_parallel_calls: Maximum parallel tool executions
            confirmation_callback: Callback for confirmation flow
        """
        self.llm = llm
        self.registry = registry or ToolRegistry()
        self.max_parallel_calls = max_parallel_calls
        self.confirmation_callback = confirmation_callback
        
        # Execution history
        self._execution_history: List[ToolResult] = []
        
        # Semaphore for parallel execution limit
        self._semaphore = asyncio.Semaphore(max_parallel_calls)
    
    def register_tool(self, tool: Union[ToolDefinition, BaseTool]) -> None:
        """Register a tool with the agent."""
        self.registry.register(tool)
    
    def get_tool_schema(
        self,
        tool_names: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Get tool schemas for LLM."""
        return self.registry.get_openai_schema(tool_names=tool_names)
    
    async def execute_tool(
        self,
        tool_call: ToolCall,
    ) -> ToolResult:
        """
        Execute a single tool call.
        
        Args:
            tool_call: The tool call to execute
        
        Returns:
            ToolResult with execution result
        """
        start_time = asyncio.get_event_loop().time()
        
        # Get tool definition
        tool = self.registry.get(tool_call.name)
        if not tool:
            return ToolResult(
                tool_call_id=tool_call.id,
                tool_name=tool_call.name,
                success=False,
                result=None,
                error=f"Tool '{tool_call.name}' not found",
            )
        
        if not tool.handler:
            return ToolResult(
                tool_call_id=tool_call.id,
                tool_name=tool_call.name,
                success=False,
                result=None,
                error="Tool has no handler",
            )
        
        # Confirmation flow
        if tool.requires_confirmation and self.confirmation_callback:
            confirmed = await self.confirmation_callback(tool_call)
            if not confirmed:
                return ToolResult(
                    tool_call_id=tool_call.id,
                    tool_name=tool_call.name,
                    success=False,
                    result=None,
                    error="User declined to execute tool",
                )
        
        # Execute with rate limiting
        async with self._semaphore:
            try:
                # Apply circuit breaker if configured
                if tool.circuit_breaker:
                    cb = CircuitBreaker.get(tool.circuit_breaker)
                    if cb:
                        result = await cb.execute(
                            self._execute_with_retry,
                            tool,
                            tool_call.arguments,
                        )
                    else:
                        result = await self._execute_with_retry(tool, tool_call.arguments)
                else:
                    result = await self._execute_with_retry(tool, tool_call.arguments)
                
                execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
                
                tool_result = ToolResult(
                    tool_call_id=tool_call.id,
                    tool_name=tool_call.name,
                    success=True,
                    result=result,
                    execution_time_ms=execution_time,
                )
                
                logger.info(
                    f"Tool '{tool_call.name}' executed successfully in {execution_time:.1f}ms",
                    extra={
                        "tool_name": tool_call.name,
                        "execution_time_ms": execution_time,
                    },
                )
                
            except Exception as e:
                execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
                
                tool_result = ToolResult(
                    tool_call_id=tool_call.id,
                    tool_name=tool_call.name,
                    success=False,
                    result=None,
                    error=str(e),
                    execution_time_ms=execution_time,
                )
                
                logger.error(
                    f"Tool '{tool_call.name}' failed: {e}",
                    extra={
                        "tool_name": tool_call.name,
                        "error": str(e),
                    },
                )
        
        # Record in history
        self._execution_history.append(tool_result)
        
        return tool_result
    
    async def _execute_with_retry(
        self,
        tool: ToolDefinition,
        arguments: Dict[str, Any],
    ) -> Any:
        """Execute tool with retry logic."""
        if tool.retries > 1:
            config = RetryConfig(
                max_attempts=tool.retries,
                base_delay=1.0,
                max_delay=10.0,
            )
            return await retry_async(
                tool.handler,
                config=config,
                **arguments,
            )
        else:
            return await asyncio.wait_for(
                tool.handler(**arguments),
                timeout=tool.timeout,
            )
    
    async def execute_tools(
        self,
        tool_calls: List[ToolCall],
    ) -> List[ToolResult]:
        """
        Execute multiple tools (potentially in parallel).
        
        Args:
            tool_calls: List of tool calls
        
        Returns:
            List of results in same order
        """
        if not tool_calls:
            return []
        
        # Execute all tools
        tasks = [self.execute_tool(tc) for tc in tool_calls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(ToolResult(
                    tool_call_id=tool_calls[i].id,
                    tool_name=tool_calls[i].name,
                    success=False,
                    result=None,
                    error=str(result),
                ))
            else:
                final_results.append(result)
        
        return final_results
    
    async def process_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tool_names: Optional[List[str]] = None,
        max_tool_rounds: int = 5,
    ) -> Dict[str, Any]:
        """
        Process messages with potential tool calls.
        
        This method handles the full tool calling loop:
        1. Send messages to LLM with tool definitions
        2. If LLM returns tool calls, execute them
        3. Send tool results back to LLM
        4. Repeat until no more tool calls or max rounds reached
        
        Args:
            messages: Conversation messages
            tool_names: Optional filter for available tools
            max_tool_rounds: Maximum tool call rounds
        
        Returns:
            Final response with all tool calls and results
        """
        all_tool_calls = []
        all_tool_results = []
        current_messages = list(messages)
        
        for round_num in range(max_tool_rounds):
            # Get tool schema
            tools = self.get_tool_schema(tool_names=tool_names)
            
            if not tools:
                # No tools available, just generate response
                response = await self.llm.generate(current_messages)
                return {
                    "content": response.content if hasattr(response, 'content') else str(response),
                    "tool_calls": all_tool_calls,
                    "tool_results": all_tool_results,
                }
            
            # Call LLM with tools
            response = await self.llm.generate(
                current_messages,
                tools=tools,
                tool_choice="auto",
            )
            
            # Check for tool calls
            tool_calls_raw = getattr(response, 'tool_calls', None)
            
            if not tool_calls_raw:
                # No tool calls, return response
                return {
                    "content": response.content if hasattr(response, 'content') else str(response),
                    "tool_calls": all_tool_calls,
                    "tool_results": all_tool_results,
                }
            
            # Parse tool calls
            tool_calls = []
            for tc in tool_calls_raw:
                if hasattr(tc, 'function'):
                    # OpenAI format
                    tool_calls.append(ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=json.loads(tc.function.arguments) if isinstance(tc.function.arguments, str) else tc.function.arguments,
                    ))
                else:
                    # Generic format
                    tool_calls.append(ToolCall(
                        id=str(tc.get('id', len(all_tool_calls))),
                        name=tc.get('name', ''),
                        arguments=tc.get('arguments', {}),
                    ))
            
            all_tool_calls.extend(tool_calls)
            
            # Execute tool calls
            results = await self.execute_tools(tool_calls)
            all_tool_results.extend(results)
            
            # Add assistant message with tool calls
            current_messages.append({
                "role": "assistant",
                "content": getattr(response, 'content', None),
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": json.dumps(tc.arguments),
                        },
                    }
                    for tc in tool_calls
                ],
            })
            
            # Add tool results
            for result in results:
                current_messages.append(result.to_dict())
        
        # Max rounds reached, get final response
        response = await self.llm.generate(current_messages)
        
        return {
            "content": response.content if hasattr(response, 'content') else str(response),
            "tool_calls": all_tool_calls,
            "tool_results": all_tool_results,
        }
    
    def get_execution_history(self) -> List[ToolResult]:
        """Get tool execution history."""
        return self._execution_history.copy()
    
    def clear_history(self) -> None:
        """Clear execution history."""
        self._execution_history.clear()


# =============================================================================
# Tool Decorator
# =============================================================================

def tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    category: ToolCategory = ToolCategory.CUSTOM,
    requires_confirmation: bool = False,
    timeout: float = 30.0,
    retries: int = 1,
):
    """
    Decorator to convert a function into a tool.
    
    Uses type hints and docstring for parameter definitions.
    
    Example:
        @tool(name="send_email", description="Send an email")
        async def send_email(
            to: str,  # Recipient email address
            subject: str,  # Email subject
            body: str,  # Email body content
        ) -> Dict[str, Any]:
            # Send the email
            return {"success": True, "message_id": "abc123"}
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> ToolDefinition:
        # Extract function info
        func_name = name or func.__name__
        func_doc = description or func.__doc__ or f"Execute {func_name}"
        
        # Extract parameters from type hints
        hints = get_type_hints(func) if hasattr(func, '__annotations__') else {}
        sig = inspect.signature(func)
        
        parameters = []
        for param_name, param in sig.parameters.items():
            if param_name in ('self', 'cls'):
                continue
            
            # Get type
            param_type = hints.get(param_name, str)
            type_mapping = {
                str: "string",
                int: "number",
                float: "number",
                bool: "boolean",
                list: "array",
                dict: "object",
            }
            json_type = type_mapping.get(param_type, "string")
            
            # Get description from docstring or comment
            param_desc = f"Parameter {param_name}"
            
            # Check if required
            required = param.default == inspect.Parameter.empty
            default_val = None if required else param.default
            
            parameters.append(ToolParameter(
                name=param_name,
                type=json_type,
                description=param_desc,
                required=required,
                default=default_val,
            ))
        
        return ToolDefinition(
            name=func_name,
            description=func_doc,
            parameters=parameters,
            category=category,
            handler=func,
            requires_confirmation=requires_confirmation,
            timeout=timeout,
            retries=retries,
        )
    
    return decorator


# =============================================================================
# Global Tool Registry
# =============================================================================

_global_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get or create global tool registry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry


def register_tool(tool: Union[ToolDefinition, BaseTool]) -> None:
    """Register a tool in the global registry."""
    get_tool_registry().register(tool)
