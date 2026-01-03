"""
Unit tests for Agents.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from sunona.agents.base_agent import BaseAgent, AgentConfig, AgentResponse, AgentState
from sunona.agents.contextual_conversational_agent import ContextualConversationalAgent

class ConcreteAgent(BaseAgent):
    """Concrete implementation for testing BaseAgent."""
    async def process_message(self, message: str) -> AgentResponse:
        response_text = await self.generate_response([{"role": "user", "content": message}])
        return AgentResponse(text=response_text)

@pytest.mark.asyncio
async def test_base_agent_initialization():
    """Test standard initialization and state."""
    config = AgentConfig(name="Test Bot", system_prompt="System Prompt")
    agent = ConcreteAgent(config=config)
    
    assert agent.config.name == "Test Bot"
    assert agent.state == AgentState.IDLE
    assert len(agent.conversation_history) == 1
    assert agent.conversation_history[0].content == "System Prompt"

@pytest.mark.asyncio
async def test_base_agent_message_history():
    """Test adding and retrieving messages."""
    agent = ConcreteAgent()
    agent.add_message("user", "Hello")
    agent.add_message("assistant", "Hi there")
    
    assert agent.turn_count == 1
    assert len(agent.conversation_history) == 3 # 1 system + 2 new
    
    llm_msgs = agent.get_messages_for_llm()
    assert llm_msgs[-2]["role"] == "user"
    assert llm_msgs[-1]["role"] == "assistant"

@pytest.mark.asyncio
async def test_base_agent_generate_response_mock():
    """Test generating response with a mock LLM."""
    mock_llm = AsyncMock()
    mock_llm.generate.return_value = "Mocked Response"
    
    agent = ConcreteAgent(llm=mock_llm)
    response = await agent.generate_response([{"role": "user", "content": "test"}])
    
    assert response == "Mocked Response"
    mock_llm.generate.assert_called_once()
    assert agent.state == AgentState.IDLE

@pytest.mark.asyncio
async def test_contextual_agent_topic_tracking():
    """Test ContextualConversationalAgent topic extraction and facts."""
    mock_llm = AsyncMock()
    mock_llm.generate.return_value = "I can help with our premium pricing plan."
    
    agent = ContextualConversationalAgent(llm=mock_llm)
    response = await agent.process_message("Tell me about price.")
    
    assert "pricing" in agent._topics
    assert "plan" in agent._topics
    assert response.data["current_topic"] == "plan"

@pytest.mark.asyncio
async def test_contextual_agent_fact_extraction():
    """Test ContextualConversationalAgent extracting name and facts."""
    agent = ContextualConversationalAgent()
    agent._update_context("My name is Alice and I prefer dark mode.")
    
    assert any("User's name: alice" in fact for fact in agent._key_facts)
    assert any("Preference: My name is Alice and I prefer dark mode." in fact for fact in agent._key_facts)
    assert agent._user_preferences["name"] == "alice"

@pytest.mark.asyncio
async def test_contextual_agent_sentiment_tracking():
    """Test ContextualConversationalAgent sentiment detection."""
    agent = ContextualConversationalAgent()
    
    agent._update_context("This is great!")
    assert agent._sentiment_history[-1] == "positive"
    
    agent._update_context("I am very angry and disappointed.")
    assert agent._sentiment_history[-1] == "negative"
    
    agent._update_context("It is okay.")
    assert agent._sentiment_history[-1] == "neutral"
