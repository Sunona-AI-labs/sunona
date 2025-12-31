"""
Sunona Voice AI - OpenAI Whisper Transcriber

High-accuracy speech-to-text using OpenAI's Whisper API.
Supports both real-time streaming and batch transcription.

Features:
- Whisper-1 model for high accuracy
- Automatic language detection
- Timestamp generation
- Word-level timestamps
- Low-latency chunked processing
"""

import os
import io
import asyncio
import logging
from typing import AsyncIterator, Optional, Dict, Any

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncOpenAI = None

from sunona.transcriber.base_transcriber import BaseTranscriber

logger = logging.getLogger(__name__)


class WhisperTranscriber(BaseTranscriber):
    """
    OpenAI Whisper transcriber for high-accuracy speech recognition.
    
    Uses the Whisper API for transcription with support for:
    - 97+ languages with auto-detection
    - Word-level timestamps
    - Chunked processing for low latency
    
    Example:
        ```python
        transcriber = WhisperTranscriber()
        
        async with transcriber:
            await transcriber.send_audio(audio_bytes)
            result = await transcriber.get_transcription()
            print(result["text"])
        ```
    """
    
    SUPPORTED_FORMATS = ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm", "flac"]
    MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB
    
    def __init__(
        self,
        model: str = "whisper-1",
        language: str = "en",
        stream: bool = True,
        sampling_rate: int = 16000,
        encoding: str = "linear16",
        endpointing: int = 500,
        api_key: Optional[str] = None,
        response_format: str = "json",
        temperature: float = 0.0,
        prompt: Optional[str] = None,
        chunk_duration: float = 1.0,
        **kwargs
    ):
        """
        Initialize the Whisper transcriber.
        
        Args:
            model: Whisper model to use (currently only "whisper-1")
            language: Language code (ISO-639-1), None for auto-detect
            stream: Whether to use pseudo-streaming (chunked processing)
            sampling_rate: Audio sample rate in Hz
            encoding: Audio encoding format
            endpointing: Silence duration (ms) before finalizing
            api_key: OpenAI API key (or OPENAI_API_KEY env var)
            response_format: Response format ("json", "text", "srt", "verbose_json", "vtt")
            temperature: Sampling temperature for decoding
            prompt: Optional prompt to guide transcription
            chunk_duration: Duration of audio chunks for streaming (seconds)
            **kwargs: Additional options
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "openai is required for WhisperTranscriber. "
                "Install with: pip install openai"
            )
        
        super().__init__(
            model=model,
            language=language,
            stream=stream,
            sampling_rate=sampling_rate,
            encoding=encoding,
            endpointing=endpointing,
            **kwargs
        )
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.response_format = response_format
        self.temperature = temperature
        self.prompt = prompt
        self.chunk_duration = chunk_duration
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self._client: Optional[AsyncOpenAI] = None
        self._audio_buffer = bytearray()
        self._chunk_size = int(sampling_rate * chunk_duration * 2)  # 16-bit audio
        
        logger.info(f"Whisper transcriber initialized (language: {language})")
    
    async def connect(self) -> None:
        """Initialize the OpenAI client."""
        if not self._is_connected:
            self._client = AsyncOpenAI(api_key=self.api_key)
            self._is_connected = True
            self._audio_buffer = bytearray()
            logger.debug("Whisper transcriber connected")
    
    async def disconnect(self) -> None:
        """Close the OpenAI client."""
        if self._is_connected:
            if self._client:
                await self._client.close()
                self._client = None
            self._is_connected = False
            self._audio_buffer = bytearray()
            logger.debug("Whisper transcriber disconnected")
    
    async def transcribe(self, audio_chunk: bytes) -> Optional[str]:
        """
        Transcribe a single audio chunk.
        
        Accumulates audio until chunk_duration is reached, then transcribes.
        
        Args:
            audio_chunk: Raw audio bytes (PCM 16-bit)
            
        Returns:
            Transcribed text or None if buffer not full
        """
        if not self._is_connected:
            await self.connect()
        
        self._audio_buffer.extend(audio_chunk)
        
        # Check if we have enough audio for a chunk
        if len(self._audio_buffer) >= self._chunk_size:
            chunk_audio = bytes(self._audio_buffer[:self._chunk_size])
            self._audio_buffer = self._audio_buffer[self._chunk_size:]
            
            return await self._transcribe_audio(chunk_audio)
        
        return None
    
    async def _transcribe_audio(self, audio_data: bytes) -> str:
        """Transcribe audio bytes using Whisper API."""
        try:
            # Convert PCM to WAV for API
            wav_data = self._pcm_to_wav(audio_data)
            
            # Create file-like object
            audio_file = io.BytesIO(wav_data)
            audio_file.name = "audio.wav"
            
            # Call Whisper API
            params = {
                "model": self.model,
                "file": audio_file,
                "response_format": self.response_format,
                "temperature": self.temperature,
            }
            
            if self.language:
                params["language"] = self.language
            
            if self.prompt:
                params["prompt"] = self.prompt
            
            response = await self._client.audio.transcriptions.create(**params)
            
            # Extract text based on response format
            if self.response_format == "json" or self.response_format == "verbose_json":
                return response.text if hasattr(response, 'text') else str(response)
            else:
                return str(response)
                
        except Exception as e:
            logger.error(f"Whisper transcription error: {e}")
            return ""
    
    def _pcm_to_wav(self, pcm_data: bytes) -> bytes:
        """Convert raw PCM to WAV format."""
        import struct
        
        num_channels = 1
        sample_width = 2  # 16-bit
        
        # WAV header
        wav_header = struct.pack(
            '<4sI4s4sIHHIIHH4sI',
            b'RIFF',
            len(pcm_data) + 36,
            b'WAVE',
            b'fmt ',
            16,  # Subchunk1Size
            1,   # AudioFormat (PCM)
            num_channels,
            self.sampling_rate,
            self.sampling_rate * num_channels * sample_width,  # ByteRate
            num_channels * sample_width,  # BlockAlign
            sample_width * 8,  # BitsPerSample
            b'data',
            len(pcm_data)
        )
        
        return wav_header + pcm_data
    
    async def transcribe_stream(
        self, 
        audio_stream: AsyncIterator[bytes]
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Transcribe a stream of audio chunks.
        
        Args:
            audio_stream: Async iterator of audio bytes
            
        Yields:
            Dictionary with transcription results:
                - text: The transcribed text
                - is_final: True for finalized results
                - confidence: Confidence score (always 1.0 for Whisper)
        """
        if not self._is_connected:
            await self.connect()
        
        async for audio_chunk in audio_stream:
            text = await self.transcribe(audio_chunk)
            if text:
                yield {
                    "text": text,
                    "is_final": True,
                    "confidence": 1.0,
                }
        
        # Flush remaining audio
        if len(self._audio_buffer) > 0:
            text = await self._transcribe_audio(bytes(self._audio_buffer))
            if text:
                yield {
                    "text": text,
                    "is_final": True,
                    "confidence": 1.0,
                }
            self._audio_buffer = bytearray()
    
    async def transcribe_file(self, file_path: str) -> str:
        """
        Transcribe an audio file.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Transcribed text
        """
        if not self._is_connected:
            await self.connect()
        
        try:
            with open(file_path, "rb") as audio_file:
                params = {
                    "model": self.model,
                    "file": audio_file,
                    "response_format": self.response_format,
                    "temperature": self.temperature,
                }
                
                if self.language:
                    params["language"] = self.language
                
                if self.prompt:
                    params["prompt"] = self.prompt
                
                response = await self._client.audio.transcriptions.create(**params)
                
                return response.text if hasattr(response, 'text') else str(response)
                
        except Exception as e:
            logger.error(f"File transcription error: {e}")
            raise
    
    async def flush(self) -> Optional[str]:
        """Flush and transcribe any remaining buffered audio."""
        if len(self._audio_buffer) > 0:
            text = await self._transcribe_audio(bytes(self._audio_buffer))
            self._audio_buffer = bytearray()
            return text
        return None
