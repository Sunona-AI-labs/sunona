"""
Sunona Voice AI - Transcriber Module

Speech-to-Text providers for converting audio to text.
"""

from sunona.transcriber.base_transcriber import BaseTranscriber
from sunona.transcriber.deepgram_transcriber import DeepgramTranscriber
from sunona.transcriber.whisper_transcriber import WhisperTranscriber
from sunona.transcriber.google_transcriber import GoogleTranscriber
from sunona.transcriber.azure_transcriber import AzureTranscriber
from sunona.transcriber.aws_transcriber import AWSTranscriber
from sunona.transcriber.assemblyai_transcriber import AssemblyAITranscriber
from sunona.transcriber.sarvam_transcriber import SarvamTranscriber
from sunona.transcriber.gladia_transcriber import GladiaTranscriber
from sunona.transcriber.elevenlabs_transcriber import ElevenLabsTranscriber
from sunona.transcriber.smallest_transcriber import SmallestTranscriber
from sunona.transcriber.pixa_transcriber import PixaTranscriber
from sunona.transcriber.groq_transcriber import GroqTranscriber


__all__ = [
    "BaseTranscriber",
    "DeepgramTranscriber",
    "WhisperTranscriber",
    "GoogleTranscriber",
    "AzureTranscriber",
    "AWSTranscriber",
    "AssemblyAITranscriber",
    "SarvamTranscriber",
    "GladiaTranscriber",
    "ElevenLabsTranscriber",
    "SmallestTranscriber",
    "PixaTranscriber",
    "GroqTranscriber",
    "create_transcriber",
]


def create_transcriber(provider: str, **kwargs) -> BaseTranscriber:
    """
    Factory function to create a transcriber instance.
    """
    providers = {
        "deepgram": DeepgramTranscriber,
        "whisper": WhisperTranscriber,
        "openai": WhisperTranscriber,
        "google": GoogleTranscriber,
        "google_speech": GoogleTranscriber,
        "azure": AzureTranscriber,
        "azure_speech": AzureTranscriber,
        "aws": AWSTranscriber,
        "aws_transcribe": AWSTranscriber,
        "assembly": AssemblyAITranscriber,
        "assemblyai": AssemblyAITranscriber,
        "sarvam": SarvamTranscriber,
        "gladia": GladiaTranscriber,
        "elevenlabs": ElevenLabsTranscriber,
        "smallest": SmallestTranscriber,
        "pixa": PixaTranscriber,
        "groq": GroqTranscriber,
        "groq_whisper": GroqTranscriber,
    }
    
    if provider not in providers:
        raise ValueError(f"Unsupported transcriber provider: '{provider}'")
    
    return providers[provider](**kwargs)
