"""
Sunona Voice AI - Gladia Transcriber

Gladia speech-to-text provider with real-time streaming.
"""

import asyncio
import logging
import os
from typing import AsyncGenerator, Dict, Optional, Any, Callable

logger = logging.getLogger(__name__)

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class GladiaTranscriber:
    """
    Gladia Speech-to-Text Transcriber.
    
    Features:
    - Real-time streaming
    - Multiple language support
    - Speaker diarization
    
    Example:
        ```python
        transcriber = GladiaTranscriber(
        if not api_key:
            api_key = os.getenv("GLADIA_API_KEY", "")
            language="en",
        )
        
        await transcriber.start_streaming()
        await transcriber.process_audio(audio_chunk)
        ```
    """
    
    BASE_URL = "https://api.gladia.io"
    WS_URL = "wss://api.gladia.io/audio/text/audio-transcription"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        language: str = "en",
        model: str = "default",
        sample_rate: int = 16000,
        encoding: str = "linear16",
        enable_diarization: bool = False,
        **kwargs,
    ):
        self.api_key = api_key or os.getenv("GLADIA_API_KEY")
        self.language = language
        self.model = model
        self.sample_rate = sample_rate
        self.encoding = encoding
        self.enable_diarization = enable_diarization
        
        self._callback: Optional[Callable] = None
        self._is_running = False
        self._ws = None
    
    def set_callback(self, callback: Callable):
        """Set callback for transcription results."""
        self._callback = callback
    
    async def transcribe(
        self,
        audio_data: bytes,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Transcribe audio data (batch mode).
        
        Args:
            audio_data: Audio bytes to transcribe
            
        Returns:
            Transcription result
        """
        if not self.api_key:
            logger.error("Gladia API key not configured")
            return {"text": "", "error": "API key not configured"}
        
        if not HTTPX_AVAILABLE:
            logger.error("httpx required for Gladia transcriber")
            return {"text": "", "error": "httpx not installed"}
        
        headers = {
            "x-gladia-key": self.api_key,
        }
        
        files = {
            "audio": ("audio.wav", audio_data, "audio/wav"),
        }
        
        data = {
            "language": self.language,
            "diarization": str(self.enable_diarization).lower(),
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.BASE_URL}/audio/text/audio-transcription",
                    headers=headers,
                    files=files,
                    data=data,
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Extract transcription from Gladia response
                    if "prediction" in result:
                        segments = result["prediction"]
                        text = " ".join(seg.get("transcription", "") for seg in segments)
                    else:
                        text = result.get("transcription", "")
                    
                    return {
                        "text": text,
                        "language": self.language,
                        "is_final": True,
                    }
                else:
                    logger.error(f"Gladia API error: {response.status_code}")
                    return {"text": "", "error": f"API error: {response.status_code}"}
        
        except Exception as e:
            logger.error(f"Gladia transcription error: {e}")
            return {"text": "", "error": str(e)}
    
    async def start_streaming(self):
        """Start real-time streaming transcription."""
        if not WEBSOCKETS_AVAILABLE:
            logger.error("websockets required for Gladia streaming")
            return
        
        self._is_running = True
        
        # Connect to WebSocket
        headers = {
            "x-gladia-key": self.api_key,
        }
        
        try:
            self._ws = await websockets.connect(
                self.WS_URL,
                extra_headers=headers,
            )
            
            # Send configuration
            config = {
                "x_gladia_key": self.api_key,
                "encoding": "WAV",
                "sample_rate": self.sample_rate,
                "language": self.language,
            }
            
            import json
            await self._ws.send(json.dumps(config))
            
            # Start receive loop
            asyncio.create_task(self._receive_loop())
            
            logger.info("Gladia streaming started")
        
        except Exception as e:
            logger.error(f"Gladia WebSocket connection error: {e}")
            self._is_running = False
    
    async def _receive_loop(self):
        """Receive transcription results from WebSocket."""
        import json
        
        while self._is_running and self._ws:
            try:
                message = await self._ws.recv()
                data = json.loads(message)
                
                if "transcription" in data:
                    result = {
                        "text": data["transcription"],
                        "is_final": data.get("type") == "final",
                        "language": self.language,
                    }
                    
                    if self._callback:
                        await self._callback(result)
            
            except Exception as e:
                if self._is_running:
                    logger.error(f"Gladia receive error: {e}")
                break
    
    async def stop_streaming(self):
        """Stop streaming mode."""
        self._is_running = False
        
        if self._ws:
            await self._ws.close()
            self._ws = None
        
        logger.info("Gladia transcriber stopped")
    
    async def process_audio(self, audio_chunk: bytes):
        """Send audio chunk to WebSocket."""
        if not self._is_running or not self._ws:
            return
        
        try:
            await self._ws.send(audio_chunk)
        except Exception as e:
            logger.error(f"Gladia send error: {e}")
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return "gladia"
