"""
Sunona Voice AI - Base Tool

Abstract base class for all tools/functions that can be called by LLM agents.

Features:
- Type-safe parameter definitions
- JSON Schema generation for OpenAI function calling
- Async execution support
- Result validation
"""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from enum import Enum

logger = logging.getLogger(__name__)


class ParameterType(str, Enum):
    """Supported parameter types."""
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


@dataclass
class ToolParameter:
    """
    Definition of a tool parameter.
    
    Attributes:
        name: Parameter name
        type: Parameter type (string, number, integer, boolean, array, object)
        description: Human-readable description
        required: Whether the parameter is required
        enum: List of allowed values (optional)
        default: Default value (optional)
        items: For array types, the type of items
    """
    name: str
    type: ParameterType
    description: str
    required: bool = True
    enum: Optional[List[Any]] = None
    default: Optional[Any] = None
    items: Optional[Dict[str, Any]] = None
    
    def to_json_schema(self) -> Dict[str, Any]:
        """Convert to JSON Schema format."""
        schema = {
            "type": self.type.value,
            "description": self.description,
        }
        
        if self.enum:
            schema["enum"] = self.enum
        
        if self.default is not None:
            schema["default"] = self.default
        
        if self.items and self.type == ParameterType.ARRAY:
            schema["items"] = self.items
        
        return schema


@dataclass
class ToolResult:
    """
    Result from tool execution.
    
    Attributes:
        success: Whether the execution was successful
        data: Result data (any type)
        error: Error message if failed
        metadata: Additional metadata about the execution
    """
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for LLM consumption."""
        if self.success:
            return {"result": self.data}
        else:
            return {"error": self.error}
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


class BaseTool(ABC):
    """
    Abstract base class for all tools.
    
    Subclasses must implement:
    - name: Tool name (used in function calling)
    - description: Tool description
    - parameters: List of ToolParameter definitions
    - execute(): Async method to execute the tool
    
    Example:
        ```python
        class WeatherTool(BaseTool):
            name = "get_weather"
            description = "Get current weather for a location"
            parameters = [
                ToolParameter(
                    name="location",
                    type=ParameterType.STRING,
                    description="City name or zip code",
                    required=True
                )
            ]
            
            async def execute(self, location: str) -> ToolResult:
                # Fetch weather data
                return ToolResult(success=True, data={"temperature": 72})
        ```
    """
    
    # Subclasses must define these
    name: str
    description: str
    parameters: List[ToolParameter] = []
    
    def __init__(self, **kwargs):
        """Initialize the tool with optional configuration."""
        self.config = kwargs
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool with the given parameters.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            ToolResult: The execution result
        """
        pass
    
    def validate_parameters(self, **kwargs) -> Optional[str]:
        """
        Validate input parameters against the parameter definitions.
        
        Args:
            **kwargs: Parameters to validate
            
        Returns:
            Error message if validation fails, None if valid
        """
        for param in self.parameters:
            if param.required and param.name not in kwargs:
                return f"Missing required parameter: {param.name}"
            
            if param.name in kwargs:
                value = kwargs[param.name]
                
                # Type checking
                if param.type == ParameterType.STRING and not isinstance(value, str):
                    return f"Parameter '{param.name}' must be a string"
                elif param.type == ParameterType.NUMBER and not isinstance(value, (int, float)):
                    return f"Parameter '{param.name}' must be a number"
                elif param.type == ParameterType.INTEGER and not isinstance(value, int):
                    return f"Parameter '{param.name}' must be an integer"
                elif param.type == ParameterType.BOOLEAN and not isinstance(value, bool):
                    return f"Parameter '{param.name}' must be a boolean"
                elif param.type == ParameterType.ARRAY and not isinstance(value, list):
                    return f"Parameter '{param.name}' must be an array"
                elif param.type == ParameterType.OBJECT and not isinstance(value, dict):
                    return f"Parameter '{param.name}' must be an object"
                
                # Enum validation
                if param.enum and value not in param.enum:
                    return f"Parameter '{param.name}' must be one of: {param.enum}"
        
        return None
    
    async def safe_execute(self, **kwargs) -> ToolResult:
        """
        Execute with validation and error handling.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            ToolResult: The execution result
        """
        # Validate parameters
        validation_error = self.validate_parameters(**kwargs)
        if validation_error:
            return ToolResult(success=False, error=validation_error)
        
        # Execute with error handling
        try:
            return await self.execute(**kwargs)
        except Exception as e:
            logger.error(f"Tool execution error ({self.name}): {e}")
            return ToolResult(success=False, error=str(e))
    
    def to_openai_function(self) -> Dict[str, Any]:
        """
        Convert to OpenAI function calling format.
        
        Returns:
            Dictionary in OpenAI function format
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
                }
            }
        }
    
    def to_json_schema(self) -> Dict[str, Any]:
        """
        Convert to JSON Schema format.
        
        Returns:
            JSON Schema dictionary
        """
        properties = {}
        required = []
        
        for param in self.parameters:
            properties[param.name] = param.to_json_schema()
            if param.required:
                required.append(param.name)
        
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            }
        }
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name='{self.name}'>"
