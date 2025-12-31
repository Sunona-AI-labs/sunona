"""
Sunona Voice AI - Summarization Agent

Agent specialized in summarizing conversations, documents, and data.
Provides concise summaries at any point in the conversation.
"""

import logging
from typing import Any, Dict, List, Optional

from sunona.agents.base_agent import (
    BaseAgent, AgentConfig, AgentResponse, AgentCapability, AgentState, ConversationTurn
)

logger = logging.getLogger(__name__)


class SummarizationAgent(BaseAgent):
    """
    Agent that provides summaries of conversations and content.
    
    Features:
    - Real-time conversation summarization
    - Key points extraction
    - Action items identification
    - Multi-language summary support
    - Different summary styles (brief, detailed, bullets)
    
    Best for:
    - Call wrap-ups
    - Meeting summaries
    - Document summarization
    - Generating call notes
    
    Example:
        ```python
        agent = SummarizationAgent()
        
        # Have a conversation...
        await agent.process_message("I need to book a flight to NYC next Tuesday")
        await agent.process_message("Sure, and back on Friday")
        await agent.process_message("I prefer afternoon flights")
        
        # Get summary
        summary = await agent.generate_summary()
        # "Customer needs a round-trip flight to NYC, departing Tuesday afternoon, returning Friday."
        
        # Get action items
        actions = await agent.extract_action_items()
        # ["Book flight to NYC for Tuesday afternoon", "Book return flight for Friday"]
        ```
    """
    
    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        llm: Optional[Any] = None,
    ):
        super().__init__(config, llm)
        
        # Summary settings
        self.summary_style = "concise"  # concise, detailed, bullets
        self.max_summary_length = 200  # words
        
        # Tracking
        self._key_points: List[str] = []
        self._action_items: List[str] = []
        self._decisions: List[str] = []
    
    @property
    def capabilities(self) -> List[AgentCapability]:
        return [AgentCapability.SUMMARIZATION, AgentCapability.CONVERSATION]
    
    async def process_message(self, message: str) -> AgentResponse:
        """Process message and track for summarization."""
        self._set_state(AgentState.LISTENING)
        self.add_message("user", message)
        
        # Extract key points from message
        self._extract_key_info(message, role="user")
        
        # Generate response
        self._set_state(AgentState.THINKING)
        response = await self.generate_response()
        
        # Track response key points too
        self._extract_key_info(response, role="assistant")
        
        self.add_message("assistant", response)
        self._set_state(AgentState.SPEAKING)
        
        return AgentResponse(
            text=response,
            data={
                "key_points_count": len(self._key_points),
                "action_items_count": len(self._action_items),
            },
        )
    
    def _extract_key_info(self, text: str, role: str = "user"):
        """Extract key information from text."""
        text_lower = text.lower()
        
        # Look for action items
        action_patterns = [
            "i need to", "please", "could you", "i want to",
            "i'd like", "we should", "let's", "make sure to",
        ]
        for pattern in action_patterns:
            if pattern in text_lower:
                # Extract the action
                idx = text_lower.find(pattern)
                action = text[idx:idx+100].split(".")[0]
                if action and action not in self._action_items:
                    self._action_items.append(action.strip())
        
        # Look for decisions
        decision_patterns = [
            "i'll go with", "let's do", "i choose", "i prefer",
            "we decided", "agreed", "confirmed",
        ]
        for pattern in decision_patterns:
            if pattern in text_lower:
                idx = text_lower.find(pattern)
                decision = text[idx:idx+100].split(".")[0]
                if decision and decision not in self._decisions:
                    self._decisions.append(decision.strip())
        
        # Extract key facts (names, dates, numbers)
        if any(word in text_lower for word in ["name is", "called", "this is"]):
            self._key_points.append(f"Name mentioned: {text[:50]}")
        
        import re
        dates = re.findall(r'\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|\d{1,2}[/-]\d{1,2})\b', text_lower)
        if dates:
            self._key_points.append(f"Date/time: {', '.join(dates)}")
    
    async def generate_summary(
        self,
        style: Optional[str] = None,
        max_length: Optional[int] = None,
    ) -> str:
        """
        Generate summary of the conversation.
        
        Args:
            style: concise, detailed, or bullets
            max_length: Maximum words
            
        Returns:
            Summary text
        """
        style = style or self.summary_style
        max_len = max_length or self.max_summary_length
        
        if not self.llm:
            return self._generate_simple_summary()
        
        conversation = self._get_conversation_text()
        
        style_instructions = {
            "concise": f"Summarize in {max_len} words or less. Be direct and factual.",
            "detailed": f"Provide a comprehensive summary covering all topics discussed.",
            "bullets": "Summarize as bullet points, one per topic.",
        }
        
        prompt = f"""Summarize this conversation:

{conversation}

Instructions: {style_instructions.get(style, style_instructions['concise'])}

KEY POINTS TO INCLUDE:
- Main topics discussed
- Decisions made
- Action items identified
- Next steps (if any)
"""
        
        try:
            summary = await self.llm.generate([{"role": "user", "content": prompt}])
            return summary
        except Exception as e:
            logger.error(f"Summary generation error: {e}")
            return self._generate_simple_summary()
    
    def _generate_simple_summary(self) -> str:
        """Generate a simple summary without LLM."""
        parts = []
        
        if self._key_points:
            parts.append("Key points: " + "; ".join(self._key_points[:5]))
        
        if self._action_items:
            parts.append("Action items: " + "; ".join(self._action_items[:5]))
        
        if self._decisions:
            parts.append("Decisions: " + "; ".join(self._decisions[:3]))
        
        if parts:
            return "\n".join(parts)
        
        return f"Conversation with {self.turn_count} exchanges."
    
    def _get_conversation_text(self) -> str:
        """Get conversation as text."""
        lines = []
        for turn in self.conversation_history:
            if turn.role != "system":
                lines.append(f"{turn.role.upper()}: {turn.content}")
        return "\n".join(lines)
    
    async def extract_action_items(self) -> List[str]:
        """Extract action items from conversation."""
        if not self.llm:
            return self._action_items
        
        conversation = self._get_conversation_text()
        
        prompt = f"""Extract action items from this conversation.
Return as a numbered list.

{conversation}

Action items:"""
        
        try:
            response = await self.llm.generate([{"role": "user", "content": prompt}])
            # Parse numbered list
            items = []
            for line in response.split("\n"):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith("-")):
                    # Remove number/bullet
                    item = line.lstrip("0123456789.-) ")
                    if item:
                        items.append(item)
            return items or self._action_items
        except Exception as e:
            logger.error(f"Action extraction error: {e}")
            return self._action_items
    
    async def extract_key_decisions(self) -> List[str]:
        """Extract key decisions from conversation."""
        if not self.llm:
            return self._decisions
        
        conversation = self._get_conversation_text()
        
        prompt = f"""Extract any decisions or agreements from this conversation.
Return as a numbered list.

{conversation}

Decisions made:"""
        
        try:
            response = await self.llm.generate([{"role": "user", "content": prompt}])
            # Parse response
            items = []
            for line in response.split("\n"):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith("-")):
                    item = line.lstrip("0123456789.-) ")
                    if item:
                        items.append(item)
            return items or self._decisions
        except Exception as e:
            logger.error(f"Decision extraction error: {e}")
            return self._decisions
    
    async def generate_call_notes(self) -> Dict[str, Any]:
        """Generate comprehensive call notes."""
        summary = await self.generate_summary(style="detailed")
        action_items = await self.extract_action_items()
        decisions = await self.extract_key_decisions()
        
        return {
            "summary": summary,
            "action_items": action_items,
            "decisions": decisions,
            "key_points": self._key_points,
            "duration_turns": self.turn_count,
            "generated_at": str(self.conversation_history[-1].timestamp if self.conversation_history else None),
        }
    
    def get_interim_summary(self) -> str:
        """Get a quick interim summary (no LLM)."""
        if not self.conversation_history:
            return "No conversation yet."
        
        recent = [t for t in self.conversation_history[-6:] if t.role != "system"]
        
        summary_parts = []
        if self._key_points:
            summary_parts.append(f"Topics: {', '.join(self._key_points[:3])}")
        
        summary_parts.append(f"Turns: {self.turn_count}")
        
        if self._action_items:
            summary_parts.append(f"Actions: {len(self._action_items)}")
        
        return " | ".join(summary_parts)
    
    def clear_tracking(self):
        """Clear tracked key points and action items."""
        self._key_points = []
        self._action_items = []
        self._decisions = []
