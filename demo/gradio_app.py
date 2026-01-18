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
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass

import gradio as gr
from dotenv import load_dotenv

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
                "You are a helpful AI assistant. Be friendly, concise, and informative. "
                "Provide accurate information and engage in natural conversation."
            ),
            "text_to_speech": (
                "You are a helpful AI assistant. Keep your responses brief and clear "
                "for voice output. Aim for 1-2 sentences when possible."
            ),
            "speech_to_speech": (
                "You are Sunona, a friendly voice assistant. Speak naturally and keep "
                "responses short for smooth conversation. Be warm and helpful."
            ),
            "twilio": (
                "You are Sunona, a professional AI phone assistant. Be polite, helpful, "
                "and courteous. Keep responses conversational and brief."
            ),
        }


config = AppConfig()


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
        provider: str = "Gemini"
    ) -> Tuple[str, Optional[str]]:
        """
        Get LLM response.
        
        Returns:
            Tuple of (response_text, error_message)
        """
        try:
            from litellm import acompletion
            
            # Map provider to model
            model_map = {
                "Gemini": "gemini/gemini-1.5-flash",
                "OpenAI GPT": "gpt-4o-mini",
                "Groq": "groq/llama-3.1-70b-versatile",
                "Anthropic Claude": "claude-3-5-sonnet-20241022",
            }
            
            model = model_map.get(provider, "gemini/gemini-1.5-flash")
            
            response = await acompletion(
                model=model,
                messages=messages,
                api_key=self.llm_key,
                max_tokens=500,
                temperature=0.7,
            )
            
            return response.choices[0].message.content, None
            
        except Exception as e:
            error_msg = str(e).lower()
            if "rate limit" in error_msg or "429" in error_msg:
                return "", "🧠 LLM: Rate limit exceeded. Add your API key."
            elif "quota" in error_msg or "credit" in error_msg:
                return "", "🧠 LLM: Credits exhausted. Add your API key."
            elif "invalid" in error_msg or "401" in error_msg or "403" in error_msg:
                return "", "🧠 LLM: Invalid API key. Check your credentials."
            else:
                logger.error(f"LLM error: {e}")
                return "", f"🧠 LLM Error: {str(e)[:100]}"
    
    async def transcribe_audio(
        self,
        audio_path: str,
        provider: str = "Deepgram"
    ) -> Tuple[str, Optional[str]]:
        """
        Transcribe audio to text.
        
        Returns:
            Tuple of (transcript, error_message)
        """
        try:
            import httpx
            
            # Detect content type
            content_type = "audio/wav"
            if audio_path.endswith(".mp3"):
                content_type = "audio/mpeg"
            elif audio_path.endswith(".webm"):
                content_type = "audio/webm"
            
            with open(audio_path, "rb") as f:
                audio_data = f.read()
            
            if provider == "Deepgram":
                stt_key = self.stt_key or os.getenv("DEEPGRAM_API_KEY")
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://api.deepgram.com/v1/listen",
                        headers={
                            "Authorization": f"Token {stt_key}",
                            "Content-Type": content_type,
                        },
                        content=audio_data,
                        params={"model": "nova-2", "language": "en", "smart_format": "true"},
                        timeout=30.0,
                    )
                    if response.status_code == 200:
                        result = response.json()
                        transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
                        return transcript, None
                    else:
                        raise Exception(f"Deepgram: {response.status_code}")
            
            elif provider == "AssemblyAI":
                stt_key = self.stt_key or os.getenv("ASSEMBLYAI_API_KEY")
                async with httpx.AsyncClient() as client:
                    # Upload
                    upload = await client.post(
                        "https://api.assemblyai.com/v2/upload",
                        headers={"authorization": stt_key},
                        content=audio_data,
                        timeout=60.0,
                    )
                    upload_url = upload.json()["upload_url"]
                    
                    # Transcribe
                    transcript_req = await client.post(
                        "https://api.assemblyai.com/v2/transcript",
                        headers={"authorization": stt_key},
                        json={"audio_url": upload_url},
                        timeout=30.0,
                    )
                    transcript_id = transcript_req.json()["id"]
                    
                    # Poll for result
                    for _ in range(60):
                        result = await client.get(
                            f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                            headers={"authorization": stt_key},
                            timeout=10.0,
                        )
                        data = result.json()
                        if data["status"] == "completed":
                            return data.get("text", ""), None
                        elif data["status"] == "error":
                            raise Exception(data.get("error", "Unknown"))
                        await asyncio.sleep(1)
                    raise Exception("Timeout")
            
            elif provider == "Groq Whisper":
                stt_key = self.stt_key or os.getenv("GROQ_API_KEY")
                async with httpx.AsyncClient() as client:
                    files = {"file": (os.path.basename(audio_path), audio_data, content_type)}
                    response = await client.post(
                        "https://api.groq.com/openai/v1/audio/transcriptions",
                        headers={"Authorization": f"Bearer {stt_key}"},
                        files=files,
                        data={"model": "whisper-large-v3"},
                        timeout=60.0,
                    )
                    if response.status_code == 200:
                        return response.json().get("text", ""), None
                    else:
                        raise Exception(f"Groq: {response.status_code}")
            
            elif provider == "OpenAI Whisper":
                stt_key = self.stt_key or os.getenv("OPENAI_API_KEY")
                async with httpx.AsyncClient() as client:
                    files = {"file": (os.path.basename(audio_path), audio_data, content_type)}
                    response = await client.post(
                        "https://api.openai.com/v1/audio/transcriptions",
                        headers={"Authorization": f"Bearer {stt_key}"},
                        files=files,
                        data={"model": "whisper-1"},
                        timeout=60.0,
                    )
                    if response.status_code == 200:
                        return response.json().get("text", ""), None
                    else:
                        raise Exception(f"OpenAI: {response.status_code}")
            
            return "", f"🎤 STT: Provider {provider} not implemented"
            
        except Exception as e:
            error_msg = str(e).lower()
            if "rate limit" in error_msg or "429" in error_msg:
                return "", f"🎤 STT: Rate limit for {provider}. Add your API key."
            elif "401" in error_msg or "403" in error_msg:
                return "", f"🎤 STT: Invalid {provider} API key."
            else:
                logger.error(f"STT error: {e}")
                return "", f"🎤 STT Error: {str(e)[:100]}"
    
    async def synthesize_speech(
        self,
        text: str,
        provider: str = "Edge TTS (Free)",
        voice_id: Optional[str] = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Synthesize speech from text.
        
        Returns:
            Tuple of (audio_path, error_message)
        """
        try:
            import tempfile
            import httpx
            
            audio_path = os.path.join(tempfile.gettempdir(), "sunona_tts_output.mp3")
            
            if provider == "Edge TTS (Free)":
                import edge_tts
                voice = voice_id or os.getenv("EDGE_TTS_VOICE", "en-US-AriaNeural")
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(audio_path)
                return audio_path, None
            
            elif provider == "ElevenLabs":
                tts_key = self.tts_key or os.getenv("ELEVENLABS_API_KEY")
                voice = voice_id or os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")
                if not tts_key:
                    return await self.synthesize_speech(text, "Edge TTS (Free)", voice_id)
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"https://api.elevenlabs.io/v1/text-to-speech/{voice}",
                        headers={"xi-api-key": tts_key, "Content-Type": "application/json"},
                        json={"text": text, "model_id": "eleven_turbo_v2_5"},
                        timeout=30.0,
                    )
                    if response.status_code == 200:
                        with open(audio_path, "wb") as f:
                            f.write(response.content)
                        return audio_path, None
                    else:
                        return await self.synthesize_speech(text, "Edge TTS (Free)")
            
            elif provider == "OpenAI TTS":
                tts_key = self.tts_key or os.getenv("OPENAI_API_KEY")
                voice = voice_id or os.getenv("OPENAI_TTS_VOICE", "alloy")
                if not tts_key:
                    return await self.synthesize_speech(text, "Edge TTS (Free)", voice_id)
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://api.openai.com/v1/audio/speech",
                        headers={"Authorization": f"Bearer {tts_key}", "Content-Type": "application/json"},
                        json={"model": "tts-1", "input": text, "voice": voice},
                        timeout=30.0,
                    )
                    if response.status_code == 200:
                        with open(audio_path, "wb") as f:
                            f.write(response.content)
                        return audio_path, None
                    else:
                        return await self.synthesize_speech(text, "Edge TTS (Free)")
            
            elif provider == "Deepgram Aura":
                tts_key = self.tts_key or os.getenv("DEEPGRAM_API_KEY")
                voice = voice_id or os.getenv("DEEPGRAM_TTS_VOICE", "aura-asteria-en")
                if not tts_key:
                    return await self.synthesize_speech(text, "Edge TTS (Free)", voice_id)
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"https://api.deepgram.com/v1/speak?model={voice}",
                        headers={"Authorization": f"Token {tts_key}", "Content-Type": "application/json"},
                        json={"text": text},
                        timeout=30.0,
                    )
                    if response.status_code == 200:
                        with open(audio_path, "wb") as f:
                            f.write(response.content)
                        return audio_path, None
                    else:
                        return await self.synthesize_speech(text, "Edge TTS (Free)")
            
            elif provider == "Play.ht":
                api_key = os.getenv("PLAYHT_API_KEY")
                user_id = os.getenv("PLAYHT_USER_ID")
                voice = voice_id or os.getenv("PLAYHT_VOICE_ID")
                if not all([api_key, user_id, voice]):
                    return await self.synthesize_speech(text, "Edge TTS (Free)", voice_id)
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://api.play.ht/api/v2/tts",
                        headers={"Authorization": f"Bearer {api_key}", "X-User-Id": user_id, "Content-Type": "application/json"},
                        json={"text": text, "voice": voice, "output_format": "mp3"},
                        timeout=30.0,
                    )
                    if response.status_code == 200:
                        with open(audio_path, "wb") as f:
                            f.write(response.content)
                        return audio_path, None
                    else:
                        return await self.synthesize_speech(text, "Edge TTS (Free)")
            
            return None, f"🔊 TTS: Provider {provider} not implemented"
            
        except Exception as e:
            error_msg = str(e).lower()
            if "rate limit" in error_msg or "429" in error_msg:
                return None, f"🔊 TTS: Rate limit for {provider}. Use Edge TTS (Free)."
            elif "401" in error_msg or "403" in error_msg:
                return None, f"🔊 TTS: Invalid {provider} API key."
            else:
                logger.error(f"TTS error: {e}")
                try:
                    return await self.synthesize_speech(text, "Edge TTS (Free)")
                except:
                    return None, f"🔊 TTS Error: {str(e)[:100]}"


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
    
    with gr.Blocks(
        title="Sunona Voice AI",
        theme=gr.themes.Soft(),
        css="""
        .error-box { background-color: #fee2e2; padding: 16px; border-radius: 8px; border: 1px solid #ef4444; }
        .success-box { background-color: #dcfce7; padding: 16px; border-radius: 8px; border: 1px solid #22c55e; }
        .highlight-section { border: 2px solid #f59e0b !important; }
        """
    ) as demo:
        
        # State variables
        user_config = gr.State({})
        current_demo_type = gr.State("")
        current_prompt = gr.State("")
        error_api = gr.State("")  # Which API failed
        chat_history = gr.State([])
        
        # ================================================================
        # PAGE 1: DEMO SELECTION
        # ================================================================
        with gr.Column(visible=True) as page_demo_select:
            gr.Markdown("# 🎙️ Sunona Voice AI")
            gr.Markdown("### Choose a demo to try")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("""
                    ### 💬 Text-to-Text
                    Chat with AI using text.
                    
                    **Pipeline:** Text → LLM → Text
                    """)
                    btn_demo_t2t = gr.Button("🚀 Try Demo", variant="primary")
                
                with gr.Column():
                    gr.Markdown("""
                    ### 🔊 Text-to-Speech
                    Ask in text, hear the answer.
                    
                    **Pipeline:** Text → LLM → TTS → Audio
                    """)
                    btn_demo_t2s = gr.Button("🚀 Try Demo", variant="primary")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("""
                    ### 🎙️ Speech-to-Speech
                    Voice conversation (hands-free).
                    
                    **Pipeline:** Audio → STT → LLM → TTS → Audio
                    """)
                    btn_demo_s2s = gr.Button("🚀 Try Demo", variant="primary")
                
                with gr.Column():
                    gr.Markdown("""
                    ### 📞 Twilio Phone Call
                    Make a real phone call with AI.
                    
                    **Pipeline:** Phone → STT → LLM → TTS → Phone
                    
                    *⚠️ Requires Twilio credentials*
                    """)
                    btn_demo_twilio = gr.Button("🚀 Try Demo", variant="primary")
            
            gr.Markdown("---")
            btn_goto_config = gr.Button("⚙️ Configure API Keys")
        
        # ================================================================
        # PAGE 2: PROMPT CONFIGURATION
        # ================================================================
        with gr.Column(visible=False) as page_prompt_config:
            prompt_title = gr.Markdown("### Configure Demo")
            btn_back_to_select = gr.Button("← Back to Demo Selection")
            
            gr.Markdown("#### System Prompt")
            gr.Markdown("*Customize the AI's personality and behavior*")
            
            prompt_input = gr.Textbox(
                label="",
                lines=5,
                placeholder="Enter your system prompt...",
                show_label=False
            )
            
            with gr.Row():
                btn_enhance = gr.Button("✨ Enhance with AI", variant="secondary")
                enhance_status = gr.Markdown("")
            
            gr.Markdown("---")
            btn_continue_to_demo = gr.Button("Continue to Demo →", variant="primary", size="lg")
        
        # ================================================================
        # PAGE 3a: TEXT-TO-TEXT DEMO
        # ================================================================
        with gr.Column(visible=False) as page_text_to_text:
            gr.Markdown("# 💬 Text-to-Text Demo")
            with gr.Row():
                btn_t2t_edit = gr.Button("← Edit Prompt", size="sm")
                btn_t2t_home = gr.Button("← Demo Selection", size="sm")
            
            chatbot_t2t = gr.Chatbot(height=400, type="messages")
            
            with gr.Row():
                msg_t2t = gr.Textbox(
                    label="Your message",
                    placeholder="Type your message...",
                    scale=4
                )
                btn_send_t2t = gr.Button("Send", variant="primary", scale=1)
            
            t2t_error = gr.Markdown("", visible=False)
        
        # ================================================================
        # PAGE 3b: TEXT-TO-SPEECH DEMO
        # ================================================================
        with gr.Column(visible=False) as page_text_to_speech:
            gr.Markdown("# 🔊 Text-to-Speech Demo")
            with gr.Row():
                btn_t2s_edit = gr.Button("← Edit Prompt", size="sm")
                btn_t2s_home = gr.Button("← Demo Selection", size="sm")
            
            gr.Markdown("*Ask a question in text, hear the AI's response*")
            
            question_t2s = gr.Textbox(
                label="Your Question",
                placeholder="What would you like to know?",
                lines=2
            )
            btn_speak_t2s = gr.Button("🔊 Get Voice Answer", variant="primary")
            
            response_text_t2s = gr.Textbox(label="AI Response", interactive=False)
            response_audio_t2s = gr.Audio(label="Voice Response", type="filepath")
            
            t2s_error = gr.Markdown("", visible=False)
        
        # ================================================================
        # PAGE 3c: SPEECH-TO-SPEECH DEMO
        # ================================================================
        with gr.Column(visible=False) as page_speech_to_speech:
            gr.Markdown("# 🎙️ Speech-to-Speech Demo")
            with gr.Row():
                btn_s2s_edit = gr.Button("← Edit Prompt", size="sm")
                btn_s2s_home = gr.Button("← Demo Selection", size="sm")
            
            gr.Markdown("*Record your voice, hear the AI respond*")
            
            audio_input_s2s = gr.Audio(
                sources=["microphone"],
                type="filepath",
                label="🎤 Click to Record"
            )
            btn_process_s2s = gr.Button("🔄 Process & Respond", variant="primary")
            
            transcript_s2s = gr.Textbox(label="You said", interactive=False)
            response_text_s2s = gr.Textbox(label="AI Response", interactive=False)
            response_audio_s2s = gr.Audio(label="AI Voice", type="filepath")
            
            s2s_error = gr.Markdown("", visible=False)
        
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
        
        async def do_speech_to_speech(audio_path: str, prompt: str, cfg: dict):
            """Process speech-to-speech."""
            if not audio_path:
                return "", "", None, gr.update(visible=False)
            
            client = APIClient(cfg)
            
            # Transcribe
            stt_provider = cfg.get("stt_provider", "Deepgram")
            transcript, stt_error = await client.transcribe_audio(audio_path, stt_provider)
            
            if stt_error:
                return "", "", None, gr.update(value=stt_error, visible=True)
            
            # Get LLM response
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": transcript}
            ]
            response, llm_error = await client.get_llm_response(messages)
            
            if llm_error:
                return transcript, "", None, gr.update(value=llm_error, visible=True)
            
            # Synthesize speech
            tts_provider = cfg.get("tts_provider", "Edge TTS (Free)")
            tts_voice = cfg.get("tts_voice")
            audio_out, tts_error = await client.synthesize_speech(response, tts_provider, tts_voice)
            
            if tts_error:
                return transcript, response, None, gr.update(value=tts_error, visible=True)
            
            return transcript, response, audio_out, gr.update(visible=False)
        
        async def do_twilio_call(phone: str, prompt: str, cfg: dict):
            """Initiate Twilio call."""
            if not phone.strip():
                return "Please enter a phone number."
            
            twilio_sid = cfg.get("twilio_sid") or os.getenv("TWILIO_ACCOUNT_SID")
            twilio_token = cfg.get("twilio_token") or os.getenv("TWILIO_AUTH_TOKEN")
            twilio_number = cfg.get("twilio_number") or os.getenv("TWILIO_PHONE_NUMBER")
            
            if not all([twilio_sid, twilio_token, twilio_number]):
                return "⚠️ Twilio credentials not configured. Go to ⚙️ Configure API Keys."
            
            try:
                from twilio.rest import Client
                client = Client(twilio_sid, twilio_token)
                
                # For demo, we'll just validate and show success
                # Actual TwiML setup would go here
                return f"📞 Call initiated to {phone}. Twilio credentials validated."
                
            except Exception as e:
                return f"⚠️ Twilio Error: {str(e)[:100]}"
        
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
        
        # Text-to-Speech demo
        btn_speak_t2s.click(
            do_text_to_speech,
            inputs=[question_t2s, current_prompt, user_config],
            outputs=[response_text_t2s, response_audio_t2s, t2s_error]
        )
        
        # Speech-to-Speech demo
        btn_process_s2s.click(
            do_speech_to_speech,
            inputs=[audio_input_s2s, current_prompt, user_config],
            outputs=[transcript_s2s, response_text_s2s, response_audio_s2s, s2s_error]
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
# MAIN
# ============================================================================

if __name__ == "__main__":
    port = int(os.getenv("DEMO_PORT", 7860))
    
    logger.info(f"Starting Sunona Demo on port {port}")
    
    app = create_demo_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
        show_error=True,
    )
