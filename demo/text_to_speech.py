"""
Text-to-Speech Demo Backend

Handles LLM response generation and TTS synthesis.
Pipeline: Text → LLM → TTS → Audio
"""

import os
import asyncio
import tempfile
import logging
from typing import Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class TextToSpeechDemo:
    """
    Text-to-Speech demo handler.
    
    Features:
    - Multiple LLM provider support
    - Multiple TTS provider support (Edge TTS, ElevenLabs, OpenAI)
    - Automatic fallback to Edge TTS (free)
    - Error handling with specific API identification
    """
    
    # TTS provider configurations
    TTS_CONFIGS = {
        "Edge TTS (Free)": {
            "requires_key": False,
            "default_voice": "en-US-AriaNeural",
        },
        "ElevenLabs": {
            "requires_key": True,
            "default_voice": "EXAVITQu4vr4xnSDxMaL",
            "env_key": "ELEVENLABS_API_KEY",
        },
        "OpenAI TTS": {
            "requires_key": True,
            "default_voice": "alloy",
            "env_key": "OPENAI_API_KEY",
        },
        "Deepgram Aura": {
            "requires_key": True,
            "default_voice": "aura-asteria-en",
            "env_key": "DEEPGRAM_API_KEY",
        },
    }
    
    def __init__(
        self,
        system_prompt: str,
        llm_provider: str = "Gemini",
        llm_api_key: Optional[str] = None,
        tts_provider: str = "Edge TTS (Free)",
        tts_api_key: Optional[str] = None,
        tts_voice: Optional[str] = None,
    ):
        """
        Initialize the Text-to-Speech demo.
        
        Args:
            system_prompt: System prompt for LLM
            llm_provider: LLM provider name
            llm_api_key: LLM API key
            tts_provider: TTS provider name
            tts_api_key: TTS API key
            tts_voice: Voice ID for TTS
        """
        self.system_prompt = system_prompt
        self.llm_provider = llm_provider
        self.llm_api_key = llm_api_key or os.getenv("GOOGLE_API_KEY")
        self.tts_provider = tts_provider
        self.tts_api_key = tts_api_key or self._get_tts_key(tts_provider)
        self.tts_voice = tts_voice or self._get_default_voice(tts_provider)
        
        # Output directory
        self.output_dir = Path(tempfile.gettempdir()) / "sunona_demo"
        self.output_dir.mkdir(exist_ok=True)
    
    def _get_tts_key(self, provider: str) -> Optional[str]:
        """Get TTS API key from environment."""
        config = self.TTS_CONFIGS.get(provider, {})
        env_key = config.get("env_key")
        return os.getenv(env_key) if env_key else None
    
    def _get_default_voice(self, provider: str) -> str:
        """Get default voice for provider."""
        config = self.TTS_CONFIGS.get(provider, {})
        return config.get("default_voice", "en-US-AriaNeural")
    
    async def generate_response(
        self,
        user_question: str,
    ) -> Tuple[str, Optional[str], Optional[str]]:
        """
        Generate LLM response and synthesize speech.
        
        Args:
            user_question: The user's question
            
        Returns:
            Tuple of (response_text, audio_path, error_message)
        """
        # Step 1: Get LLM response
        response_text, llm_error = await self._get_llm_response(user_question)
        
        if llm_error:
            return "", None, llm_error
        
        # Step 2: Synthesize speech
        audio_path, tts_error = await self._synthesize_speech(response_text)
        
        if tts_error:
            return response_text, None, tts_error
        
        return response_text, audio_path, None
    
    async def _get_llm_response(self, question: str) -> Tuple[str, Optional[str]]:
        """Get response from LLM."""
        if not self.llm_api_key:
            return "", f"🧠 LLM: No API key configured for {self.llm_provider}. Add your key."
        
        try:
            from litellm import acompletion
            
            # Map provider to model
            model_map = {
                "Gemini": "gemini/gemini-1.5-flash",
                "OpenAI GPT": "gpt-4o-mini",
                "Groq": "groq/llama-3.1-70b-versatile",
                "Anthropic Claude": "claude-3-5-sonnet-20241022",
            }
            model = model_map.get(self.llm_provider, "gemini/gemini-1.5-flash")
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": question}
            ]
            
            response = await acompletion(
                model=model,
                messages=messages,
                api_key=self.llm_api_key,
                max_tokens=300,  # Keep short for TTS
                temperature=0.7,
            )
            
            return response.choices[0].message.content, None
            
        except Exception as e:
            return "", self._parse_llm_error(e)
    
    async def _synthesize_speech(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Synthesize speech from text."""
        try:
            if self.tts_provider == "Edge TTS (Free)":
                return await self._edge_tts(text)
            elif self.tts_provider == "ElevenLabs":
                return await self._elevenlabs_tts(text)
            elif self.tts_provider == "OpenAI TTS":
                return await self._openai_tts(text)
            else:
                # Fallback to Edge TTS
                logger.warning(f"Unknown TTS provider {self.tts_provider}, using Edge TTS")
                return await self._edge_tts(text)
                
        except Exception as e:
            logger.error(f"TTS error: {e}")
            # Try fallback to Edge TTS
            try:
                return await self._edge_tts(text)
            except Exception as fallback_error:
                return None, f"🔊 TTS Error: {str(fallback_error)[:100]}"
    
    async def _edge_tts(self, text: str) -> Tuple[str, Optional[str]]:
        """Synthesize with Edge TTS (free)."""
        import edge_tts
        
        output_path = str(self.output_dir / "tts_output.mp3")
        communicate = edge_tts.Communicate(text, self.tts_voice)
        await communicate.save(output_path)
        
        return output_path, None
    
    async def _elevenlabs_tts(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Synthesize with ElevenLabs."""
        if not self.tts_api_key:
            # Fallback to Edge TTS
            logger.warning("No ElevenLabs key, falling back to Edge TTS")
            return await self._edge_tts(text)
        
        import httpx
        
        output_path = str(self.output_dir / "tts_output.mp3")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{self.tts_voice}",
                headers={
                    "xi-api-key": self.tts_api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "text": text,
                    "model_id": "eleven_turbo_v2_5",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75,
                    }
                },
                timeout=30.0,
            )
            
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return output_path, None
            else:
                error_msg = str(response.text)[:100]
                if "quota" in error_msg.lower() or "limit" in error_msg.lower():
                    # Fallback to Edge TTS
                    logger.warning("ElevenLabs quota exceeded, falling back to Edge TTS")
                    return await self._edge_tts(text)
                return None, f"🔊 ElevenLabs Error: {error_msg}"
    
    async def _openai_tts(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Synthesize with OpenAI TTS."""
        if not self.tts_api_key:
            return await self._edge_tts(text)
        
        import httpx
        
        output_path = str(self.output_dir / "tts_output.mp3")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/audio/speech",
                headers={
                    "Authorization": f"Bearer {self.tts_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "tts-1",
                    "input": text,
                    "voice": self.tts_voice or "alloy",
                },
                timeout=30.0,
            )
            
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return output_path, None
            else:
                return await self._edge_tts(text)
    
    def _parse_llm_error(self, e: Exception) -> str:
        """Parse LLM exception and return user-friendly error."""
        error_msg = str(e).lower()
        
        if "rate limit" in error_msg or "429" in error_msg:
            return f"🧠 LLM: Rate limit exceeded for {self.llm_provider}. Add your API key."
        elif "quota" in error_msg or "credit" in error_msg:
            return f"🧠 LLM: Credits exhausted for {self.llm_provider}. Add your API key."
        elif "401" in error_msg or "403" in error_msg:
            return f"🧠 LLM: Invalid API key for {self.llm_provider}. Check your credentials."
        else:
            return f"🧠 LLM Error: {str(e)[:100]}"


# Convenience function
async def ask_and_speak(
    question: str,
    system_prompt: str,
    llm_provider: str = "Gemini",
    llm_api_key: Optional[str] = None,
    tts_provider: str = "Edge TTS (Free)",
    tts_api_key: Optional[str] = None,
    tts_voice: Optional[str] = None,
) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Ask a question and get voice response.
    
    Returns:
        Tuple of (response_text, audio_path, error)
    """
    demo = TextToSpeechDemo(
        system_prompt=system_prompt,
        llm_provider=llm_provider,
        llm_api_key=llm_api_key,
        tts_provider=tts_provider,
        tts_api_key=tts_api_key,
        tts_voice=tts_voice,
    )
    return await demo.generate_response(question)
