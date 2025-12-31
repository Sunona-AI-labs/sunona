"""
Sunona Voice AI - Agents Module

Provides various specialized AI agent types for different use cases.
"""

from sunona.agents.base_agent import (
    BaseAgent,
    AgentConfig,
    AgentResponse,
    AgentState,
    AgentCapability,
    ConversationTurn,
)

from sunona.agents.contextual_conversational_agent import (
    ContextualConversationalAgent,
)

from sunona.agents.extraction_agent import (
    ExtractionAgent,
    ExtractionField,
    ExtractionResult,
    create_lead_capture_agent,
    create_appointment_agent,
)

from sunona.agents.graph_agent import (
    GraphAgent,
    ConversationGraph,
    GraphNode,
    GraphEdge,
    NodeType,
    create_simple_ivr_graph,
    create_qualification_graph,
)

from sunona.agents.graph_based_conversational_agent import (
    GraphBasedConversationalAgent,
)

from sunona.agents.knowledgebase_agent import (
    KnowledgeBaseAgent,
)

from sunona.agents.summarization_agent import (
    SummarizationAgent,
)

from sunona.agents.webhook_agent import (
    WebhookAgent,
    WebhookTrigger,
    WebhookEvent,
    WebhookResult,
    create_crm_webhook_agent,
    create_analytics_webhook_agent,
)


__all__ = [
    # Base
    "BaseAgent",
    "AgentConfig",
    "AgentResponse",
    "AgentState",
    "AgentCapability",
    "ConversationTurn",
    
    # Contextual
    "ContextualConversationalAgent",
    
    # Extraction
    "ExtractionAgent",
    "ExtractionField",
    "ExtractionResult",
    "create_lead_capture_agent",
    "create_appointment_agent",
    
    # Graph
    "GraphAgent",
    "ConversationGraph",
    "GraphNode",
    "GraphEdge",
    "NodeType",
    "create_simple_ivr_graph",
    "create_qualification_graph",
    
    # Hybrid Graph
    "GraphBasedConversationalAgent",
    
    # Knowledge Base
    "KnowledgeBaseAgent",
    
    # Summarization
    "SummarizationAgent",
    
    # Webhook
    "WebhookAgent",
    "WebhookTrigger",
    "WebhookEvent",
    "WebhookResult",
    "create_crm_webhook_agent",
    "create_analytics_webhook_agent",
]


# Agent type registry
AGENT_TYPES = {
    "base": BaseAgent,
    "contextual": ContextualConversationalAgent,
    "extraction": ExtractionAgent,
    "graph": GraphAgent,
    "graph_conversational": GraphBasedConversationalAgent,
    "knowledge_base": KnowledgeBaseAgent,
    "summarization": SummarizationAgent,
    "webhook": WebhookAgent,
}


def get_agent_class(agent_type: str) -> type:
    """
    Get agent class by type name.
    
    Args:
        agent_type: One of: base, contextual, extraction, graph,
                    graph_conversational, knowledge_base, summarization, webhook
                    
    Returns:
        Agent class
    """
    return AGENT_TYPES.get(agent_type.lower(), BaseAgent)


def create_agent(
    agent_type: str,
    config: AgentConfig = None,
    **kwargs,
) -> BaseAgent:
    """
    Factory function to create agents.
    
    Args:
        agent_type: Type of agent to create
        config: Agent configuration
        **kwargs: Additional arguments for specific agent types
        
    Returns:
        Configured agent instance
        
    Example:
        ```python
        # Create a lead capture agent
        agent = create_agent(
            "extraction",
            config=AgentConfig(name="Lead Bot"),
        )
        
        # Create a knowledge base agent
        agent = create_agent(
            "knowledge_base",
            knowledge_base=my_kb,
        )
        ```
    """
    agent_class = get_agent_class(agent_type)
    return agent_class(config=config, **kwargs)


# Smart agent selection
from sunona.agents.agent_selector import (
    SmartAgentSelector,
    AdaptiveAgent,
    AgentRequirements,
    UseCase,
    select_agent,
    get_smart_selector,
)

__all__.extend([
    "SmartAgentSelector",
    "AdaptiveAgent",
    "AgentRequirements",
    "UseCase",
    "select_agent",
    "get_smart_selector",
])
