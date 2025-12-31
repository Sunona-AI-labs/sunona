"""
Sunona Voice AI - Graph-Based Conversational Agent

Combines the flexibility of conversational AI with structured graph flows.
Uses graph as guidance but allows natural conversation within nodes.
"""

import logging
from typing import Any, Dict, List, Optional

from sunona.agents.base_agent import (
    BaseAgent, AgentConfig, AgentResponse, AgentCapability, AgentState
)
from sunona.agents.graph_agent import ConversationGraph, GraphNode, NodeType

logger = logging.getLogger(__name__)


class GraphBasedConversationalAgent(BaseAgent):
    """
    Hybrid agent: Graph structure + Conversational AI.
    
    Unlike pure GraphAgent:
    - Uses LLM to handle conversations within a node
    - Falls back to graph transitions heuristically
    - More natural, less robotic
    - Still follows overall structure
    
    Features:
    - Guided flow with natural language
    - LLM enriches graph responses
    - Dynamic node transitions
    - Best of both worlds
    
    Best for:
    - Complex sales flows
    - Onboarding calls
    - Multi-step processes with variation
    - When scripted + AI hybrid needed
    
    Example:
        ```python
        graph = ConversationGraph()
        # Add nodes...
        
        agent = GraphBasedConversationalAgent(
            graph=graph,
            llm=my_llm,
        )
        
        # User says something off-script
        response = await agent.process_message("Actually, before pricing, what's your refund policy?")
        # Agent uses LLM to answer, then guides back to flow
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
        self._off_script_count = 0
        self._max_off_script = 3  # Max off-script turns before redirecting
    
    @property
    def capabilities(self) -> List[AgentCapability]:
        return [AgentCapability.CONVERSATION, AgentCapability.GRAPH_FLOW]
    
    async def start(self):
        """Start agent and initialize graph."""
        await super().start()
        self._current_node_id = self.graph.start_node
        
        if self._current_node_id:
            self._visited_nodes.append(self._current_node_id)
    
    async def process_message(self, message: str) -> AgentResponse:
        """Process with graph guidance + LLM flexibility."""
        self._set_state(AgentState.LISTENING)
        self.add_message("user", message)
        
        current_node = self.graph.get_node(self._current_node_id) if self._current_node_id else None
        
        # Try graph transition first
        if current_node:
            next_node = self.graph.get_next_node(
                self._current_node_id,
                message,
                {"visited": self._visited_nodes},
            )
            
            if next_node:
                # Clear transition found
                self._current_node_id = next_node.id
                self._visited_nodes.append(next_node.id)
                self._off_script_count = 0
                
                return await self._handle_node_with_llm(next_node, message)
        
        # No clear transition - user is off-script
        self._off_script_count += 1
        
        if self._off_script_count >= self._max_off_script:
            # Too many off-script turns, redirect
            redirect_text = await self._generate_redirect()
            self.add_message("assistant", redirect_text)
            self._off_script_count = 0
            
            return AgentResponse(
                text=redirect_text,
                data={"action": "redirect", "current_node": self._current_node_id},
            )
        
        # Use LLM to handle off-script question
        response = await self._handle_off_script(message, current_node)
        return response
    
    async def _handle_node_with_llm(
        self,
        node: GraphNode,
        user_message: str,
    ) -> AgentResponse:
        """Handle node using LLM to enhance the response."""
        
        if node.node_type == NodeType.TRANSFER:
            return await self.transfer("graph_transfer")
        
        if node.node_type == NodeType.END:
            await self.end("graph_completed")
            return AgentResponse(
                text=node.content or "Thank you! Goodbye.",
                action="end",
            )
        
        # Use LLM to enhance node content
        if self.llm:
            enhanced = await self._enhance_response(node.content, user_message)
        else:
            enhanced = node.content
        
        self.add_message("assistant", enhanced)
        
        return AgentResponse(
            text=enhanced,
            data={
                "node_id": node.id,
                "node_type": node.node_type.value,
                "enhanced": self.llm is not None,
            },
        )
    
    async def _enhance_response(
        self,
        base_response: str,
        user_message: str,
    ) -> str:
        """Use LLM to enhance a base response."""
        if not self.llm:
            return base_response
        
        prompt = f"""You are continuing a conversation. 
The user said: "{user_message}"
Your base response should convey: "{base_response}"

Respond naturally, incorporating the base message but making it conversational.
Keep it concise (1-2 sentences for phone call).
"""
        
        messages = [
            {"role": "system", "content": self.config.system_prompt},
            {"role": "user", "content": prompt},
        ]
        
        try:
            enhanced = await self.llm.generate(messages)
            return enhanced
        except Exception as e:
            logger.error(f"Enhancement error: {e}")
            return base_response
    
    async def _handle_off_script(
        self,
        message: str,
        current_node: Optional[GraphNode],
    ) -> AgentResponse:
        """Handle off-script questions with LLM."""
        if not self.llm:
            fallback = "I want to make sure I address your main question. Could you tell me more about what you're looking for?"
            self.add_message("assistant", fallback)
            return AgentResponse(text=fallback)
        
        # Build context-aware prompt
        context_prompt = ""
        if current_node:
            context_prompt = f"\nNote: We were discussing: {current_node.content}. Answer the user's question, then guide back if appropriate."
        
        messages = [
            {"role": "system", "content": self.config.system_prompt + context_prompt},
        ] + self.get_messages_for_llm()
        
        response = await self.llm.generate(messages)
        self.add_message("assistant", response)
        
        return AgentResponse(
            text=response,
            data={"off_script": True, "off_script_count": self._off_script_count},
        )
    
    async def _generate_redirect(self) -> str:
        """Generate a message to redirect conversation back to flow."""
        current_node = self.graph.get_node(self._current_node_id)
        
        if not current_node:
            return "Let me make sure I understand what you need. What can I help you with?"
        
        if self.llm:
            prompt = f"""The conversation has gone off-topic. 
We need to get back to: "{current_node.content}"
Generate a smooth redirect that acknowledges the user and guides them back.
Be natural, not robotic. 1-2 sentences.
"""
            try:
                return await self.llm.generate([{"role": "user", "content": prompt}])
            except Exception:
                pass
        
        return f"I appreciate that. To help you best, {current_node.content.lower()}"
    
    def force_transition(self, node_id: str) -> bool:
        """Force transition to a specific node."""
        if node_id in self.graph.nodes:
            self._current_node_id = node_id
            self._visited_nodes.append(node_id)
            self._off_script_count = 0
            return True
        return False
    
    def get_conversation_state(self) -> Dict[str, Any]:
        """Get current conversation state."""
        current_node = self.graph.get_node(self._current_node_id)
        
        return {
            "current_node_id": self._current_node_id,
            "current_node_content": current_node.content if current_node else None,
            "visited_nodes": self._visited_nodes,
            "off_script_count": self._off_script_count,
            "turn_count": self.turn_count,
        }
