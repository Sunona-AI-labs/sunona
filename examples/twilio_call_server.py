"""
Sunona Voice AI - Complete Twilio Call Server

A working example that connects Twilio phone calls to the Sunona voice AI.
Run this to make and receive AI-powered phone calls.

Usage:
    1. Set up your .env file with credentials
    2. Start ngrok: ngrok http 8000
    3. Update TWILIO_WEBHOOK_URL in .env with ngrok URL
    4. Run: python examples/twilio_call_server.py
    5. Make a call: POST http://localhost:8000/make-call?to=+1234567890
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
BILLING_AVAILABLE = False

try:
    from sunona.telephony.twilio_handler import TwilioHandler
    from sunona.llms import create_llm
    from sunona.transcriber import create_transcriber
    from sunona.synthesizer import create_synthesizer
    from sunona.vad import SileroVAD
    SUNONA_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Sunona core modules not available: {e}")

try:
    from sunona.billing.middleware import (
        BillingMiddleware,
        CallTracker,
        get_call_tracker,
    )
    BILLING_AVAILABLE = True
except ImportError as e:
    logger.debug(f"Billing modules not available: {e}")

# ==================== Configuration ====================
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
WEBHOOK_URL = os.getenv("TWILIO_WEBHOOK_URL", "http://localhost:8000")

# AI Providers - LLM (supports OpenRouter OR OpenAI)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct:free")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# STT and TTS
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")

# Default agent configuration
DEFAULT_SYSTEM_PROMPT = """You are a friendly AI phone assistant for Sunona AI. 
Your name is Sarah. You speak naturally and conversationally.
Keep your responses concise since this is a phone call.
Be helpful, warm, and professional."""

# ==================== Global Services ====================
twilio_handler = None
llm = None
transcriber = None
synthesizer = None
vad = None


async def initialize_services():
    """Initialize all services."""
    global twilio_handler, llm, transcriber, synthesizer, vad
    
    # Check required credentials
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        logger.error("❌ TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN are required!")
        logger.error("Set them in your .env file")
        return
    
    # Initialize Twilio
    try:
        twilio_handler = TwilioHandler(
            account_sid=TWILIO_ACCOUNT_SID,
            auth_token=TWILIO_AUTH_TOKEN,

            phone_number=TWILIO_PHONE_NUMBER,
            webhook_base_url=WEBHOOK_URL,
        )
        logger.info("✅ Twilio handler initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Twilio: {e}")
        return
    
    # Initialize LLM (prefer OpenRouter, fallback to OpenAI)
    if OPENROUTER_API_KEY and SUNONA_AVAILABLE:
        try:
            # Use OpenRouter with LiteLLM format
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
    
    if llm is None:
        logger.warning("⚠️ No LLM configured! Set OPENROUTER_API_KEY or OPENAI_API_KEY")
    
    # Initialize Transcriber (STT)
    if DEEPGRAM_API_KEY and SUNONA_AVAILABLE:
        try:
            transcriber = create_transcriber("deepgram", api_key=DEEPGRAM_API_KEY)
            logger.info("✅ Transcriber initialized (Deepgram)")
        except Exception as e:
            logger.warning(f"⚠️ Transcriber not available: {e}")
    
    # Initialize Synthesizer (TTS)
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
    
    logger.info(f"🚀 Server ready at {WEBHOOK_URL}")
    logger.info(f"📞 Twilio phone: {TWILIO_PHONE_NUMBER}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    await initialize_services()
    yield
    # Cleanup on shutdown
    logger.info("Shutting down server...")


# ==================== App Setup ====================
app = FastAPI(
    title="Sunona Voice AI - Twilio Server",
    description="Make AI-powered phone calls with Twilio",
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

async def health_check():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "Sunona Voice AI - Twilio Server",
        "twilio_ready": twilio_handler is not None,
        "llm_ready": llm is not None,
        "stt_ready": transcriber is not None,
        "tts_ready": synthesizer is not None,
        "webhook_url": WEBHOOK_URL,
    }


# ==================== Twilio Webhooks ====================
@app.post("/twiml/{agent_id}")
async def twiml_webhook(agent_id: str, request: Request):
    """
    TwiML webhook called by Twilio when a call connects.
    Returns TwiML instructions to connect to WebSocket.
    """
    if not twilio_handler:
        return Response(
            content="<Response><Say>Service unavailable</Say></Response>",
            media_type="application/xml"
        )
    
    twiml = twilio_handler.generate_twiml(agent_id)
    logger.info(f"Generated TwiML for agent: {agent_id}")
    
    return Response(content=twiml, media_type="application/xml")


@app.post("/status/{agent_id}")
async def status_webhook(agent_id: str, request: Request):
    """Handle call status updates from Twilio."""
    form = await request.form()
    call_status = form.get("CallStatus", "unknown")
    call_sid = form.get("CallSid", "unknown")
    
    logger.info(f"Call {call_sid} status: {call_status}")
    
    return {"status": "received"}


# ==================== WebSocket Media Handler ====================
@app.websocket("/media/{agent_id}")
async def media_websocket(websocket: WebSocket, agent_id: str):
    """
    Handle Twilio media stream WebSocket.
    This is where the voice AI magic happens!
    """
    await websocket.accept()
    logger.info(f"WebSocket connected for agent: {agent_id}")
    
    # Conversation state
    stream_sid = None
    call_sid = None
    conversation_history = []
    audio_buffer = bytearray()
    
    try:
        # Greeting - say hello when call starts
        greeting = "Hello! This is Sarah from Sunona AI. How can I help you today?"
        conversation_history.append({"role": "assistant", "content": greeting})
        
        async for message in websocket.iter_text():
            data = json.loads(message)
            event = data.get("event")
            
            if event == "connected":
                logger.info("Twilio stream connected")
            
            elif event == "start":
                stream_sid = data.get("streamSid")
                call_sid = data.get("start", {}).get("callSid")
                logger.info(f"Call started: {call_sid}")
                
                # Send greeting audio
                if synthesizer:
                    try:
                        audio = await synthesizer.synthesize(greeting)
                        await send_audio_to_twilio(websocket, stream_sid, audio)
                    except Exception as e:
                        logger.error(f"Failed to send greeting: {e}")
            
            elif event == "media":
                # Received audio from caller
                payload = data.get("media", {}).get("payload", "")
                if payload:
                    audio_chunk = base64.b64decode(payload)
                    audio_buffer.extend(audio_chunk)
                    
                    # Process audio when we have enough (about 1 second)
                    if len(audio_buffer) > 8000:  # ~0.5 seconds at 8kHz
                        await process_audio(
                            websocket,
                            stream_sid,
                            call_sid,
                            bytes(audio_buffer),
                            conversation_history,
                        )
                        audio_buffer.clear()
            
            elif event == "stop":
                logger.info(f"Call ended: {call_sid}")
                
                # Charge for the call
                if BILLING_AVAILABLE and call_sid:
                    try:
                        tracker = get_call_tracker()
                        charge_result = await tracker.end_call(call_sid)
                        if charge_result:
                            logger.info(f"💰 Charged ${charge_result['costs']['total']:.4f} for call {call_sid}")
                    except Exception as e:
                        logger.error(f"Billing error: {e}")
                
                break
    
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
        # Also charge if disconnect
        if BILLING_AVAILABLE and call_sid:
            try:
                tracker = get_call_tracker()
                await tracker.end_call(call_sid)
            except Exception as e:
                logger.error(f"Billing on disconnect error: {e}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        logger.info(f"Cleaned up call: {call_sid}")


async def process_audio(
    websocket: WebSocket,
    stream_sid: str,
    call_sid: str,
    audio: bytes,
    history: list,
):
    """
    Process audio from caller:
    1. Transcribe (STT)
    2. Generate response (LLM)
    3. Synthesize (TTS)
    4. Send back to caller
    """
    global llm, transcriber, synthesizer
    from sunona.billing import get_usage_tracker
    tracker = get_usage_tracker()
    
    # Step 1: Transcribe
    transcript = ""
    if transcriber:
        try:
            # Report STT usage (estimate based on audio duration)
            audio_duration = len(audio) / (16000 * 2)  # Assuming 16k 16-bit PCM
            if call_sid:
                tracker.add_stt_usage(call_sid, audio_duration)
            
            transcript = await transcriber.transcribe(audio)
        except Exception as e:
            logger.error(f"Transcription error: {e}")
    
    if not transcript or len(transcript.strip()) < 2:
        return  # No speech detected
    
    logger.info(f"👤 User: {transcript}")
    history.append({"role": "user", "content": transcript})
    
    # Step 2: Generate response
    response_text = "I'm sorry, I couldn't process that."
    if llm:
        try:
            messages = [
                {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
                *history[-10:]  # Keep last 10 messages for context
            ]
            
            # Use generate with tokens if possible, or estimate
            # Here we estimate: 1 char ~= 0.25 tokens
            input_tokens = sum(len(m["content"]) for m in messages) // 4
            response_text = await llm.generate(messages)
            output_tokens = len(response_text) // 4
            
            if call_sid:
                tracker.add_llm_usage(call_sid, input_tokens, output_tokens)
                
            logger.info(f"🤖 AI: {response_text}")
        except Exception as e:
            logger.error(f"LLM error: {e}")
    
    history.append({"role": "assistant", "content": response_text})
    
    # Step 3: Synthesize and send
    if synthesizer and stream_sid:
        try:
            if call_sid:
                tracker.add_tts_usage(call_sid, response_text)
                
            audio = await synthesizer.synthesize(response_text)
            await send_audio_to_twilio(websocket, stream_sid, audio)
        except Exception as e:
            logger.error(f"Synthesis error: {e}")


async def send_audio_to_twilio(
    websocket: WebSocket,
    stream_sid: str,
    audio: bytes,
):
    """Send audio back to Twilio call."""
    # Convert to mulaw format for Twilio
    # Twilio expects base64-encoded mulaw audio
    audio_b64 = base64.b64encode(audio).decode("utf-8")
    
    # Send media message
    message = {
        "event": "media",
        "streamSid": stream_sid,
        "media": {
            "payload": audio_b64
        }
    }
    
    await websocket.send_text(json.dumps(message))


# ==================== API Endpoints ====================
@app.post("/make-call")
async def make_call(
    to: str,
    agent_id: str = "default",
    account_id: str = "demo_account",  # In production, get from API key
):
    """
    Make an outbound call.
    
    Args:
        to: Phone number to call (E.164 format, e.g., +1234567890)
        agent_id: Agent configuration ID
        account_id: Account ID for billing
        
    Returns:
        Call SID and status
        
    Raises:
        402: Insufficient balance
    """
    if not twilio_handler:
        raise HTTPException(500, "Twilio not configured")
    
    if not to.startswith("+"):
        to = f"+{to}"
    
    # Check balance before making call
    if BILLING_AVAILABLE:
        try:
            billing = BillingMiddleware()
            await billing.check_balance(account_id)
            logger.info(f"✅ Balance check passed for {account_id}")
        except HTTPException as e:
            logger.warning(f"❌ Balance check failed: {e.detail}")
            raise
        except Exception as e:
            logger.warning(f"Billing check skipped: {e}")
    
    try:
        call_sid = twilio_handler.initiate_call(
            to_number=to,
            agent_id=agent_id,
        )
        
        # Track call for billing
        if BILLING_AVAILABLE:
            tracker = get_call_tracker()
            tracker.start_call(
                call_sid=call_sid,
                account_id=account_id,
                llm_model=OPENROUTER_MODEL or "gpt-4o-mini",
                stt_provider="deepgram-nova-2",
                tts_provider="elevenlabs",
                telephony_provider="twilio",
            )
        
        logger.info(f"📞 Initiated call to {to}")
        
        return {
            "success": True,
            "call_sid": call_sid,
            "to": to,
            "from": TWILIO_PHONE_NUMBER,
            "status": "initiated",
            "billing": "Call will be charged upon completion" if BILLING_AVAILABLE else "Billing not enabled",
        }
    except Exception as e:
        logger.error(f"Failed to make call: {e}")
        raise HTTPException(500, str(e))


@app.get("/calls")
async def list_active_calls():
    """List active calls."""
    if not twilio_handler:
        return {"calls": []}
    
    return {
        "calls": list(twilio_handler._active_calls.keys())
    }


@app.post("/hangup/{call_sid}")
async def hangup_call(call_sid: str):
    """Hang up a call."""
    if not twilio_handler:
        raise HTTPException(500, "Twilio not configured")
    
    try:
        twilio_handler._client.calls(call_sid).update(status="completed")
        return {"success": True, "call_sid": call_sid}
    except Exception as e:
        raise HTTPException(500, str(e))


# ==================== Main ====================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎙️  SUNONA VOICE AI - TWILIO CALL SERVER")
    print("="*60)
    print(f"\n📍 Webhook URL: {WEBHOOK_URL}")
    print(f"📞 Twilio Phone: {TWILIO_PHONE_NUMBER or 'Not configured'}")
    print("\n⚡ Starting server on http://localhost:8000")
    print("\n📖 To make a call:")
    print("   POST http://localhost:8000/make-call?to=+1234567890")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
