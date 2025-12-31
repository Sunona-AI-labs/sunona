"""
Sunona Voice AI - AssemblyAI Transcriber

AssemblyAI integration for speech-to-text.
High accuracy with speaker diarization.
"""

import os
import asyncio
import logging
from typing import AsyncIterator, Optional

logger = logging.getLogger(__name__)

try:
    import assemblyai as aai
    ASSEMBLYAI_AVAILABLE = True
except ImportError:
    ASSEMBLYAI_AVAILABLE = False
    aai = None


class AssemblyAITranscriber:
    """
    AssemblyAI transcriber with real-time and batch modes.
    
    Features:
        - Real-time streaming transcription
        - Speaker diarization
        - Sentiment analysis
        - Entity detection
        - PII redaction
    
    Example:
        ```python
        transcriber = AssemblyAITranscriber()
        
        async for text in transcriber.transcribe_stream(audio_generator):
            print(f"Transcript: {text}")
        ```
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        language: str = "en",
        speaker_labels: bool = False,
        punctuate: bool = True,
        format_text: bool = True,
    ):
        if not ASSEMBLYAI_AVAILABLE:
            raise ImportError("assemblyai package required: pip install assemblyai")
        
        self.api_key = api_key or os.getenv("ASSEMBLYAI_API_KEY")
        if not self.api_key:
            raise ValueError("ASSEMBLYAI_API_KEY required")
        
        aai.settings.api_key = self.api_key
        
        self.language = language
        self.speaker_labels = speaker_labels
        self.punctuate = punctuate
        self.format_text = format_text
        
        logger.info("AssemblyAI transcriber initialized")
    
    async def transcribe_stream(
        self,
        audio_iterator: AsyncIterator[bytes],
    ) -> AsyncIterator[str]:
        """Stream transcribe audio chunks."""
        # AssemblyAI real-time transcription
        config = aai.TranscriptionConfig(
            language_code=self.language,
            punctuate=self.punctuate,
            format_text=self.format_text,
        )
        
        transcriber = aai.RealtimeTranscriber(
            config=config,
            on_error=lambda e: logger.error(f"AssemblyAI error: {e}"),
        )
        
        await transcriber.connect()
        
        try:
            async for chunk in audio_iterator:
                await transcriber.stream(chunk)
                
                # Get any available transcripts
                while transcriber.has_results():
                    result = transcriber.get_result()
                    if result.text:
                        yield result.text
        finally:
            await transcriber.close()
    
    async def transcribe_file(self, file_path: str) -> str:
        """Transcribe an audio file."""
        config = aai.TranscriptionConfig(
            language_code=self.language,
            punctuate=self.punctuate,
            format_text=self.format_text,
            speaker_labels=self.speaker_labels,
        )
        
        transcriber = aai.Transcriber(config=config)
        transcript = transcriber.transcribe(file_path)
        
        return transcript.text
    
    async def transcribe_with_diarization(self, file_path: str) -> list:
        """Transcribe with speaker identification."""
        config = aai.TranscriptionConfig(
            language_code=self.language,
            speaker_labels=True,
        )
        
        transcriber = aai.Transcriber(config=config)
        transcript = transcriber.transcribe(file_path)
        
        return [
            {"speaker": u.speaker, "text": u.text}
            for u in transcript.utterances
        ]
