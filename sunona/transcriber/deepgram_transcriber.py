"""
Sunona Voice AI - Deepgram Transcriber

Real-time speech-to-text using Deepgram's WebSocket API.
"""

import os
import json
import asyncio
import logging
from typing import AsyncIterator, Optional, Dict, Any

try:
    import websockets
    from websockets.client import WebSocketClientProtocol
except ImportError:
    websockets = None

from sunona.transcriber.base_transcriber import BaseTranscriber

logger = logging.getLogger(__name__)


class DeepgramTranscriber(BaseTranscriber):
    """
    Deepgram real-time transcription using WebSocket streaming.
    
    Features:
        - Real-time streaming transcription
        - Interim and final results
        - Automatic punctuation
        - Multiple language support
        - Utterance detection
    """
    
    DEEPGRAM_WS_URL = "wss://api.deepgram.com/v1/listen"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "nova-2",
        language: str = "en",
        stream: bool = True,
        sampling_rate: int = 16000,
        encoding: str = "linear16",
        endpointing: int = 500,
        punctuate: bool = True,
        interim_results: bool = True,
        utterance_end_ms: int = 1000,
        vad_events: bool = True,
        smart_format: bool = True,
        **kwargs
    ):
        """
        Initialize Deepgram transcriber.
        
        Args:
            api_key: Deepgram API key (or set DEEPGRAM_API_KEY env var)
            model: Deepgram model (nova-2, nova-2-general, etc.)
            language: Language code
            stream: Enable streaming
            sampling_rate: Audio sample rate in Hz
            encoding: Audio encoding (linear16, mulaw, etc.)
            endpointing: Silence duration (ms) before finalizing
            punctuate: Add punctuation to output
            interim_results: Return partial results
            utterance_end_ms: Utterance end silence threshold
            vad_events: Enable voice activity detection events
            smart_format: Enable smart formatting
        """
        super().__init__(
            model=model,
            language=language,
            stream=stream,
            sampling_rate=sampling_rate,
            encoding=encoding,
            endpointing=endpointing,
            **kwargs
        )
        
        self.api_key = api_key or os.getenv("DEEPGRAM_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Deepgram API key required. Set DEEPGRAM_API_KEY env var or pass api_key."
            )
        
        self.punctuate = punctuate
        self.interim_results = interim_results
        self.utterance_end_ms = utterance_end_ms
        self.vad_events = vad_events
        self.smart_format = smart_format
        
        self._ws: Optional[WebSocketClientProtocol] = None
        self._receive_task: Optional[asyncio.Task] = None
        self._keep_alive_task: Optional[asyncio.Task] = None
    
    def _build_url(self) -> str:
        """Build the Deepgram WebSocket URL with parameters."""
        params = [
            f"model={self.model}",
            f"language={self.language}",
            f"encoding={self.encoding}",
            f"sample_rate={self.sampling_rate}",
            f"channels=1",
            f"punctuate={str(self.punctuate).lower()}",
            f"interim_results={str(self.interim_results).lower()}",
            f"utterance_end_ms={self.utterance_end_ms}",
            f"vad_events={str(self.vad_events).lower()}",
            f"smart_format={str(self.smart_format).lower()}",
        ]
        
        if self.endpointing:
            params.append(f"endpointing={self.endpointing}")
        
        return f"{self.DEEPGRAM_WS_URL}?{'&'.join(params)}"
    
    async def connect(self) -> None:
        """Connect to Deepgram WebSocket API."""
        if websockets is None:
            raise ImportError("websockets package required. Install with: pip install websockets")
        
        if self._is_connected:
            logger.warning("Already connected to Deepgram")
            return
        
        try:
            url = self._build_url()
            headers = {"Authorization": f"Token {self.api_key}"}
            
            self._ws = await websockets.connect(
                url,
                additional_headers=headers,
                ping_interval=20,
                ping_timeout=10,
            )
            
            self._is_connected = True
            
            # Start background tasks
            self._receive_task = asyncio.create_task(self._receive_loop())
            self._keep_alive_task = asyncio.create_task(self._keep_alive_loop())
            
            logger.info("Connected to Deepgram WebSocket")
            
        except Exception as e:
            logger.error(f"Failed to connect to Deepgram: {e}")
            self._is_connected = False
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from Deepgram WebSocket API."""
        if not self._is_connected:
            return
        
        self._is_connected = False
        
        # Cancel background tasks
        if self._receive_task and not self._receive_task.done():
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
        
        if self._keep_alive_task and not self._keep_alive_task.done():
            self._keep_alive_task.cancel()
            try:
                await self._keep_alive_task
            except asyncio.CancelledError:
                pass
        
        # Close WebSocket
        if self._ws:
            try:
                # Send close message
                await self._ws.send(json.dumps({"type": "CloseStream"}))
                await self._ws.close()
            except Exception as e:
                logger.debug(f"Error during WebSocket close: {e}")
            finally:
                self._ws = None
        
        logger.info("Disconnected from Deepgram")
    
    async def _receive_loop(self) -> None:
        """Background loop to receive transcription results."""
        try:
            while self._is_connected and self._ws:
                try:
                    message = await self._ws.recv()
                    data = json.loads(message)
                    
                    # Process different message types
                    msg_type = data.get("type", "")
                    
                    if msg_type == "Results":
                        result = self._parse_result(data)
                        if result:
                            await self._output_queue.put(result)
                    
                    elif msg_type == "UtteranceEnd":
                        await self._output_queue.put({
                            "type": "utterance_end",
                            "text": "",
                            "is_final": True,
                        })
                    
                    elif msg_type == "SpeechStarted":
                        await self._output_queue.put({
                            "type": "speech_started",
                        })
                    
                    elif msg_type == "Metadata":
                        logger.debug(f"Deepgram metadata: {data}")
                    
                    elif msg_type == "Error":
                        logger.error(f"Deepgram error: {data}")
                
                except websockets.ConnectionClosed:
                    logger.info("Deepgram connection closed")
                    break
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON from Deepgram: {e}")
                    
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in Deepgram receive loop: {e}")
    
    async def _keep_alive_loop(self) -> None:
        """Send periodic keep-alive messages."""
        try:
            while self._is_connected and self._ws:
                await asyncio.sleep(10)
                if self._ws and self._is_connected:
                    try:
                        await self._ws.send(json.dumps({"type": "KeepAlive"}))
                    except Exception:
                        pass
        except asyncio.CancelledError:
            pass
    
    def _parse_result(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse Deepgram result message."""
        try:
            channel = data.get("channel", {})
            alternatives = channel.get("alternatives", [])
            
            if not alternatives:
                return None
            
            best = alternatives[0]
            transcript = best.get("transcript", "").strip()
            
            if not transcript:
                return None
            
            return {
                "type": "transcription",
                "text": transcript,
                "is_final": data.get("is_final", False),
                "speech_final": data.get("speech_final", False),
                "confidence": best.get("confidence", 0.0),
                "words": best.get("words", []),
                "start": data.get("start", 0),
                "duration": data.get("duration", 0),
            }
            
        except Exception as e:
            logger.error(f"Error parsing Deepgram result: {e}")
            return None
    
    async def transcribe(self, audio_chunk: bytes) -> Optional[str]:
        """
        Send audio chunk for transcription.
        
        Args:
            audio_chunk: Raw audio bytes
            
        Returns:
            Transcribed text if available, None otherwise
        """
        if not self._is_connected or not self._ws:
            raise RuntimeError("Not connected to Deepgram. Call connect() first.")
        
        try:
            await self._ws.send(audio_chunk)
            
            # Try to get a result without blocking
            if not self._output_queue.empty():
                result = await self._output_queue.get()
                if result.get("type") == "transcription":
                    return result.get("text")
            
            return None
            
        except Exception as e:
            logger.error(f"Error sending audio to Deepgram: {e}")
            raise
    
    async def transcribe_stream(
        self, 
        audio_stream: AsyncIterator[bytes]
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Transcribe a stream of audio chunks.
        
        Args:
            audio_stream: Async iterator of audio bytes
            
        Yields:
            Transcription results
        """
        if not self._is_connected:
            await self.connect()
        
        # Start sending audio
        send_task = asyncio.create_task(self._send_audio_stream(audio_stream))
        
        try:
            while True:
                result = await self.get_transcription(timeout=30.0)
                if result is None:
                    # Check if send task completed
                    if send_task.done():
                        break
                    continue
                
                yield result
                
                # Check for end of utterance/stream
                if result.get("type") == "utterance_end":
                    break
                    
        finally:
            if not send_task.done():
                send_task.cancel()
                try:
                    await send_task
                except asyncio.CancelledError:
                    pass
    
    async def _send_audio_stream(self, audio_stream: AsyncIterator[bytes]) -> None:
        """Send audio stream to Deepgram."""
        try:
            async for chunk in audio_stream:
                if not self._is_connected:
                    break
                await self.transcribe(chunk)
        except Exception as e:
            logger.error(f"Error in audio stream: {e}")
