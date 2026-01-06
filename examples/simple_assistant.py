"""
Sunona Voice AI - Simple Voice Assistant

Hands-free voice assistant with:
- Deepgram REST API (nova-2) for Speech-to-Text
- OpenRouter (Mistral 7B free) for LLM, Groq (Llama 3.1 8B) as fallback
- ElevenLabs TTS (premium) with Edge TTS (FREE) as fallback
- Profanity detection with empathetic responses

Provider Selection (automatic based on .env file):
- LLM: OpenRouter (free) primary → Groq (fallback)
- TTS: ElevenLabs (if API key set) → Edge TTS (free, unlimited)

Required .env variables:
- DEEPGRAM_API_KEY (required)
- OPENROUTER_API_KEY or GROQ_API_KEY (at least one required)
- ELEVENLABS_API_KEY (optional, for premium TTS)

Usage:
    pip install sounddevice numpy edge-tts pygame httpx better-profanity langdetect
    python examples/simple_assistant.py
"""

import os
import sys
import json
import asyncio
import tempfile
import uuid
import wave
import io

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    # Add space between lowercase letter followed by uppercase (e.g., "HelloWorld" -> "Hello World")
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    # Add space between letter and number when it looks like a sentence (e.g., "topic1" stays, but "today?What" fixes)
    text = re.sub(r'([a-z][.!?])([A-Z])', r'\1 \2', text)
    # Fix missing space after punctuation
    text = re.sub(r'([.!?,;:])([A-Za-z])', r'\1 \2', text)
    # Fix multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

# Audio recording
try:
    import sounddevice as sd
    import numpy as np
    AUDIO_INPUT_OK = True
except ImportError:
    AUDIO_INPUT_OK = False
    print("ERROR: pip install sounddevice numpy")

# Audio playback
try:
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    PYGAME_OK = True
except ImportError:
    PYGAME_OK = False
    print("WARNING: pip install pygame")

# TTS - Edge TTS (free)
try:
    import edge_tts
    EDGE_TTS_OK = True
except ImportError:
    EDGE_TTS_OK = False
    print("WARNING: pip install edge-tts")

# TTS - ElevenLabs (premium, optional)
# Uses httpx which is already imported above
ELEVENLABS_OK = True

# ElevenLabs voice mapping
ELEVENLABS_VOICES = {
    "Bella": "EXAVITQu4vr4xnSDxMaL",
    "Rachel": "21m00Tcm4TlvDq8ikWAM", 
    "Domi": "AZnzlk1XvdvUeBnXmlld",
    "Elli": "MF3mGyEYCl7XYWbV9V6O",
    "Josh": "TxGEqnHWrfWFTfGW9XjX",
    "Arnold": "VR6AewLTigWG4xSOukaG",
    "Adam": "pNInz6obpgDQGcFmaJgB",
    "Sam": "yoZ06aMxZJJ28mfd3POQ",
}

# Profanity detection
try:
    from better_profanity import profanity
    profanity.load_censor_words()
    PROFANITY_OK = True
except ImportError:
    PROFANITY_OK = False

# Language detection for multilingual TTS
try:
    from langdetect import detect
    LANGDETECT_OK = True
except ImportError:
    LANGDETECT_OK = False

# Multilingual voice mapping
LANGUAGE_VOICES = {
    "en": "en-US-AriaNeural",        # English (premium female voice)
    "hi": "hi-IN-SwaraNeural",       # Hindi
    "es": "es-ES-ElviraNeural",      # Spanish
    "fr": "fr-FR-DeniseNeural",      # French
    "de": "de-DE-KatjaNeural",       # German
    "it": "it-IT-ElsaNeural",        # Italian
    "pt": "pt-BR-FranciscaNeural",   # Portuguese
    "ru": "ru-RU-SvetlanaNeural",    # Russian
    "ja": "ja-JP-NanamiNeural",      # Japanese
    "ko": "ko-KR-SunHiNeural",       # Korean
    "zh": "zh-CN-XiaoxiaoNeural",    # Chinese
    "ar": "ar-SA-ZariyahNeural",     # Arabic
    "ta": "ta-IN-PallaviNeural",     # Tamil
    "te": "te-IN-ShrutiNeural",      # Telugu
    "bn": "bn-IN-TanishaaNeural",    # Bengali
    "mr": "mr-IN-AarohiNeural",      # Marathi
    "gu": "gu-IN-DhwaniNeural",      # Gujarati
}


