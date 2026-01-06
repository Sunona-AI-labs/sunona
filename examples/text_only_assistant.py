"""
Sunona Voice AI - Text-Only Assistant Example

Demonstrates a text-only pipeline using:
- OpenRouter (Mistral 7B free) as primary LLM
- Groq (Llama 3.1 8B) as fallback LLM
- Simple synchronous HTTP calls for reliability

Usage:
    python examples/text_only_assistant.py
"""

import os
import sys
import json

# Add parent directory to path for development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

import httpx
import re


def clean_llm_tokens(text: str) -> str:
    """Remove special tokens and artifacts from LLM output, fix spacing issues."""
    if not text:
        return ""
    
    # Remove special tokens (handle both with and without angle brackets)
    patterns = [
        r'^\s*<s>\s*',      # Start-of-sequence token at beginning
        r'\s*</s>\s*$',     # End-of-sequence token at end
        r'<s>',             # Any remaining <s> tokens
        r'</s>',            # Any remaining </s> tokens
        r'<\|im_start\|>',
        r'<\|im_end\|>',
        r'\[INST\]',
        r'\[/INST\]',
        r'\[OUT\]',
        r'\[/OUT\]',
        r'<\|assistant\|>',
        r'<\|user\|>',
        r'<\|system\|>',
        r'###\s*Example\s*\d*',  # Remove "### Example" artifacts
        r'###\s*\w+\s*\d*$',     # Remove trailing markdown headers
    ]
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Fix common spacing issues (word boundaries without spaces)
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    text = re.sub(r'([a-z][.!?])([A-Z])', r'\1 \2', text)
    text = re.sub(r'([.!?,;:])([A-Za-z])', r'\1 \2', text)
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


class SimpleChat:
    """Simple synchronous chat with OpenRouter and Groq fallback."""
    
    def __init__(
        self, 
        openrouter_key: str = None, 
        groq_key: str = None,
        model: str = "mistralai/mistral-7b-instruct:free"
    ):
        self.openrouter_key = openrouter_key
        self.groq_key = groq_key
        self.model = model
        self.messages = []
    
    def set_system_prompt(self, prompt: str):
        """Set the system prompt."""
        self.messages = [{"role": "system", "content": prompt}]
    
    def chat(self, user_message: str) -> str:
        """Send a message and get a streaming response."""
        self.messages.append({"role": "user", "content": user_message})
        
        full_response = []
        
        # Try OpenRouter first (free)
        if self.openrouter_key:
            try:
                full_response = self._call_openrouter(self.messages)
            except Exception:
                pass  # Silent fallback
        
        # Fallback to Groq
        if not full_response and self.groq_key:
            try:
                full_response = self._call_groq(self.messages)
            except Exception as e:
                print(f"\n❌ Error: {e}")
        
        if not full_response:
            print("\n❌ No LLM response available")
            return ""
        
        response_text = "".join(full_response)
        # Clean the final response (fixes spacing and removes artifacts)
        response_text = clean_llm_tokens(response_text)
        print(response_text, end="", flush=True)  # Print cleaned response
        self.messages.append({"role": "assistant", "content": response_text})
        return response_text
    
    def _call_openrouter(self, messages: list) -> list:
        """Call OpenRouter API with streaming."""
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://sunona.ai",
            "X-Title": "Sunona AI",
        }
        
        body = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 256,
            "temperature": 0.5,
            "stream": True,
        }
        
        full_response = []
        
        with httpx.Client(timeout=30.0) as client:
            with client.stream("POST", "https://openrouter.ai/api/v1/chat/completions", 
                             headers=headers, json=body) as response:
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if not line or line.startswith(":"):
                        continue
                    
                    if line.startswith("data: "):
                        data_str = line[6:]
                        
                        if data_str.strip() == "[DONE]":
                            break
                        
                        try:
                            data = json.loads(data_str)
                            content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            
                            if content:
                                # Don't clean individual tokens - preserve spaces
                                full_response.append(content)
                        except json.JSONDecodeError:
                            continue
        
        return full_response
    
    def _call_groq(self, messages: list) -> list:
        """Call Groq API with streaming."""
        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json",
        }
        
        body = {
            "model": "llama-3.1-8b-instant",
            "messages": messages,
            "max_tokens": 256,
            "temperature": 0.5,
            "stream": True,
        }
        
        full_response = []
        
        with httpx.Client(timeout=15.0) as client:
            with client.stream("POST", "https://api.groq.com/openai/v1/chat/completions", 
                             headers=headers, json=body) as response:
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if not line or line.startswith(":"):
                        continue
                    
                    if line.startswith("data: "):
                        data_str = line[6:]
                        
                        if data_str.strip() == "[DONE]":
                            break
                        
                        try:
                            data = json.loads(data_str)
                            content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            
                            if content:
                                print(content, end="", flush=True)
                                full_response.append(content)
                        except json.JSONDecodeError:
                            continue
        
        return full_response


def main():
    """Run a text-only assistant."""
    print()
    print("=" * 50)
    print("  🤖 Sunona Voice AI - Text-Only Assistant")
    print("=" * 50)
    print()
    
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    
    # Need at least one LLM provider
    if not openrouter_key and not groq_key:
        print("❌ ERROR: Set OPENROUTER_API_KEY or GROQ_API_KEY in .env")
        print()
        print("Get your free API key at:")
        print("  - https://openrouter.ai/ (free Mistral 7B)")
        print("  - https://console.groq.com/ (fast Llama 3.1)")
        sys.exit(1)
    
    # Show which LLM is being used
    if openrouter_key:
        print("LLM: OpenRouter (mistral-7b) 🆓 free")
    if groq_key:
        print("LLM: Groq (llama-3.1-8b) 🔄 fallback" if openrouter_key else "LLM: Groq (llama-3.1-8b)")
    
    print()
    print("Type 'quit' or 'exit' to stop.")
    print("-" * 50)
    
    # Create chat instance
    chat = SimpleChat(openrouter_key=openrouter_key, groq_key=groq_key)
    
    # Set system prompt
    chat.set_system_prompt("""You are Sunona, a friendly and helpful AI assistant. 
Be conversational, helpful, and concise in your responses.
Keep responses SHORT (2-3 sentences) for efficient text conversation.""")
    
    # Display welcome message
    print("\n💭 Sunona: Hello! I'm Sunona, your AI assistant. How can I help you today?\n")
    
    try:
        while True:
            # Get user input
            try:
                user_input = input("You: ").strip()
            except EOFError:
                break
            
            if not user_input:
                continue
            
            # Exit words
            if user_input.lower() in ['quit', 'exit', 'q', 'bye', 'goodbye']:
                print("\n💭 Sunona: Goodbye! Have a great day! 👋\n")
                break
            
            # Get and display streaming response
            print("\n💭 Sunona: ", end="", flush=True)
            chat.chat(user_input)
            print("\n")
    
    except KeyboardInterrupt:
        print("\n\n💭 Sunona: Goodbye! 👋")
    
    print("✅ Session ended.")


if __name__ == "__main__":
    main()
