"""
Sunona Voice AI - Smart Agent Selector

Automatically selects the best agent type based on:
- Use case requirements
- Available resources (knowledge base, graph, etc.)
- Conversation context
- User preferences

This ensures the right agent is used for each situation.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Type, Union
from dataclasses import dataclass, field
from enum import Enum

from sunona.agents.base_agent import (
    BaseAgent, AgentConfig, AgentCapability
)

logger = logging.getLogger(__name__)


class UseCase(Enum):
    """Predefined use cases for agent selection."""
    GENERAL_CONVERSATION = "general_conversation"
    LEAD_CAPTURE = "lead_capture"
    APPOINTMENT_BOOKING = "appointment_booking"
    CUSTOMER_SUPPORT = "customer_support"
    FAQ = "faq"
    SALES = "sales"
    IVR_MENU = "ivr_menu"
    SURVEY = "survey"
    DATA_COLLECTION = "data_collection"
    GUIDED_FLOW = "guided_flow"
    CRM_INTEGRATION = "crm_integration"


@dataclass
class AgentRequirements:
    """Requirements for agent selection."""
    use_case: Optional[UseCase] = None
    
    # Resources available
    has_knowledge_base: bool = False
    has_graph_flow: bool = False
    has_webhook: bool = False
    
    # Features needed
    needs_extraction: bool = False
    needs_summarization: bool = False
    needs_context_tracking: bool = False
    needs_crm_integration: bool = False
    
    # Hints from message content
    first_message: Optional[str] = None
    
    # Custom
    custom_requirements: Dict[str, Any] = field(default_factory=dict)


class SmartAgentSelector:
    """
    Intelligently selects the best agent for a given situation.
    
    Selection logic:
    1. Check explicit use case → Match to best agent
    2. Check available resources → Use appropriate agent
    3. Analyze first message → Detect intent
    4. Fall back to contextual conversational agent
    
    Example:
        ```python
        selector = SmartAgentSelector()
        
        # Based on use case
        agent = selector.select(AgentRequirements(
            use_case=UseCase.LEAD_CAPTURE,
            has_webhook=True,
        ))
        # Returns: ExtractionAgent with webhook integration
        
        # Auto-detect from message
        agent = selector.select_from_message(
            "I want to book an appointment for next week"
        )
        # Returns: ExtractionAgent (detects appointment booking intent)
        ```
    """
    
    # Intent detection patterns
    INTENT_PATTERNS = {
        "appointment": [
            r"book(?:ing)?", r"appointment", r"schedule", r"reserve",
            r"set up a time", r"meeting", r"consultation",
        ],
        "lead_capture": [
            r"interested", r"more information", r"demo", r"pricing",
            r"contact me", r"call me back", r"sign up",
        ],
        "support": [
            r"help", r"problem", r"issue", r"not working", r"error",
            r"broken", r"fix", r"support", r"trouble",
        ],
        "faq": [
            r"what is", r"how do", r"where can", r"when does",
            r"why does", r"tell me about", r"explain",
        ],
        "sales": [
            r"buy", r"purchase", r"order", r"pricing", r"cost",
            r"discount", r"deal", r"offer",
        ],
    }
    
    def __init__(self):
        # Lazy imports to avoid circular dependencies
        self._agent_classes = None
    
    def _get_agent_classes(self) -> Dict[str, Type[BaseAgent]]:
        """Get agent classes with lazy loading."""
        if self._agent_classes is None:
            from sunona.agents.contextual_conversational_agent import ContextualConversationalAgent
            from sunona.agents.extraction_agent import (
                ExtractionAgent, create_lead_capture_agent, create_appointment_agent
            )
            from sunona.agents.graph_agent import GraphAgent
            from sunona.agents.graph_based_conversational_agent import GraphBasedConversationalAgent
            from sunona.agents.knowledgebase_agent import KnowledgeBaseAgent
            from sunona.agents.summarization_agent import SummarizationAgent
            from sunona.agents.webhook_agent import WebhookAgent
            
            self._agent_classes = {
                "contextual": ContextualConversationalAgent,
                "extraction": ExtractionAgent,
                "graph": GraphAgent,
                "graph_conversational": GraphBasedConversationalAgent,
                "knowledge_base": KnowledgeBaseAgent,
                "summarization": SummarizationAgent,
                "webhook": WebhookAgent,
            }
        
        return self._agent_classes
    
    def select(
        self,
        requirements: AgentRequirements,
        config: Optional[AgentConfig] = None,
        llm: Optional[Any] = None,
        **kwargs,
    ) -> BaseAgent:
        """
        Select the best agent based on requirements.
        
        Args:
            requirements: What the agent needs to do
            config: Agent configuration
            llm: LLM instance
            **kwargs: Additional resources (knowledge_base, graph, etc.)
            
        Returns:
            Configured agent instance
        """
        agent_type = self._determine_agent_type(requirements)
        
        logger.info(f"Selected agent type: {agent_type} for {requirements.use_case}")
        
        return self._create_agent(
            agent_type=agent_type,
            requirements=requirements,
            config=config,
            llm=llm,
            **kwargs,
        )
    
    def select_from_message(
        self,
        first_message: str,
        config: Optional[AgentConfig] = None,
        llm: Optional[Any] = None,
        **kwargs,
    ) -> BaseAgent:
        """
        Select agent based on first message content.
        
        Analyzes the message to detect intent and selects appropriate agent.
        
        Args:
            first_message: First message from user
            config: Agent configuration
            llm: LLM instance
            
        Returns:
            Agent suited for the detected intent
        """
        intent = self._detect_intent(first_message)
        use_case = self._intent_to_use_case(intent)
        
        requirements = AgentRequirements(
            use_case=use_case,
            first_message=first_message,
            has_knowledge_base=kwargs.get("knowledge_base") is not None,
            has_graph_flow=kwargs.get("graph") is not None,
        )
        
        return self.select(requirements, config, llm, **kwargs)
    
    def _determine_agent_type(self, req: AgentRequirements) -> str:
        """Determine the best agent type for requirements."""
        
        # Priority 1: Explicit use case
        if req.use_case:
            use_case_mapping = {
                UseCase.LEAD_CAPTURE: "extraction",
                UseCase.APPOINTMENT_BOOKING: "extraction",
                UseCase.DATA_COLLECTION: "extraction",
                UseCase.SURVEY: "extraction",
                UseCase.FAQ: "knowledge_base",
                UseCase.CUSTOMER_SUPPORT: "knowledge_base",
                UseCase.IVR_MENU: "graph",
                UseCase.GUIDED_FLOW: "graph_conversational",
                UseCase.SALES: "graph_conversational",
                UseCase.CRM_INTEGRATION: "webhook",
                UseCase.GENERAL_CONVERSATION: "contextual",
            }
            
            agent_type = use_case_mapping.get(req.use_case)
            if agent_type:
                return agent_type
        
        # Priority 2: Resource-based selection
        if req.has_graph_flow:
            # Has a graph defined
            if req.needs_context_tracking:
                return "graph_conversational"  # Hybrid
            return "graph"
        
        if req.has_knowledge_base:
            return "knowledge_base"
        
        # Priority 3: Feature-based selection
        if req.needs_extraction:
            return "extraction"
        
        if req.needs_summarization:
            return "summarization"
        
        if req.needs_crm_integration or req.has_webhook:
            return "webhook"
        
        if req.needs_context_tracking:
            return "contextual"
        
        # Default: Contextual conversational (most flexible)
        return "contextual"
    
    def _detect_intent(self, message: str) -> str:
        """Detect user intent from message."""
        message_lower = message.lower()
        
        intent_scores = {}
        
        for intent, patterns in self.INTENT_PATTERNS.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    score += 1
            if score > 0:
                intent_scores[intent] = score
        
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        
        return "general"
    
    def _intent_to_use_case(self, intent: str) -> UseCase:
        """Map detected intent to use case."""
        mapping = {
            "appointment": UseCase.APPOINTMENT_BOOKING,
            "lead_capture": UseCase.LEAD_CAPTURE,
            "support": UseCase.CUSTOMER_SUPPORT,
            "faq": UseCase.FAQ,
            "sales": UseCase.SALES,
            "general": UseCase.GENERAL_CONVERSATION,
        }
        return mapping.get(intent, UseCase.GENERAL_CONVERSATION)
    
    def _create_agent(
        self,
        agent_type: str,
        requirements: AgentRequirements,
        config: Optional[AgentConfig],
        llm: Optional[Any],
        **kwargs,
    ) -> BaseAgent:
        """Create and configure the selected agent."""
        classes = self._get_agent_classes()
        
        agent_class = classes.get(agent_type, classes["contextual"])
        
        # Build kwargs for agent
        agent_kwargs = {"config": config, "llm": llm}
        
        # Add specialized kwargs
        if agent_type == "knowledge_base" and kwargs.get("knowledge_base"):
            agent_kwargs["knowledge_base"] = kwargs["knowledge_base"]
        
        if agent_type in ["graph", "graph_conversational"] and kwargs.get("graph"):
            agent_kwargs["graph"] = kwargs["graph"]
        
        if agent_type == "knowledge_base" and kwargs.get("vector_store"):
            agent_kwargs["vector_store"] = kwargs["vector_store"]
        
        # Create agent
        agent = agent_class(**agent_kwargs)
        
        # Configure based on use case
        if requirements.use_case == UseCase.LEAD_CAPTURE:
            self._configure_for_lead_capture(agent)
        elif requirements.use_case == UseCase.APPOINTMENT_BOOKING:
            self._configure_for_appointment(agent)
        
        return agent
    
    def _configure_for_lead_capture(self, agent: BaseAgent):
        """Configure agent for lead capture."""
        from sunona.agents.extraction_agent import ExtractionAgent, ExtractionField
        
        if isinstance(agent, ExtractionAgent):
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
            ])
    
    def _configure_for_appointment(self, agent: BaseAgent):
        """Configure agent for appointment booking."""
        from sunona.agents.extraction_agent import ExtractionAgent, ExtractionField
        
        if isinstance(agent, ExtractionAgent):
            agent.add_fields([
                ExtractionField(
                    name="name",
                    description="Customer name",
                    required=True,
                    prompt_question="May I have your name for the appointment?",
                ),
                ExtractionField(
                    name="date",
                    description="Preferred date",
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


class AdaptiveAgent(BaseAgent):
    """
    An agent that adapts its behavior based on conversation context.
    
    Dynamically switches between agent behaviors as needed:
    - Starts as conversational
    - Switches to extraction when data needed
    - Uses knowledge base when questions detected
    - Generates summaries on demand
    
    This provides the benefits of all specialized agents in one.
    
    Example:
        ```python
        agent = AdaptiveAgent(
            config=config,
            llm=llm,
            knowledge_base=kb,  # Optional
        )
        
        # Starts conversational
        response = await agent.process_message("Hi there!")
        
        # Detects extraction need
        response = await agent.process_message("I'd like to book an appointment")
        # Automatically starts collecting: name, date, time...
        
        # Detects FAQ
        response = await agent.process_message("What are your hours?")
        # Checks knowledge base
        ```
    """
    
    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        llm: Optional[Any] = None,
        knowledge_base: Optional[Any] = None,
        graph: Optional[Any] = None,
    ):
        super().__init__(config, llm)
        
        self.knowledge_base = knowledge_base
        self.graph = graph
        
        # Sub-agents (created on demand)
        self._extraction_agent = None
        self._kb_agent = None
        
        # Current mode
        self._mode = "conversational"
        self._extraction_fields: Dict[str, Any] = {}
        
        # Intent patterns from SmartAgentSelector
        self._intent_patterns = SmartAgentSelector.INTENT_PATTERNS
    
    @property
    def capabilities(self) -> List[AgentCapability]:
        caps = [AgentCapability.CONVERSATION]
        if self.knowledge_base:
            caps.append(AgentCapability.KNOWLEDGE_BASE)
        return caps
    
    async def process_message(self, message: str) -> "AgentResponse":
        """Process message with adaptive behavior."""
        from sunona.agents.base_agent import AgentResponse
        
        self._set_state(AgentState.LISTENING)
        self.add_message("user", message)
        
        # Detect what type of handling is needed
        current_intent = self._detect_intent(message)
        
        # Handle based on intent
        if current_intent == "appointment" and not self._extraction_fields:
            # Start appointment booking mode
            self._mode = "extraction"
            response = await self._handle_extraction_start("appointment", message)
        
        elif current_intent == "lead_capture" and not self._extraction_fields:
            self._mode = "extraction"
            response = await self._handle_extraction_start("lead", message)
        
        elif self._mode == "extraction":
            # Continue extraction
            response = await self._handle_extraction_continue(message)
        
        elif current_intent in ["faq", "support"] and self.knowledge_base:
            # Use knowledge base
            response = await self._handle_knowledge_query(message)
        
        else:
            # General conversation
            response = await self._handle_conversation(message)
        
        self.add_message("assistant", response.text)
        self._set_state(AgentState.SPEAKING)
        
        return response
    
    def _detect_intent(self, message: str) -> str:
        """Detect intent from message."""
        message_lower = message.lower()
        
        for intent, patterns in self._intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return intent
        
        return "general"
    
    async def _handle_extraction_start(
        self,
        extraction_type: str,
        message: str,
    ) -> "AgentResponse":
        """Start extraction flow."""
        from sunona.agents.base_agent import AgentResponse
        
        if extraction_type == "appointment":
            self._extraction_fields = {
                "name": {"required": True, "value": None},
                "date": {"required": True, "value": None},
                "time": {"required": True, "value": None},
                "phone": {"required": True, "value": None},
            }
            
            # Check if name is in message
            self._extract_from_message(message)
            
            next_field = self._get_next_missing_field()
            if next_field:
                prompts = {
                    "name": "I'd be happy to help you book an appointment. May I have your name?",
                    "date": "What date works best for you?",
                    "time": "And what time would you prefer?",
                    "phone": "What phone number should we use to confirm?",
                }
                return AgentResponse(text=prompts.get(next_field, "Please continue."))
        
        elif extraction_type == "lead":
            self._extraction_fields = {
                "name": {"required": True, "value": None},
                "email": {"required": True, "value": None},
                "phone": {"required": False, "value": None},
            }
            
            self._extract_from_message(message)
            next_field = self._get_next_missing_field()
            
            if next_field:
                prompts = {
                    "name": "I'd love to help you. May I have your name?",
                    "email": "What's the best email to reach you?",
                    "phone": "And your phone number?",
                }
                return AgentResponse(text=prompts.get(next_field, "Please continue."))
        
        return AgentResponse(text="How can I help you today?")
    
    async def _handle_extraction_continue(self, message: str) -> "AgentResponse":
        """Continue extraction flow."""
        from sunona.agents.base_agent import AgentResponse
        
        # Extract from latest message
        self._extract_from_message(message)
        
        next_field = self._get_next_missing_field()
        
        if not next_field:
            # All required fields collected
            self._mode = "conversational"
            extracted = {k: v["value"] for k, v in self._extraction_fields.items() if v["value"]}
            
            return AgentResponse(
                text="Perfect! I have all your information. Is there anything else I can help you with?",
                data={"extracted": extracted, "extraction_complete": True},
            )
        
        prompts = {
            "name": "May I have your name?",
            "email": "What's your email address?",
            "phone": "What's your phone number?",
            "date": "What date works for you?",
            "time": "What time would you prefer?",
        }
        
        return AgentResponse(text=prompts.get(next_field, f"Could you provide your {next_field}?"))
    
    def _extract_from_message(self, message: str):
        """Extract field values from message."""
        import re
        
        # Email
        if "email" in self._extraction_fields and not self._extraction_fields["email"]["value"]:
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', message)
            if email_match:
                self._extraction_fields["email"]["value"] = email_match.group()
        
        # Phone
        if "phone" in self._extraction_fields and not self._extraction_fields["phone"]["value"]:
            phone_match = re.search(r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{7,}', message)
            if phone_match:
                self._extraction_fields["phone"]["value"] = phone_match.group()
        
        # Name (first message often contains name)
        if "name" in self._extraction_fields and not self._extraction_fields["name"]["value"]:
            name_patterns = [
                r"(?:i'm|i am|my name is|this is)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)?)",
                r"^([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)$",
            ]
            for pattern in name_patterns:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    self._extraction_fields["name"]["value"] = match.group(1).title()
                    break
        
        # Date
        if "date" in self._extraction_fields and not self._extraction_fields["date"]["value"]:
            date_patterns = [
                r'\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
                r'\b(?:next|this)\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
                r'\d{1,2}[/-]\d{1,2}[/-]?\d{0,4}',
            ]
            for pattern in date_patterns:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    self._extraction_fields["date"]["value"] = match.group()
                    break
        
        # Time
        if "time" in self._extraction_fields and not self._extraction_fields["time"]["value"]:
            time_match = re.search(r'\d{1,2}:\d{2}\s*(?:am|pm)?|\d{1,2}\s*(?:am|pm)', message, re.IGNORECASE)
            if time_match:
                self._extraction_fields["time"]["value"] = time_match.group()
    
    def _get_next_missing_field(self) -> Optional[str]:
        """Get next required field that's missing."""
        for field, info in self._extraction_fields.items():
            if info.get("required") and not info.get("value"):
                return field
        return None
    
    async def _handle_knowledge_query(self, message: str) -> "AgentResponse":
        """Handle query using knowledge base."""
        from sunona.agents.base_agent import AgentResponse
        
        # Search knowledge base
        if hasattr(self.knowledge_base, "full_text"):
            # Simple keyword search
            query_words = set(message.lower().split())
            kb_text = self.knowledge_base.full_text.lower()
            
            # Find relevant section
            for word in query_words:
                if word in kb_text and len(word) > 3:
                    # Found relevant content
                    if self.llm:
                        prompt = f"""Answer this question using the knowledge base:

KNOWLEDGE:
{self.knowledge_base.full_text[:2000]}

QUESTION: {message}

Provide a concise answer for a phone conversation (1-2 sentences).
"""
                        response_text = await self.llm.generate([{"role": "user", "content": prompt}])
                        return AgentResponse(text=response_text, data={"source": "knowledge_base"})
        
        # Fall back to general response
        return await self._handle_conversation(message)
    
    async def _handle_conversation(self, message: str) -> "AgentResponse":
        """Handle general conversation."""
        from sunona.agents.base_agent import AgentResponse
        
        self._set_state(AgentState.THINKING)
        response_text = await self.generate_response()
        
        return AgentResponse(text=response_text)


