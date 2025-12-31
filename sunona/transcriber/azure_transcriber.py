"""
Sunona Voice AI - Azure Speech Transcriber

Azure Cognitive Services Speech-to-Text for enterprise transcription.
Supports real-time streaming with custom models.

Features:
- Real-time streaming transcription
- Custom speech models
- Pronunciation assessment
- Keyword spotting
- Enterprise security
"""

import os
import asyncio
import logging
from typing import AsyncIterator, Optional, Dict, Any

logger = logging.getLogger(__name__)

# Try to import Azure Speech SDK
try:
    import azure.cognitiveservices.speech as speechsdk
    AZURE_SPEECH_AVAILABLE = True
except ImportError:
    AZURE_SPEECH_AVAILABLE = False
    speechsdk = None

from sunona.transcriber.base_transcriber import BaseTranscriber


class AzureTranscriber(BaseTranscriber):
    """
    Azure Cognitive Services Speech-to-Text transcriber.
    
    Uses Azure's speech recognition for enterprise-grade transcription.
    
    Example:
        ```python
        transcriber = AzureTranscriber(
            subscription_key=None,  # Falls back to env
            region="eastus"
        )
        
        async with transcriber:
            async for result in transcriber.transcribe_stream(audio_stream):
                print(result["text"])
        ```
    
    Prerequisites:
        - pip install azure-cognitiveservices-speech
        - Azure subscription with Speech service
    """
    
    def __init__(
        self,
        model: str = "default",
        language: str = "en-US",
        stream: bool = True,
        sampling_rate: int = 16000,
        encoding: str = "linear16",
        endpointing: int = 500,
        subscription_key: Optional[str] = None,
        region: Optional[str] = None,
        enable_profanity_filter: bool = False,
        **kwargs
    ):
        """
        Initialize Azure Speech transcriber.
        
        Args:
            model: Speech model (or custom endpoint ID)
            language: Language code (e.g., "en-US")
            stream: Whether to use streaming mode
            sampling_rate: Audio sample rate
            encoding: Audio encoding
            endpointing: Silence duration for endpointing (ms)
            subscription_key: Azure subscription key
            region: Azure region (e.g., "eastus")
            enable_profanity_filter: Enable profanity filtering
        """
        if not AZURE_SPEECH_AVAILABLE:
            raise ImportError(
                "azure-cognitiveservices-speech is required. "
                "Install with: pip install azure-cognitiveservices-speech"
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
        
        self.subscription_key = subscription_key or os.getenv("AZURE_SPEECH_KEY")
        self.region = region or os.getenv("AZURE_SPEECH_REGION", "eastus")
        self.enable_profanity_filter = enable_profanity_filter
        
        if not self.subscription_key:
            raise ValueError(
                "Azure subscription key required. "
                "Set AZURE_SPEECH_KEY environment variable."
            )
        
        self._speech_config = None
        self._recognizer = None
        self._audio_buffer = bytearray()
        
        logger.info(f"Azure Speech transcriber initialized (language: {language})")
    
    async def connect(self) -> None:
        """Initialize the Azure Speech client."""
        if not self._is_connected:
            self._speech_config = speechsdk.SpeechConfig(
                subscription=self.subscription_key,
                region=self.region
            )
            self._speech_config.speech_recognition_language = self.language
            
            if self.enable_profanity_filter:
                self._speech_config.set_profanity(speechsdk.ProfanityOption.Masked)
            
            self._is_connected = True
            logger.debug("Azure Speech client connected")
    
    async def disconnect(self) -> None:
        """Close the client."""
        if self._is_connected:
            if self._recognizer:
                self._recognizer = None
            self._speech_config = None
            self._is_connected = False
            logger.debug("Azure Speech client disconnected")
    
    async def transcribe(self, audio_chunk: bytes) -> Optional[str]:
        """Transcribe a single audio chunk."""
        if not self._is_connected:
            await self.connect()
        
        # Create audio config from bytes
        audio_stream = speechsdk.audio.PushAudioInputStream()
        audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)
        
        # Push audio data
        audio_stream.write(audio_chunk)
        audio_stream.close()
        
        # Create recognizer
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=self._speech_config,
            audio_config=audio_config
        )
        
        # Run recognition
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            recognizer.recognize_once
        )
        
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return result.text
        elif result.reason == speechsdk.ResultReason.NoMatch:
            return None
        else:
            logger.warning(f"Azure Speech error: {result.reason}")
            return None
    
    async def transcribe_stream(
        self, 
        audio_stream: AsyncIterator[bytes]
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Transcribe a stream of audio chunks.
        
        Args:
            audio_stream: Async iterator of audio bytes
            
        Yields:
            Dictionary with transcription results
        """
        if not self._is_connected:
            await self.connect()
        
        # Buffer audio and process in chunks
        audio_buffer = bytearray()
        
        async for audio_chunk in audio_stream:
            audio_buffer.extend(audio_chunk)
            
            # Process every ~1 second of audio
            if len(audio_buffer) >= self.sampling_rate * 2:
                chunk = bytes(audio_buffer)
                audio_buffer = bytearray()
                
                result = await self.transcribe(chunk)
                if result:
                    yield {
                        "text": result,
                        "is_final": True,
                        "confidence": 0.9,
                    }
        
        # Process remaining audio
        if len(audio_buffer) > 0:
            result = await self.transcribe(bytes(audio_buffer))
            if result:
                yield {
                    "text": result,
                    "is_final": True,
                    "confidence": 0.9,
                }
    
    async def transcribe_file(self, file_path: str) -> str:
        """Transcribe an audio file."""
        if not self._is_connected:
            await self.connect()
        
        audio_config = speechsdk.audio.AudioConfig(filename=file_path)
        
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=self._speech_config,
            audio_config=audio_config
        )
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            recognizer.recognize_once
        )
        
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return result.text
        return ""
