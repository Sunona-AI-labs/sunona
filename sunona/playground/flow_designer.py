"""
Sunona Voice AI - Visual Flow Designer

Backend support for visual IVR/conversation flow design.
Enables drag-and-drop creation of decision trees and conversation graphs.

Features:
- Node-based flow editor support
- Condition evaluation
- Dynamic flow execution
- State management
"""

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Awaitable

logger = logging.getLogger(__name__)


class NodeType(Enum):
    """Types of nodes in a conversation flow."""
    START = "start"
    MESSAGE = "message"
    QUESTION = "question"
    CONDITION = "condition"
    TRANSFER = "transfer"
    WEBHOOK = "webhook"
    SET_VARIABLE = "set_variable"
    WAIT = "wait"
    END = "end"
    SUB_FLOW = "sub_flow"


class ConditionOperator(Enum):
    """Operators for condition nodes."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    MATCHES_INTENT = "matches_intent"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"


@dataclass
class Position:
    """Visual position of a node."""
    x: float = 0
    y: float = 0
    
    def to_dict(self) -> Dict[str, float]:
        return {"x": self.x, "y": self.y}


@dataclass
class Connection:
    """Connection between nodes."""
    id: str
    source_node: str
    source_port: str  # "default", "yes", "no", or custom
    target_node: str
    target_port: str = "input"
    label: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source_node,
            "sourceHandle": self.source_port,
            "target": self.target_node,
            "targetHandle": self.target_port,
            "label": self.label,
        }


@dataclass
class FlowNode:
    """
    A node in the conversation flow.
    
    Each node type has specific properties:
    - MESSAGE: text to speak
    - QUESTION: text + variable to store answer
    - CONDITION: variable + operator + value
    - TRANSFER: transfer_number
    - WEBHOOK: url, method, headers
    - SET_VARIABLE: variable + value
    - WAIT: duration
    """
    id: str
    type: NodeType
    name: str = ""
    position: Position = field(default_factory=Position)
    
    # Common properties
    properties: Dict[str, Any] = field(default_factory=dict)
    
    # Visual
    color: str = "#4F46E5"
    icon: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "position": self.position.to_dict(),
            "data": self.properties,
            "color": self.color,
            "icon": self.icon,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FlowNode":
        """Create node from dictionary."""
        position = Position(
            x=data.get("position", {}).get("x", 0),
            y=data.get("position", {}).get("y", 0),
        )
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            type=NodeType(data.get("type", "message")),
            name=data.get("name", ""),
            position=position,
            properties=data.get("data", {}),
            color=data.get("color", "#4F46E5"),
            icon=data.get("icon", ""),
        )


@dataclass
class ConversationFlow:
    """
    Complete conversation flow definition.
    
    A flow consists of nodes and connections that define
    how a conversation progresses.
    """
    id: str
    name: str
    description: str = ""
    
    # Flow structure
    nodes: Dict[str, FlowNode] = field(default_factory=dict)
    connections: List[Connection] = field(default_factory=list)
    
    # Entry point
    start_node_id: Optional[str] = None
    
    # Variables
    variables: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    organization_id: Optional[str] = None
    created_by: Optional[str] = None
    
    # Status
    is_published: bool = False
    version: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [conn.to_dict() for conn in self.connections],
            "start_node_id": self.start_node_id,
            "variables": self.variables,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_published": self.is_published,
            "version": self.version,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationFlow":
        """Create flow from dictionary."""
        flow = cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", "Untitled Flow"),
            description=data.get("description", ""),
        )
        
        # Parse nodes
        for node_data in data.get("nodes", []):
            node = FlowNode.from_dict(node_data)
            flow.nodes[node.id] = node
        
        # Parse connections
        for edge_data in data.get("edges", []):
            conn = Connection(
                id=edge_data.get("id", str(uuid.uuid4())),
                source_node=edge_data.get("source", ""),
                source_port=edge_data.get("sourceHandle", "default"),
                target_node=edge_data.get("target", ""),
                target_port=edge_data.get("targetHandle", "input"),
                label=edge_data.get("label", ""),
            )
            flow.connections.append(conn)
        
        flow.start_node_id = data.get("start_node_id")
        flow.variables = data.get("variables", {})
        flow.is_published = data.get("is_published", False)
        flow.version = data.get("version", 1)
        
        return flow


@dataclass
class FlowExecutionState:
    """State of a flow execution instance."""
    flow_id: str
    current_node_id: str
    variables: Dict[str, Any] = field(default_factory=dict)
    history: List[str] = field(default_factory=list)  # Node IDs visited
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_complete: bool = False


class FlowDesigner:
    """
    Visual flow designer service.
    
    Provides CRUD operations for conversation flows
    and supports the visual editor frontend.
    
    Example:
        designer = FlowDesigner()
        
        # Create new flow
        flow = await designer.create_flow("Welcome IVR")
        
        # Add nodes
        start = await designer.add_node(flow.id, NodeType.START, {"x": 100, "y": 100})
        greeting = await designer.add_node(
            flow.id, NodeType.MESSAGE,
            {"x": 100, "y": 200},
            properties={"text": "Welcome! Press 1 for sales, 2 for support."}
        )
        
        # Connect nodes
        await designer.connect_nodes(flow.id, start.id, greeting.id)
        
        # Save and publish
        await designer.publish_flow(flow.id)
    """
    
    def __init__(self):
        self._flows: Dict[str, ConversationFlow] = {}
        self._node_templates: Dict[NodeType, Dict[str, Any]] = self._init_templates()
    
    def _init_templates(self) -> Dict[NodeType, Dict[str, Any]]:
        """Initialize node type templates."""
        return {
            NodeType.START: {
                "name": "Start",
                "icon": "▶️",
                "color": "#10B981",
                "properties": {},
                "outputs": ["default"],
            },
            NodeType.MESSAGE: {
                "name": "Speak Message",
                "icon": "💬",
                "color": "#3B82F6",
                "properties": {
                    "text": "",
                    "voice": "",
                    "wait_for_response": False,
                },
                "outputs": ["default"],
            },
            NodeType.QUESTION: {
                "name": "Ask Question",
                "icon": "❓",
                "color": "#8B5CF6",
                "properties": {
                    "text": "",
                    "variable": "",
                    "timeout": 10,
                    "retry_text": "I didn't catch that. Could you repeat?",
                    "max_retries": 2,
                },
                "outputs": ["answered", "timeout", "no_match"],
            },
            NodeType.CONDITION: {
                "name": "Condition",
                "icon": "🔀",
                "color": "#F59E0B",
                "properties": {
                    "variable": "",
                    "operator": "equals",
                    "value": "",
                },
                "outputs": ["yes", "no"],
            },
            NodeType.TRANSFER: {
                "name": "Transfer Call",
                "icon": "📞",
                "color": "#EF4444",
                "properties": {
                    "transfer_number": "",
                    "transfer_message": "Transferring your call now.",
                    "warm_transfer": False,
                },
                "outputs": ["success", "failed"],
            },
            NodeType.WEBHOOK: {
                "name": "Call Webhook",
                "icon": "🌐",
                "color": "#14B8A6",
                "properties": {
                    "url": "",
                    "method": "POST",
                    "headers": {},
                    "body": {},
                    "store_response_in": "",
                },
                "outputs": ["success", "error"],
            },
            NodeType.SET_VARIABLE: {
                "name": "Set Variable",
                "icon": "📝",
                "color": "#6366F1",
                "properties": {
                    "variable": "",
                    "value": "",
                    "type": "string",
                },
                "outputs": ["default"],
            },
            NodeType.WAIT: {
                "name": "Wait",
                "icon": "⏱️",
                "color": "#94A3B8",
                "properties": {
                    "duration_seconds": 1.0,
                },
                "outputs": ["default"],
            },
            NodeType.END: {
                "name": "End Call",
                "icon": "🔚",
                "color": "#DC2626",
                "properties": {
                    "goodbye_message": "Thank you for calling. Goodbye!",
                },
                "outputs": [],
            },
            NodeType.SUB_FLOW: {
                "name": "Sub-Flow",
                "icon": "📂",
                "color": "#EC4899",
                "properties": {
                    "flow_id": "",
                },
                "outputs": ["completed", "error"],
            },
        }
    
    async def create_flow(
        self,
        name: str,
        description: str = "",
        organization_id: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> ConversationFlow:
        """Create a new conversation flow."""
        flow_id = f"flow_{uuid.uuid4().hex}"
        
        flow = ConversationFlow(
            id=flow_id,
            name=name,
            description=description,
            organization_id=organization_id,
            created_by=created_by,
        )
        
        # Add default start node
        start_node = FlowNode(
            id=f"node_{uuid.uuid4().hex[:8]}",
            type=NodeType.START,
            name="Start",
            position=Position(x=250, y=50),
            color="#10B981",
            icon="▶️",
        )
        flow.nodes[start_node.id] = start_node
        flow.start_node_id = start_node.id
        
        self._flows[flow_id] = flow
        logger.info(f"Created flow: {flow_id}")
        return flow
    
    async def get_flow(self, flow_id: str) -> Optional[ConversationFlow]:
        """Get a flow by ID."""
        return self._flows.get(flow_id)
    
    async def update_flow(
        self,
        flow_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[ConversationFlow]:
        """Update flow metadata."""
        flow = self._flows.get(flow_id)
        if not flow:
            return None
        
        if name:
            flow.name = name
        if description is not None:
            flow.description = description
        
        flow.updated_at = datetime.now(timezone.utc)
        return flow
    
    async def delete_flow(self, flow_id: str) -> bool:
        """Delete a flow."""
        if flow_id in self._flows:
            del self._flows[flow_id]
            return True
        return False
    
    async def list_flows(
        self,
        organization_id: Optional[str] = None,
    ) -> List[ConversationFlow]:
        """List all flows."""
        flows = list(self._flows.values())
        
        if organization_id:
            flows = [f for f in flows if f.organization_id == organization_id]
        
        return flows
    
    async def add_node(
        self,
        flow_id: str,
        node_type: NodeType,
        position: Dict[str, float],
        properties: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None,
    ) -> Optional[FlowNode]:
        """Add a node to a flow."""
        flow = self._flows.get(flow_id)
        if not flow:
            return None
        
        template = self._node_templates.get(node_type, {})
        
        node = FlowNode(
            id=f"node_{uuid.uuid4().hex[:8]}",
            type=node_type,
            name=name or template.get("name", node_type.value),
            position=Position(x=position.get("x", 0), y=position.get("y", 0)),
            properties=properties or template.get("properties", {}).copy(),
            color=template.get("color", "#4F46E5"),
            icon=template.get("icon", ""),
        )
        
        flow.nodes[node.id] = node
        flow.updated_at = datetime.now(timezone.utc)
        
        return node
    
    async def update_node(
        self,
        flow_id: str,
        node_id: str,
        position: Optional[Dict[str, float]] = None,
        properties: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None,
    ) -> Optional[FlowNode]:
        """Update a node in a flow."""
        flow = self._flows.get(flow_id)
        if not flow or node_id not in flow.nodes:
            return None
        
        node = flow.nodes[node_id]
        
        if position:
            node.position = Position(x=position.get("x", 0), y=position.get("y", 0))
        
        if properties:
            node.properties.update(properties)
        
        if name:
            node.name = name
        
        flow.updated_at = datetime.now(timezone.utc)
        return node
    
    async def delete_node(self, flow_id: str, node_id: str) -> bool:
        """Delete a node from a flow."""
        flow = self._flows.get(flow_id)
        if not flow or node_id not in flow.nodes:
            return False
        
        # Remove node
        del flow.nodes[node_id]
        
        # Remove connections to/from this node
        flow.connections = [
            c for c in flow.connections
            if c.source_node != node_id and c.target_node != node_id
        ]
        
        # Clear start if it was deleted
        if flow.start_node_id == node_id:
            flow.start_node_id = None
        
        flow.updated_at = datetime.now(timezone.utc)
        return True
    
    async def connect_nodes(
        self,
        flow_id: str,
        source_id: str,
        target_id: str,
        source_port: str = "default",
        target_port: str = "input",
        label: str = "",
    ) -> Optional[Connection]:
        """Connect two nodes."""
        flow = self._flows.get(flow_id)
        if not flow:
            return None
        
        if source_id not in flow.nodes or target_id not in flow.nodes:
            return None
        
        conn = Connection(
            id=f"edge_{uuid.uuid4().hex[:8]}",
            source_node=source_id,
            source_port=source_port,
            target_node=target_id,
            target_port=target_port,
            label=label,
        )
        
        flow.connections.append(conn)
        flow.updated_at = datetime.now(timezone.utc)
        
        return conn
    
    async def disconnect_nodes(
        self,
        flow_id: str,
        connection_id: str,
    ) -> bool:
        """Remove a connection."""
        flow = self._flows.get(flow_id)
        if not flow:
            return False
        
        original_len = len(flow.connections)
        flow.connections = [c for c in flow.connections if c.id != connection_id]
        
        if len(flow.connections) < original_len:
            flow.updated_at = datetime.now(timezone.utc)
            return True
        
        return False
    
    async def validate_flow(self, flow_id: str) -> Dict[str, Any]:
        """Validate a flow for errors."""
        flow = self._flows.get(flow_id)
        if not flow:
            return {"valid": False, "errors": ["Flow not found"]}
        
        errors = []
        warnings = []
        
        # Check start node
        if not flow.start_node_id:
            errors.append("No start node defined")
        elif flow.start_node_id not in flow.nodes:
            errors.append("Start node not found in nodes")
        
        # Check for orphan nodes
        connected_nodes = set()
        for conn in flow.connections:
            connected_nodes.add(conn.source_node)
            connected_nodes.add(conn.target_node)
        
        if flow.start_node_id:
            connected_nodes.add(flow.start_node_id)
        
        for node_id in flow.nodes:
            if node_id not in connected_nodes:
                warnings.append(f"Node '{flow.nodes[node_id].name}' is not connected")
        
        # Check for cycles (simple check)
        # More complex cycle detection could be added
        
        # Check for dead ends (nodes with no outgoing connections)
        for node_id, node in flow.nodes.items():
            if node.type == NodeType.END:
                continue  # End nodes are supposed to have no connections
            
            has_outgoing = any(
                c.source_node == node_id for c in flow.connections
            )
            if not has_outgoing and node.type != NodeType.START:
                warnings.append(f"Node '{node.name}' has no outgoing connections")
        
        # Check required properties
        for node_id, node in flow.nodes.items():
            if node.type == NodeType.MESSAGE:
                if not node.properties.get("text"):
                    errors.append(f"Node '{node.name}' is missing message text")
            elif node.type == NodeType.QUESTION:
                if not node.properties.get("text"):
                    errors.append(f"Node '{node.name}' is missing question text")
                if not node.properties.get("variable"):
                    errors.append(f"Node '{node.name}' is missing variable name")
            elif node.type == NodeType.TRANSFER:
                if not node.properties.get("transfer_number"):
                    errors.append(f"Node '{node.name}' is missing transfer number")
            elif node.type == NodeType.WEBHOOK:
                if not node.properties.get("url"):
                    errors.append(f"Node '{node.name}' is missing webhook URL")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "node_count": len(flow.nodes),
            "connection_count": len(flow.connections),
        }
    
    async def publish_flow(self, flow_id: str) -> Dict[str, Any]:
        """Publish a flow (make it live)."""
        validation = await self.validate_flow(flow_id)
        if not validation["valid"]:
            return {
                "success": False,
                "errors": validation["errors"],
            }
        
        flow = self._flows.get(flow_id)
        if flow:
            flow.is_published = True
            flow.version += 1
            flow.updated_at = datetime.now(timezone.utc)
            
            return {
                "success": True,
                "version": flow.version,
            }
        
        return {"success": False, "errors": ["Flow not found"]}
    
    async def unpublish_flow(self, flow_id: str) -> bool:
        """Unpublish a flow."""
        flow = self._flows.get(flow_id)
        if flow:
            flow.is_published = False
            flow.updated_at = datetime.now(timezone.utc)
            return True
        return False
    
    async def duplicate_flow(
        self,
        flow_id: str,
        new_name: Optional[str] = None,
    ) -> Optional[ConversationFlow]:
        """Create a copy of a flow."""
        flow = self._flows.get(flow_id)
        if not flow:
            return None
        
        # Create new flow with copied data
        new_flow = ConversationFlow(
            id=f"flow_{uuid.uuid4().hex}",
            name=new_name or f"{flow.name} (Copy)",
            description=flow.description,
            organization_id=flow.organization_id,
        )
        
        # Map old IDs to new IDs
        id_map = {}
        
        # Copy nodes with new IDs
        for old_id, node in flow.nodes.items():
            new_id = f"node_{uuid.uuid4().hex[:8]}"
            id_map[old_id] = new_id
            
            new_node = FlowNode(
                id=new_id,
                type=node.type,
                name=node.name,
                position=Position(x=node.position.x, y=node.position.y),
                properties=node.properties.copy(),
                color=node.color,
                icon=node.icon,
            )
            new_flow.nodes[new_id] = new_node
        
        # Copy connections with new IDs
        for conn in flow.connections:
            new_conn = Connection(
                id=f"edge_{uuid.uuid4().hex[:8]}",
                source_node=id_map.get(conn.source_node, conn.source_node),
                source_port=conn.source_port,
                target_node=id_map.get(conn.target_node, conn.target_node),
                target_port=conn.target_port,
                label=conn.label,
            )
            new_flow.connections.append(new_conn)
        
        # Update start node ID
        if flow.start_node_id:
            new_flow.start_node_id = id_map.get(flow.start_node_id)
        
        # Copy variables
        new_flow.variables = flow.variables.copy()
        
        self._flows[new_flow.id] = new_flow
        return new_flow
    
    def get_node_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get all node type templates for the UI."""
        return {
            node_type.value: template
            for node_type, template in self._node_templates.items()
        }