# Global selector instance
_selector = None


def get_smart_selector() -> SmartAgentSelector:
    """Get global smart agent selector."""
    global _selector
    if _selector is None:
        _selector = SmartAgentSelector()
    return _selector


def select_agent(
    use_case: Optional[Union[str, UseCase]] = None,
    first_message: Optional[str] = None,
    **kwargs,
) -> BaseAgent:
    """
    Convenience function to select the best agent.
    
    Args:
        use_case: Explicit use case (or auto-detect from message)
        first_message: First message to analyze for intent
        **kwargs: Additional arguments (config, llm, knowledge_base, etc.)
        
    Returns:
        Best agent for the situation
        
    Example:
        ```python
        # Auto-detect from message
        agent = select_agent(first_message="I want to book an appointment")
        
        # Explicit use case
        agent = select_agent(use_case="lead_capture")
        
        # With resources
        agent = select_agent(
            use_case="faq",
            knowledge_base=my_kb,
            llm=my_llm,
        )
        ```
    """
    selector = get_smart_selector()
    
    if first_message and not use_case:
        return selector.select_from_message(first_message, **kwargs)
    
    # Convert string to UseCase
    if isinstance(use_case, str):
        use_case = UseCase[use_case.upper()] if use_case.upper() in UseCase.__members__ else UseCase.GENERAL_CONVERSATION
    
    requirements = AgentRequirements(
        use_case=use_case,
        has_knowledge_base=kwargs.get("knowledge_base") is not None,
        has_graph_flow=kwargs.get("graph") is not None,
        first_message=first_message,
    )
    
    return selector.select(requirements, **kwargs)
