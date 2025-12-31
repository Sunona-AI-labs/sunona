"""
Sunona Voice AI - Contextual Conversational Agent

An agent that maintains deep context awareness throughout conversations.
Remembers and references previous topics, adapts tone, and provides
highly personalized responses.
"""

import logging
from typing import Any, Dict, List, Optional

from sunona.agents.base_agent import (
    BaseAgent, AgentConfig, AgentResponse, AgentCapability, AgentState
)

logger = logging.getLogger(__name__)


class ContextualConversationalAgent(BaseAgent):
    """
    Agent with deep contextual understanding.
    
    Features:
    - Remembers all topics discussed
    - Tracks user preferences and sentiment
    - Adapts responses based on conversation flow
    - Maintains topic continuity
    - Detects conversation shifts
    
    Best for:
    - Customer support with history
    - Personal assistants
    - Long-form consultations
    - Relationship-building conversations
    
    Example:
        ```python
        agent = ContextualConversationalAgent(config)
        
        # First call
        response = await agent.process_message("I'm interested in your premium plan")
        # Later...
        response = await agent.process_message("What about the one we discussed earlier?")
        # Agent remembers "premium plan" and responds appropriately
        ```
    """
    
    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        llm: Optional[Any] = None,
    ):
        super().__init__(config, llm)
        
        # Context tracking
        self._topics: List[str] = []
        self._user_preferences: Dict[str, Any] = {}
        self._sentiment_history: List[str] = []
        self._key_facts: List[str] = []
        self._current_topic: Optional[str] = None
    
    @property
    def capabilities(self) -> List[AgentCapability]:
        return [AgentCapability.CONVERSATION, AgentCapability.KNOWLEDGE_BASE]
    
    async def process_message(self, message: str) -> AgentResponse:
        """Process message with full context awareness."""
        self._set_state(AgentState.LISTENING)
        
        # Add to history
        self.add_message("user", message)
        
        # Analyze message for context
        self._update_context(message)
        
        # Build context-aware prompt
        context_prompt = self._build_context_prompt()
        
        # Generate response
        self._set_state(AgentState.THINKING)
        
        messages = self.get_messages_for_llm()
        
        # Inject context
        if messages and messages[0]["role"] == "system":
            messages[0]["content"] = context_prompt + "\n\n" + messages[0]["content"]
        
        response_text = await self.generate_response(messages)
        
        # Track response topics
        self._extract_topics(response_text)
        
        # Add to history
        self.add_message("assistant", response_text)
        
        self._set_state(AgentState.SPEAKING)
        
        return AgentResponse(
            text=response_text,
            data={
                "current_topic": self._current_topic,
                "topics_discussed": self._topics,
                "key_facts": self._key_facts,
            }
        )
    
    def _update_context(self, message: str):
        """Update context from user message."""
        message_lower = message.lower()
        
        # Detect topic references
        if any(word in message_lower for word in ["earlier", "before", "discussed", "mentioned"]):
            # User is referencing previous context
            pass
        
        # Detect sentiment
        positive_words = ["great", "love", "excellent", "happy", "thanks"]
        negative_words = ["bad", "terrible", "frustrated", "angry", "disappointed"]
        
        if any(w in message_lower for w in positive_words):
            self._sentiment_history.append("positive")
        elif any(w in message_lower for w in negative_words):
            self._sentiment_history.append("negative")
        else:
            self._sentiment_history.append("neutral")
        
        # Extract key facts
        if "my name is" in message_lower:
            name = message_lower.split("my name is")[-1].strip().split()[0]
            self._key_facts.append(f"User's name: {name}")
            self._user_preferences["name"] = name
        
        if "i prefer" in message_lower or "i like" in message_lower:
            self._key_facts.append(f"Preference: {message}")
    
    def _build_context_prompt(self) -> str:
        """Build context-aware system prompt addition."""
        context_parts = []
        
        if self._topics:
            context_parts.append(f"Topics discussed: {', '.join(self._topics[-5:])}")
        
        if self._key_facts:
            context_parts.append(f"Key facts: {'; '.join(self._key_facts[-5:])}")
        
        if self._sentiment_history:
            recent_sentiment = self._sentiment_history[-3:]
            if recent_sentiment.count("negative") >= 2:
                context_parts.append("Note: User seems frustrated. Be extra empathetic.")
            elif recent_sentiment.count("positive") >= 2:
                context_parts.append("Note: User is in a positive mood. Match their energy.")
        
        if self._user_preferences.get("name"):
            context_parts.append(f"Address user as: {self._user_preferences['name']}")
        
        if context_parts:
            return "CONVERSATION CONTEXT:\n" + "\n".join(context_parts)
        
        return ""
    
    def _extract_topics(self, text: str):
        """Extract topics from response."""
        # Simple topic extraction based on nouns
        # In production, use NLP
        topic_keywords = [
            "pricing", "features", "support", "account", "billing",
            "product", "service", "plan", "subscription", "order",
        ]
        
        text_lower = text.lower()
        for keyword in topic_keywords:
            if keyword in text_lower and keyword not in self._topics:
                self._topics.append(keyword)
                self._current_topic = keyword
    
    def add_key_fact(self, fact: str):
        """Manually add a key fact to context."""
        if fact not in self._key_facts:
            self._key_facts.append(fact)
    
    def set_user_preference(self, key: str, value: Any):
        """Set a user preference."""
        self._user_preferences[key] = value
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of current context."""
        return {
            "topics": self._topics,
            "current_topic": self._current_topic,
            "key_facts": self._key_facts,
            "preferences": self._user_preferences,
            "sentiment_trend": self._sentiment_history[-5:] if self._sentiment_history else [],
            "turn_count": self.turn_count,
        }
