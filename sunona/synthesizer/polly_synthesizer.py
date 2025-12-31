"""
Sunona Voice AI - AWS Polly Synthesizer

Amazon Polly for neural text-to-speech synthesis.
Supports NTTS (Neural TTS) for natural-sounding voices.

Features:
- Neural and standard voices
- SSML support
- Speech marks (word timing)
- Multiple audio formats
- Long-form synthesis
"""

import os
import asyncio
import logging
from typing import AsyncIterator, Optional, Dict, Any

logger = logging.getLogger(__name__)

# Try to import boto3
try:
    import boto3
    from botocore.config import Config
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    boto3 = None
    Config = None

from sunona.synthesizer.base_synthesizer import BaseSynthesizer


class PollySynthesizer(BaseSynthesizer):
    """
    AWS Polly text-to-speech synthesizer.
    
    Uses Amazon Polly for natural neural voices with 
    extensive SSML support.
    
    Example:
        ```python
        synth = PollySynthesizer(
            voice_id="Joanna",
            engine="neural"
        )
        
        async with synth:
            async for audio in synth.synthesize("Hello, world!"):
                play(audio)
        ```
    
    Prerequisites:
        - pip install boto3
        - AWS credentials configured
    """
    
    # Popular Polly neural voices
    VOICES = {
        # US English
        "Joanna": {"language": "en-US", "gender": "Female", "engine": "neural"},
        "Matthew": {"language": "en-US", "gender": "Male", "engine": "neural"},
        "Ivy": {"language": "en-US", "gender": "Female", "engine": "neural"},
        "Kendra": {"language": "en-US", "gender": "Female", "engine": "neural"},
        "Kimberly": {"language": "en-US", "gender": "Female", "engine": "neural"},
        "Salli": {"language": "en-US", "gender": "Female", "engine": "neural"},
        "Joey": {"language": "en-US", "gender": "Male", "engine": "neural"},
        "Justin": {"language": "en-US", "gender": "Male", "engine": "neural"},
        # British English
        "Amy": {"language": "en-GB", "gender": "Female", "engine": "neural"},
        "Brian": {"language": "en-GB", "gender": "Male", "engine": "neural"},
        "Emma": {"language": "en-GB", "gender": "Female", "engine": "neural"},
        # Other languages
        "Léa": {"language": "fr-FR", "gender": "Female", "engine": "neural"},
        "Vicki": {"language": "de-DE", "gender": "Female", "engine": "neural"},
        "Lucia": {"language": "es-ES", "gender": "Female", "engine": "neural"},
        "Takumi": {"language": "ja-JP", "gender": "Male", "engine": "neural"},
    }
    
    def __init__(
        self,
        voice_id: str = "Joanna",
        engine: str = "neural",
        output_format: str = "pcm",
        sample_rate: int = 16000,
        region: Optional[str] = None,
        aws_access_key: Optional[str] = None,
        aws_secret_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize AWS Polly synthesizer.
        
        Args:
            voice_id: Polly voice ID (e.g., "Joanna", "Matthew")
            engine: Engine type ("neural" or "standard")
            output_format: Audio format ("pcm", "mp3", "ogg_vorbis")
            sample_rate: Audio sample rate
            region: AWS region
            aws_access_key: AWS access key
            aws_secret_key: AWS secret key
        """
        if not BOTO3_AVAILABLE:
            raise ImportError(
                "boto3 is required for AWS Polly. "
                "Install with: pip install boto3"
            )
        
        super().__init__(**kwargs)
        
        self.voice_id = voice_id
        self.engine = engine
        self.output_format = output_format
        self.sample_rate = sample_rate
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.aws_access_key = aws_access_key or os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_key = aws_secret_key or os.getenv("AWS_SECRET_ACCESS_KEY")
        
        self._client = None
        
        logger.info(f"AWS Polly synthesizer initialized (voice: {voice_id})")
    
    async def connect(self) -> None:
        """Initialize the Polly client."""
        if not self._is_connected:
            config = Config(
                region_name=self.region,
                retries={'max_attempts': 3}
            )
            
            session_kwargs = {}
            if self.aws_access_key and self.aws_secret_key:
                session_kwargs = {
                    'aws_access_key_id': self.aws_access_key,
                    'aws_secret_access_key': self.aws_secret_key,
                }
            
            self._client = boto3.client(
                'polly',
                config=config,
                **session_kwargs
            )
            
            self._is_connected = True
            logger.debug("AWS Polly client connected")
    
    async def disconnect(self) -> None:
        """Close the client."""
        if self._is_connected:
            self._client = None
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
        
        # Determine sample rate format for Polly
        sample_rate_str = str(self.sample_rate)
        
        params = {
            'Text': text,
            'VoiceId': self.voice_id,
            'Engine': self.engine,
            'OutputFormat': self.output_format,
        }
        
        if self.output_format == 'pcm':
            params['SampleRate'] = sample_rate_str
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self._client.synthesize_speech(**params)
        )
        
        # Read audio stream
        audio_stream = response['AudioStream']
        
        # Stream in chunks
        chunk_size = 4096
        while True:
            chunk = audio_stream.read(chunk_size)
            if not chunk:
                break
            yield chunk
    
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
        
        params = {
            'Text': ssml,
            'TextType': 'ssml',
            'VoiceId': self.voice_id,
            'Engine': self.engine,
            'OutputFormat': self.output_format,
        }
        
        if self.output_format == 'pcm':
            params['SampleRate'] = str(self.sample_rate)
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self._client.synthesize_speech(**params)
        )
        
        audio_stream = response['AudioStream']
        
        chunk_size = 4096
        while True:
            chunk = audio_stream.read(chunk_size)
            if not chunk:
                break
            yield chunk
    
    async def get_speech_marks(self, text: str) -> list:
        """
        Get speech marks for timing information.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of speech marks with timing
        """
        if not self._is_connected:
            await self.connect()
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self._client.synthesize_speech(
                Text=text,
                VoiceId=self.voice_id,
                Engine=self.engine,
                OutputFormat='json',
                SpeechMarkTypes=['word', 'sentence']
            )
        )
        
        import json
        marks = []
        for line in response['AudioStream'].read().decode().strip().split('\n'):
            if line:
                marks.append(json.loads(line))
        
        return marks
    
    @classmethod
    def list_voices(cls) -> Dict[str, Dict[str, str]]:
        """List available voices."""
        return cls.VOICES
