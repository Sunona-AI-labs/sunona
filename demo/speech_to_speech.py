"""
Speech-to-Speech Demo Backend

Handles full voice conversation: Audio → STT → LLM → TTS → Audio
Features hands-free operation with Voice Activity Detection (VAD).
"""

import os
import asyncio
import tempfile
import logging
import wave
import struct
from typing import Optional, Tuple, Callable, List, Dict
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class DemoState(Enum):
    """State of the speech-to-speech demo."""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"


@dataclass
class VADConfig:
    """Voice Activity Detection configuration."""
    sample_rate: int = 16000
    frame_duration_ms: int = 30  # 10, 20, or 30 ms
    silence_threshold_ms: int = 1500  # 1.5 seconds of silence = end of speech
    min_speech_duration_ms: int = 300  # Minimum speech to process
    energy_threshold: float = 300.0  # Energy threshold for voice detection


class SpeechToSpeechDemo:
    """
    Speech-to-Speech conversation handler.
    
    Features:
    - Voice Activity Detection for hands-free operation
    - Multiple STT provider support
    - Multiple LLM provider support
    - Multiple TTS provider support with Edge TTS fallback
    - Continuous conversation mode
    """
    
    # STT provider configurations
    STT_CONFIGS = {
        "Deepgram": {
            "env_key": "DEEPGRAM_API_KEY",
            "endpoint": "https://api.deepgram.com/v1/listen",
        },
        "AssemblyAI": {
            "env_key": "ASSEMBLYAI_API_KEY",
            "endpoint": "https://api.assemblyai.com/v2/transcript",
        },
        "Groq Whisper": {
            "env_key": "GROQ_API_KEY",
            "model": "whisper-large-v3",
        },
        "OpenAI Whisper": {
            "env_key": "OPENAI_API_KEY",
            "model": "whisper-1",
        },
    }
    
    def __init__(
        self,
        system_prompt: str,
        stt_provider: str = "Deepgram",
        stt_api_key: Optional[str] = None,
        llm_provider: str = "Gemini",
        llm_api_key: Optional[str] = None,
        tts_provider: str = "Edge TTS (Free)",
        tts_api_key: Optional[str] = None,
        tts_voice: Optional[str] = None,
        vad_config: Optional[VADConfig] = None,
    ):
        """
        Initialize Speech-to-Speech demo.
        
        Args:
            system_prompt: System prompt for LLM
            stt_provider: STT provider name
            stt_api_key: STT API key
            llm_provider: LLM provider name
            llm_api_key: LLM API key
            tts_provider: TTS provider name
            tts_api_key: TTS API key
            tts_voice: Voice ID for TTS
            vad_config: VAD configuration
        """
        self.system_prompt = system_prompt
        
        # STT config
        self.stt_provider = stt_provider
        self.stt_api_key = stt_api_key or self._get_stt_key(stt_provider)
        
        # LLM config
        self.llm_provider = llm_provider
        self.llm_api_key = llm_api_key or os.getenv("GOOGLE_API_KEY")
        
        # TTS config
        self.tts_provider = tts_provider
        self.tts_api_key = tts_api_key or os.getenv("ELEVENLABS_API_KEY")
        self.tts_voice = tts_voice or "en-US-AriaNeural"
        
        # VAD config
        self.vad_config = vad_config or VADConfig()
        
        # State
        self.state = DemoState.IDLE
        self.conversation_history: List[Dict[str, str]] = []
        self.is_running = False
        
        # Output directory
        self.output_dir = Path(tempfile.gettempdir()) / "sunona_demo"
        self.output_dir.mkdir(exist_ok=True)
    
    def _get_stt_key(self, provider: str) -> Optional[str]:
        """Get STT API key from environment."""
        config = self.STT_CONFIGS.get(provider, {})
        env_key = config.get("env_key")
        return os.getenv(env_key) if env_key else None
    
    async def process_audio(
        self,
        audio_path: str,
    ) -> Tuple[str, str, Optional[str], Optional[str]]:
        """
        Process audio through full pipeline: STT → LLM → TTS
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Tuple of (transcript, response_text, audio_path, error)
        """
        self.state = DemoState.PROCESSING
        
        # Step 1: Transcribe audio
        transcript, stt_error = await self._transcribe(audio_path)
        
        if stt_error:
            self.state = DemoState.IDLE
            return "", "", None, stt_error
        
        if not transcript.strip():
            self.state = DemoState.IDLE
            return "", "", None, None  # No speech detected
        
        # Step 2: Get LLM response
        response_text, llm_error = await self._get_llm_response(transcript)
        
        if llm_error:
            self.state = DemoState.IDLE
            return transcript, "", None, llm_error
        
        # Step 3: Synthesize speech
        self.state = DemoState.SPEAKING
        audio_out, tts_error = await self._synthesize(response_text)
        
        if tts_error:
            self.state = DemoState.IDLE
            return transcript, response_text, None, tts_error
        
        self.state = DemoState.IDLE
        return transcript, response_text, audio_out, None
    
    async def _transcribe(self, audio_path: str) -> Tuple[str, Optional[str]]:
        """Transcribe audio to text."""
        if not self.stt_api_key:
            return "", f"🎤 STT: No API key for {self.stt_provider}. Add your key."
        
        try:
            if self.stt_provider == "Deepgram":
                return await self._transcribe_deepgram(audio_path)
            elif self.stt_provider == "AssemblyAI":
                return await self._transcribe_assemblyai(audio_path)
            elif self.stt_provider == "Groq Whisper":
                return await self._transcribe_groq(audio_path)
            elif self.stt_provider == "OpenAI Whisper":
                return await self._transcribe_openai(audio_path)
            else:
                return "", f"🎤 STT: Unknown provider {self.stt_provider}"
                
        except Exception as e:
            return "", self._parse_stt_error(e)
    
    async def _transcribe_deepgram(self, audio_path: str) -> Tuple[str, Optional[str]]:
        """Transcribe with Deepgram."""
        import httpx
        
        with open(audio_path, "rb") as f:
            audio_data = f.read()
        
        # Detect content type
        content_type = "audio/wav"
        if audio_path.endswith(".mp3"):
            content_type = "audio/mpeg"
        elif audio_path.endswith(".webm"):
            content_type = "audio/webm"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.deepgram.com/v1/listen",
                headers={
                    "Authorization": f"Token {self.stt_api_key}",
                    "Content-Type": content_type,
                },
                content=audio_data,
                params={
                    "model": "nova-2",
                    "language": "en",
                    "smart_format": "true",
                },
                timeout=30.0,
            )
            
            if response.status_code == 200:
                result = response.json()
                channels = result.get("results", {}).get("channels", [])
                if channels:
                    alternatives = channels[0].get("alternatives", [])
                    if alternatives:
                        return alternatives[0].get("transcript", ""), None
                return "", None
            else:
                raise Exception(f"Deepgram error: {response.status_code}")
    
    async def _transcribe_assemblyai(self, audio_path: str) -> Tuple[str, Optional[str]]:
        """Transcribe with AssemblyAI."""
        import httpx
        
        async with httpx.AsyncClient() as client:
            # Upload file
            with open(audio_path, "rb") as f:
                upload_response = await client.post(
                    "https://api.assemblyai.com/v2/upload",
                    headers={"authorization": self.stt_api_key},
                    content=f.read(),
                    timeout=60.0,
                )
            
            if upload_response.status_code != 200:
                raise Exception("AssemblyAI upload failed")
            
            upload_url = upload_response.json()["upload_url"]
            
            # Request transcription
            transcript_response = await client.post(
                "https://api.assemblyai.com/v2/transcript",
                headers={"authorization": self.stt_api_key},
                json={"audio_url": upload_url},
                timeout=30.0,
            )
            
            if transcript_response.status_code != 200:
                raise Exception("AssemblyAI transcription request failed")
            
            transcript_id = transcript_response.json()["id"]
            
            # Poll for result
            for _ in range(60):  # Max 60 seconds
                result_response = await client.get(
                    f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                    headers={"authorization": self.stt_api_key},
                    timeout=10.0,
                )
                
                result = result_response.json()
                status = result.get("status")
                
                if status == "completed":
                    return result.get("text", ""), None
                elif status == "error":
                    raise Exception(result.get("error", "Unknown error"))
                
                await asyncio.sleep(1)
            
            raise Exception("AssemblyAI transcription timeout")
    
    async def _transcribe_groq(self, audio_path: str) -> Tuple[str, Optional[str]]:
        """Transcribe with Groq Whisper."""
        import httpx
        
        async with httpx.AsyncClient() as client:
            with open(audio_path, "rb") as f:
                files = {"file": (os.path.basename(audio_path), f, "audio/wav")}
                response = await client.post(
                    "https://api.groq.com/openai/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {self.stt_api_key}"},
                    files=files,
                    data={"model": "whisper-large-v3"},
                    timeout=60.0,
                )
            
            if response.status_code == 200:
                return response.json().get("text", ""), None
            else:
                raise Exception(f"Groq error: {response.status_code}")
    
    async def _transcribe_openai(self, audio_path: str) -> Tuple[str, Optional[str]]:
        """Transcribe with OpenAI Whisper."""
        import httpx
        
        async with httpx.AsyncClient() as client:
            with open(audio_path, "rb") as f:
                files = {"file": (os.path.basename(audio_path), f, "audio/wav")}
                response = await client.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {self.stt_api_key}"},
                    files=files,
                    data={"model": "whisper-1"},
                    timeout=60.0,
                )
            
            if response.status_code == 200:
                return response.json().get("text", ""), None
            else:
                raise Exception(f"OpenAI error: {response.status_code}")
    
    async def _get_llm_response(self, user_message: str) -> Tuple[str, Optional[str]]:
        """Get response from LLM."""
        if not self.llm_api_key:
            return "", f"🧠 LLM: No API key for {self.llm_provider}. Add your key."
        
        try:
            from litellm import acompletion
            
            model_map = {
                "Gemini": "gemini/gemini-1.5-flash",
                "OpenAI GPT": "gpt-4o-mini",
                "Groq": "groq/llama-3.1-70b-versatile",
                "Anthropic Claude": "claude-3-5-sonnet-20241022",
            }
            model = model_map.get(self.llm_provider, "gemini/gemini-1.5-flash")
            
            # Build messages
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(self.conversation_history)
            messages.append({"role": "user", "content": user_message})
            
            response = await acompletion(
                model=model,
                messages=messages,
                api_key=self.llm_api_key,
                max_tokens=200,  # Keep short for voice
                temperature=0.7,
            )
            
            assistant_message = response.choices[0].message.content
            
            # Update history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            # Keep history manageable
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return assistant_message, None
            
        except Exception as e:
            return "", self._parse_llm_error(e)
    
    async def _synthesize(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Synthesize speech from text."""
        try:
            if self.tts_provider == "Edge TTS (Free)":
                return await self._edge_tts(text)
            elif self.tts_provider == "ElevenLabs":
                return await self._elevenlabs_tts(text)
            else:
                return await self._edge_tts(text)
                
        except Exception as e:
            # Fallback to Edge TTS
            try:
                return await self._edge_tts(text)
            except Exception as fallback_error:
                return None, f"🔊 TTS Error: {str(fallback_error)[:100]}"
    
    async def _edge_tts(self, text: str) -> Tuple[str, Optional[str]]:
        """Synthesize with Edge TTS."""
        import edge_tts
        
        output_path = str(self.output_dir / "s2s_output.mp3")
        voice = self.tts_voice if "Neural" in self.tts_voice else "en-US-AriaNeural"
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        
        return output_path, None
    
    async def _elevenlabs_tts(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Synthesize with ElevenLabs."""
        if not self.tts_api_key:
            return await self._edge_tts(text)
        
        import httpx
        
        output_path = str(self.output_dir / "s2s_output.mp3")
        voice_id = self.tts_voice if len(self.tts_voice) > 10 else "EXAVITQu4vr4xnSDxMaL"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                headers={
                    "xi-api-key": self.tts_api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "text": text,
                    "model_id": "eleven_turbo_v2_5",
                },
                timeout=30.0,
            )
            
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return output_path, None
            else:
                return await self._edge_tts(text)
    
    def _parse_stt_error(self, e: Exception) -> str:
        """Parse STT error."""
        error_msg = str(e).lower()
        
        if "rate limit" in error_msg or "429" in error_msg:
            return f"🎤 STT: Rate limit for {self.stt_provider}. Add your key."
        elif "401" in error_msg or "403" in error_msg:
            return f"🎤 STT: Invalid key for {self.stt_provider}."
        else:
            return f"🎤 STT Error: {str(e)[:100]}"
    
    def _parse_llm_error(self, e: Exception) -> str:
        """Parse LLM error."""
        error_msg = str(e).lower()
        
        if "rate limit" in error_msg or "429" in error_msg:
            return f"🧠 LLM: Rate limit for {self.llm_provider}. Add your key."
        elif "quota" in error_msg or "credit" in error_msg:
            return f"🧠 LLM: Credits exhausted for {self.llm_provider}. Add your key."
        elif "401" in error_msg or "403" in error_msg:
            return f"🧠 LLM: Invalid key for {self.llm_provider}."
        else:
            return f"🧠 LLM Error: {str(e)[:100]}"
    
    def reset_conversation(self):
        """Reset conversation history."""
        self.conversation_history = []
        self.state = DemoState.IDLE


# Convenience function
async def process_voice(
    audio_path: str,
    system_prompt: str,
    stt_provider: str = "Deepgram",
    stt_api_key: Optional[str] = None,
    llm_provider: str = "Gemini",
    llm_api_key: Optional[str] = None,
    tts_provider: str = "Edge TTS (Free)",
    tts_api_key: Optional[str] = None,
    tts_voice: Optional[str] = None,
) -> Tuple[str, str, Optional[str], Optional[str]]:
    """
    Process voice input through full pipeline.
    
    Returns:
        Tuple of (transcript, response, audio_path, error)
    """
    demo = SpeechToSpeechDemo(
        system_prompt=system_prompt,
        stt_provider=stt_provider,
        stt_api_key=stt_api_key,
        llm_provider=llm_provider,
        llm_api_key=llm_api_key,
        tts_provider=tts_provider,
        tts_api_key=tts_api_key,
        tts_voice=tts_voice,
    )
    return await demo.process_audio(audio_path)
