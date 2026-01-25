"""
Sunona Voice AI - Interactive Demo

A comprehensive demo showcasing Sunona's voice AI capabilities.
Features:
- 3-page flow: Demo Selection → Prompt Config → Demo Interaction
- 4 demo types: Text-to-Text, Text-to-Speech, Speech-to-Speech, Twilio
- Prompt enhancement with AI
- Hands-free voice conversation with VAD
- Graceful error handling with API configuration

Author: Sunona AI Labs
License: MIT
"""

import os
import asyncio
import logging
import time
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
import sys
from pathlib import Path

# Add project root to path for sunona imports
sys.path.append(str(Path(__file__).parent.parent))

import gradio as gr
from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from fastapi.responses import Response
import json
import base64
import httpx
from sunona.helpers.audio_utils import convert_audio_format, mulaw_to_pcm

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class AppConfig:
    """Application configuration."""
    # LLM Providers
    LLM_PROVIDERS: List[str] = None
    # STT Providers
    STT_PROVIDERS: List[str] = None
    # TTS Providers
    TTS_PROVIDERS: List[str] = None
    # Default prompts per demo type
    DEFAULT_PROMPTS: Dict[str, str] = None
    
    def __post_init__(self):
        self.LLM_PROVIDERS = [
            "Gemini",
            "OpenAI GPT",
            "Groq",
            "Anthropic Claude",
        ]
        self.STT_PROVIDERS = [
            "Deepgram",
            "AssemblyAI",
            "Groq Whisper",
            "OpenAI Whisper",
        ]
        self.TTS_PROVIDERS = [
            "Edge TTS (Free)",
            "ElevenLabs",
            "OpenAI TTS",
            "Deepgram Aura",
            "Play.ht",
        ]
        self.DEFAULT_PROMPTS = {
            "text_to_text": (
                "You are Sunona, a helpful AI assistant. When asked your name, always say 'Sunona'. "
                "Be friendly, concise, and informative. Provide accurate information and engage in natural conversation."
            ),
            "text_to_speech": (
                "You are Sunona, a helpful AI assistant. When asked your name, always say 'Sunona'. "
                "Keep your responses brief and clear for voice output. Aim for 1-2 sentences when possible."
            ),
            "speech_to_speech": (
                "You are Sunona, a friendly voice assistant. When asked your name, always say 'Sunona'. "
                "Speak naturally and keep responses short for smooth conversation. Be warm and helpful."
            ),
            "twilio": (
                "You are Sunona, a professional AI phone assistant. When asked your name, always say 'Sunona'. "
                "Be polite, helpful, and courteous. Keep responses conversational and brief."
            ),
        }


config = AppConfig()

# Global storage for call contexts (prompts/config)
# In production, use Redis. For demo, memory is fine.
call_contexts = {}


# ============================================================================
# API CLIENT
# ============================================================================

