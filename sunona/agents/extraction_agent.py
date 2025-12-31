"""
Sunona Voice AI - Extraction Agent

Agent specialized in extracting structured data from conversations.
Extracts names, emails, phone numbers, dates, preferences, and custom fields.
"""

import re
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from sunona.agents.base_agent import (
    BaseAgent, AgentConfig, AgentResponse, AgentCapability, AgentState
)

logger = logging.getLogger(__name__)


@dataclass
class ExtractionField:
    """Definition of a field to extract."""
    name: str
    description: str
    field_type: str = "text"  # text, email, phone, date, number, boolean
    required: bool = False
    validation_regex: Optional[str] = None
    prompt_question: Optional[str] = None


@dataclass
class ExtractionResult:
    """Result of extraction."""
    field_name: str
    value: Any
    confidence: float = 1.0
    raw_text: str = ""


class ExtractionAgent(BaseAgent):
    """
    Agent that extracts structured information from conversations.
    
    Features:
    - Extracts predefined fields (name, email, phone, etc.)
    - Custom field extraction
    - Validation of extracted data
    - Progressive extraction (asks for missing fields)
    - Confirmation of extracted values
    
    Best for:
    - Lead capture
    - Appointment booking
    - Survey/form completion
    - Data collection calls
    
    Example:
        ```python
        agent = ExtractionAgent(config)
        
        # Define fields to extract
        agent.add_field(ExtractionField(
            name="name",
            description="Customer's full name",
            required=True,
            prompt_question="May I have your name please?",
        ))
        agent.add_field(ExtractionField(
            name="email",
            description="Email address",
            field_type="email",
            required=True,
        ))
        
        # Process conversation
        response = await agent.process_message("Hi, I'm John Smith")
        # Extracts: {"name": "John Smith"}
        
        response = await agent.process_message("john@example.com")
        # Extracts: {"email": "john@example.com"}
        
        # Check if all required extracted
        if agent.is_complete():
            data = agent.get_extracted_data()
        ```
    """
    
    # Built-in regex patterns
    PATTERNS = {
        "email": r'[\w\.-]+@[\w\.-]+\.\w+',
        "phone": r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{7,}',
        "date": r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
        "time": r'\d{1,2}:\d{2}\s*(?:am|pm|AM|PM)?',
        "number": r'\b\d+(?:\.\d+)?\b',
        "yes_no": r'\b(?:yes|no|yeah|nope|yep|nah)\b',
    }
    
    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        llm: Optional[Any] = None,
    ):
        super().__init__(config, llm)
        
        self._fields: Dict[str, ExtractionField] = {}
        self._extracted: Dict[str, ExtractionResult] = {}
        self._pending_confirmation: Optional[str] = None
    
    @property
    def capabilities(self) -> List[AgentCapability]:
        return [AgentCapability.EXTRACTION]
    
    def add_field(self, field: ExtractionField):
        """Add a field to extract."""
        self._fields[field.name] = field
    
    def add_fields(self, fields: List[ExtractionField]):
        """Add multiple fields."""
        for field in fields:
            self.add_field(field)
    
    async def process_message(self, message: str) -> AgentResponse:
        """Process message and extract data."""
        self._set_state(AgentState.LISTENING)
        self.add_message("user", message)
        
        # Handle pending confirmation
        if self._pending_confirmation:
            confirmed = self._check_confirmation(message)
            field_name = self._pending_confirmation
            self._pending_confirmation = None
            
            if not confirmed:
                # User rejected, ask again
                field = self._fields[field_name]
                del self._extracted[field_name]
                return AgentResponse(
                    text=f"I understand. {field.prompt_question or f'Could you please provide your {field.name}?'}",
                    data={"action": "re_ask", "field": field_name},
                )
        
        # Extract from message
        extracted_fields = self._extract_from_message(message)
        
        # Generate response
        self._set_state(AgentState.THINKING)
        
        # Check if we need to ask for more fields
        missing = self._get_missing_required()
        
        if missing:
            # Ask for next missing field
            field = self._fields[missing[0]]
            question = field.prompt_question or f"Could you please provide your {field.name}?"
            response_text = question
            
            self.add_message("assistant", response_text)
            
            return AgentResponse(
                text=response_text,
                data={
                    "action": "ask_field",
                    "field": missing[0],
                    "extracted_so_far": self.get_extracted_data(),
                },
            )
        
        # All required fields collected
        if extracted_fields:
            # Confirm the last extracted value
            last_field = list(extracted_fields.keys())[-1]
            last_value = extracted_fields[last_field]
            
            response_text = f"I've got your {last_field} as {last_value}. Is that correct?"
            self._pending_confirmation = last_field
            
            self.add_message("assistant", response_text)
            
            return AgentResponse(
                text=response_text,
                data={
                    "action": "confirm",
                    "field": last_field,
                    "value": last_value,
                },
            )
        
        # No extraction happened, use LLM
        response_text = await self.generate_response()
        self.add_message("assistant", response_text)
        
        return AgentResponse(
            text=response_text,
            data={"extracted": self.get_extracted_data()},
        )
    
    def _extract_from_message(self, message: str) -> Dict[str, Any]:
        """Extract data from message."""
        extracted = {}
        
        for field_name, field in self._fields.items():
            if field_name in self._extracted:
                continue  # Already extracted
            
            value = self._extract_field(message, field)
            if value:
                self._extracted[field_name] = ExtractionResult(
                    field_name=field_name,
                    value=value,
                    raw_text=message,
                )
                extracted[field_name] = value
                logger.info(f"Extracted {field_name}: {value}")
        
        return extracted
    
    def _extract_field(self, message: str, field: ExtractionField) -> Optional[Any]:
        """Extract a single field from message."""
        message_lower = message.lower()
        
        # Use validation regex if provided
        if field.validation_regex:
            match = re.search(field.validation_regex, message, re.IGNORECASE)
            if match:
                return match.group()
        
        # Use built-in patterns
        if field.field_type in self.PATTERNS:
            pattern = self.PATTERNS[field.field_type]
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group()
        
        # For text/name fields, try to extract intelligently
        if field.field_type == "text":
            if field.name in ["name", "full_name"]:
                # Look for "I'm X" or "My name is X" patterns
                patterns = [
                    r"(?:i'm|i am|my name is|this is)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)?)",
                    r"^([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)$",
                ]
                for pattern in patterns:
                    match = re.search(pattern, message, re.IGNORECASE)
                    if match:
                        return match.group(1).title()
        
        # Boolean extraction
        if field.field_type == "boolean":
            if any(w in message_lower for w in ["yes", "yeah", "yep", "sure", "correct"]):
                return True
            if any(w in message_lower for w in ["no", "nope", "nah", "wrong", "incorrect"]):
                return False
        
        return None
    
    def _check_confirmation(self, message: str) -> bool:
        """Check if message confirms or denies."""
        message_lower = message.lower()
        
        positive = ["yes", "yeah", "yep", "correct", "right", "that's right", "sure"]
        negative = ["no", "nope", "wrong", "incorrect", "not right"]
        
        if any(w in message_lower for w in positive):
            return True
        if any(w in message_lower for w in negative):
            return False
        
        return True  # Default to confirmed if unclear
    
    def _get_missing_required(self) -> List[str]:
        """Get list of missing required fields."""
        missing = []
        for name, field in self._fields.items():
            if field.required and name not in self._extracted:
                missing.append(name)
        return missing
    
    def is_complete(self) -> bool:
        """Check if all required fields are extracted."""
        return len(self._get_missing_required()) == 0
    
    def get_extracted_data(self) -> Dict[str, Any]:
        """Get all extracted data."""
        return {name: result.value for name, result in self._extracted.items()}
    
    def get_extraction_summary(self) -> Dict[str, Any]:
        """Get extraction summary."""
        return {
            "extracted": self.get_extracted_data(),
            "missing_required": self._get_missing_required(),
            "is_complete": self.is_complete(),
            "total_fields": len(self._fields),
            "extracted_count": len(self._extracted),
        }
    
    def clear_extracted(self):
        """Clear extracted data."""
        self._extracted = {}
        self._pending_confirmation = None


