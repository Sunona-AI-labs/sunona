"""
Sunona Voice AI - Data Extraction Task

Specialized task for extracting structured data from conversations.
Uses LLM to identify and extract entities based on domain schemas.

Features:
- Schema-based extraction
- Validation with patterns
- Incremental extraction
- Confidence scoring
"""

import re
import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ExtractedField:
    """A single extracted field."""
    name: str
    value: Any
    confidence: float
    source_text: str = ""
    validated: bool = False


@dataclass
class ExtractionResult:
    """Result of data extraction from conversation."""
    fields: Dict[str, ExtractedField] = field(default_factory=dict)
    raw_data: Dict[str, Any] = field(default_factory=dict)
    missing_required: List[str] = field(default_factory=list)
    extraction_time: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with just values."""
        return {
            name: field.value 
            for name, field in self.fields.items()
        }
    
    def is_complete(self, required_fields: List[str]) -> bool:
        """Check if all required fields are extracted."""
        return all(f in self.fields for f in required_fields)


class DataExtractor:
    """
    Extract structured data from conversation history.
    
    Uses the domain template's extraction schema to identify
    and validate data from the conversation.
    
    Example:
        ```python
        from sunona.templates import get_template
        
        template = get_template("hospitality")
        extractor = DataExtractor(template)
        
        result = await extractor.extract(conversation_history)
        print(result.to_dict())
        ```
    """
    
    # Common validation patterns
    PATTERNS = {
        "email": r"[\w\.-]+@[\w\.-]+\.\w+",
        "phone": r"\+?[\d\s\-\(\)]{10,}",
        "date": r"\d{4}-\d{2}-\d{2}|\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}",
        "time": r"\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?",
        "number": r"\d+(?:\.\d+)?",
        "order_id": r"(?:ORD|#|ORDER)[-\s]?\w+",
        "confirmation": r"(?:CONF|RES|BK|CNF)[-\s]?\w+",
    }
    
    def __init__(
        self,
        template=None,
        llm=None,
        custom_patterns: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize data extractor.
        
        Args:
            template: Domain template with extraction schema
            llm: LLM instance for intelligent extraction
            custom_patterns: Additional regex patterns
        """
        self.template = template
        self.llm = llm
        self.patterns = {**self.PATTERNS}
        
        if custom_patterns:
            self.patterns.update(custom_patterns)
        
        self._extracted_data: Dict[str, ExtractedField] = {}
    
    def extract_with_regex(
        self, 
        text: str, 
        field_type: str
    ) -> Optional[str]:
        """Extract field using regex pattern."""
        pattern = self.patterns.get(field_type)
        if not pattern:
            return None
        
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0).strip()
        return None
    
    def extract_from_text(
        self, 
        text: str, 
        schema: Dict[str, Any] = None
    ) -> ExtractionResult:
        """
        Extract data from text using patterns and heuristics.
        
        Args:
            text: Text to extract from
            schema: Extraction schema (uses template schema if not provided)
            
        Returns:
            ExtractionResult with extracted fields
        """
        if schema is None and self.template:
            fields = self.template.get_extraction_fields()
            schema = {f.name: f for f in fields}
        elif schema is None:
            schema = {}
        
        result = ExtractionResult()
        
        for name, field in schema.items():
            # Try regex extraction first
            field_type = getattr(field, 'field_type', 'string')
            value = self.extract_with_regex(text, field_type)
            
            # Try custom validation pattern
            if not value and hasattr(field, 'validation_pattern') and field.validation_pattern:
                match = re.search(field.validation_pattern, text, re.IGNORECASE)
                if match:
                    value = match.group(0)
            
            if value:
                # Validate if pattern exists
                validated = True
                if hasattr(field, 'validation_pattern') and field.validation_pattern:
                    validated = bool(re.match(field.validation_pattern, value))
                
                result.fields[name] = ExtractedField(
                    name=name,
                    value=value,
                    confidence=0.8 if validated else 0.5,
                    source_text=text[:100],
                    validated=validated,
                )
        
        # Track missing required fields
        if self.template:
            required = [f.name for f in self.template.get_extraction_fields() if f.required]
            result.missing_required = [f for f in required if f not in result.fields]
        
        return result
    
    async def extract_with_llm(
        self, 
        conversation: List[Dict[str, str]],
        schema: Dict[str, Any] = None,
    ) -> ExtractionResult:
        """
        Extract data using LLM for intelligent parsing.
        
        Args:
            conversation: Conversation history
            schema: Extraction schema
            
        Returns:
            ExtractionResult with extracted fields
        """
        if not self.llm:
            # Fall back to regex extraction
            text = " ".join(msg.get("content", "") for msg in conversation)
            return self.extract_from_text(text, schema)
        
        # Build extraction prompt
        if schema is None and self.template:
            schema = self.template.get_extraction_schema()
        elif schema is None:
            schema = {"type": "object", "properties": {}}
        
        prompt = self._build_extraction_prompt(conversation, schema)
        
        try:
            response = await self.llm.generate(
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
            
            data = json.loads(response)
            return self._parse_llm_response(data, schema)
            
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            # Fall back to regex
            text = " ".join(msg.get("content", "") for msg in conversation)
            return self.extract_from_text(text)
    
    def _build_extraction_prompt(
        self, 
        conversation: List[Dict[str, str]],
        schema: Dict[str, Any],
    ) -> str:
        """Build prompt for LLM extraction."""
        conv_text = "\n".join(
            f"{msg.get('role', 'user')}: {msg.get('content', '')}"
            for msg in conversation
        )
        
        fields_desc = []
        for name, props in schema.get("properties", {}).items():
            desc = props.get("description", name)
            fields_desc.append(f"- {name}: {desc}")
        
        return f"""Extract the following information from the conversation below.
Return a JSON object with the extracted values. Use null for missing information.

Fields to extract:
{chr(10).join(fields_desc)}

Conversation:
{conv_text}

Return JSON only, no explanation."""
    
    def _parse_llm_response(
        self, 
        data: Dict[str, Any],
        schema: Dict[str, Any],
    ) -> ExtractionResult:
        """Parse LLM response into ExtractionResult."""
        result = ExtractionResult(raw_data=data)
        
        for name, value in data.items():
            if value is not None:
                result.fields[name] = ExtractedField(
                    name=name,
                    value=value,
                    confidence=0.9,  # LLM extraction has high confidence
                    validated=True,
                )
        
        # Track missing required
        required = schema.get("required", [])
        result.missing_required = [f for f in required if f not in result.fields]
        
        return result
    
    def update(self, text: str) -> ExtractionResult:
        """
        Incrementally update extraction with new text.
        
        Args:
            text: New text to extract from
            
        Returns:
            Updated extraction result
        """
        new_result = self.extract_from_text(text)
        
        # Merge with existing
        for name, field in new_result.fields.items():
            if name not in self._extracted_data or field.confidence > self._extracted_data[name].confidence:
                self._extracted_data[name] = field
        
        result = ExtractionResult(
            fields=self._extracted_data.copy(),
            raw_data={n: f.value for n, f in self._extracted_data.items()},
        )
        
        if self.template:
            required = [f.name for f in self.template.get_extraction_fields() if f.required]
            result.missing_required = [f for f in required if f not in result.fields]
        
        return result
    
    def get_missing_fields(self) -> List[str]:
        """Get list of required fields still missing."""
        if not self.template:
            return []
        
        required = [f.name for f in self.template.get_extraction_fields() if f.required]
        return [f for f in required if f not in self._extracted_data]
    
    def get_prompt_for_missing(self) -> Optional[str]:
        """Generate a prompt to ask for missing information."""
        missing = self.get_missing_fields()
        
        if not missing:
            return None
        
        if not self.template:
            return f"Could you please provide: {', '.join(missing)}?"
        
        # Get field descriptions
        fields = {f.name: f for f in self.template.get_extraction_fields()}
        
        prompts = []
        for name in missing[:2]:  # Ask for max 2 at a time
            field = fields.get(name)
            if field:
                prompts.append(field.description.lower())
        
        if len(prompts) == 1:
            return f"Could you please provide your {prompts[0]}?"
        else:
            return f"Could you please provide your {prompts[0]} and {prompts[1]}?"
    
    def reset(self) -> None:
        """Reset extracted data."""
        self._extracted_data.clear()