class APIClient:
    """Handles all API interactions with error handling."""
    
    def __init__(self, user_config: Optional[Dict[str, Any]] = None):
        self.user_config = user_config or {}
        self._load_default_keys()
    
    def _load_default_keys(self):
        """Load API keys from environment."""
        self.llm_key = self.user_config.get("llm_key") or os.getenv("GOOGLE_API_KEY")
        self.stt_key = self.user_config.get("stt_key") or os.getenv("DEEPGRAM_API_KEY")
        self.tts_key = self.user_config.get("tts_key") or os.getenv("ELEVENLABS_API_KEY")
        self.twilio_sid = self.user_config.get("twilio_sid") or os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_token = self.user_config.get("twilio_token") or os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_number = self.user_config.get("twilio_number") or os.getenv("TWILIO_PHONE_NUMBER")
    
    async def get_llm_response(
        self,
        messages: List[Dict[str, str]],
        provider: str = "Groq"
    ) -> Tuple[str, Optional[str]]:
        """Instant fallback LLM response (Groq primary, Gemini secondary)."""
        import httpx
        
        # Priority order for LLMs
        providers = []
        if provider: providers.append(provider)
        
        # Ensure Groq and Gemini are in the list in preferred order
        for fallback in ["Groq", "Gemini", "OpenAI GPT"]:
            if fallback not in providers:
                providers.append(fallback)
            
        last_err = None
        for p in providers:
            try:
                if p == "Gemini":
                    key = self.llm_key or os.getenv("GOOGLE_API_KEY")
                    if not key: continue
                    async with httpx.AsyncClient() as client:
                        # Direct REST call to avoid library version issues
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
                        # Simple message conversion for Gemini
                        prompt = ""
                        for m in messages:
                            role = "User" if m["role"] == "user" else "Assistant"
                            if m["role"] == "system": prompt += f"Instructions: {m['content']}\n"
                            else: prompt += f"{role}: {m['content']}\n"
                        prompt += "Assistant:"
                        
                        resp = await client.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=10.0)
                        if resp.status_code == 200:
                            return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip(), None
                        else: raise Exception(f"Gemini {resp.status_code}")
                
                elif p == "Groq":
                    key = os.getenv("GROQ_API_KEY")
                    if not key: continue
                    async with httpx.AsyncClient() as client:
                        resp = await client.post(
                            "https://api.groq.com/openai/v1/chat/completions",
                            headers={"Authorization": f"Bearer {key}"},
                            json={"model": "llama-3.3-70b-versatile", "messages": messages, "max_tokens": 500},
                            timeout=10.0
                        )
                        if resp.status_code == 200:
                            return resp.json()["choices"][0]["message"]["content"].strip(), None
                        else: raise Exception(f"Groq {resp.status_code}")
            except Exception as e:
                logger.warning(f"LLM Provider {p} failed: {e}")
                last_err = str(e)
                continue
        return "", f"LLM error: {last_err}"
    
    async def transcribe_audio(
        self,
        audio_path: str,
        provider: str = "Deepgram"
    ) -> Tuple[str, Optional[str]]:
        """Instant fallback transcription."""
        import httpx
        
        providers = [provider]
        if "Groq Whisper" not in providers and os.getenv("GROQ_API_KEY"):
            providers.append("Groq Whisper")
            
        last_err = None
        for p in providers:
            try:
                with open(audio_path, "rb") as f:
                    audio_data = f.read()
                
                if p == "Deepgram":
                    key = self.stt_key or os.getenv("DEEPGRAM_API_KEY")
                    if not key: continue
                    async with httpx.AsyncClient() as client:
                        resp = await client.post(
                            "https://api.deepgram.com/v1/listen",
                            headers={"Authorization": f"Token {key}", "Content-Type": "audio/wav"},
                            content=audio_data,
                            params={"model": "nova-2", "smart_format": "true"},
                            timeout=15.0
                        )
                        if resp.status_code == 200:
                            return resp.json()["results"]["channels"][0]["alternatives"][0]["transcript"], None
                        else: raise Exception(f"Deepgram {resp.status_code}")
                
                elif p == "Groq Whisper":
                    key = os.getenv("GROQ_API_KEY")
                    if not key: continue
                    async with httpx.AsyncClient() as client:
                        files = {"file": ("audio.wav", audio_data, "audio/wav")}
                        resp = await client.post(
                            "https://api.groq.com/openai/v1/audio/transcriptions",
                            headers={"Authorization": f"Bearer {key}"},
                            files=files,
                            data={"model": "whisper-large-v3"},
                            timeout=20.0
                        )
                        if resp.status_code == 200:
                            return resp.json().get("text", ""), None
                        else: raise Exception(f"Groq Whisper {resp.status_code}")
            except Exception as e:
                logger.warning(f"STT Provider {p} failed: {e}")
                last_err = str(e)
                continue
        return "", f"STT error: {last_err}"
    
    async def synthesize_speech(
        self,
        text: str,
        provider: str = "Edge TTS (Free)",
        voice_id: Optional[str] = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Synthesize speech with multi-layer fallback.
        Priority: Selected Provider -> ElevenLabs (if key exists) -> OpenAI (if key exists) -> Edge TTS
        """
        import tempfile
        import httpx
        import edge_tts
        
        audio_path = os.path.join(tempfile.gettempdir(), f"sunona_tts_{int(time.time())}.mp3")
        
        # Define priority list for fallbacks
        try_providers = [provider]
        
        # Add fallbacks if not already the primary choice
        if provider != "ElevenLabs" and (self.user_config.get("tts_key") or os.getenv("ELEVENLABS_API_KEY")):
            try_providers.append("ElevenLabs")
        
        if provider != "OpenAI TTS" and (self.user_config.get("openai_key") or os.getenv("OPENAI_API_KEY")):
            try_providers.append("OpenAI TTS")

        if provider != "Play.ht" and (self.user_config.get("playht_key") or os.getenv("PLAYHT_API_KEY")):
            try_providers.append("Play.ht")
            
        if "Edge TTS (Free)" not in try_providers:
            try_providers.append("Edge TTS (Free)")

        errors = []
        
        for p in try_providers:
            try:
                if p == "Edge TTS (Free)":
                    voice = voice_id or os.getenv("EDGE_TTS_VOICE", "en-US-AriaNeural")
                    communicate = edge_tts.Communicate(text, voice)
                    await communicate.save(audio_path)
                    return audio_path, None
                
                elif p == "ElevenLabs":
                    tts_key = self.user_config.get("tts_key") or os.getenv("ELEVENLABS_API_KEY")
                    voice = voice_id or self.user_config.get("tts_voice") or os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")
                    if not tts_key: continue
                    
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            f"https://api.elevenlabs.io/v1/text-to-speech/{voice}",
                            headers={"xi-api-key": tts_key, "Content-Type": "application/json"},
                            json={"text": text, "model_id": "eleven_turbo_v2_5"},
                            timeout=15.0,
                        )
                        if response.status_code == 200:
                            with open(audio_path, "wb") as f:
                                f.write(response.content)
                            return audio_path, None
                        else:
                            errors.append(f"ElevenLabs failed: {response.status_code}")
                
                elif p == "OpenAI TTS":
                    key = self.user_config.get("openai_key") or os.getenv("OPENAI_API_KEY")
                    voice = voice_id or os.getenv("OPENAI_TTS_VOICE", "alloy")
                    if not key: continue
                    
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            "https://api.openai.com/v1/audio/speech",
                            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                            json={"model": "tts-1", "input": text, "voice": voice},
                            timeout=15.0,
                        )
                        if response.status_code == 200:
                            with open(audio_path, "wb") as f:
                                f.write(response.content)
                            return audio_path, None
                        else:
                            errors.append(f"OpenAI TTS failed: {response.status_code}")

                elif p == "Deepgram Aura":
                    key = self.user_config.get("stt_key") or os.getenv("DEEPGRAM_API_KEY") 
                    voice = voice_id or os.getenv("DEEPGRAM_TTS_VOICE", "aura-asteria-en")
                    if not key: continue
                    
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            f"https://api.deepgram.com/v1/speak?model={voice}",
                            headers={"Authorization": f"Token {key}", "Content-Type": "application/json"},
                            json={"text": text},
                            timeout=15.0,
                        )
                        if response.status_code == 200:
                            with open(audio_path, "wb") as f:
                                f.write(response.content)
                            return audio_path, None
                        else:
                            errors.append(f"Deepgram Aura failed: {response.status_code}")

                elif p == "Play.ht":
                    api_key = self.user_config.get("playht_key") or os.getenv("PLAYHT_API_KEY")
                    user_id = self.user_config.get("playht_user_id") or os.getenv("PLAYHT_USER_ID")
                    voice = voice_id or self.user_config.get("playht_voice") or os.getenv("PLAYHT_VOICE_ID")
                    if not all([api_key, user_id, voice]): continue
                    
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            "https://api.play.ht/api/v2/tts",
                            headers={"Authorization": f"Bearer {api_key}", "X-User-Id": user_id, "Content-Type": "application/json"},
                            json={"text": text, "voice": voice, "output_format": "mp3"},
                            timeout=15.0,
                        )
                        if response.status_code == 200:
                            with open(audio_path, "wb") as f:
                                f.write(response.content)
                            return audio_path, None
                        else:
                            errors.append(f"Play.ht failed: {response.status_code}")

            except Exception as e:
                errors.append(f"{p} error: {str(e)}")
                continue
                
        return None, f"🚫 All TTS providers failed. Last errors: {'; '.join(errors[-2:])}"


# ============================================================================
# PROMPT ENHANCER
# ============================================================================

async def enhance_prompt(current_prompt: str, api_client: APIClient) -> Tuple[str, Optional[str]]:
    """
    Use LLM to enhance/improve a system prompt.
    
    Returns:
        Tuple of (enhanced_prompt, error_message)
    """
    messages = [
        {
            "role": "system",
            "content": "You are an expert at writing effective AI system prompts."
        },
        {
            "role": "user",
            "content": f"""Improve this system prompt to make it more effective:

"{current_prompt}"

Requirements:
- Make it more specific and clear
- Add helpful behavior guidelines
- Keep it concise (under 100 words)
- Maintain the original intent

Return ONLY the improved prompt, nothing else."""
        }
    ]
    
    enhanced, error = await api_client.get_llm_response(messages)
    
    if error:
        return current_prompt, error
    
    # Clean up the response
    enhanced = enhanced.strip().strip('"').strip("'")
    return enhanced, None


# ============================================================================
# GRADIO APP
# ============================================================================

def create_demo_app():
    """Create the Gradio demo application."""
    
    # Shared state
    api_client = APIClient()
    
    # Professional CSS styling
    custom_css = """
    /* Global Styles */
    .gradio-container {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Hero Header */
    .hero-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        text-align: center;
        margin-bottom: 0.5rem !important;
    }
    
    .hero-subtitle {
        text-align: center;
        color: #6b7280 !important;
        font-size: 1.1rem !important;
        margin-bottom: 2rem !important;
    }
    
    /* Demo Cards */
    .demo-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 24px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .demo-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        border-color: #a78bfa;
    }
    
    .demo-card h3 {
        color: #1e293b !important;
        font-weight: 700 !important;
        margin-bottom: 8px !important;
    }
    
    /* Buttons */
    .primary-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .primary-btn:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 15px -3px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Page Headers */
    .page-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
    }
    
    /* Status Messages */
    .error-box { 
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); 
        padding: 16px; 
        border-radius: 12px; 
        border: 1px solid #f87171; 
    }
    .success-box { 
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%); 
        padding: 16px; 
        border-radius: 12px; 
        border: 1px solid #4ade80; 
    }
    .info-box {
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #38bdf8;
    }
    
    /* Chat/Conversation */
    .chatbot {
        border-radius: 16px !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    /* Audio Components */
    .audio-component {
        border-radius: 12px !important;
    }
    
    /* Config Page */
    .config-section {
        background: #f8fafc;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #e2e8f0;
    }
    
    /* Footer */
    .footer-text {
        text-align: center;
        color: #9ca3af;
        font-size: 0.875rem;
        margin-top: 2rem;
    }
    """
    
    # Define theme and css for launch
    theme = gr.themes.Soft(
        primary_hue="violet",
        secondary_hue="slate",
        neutral_hue="slate",
        font=("Inter", "system-ui", "sans-serif")
    )
    
    with gr.Blocks(title="Sunona Voice AI") as demo:
        
        # State variables
        user_config = gr.State({})
        current_demo_type = gr.State("")
        current_prompt = gr.State("")
        error_api = gr.State("")  # Which API failed
        chat_history = gr.State([])
        s2s_history = gr.State([])  # Speech-to-Speech conversation history
        
        # ================================================================
        # PAGE 1: DEMO SELECTION
        # ================================================================
        with gr.Column(visible=True) as page_demo_select:
            gr.Markdown(
                """
                <div style="text-align: center; padding: 20px 0;">
                    <a href="https://github.com/sunona-ai-labs/sunona" target="_blank" style="display: inline-block; background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); color: #1f2937; padding: 8px 16px; border-radius: 20px; text-decoration: none; font-weight: 600; font-size: 0.9rem; margin-bottom: 16px;">
                        ⭐ Love it? Star us on GitHub – Help Sunona grow with your support!
                    </a>
                    <h1 style="font-size: 2.5rem; font-weight: 800; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px;">
                        🎙️ Sunona Voice AI
                    </h1>
                    <p style="color: #6b7280; font-size: 1.1rem;">
                        Experience the power of conversational AI with voice
                    </p>
                </div>
                """
            )
            
            gr.Markdown(
                """
                <div style="display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 16px;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#667eea" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
                    <span style="font-size: 1.25rem; font-weight: 700; color: #374151;">Choose Your Demo Experience</span>
                </div>
                """
            )
            
            with gr.Row(equal_height=True):
                with gr.Column(scale=1):
                    gr.Markdown(
                        """
                        <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border-radius: 16px; padding: 24px; border: 1px solid #bae6fd; height: 100%;">
                            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#0369a1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                                <h3 style="margin: 0; color: #0369a1; font-weight: 700;">Text-to-Text</h3>
                            </div>
                            <p style="color: #64748b; margin: 0 0 12px 0;">Chat with Sunona using text messages</p>
                            <p style="color: #94a3b8; font-size: 0.85rem; margin: 0;"><strong>Pipeline:</strong> Text → LLM → Text</p>
                        </div>
                        """
                    )
                    btn_demo_t2t = gr.Button("→ Start Chat", variant="primary", size="lg")
                
                with gr.Column(scale=1):
                    gr.Markdown(
                        """
                        <div style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border-radius: 16px; padding: 24px; border: 1px solid #86efac; height: 100%;">
                            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#15803d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path><path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path></svg>
                                <h3 style="margin: 0; color: #15803d; font-weight: 700;">Text-to-Speech</h3>
                            </div>
                            <p style="color: #64748b; margin: 0 0 12px 0;">Type your question, hear Sunona's voice</p>
                            <p style="color: #94a3b8; font-size: 0.85rem; margin: 0;"><strong>Pipeline:</strong> Text → LLM → TTS → Audio</p>
                        </div>
                        """
                    )
                    btn_demo_t2s = gr.Button("→ Start Voice", variant="primary", size="lg")
            
            with gr.Row(equal_height=True):
                with gr.Column(scale=1):
                    gr.Markdown(
                        """
                        <div style="background: linear-gradient(135deg, #fdf4ff 0%, #fae8ff 100%); border-radius: 16px; padding: 24px; border: 1px solid #e879f9; height: 100%;">
                            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#a21caf" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>
                                <h3 style="margin: 0; color: #a21caf; font-weight: 700;">Speech-to-Speech</h3>
                            </div>
                            <p style="color: #64748b; margin: 0 0 12px 0;">Full voice conversation with Sunona</p>
                            <p style="color: #94a3b8; font-size: 0.85rem; margin: 0;"><strong>Pipeline:</strong> Audio → STT → LLM → TTS → Audio</p>
                        </div>
                        """
                    )
                    btn_demo_s2s = gr.Button("→ Start Conversation", variant="primary", size="lg")
                
                with gr.Column(scale=1):
                    gr.Markdown(
                        """
                        <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-radius: 16px; padding: 24px; border: 1px solid #fbbf24; height: 100%;">
                            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#b45309" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
                                <h3 style="margin: 0; color: #b45309; font-weight: 700;">Phone Call</h3>
                            </div>
                            <p style="color: #64748b; margin: 0 0 12px 0;">Sunona calls you on your phone</p>
                            <p style="color: #374151; font-size: 0.85rem; margin: 0;"><strong>Requires:</strong> Twilio credentials</p>
                        </div>
                        """
                    )
                    btn_demo_twilio = gr.Button("→ Start Call", variant="primary", size="lg")
            
            gr.Markdown("---")
            
            with gr.Row():
                btn_goto_config = gr.Button("⚙ Configure API Keys", variant="secondary")
            
            gr.Markdown(
                """
                <div style="text-align: center; margin-top: 24px; padding: 20px; background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border-radius: 12px; border: 1px solid #e2e8f0;">
                    <p style="margin: 0 0 12px 0; color: #374151; font-size: 0.95rem;">
                        ⭐ <strong>Love Sunona?</strong> Star us on GitHub and contribute!
                    </p>
                    <a href="https://github.com/sunona-ai-labs/sunona" target="_blank" style="display: inline-block; background: linear-gradient(135deg, #1f2937 0%, #374151 100%); color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: 600; margin: 0 8px;">
                        ⭐ Star on GitHub
                    </a>
                    <a href="https://github.com/sunona-ai-labs/sunona/blob/master/CONTRIBUTING.md" target="_blank" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: 600; margin: 0 8px;">
                        🤝 Contribute
                    </a>
                </div>
                <div style="text-align: center; color: #9ca3af; font-size: 0.85rem; margin-top: 16px;">
                    <p>Built with ❤️ by <strong>Sunona AI Labs</strong></p>
                </div>
                """
            )
        
        # ================================================================
        # PAGE 2: PROMPT CONFIGURATION
        # ================================================================
        with gr.Column(visible=False) as page_prompt_config:
            gr.Markdown(
                """
                <h2 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px;">
                    ✨ Configure Your Experience
                </h2>
                """
            )
            prompt_title = gr.Markdown("### Setting up your demo...")
            
            with gr.Row():
                btn_back_to_select = gr.Button("← Back", variant="secondary", size="sm")
            
            gr.Markdown(
                """
                <div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border-radius: 12px; padding: 16px; border: 1px solid #e2e8f0; margin: 16px 0;">
                    <h4 style="margin: 0 0 8px 0; color: #334155;">🎭 System Prompt</h4>
                    <p style="margin: 0; color: #64748b; font-size: 0.9rem;">Customize how Sunona behaves and responds. The AI will follow these instructions.</p>
                </div>
                """
            )
            
            prompt_input = gr.Textbox(
                label="",
                lines=6,
                placeholder="Enter your system prompt here...\n\nExample: You are Sunona, a helpful AI assistant. Be friendly and concise.",
                show_label=False
            )
            
            with gr.Row():
                btn_enhance = gr.Button("✨ Enhance with AI", variant="secondary")
                enhance_status = gr.Markdown("")
            
            gr.Markdown("")
            btn_continue_to_demo = gr.Button("🚀 Continue to Demo →", variant="primary", size="lg")
        
        # ================================================================
        # PAGE 3a: TEXT-TO-TEXT DEMO
        # ================================================================
        with gr.Column(visible=False) as page_text_to_text:
            gr.Markdown(
                """
                <div style="display: flex; align-items: center; gap: 12px;">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#0369a1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                    <h1 style="margin: 0; background: linear-gradient(135deg, #0369a1 0%, #0284c7 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                        Chat with Sunona
                    </h1>
                </div>
                """
            )
            with gr.Row():
                btn_t2t_edit = gr.Button("← Edit Prompt", size="sm", variant="secondary")
                btn_t2t_home = gr.Button("⌂ Home", size="sm", variant="secondary")
            
            chatbot_t2t = gr.Chatbot(height=450, show_label=False)
            
            with gr.Row():
                msg_t2t = gr.Textbox(
                    label="",
                    placeholder="Type your message and press Enter...",
                    scale=5,
                    show_label=False
                )
                btn_send_t2t = gr.Button("Send →", variant="primary", scale=1)
            
            t2t_error = gr.Markdown("", visible=False)
        
        # ================================================================
        # PAGE 3b: TEXT-TO-SPEECH DEMO
        # ================================================================
        with gr.Column(visible=False) as page_text_to_speech:
            gr.Markdown(
                """
                <h1 style="background: linear-gradient(135deg, #15803d 0%, #22c55e 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    🔊 Text-to-Speech
                </h1>
                """
            )
            with gr.Row():
                btn_t2s_edit = gr.Button("← Edit Prompt", size="sm", variant="secondary")
                btn_t2s_home = gr.Button("🏠 Home", size="sm", variant="secondary")
            
            gr.Markdown(
                """
                <div style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border-radius: 12px; padding: 16px; border: 1px solid #86efac; margin: 12px 0;">
                    <p style="margin: 0; color: #166534;">💡 Type your question below and hear Sunona respond with voice!</p>
                </div>
                """
            )
            
            with gr.Row():
                question_t2s = gr.Textbox(
                    label="",
                    placeholder="Type your question and press Enter...",
                    lines=2,
                    scale=5,
                    show_label=False
                )
                btn_speak_t2s = gr.Button("🔊 Speak", variant="primary", scale=1)
            
            with gr.Row():
                with gr.Column():
                    response_text_t2s = gr.Textbox(label="📝 Sunona's Response", interactive=False, lines=3)
                with gr.Column():
                    response_audio_t2s = gr.Audio(label="🔊 Voice", type="filepath", autoplay=True)
            
            t2s_error = gr.Markdown("", visible=False)
        
        # ================================================================
        # PAGE 3c: SPEECH-TO-SPEECH DEMO
        # ================================================================
        with gr.Column(visible=False) as page_speech_to_speech:
            gr.Markdown(
                """
                <h1 style="background: linear-gradient(135deg, #a21caf 0%, #d946ef 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    🎙️ Voice Conversation
                </h1>
                """
            )
            with gr.Row():
                btn_s2s_edit = gr.Button("← Edit Prompt", size="sm", variant="secondary")
                btn_s2s_home = gr.Button("🏠 Home", size="sm", variant="secondary")
            
            gr.Markdown(
                """
                <div style="background: linear-gradient(135deg, #fdf4ff 0%, #fae8ff 100%); border-radius: 12px; padding: 16px; border: 1px solid #e879f9; margin: 12px 0;">
                    <p style="margin: 0 0 8px 0; color: #86198f;"><strong>🎤 Record your voice</strong> using the microphone, then hear Sunona respond!</p>
                    <p style="margin: 0; color: #a855f7; font-size: 0.85rem;">💡 Want TRUE hands-free? Run: <code>python demo/hands_free_assistant.py</code></p>
                </div>
                """
            )
            
            s2s_status = gr.Markdown("**Status:** 🟢 Ready to record")
            
            audio_input_s2s = gr.Audio(
                sources=["microphone"],
                type="filepath",
                label="🎤 Click to Record"
            )
            
            with gr.Row():
                with gr.Column():
                    transcript_s2s = gr.Textbox(label="📝 You said", interactive=False, lines=2)
                with gr.Column():
                    response_text_s2s = gr.Textbox(label="🤖 Sunona says", interactive=False, lines=2)
            
            response_audio_s2s = gr.Audio(label="🔊 AI Voice", type="filepath", autoplay=True)
            
            s2s_error = gr.Markdown("", visible=False)
            
            # Conversation history display
            conversation_display_s2s = gr.Chatbot(
                label="💬 Conversation History",
                height=200
            )
        
        # ================================================================
        # PAGE 3d: TWILIO DEMO
        # ================================================================
        with gr.Column(visible=False) as page_twilio:
            gr.Markdown("# 📞 Twilio Phone Call Demo")
            with gr.Row():
                btn_twilio_edit = gr.Button("← Edit Prompt", size="sm")
                btn_twilio_home = gr.Button("← Demo Selection", size="sm")
            
            twilio_warning = gr.Markdown("", visible=False)
            
            gr.Markdown("*Enter a phone number and our AI will call you*")
            
            phone_input = gr.Textbox(
                label="Phone Number to Call",
                placeholder="+1234567890",
                info="Enter with country code (e.g., +1 for US)"
            )
            btn_call = gr.Button("📞 Call Me", variant="primary", size="lg")
            call_status = gr.Textbox(label="Status", interactive=False)
            
            twilio_error = gr.Markdown("", visible=False)
        
        # ================================================================
        # CONFIG PAGE: API KEYS
        # ================================================================
        with gr.Column(visible=False) as page_config:
            gr.Markdown("# ⚙️ Configure API Keys")
            config_error_msg = gr.Markdown("", visible=False)
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### 🧠 LLM (AI Brain)")
                    llm_provider = gr.Dropdown(
                        label="Provider",
                        choices=config.LLM_PROVIDERS,
                        value="Gemini"
                    )
                    llm_key_input = gr.Textbox(
                        label="API Key",
                        type="password",
                        placeholder="Your LLM API key"
                    )
                    gr.Markdown("[Get Gemini Key](https://aistudio.google.com/app/apikey)")
                
                with gr.Column():
                    gr.Markdown("#### 🎤 STT (Speech-to-Text)")
                    stt_provider = gr.Dropdown(
                        label="Provider",
                        choices=config.STT_PROVIDERS,
                        value="Deepgram"
                    )
                    stt_key_input = gr.Textbox(
                        label="API Key",
                        type="password",
                        placeholder="Your STT API key"
                    )
                    gr.Markdown("[Get Deepgram Key](https://console.deepgram.com/)")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### 🔊 TTS (Text-to-Speech)")
                    tts_provider = gr.Dropdown(
                        label="Provider",
                        choices=config.TTS_PROVIDERS,
                        value="Edge TTS (Free)"
                    )
                    tts_key_input = gr.Textbox(
                        label="API Key",
                        type="password",
                        placeholder="Not needed for Edge TTS",
                        visible=True
                    )
                    tts_voice_input = gr.Textbox(
                        label="Voice ID (optional)",
                        placeholder="e.g., EXAVITQu4vr4xnSDxMaL"
                    )
                    gr.Markdown("Edge TTS is FREE - no key needed!")
                
                with gr.Column():
                    gr.Markdown("#### 📞 Twilio (Phone Calls)")
                    twilio_sid_input = gr.Textbox(
                        label="Account SID",
                        type="password",
                        placeholder="ACxxxxxxxxxx"
                    )
                    twilio_token_input = gr.Textbox(
                        label="Auth Token",
                        type="password"
                    )
                    twilio_number_input = gr.Textbox(
                        label="Phone Number",
                        placeholder="+1234567890"
                    )
                    gr.Markdown("[Get Twilio Credentials](https://twilio.com/console)")
            
            gr.Markdown("---")
            btn_save_config = gr.Button("💾 Save & Return to Demo", variant="primary", size="lg")
        
        # ================================================================
        # NAVIGATION FUNCTIONS
        # ================================================================
        
        def go_to_prompt_config(demo_type: str):
            """Navigate to prompt configuration page."""
            prompt = config.DEFAULT_PROMPTS.get(demo_type, "")
            title = demo_type.replace("_", " ").title()
            return (
                demo_type,
                prompt,
                gr.update(value=prompt),
                gr.update(value=f"### Configure {title} Demo"),
                gr.update(visible=False),
                gr.update(visible=True),
            )
        
        def go_to_demo(demo_type: str, prompt: str, cfg: dict):
            """Navigate to the appropriate demo page."""
            # Update API client with user config
            nonlocal api_client
            api_client = APIClient(cfg)
            
            # Hide all pages first
            updates = {
                page_prompt_config: gr.update(visible=False),
                page_text_to_text: gr.update(visible=False),
                page_text_to_speech: gr.update(visible=False),
                page_speech_to_speech: gr.update(visible=False),
                page_twilio: gr.update(visible=False),
            }
            
            # Show the appropriate demo page
            if demo_type == "text_to_text":
                updates[page_text_to_text] = gr.update(visible=True)
            elif demo_type == "text_to_speech":
                updates[page_text_to_speech] = gr.update(visible=True)
            elif demo_type == "speech_to_speech":
                updates[page_speech_to_speech] = gr.update(visible=True)
            elif demo_type == "twilio":
                updates[page_twilio] = gr.update(visible=True)
            
            return tuple(updates.values())
        
        def go_to_config(error_api_name: str = ""):
            """Navigate to config page, optionally highlighting failed API."""
            error_msg = ""
            if error_api_name:
                error_msg = f"⚠️ **{error_api_name}** needs configuration. Enter your API key below."
            
            return (
                gr.update(visible=False),  # Hide current page
                gr.update(visible=True),   # Show config
                gr.update(value=error_msg, visible=bool(error_msg)),
            )
        
        def save_config_and_return(
            llm_prov, llm_key, stt_prov, stt_key,
            tts_prov, tts_key, tts_voice,
            t_sid, t_token, t_num
        ):
            """Save configuration and return to demo selection."""
            new_config = {
                "llm_provider": llm_prov,
                "llm_key": llm_key,
                "stt_provider": stt_prov,
                "stt_key": stt_key,
                "tts_provider": tts_prov,
                "tts_key": tts_key,
                "tts_voice": tts_voice,
                "twilio_sid": t_sid,
                "twilio_token": t_token,
                "twilio_number": t_num,
            }
            return (
                new_config,
                gr.update(visible=True),   # Show demo select
                gr.update(visible=False),  # Hide config
            )
        
        # ================================================================
        # DEMO FUNCTIONS
        # ================================================================
        
        async def do_enhance_prompt(prompt: str, cfg: dict):
            """Enhance prompt using AI."""
            client = APIClient(cfg)
            enhanced, error = await enhance_prompt(prompt, client)
            
            if error:
                return prompt, f"⚠️ {error}"
            return enhanced, "✅ Prompt enhanced!"
        
        async def do_text_to_text(
            message: str,
            history: List[Dict],
            prompt: str,
            cfg: dict
        ):
            """Process text-to-text chat."""
            if not message.strip():
                return history, "", gr.update(visible=False)
            
            client = APIClient(cfg)
            
            # Build messages
            messages = [{"role": "system", "content": prompt}]
            for h in history:
                messages.append(h)
            messages.append({"role": "user", "content": message})
            
            response, error = await client.get_llm_response(messages)
            
            if error:
                return history, "", gr.update(value=error, visible=True)
            
            # Update history
            new_history = history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": response}
            ]
            
            return new_history, "", gr.update(visible=False)
        
        async def do_text_to_speech(question: str, prompt: str, cfg: dict):
            """Process text-to-speech."""
            if not question.strip():
                return "", None, gr.update(visible=False)
            
            client = APIClient(cfg)
            
            # Get LLM response
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": question}
            ]
            response, error = await client.get_llm_response(messages)
            
            if error:
                return "", None, gr.update(value=error, visible=True)
            
            # Synthesize speech
            tts_provider = cfg.get("tts_provider", "Edge TTS (Free)")
            tts_voice = cfg.get("tts_voice")
            audio_path, tts_error = await client.synthesize_speech(response, tts_provider, tts_voice)
            
            if tts_error:
                return response, None, gr.update(value=tts_error, visible=True)
            
            return response, audio_path, gr.update(visible=False)
        
        async def do_speech_to_speech(audio_path: str, prompt: str, cfg: dict, history: list):
            """Process speech-to-speech with conversation history."""
            if not audio_path:
                return "", "", None, gr.update(visible=False), history or [], "**Status:** Waiting for speech..."
            
            client = APIClient(cfg)
            history = history or []
            
            # Transcribe
            stt_provider = cfg.get("stt_provider", "Deepgram")
            transcript, stt_error = await client.transcribe_audio(audio_path, stt_provider)
            
            if stt_error:
                return "", "", None, gr.update(value=stt_error, visible=True), history, f"**Status:** ⚠️ {stt_error}"
            
            if not transcript.strip():
                return "", "", None, gr.update(visible=False), history, "**Status:** No speech detected. Try again..."
            
            # Build messages with history
            messages = [{"role": "system", "content": prompt}]
            for msg in history:
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": transcript})
            
            # Get LLM response
            response, llm_error = await client.get_llm_response(messages)
            
            if llm_error:
                return transcript, "", None, gr.update(value=llm_error, visible=True), history, f"**Status:** ⚠️ {llm_error}"
            
            # Update history
            new_history = history + [
                {"role": "user", "content": transcript},
                {"role": "assistant", "content": response}
            ]
            
            # Synthesize speech
            tts_provider = cfg.get("tts_provider", "Edge TTS (Free)")
            tts_voice = cfg.get("tts_voice")
            audio_out, tts_error = await client.synthesize_speech(response, tts_provider, tts_voice)
            
            if tts_error:
                return transcript, response, None, gr.update(value=tts_error, visible=True), new_history, f"**Status:** ⚠️ {tts_error}"
            
            return transcript, response, audio_out, gr.update(visible=False), new_history, "**Status:** ✅ Response ready! Speak again to continue..."
        
        async def do_twilio_call(phone: str, prompt: str, cfg: dict, gr_request: gr.Request):
            """Initiate Twilio call with real-time streaming."""
            if not phone.strip():
                return "Please enter a phone number."
            
            # Normalize phone number
            phone = phone.strip()
            if not phone.startswith("+"):
                phone = "+" + phone
            
            twilio_sid = cfg.get("twilio_sid") or os.getenv("TWILIO_ACCOUNT_SID")
            twilio_token = cfg.get("twilio_token") or os.getenv("TWILIO_AUTH_TOKEN")
            twilio_number = cfg.get("twilio_number") or os.getenv("TWILIO_PHONE_NUMBER")
            
            if not all([twilio_sid, twilio_token, twilio_number]):
                return "⚠️ Twilio credentials not configured. Go to ⚙️ Configure API Keys."
            
            try:
                from twilio.rest import Client
                
                # Store context for the stream
                session_id = f"sess_{int(time.time())}"
                call_contexts[session_id] = {
                    "prompt": prompt,
                    "cfg": cfg
                }
                
                client = Client(twilio_sid, twilio_token)
                
                # Determine webhook URL
                # If NGROK is running or TWILIO_WEBHOOK_URL is set, use it.
                # Otherwise try to guess from the Gradio request.
                webhook_url = os.getenv("TWILIO_WEBHOOK_URL", "")
                if not webhook_url:
                    # Attempt to derive from the current request URL
                    base_url = str(gr_request.request.base_url).rstrip("/")
                    webhook_url = f"{base_url}/voice"
                elif not webhook_url.endswith("/voice"):
                    # Ensure it ends with /voice
                    webhook_url = f"{webhook_url.rstrip('/')}/voice"
                
                # Append session_id
                final_webhook_url = f"{webhook_url}?session_id={session_id}"
                
                # Make the call using our webhook URL
                call = client.calls.create(
                    to=phone,
                    from_=twilio_number,
                    url=final_webhook_url,
                    method="POST"
                )
                
                return f"✅ Real-time call initiated! (ID: {call.sid[:10]})\nAnswer your phone and press any key to start talking."
                
            except Exception as e:
                error_msg = str(e)
                if "unverified" in error_msg.lower():
                    return f"⚠️ Phone number {phone} is not verified. Add it in Twilio console (trial account limitation)."
                else:
                    return f"⚠️ Twilio Error: {error_msg[:150]}"
        
        # ================================================================
        # WIRE UP EVENTS
        # ================================================================
        
        # Demo selection → Prompt config
        btn_demo_t2t.click(
            lambda: go_to_prompt_config("text_to_text"),
            outputs=[current_demo_type, current_prompt, prompt_input, prompt_title, page_demo_select, page_prompt_config]
        )
        btn_demo_t2s.click(
            lambda: go_to_prompt_config("text_to_speech"),
            outputs=[current_demo_type, current_prompt, prompt_input, prompt_title, page_demo_select, page_prompt_config]
        )
        btn_demo_s2s.click(
            lambda: go_to_prompt_config("speech_to_speech"),
            outputs=[current_demo_type, current_prompt, prompt_input, prompt_title, page_demo_select, page_prompt_config]
        )
        btn_demo_twilio.click(
            lambda: go_to_prompt_config("twilio"),
            outputs=[current_demo_type, current_prompt, prompt_input, prompt_title, page_demo_select, page_prompt_config]
        )
        
        # Config button from demo select
        btn_goto_config.click(
            lambda: (gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)),
            outputs=[page_demo_select, page_config, config_error_msg]
        )
        
        # Back to demo select from prompt config
        btn_back_to_select.click(
            lambda: (gr.update(visible=True), gr.update(visible=False)),
            outputs=[page_demo_select, page_prompt_config]
        )
        
        # Enhance prompt
        btn_enhance.click(
            do_enhance_prompt,
            inputs=[prompt_input, user_config],
            outputs=[prompt_input, enhance_status]
        )
        
        # Continue to demo from prompt config
        btn_continue_to_demo.click(
            go_to_demo,
            inputs=[current_demo_type, prompt_input, user_config],
            outputs=[page_prompt_config, page_text_to_text, page_text_to_speech, page_speech_to_speech, page_twilio]
        )
        
        # Save config
        btn_save_config.click(
            save_config_and_return,
            inputs=[
                llm_provider, llm_key_input, stt_provider, stt_key_input,
                tts_provider, tts_key_input, tts_voice_input,
                twilio_sid_input, twilio_token_input, twilio_number_input
            ],
            outputs=[user_config, page_demo_select, page_config]
        )
        
        # Text-to-Text demo
        btn_send_t2t.click(
            do_text_to_text,
            inputs=[msg_t2t, chat_history, current_prompt, user_config],
            outputs=[chatbot_t2t, msg_t2t, t2t_error]
        )
        msg_t2t.submit(
            do_text_to_text,
            inputs=[msg_t2t, chat_history, current_prompt, user_config],
            outputs=[chatbot_t2t, msg_t2t, t2t_error]
        )
        
        # Text-to-Speech demo - Enter key
        question_t2s.submit(
            do_text_to_speech,
            inputs=[question_t2s, current_prompt, user_config],
            outputs=[response_text_t2s, response_audio_t2s, t2s_error]
        ).then(
            lambda: "",
            outputs=[question_t2s]
        )
        
        # Text-to-Speech demo - Button click
        btn_speak_t2s.click(
            do_text_to_speech,
            inputs=[question_t2s, current_prompt, user_config],
            outputs=[response_text_t2s, response_audio_t2s, t2s_error]
        ).then(
            lambda: "",
            outputs=[question_t2s]
        )
        
        # Speech-to-Speech demo - auto process when recording stops
        audio_input_s2s.stop_recording(
            do_speech_to_speech,
            inputs=[audio_input_s2s, current_prompt, user_config, s2s_history],
            outputs=[transcript_s2s, response_text_s2s, response_audio_s2s, s2s_error, conversation_display_s2s, s2s_status]
        )
        
        # Twilio demo
        btn_call.click(
            do_twilio_call,
            inputs=[phone_input, current_prompt, user_config],
            outputs=[call_status]
        )
        
        # Back/Home buttons for demos
        for btn, page in [
            (btn_t2t_edit, page_text_to_text),
            (btn_t2s_edit, page_text_to_speech),
            (btn_s2s_edit, page_speech_to_speech),
            (btn_twilio_edit, page_twilio),
        ]:
            btn.click(
                lambda: (gr.update(visible=False), gr.update(visible=True)),
                outputs=[page, page_prompt_config]
            )
        
        for btn, page in [
            (btn_t2t_home, page_text_to_text),
            (btn_t2s_home, page_text_to_speech),
            (btn_s2s_home, page_speech_to_speech),
            (btn_twilio_home, page_twilio),
        ]:
            btn.click(
                lambda: (gr.update(visible=False), gr.update(visible=True)),
                outputs=[page, page_demo_select]
            )
    
    return demo


# ============================================================================
# FASTAPI WRAPPER FOR REAL-TIME STREAMING
# ============================================================================

fastapi_app = FastAPI()

@fastapi_app.get("/health")
async def health_check():
    return {"status": "ok"}

@fastapi_app.post("/voice")
async def voice_endpoint(request: Request):
    """Twilio Webhook endpoint with detailed logging."""
    try:
        session_id = request.query_params.get("session_id")
        logger.info(f"Incoming call webhook. Session: {session_id}")
        
        # Determine host and protocol
        # Render specific: check x-forwarded headers
        host = request.headers.get("x-forwarded-host") or request.headers.get("host")
        protocol = "wss" if ".onrender.com" in host or request.headers.get("x-forwarded-proto") == "https" else "ws"
        
        # Override with env var if available
        env_url = os.getenv("TWILIO_WEBHOOK_URL", "")
        if env_url:
            from urllib.parse import urlparse
            parsed = urlparse(env_url)
            if parsed.netloc:
                host = parsed.netloc
        
        ws_url = f"{protocol}://{host}/media"
        if session_id:
            ws_url = f"{ws_url}?session_id={session_id}"
            
        logger.info(f"Connecting Twilio Stream to: {ws_url}")
        
        # Simplified TwiML for maximum compatibility
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Connecting to Sunona AI...</Say>
    <Connect>
        <Stream url="{ws_url}" />
    </Connect>
    <Pause length="30"/>
</Response>"""
        return Response(content=twiml, media_type="text/xml")
    except Exception as e:
        logger.error(f"CRITICAL ERROR in voice_endpoint: {e}", exc_info=True)
        return Response(content="<Response><Say>Internal server error</Say></Response>", media_type="text/xml")

@fastapi_app.websocket("/media")
async def media_stream(websocket: WebSocket):
    """Twilio Media Stream with Interruption Handling and HD Pacing."""
    await websocket.accept()
    logger.info("Twilio WebSocket connected")
    
    session_id = websocket.query_params.get("session_id")
    context = call_contexts.get(session_id, {"prompt": "Be a helpful assistant.", "cfg": {}})
    
    api_client = APIClient(context["cfg"])
    history = []
    audio_buffer = bytearray()
    stream_sid = None
    
    # State tracking
    from sunona.vad.silero_vad import SimpleVAD
    vad = SimpleVAD(threshold=0.04)
    user_is_speaking = False
    silence_start = None
    speech_start_time = 0
    active_ai_task = None
    last_ai_speech_time = 0 

    async def cancel_ai_speech():
        """Cancel current AI response and clear Twilio buffer."""
        nonlocal active_ai_task
        if active_ai_task and not active_ai_task.done():
            logger.info("Interruption detected: Stopping AI speech")
            active_ai_task.cancel()
            if stream_sid:
                try:
                    # Send clear command to Twilio to stop playback immediately
                    await websocket.send_text(json.dumps({"event": "clear", "streamSid": stream_sid}))
                except: pass
            active_ai_task = None

    async def send_to_twilio(audio_mulaw, sid):
        """High-precision pacer with Jitter Buffer (320ms)."""
        if not sid: return
        import time
        
        chunk_size = 160 # 20ms
        sent_chunks = 0
        
        # 1. Jitter Buffer Pre-fill (first 16 chunks / 320ms)
        # This prevents "scattered" sound due to network jitter.
        prefill_count = 16
        for i in range(0, min(len(audio_mulaw), chunk_size * prefill_count), chunk_size):
            chunk = audio_mulaw[i:i + chunk_size]
            msg = {"event": "media", "streamSid": sid, "media": {"payload": base64.b64encode(chunk).decode()}}
            await websocket.send_text(json.dumps(msg))
            sent_chunks += 1

        # 2. Paced delivery for the rest
        start_time = time.perf_counter()
        for i in range(sent_chunks * chunk_size, len(audio_mulaw), chunk_size):
            chunk = audio_mulaw[i:i + chunk_size]
            if len(chunk) < chunk_size: break
            
            msg = {"event": "media", "streamSid": sid, "media": {"payload": base64.b64encode(chunk).decode()}}
            try:
                # Check if socket is still open
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_text(json.dumps(msg))
                    sent_chunks += 1
                else:
                    break
            except Exception as e:
                logger.warning(f"Failed to send media chunk to Twilio: {e}")
                break
            
            # Target time for this chunk (0.02s per chunk)
            # Aggressive catch-up for weak server (Render Free)
            target_time = start_time + ((sent_chunks - prefill_count) * 0.02)
            delay = target_time - time.perf_counter()
            
            if delay > 0:
                await asyncio.sleep(delay)
            elif delay < -0.1: # If late by >100ms, reset start_time to catch up
                start_time = time.perf_counter() - ((sent_chunks - prefill_count) * 0.02)

    async def handle_interaction(audio_data, sid):
        """Processes user voice and speaks back."""
        import tempfile
        path = None
        try:
            # 1. Save and Upsample to 16kHz for better STT
            from pydub import AudioSegment
            audio = AudioSegment(audio_data, frame_rate=8000, sample_width=2, channels=1)
            audio = audio.set_frame_rate(16000)
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
                audio.export(tf.name, format="wav")
                path = tf.name
            
            # 2. Transcribe
            transcript, err = await api_client.transcribe_audio(path, "Deepgram")
            if path: 
                try: os.unlink(path)
                except: pass
            
            if not transcript or len(transcript.strip()) < 2: return
            logger.info(f"User: {transcript}")
            history.append({"role": "user", "content": transcript})
            
            # 3. LLM Response
            # Add strict brevity instructions for phone calls
            base_prompt = context.get("prompt", "You are Sunona AI.")
            prompt = f"{base_prompt}\n\nCONVERSATIONAL RULES:\n1. Keep responses extremely brief (1-2 short sentences max).\n2. Be ultra-natural and conversational.\n3. Do not use lists or markdown formatting."
            
            messages = [{"role": "system", "content": prompt}] + history[-5:]
            resp, err = await api_client.get_llm_response(messages)
            if not resp: return
            
            logger.info(f"AI: {resp}")
            history.append({"role": "assistant", "content": resp})
            
            # 4. Synthesize (ElevenLabs primary, Edge TTS fallback)
            tts_path, err = await api_client.synthesize_speech(resp, "ElevenLabs")
            if tts_path:
                try:
                    from pydub import AudioSegment, effects
                    logger.info(f"Preparing AI voice from {tts_path}")
                    # Normalizing for clear, crackle-free audio
                    audio = AudioSegment.from_file(tts_path)
                    audio = effects.normalize(audio, headroom=3.0) # -3dB peak
                    audio = audio.set_frame_rate(8000).set_channels(1).set_sample_width(2)
                    
                    from sunona.helpers.audio_utils import pcm_to_mulaw
                    mulaw_data = pcm_to_mulaw(audio.raw_data)
                    
                    nonlocal last_ai_speech_time
                    await send_to_twilio(mulaw_data, sid)
                    import time
                    last_ai_speech_time = time.time() # Start echo cooldown
                finally:
                    try: os.unlink(tts_path)
                    except: pass
        except asyncio.CancelledError:
            logger.info("Response task cancelled due to interruption")
        except Exception as ex:
            logger.error(f"Interaction error: {ex}")

    try:
        async for message in websocket.iter_text():
            packet = json.loads(message)
            event = packet.get("event")
            
            if event == "start":
                stream_sid = packet.get("start", {}).get("streamSid")
                # Initial greeting
                async def greet():
                    nonlocal active_ai_task
                    await asyncio.sleep(0.5)
                    path, err = await api_client.synthesize_speech("Hello! This is Sunona. How can I help you?", "ElevenLabs")
                    if path:
                        try:
                            from pydub import AudioSegment
                            audio = AudioSegment.from_file(path).set_frame_rate(8000).set_channels(1).set_sample_width(2)
                            from sunona.helpers.audio_utils import pcm_to_mulaw
                            await send_to_twilio(pcm_to_mulaw(audio.raw_data), stream_sid)
                        finally:
                            try: os.unlink(path)
                            except: pass
                active_ai_task = asyncio.create_task(greet())
                
            elif event == "media":
                payload = packet.get("media", {}).get("payload")
                if payload:
                    import time
                    cur_now = time.time()
                    # Echo suppression cooldown (ignore speech for 600ms after AI finishes)
                    if cur_now - last_ai_speech_time < 0.6:
                        continue
                        
                    chunk_pcm = mulaw_to_pcm(base64.b64decode(payload))
                    is_speech = await vad.process(chunk_pcm)
                    
                    if is_speech:
                        if not user_is_speaking:
                            logger.info("VAD: User started speaking")
                            await cancel_ai_speech()
                            user_is_speaking = True
                            speech_start_time = cur_now
                            
                        silence_start = None
                        audio_buffer.extend(chunk_pcm)
                        
                        # Safety: If user speaks for > 6s, force process (prevents noise lockup)
                        if cur_now - speech_start_time > 6.0:
                            logger.info("VAD: Max speech duration reached, triggering AI")
                            user_is_speaking = False
                            data = bytes(audio_buffer)
                            audio_buffer.clear()
                            active_ai_task = asyncio.create_task(handle_interaction(data, stream_sid))
                            
                    elif user_is_speaking:
                        if silence_start is None: silence_start = cur_now
                        
                        # Wait for 0.8s of silence
                        if cur_now - silence_start > 0.8:
                            logger.info("VAD: User finished speaking")
                            user_is_speaking = False
                            data = bytes(audio_buffer)
                            audio_buffer.clear()
                            silence_start = None
                            active_ai_task = asyncio.create_task(handle_interaction(data, stream_sid))
            
            elif event == "stop": break
    except Exception as e:
        logger.error(f"WebSocket Loop Error: {e}")
    finally:
        logger.info("Twilio WebSocket disconnecting")
        await cancel_ai_speech()

# Mount Gradio on FastAPI
demo_app = create_demo_app()
app = gr.mount_gradio_app(fastapi_app, demo_app, path="/")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Support standard PORT (Render/Heroku) and DEMO_PORT
    port = int(os.getenv("PORT") or os.getenv("DEMO_PORT") or 7860)
    
    logger.info(f"Starting Sunona Demo + Twilio Stream on port {port}")
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