# ==================== Pre-built Extraction Configs ====================

def create_lead_capture_agent(config: Optional[AgentConfig] = None) -> ExtractionAgent:
    """Create an agent for lead capture."""
    agent = ExtractionAgent(config)
    
    agent.add_fields([
        ExtractionField(
            name="name",
            description="Lead's full name",
            required=True,
            prompt_question="May I have your name please?",
        ),
        ExtractionField(
            name="email",
            description="Email address",
            field_type="email",
            required=True,
            prompt_question="What's the best email to reach you?",
        ),
        ExtractionField(
            name="phone",
            description="Phone number",
            field_type="phone",
            required=False,
            prompt_question="And your phone number?",
        ),
        ExtractionField(
            name="company",
            description="Company name",
            required=False,
            prompt_question="What company are you with?",
        ),
    ])
    
    return agent


def create_appointment_agent(config: Optional[AgentConfig] = None) -> ExtractionAgent:
    """Create an agent for appointment booking."""
    agent = ExtractionAgent(config)
    
    agent.add_fields([
        ExtractionField(
            name="name",
            description="Customer name",
            required=True,
            prompt_question="May I have your name for the appointment?",
        ),
        ExtractionField(
            name="date",
            description="Appointment date",
            field_type="date",
            required=True,
            prompt_question="What date works best for you?",
        ),
        ExtractionField(
            name="time",
            description="Preferred time",
            field_type="time",
            required=True,
            prompt_question="And what time would you prefer?",
        ),
        ExtractionField(
            name="phone",
            description="Contact phone",
            field_type="phone",
            required=True,
            prompt_question="What phone number should we use to confirm?",
        ),
    ])
    
    return agent
