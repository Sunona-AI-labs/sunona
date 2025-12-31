"""
Sunona Voice AI - Tools Package

Function calling and tool execution for voice AI agents.

Provides:
- BaseTool: Abstract base class for all tools
- ToolExecutor: Orchestrator for executing tool calls
- FunctionCallingAgent: Real-time function calling during conversations
- Built-in tools: Calendar, CRM, HTTP, SMS, Call Transfer
"""

from sunona.tools.base_tool import BaseTool, ToolResult, ToolParameter
from sunona.tools.tool_executor import ToolExecutor, ToolRegistry

# Import new function calling system
from sunona.tools.function_calling import (
    ToolDefinition,
    ToolCategory,
    ToolCall,
    FunctionCallingAgent,
    tool as function_tool,
    get_tool_registry,
    register_tool,
    ToolExecutionError,
    ToolNotFoundError,
)

# Import built-in tools
from sunona.tools.builtin_tools import (
    CheckAvailabilityTool,
    BookAppointmentTool,
    LookupCustomerTool,
    CreateLeadTool,
    GetCurrentTimeTool,
    HttpRequestTool,
    CalculateTool,
    SendSMSTool,
    TransferCallTool,
    get_builtin_tools,
    register_builtin_tools,
)

__all__ = [
    # Original exports
    "BaseTool",
    "ToolResult",
    "ToolParameter",
    "ToolExecutor",
    "ToolRegistry",
    "create_tool",
    # Function calling
    "ToolDefinition",
    "ToolCategory",
    "ToolCall",
    "FunctionCallingAgent",
    "function_tool",
    "get_tool_registry",
    "register_tool",
    "ToolExecutionError",
    "ToolNotFoundError",
    # Built-in tools
    "CheckAvailabilityTool",
    "BookAppointmentTool",
    "LookupCustomerTool",
    "CreateLeadTool",
    "GetCurrentTimeTool",
    "HttpRequestTool",
    "CalculateTool",
    "SendSMSTool",
    "TransferCallTool",
    "get_builtin_tools",
    "register_builtin_tools",
]


def create_tool(tool_type: str, **kwargs) -> BaseTool:
    """
    Factory function to create a tool instance.
    
    Args:
        tool_type: The tool type ('http', 'search', 'serpapi', 'calendar', 'crm', etc.)
        **kwargs: Tool-specific configuration
        
    Returns:
        BaseTool: A tool instance
    """
    from sunona.tools.http_tool import HTTPTool
    from sunona.tools.web_search_tool import WebSearchTool, SerpAPITool
    
    tools = {
        "http": HTTPTool,
        "api": HTTPTool,
        "search": WebSearchTool,
        "web_search": WebSearchTool,
        "serpapi": SerpAPITool,
        # New built-in tools
        "check_availability": CheckAvailabilityTool,
        "book_appointment": BookAppointmentTool,
        "lookup_customer": LookupCustomerTool,
        "create_lead": CreateLeadTool,
        "get_time": GetCurrentTimeTool,
        "http_request": HttpRequestTool,
        "calculate": CalculateTool,
        "send_sms": SendSMSTool,
        "transfer_call": TransferCallTool,
    }
    
    if tool_type not in tools:
        raise ValueError(
            f"Unknown tool type: '{tool_type}'. "
            f"Available: {list(tools.keys())}"
        )
    
    return tools[tool_type](**kwargs)

