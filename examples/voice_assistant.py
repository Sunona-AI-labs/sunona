"""
Sunona Voice AI - Voice Assistant Example

Demonstrates text-to-speech using:
- OpenRouter (Mistral 7B free) as primary LLM, Groq as fallback
- ElevenLabs (Bella voice) as primary TTS, Edge TTS as fallback

Usage:
    python examples/voice_assistant.py
"""

import os
import sys
import json
import asyncio
import tempfile

# Add parent directory to path for development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

import httpx
import re


def clean_llm_tokens(text: str) -> str:
    """Remove special tokens from LLM output."""
    if not text:
        return ""
    # Remove common special tokens
    patterns = [
        r'\s*<s>\s*',      # <s> with surrounding spaces
        r'\s*</s>\s*',     # </s> with surrounding spaces
        r'\s*<\|im_start\|>\s*',
        r'\s*<\|im_end\|>\s*',
        r'\s*\[INST\]\s*',
        r'\s*\[/INST\]\s*',
        r'\s*\[OUT\]\s*',
        r'\s*\[/OUT\]\s*',
    ]
    for pattern in patterns:
        text = re.sub(pattern, '', text)
    return text

# Try to import audio playback
try:
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    PYGAME_OK = True
except ImportError:
    PYGAME_OK = False
    print("Warning: pygame not available. Install with: pip install pygame")

# Try to import Edge TTS (free fallback)
try:
    import edge_tts
    EDGE_TTS_OK = True
except ImportError:
    EDGE_TTS_OK = False


class VoiceChat:
    """Voice chat with LLM and TTS (with fallbacks)."""
    
    def __init__(
        self,
        openrouter_key: str = None,
        groq_key: str = None,
        elevenlabs_key: str = None,
        model: str = "mistralai/mistral-7b-instruct:free",
        voice_id: str = "EXAVITQu4vr4xnSDxMaL",  # Bella
    ):
        self.openrouter_key = openrouter_key
        self.groq_key = groq_key
        self.elevenlabs_key = elevenlabs_key
        self.model = model
        self.voice_id = voice_id
        self.messages = []
        self.use_elevenlabs = bool(elevenlabs_key)
    
    def set_system_prompt(self, prompt: str):
        """Set the system prompt."""
        self.messages = [{"role": "system", "content": prompt}]
    
    def get_llm_response(self, user_message: str) -> str:
        """Get response from OpenRouter (free) or Groq (fallback)."""
        self.messages.append({"role": "user", "content": user_message})
        
        full_response = []
        print("💭 Sunona: ", end="", flush=True)
        
        # Try OpenRouter first (free)
        if self.openrouter_key:
            try:
                full_response = self._call_openrouter()
            except Exception:
                pass  # Silent fallback
        
        # Fallback to Groq
        if not full_response and self.groq_key:
            try:
                full_response = self._call_groq()
            except Exception:
                pass
        
        if not full_response:
            print("❌ No LLM response")
        
        print()  # Newline after response
        
        response_text = "".join(full_response)
        if response_text:
            self.messages.append({"role": "assistant", "content": response_text})
        return response_text
    
    def _call_openrouter(self) -> list:
        """Call OpenRouter API."""
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://sunona.ai",
            "X-Title": "Sunona AI",
        }
        
        body = {
            "model": self.model,
            "messages": self.messages,
            "max_tokens": 150,
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
                                # Clean special tokens using regex
                                content = clean_llm_tokens(content)
                                if content:
                                    print(content, end="", flush=True)
                                    full_response.append(content)
                        except json.JSONDecodeError:
                            continue
        
        return full_response
    
    def _call_groq(self) -> list:
        """Call Groq API."""
        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json",
        }
        
        body = {
            "model": "llama-3.1-8b-instant",
            "messages": self.messages,
            "max_tokens": 150,
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
    
    def speak(self, text: str):
        """Speak the text using TTS (ElevenLabs or Edge TTS fallback)."""
        if not PYGAME_OK:
            print("[Audio playback not available]")
            return
        
        if not text.strip():
            return
        
        try:
            print("🔊 Speaking...", end=" ", flush=True)
            audio_file = os.path.join(tempfile.gettempdir(), "sunona_voice.mp3")
            
            # Try ElevenLabs first
            if self.use_elevenlabs:
                try:
                    self._speak_elevenlabs(text, audio_file)
                except Exception:
                    self.use_elevenlabs = False  # Don't retry
                    if EDGE_TTS_OK:
                        self._speak_edge_tts(text, audio_file)
                    else:
                        print("❌ TTS failed")
                        return
            elif EDGE_TTS_OK:
                self._speak_edge_tts(text, audio_file)
            else:
                print("❌ No TTS available")
                return
            
            # Play audio
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                pygame.time.wait(50)
            
            pygame.mixer.music.unload()
            
            try:
                os.remove(audio_file)
            except:
                pass
            
            print("Done")
        except Exception as e:
            print(f"❌ Voice error: {e}")
    
    def _speak_elevenlabs(self, text: str, audio_file: str):
        """Synthesize speech using ElevenLabs."""
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        
        headers = {
            "xi-api-key": self.elevenlabs_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }
        
        body = {
            "text": text,
            "model_id": "eleven_turbo_v2_5",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
            }
        }
        
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, headers=headers, json=body)
            response.raise_for_status()
            
            with open(audio_file, "wb") as f:
                f.write(response.content)
    
    def _speak_edge_tts(self, text: str, audio_file: str):
        """Synthesize speech using Edge TTS (free)."""
        loop = asyncio.new_event_loop()
        loop.run_until_complete(
            edge_tts.Communicate(text, "en-US-JennyNeural").save(audio_file)
        )
        loop.close()
    
    def chat(self, user_message: str, speak_response: bool = True):
        """Chat with voice output."""
        response = self.get_llm_response(user_message)
        
        if speak_response and response:
            self.speak(response)
        
        return response


