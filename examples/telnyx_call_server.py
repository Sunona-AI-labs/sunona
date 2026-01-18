"""
Sunona Voice AI - Telnyx Call Server

A working example that connects Telnyx phone calls to the Sunona voice AI.
Run this to make and receive AI-powered phone calls via Telnyx.

Usage:
    1. Set up your .env file with Telnyx credentials
    2. Start ngrok: ngrok http 8004
    3. Update TELNYX_WEBHOOK_URL in .env with ngrok URL
    4. Run: python examples/telnyx_call_server.py
    5. Make a call: POST http://localhost:8004/make-call?to=+1234567890
"""

import os
import sys
import json
import base64
import asyncio
import logging
from typing import Optional
from pathlib import Path
from contextlib import asynccontextmanager

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ==================== Imports ====================
SUNONA_AVAILABLE = False

try:
    from sunona.telephony.telnyx_handler import TelnyxHandler
    from sunona.llms import create_llm
    from sunona.transcriber import create_transcriber
    from sunona.synthesizer import create_synthesizer
    from sunona.vad import SileroVAD
    SUNONA_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Sunona core modules not available: {e}")

# ==================== Configuration ====================
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
TELNYX_PROFILE_NAME = os.getenv("TELNYX_PROFILE_NAME")
TELNYX_PHONE_NUMBER = os.getenv("TELNYX_PHONE_NUMBER")
WEBHOOK_URL = os.getenv("TELNYX_WEBHOOK_URL", "http://localhost:8004")

# AI Providers
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct:free")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Default agent configuration
DEFAULT_SYSTEM_PROMPT = """You are a friendly AI phone assistant for Sunona AI. 
Your name is Sarah. You speak naturally and conversationally.
Keep your responses concise since this is a phone call.
Be helpful, warm, and professional."""

# ==================== Global Services ====================
telnyx_handler = None
llm = None
transcriber = None
synthesizer = None
vad = None


async def initialize_services():
    """Initialize all services."""
    global telnyx_handler, llm, transcriber, synthesizer, vad
    
    # Check required credentials
    if not TELNYX_API_KEY:
        logger.error("❌ TELNYX_API_KEY is required!")
        logger.error("Set it in your .env file")
        return
    
    # Initialize Telnyx
    try:
        telnyx_handler = TelnyxHandler(
            api_key=TELNYX_API_KEY,
            profile_name=TELNYX_PROFILE_NAME,
            phone_number=TELNYX_PHONE_NUMBER,
            webhook_base_url=WEBHOOK_URL,
        )
        logger.info("✅ Telnyx handler initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Telnyx: {e}")
        return
    
    # Initialize LLM
    if OPENROUTER_API_KEY and SUNONA_AVAILABLE:
        try:
            llm = create_llm(
                "litellm",
                model=f"openrouter/{OPENROUTER_MODEL}",
                api_key=OPENROUTER_API_KEY,
                api_base="https://openrouter.ai/api/v1"
            )
            logger.info(f"✅ LLM initialized (OpenRouter: {OPENROUTER_MODEL})")
        except Exception as e:
            logger.warning(f"⚠️ OpenRouter LLM failed: {e}")
    
    if llm is None and OPENAI_API_KEY and SUNONA_AVAILABLE:
        try:
            llm = create_llm("openai", model="gpt-4o-mini", api_key=OPENAI_API_KEY)
            logger.info("✅ LLM initialized (OpenAI GPT-4o-mini)")
        except Exception as e:
            logger.warning(f"⚠️ OpenAI LLM not available: {e}")
    
    # Initialize Transcriber
    if DEEPGRAM_API_KEY and SUNONA_AVAILABLE:
        try:
            transcriber = create_transcriber("deepgram", api_key=DEEPGRAM_API_KEY)
            logger.info("✅ Transcriber initialized (Deepgram)")
        except Exception as e:
            logger.warning(f"⚠️ Transcriber not available: {e}")
    
    # Initialize Synthesizer
    if ELEVENLABS_API_KEY and SUNONA_AVAILABLE:
        try:
            synthesizer = create_synthesizer("elevenlabs", api_key=ELEVENLABS_API_KEY)
            logger.info("✅ Synthesizer initialized (ElevenLabs)")
        except Exception as e:
            logger.warning(f"⚠️ Synthesizer not available: {e}")
    
    # Initialize VAD
    if SUNONA_AVAILABLE:
        try:
            vad = SileroVAD()
            logger.info("✅ Voice Activity Detection initialized")
        except Exception as e:
            logger.warning(f"⚠️ VAD not available: {e}")
    
    logger.info(f"🚀 Telnyx Server ready at {WEBHOOK_URL}")
    logger.info(f"📞 Telnyx phone: {TELNYX_PHONE_NUMBER}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    await initialize_services()
    yield
    logger.info("Shutting down Telnyx server...")


# ==================== App Setup ====================
app = FastAPI(
    title="Sunona Voice AI - Telnyx Server",
    description="Make AI-powered phone calls with Telnyx",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Health Check ====================
@app.get("/")
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "Sunona Voice AI - Telnyx Server",
        "telnyx_ready": telnyx_handler is not None,
        "llm_ready": llm is not None,
        "stt_ready": transcriber is not None,
        "tts_ready": synthesizer is not None,
        "webhook_url": WEBHOOK_URL,
    }


# ==================== Telnyx Webhooks ====================
@app.post("/webhook/{agent_id}")
async def telnyx_webhook(agent_id: str, request: Request):
    """
    Webhook called by Telnyx for call events.
    """
    try:
        data = await request.json()
        event_type = data.get("data", {}).get("event_type", "unknown")
        call_control_id = data.get("data", {}).get("payload", {}).get("call_control_id", "unknown")
        
        logger.info(f"Telnyx event: {event_type} for call: {call_control_id}")
        
        if telnyx_handler and event_type == "call.initiated":
            # Handle incoming call
            response = telnyx_handler.handle_incoming_call(data, agent_id)
            return JSONResponse(response)
        
        return {"status": "received"}
    except Exception as e:
        logger.error(f"Error handling Telnyx webhook: {e}")
        return {"status": "error", "message": str(e)}


# ==================== API Endpoints ====================
@app.post("/make-call")
async def make_call(to: str, agent_id: str = "default"):
    """
    Make an outbound call via Telnyx.
    
    Args:
        to: Phone number to call (E.164 format)
        agent_id: Agent configuration ID
    """
    if not telnyx_handler:
        raise HTTPException(500, "Telnyx not configured")
    
    if not to.startswith("+"):
        to = f"+{to}"
    
    try:
        call_control_id = telnyx_handler.initiate_call(
            to_number=to,
            agent_id=agent_id,
        )
        
        logger.info(f"📞 Initiated Telnyx call to {to}")
        
        return {
            "success": True,
            "call_control_id": call_control_id,
            "to": to,
            "from": TELNYX_PHONE_NUMBER,
            "status": "initiated",
            "provider": "telnyx",
        }
    except Exception as e:
        logger.error(f"Failed to make Telnyx call: {e}")
        raise HTTPException(500, str(e))


@app.get("/calls")
async def list_active_calls():
    """List active Telnyx calls."""
    if not telnyx_handler:
        return {"calls": [], "provider": "telnyx"}
    
    return {
        "calls": list(telnyx_handler._active_calls.keys()) if hasattr(telnyx_handler, '_active_calls') else [],
        "provider": "telnyx"
    }


# ==================== Main ====================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎙️  SUNONA VOICE AI - TELNYX CALL SERVER")
    print("="*60)
    print(f"\n📍 Webhook URL: {WEBHOOK_URL}")
    print(f"📞 Telnyx Phone: {TELNYX_PHONE_NUMBER or 'Not configured'}")
    print("\n⚡ Starting server on http://localhost:8004")
    print("\n📖 To make a call:")
    print("   POST http://localhost:8004/make-call?to=+1234567890")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8004,
        log_level="info",
    )
