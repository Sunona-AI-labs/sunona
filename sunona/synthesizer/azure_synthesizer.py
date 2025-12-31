"""
Sunona Voice AI - Azure TTS Synthesizer

Azure Cognitive Services Text-to-Speech for enterprise synthesis.
Supports neural voices with SSML and custom voice models.

Features:
- Neural voices in 140+ languages
- SSML support with prosody control
- Custom neural voice
- Viseme support for lip-sync
- Audio effects
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

from sunona.synthesizer.base_synthesizer import BaseSynthesizer


class AzureSynthesizer(BaseSynthesizer):
    """
    Azure Cognitive Services Text-to-Speech synthesizer.
    
    Uses Azure's neural voices for natural-sounding speech.
    
    Example:
        ```python
        synth = AzureSynthesizer(
            voice_name="en-US-JennyNeural",
            subscription_key=None,  # Falls back to env
        )
        
        async with synth:
            async for audio in synth.synthesize("Hello!"):
                play(audio)
        ```
    
    Prerequisites:
        - pip install azure-cognitiveservices-speech
        - Azure subscription with Speech service
    """
    
    # Popular Azure neural voices
    VOICES = {
        # US English
        "en-US-JennyNeural": {"gender": "Female", "style": "friendly"},
        "en-US-AriaNeural": {"gender": "Female", "style": "chat"},
        "en-US-GuyNeural": {"gender": "Male", "style": "newscast"},
        "en-US-DavisNeural": {"gender": "Male", "style": "default"},
        "en-US-JaneNeural": {"gender": "Female", "style": "default"},
        "en-US-JasonNeural": {"gender": "Male", "style": "default"},
        # British English
        "en-GB-SoniaNeural": {"gender": "Female", "style": "default"},
        "en-GB-RyanNeural": {"gender": "Male", "style": "default"},
        # Other languages
        "de-DE-KatjaNeural": {"gender": "Female", "style": "default"},
        "fr-FR-DeniseNeural": {"gender": "Female", "style": "default"},
        "es-ES-ElviraNeural": {"gender": "Female", "style": "default"},
        "ja-JP-NanamiNeural": {"gender": "Female", "style": "default"},
        "zh-CN-XiaoxiaoNeural": {"gender": "Female", "style": "chat"},
    }
    
    def __init__(
        self,
        voice_name: str = "en-US-JennyNeural",
        output_format: str = "audio-16khz-32kbitrate-mono-mp3",
        sample_rate: int = 16000,
        subscription_key: Optional[str] = None,
        region: Optional[str] = None,
        speaking_rate: float = 1.0,
        pitch: str = "default",
        **kwargs
    ):
        """
        Initialize Azure TTS synthesizer.
        
        Args:
            voice_name: Azure voice name (e.g., "en-US-JennyNeural")
            output_format: Audio output format
            sample_rate: Audio sample rate
            subscription_key: Azure subscription key
            region: Azure region (e.g., "eastus")
            speaking_rate: Speech rate (0.5-2.0)
            pitch: Voice pitch ("default", "low", "high", or percentage)
        """
        if not AZURE_SPEECH_AVAILABLE:
            raise ImportError(
                "azure-cognitiveservices-speech is required. "
                "Install with: pip install azure-cognitiveservices-speech"
            )
        
        super().__init__(**kwargs)
        
        self.voice_name = voice_name
        self.output_format = output_format
        self.sample_rate = sample_rate
        self.speaking_rate = speaking_rate
        self.pitch = pitch
        
        self.subscription_key = subscription_key or os.getenv("AZURE_SPEECH_KEY")
        self.region = region or os.getenv("AZURE_SPEECH_REGION", "eastus")
        
        if not self.subscription_key:
            raise ValueError(
                "Azure subscription key required. "
                "Set AZURE_SPEECH_KEY environment variable."
            )
        
        self._speech_config = None
        self._synthesizer = None
        
        logger.info(f"Azure TTS synthesizer initialized (voice: {voice_name})")
    
    async def connect(self) -> None:
        """Initialize the Azure Speech client."""
        if not self._is_connected:
            self._speech_config = speechsdk.SpeechConfig(
                subscription=self.subscription_key,
                region=self.region
            )
            
            # Set voice
            self._speech_config.speech_synthesis_voice_name = self.voice_name
            
            # Set output format
            format_mapping = {
                "audio-16khz-32kbitrate-mono-mp3": speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3,
                "audio-16khz-128kbitrate-mono-mp3": speechsdk.SpeechSynthesisOutputFormat.Audio16Khz128KBitRateMonoMp3,
                "audio-24khz-160kbitrate-mono-mp3": speechsdk.SpeechSynthesisOutputFormat.Audio24Khz160KBitRateMonoMp3,
                "riff-16khz-16bit-mono-pcm": speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm,
                "raw-16khz-16bit-mono-pcm": speechsdk.SpeechSynthesisOutputFormat.Raw16Khz16BitMonoPcm,
            }
            
            if self.output_format in format_mapping:
                self._speech_config.set_speech_synthesis_output_format(
                    format_mapping[self.output_format]
                )
            
            self._synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self._speech_config,
                audio_config=None  # Return audio data
            )
            
            self._is_connected = True
            logger.debug("Azure TTS client connected")
    
    async def disconnect(self) -> None:
        """Close the client."""
        if self._is_connected:
            self._synthesizer = None
            self._speech_config = None
            self._is_connected = False
    
    async def synthesize(self, text: str) -> AsyncIterator[bytes]:
        """
        Synthesize text to audio.
        
        Args:
            text: Text to synthesize
            
        Yields:
            Audio bytes
        """
        if not self._is_connected:
            await self.connect()
        
        # Create SSML with prosody if needed
        if self.speaking_rate != 1.0 or self.pitch != "default":
            ssml = self._create_ssml(text)
            async for chunk in self.synthesize_ssml(ssml):
                yield chunk
            return
        
        # Use plain text synthesis
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self._synthesizer.speak_text_async(text).get()
        )
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            # Yield audio in chunks
            audio_data = result.audio_data
            chunk_size = 4096
            
            for i in range(0, len(audio_data), chunk_size):
                yield audio_data[i:i + chunk_size]
        else:
            logger.error(f"Azure TTS error: {result.reason}")
    
    def _create_ssml(self, text: str) -> str:
        """Create SSML with prosody settings."""
        rate = f"{int(self.speaking_rate * 100)}%"
        
        ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
    <voice name="{self.voice_name}">
        <prosody rate="{rate}" pitch="{self.pitch}">
            {text}
        </prosody>
    </voice>
</speak>"""
        return ssml
    
    async def synthesize_ssml(self, ssml: str) -> AsyncIterator[bytes]:
        """
        Synthesize SSML to audio.
        
        Args:
            ssml: SSML markup to synthesize
            
        Yields:
            Audio bytes
        """
        if not self._is_connected:
            await self.connect()
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self._synthesizer.speak_ssml_async(ssml).get()
        )
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            audio_data = result.audio_data
            chunk_size = 4096
            
            for i in range(0, len(audio_data), chunk_size):
                yield audio_data[i:i + chunk_size]
        else:
            logger.error(f"Azure TTS SSML error: {result.reason}")
    
    @classmethod
    def list_voices(cls) -> Dict[str, Dict[str, str]]:
        """List available voices."""
        return cls.VOICES