def main():
    """Run a voice assistant."""
    print()
    print("=" * 50)
    print("  🎙️ Sunona Voice AI - Voice Assistant")
    print("=" * 50)
    print()
    
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    
    # Need at least one LLM provider
    if not openrouter_key and not groq_key:
        print("❌ Set OPENROUTER_API_KEY or GROQ_API_KEY in .env")
        sys.exit(1)
    
    # Show which providers are being used
    if openrouter_key:
        print("LLM: OpenRouter (mistral-7b) 🆓 free")
    if groq_key:
        print("LLM: Groq (llama-3.1-8b) 🔄 fallback" if openrouter_key else "LLM: Groq (llama-3.1-8b)")
    
    if elevenlabs_key:
        print("TTS: ElevenLabs (Bella) 🎙️ premium → Edge TTS 🔄 fallback")
    elif EDGE_TTS_OK:
        print("TTS: Edge TTS (Jenny) 🆓 free")
    else:
        print("⚠️ No TTS available")
    
    print()
    print("Type 'quit' to stop, 'mute' to toggle voice.")
    print("-" * 50)
    
    # Create chat instance
    chat = VoiceChat(
        openrouter_key=openrouter_key,
        groq_key=groq_key,
        elevenlabs_key=elevenlabs_key
    )
    
    chat.set_system_prompt("""You are Sunona, a friendly AI voice assistant.
Keep responses SHORT (1-2 sentences) for natural speech.
Be warm and conversational.""")
    
    # Welcome message
    welcome = "Hello! I'm Sunona. How can I help you today?"
    print(f"\n💭 Sunona: {welcome}\n")
    
    speak = PYGAME_OK and (elevenlabs_key or EDGE_TTS_OK)
    if speak:
        chat.speak(welcome)
    
    try:
        while True:
            try:
                user_input = input("\nYou: ").strip()
            except EOFError:
                break
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q', 'bye', 'goodbye']:
                print("\n💭 Sunona: Goodbye! 👋")
                if speak:
                    chat.speak("Goodbye!")
                break
            
            if user_input.lower() == 'mute':
                speak = not speak
                status = "ON 🔊" if speak else "OFF 🔇"
                print(f"[Voice: {status}]")
                continue
            
            chat.chat(user_input, speak_response=speak)
    
    except KeyboardInterrupt:
        print("\n\n💭 Sunona: Goodbye! 👋")
    
    print("\n✅ Session ended.")


if __name__ == "__main__":
    main()
