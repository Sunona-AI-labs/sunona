"""
Sunona Voice AI - Base Domain Template

Abstract base class for all domain templates.
Provides structure for system prompts, tools, and data extraction.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ToolType(str, Enum):
    """Types of tools available."""
    API = "api"
    DATABASE = "database"
    CALENDAR = "calendar"
    NOTIFICATION = "notification"
    PAYMENT = "payment"
    SEARCH = "search"
    VALIDATION = "validation"


@dataclass
class ToolDefinition:
    """
    Definition of a tool for the agent.
    
    Attributes:
        name: Tool name (function name)
        description: What the tool does
        parameters: List of parameter definitions
        tool_type: Type of tool
        required_fields: Fields that must be extracted first
        api_endpoint: Optional API endpoint for HTTP tools
    """
    name: str
    description: str
    parameters: List[Dict[str, Any]]
    tool_type: ToolType = ToolType.API
    required_fields: List[str] = field(default_factory=list)
    api_endpoint: Optional[str] = None
    
    def to_openai_function(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling format."""
        properties = {}
        required = []
        
        for param in self.parameters:
            prop = {
                "type": param.get("type", "string"),
                "description": param.get("description", ""),
            }
            
            if "enum" in param:
                prop["enum"] = param["enum"]
            
            properties[param["name"]] = prop
            
            if param.get("required", False):
                required.append(param["name"])
        
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
class ExtractionField:
    """
    Field to extract from conversation.
    
    Attributes:
        name: Field name
        description: What to extract
        field_type: Data type (string, number, date, phone, email)
        required: Whether field is required
        validation_pattern: Regex pattern for validation
        examples: Example values
    """
    name: str
    description: str
    field_type: str = "string"
    required: bool = False
    validation_pattern: Optional[str] = None
    examples: List[str] = field(default_factory=list)


class DomainTemplate(ABC):
    """
    Base class for domain-specific templates.
    
    Provides system prompts, tools, and extraction schemas
    for specific industry use cases.
    
    Example:
        ```python
        template = HospitalityTemplate(
            business_name="Grand Hotel",
            agent_name="Sarah"
        )
        
        system_prompt = template.get_system_prompt()
        tools = template.get_tools()
        ```
    """
    
    def __init__(
        self,
        business_name: str = "Our Company",
        agent_name: str = "Alex",
        language: str = "en",
        tone: str = "professional",
        custom_instructions: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize domain template.
        
        Args:
            business_name: Name of the business
            agent_name: Name of the AI agent
            language: Primary language
            tone: Communication tone (professional, friendly, formal)
            custom_instructions: Additional custom instructions
        """
        self.business_name = business_name
        self.agent_name = agent_name
        self.language = language
        self.tone = tone
        self.custom_instructions = custom_instructions
        self.config = kwargs
    
    @property
    @abstractmethod
    def domain_name(self) -> str:
        """Get the domain name."""
        pass
    
    @property
    @abstractmethod
    def domain_description(self) -> str:
        """Get domain description."""
        pass
    
    @abstractmethod
    def get_base_prompt(self) -> str:
        """Get the base system prompt for this domain."""
        pass
    
    @abstractmethod
    def get_tools(self) -> List[ToolDefinition]:
        """Get available tools for this domain."""
        pass
    
    @abstractmethod
    def get_extraction_fields(self) -> List[ExtractionField]:
        """Get fields to extract from conversations."""
        pass
    
    def get_system_prompt(self) -> str:
        """
        Get the complete system prompt.
        
        Combines base prompt with agent personality and custom instructions.
        """
        base = self.get_base_prompt()
        
        personality = self._get_personality_section()
        guidelines = self._get_guidelines_section()
        
        prompt = f"""{base}

{personality}

{guidelines}"""
        
        if self.custom_instructions:
            prompt += f"\n\n## Additional Instructions\n{self.custom_instructions}"
        
        return prompt
    
    def _get_personality_section(self) -> str:
        """Get personality configuration."""
        tone_descriptions = {
            "professional": "professional, helpful, and efficient",
            "friendly": "warm, friendly, and approachable",
            "formal": "formal, respectful, and precise",
            "casual": "casual, relaxed, and conversational",
        }
        
        tone_desc = tone_descriptions.get(self.tone, "professional and helpful")
        
        return f"""## Your Identity
- You are {self.agent_name}, an AI assistant for {self.business_name}
- Your communication style is {tone_desc}
- You speak clearly and concisely
- You are patient and understanding"""
    
    def _get_guidelines_section(self) -> str:
        """Get general guidelines."""
        return """## Guidelines
- Always confirm important information before taking action
- If you don't understand something, ask for clarification
- Never make up information - use available tools to look up data
- Be respectful of the caller's time
- If you cannot help, offer to transfer to a human agent"""
    
    def get_tools_for_llm(self) -> List[Dict[str, Any]]:
        """Get tools in OpenAI function format."""
        return [tool.to_openai_function() for tool in self.get_tools()]
    
    def get_extraction_schema(self) -> Dict[str, Any]:
        """Get extraction schema for structured data."""
        properties = {}
        required = []
        
        for field in self.get_extraction_fields():
            properties[field.name] = {
                "type": field.field_type,
                "description": field.description,
            }
            
            if field.examples:
                properties[field.name]["examples"] = field.examples
            
            if field.required:
                required.append(field.name)
        
        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }
