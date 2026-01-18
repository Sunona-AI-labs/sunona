"""
Sunona Voice AI - Bandwidth Call Server

A working example that connects Bandwidth phone calls to the Sunona voice AI.
Run this to make and receive AI-powered phone calls via Bandwidth.

Usage:
    1. Set up your .env file with Bandwidth credentials
    2. Start ngrok: ngrok http 8005
    3. Update BANDWIDTH_WEBHOOK_URL in .env with ngrok URL
    4. Run: python examples/bandwidth_call_server.py
    5. Make a call: POST http://localhost:8005/make-call?to=+1234567890
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
    from sunona.telephony.bandwidth_handler import BandwidthHandler
    from sunona.llms import create_llm
    from sunona.transcriber import create_transcriber
    from sunona.synthesizer import create_synthesizer
    from sunona.vad import SileroVAD
    SUNONA_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Sunona core modules not available: {e}")

# ==================== Configuration ====================
BANDWIDTH_USERNAME = os.getenv("BANDWIDTH_USERNAME")
BANDWIDTH_PASSWORD = os.getenv("BANDWIDTH_PASSWORD")
BANDWIDTH_ACCOUNT_ID = os.getenv("BANDWIDTH_ACCOUNT_ID")
BANDWIDTH_APPLICATION_ID = os.getenv("BANDWIDTH_APPLICATION_ID")
BANDWIDTH_PHONE_NUMBER = os.getenv("BANDWIDTH_PHONE_NUMBER")
WEBHOOK_URL = os.getenv("BANDWIDTH_WEBHOOK_URL", "http://localhost:8005")

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
bandwidth_handler = None
llm = None
transcriber = None
synthesizer = None
vad = None


async def initialize_services():
    """Initialize all services."""
    global bandwidth_handler, llm, transcriber, synthesizer, vad
    
    # Check required credentials
    if not BANDWIDTH_USERNAME or not BANDWIDTH_PASSWORD or not BANDWIDTH_ACCOUNT_ID:
        logger.error("❌ BANDWIDTH_USERNAME, BANDWIDTH_PASSWORD, and BANDWIDTH_ACCOUNT_ID are required!")
        logger.error("Set them in your .env file")
        return
    
    # Initialize Bandwidth
    try:
        bandwidth_handler = BandwidthHandler(
            username=BANDWIDTH_USERNAME,
            password=BANDWIDTH_PASSWORD,
            account_id=BANDWIDTH_ACCOUNT_ID,
            application_id=BANDWIDTH_APPLICATION_ID,
            phone_number=BANDWIDTH_PHONE_NUMBER,
            webhook_base_url=WEBHOOK_URL,
        )
        logger.info("✅ Bandwidth handler initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Bandwidth: {e}")
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
    
    logger.info(f"🚀 Bandwidth Server ready at {WEBHOOK_URL}")
    logger.info(f"📞 Bandwidth phone: {BANDWIDTH_PHONE_NUMBER}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    await initialize_services()
    yield
    logger.info("Shutting down Bandwidth server...")


# ==================== App Setup ====================
app = FastAPI(
    title="Sunona Voice AI - Bandwidth Server",
    description="Make AI-powered phone calls with Bandwidth",
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
        "service": "Sunona Voice AI - Bandwidth Server",
        "bandwidth_ready": bandwidth_handler is not None,
        "llm_ready": llm is not None,
        "stt_ready": transcriber is not None,
        "tts_ready": synthesizer is not None,
        "webhook_url": WEBHOOK_URL,
    }


# ==================== Bandwidth Webhooks ====================
@app.post("/callback/{agent_id}")
async def bandwidth_callback(agent_id: str, request: Request):
    """
    Callback webhook called by Bandwidth for call events.
    """
    try:
        data = await request.json()
        event_type = data.get("eventType", "unknown")
        call_id = data.get("callId", "unknown")
        
        logger.info(f"Bandwidth event: {event_type} for call: {call_id}")
        
        if bandwidth_handler and event_type == "answer":
            # Handle call answered
            response = bandwidth_handler.handle_answer(data, agent_id)
            return Response(content=response, media_type="application/xml")
        
        return {"status": "received"}
    except Exception as e:
        logger.error(f"Error handling Bandwidth callback: {e}")
        return {"status": "error", "message": str(e)}


# ==================== API Endpoints ====================
@app.post("/make-call")
async def make_call(to: str, agent_id: str = "default"):
    """
    Make an outbound call via Bandwidth.
    
    Args:
        to: Phone number to call (E.164 format)
        agent_id: Agent configuration ID
    """
    if not bandwidth_handler:
        raise HTTPException(500, "Bandwidth not configured")
    
    if not to.startswith("+"):
        to = f"+{to}"
    
    try:
        call_id = bandwidth_handler.initiate_call(
            to_number=to,
            agent_id=agent_id,
        )
        
        logger.info(f"📞 Initiated Bandwidth call to {to}")
        
        return {
            "success": True,
            "call_id": call_id,
            "to": to,
            "from": BANDWIDTH_PHONE_NUMBER,
            "status": "initiated",
            "provider": "bandwidth",
        }
    except Exception as e:
        logger.error(f"Failed to make Bandwidth call: {e}")
        raise HTTPException(500, str(e))


@app.get("/calls")
async def list_active_calls():
    """List active Bandwidth calls."""
    if not bandwidth_handler:
        return {"calls": [], "provider": "bandwidth"}
    
    return {
        "calls": list(bandwidth_handler._active_calls.keys()) if hasattr(bandwidth_handler, '_active_calls') else [],
        "provider": "bandwidth"
    }


# ==================== Main ====================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎙️  SUNONA VOICE AI - BANDWIDTH CALL SERVER")
    print("="*60)
    print(f"\n📍 Webhook URL: {WEBHOOK_URL}")
    print(f"📞 Bandwidth Phone: {BANDWIDTH_PHONE_NUMBER or 'Not configured'}")
    print("\n⚡ Starting server on http://localhost:8005")
    print("\n📖 To make a call:")
    print("   POST http://localhost:8005/make-call?to=+1234567890")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8005,
        log_level="info",
    )