class FlowExecutor:
    """
    Execute conversation flows at runtime.
    
    Processes nodes and manages flow state during calls.
    """
    
    def __init__(
        self,
        flow: ConversationFlow,
        webhook_handler: Optional[Callable[[str, str, Dict], Awaitable[Dict]]] = None,
    ):
        self.flow = flow
        self.webhook_handler = webhook_handler
        self.state = FlowExecutionState(
            flow_id=flow.id,
            current_node_id=flow.start_node_id or "",
            variables=flow.variables.copy(),
        )
    
    async def start(self) -> Optional[FlowNode]:
        """Start flow execution."""
        if not self.flow.start_node_id:
            return None
        
        self.state.current_node_id = self.flow.start_node_id
        return self.flow.nodes.get(self.flow.start_node_id)
    
    async def get_current_node(self) -> Optional[FlowNode]:
        """Get the current node."""
        return self.flow.nodes.get(self.state.current_node_id)
    
    async def advance(
        self,
        output_port: str = "default",
        user_input: Optional[str] = None,
    ) -> Optional[FlowNode]:
        """
        Advance to the next node.
        
        Args:
            output_port: Which output port to follow
            user_input: User's input (for questions/conditions)
        
        Returns:
            Next node or None if flow ended
        """
        current = self.state.current_node_id
        
        # Record history
        self.state.history.append(current)
        
        # Find connection from current node with matching port
        next_conn = None
        for conn in self.flow.connections:
            if conn.source_node == current and conn.source_port == output_port:
                next_conn = conn
                break
        
        if not next_conn:
            # Try default port
            for conn in self.flow.connections:
                if conn.source_node == current and conn.source_port == "default":
                    next_conn = conn
                    break
        
        if not next_conn:
            self.state.is_complete = True
            return None
        
        # Move to next node
        self.state.current_node_id = next_conn.target_node
        return self.flow.nodes.get(next_conn.target_node)
    
    async def set_variable(self, name: str, value: Any) -> None:
        """Set a variable value."""
        self.state.variables[name] = value
    
    def get_variable(self, name: str) -> Any:
        """Get a variable value."""
        return self.state.variables.get(name)
    
    async def evaluate_condition(
        self,
        node: FlowNode,
        user_input: Optional[str] = None,
    ) -> str:
        """
        Evaluate a condition node.
        
        Returns "yes" or "no" based on the condition.
        """
        props = node.properties
        variable = props.get("variable", "")
        operator = props.get("operator", "equals")
        value = props.get("value", "")
        
        # Get variable value
        var_value = self.state.variables.get(variable, user_input or "")
        
        # Evaluate
        result = False
        
        if operator == "equals":
            result = str(var_value).lower() == str(value).lower()
        elif operator == "not_equals":
            result = str(var_value).lower() != str(value).lower()
        elif operator == "contains":
            result = str(value).lower() in str(var_value).lower()
        elif operator == "not_contains":
            result = str(value).lower() not in str(var_value).lower()
        elif operator == "starts_with":
            result = str(var_value).lower().startswith(str(value).lower())
        elif operator == "ends_with":
            result = str(var_value).lower().endswith(str(value).lower())
        elif operator == "greater_than":
            try:
                result = float(var_value) > float(value)
            except ValueError:
                result = False
        elif operator == "less_than":
            try:
                result = float(var_value) < float(value)
            except ValueError:
                result = False
        elif operator == "is_empty":
            result = not var_value or str(var_value).strip() == ""
        elif operator == "is_not_empty":
            result = bool(var_value) and str(var_value).strip() != ""
        
        return "yes" if result else "no"


# Global designer instance
_global_designer: Optional[FlowDesigner] = None


def get_flow_designer() -> FlowDesigner:
    """Get or create global flow designer."""
    global _global_designer
    if _global_designer is None:
        _global_designer = FlowDesigner()
    return _global_designer
