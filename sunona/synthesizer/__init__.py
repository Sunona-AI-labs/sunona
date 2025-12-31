"""
Sunona Voice AI - Synthesizer Module

Text-to-Speech providers for converting text to audio.
"""

from sunona.synthesizer.base_synthesizer import BaseSynthesizer
from sunona.synthesizer.elevenlabs_synthesizer import ElevenLabsSynthesizer
from sunona.synthesizer.openai_synthesizer import OpenAISynthesizer
from sunona.synthesizer.deepgram_synthesizer import DeepgramSynthesizer
from sunona.synthesizer.polly_synthesizer import PollySynthesizer
from sunona.synthesizer.azure_synthesizer import AzureSynthesizer
from sunona.synthesizer.cartesia_synthesizer import CartesiaSynthesizer
from sunona.synthesizer.rime_synthesizer import RimeSynthesizer
from sunona.synthesizer.smallest_synthesizer import SmallestSynthesizer
from sunona.synthesizer.sarvam_synthesizer import SarvamSynthesizer
from sunona.synthesizer.playht_synthesizer import PlayHTSynthesizer


# Aliases
ElevenlabsSynthesizer = ElevenLabsSynthesizer
OPENAISynthesizer = OpenAISynthesizer

__all__ = [
    "BaseSynthesizer",
    "ElevenLabsSynthesizer",
    "ElevenlabsSynthesizer",
    "OPENAISynthesizer",
    "DeepgramSynthesizer",
    "PollySynthesizer",
    "AzureSynthesizer",
    "CartesiaSynthesizer",
    "RimeSynthesizer",
    "SmallestSynthesizer",
    "SarvamSynthesizer",
    "PlayHTSynthesizer",
    "create_synthesizer",
]


def create_synthesizer(provider: str, **kwargs) -> BaseSynthesizer:
    """
    Factory function to create a synthesizer instance.
    """
    providers = {
        "elevenlabs": ElevenLabsSynthesizer,
        "openai": OpenAISynthesizer,
        "deepgram": DeepgramSynthesizer,
        "deepgram_tts": DeepgramSynthesizer,
        "polly": PollySynthesizer,
        "aws_polly": PollySynthesizer,
        "azure": AzureSynthesizer,
        "azure_tts": AzureSynthesizer,
        "azuretts": AzureSynthesizer,
        "cartesia": CartesiaSynthesizer,
        "rime": RimeSynthesizer,
        "smallest": SmallestSynthesizer,
        "sarvam": SarvamSynthesizer,
        "playht": PlayHTSynthesizer,
    }
    
    if provider not in providers:
        raise ValueError(f"Unsupported synthesizer provider: '{provider}'")
    
    provider_class = providers[provider]
    if provider_class is None:
        raise ValueError(f"Provider '{provider}' is not available (missing dependencies)")
    
    return provider_class(**kwargs)
