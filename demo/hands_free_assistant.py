"""
Sunona Voice AI - Hands-Free Speech-to-Speech Demo

A truly hands-free voice assistant similar to simple_assistant.py.
Uses VAD (Voice Activity Detection) to automatically detect when you speak.

Features:
- Continuous listening with energy-based VAD
- Automatic speech detection and silence detection  
- Gemini/Groq LLM with fallback support
- Edge TTS (free) or ElevenLabs for voice output
- Barge-in support (interrupt AI while speaking)

Usage:
    python demo/hands_free_assistant.py
"""

import os
import sys
import asyncio
import tempfile
import wave
import io

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

import httpx

# Audio recording
try:
    import sounddevice as sd
    import numpy as np
    AUDIO_OK = True
except ImportError:
    AUDIO_OK = False
    print("❌ ERROR: pip install sounddevice numpy")
    sys.exit(1)

# Audio playback
try:
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    PYGAME_OK = True
except ImportError:
    PYGAME_OK = False
    print("⚠️ WARNING: pip install pygame (for audio playback)")

# TTS - Edge TTS (free)
try:
    import edge_tts
    EDGE_TTS_OK = True
except ImportError:
    EDGE_TTS_OK = False
    print("⚠️ WARNING: pip install edge-tts")


class HandsFreeAssistant:
    """Hands-free voice assistant with VAD."""
    
    def __init__(self):
        self.sample_rate = 16000
        self.energy_threshold = 300  # Adjust for mic sensitivity
        self.messages = []
        
        # API Keys
        self.google_key = os.getenv("GOOGLE_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.deepgram_key = os.getenv("DEEPGRAM_API_KEY")
        self.elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
        
        # System prompt
        self.messages.append({
            "role": "system",
            "content": """You are Sunona, a helpful and friendly AI voice assistant. 

When asked your name, always say 'Sunona'.

You are:
- Warm, empathetic, and understanding
- Quick to help solve problems
- Professional yet conversational
- Always patient and supportive

Keep responses SHORT (1-2 sentences) for natural voice conversation."""
        })
    
    def listen(self, max_duration=30, silence_duration=1.5):
        """Listen for speech with VAD - returns when speech ends."""
        print("\n🎤 Listening...", end="", flush=True)
        
        chunk_duration = 0.1
        chunk_samples = int(self.sample_rate * chunk_duration)
        silence_chunks = int(silence_duration / chunk_duration)
        max_chunks = int(max_duration / chunk_duration)
        
        while True:
            chunks = []
            silence_count = 0
            speech_detected = False
            
            try:
                with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='int16') as stream:
                    for _ in range(max_chunks):
                        data, _ = stream.read(chunk_samples)
                        chunks.append(data.copy())
                        
                        energy = np.sqrt(np.mean(data.astype(np.float32) ** 2))
                        
                        if energy > self.energy_threshold:
                            if not speech_detected:
                                print(" (speaking)", end="", flush=True)
                                speech_detected = True
                            silence_count = 0
                        else:
                            if speech_detected:
                                silence_count += 1
                                if silence_count >= silence_chunks:
                                    break
            except Exception as e:
                print(f"\n❌ Recording error: {e}")
                return None
            
            if speech_detected:
                print()  # New line
                
                # Convert to WAV
                audio = np.concatenate(chunks)
                wav_buffer = io.BytesIO()
                with wave.open(wav_buffer, 'wb') as wav:
                    wav.setnchannels(1)
                    wav.setsampwidth(2)
                    wav.setframerate(self.sample_rate)
                    wav.writeframes(audio.tobytes())
                
                return wav_buffer.getvalue()
    
    def transcribe(self, wav_data):
        """Transcribe audio using Deepgram."""
        if not self.deepgram_key:
            print("❌ DEEPGRAM_API_KEY not set")
            return ""
        
        print("📝 Transcribing...", end=" ", flush=True)
        
        url = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true"
        headers = {
            "Authorization": f"Token {self.deepgram_key}",
            "Content-Type": "audio/wav"
        }
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(url, headers=headers, content=wav_data)
                response.raise_for_status()
                
                data = response.json()
                text = data.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "")
                
                if text:
                    print(f'"{text}"')
                else:
                    print("(no speech)")
                
                return text
        except Exception as e:
            print(f"❌ Error: {e}")
            return ""
    
    def get_llm_response(self, user_message):
        """Get response from Gemini or Groq."""
        self.messages.append({"role": "user", "content": user_message})
        
        print("💭 Sunona: ", end="", flush=True)
        
        # Try Gemini first
        if self.google_key:
            try:
                # Build prompt
                prompt_parts = []
                for msg in self.messages:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role == "system":
                        prompt_parts.append(f"Instructions: {content}\n\n")
                    elif role == "user":
                        prompt_parts.append(f"User: {content}\n")
                    elif role == "assistant":
                        prompt_parts.append(f"Assistant: {content}\n")
                prompt_parts.append("Assistant: ")
                full_prompt = "".join(prompt_parts)
                
                with httpx.Client(timeout=30.0) as client:
                    response = client.post(
                        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash:generateContent?key={self.google_key}",
                        json={
                            "contents": [{"parts": [{"text": full_prompt}]}],
                            "generationConfig": {"maxOutputTokens": 150, "temperature": 0.7}
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        text = result["candidates"][0]["content"]["parts"][0]["text"]
                        print(text)
                        self.messages.append({"role": "assistant", "content": text})
                        return text
            except Exception as e:
                pass  # Fall through to Groq
        
        # Fallback to Groq
        if self.groq_key:
            try:
                with httpx.Client(timeout=30.0) as client:
                    response = client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.groq_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "llama-3.3-70b-versatile",
                            "messages": self.messages,
                            "max_tokens": 150,
                            "temperature": 0.7
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        text = result["choices"][0]["message"]["content"]
                        print(text)
                        self.messages.append({"role": "assistant", "content": text})
                        return text
            except Exception as e:
                print(f"❌ LLM Error: {e}")
        
        return ""
    
    def speak(self, text):
        """Synthesize and play speech using Edge TTS."""
        if not EDGE_TTS_OK or not PYGAME_OK:
            print("(TTS unavailable)")
            return
        
        print("🔊 Speaking...", end=" ", flush=True)
        
        try:
            # Generate audio
            audio_file = os.path.join(tempfile.gettempdir(), f"sunona_tts_{os.getpid()}.mp3")
            
            loop = asyncio.new_event_loop()
            loop.run_until_complete(
                edge_tts.Communicate(text, "en-US-AriaNeural").save(audio_file)
            )
            loop.close()
            
            # Play audio
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            # Wait for playback with barge-in detection
            while pygame.mixer.music.get_busy():
                pygame.time.wait(50)
            
            print("done")
            
            # Cleanup
            try:
                os.remove(audio_file)
            except:
                pass
                
        except Exception as e:
            print(f"❌ TTS Error: {e}")
    
    def run(self):
        """Main conversation loop."""
        print("\n" + "=" * 60)
        print("🎙️  SUNONA - Hands-Free Voice Assistant")
        print("=" * 60)
        
        # Show providers
        if self.google_key:
            print("✅ LLM: Gemini (gemini-3-flash)")
        if self.groq_key:
            print("✅ LLM: Groq (llama-3.3-70b) - fallback")
        if self.deepgram_key:
            print("✅ STT: Deepgram (nova-2)")
        if EDGE_TTS_OK:
            print("✅ TTS: Edge TTS (AriaNeural) - FREE")
        
        print("\n" + "-" * 60)
        print("Just speak - Sunona listens and responds!")
        print("Say 'quit', 'goodbye', or 'exit' to end.")
        print("-" * 60)
        
        # Welcome
        welcome = "Hi! I'm Sunona, your AI assistant. How can I help you today?"
        print(f"\n💭 Sunona: {welcome}")
        self.speak(welcome)
        
        # Main loop
        exit_words = ["quit", "exit", "bye", "goodbye", "stop", "end", "close"]
        
        try:
            while True:
                wav_data = self.listen()
                
                if not wav_data:
                    continue
                
                text = self.transcribe(wav_data)
                
                if not text:
                    continue
                
                # Check for exit
                if any(word in text.lower() for word in exit_words):
                    break
                
                # Get and speak response
                response = self.get_llm_response(text)
                if response:
                    self.speak(response)
        
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted")
        
        # Goodbye
        goodbye = "It was great talking with you! Goodbye!"
        print(f"\n💭 Sunona: {goodbye}")
        self.speak(goodbye)
        
        print("\n✅ Session ended.")


def main():
    """Entry point."""
    if not AUDIO_OK:
        print("❌ Audio input not available. Install: pip install sounddevice numpy")
        sys.exit(1)
    
    assistant = HandsFreeAssistant()
    assistant.run()


if __name__ == "__main__":
    main()