class SimpleVoiceAssistant:
    """Simple hands-free voice assistant."""
    
    def __init__(
        self,
        groq_key: str = None,
        openrouter_key: str = None,
        deepgram_key: str = None,
        elevenlabs_key: str = None,
        voice: str = "en-US-AriaNeural",  # Premium female voice (Edge TTS)
        elevenlabs_voice: str = "Bella"
    ):
        self.groq_key = groq_key
        self.openrouter_key = openrouter_key
        self.deepgram_key = deepgram_key
        self.elevenlabs_key = elevenlabs_key
        self.voice = voice  # Edge TTS voice
        self.elevenlabs_voice = elevenlabs_voice  # ElevenLabs voice name
        self.elevenlabs_voice_id = ELEVENLABS_VOICES.get(elevenlabs_voice, "EXAVITQu4vr4xnSDxMaL")
        self.messages = []
        self.sample_rate = 16000
        self.energy_threshold = 300  # Higher = less sensitive (reduces false triggers from noise)
        
        # Use Edge TTS by default (free, unlimited, low latency)
        # Set use_elevenlabs=True manually if you have an API key and prefer it
        self.use_elevenlabs = False  # Disabled by default for faster response
        
        # Set system prompt
        self.messages.append({
            "role": "system",
            "content": """You are Sunona, a helpful and friendly AI voice assistant. 

You provide support in every aspect and are capable of excellent customer service. You are:
- Warm, empathetic, and understanding
- Quick to help solve problems
- Professional yet conversational
- Always patient and supportive

Keep responses SHORT (1-2 sentences) for natural voice conversation. Be helpful and make every interaction positive."""
        })
    
    def listen(self, max_duration=30, silence_duration=1.5):
        """Listen for speech with fast VAD - prints once, waits until speech."""
        print("\n🎤 Listening...", end="", flush=True)
        
        chunk_duration = 0.1
        chunk_samples = int(self.sample_rate * chunk_duration)
        silence_chunks = int(silence_duration / chunk_duration)
        max_chunks = int(max_duration / chunk_duration)
        
        # Keep trying until we get speech
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
                print()  # New line after listening status
                
                # Convert to WAV
                audio = np.concatenate(chunks)
                wav_buffer = io.BytesIO()
                with wave.open(wav_buffer, 'wb') as wav:
                    wav.setnchannels(1)
                    wav.setsampwidth(2)
                    wav.setframerate(self.sample_rate)
                    wav.writeframes(audio.tobytes())
                
                return wav_buffer.getvalue()
            
            # No speech detected - continue waiting silently (no new print)
    
    def transcribe(self, wav_data, retries: int = 1):
        """Transcribe audio using Deepgram with retry logic."""
        print("📝 Transcribing...", end=" ", flush=True)
        
        url = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true"
        headers = {
            "Authorization": f"Token {self.deepgram_key}",
            "Content-Type": "audio/wav"
        }
        
        for attempt in range(retries + 1):
            try:
                with httpx.Client(timeout=5.0) as client:  # Fast 5s timeout
                    response = client.post(url, headers=headers, content=wav_data)
                    response.raise_for_status()
                    
                    data = response.json()
                    text = data.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "")
                    
                    if text:
                        print(f'"{text}"')
                    else:
                        print("(no speech)")
                    
                    return text
            except httpx.TimeoutException:
                if attempt < retries:
                    print(f"(retry {attempt + 1})...", end=" ", flush=True)
                    continue
                print("❌ Timeout")
                return ""
            except Exception as e:
                print(f"❌ Error: {e}")
                return ""
        
        return ""
    
    def check_profanity(self, text: str) -> tuple[bool, str]:
        """Check for profanity and return sympathetic response if needed."""
        if not PROFANITY_OK:
            return False, ""
        
        if profanity.contains_profanity(text):
            responses = [
                "I understand you might be frustrated. I'm here to help - how can I make things better for you?",
                "I hear that you're upset. Let's take a breath together. What can I do to assist you?",
                "It sounds like you're going through a tough time. I'm here to listen and help in any way I can.",
                "I sense some frustration. That's completely okay. How can I support you right now?",
                "I'm sorry you're feeling this way. I'm here for you - let's work through this together.",
            ]
            import random
            return True, random.choice(responses)
        
        return False, ""
    
    def get_llm_response(self, user_message: str) -> str:
        """Get response from OpenRouter (free) or Groq (fallback) LLM."""
        self.messages.append({"role": "user", "content": user_message})
        
        full_response = []
        print("💭 Sunona: ", end="", flush=True)  # Will print response after collecting
        
        # Try OpenRouter first (free Mistral 7B)
        if self.openrouter_key:
            try:
                headers = {
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://sunona.ai",
                    "X-Title": "Sunona Voice AI"
                }
                
                body = {
                    "model": "mistralai/mistral-7b-instruct:free",
                    "messages": self.messages,
                    "max_tokens": 100,
                    "temperature": 0.7,
                    "stream": True
                }
                
                with httpx.Client(timeout=15.0) as client:  # Fast 15s timeout
                    with client.stream(
                        "POST",
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json=body
                    ) as response:
                        response.raise_for_status()
                        
                        for line in response.iter_lines():
                            if not line or line.startswith(":"):
                                continue
                            
                            if line.startswith("data:"):
                                data_str = line[5:].strip()
                                
                                if data_str == "[DONE]":
                                    break
                                
                                try:
                                    data = json.loads(data_str)
                                    content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                    
                                    if content:
                                        # Don't clean individual tokens - preserve spaces
                                        # Clean only the final joined response
                                        full_response.append(content)
                                except json.JSONDecodeError:
                                    continue
            except Exception as e:
                # Uncomment below to see OpenRouter error:
                # print(f"[OpenRouter failed: {e}, trying Groq...]", end=" ", flush=True)
                pass
        
        # Fallback to Groq if OpenRouter failed or not available
        if not full_response and self.groq_key:
            try:
                headers = {
                    "Authorization": f"Bearer {self.groq_key}",
                    "Content-Type": "application/json"
                }
                
                body = {
                    "model": "llama-3.1-8b-instant",
                    "messages": self.messages,
                    "max_tokens": 100,
                    "temperature": 0.7,
                    "stream": True
                }
                
                with httpx.Client(timeout=10.0) as client:  # Fast 10s timeout
                    with client.stream(
                        "POST",
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers=headers,
                        json=body
                    ) as response:
                        response.raise_for_status()
                        
                        for line in response.iter_lines():
                            if not line or line.startswith(":"):
                                continue
                            
                            if line.startswith("data:"):
                                data_str = line[5:].strip()
                                
                                if data_str == "[DONE]":
                                    break
                                
                                try:
                                    data = json.loads(data_str)
                                    content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                    
                                    if content:
                                        full_response.append(content)
                                except json.JSONDecodeError:
                                    continue
            except Exception as e:
                # Uncomment below to see Groq error:
                # print(f"❌ Groq Error: {e}")
                pass
        
        if not full_response:
            print("❌ No LLM response")
        else:
            # Print complete response (properly spaced, not streamed)
            response_text = "".join(full_response).strip()
            response_text = clean_llm_tokens(response_text)
            print(response_text)
        
        response_text = "".join(full_response).strip()
        # Final cleanup of any remaining tokens (handles accumulated edge cases)
        response_text = clean_llm_tokens(response_text)
        if response_text:
            self.messages.append({"role": "assistant", "content": response_text})
        
        return response_text
    
    def speak(self, text: str) -> bool:
        """
        Speak text using ElevenLabs (if API key set) or Edge TTS (free fallback).
        
        Returns:
            True if speech was interrupted by user (barge-in), False otherwise.
        """
        if not text.strip():
            return False
        
        if not PYGAME_OK:
            print("⚠️ pygame not available for audio playback")
            return False
        
        interrupted = False
        
        try:
            print("🔊 Speaking...", end=" ", flush=True)
            # Use unique filename to avoid Windows file locking issues
            audio_file = os.path.join(tempfile.gettempdir(), f"sunona_voice_{uuid.uuid4().hex[:8]}.mp3")
            
            # Use ElevenLabs if API key is set
            if self.use_elevenlabs:
                try:
                    self._speak_elevenlabs(text, audio_file)
                except Exception as e:
                    # Uncomment below to see ElevenLabs error:
                    # print(f"[ElevenLabs failed: {e}, using Edge TTS]", end=" ", flush=True)
                    # Silently fall back to Edge TTS
                    self.use_elevenlabs = False  # Don't retry ElevenLabs
                    self._speak_edge_tts(text, audio_file)
            else:
                # Use free Edge TTS
                if not EDGE_TTS_OK:
                    print("❌ No TTS available (install edge-tts)")
                    return False
                self._speak_edge_tts(text, audio_file)
            
            # Play audio with barge-in detection
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            # Monitor for user interruption while playing
            interrupted = self._play_with_barge_in()
            
            # Stop and cleanup
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            
            try:
                os.remove(audio_file)
            except:
                pass
            
            if interrupted:
                print("(interrupted)\n")
            else:
                print("Done\n")
                
        except Exception as e:
            print(f"❌ Voice error: {e}")
        
        return interrupted
    
    def _play_with_barge_in(self) -> bool:
        """
        Play audio while monitoring microphone for user speech (barge-in).
        
        Returns:
            True if user started speaking (barge-in detected), False if playback completed.
        """
        if not AUDIO_INPUT_OK:
            # No mic available, just wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.wait(50)
            return False
        
        chunk_samples = int(self.sample_rate * 0.1)  # 100ms chunks
        consecutive_speech = 0
        speech_threshold = 5  # Need 5 consecutive chunks (500ms) of speech to trigger barge-in
        
        try:
            with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='int16') as stream:
                while pygame.mixer.music.get_busy():
                    data, _ = stream.read(chunk_samples)
                    energy = np.sqrt(np.mean(data.astype(np.float32) ** 2))
                    
                    # Much higher threshold for barge-in to reduce false positives from noise
                    if energy > self.energy_threshold * 2.5:
                        consecutive_speech += 1
                        if consecutive_speech >= speech_threshold:
                            return True  # User is speaking, barge-in!
                    else:
                        consecutive_speech = 0
                    
        except Exception:
            # If mic fails, just wait for playback
            while pygame.mixer.music.get_busy():
                pygame.time.wait(50)
        
        return False
    
    def _speak_elevenlabs(self, text: str, audio_file: str):
        """Synthesize speech using ElevenLabs REST API."""
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.elevenlabs_voice_id}"
        
        headers = {
            "xi-api-key": self.elevenlabs_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg"
        }
        
        body = {
            "text": text,
            "model_id": "eleven_turbo_v2_5",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        with httpx.Client(timeout=15.0) as client:  # Fast 15s timeout
            response = client.post(url, headers=headers, json=body)
            response.raise_for_status()
            
            with open(audio_file, "wb") as f:
                f.write(response.content)
    
    def _speak_edge_tts(self, text: str, audio_file: str):
        """Synthesize speech using Edge TTS (free)."""
        # Auto-detect language and select voice
        voice = self.voice  # Default English
        if LANGDETECT_OK:
            try:
                lang = detect(text)
                if lang in LANGUAGE_VOICES:
                    voice = LANGUAGE_VOICES[lang]
            except:
                pass
        
        loop = asyncio.new_event_loop()
        loop.run_until_complete(
            edge_tts.Communicate(text, voice).save(audio_file)
        )
        loop.close()
    
    def chat(self, user_message: str, speak_response: bool = True) -> tuple[str, bool]:
        """
        Chat with profanity detection.
        
        Returns:
            Tuple of (response_text, was_interrupted)
        """
        is_profane, sympathetic_response = self.check_profanity(user_message)
        
        if is_profane:
            print(f"💙 Sunona: {sympathetic_response}")
            self.messages.append({"role": "user", "content": user_message})
            self.messages.append({"role": "assistant", "content": sympathetic_response})
            
            interrupted = False
            if speak_response:
                interrupted = self.speak(sympathetic_response)
            
            return sympathetic_response, interrupted
        
        response = self.get_llm_response(user_message)
        
        interrupted = False
        if speak_response and response:
            interrupted = self.speak(response)
        
        return response, interrupted


def main():
    """Run the voice assistant."""
    print()
    print("=" * 60)
    print("   🎙️ SUNONA VOICE AI")
    print("=" * 60)
    print()
    
    groq_key = os.getenv("GROQ_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    deepgram_key = os.getenv("DEEPGRAM_API_KEY")
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    
    # Need at least one LLM provider
    if not groq_key and not openrouter_key:
        print("❌ Set GROQ_API_KEY or OPENROUTER_API_KEY in .env")
        sys.exit(1)
    
    if not deepgram_key:
        print("❌ DEEPGRAM_API_KEY not set in .env")
        sys.exit(1)
    
    if not AUDIO_INPUT_OK:
        print("❌ pip install sounddevice numpy")
        sys.exit(1)
    
    # Show which LLM is being used
    if openrouter_key:
        print("LLM: OpenRouter (mistral-7b) 🆓 free")
    if groq_key:
        print("LLM: Groq (llama-3.1-8b-instant) 🔄 fallback" if openrouter_key else "LLM: Groq (llama-3.1-8b-instant)")
    
    # Show STT provider
    print("STT: Deepgram (nova-2) 🎤 speech-to-text")
    
    # Show which TTS is being used
    if elevenlabs_key:
        print("TTS: ElevenLabs (Bella) 🎙️ premium → Edge TTS 🔄 fallback")
    elif EDGE_TTS_OK:
        print("TTS: Edge TTS (Jenny) 🆓 free unlimited")
    else:
        print("⚠️ No TTS available")
    
    print()
    
    print("Just speak - Sunona listens and responds!")
    print("Say 'quit', 'goodbye', 'bye', 'stop', 'exit', 'end', or 'close' to exit.\n")
    print("-" * 60)
    
    assistant = SimpleVoiceAssistant(
        groq_key=groq_key,
        openrouter_key=openrouter_key,
        deepgram_key=deepgram_key,
        elevenlabs_key=elevenlabs_key
    )
    
    # Welcome (using phonetic spelling for TTS)
    welcome = "Hi there! I'm Sue-nona, your personal AI assistant. I'm here to help with anything you need. How can I assist you today?"
    print(f"\n💭 Sunona: {welcome}")
    assistant.speak(welcome)
    
    # Main loop
    try:
        while True:
            wav_data = assistant.listen()
            
            if not wav_data:
                continue
            
            text = assistant.transcribe(wav_data)
            
            if not text:
                continue
            
            # Exit words to end the conversation
            exit_words = ["quit", "exit", "bye", "goodbye", "stop", "end", "close", "terminate", "finish", "done for now", "leave", "see you", "later", "take care"]
            if any(word in text.lower() for word in exit_words):
                break
            
            # Chat and check if user interrupted (barge-in)
            response, was_interrupted = assistant.chat(text, speak_response=True)
            
            # If user interrupted, immediately listen for their new input
            # This creates a natural conversational flow
            while was_interrupted:
                print("🎤 (barge-in detected, listening...)")
                wav_data = assistant.listen()
                
                if not wav_data:
                    break
                
                text = assistant.transcribe(wav_data)
                
                if not text:
                    break
                
                # Check for exit words in interrupted speech too
                if any(word in text.lower() for word in exit_words):
                    break
                
                # Process the interrupted input
                response, was_interrupted = assistant.chat(text, speak_response=True)
    
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted")
    
    # Goodbye (using phonetic spelling for TTS)
    goodbye = "It was wonderful talking with you! Thank you for choosing Sue-nona. Take care, and I'm always here whenever you need me!"
    print(f"\n💭 Sunona: {goodbye}")
    assistant.speak(goodbye)
    
    print("\n✅ Session ended.")


if __name__ == "__main__":
    main()
