"""
Sunona Voice AI - Plivo Call Server

A working example that connects Plivo phone calls to the Sunona voice AI.
Run this to make and receive AI-powered phone calls via Plivo.

Usage:
    1. Set up your .env file with Plivo credentials
    2. Start ngrok: ngrok http 8002
    3. Update PLIVO_WEBHOOK_URL in .env with ngrok URL
    4. Run: python examples/plivo_call_server.py
    5. Make a call: POST http://localhost:8002/make-call?to=+1234567890
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
    from sunona.telephony.plivo_handler import PlivoHandler
    from sunona.llms import create_llm
    from sunona.transcriber import create_transcriber
    from sunona.synthesizer import create_synthesizer
    from sunona.vad import SileroVAD
    SUNONA_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Sunona core modules not available: {e}")

# ==================== Configuration ====================
PLIVO_AUTH_ID = os.getenv("PLIVO_AUTH_ID")
PLIVO_AUTH_TOKEN = os.getenv("PLIVO_AUTH_TOKEN")
PLIVO_PHONE_NUMBER = os.getenv("PLIVO_PHONE_NUMBER")
WEBHOOK_URL = os.getenv("PLIVO_WEBHOOK_URL", "http://localhost:8002")

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
plivo_handler = None
llm = None
transcriber = None
synthesizer = None
vad = None


async def initialize_services():
    """Initialize all services."""
    global plivo_handler, llm, transcriber, synthesizer, vad
    
    # Check required credentials
    if not PLIVO_AUTH_ID or not PLIVO_AUTH_TOKEN:
        logger.error("❌ PLIVO_AUTH_ID and PLIVO_AUTH_TOKEN are required!")
        logger.error("Set them in your .env file")
        return
    
    # Initialize Plivo
    try:
        plivo_handler = PlivoHandler(
            auth_id=PLIVO_AUTH_ID,
            auth_token=PLIVO_AUTH_TOKEN,
            phone_number=PLIVO_PHONE_NUMBER,
            webhook_base_url=WEBHOOK_URL,
        )
        logger.info("✅ Plivo handler initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Plivo: {e}")
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
    
    logger.info(f"🚀 Plivo Server ready at {WEBHOOK_URL}")
    logger.info(f"📞 Plivo phone: {PLIVO_PHONE_NUMBER}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    await initialize_services()
    yield
    logger.info("Shutting down Plivo server...")


# ==================== App Setup ====================
app = FastAPI(
    title="Sunona Voice AI - Plivo Server",
    description="Make AI-powered phone calls with Plivo",
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
        "service": "Sunona Voice AI - Plivo Server",
        "plivo_ready": plivo_handler is not None,
        "llm_ready": llm is not None,
        "stt_ready": transcriber is not None,
        "tts_ready": synthesizer is not None,
        "webhook_url": WEBHOOK_URL,
    }


# ==================== Plivo Webhooks ====================
@app.post("/answer/{agent_id}")
async def answer_webhook(agent_id: str, request: Request):
    """
    Answer webhook called by Plivo when a call connects.
    Returns XML instructions for the call.
    """
    if not plivo_handler:
        return Response(
            content="<Response><Speak>Service unavailable</Speak></Response>",
            media_type="application/xml"
        )
    
    xml_response = plivo_handler.generate_answer_xml(agent_id)
    logger.info(f"Generated answer XML for agent: {agent_id}")
    
    return Response(content=xml_response, media_type="application/xml")


@app.post("/status/{agent_id}")
async def status_webhook(agent_id: str, request: Request):
    """Handle call status updates from Plivo."""
    form = await request.form()
    call_status = form.get("CallStatus", "unknown")
    call_uuid = form.get("CallUUID", "unknown")
    
    logger.info(f"Plivo Call {call_uuid} status: {call_status}")
    
    return {"status": "received"}


# ==================== API Endpoints ====================
@app.post("/make-call")
async def make_call(to: str, agent_id: str = "default"):
    """
    Make an outbound call via Plivo.
    
    Args:
        to: Phone number to call (E.164 format)
        agent_id: Agent configuration ID
    """
    if not plivo_handler:
        raise HTTPException(500, "Plivo not configured")
    
    if not to.startswith("+"):
        to = f"+{to}"
    
    try:
        call_uuid = plivo_handler.initiate_call(
            to_number=to,
            agent_id=agent_id,
        )
        
        logger.info(f"📞 Initiated Plivo call to {to}")
        
        return {
            "success": True,
            "call_uuid": call_uuid,
            "to": to,
            "from": PLIVO_PHONE_NUMBER,
            "status": "initiated",
            "provider": "plivo",
        }
    except Exception as e:
        logger.error(f"Failed to make Plivo call: {e}")
        raise HTTPException(500, str(e))


@app.get("/calls")
async def list_active_calls():
    """List active Plivo calls."""
    if not plivo_handler:
        return {"calls": [], "provider": "plivo"}
    
    return {
        "calls": list(plivo_handler._active_calls.keys()) if hasattr(plivo_handler, '_active_calls') else [],
        "provider": "plivo"
    }


# ==================== Main ====================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎙️  SUNONA VOICE AI - PLIVO CALL SERVER")
    print("="*60)
    print(f"\n📍 Webhook URL: {WEBHOOK_URL}")
    print(f"📞 Plivo Phone: {PLIVO_PHONE_NUMBER or 'Not configured'}")
    print("\n⚡ Starting server on http://localhost:8002")
    print("\n📖 To make a call:")
    print("   POST http://localhost:8002/make-call?to=+1234567890")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info",
    )
