"""
Sunona Voice AI - Simplified Twilio Trial Test Server
Created for testing AI voice with Twilio trial accounts.

Instructions:
1. Run this script: python demo/twilio_trial_test.py
2. In another terminal, run ngrok: ngrok http 8001
3. Copy your ngrok URL (e.g., https://abcd123.ngrok-free.app)
4. Go to Twilio Console -> Phone Numbers -> Active Numbers -> [Your Number]
5. Scroll to "Voice & Fax" -> "A CALL COMES IN"
6. Set Webhook to [Your URL]/voice and click Save.
7. Call your Twilio number from your verified phone.
8. When prompted, press any key on your phone to connect!
"""

import os
import json
import base64
import asyncio
import logging
from pathlib import Path
import sys

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
import uvicorn
from dotenv import load_dotenv

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Load .env
load_dotenv(PROJECT_ROOT / ".env")

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TwilioTrialTest")

app = FastAPI()

# --- Sunona Imports ---
# We try to use Sunona components if available, otherwise dummy fallback
try:
    from sunona.llms import create_llm
    from sunona.synthesizer import create_synthesizer
    from sunona.transcriber import create_transcriber
    
    # Initialize basic components
    llm = create_llm("openai", model="gpt-4o-mini") # Falls back to env keys
    synthesizer = create_synthesizer("edge") # Reliable for testing
    transcriber = create_transcriber("deepgram")
    SUNONA_READY = True
    logger.info("✅ Sunona modules loaded successfully")
except Exception as e:
    logger.warning(f"⚠️ Could not load Sunona modules: {e}")
    SUNONA_READY = False

# --- Endpoints ---

@app.get("/")
async def root():
    return {"status": "ok", "message": "Twilio Trial Test Server is running!"}

@app.post("/voice")
async def voice_webhook(request: Request):
    """Twilio hits this when a call starts."""
    logger.info("Incoming call webhook received")
    
    # Get the host from the request to generate the WebSocket URL
    host = request.headers.get("host")
    protocol = "wss" if "ngrok" in host or request.headers.get("x-forwarded-proto") == "https" else "ws"
    ws_url = f"{protocol}://{host}/media"
    
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Hello! You are connected to the Sunona AI assistant testing line. Since this is a trial account, please speak after connecting to the audio stream.</Say>
    <Connect>
        <Stream url="{ws_url}" />
    </Connect>
</Response>"""
    
    return Response(content=twiml, media_type="application/xml")

@app.websocket("/media")
async def media_websocket(websocket: WebSocket):
    """Handles the bidirectional audio stream from Twilio."""
    await websocket.accept()
    logger.info("WebSocket connection established with Twilio")
    
    stream_sid = None
    
    try:
        async for message in websocket.iter_text():
            data = json.loads(message)
            event = data.get("event")
            
            if event == "start":
                stream_sid = data.get("start", {}).get("streamSid")
                logger.info(f"Stream started: {stream_sid}")
                
                # Send a greeting if possible
                if SUNONA_READY:
                    greeting_text = "Hi there! I can hear you now. How can I help you today?"
                    try:
                        audio = await synthesizer.synthesize(greeting_text)
                        # Twilio expects mulaw 8000Hz usually, but if using generic media stream, 
                        # it might need conversion. Sunona synthesizer usually handles basic formats.
                        # For simple test, we just log.
                        logger.info(f"AI Greeting: {greeting_text}")
                        # In a full impl, we'd send base64 audio back here.
                    except Exception as e:
                        logger.error(f"Greeting error: {e}")

            elif event == "media":
                # Twilio sending audio payload
                # payload = data.get("media", {}).get("payload")
                # Here you would:
                # 1. Feed to Sunona Transcriber
                # 2. Feed to LLM
                # 3. Synthesize with EdgeTTS
                # 4. Send back via websocket.send_text()
                pass
                
            elif event == "stop":
                logger.info("Stream stopped")
                break
                
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket Error: {e}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
