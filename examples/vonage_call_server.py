"""
Sunona Voice AI - Vonage Call Server

A working example that connects Vonage phone calls to the Sunona voice AI.
Run this to make and receive AI-powered phone calls via Vonage.

Usage:
    1. Set up your .env file with Vonage credentials
    2. Start ngrok: ngrok http 8003
    3. Update VONAGE_WEBHOOK_URL in .env with ngrok URL
    4. Run: python examples/vonage_call_server.py
    5. Make a call: POST http://localhost:8003/make-call?to=+1234567890
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
    from sunona.telephony.vonage_handler import VonageHandler
    from sunona.llms import create_llm
    from sunona.transcriber import create_transcriber
    from sunona.synthesizer import create_synthesizer
    from sunona.vad import SileroVAD
    SUNONA_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Sunona core modules not available: {e}")

# ==================== Configuration ====================
VONAGE_API_KEY = os.getenv("VONAGE_API_KEY")
VONAGE_API_SECRET = os.getenv("VONAGE_API_SECRET")
VONAGE_APPLICATION_ID = os.getenv("VONAGE_APPLICATION_ID")
VONAGE_PRIVATE_KEY = os.getenv("VONAGE_PRIVATE_KEY")
VONAGE_PHONE_NUMBER = os.getenv("VONAGE_PHONE_NUMBER")
WEBHOOK_URL = os.getenv("VONAGE_WEBHOOK_URL", "http://localhost:8003")

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
vonage_handler = None
llm = None
transcriber = None
synthesizer = None
vad = None


async def initialize_services():
    """Initialize all services."""
    global vonage_handler, llm, transcriber, synthesizer, vad
    
    # Check required credentials
    if not VONAGE_API_KEY or not VONAGE_API_SECRET:
        logger.error("❌ VONAGE_API_KEY and VONAGE_API_SECRET are required!")
        logger.error("Set them in your .env file")
        return
    
    # Initialize Vonage
    try:
        vonage_handler = VonageHandler(
            api_key=VONAGE_API_KEY,
            api_secret=VONAGE_API_SECRET,
            application_id=VONAGE_APPLICATION_ID,
            private_key=VONAGE_PRIVATE_KEY,
            phone_number=VONAGE_PHONE_NUMBER,
            webhook_base_url=WEBHOOK_URL,
        )
        logger.info("✅ Vonage handler initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Vonage: {e}")
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
    
    logger.info(f"🚀 Vonage Server ready at {WEBHOOK_URL}")
    logger.info(f"📞 Vonage phone: {VONAGE_PHONE_NUMBER}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    await initialize_services()
    yield
    logger.info("Shutting down Vonage server...")


# ==================== App Setup ====================
app = FastAPI(
    title="Sunona Voice AI - Vonage Server",
    description="Make AI-powered phone calls with Vonage",
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
        "service": "Sunona Voice AI - Vonage Server",
        "vonage_ready": vonage_handler is not None,
        "llm_ready": llm is not None,
        "stt_ready": transcriber is not None,
        "tts_ready": synthesizer is not None,
        "webhook_url": WEBHOOK_URL,
    }


# ==================== Vonage Webhooks ====================
@app.post("/answer/{agent_id}")
@app.get("/answer/{agent_id}")
async def answer_webhook(agent_id: str, request: Request):
    """
    Answer webhook called by Vonage when a call connects.
    Returns NCCO (Nexmo Call Control Object) instructions.
    """
    if not vonage_handler:
        return JSONResponse([{"action": "talk", "text": "Service unavailable"}])
    
    ncco = vonage_handler.generate_ncco(agent_id)
    logger.info(f"Generated NCCO for agent: {agent_id}")
    
    return JSONResponse(ncco)


@app.post("/event/{agent_id}")
async def event_webhook(agent_id: str, request: Request):
    """Handle call events from Vonage."""
    try:
        data = await request.json()
        call_status = data.get("status", "unknown")
        call_uuid = data.get("uuid", "unknown")
        
        logger.info(f"Vonage Call {call_uuid} status: {call_status}")
    except Exception as e:
        logger.error(f"Error parsing Vonage event: {e}")
    
    return {"status": "received"}


# ==================== API Endpoints ====================
@app.post("/make-call")
async def make_call(to: str, agent_id: str = "default"):
    """
    Make an outbound call via Vonage.
    
    Args:
        to: Phone number to call (E.164 format)
        agent_id: Agent configuration ID
    """
    if not vonage_handler:
        raise HTTPException(500, "Vonage not configured")
    
    if not to.startswith("+"):
        to = f"+{to}"
    
    try:
        call_uuid = vonage_handler.initiate_call(
            to_number=to,
            agent_id=agent_id,
        )
        
        logger.info(f"📞 Initiated Vonage call to {to}")
        
        return {
            "success": True,
            "call_uuid": call_uuid,
            "to": to,
            "from": VONAGE_PHONE_NUMBER,
            "status": "initiated",
            "provider": "vonage",
        }
    except Exception as e:
        logger.error(f"Failed to make Vonage call: {e}")
        raise HTTPException(500, str(e))


@app.get("/calls")
async def list_active_calls():
    """List active Vonage calls."""
    if not vonage_handler:
        return {"calls": [], "provider": "vonage"}
    
    return {
        "calls": list(vonage_handler._active_calls.keys()) if hasattr(vonage_handler, '_active_calls') else [],
        "provider": "vonage"
    }


# ==================== Main ====================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎙️  SUNONA VOICE AI - VONAGE CALL SERVER")
    print("="*60)
    print(f"\n📍 Webhook URL: {WEBHOOK_URL}")
    print(f"📞 Vonage Phone: {VONAGE_PHONE_NUMBER or 'Not configured'}")
    print("\n⚡ Starting server on http://localhost:8003")
    print("\n📖 To make a call:")
    print("   POST http://localhost:8003/make-call?to=+1234567890")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        log_level="info",
    )
