"""
Sunona Voice AI - ElevenLabs Synthesizer

Text-to-Speech using ElevenLabs API with WebSocket streaming.
"""

import os
import json
import base64
import asyncio
import logging
from typing import AsyncIterator, Optional, Dict, Any

try:
    import websockets
    from websockets.client import WebSocketClientProtocol
except ImportError:
    websockets = None

try:
    import httpx
except ImportError:
    httpx = None

from sunona.synthesizer.base_synthesizer import BaseSynthesizer

logger = logging.getLogger(__name__)


class ElevenLabsSynthesizer(BaseSynthesizer):
    """
    ElevenLabs Text-to-Speech with WebSocket streaming.
    
    Features:
        - Real-time WebSocket streaming
        - Multiple voices (Bella, Rachel, etc.)
        - Turbo v2.5 model for low latency
        - Voice settings customization
    """
    
    BASE_URL = "https://api.elevenlabs.io/v1"
    WS_URL = "wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input"
    
    # Free voices available on ElevenLabs
    FREE_VOICES = {
        "Bella": "EXAVITQu4vr4xnSDxMaL",
        "Rachel": "21m00Tcm4TlvDq8ikWAM",
        "Domi": "AZnzlk1XvdvUeBnXmlld",
        "Elli": "MF3mGyEYCl7XYWbV9V6O",
        "Josh": "TxGEqnHWrfWFTfGW9XjX",
        "Arnold": "VR6AewLTigWG4xSOukaG",
        "Adam": "pNInz6obpgDQGcFmaJgB",
        "Sam": "yoZ06aMxZJJ28mfd3POQ",
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        voice: str = "Bella",
        voice_id: Optional[str] = None,
        model: str = "eleven_turbo_v2_5",
        stream: bool = True,
        audio_format: str = "pcm",
        sample_rate: int = 16000,
        buffer_size: int = 40,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        use_speaker_boost: bool = True,
        **kwargs
    ):
        """
        Initialize ElevenLabs synthesizer.
        
        Args:
            api_key: ElevenLabs API key (or set ELEVENLABS_API_KEY env var)
            voice: Voice name (Bella, Rachel, etc.)
            voice_id: Voice ID (overrides voice name lookup)
            model: TTS model (eleven_turbo_v2_5 recommended)
            stream: Enable streaming
            audio_format: Output format (pcm, mp3, etc.)
            sample_rate: Output sample rate
            buffer_size: Text buffer size
            stability: Voice stability (0-1)
            similarity_boost: Voice clarity (0-1)
            style: Style exaggeration (0-1)
            use_speaker_boost: Enable speaker boost
        """
        # Resolve voice_id from voice name if not provided
        if voice_id is None:
            voice_id = self.FREE_VOICES.get(voice, "EXAVITQu4vr4xnSDxMaL")
        
        super().__init__(
            voice=voice,
            voice_id=voice_id,
            model=model,
            stream=stream,
            audio_format=audio_format,
            sample_rate=sample_rate,
            buffer_size=buffer_size,
            **kwargs
        )
        
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ElevenLabs API key required. Set ELEVENLABS_API_KEY env var or pass api_key."
            )
        
        self.stability = stability
        self.similarity_boost = similarity_boost
        self.style = style
        self.use_speaker_boost = use_speaker_boost
        
        self._ws: Optional[WebSocketClientProtocol] = None
        self._http_client: Optional[httpx.AsyncClient] = None
        self._receive_task: Optional[asyncio.Task] = None
        self._audio_queue: asyncio.Queue = asyncio.Queue()
    
    def _get_output_format(self) -> str:
        """Get the ElevenLabs output format string."""
        if self.audio_format == "pcm":
            if self.sample_rate == 16000:
                return "pcm_16000"
            elif self.sample_rate == 22050:
                return "pcm_22050"
            elif self.sample_rate == 24000:
                return "pcm_24000"
            elif self.sample_rate == 44100:
                return "pcm_44100"
            else:
                return "pcm_16000"
        elif self.audio_format == "mp3":
            return "mp3_44100_128"
        elif self.audio_format == "mulaw":
            return "ulaw_8000"
        else:
            return "pcm_16000"
    
    def _build_ws_url(self) -> str:
        """Build the WebSocket URL with parameters."""
        base = self.WS_URL.format(voice_id=self.voice_id)
        params = [
            f"model_id={self.model}",
            f"output_format={self._get_output_format()}",
        ]
        return f"{base}?{'&'.join(params)}"
    
    async def connect(self) -> None:
        """Connect to ElevenLabs WebSocket API."""
        if websockets is None:
            raise ImportError("websockets package required. Install with: pip install websockets")
        
        if self._is_connected:
            logger.warning("Already connected to ElevenLabs")
            return
        
        try:
            url = self._build_ws_url()
            
            self._ws = await websockets.connect(
                url,
                additional_headers={"xi-api-key": self.api_key},
                ping_interval=20,
                ping_timeout=10,
            )
            
            # Send initial configuration
            init_message = {
                "text": " ",  # Initial space to prime the connection
                "voice_settings": {
                    "stability": self.stability,
                    "similarity_boost": self.similarity_boost,
                    "style": self.style,
                    "use_speaker_boost": self.use_speaker_boost,
                },
                "generation_config": {
                    "chunk_length_schedule": [120, 160, 250, 290],
                },
                "xi_api_key": self.api_key,
            }
            
            await self._ws.send(json.dumps(init_message))
            
            self._is_connected = True
            
            # Start receive loop
            self._receive_task = asyncio.create_task(self._receive_loop())
            
            logger.info("Connected to ElevenLabs WebSocket")
            
        except Exception as e:
            logger.error(f"Failed to connect to ElevenLabs: {e}")
            self._is_connected = False
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from ElevenLabs WebSocket API."""
        if not self._is_connected:
            return
        
        self._is_connected = False
        
        # Cancel receive task
        if self._receive_task and not self._receive_task.done():
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
        
        # Close WebSocket
        if self._ws:
            try:
                # Send end of sequence
                await self._ws.send(json.dumps({"text": ""}))
                await self._ws.close()
            except Exception as e:
                logger.debug(f"Error closing ElevenLabs WebSocket: {e}")
            finally:
                self._ws = None
        
        # Close HTTP client
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()
            self._http_client = None
        
        logger.info("Disconnected from ElevenLabs")
    
    async def _receive_loop(self) -> None:
        """Background loop to receive audio chunks."""
        try:
            while self._is_connected and self._ws:
                try:
                    message = await self._ws.recv()
                    data = json.loads(message)
                    
                    # Check for audio data
                    audio_b64 = data.get("audio")
                    if audio_b64:
                        audio_bytes = base64.b64decode(audio_b64)
                        await self._audio_queue.put(audio_bytes)
                    
                    # Check for completion
                    if data.get("isFinal"):
                        await self._audio_queue.put(None)  # Signal end
                        break
                        
                except websockets.ConnectionClosed:
                    logger.info("ElevenLabs connection closed")
                    break
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON from ElevenLabs: {e}")
                    
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in ElevenLabs receive loop: {e}")
    
    async def synthesize(self, text: str) -> bytes:
        """
        Synthesize text to audio using REST API.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio bytes
        """
        if httpx is None:
            raise ImportError("httpx package required. Install with: pip install httpx")
        
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers={"xi-api-key": self.api_key},
                timeout=httpx.Timeout(30.0),
            )
        
        url = f"/text-to-speech/{self.voice_id}"
        params = {
            "output_format": self._get_output_format(),
        }
        
        body = {
            "text": text,
            "model_id": self.model,
            "voice_settings": {
                "stability": self.stability,
                "similarity_boost": self.similarity_boost,
                "style": self.style,
                "use_speaker_boost": self.use_speaker_boost,
            },
        }
        
        try:
            response = await self._http_client.post(url, params=params, json=body)
            response.raise_for_status()
            return response.content
            
        except Exception as e:
            logger.error(f"ElevenLabs synthesis error: {e}")
            raise
    
    async def synthesize_stream(
        self, 
        text_stream: AsyncIterator[str]
    ) -> AsyncIterator[bytes]:
        """
        Stream synthesis of text chunks.
        
        Args:
            text_stream: Async iterator of text chunks
            
        Yields:
            Audio bytes chunks
        """
        if not self._is_connected:
            await self.connect()
        
        # Start sending text in background
        send_task = asyncio.create_task(self._send_text_stream(text_stream))
        
        try:
            while True:
                try:
                    audio = await asyncio.wait_for(
                        self._audio_queue.get(),
                        timeout=30.0
                    )
                    
                    if audio is None:  # End signal
                        break
                    
                    yield audio
                    
                except asyncio.TimeoutError:
                    if send_task.done():
                        break
                    logger.warning("ElevenLabs audio timeout")
                    
        finally:
            if not send_task.done():
                send_task.cancel()
                try:
                    await send_task
                except asyncio.CancelledError:
                    pass
    
    async def _send_text_stream(self, text_stream: AsyncIterator[str]) -> None:
        """Send text stream to ElevenLabs."""
        try:
            async for text_chunk in text_stream:
                if not self._is_connected or not self._ws:
                    break
                
                if text_chunk.strip():
                    message = {"text": text_chunk}
                    await self._ws.send(json.dumps(message))
            
            # Send end of text signal
            if self._ws and self._is_connected:
                await self._ws.send(json.dumps({"text": ""}))
                
        except Exception as e:
            logger.error(f"Error sending text to ElevenLabs: {e}")
    
    async def speak(self, text: str) -> AsyncIterator[bytes]:
        """
        Convenience method to synthesize and stream text.
        
        Args:
            text: Text to speak
            
        Yields:
            Audio bytes chunks
        """
        if self.stream:
            async def text_gen():
                yield text
            
            async for chunk in self.synthesize_stream(text_gen()):
                yield chunk
        else:
            audio = await self.synthesize(text)
            yield audio
    
    @classmethod
    def list_free_voices(cls) -> Dict[str, str]:
        """List available free voices."""
        return cls.FREE_VOICES.copy()
