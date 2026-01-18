"""
Text-to-Text Demo Backend

Handles LLM conversation with proper error handling and streaming support.
"""

import os
import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple, AsyncGenerator

logger = logging.getLogger(__name__)


class TextToTextDemo:
    """
    Text-to-Text conversation handler.
    
    Features:
    - Multiple LLM provider support
    - Conversation history management
    - Streaming responses
    - Error handling with specific API identification
    """
    
    # Provider to model mapping
    PROVIDER_MODELS = {
        "Gemini": "gemini/gemini-1.5-flash",
        "OpenAI GPT": "gpt-4o-mini",
        "Groq": "groq/llama-3.1-70b-versatile",
        "Anthropic Claude": "claude-3-5-sonnet-20241022",
    }
    
    def __init__(
        self,
        system_prompt: str,
        provider: str = "Gemini",
        api_key: Optional[str] = None,
    ):
        """
        Initialize the Text-to-Text demo.
        
        Args:
            system_prompt: The system prompt for the AI
            provider: LLM provider name
            api_key: API key (falls back to environment variable)
        """
        self.system_prompt = system_prompt
        self.provider = provider
        self.api_key = api_key or self._get_default_key(provider)
        self.model = self.PROVIDER_MODELS.get(provider, "gemini/gemini-1.5-flash")
        self.conversation_history: List[Dict[str, str]] = []
    
    def _get_default_key(self, provider: str) -> Optional[str]:
        """Get default API key from environment."""
        key_mapping = {
            "Gemini": "GOOGLE_API_KEY",
            "OpenAI GPT": "OPENAI_API_KEY",
            "Groq": "GROQ_API_KEY",
            "Anthropic Claude": "ANTHROPIC_API_KEY",
        }
        env_var = key_mapping.get(provider, "GOOGLE_API_KEY")
        return os.getenv(env_var)
    
    def reset_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def _build_messages(self, user_message: str) -> List[Dict[str, str]]:
        """Build messages list for LLM API."""
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": user_message})
        return messages
    
    async def get_response(
        self,
        user_message: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
    ) -> Tuple[str, Optional[str]]:
        """
        Get a response from the LLM.
        
        Args:
            user_message: The user's message
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            
        Returns:
            Tuple of (response_text, error_message)
            error_message is None if successful
        """
        if not self.api_key:
            return "", f"🧠 LLM: No API key configured for {self.provider}. Add your key."
        
        try:
            from litellm import acompletion
            
            messages = self._build_messages(user_message)
            
            response = await acompletion(
                model=self.model,
                messages=messages,
                api_key=self.api_key,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            
            assistant_message = response.choices[0].message.content
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message, None
            
        except Exception as e:
            error = self._parse_error(e)
            logger.error(f"LLM error: {e}")
            return "", error
    
    async def get_response_stream(
        self,
        user_message: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
    ) -> AsyncGenerator[Tuple[str, Optional[str]], None]:
        """
        Get a streaming response from the LLM.
        
        Yields:
            Tuple of (partial_response, error_message)
        """
        if not self.api_key:
            yield "", f"🧠 LLM: No API key configured for {self.provider}. Add your key."
            return
        
        try:
            from litellm import acompletion
            
            messages = self._build_messages(user_message)
            
            response = await acompletion(
                model=self.model,
                messages=messages,
                api_key=self.api_key,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
            )
            
            full_response = ""
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield full_response, None
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            error = self._parse_error(e)
            logger.error(f"LLM streaming error: {e}")
            yield "", error
    
    def _parse_error(self, e: Exception) -> str:
        """Parse exception and return user-friendly error message."""
        error_msg = str(e).lower()
        
        if "rate limit" in error_msg or "429" in error_msg:
            return f"🧠 LLM: Rate limit exceeded for {self.provider}. Add your API key."
        elif "quota" in error_msg or "credit" in error_msg or "exceeded" in error_msg:
            return f"🧠 LLM: Credits exhausted for {self.provider}. Add your API key."
        elif "invalid" in error_msg or "401" in error_msg or "403" in error_msg:
            return f"🧠 LLM: Invalid API key for {self.provider}. Check your credentials."
        elif "timeout" in error_msg:
            return f"🧠 LLM: Request timed out. Try again."
        else:
            return f"🧠 LLM Error: {str(e)[:100]}"
    
    def get_conversation_for_display(self) -> List[Dict[str, str]]:
        """Get conversation history formatted for Gradio chatbot."""
        return self.conversation_history.copy()


# Convenience function for simple usage
async def chat(
    message: str,
    history: List[Dict[str, str]],
    system_prompt: str,
    provider: str = "Gemini",
    api_key: Optional[str] = None,
) -> Tuple[str, Optional[str]]:
    """
    Simple chat function.
    
    Args:
        message: User message
        history: Conversation history
        system_prompt: System prompt
        provider: LLM provider
        api_key: API key
        
    Returns:
        Tuple of (response, error)
    """
    demo = TextToTextDemo(system_prompt, provider, api_key)
    demo.conversation_history = history.copy() if history else []
    return await demo.get_response(message)
