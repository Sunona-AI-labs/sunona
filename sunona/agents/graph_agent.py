"""
Sunona Voice AI - Graph Agent

Agent that follows a conversation flow graph/tree.
Enables complex branching conversations with defined paths.
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

from sunona.agents.base_agent import (
    BaseAgent, AgentConfig, AgentResponse, AgentCapability, AgentState
)

logger = logging.getLogger(__name__)


class NodeType(Enum):
    """Types of conversation nodes."""
    MESSAGE = "message"       # Say something
    QUESTION = "question"     # Ask and branch
    CONDITION = "condition"   # Branch based on logic
    ACTION = "action"         # Perform an action
    TRANSFER = "transfer"     # Transfer call
    END = "end"              # End conversation


@dataclass
class GraphNode:
    """A node in the conversation graph."""
    id: str
    node_type: NodeType
    content: str = ""
    
    # Next node(s)
    next_node: Optional[str] = None
    branches: Dict[str, str] = field(default_factory=dict)  # keyword -> node_id
    
    # For conditions
    condition: Optional[Callable] = None
    
    # For actions
    action: Optional[Callable] = None
    action_name: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEdge:
    """An edge connecting two nodes."""
    from_node: str
    to_node: str
    condition: Optional[str] = None
    keywords: List[str] = field(default_factory=list)


class ConversationGraph:
    """
    Defines a conversation flow as a directed graph.
    
    Example:
        ```python
        graph = ConversationGraph()
        
        # Define nodes
        graph.add_node(GraphNode(
            id="greeting",
            node_type=NodeType.MESSAGE,
            content="Hello! How can I help you today?",
            branches={
                "pricing": "pricing_info",
                "support": "support_flow",
                "speak to human": "transfer",
            },
        ))
        
        graph.add_node(GraphNode(
            id="pricing_info",
            node_type=NodeType.MESSAGE,
            content="Our pricing starts at $29/month...",
            next_node="anything_else",
        ))
        ```
    """
    
    def __init__(self, name: str = "Conversation Flow"):
        self.name = name
        self.nodes: Dict[str, GraphNode] = {}
        self.start_node: Optional[str] = None
    
    def add_node(self, node: GraphNode):
        """Add a node to the graph."""
        self.nodes[node.id] = node
        
        # First node is start by default
        if self.start_node is None:
            self.start_node = node.id
    
    def set_start_node(self, node_id: str):
        """Set the starting node."""
        if node_id in self.nodes:
            self.start_node = node_id
    
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)
    
    def get_next_node(
        self,
        current_node_id: str,
        user_input: str = "",
        context: Optional[Dict] = None,
    ) -> Optional[GraphNode]:
        """
        Get the next node based on current state and input.
        """
        current = self.get_node(current_node_id)
        if not current:
            return None
        
        # Check branches based on keywords
        if current.branches:
            input_lower = user_input.lower()
            for keyword, next_id in current.branches.items():
                if keyword.lower() in input_lower:
                    return self.get_node(next_id)
        
        # Check condition
        if current.node_type == NodeType.CONDITION and current.condition:
            try:
                result = current.condition(user_input, context or {})
                if result in current.branches:
                    return self.get_node(current.branches[result])
            except Exception as e:
                logger.error(f"Condition error: {e}")
        
        # Default to next_node
        if current.next_node:
            return self.get_node(current.next_node)
        
        return None


class GraphAgent(BaseAgent):
    """
    Agent that follows a predefined conversation graph.
    
    Features:
    - Follows defined conversation paths
    - Branching based on user responses
    - Conditions and actions at each node
    - Easy to visualize and design
    - Predictable conversation flows
    
    Best for:
    - IVR-style menus
    - Guided conversations
    - Scripts with branches
    - Qualification flows
    
    Example:
        ```python
        # Create graph
        graph = ConversationGraph()
        graph.add_node(GraphNode(
            id="start",
            node_type=NodeType.QUESTION,
            content="Are you calling about sales or support?",
            branches={"sales": "sales_flow", "support": "support_flow"},
        ))
        
        # Create agent
        agent = GraphAgent(graph=graph)
        
        # Process
        response = await agent.process_message("I need help with sales")
        # Agent moves to sales_flow node
        ```
    """
    
    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        llm: Optional[Any] = None,
        graph: Optional[ConversationGraph] = None,
    ):
        super().__init__(config, llm)
        
        self.graph = graph or ConversationGraph()
        self._current_node_id: Optional[str] = None
        self._visited_nodes: List[str] = []
    
    @property
    def capabilities(self) -> List[AgentCapability]:
        return [AgentCapability.GRAPH_FLOW]
    
    @property
    def current_node(self) -> Optional[GraphNode]:
        """Get current node."""
        if self._current_node_id:
            return self.graph.get_node(self._current_node_id)
        return None
    
    async def start(self):
        """Start the graph agent."""
        await super().start()
        
        # Move to start node
        self._current_node_id = self.graph.start_node
        
        if self.current_node:
            self._visited_nodes.append(self._current_node_id)
    
    async def process_message(self, message: str) -> AgentResponse:
        """Process message following graph."""
        self._set_state(AgentState.LISTENING)
        self.add_message("user", message)
        
        # Get current node
        current = self.current_node
        if not current:
            # No graph defined, fall back to LLM
            response = await self.generate_response()
            self.add_message("assistant", response)
            return AgentResponse(text=response)
        
        # Find next node
        next_node = self.graph.get_next_node(
            self._current_node_id,
            message,
            {"history": self._visited_nodes},
        )
        
        if next_node:
            self._current_node_id = next_node.id
            self._visited_nodes.append(next_node.id)
            
            # Handle node type
            return await self._handle_node(next_node, message)
        
        # No matching branch, use LLM or repeat
        if self.llm:
            response = await self.generate_response()
        else:
            response = current.content or "I didn't quite catch that. Could you repeat?"
        
        self.add_message("assistant", response)
        return AgentResponse(text=response)
    
    async def _handle_node(
        self,
        node: GraphNode,
        user_message: str,
    ) -> AgentResponse:
        """Handle different node types."""
        
        if node.node_type == NodeType.MESSAGE:
            self.add_message("assistant", node.content)
            return AgentResponse(
                text=node.content,
                data={"node_id": node.id, "node_type": "message"},
            )
        
        elif node.node_type == NodeType.QUESTION:
            self.add_message("assistant", node.content)
            return AgentResponse(
                text=node.content,
                data={"node_id": node.id, "node_type": "question", "expects_response": True},
            )
        
        elif node.node_type == NodeType.ACTION:
            # Execute action
            action_result = None
            if node.action:
                try:
                    action_result = await node.action(user_message, self)
                except Exception as e:
                    logger.error(f"Action error: {e}")
            
            response = node.content or "Processing..."
            self.add_message("assistant", response)
            
            return AgentResponse(
                text=response,
                data={
                    "node_id": node.id,
                    "node_type": "action",
                    "action_name": node.action_name,
                    "action_result": action_result,
                },
            )
        
        elif node.node_type == NodeType.TRANSFER:
            return await self.transfer(node.content or "user_request")
        
        elif node.node_type == NodeType.END:
            await self.end("graph_completed")
            return AgentResponse(
                text=node.content or "Thank you for calling. Goodbye!",
                action="end",
            )
        
        # Default
        return AgentResponse(text=node.content)
    
    def go_to_node(self, node_id: str):
        """Manually move to a specific node."""
        if node_id in self.graph.nodes:
            self._current_node_id = node_id
            self._visited_nodes.append(node_id)
    
    def get_flow_summary(self) -> Dict[str, Any]:
        """Get summary of conversation flow."""
        return {
            "current_node": self._current_node_id,
            "visited_nodes": self._visited_nodes,
            "total_nodes": len(self.graph.nodes),
            "path_length": len(self._visited_nodes),
        }


# ==================== Pre-built Flow Templates ====================

def create_simple_ivr_graph() -> ConversationGraph:
    """Create a simple IVR-style graph."""
    graph = ConversationGraph("Simple IVR")
    
    graph.add_node(GraphNode(
        id="greeting",
        node_type=NodeType.QUESTION,
        content="Hello! Press 1 or say 'sales' for sales, press 2 or say 'support' for support.",
        branches={
            "1": "sales",
            "sales": "sales",
            "2": "support",
            "support": "support",
            "human": "transfer",
            "agent": "transfer",
        },
    ))
    
    graph.add_node(GraphNode(
        id="sales",
        node_type=NodeType.MESSAGE,
        content="Connecting you to our sales team...",
        next_node="transfer_sales",
    ))
    
    graph.add_node(GraphNode(
        id="support",
        node_type=NodeType.MESSAGE,
        content="Let me help you with support. What issue are you experiencing?",
        next_node="support_detail",
    ))
    
    graph.add_node(GraphNode(
        id="transfer_sales",
        node_type=NodeType.TRANSFER,
        content="Transferring to sales...",
    ))
    
    graph.add_node(GraphNode(
        id="support_detail",
        node_type=NodeType.QUESTION,
        content="Is this regarding billing, technical issues, or something else?",
        branches={
            "billing": "billing_support",
            "technical": "tech_support",
        },
        next_node="general_support",
    ))
    
    graph.add_node(GraphNode(
        id="transfer",
        node_type=NodeType.TRANSFER,
        content="Connecting you with an agent...",
    ))
    
    return graph


def create_qualification_graph() -> ConversationGraph:
    """Create a lead qualification graph."""
    graph = ConversationGraph("Lead Qualification")
    
    graph.add_node(GraphNode(
        id="start",
        node_type=NodeType.MESSAGE,
        content="Hi! I'd love to learn more about your needs. Are you currently using any similar solution?",
        branches={"yes": "current_solution", "no": "new_user"},
    ))
    
    graph.add_node(GraphNode(
        id="current_solution",
        node_type=NodeType.QUESTION,
        content="What are you currently using and what challenges are you facing?",
        next_node="timeline",
    ))
    
    graph.add_node(GraphNode(
        id="new_user",
        node_type=NodeType.QUESTION,
        content="What prompted you to look for a solution now?",
        next_node="timeline",
    ))
    
    graph.add_node(GraphNode(
        id="timeline",
        node_type=NodeType.QUESTION,
        content="When are you looking to make a decision?",
        next_node="budget",
    ))
    
    graph.add_node(GraphNode(
        id="budget",
        node_type=NodeType.QUESTION,
        content="Do you have a budget in mind for this solution?",
        next_node="qualified",
    ))
    
    graph.add_node(GraphNode(
        id="qualified",
        node_type=NodeType.MESSAGE,
        content="Great! Based on what you've shared, I think we can definitely help. Let me connect you with a specialist.",
        next_node="transfer",
    ))
    
    graph.add_node(GraphNode(
        id="transfer",
        node_type=NodeType.TRANSFER,
        content="Connecting with specialist...",
    ))
    
    return graph
