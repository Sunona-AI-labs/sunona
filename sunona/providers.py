"""
Sunona Voice AI - Provider Registry

Central registry for all supported providers:
- Synthesizers (Text-to-Speech)
- Transcribers (Speech-to-Text)
- LLMs (Language Models)
- Input/Output Handlers (Telephony)

Each provider has metadata for cost estimation and feature detection.
"""

from typing import Dict, Any, Type, Optional
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ==================== PROVIDER METADATA ====================

@dataclass
class ProviderInfo:
    """Metadata about a provider."""
    name: str
    display_name: str
    cost_per_unit: Decimal
    unit_type: str  # minute, character, token
    supports_streaming: bool = True
    is_free: bool = False
    quality_score: int = 5  # 1-10
    latency_score: int = 5  # 1-10 (higher = faster)
    languages: list = field(default_factory=lambda: ["en"])


# ==================== SYNTHESIZER IMPORTS ====================

SUPPORTED_SYNTHESIZER_MODELS = {}
SYNTHESIZER_INFO = {}

try:
    from .synthesizer import (
        PollySynthesizer,
        ElevenlabsSynthesizer,
        OPENAISynthesizer,
        DeepgramSynthesizer,
        AzureSynthesizer,
        CartesiaSynthesizer,
        SmallestSynthesizer,
        SarvamSynthesizer,
        RimeSynthesizer,
    )
    
    SUPPORTED_SYNTHESIZER_MODELS = {
        "polly": PollySynthesizer,
        "elevenlabs": ElevenlabsSynthesizer,
        "openai": OPENAISynthesizer,
        "deepgram": DeepgramSynthesizer,
        "azuretts": AzureSynthesizer,
        "cartesia": CartesiaSynthesizer,
        "smallest": SmallestSynthesizer,
        "sarvam": SarvamSynthesizer,
        "rime": RimeSynthesizer,
    }
    
    SYNTHESIZER_INFO = {
        "polly": ProviderInfo(
            name="polly",
            display_name="Amazon Polly",
            cost_per_unit=Decimal("0.004"),
            unit_type="1K characters",
            quality_score=7,
            latency_score=8,
            languages=["en", "es", "fr", "de", "it", "pt", "ja", "ko", "zh", "ar", "hi"],
        ),
        "elevenlabs": ProviderInfo(
            name="elevenlabs",
            display_name="ElevenLabs",
            cost_per_unit=Decimal("0.18"),
            unit_type="1K characters",
            quality_score=10,
            latency_score=7,
            languages=["en", "es", "fr", "de", "it", "pt", "pl", "hi", "ar"],
        ),
        "openai": ProviderInfo(
            name="openai",
            display_name="OpenAI TTS",
            cost_per_unit=Decimal("0.015"),
            unit_type="1K characters",
            quality_score=8,
            latency_score=7,
            languages=["en", "es", "fr", "de", "it", "pt", "ja", "ko", "zh"],
        ),
        "deepgram": ProviderInfo(
            name="deepgram",
            display_name="Deepgram Aura",
            cost_per_unit=Decimal("0.0065"),
            unit_type="1K characters",
            quality_score=8,
            latency_score=10,
            languages=["en"],
        ),
        "azuretts": ProviderInfo(
            name="azuretts",
            display_name="Azure Neural TTS",
            cost_per_unit=Decimal("0.016"),
            unit_type="1K characters",
            quality_score=8,
            latency_score=8,
            languages=["en", "es", "fr", "de", "it", "pt", "ja", "ko", "zh", "ar", "hi"],
        ),
        "cartesia": ProviderInfo(
            name="cartesia",
            display_name="Cartesia",
            cost_per_unit=Decimal("0.05"),
            unit_type="1K characters",
            quality_score=9,
            latency_score=9,
            languages=["en", "es", "fr", "de"],
        ),
        "smallest": ProviderInfo(
            name="smallest",
            display_name="Smallest AI",
            cost_per_unit=Decimal("0.01"),
            unit_type="1K characters",
            quality_score=7,
            latency_score=9,
            languages=["en"],
        ),
        "sarvam": ProviderInfo(
            name="sarvam",
            display_name="Sarvam AI",
            cost_per_unit=Decimal("0.02"),
            unit_type="1K characters",
            quality_score=8,
            latency_score=7,
            languages=["hi", "ta", "te", "kn", "ml", "bn", "gu", "mr", "pa", "en"],
        ),
        "rime": ProviderInfo(
            name="rime",
            display_name="Rime AI",
            cost_per_unit=Decimal("0.03"),
            unit_type="1K characters",
            quality_score=8,
            latency_score=8,
            languages=["en"],
        ),
    }
    SYNTHESIZERS_AVAILABLE = True
except ImportError as e:
    SYNTHESIZERS_AVAILABLE = False
    logger.warning(f"Some synthesizers not available: {e}")


# ==================== TRANSCRIBER IMPORTS ====================

SUPPORTED_TRANSCRIBER_PROVIDERS = {}
TRANSCRIBER_INFO = {}

try:
    from .transcriber import (
        DeepgramTranscriber,
        AzureTranscriber,
        SarvamTranscriber,
        AssemblyAITranscriber,
        GoogleTranscriber,
        PixaTranscriber,
        GladiaTranscriber,
        ElevenLabsTranscriber,
        SmallestTranscriber,
    )
    
    SUPPORTED_TRANSCRIBER_PROVIDERS = {
        "deepgram": DeepgramTranscriber,
        "azure": AzureTranscriber,
        "sarvam": SarvamTranscriber,
        "assembly": AssemblyAITranscriber,
        "google": GoogleTranscriber,
        "pixa": PixaTranscriber,
        "gladia": GladiaTranscriber,
        "elevenlabs": ElevenLabsTranscriber,
        "smallest": SmallestTranscriber,
    }
    
    TRANSCRIBER_INFO = {
        "deepgram": ProviderInfo(
            name="deepgram",
            display_name="Deepgram Nova-2",
            cost_per_unit=Decimal("0.0145"),
            unit_type="minute",
            quality_score=9,
            latency_score=10,
            languages=["en", "es", "fr", "de", "it", "pt", "ja", "ko", "zh", "nl", "ru"],
        ),
        "azure": ProviderInfo(
            name="azure",
            display_name="Azure Speech",
            cost_per_unit=Decimal("0.016"),
            unit_type="minute",
            quality_score=8,
            latency_score=8,
            languages=["en", "es", "fr", "de", "it", "pt", "ja", "ko", "zh", "ar", "hi"],
        ),
        "sarvam": ProviderInfo(
            name="sarvam",
            display_name="Sarvam AI STT",
            cost_per_unit=Decimal("0.015"),
            unit_type="minute",
            quality_score=8,
            latency_score=7,
            languages=["hi", "ta", "te", "kn", "ml", "bn", "gu", "mr", "pa", "en"],
        ),
        "assembly": ProviderInfo(
            name="assembly",
            display_name="AssemblyAI",
            cost_per_unit=Decimal("0.015"),
            unit_type="minute",
            quality_score=9,
            latency_score=8,
            languages=["en", "es", "fr", "de", "it", "pt", "nl"],
        ),
        "google": ProviderInfo(
            name="google",
            display_name="Google Speech-to-Text",
            cost_per_unit=Decimal("0.016"),
            unit_type="minute",
            quality_score=8,
            latency_score=7,
            languages=["en", "es", "fr", "de", "it", "pt", "ja", "ko", "zh", "ar", "hi"],
        ),
        "pixa": ProviderInfo(
            name="pixa",
            display_name="Pixa Transcription",
            cost_per_unit=Decimal("0.01"),
            unit_type="minute",
            quality_score=7,
            latency_score=8,
            languages=["en"],
        ),
        "gladia": ProviderInfo(
            name="gladia",
            display_name="Gladia",
            cost_per_unit=Decimal("0.012"),
            unit_type="minute",
            quality_score=8,
            latency_score=9,
            languages=["en", "es", "fr", "de", "it", "pt"],
        ),
        "elevenlabs": ProviderInfo(
            name="elevenlabs",
            display_name="ElevenLabs STT",
            cost_per_unit=Decimal("0.02"),
            unit_type="minute",
            quality_score=8,
            latency_score=8,
            languages=["en"],
        ),
        "smallest": ProviderInfo(
            name="smallest",
            display_name="Smallest AI STT",
            cost_per_unit=Decimal("0.008"),
            unit_type="minute",
            quality_score=7,
            latency_score=9,
            languages=["en"],
        ),
    }
    TRANSCRIBERS_AVAILABLE = True
except ImportError as e:
    TRANSCRIBERS_AVAILABLE = False
    logger.warning(f"Some transcribers not available: {e}")


# Backwards compatibility alias
SUPPORTED_TRANSCRIBER_MODELS = SUPPORTED_TRANSCRIBER_PROVIDERS


# ==================== LLM IMPORTS ====================

SUPPORTED_LLM_PROVIDERS = {}
LLM_INFO = {}

try:
    from .llms import OpenAiLLM, LiteLLM, AzureLLM
    
    SUPPORTED_LLM_PROVIDERS = {
        # OpenAI Family
        "openai": OpenAiLLM,
        "custom": OpenAiLLM,
        "ola": OpenAiLLM,
        
        # Azure
        "azure": AzureLLM,
        "azure-openai": AzureLLM,
        
        # LiteLLM (universal connector)
        "cohere": LiteLLM,
        "ollama": LiteLLM,
        "deepinfra": LiteLLM,
        "together": LiteLLM,
        "fireworks": LiteLLM,
        "perplexity": LiteLLM,
        "vllm": LiteLLM,
        "anyscale": LiteLLM,
        "groq": LiteLLM,
        "anthropic": LiteLLM,
        "deepseek": LiteLLM,
        "openrouter": LiteLLM,
        "mistral": LiteLLM,
        "google": LiteLLM,
        "bedrock": LiteLLM,
        "vertex": LiteLLM,
        "replicate": LiteLLM,
        "huggingface": LiteLLM,
    }
    
    LLM_INFO = {
        "openai": ProviderInfo(
            name="openai",
            display_name="OpenAI",
            cost_per_unit=Decimal("0.005"),
            unit_type="1K tokens",
            quality_score=10,
            latency_score=8,
        ),
        "anthropic": ProviderInfo(
            name="anthropic",
            display_name="Anthropic Claude",
            cost_per_unit=Decimal("0.008"),
            unit_type="1K tokens",
            quality_score=10,
            latency_score=7,
        ),
        "groq": ProviderInfo(
            name="groq",
            display_name="Groq",
            cost_per_unit=Decimal("0.0001"),
            unit_type="1K tokens",
            quality_score=8,
            latency_score=10,
        ),
        "openrouter": ProviderInfo(
            name="openrouter",
            display_name="OpenRouter",
            cost_per_unit=Decimal("0.001"),
            unit_type="1K tokens",
            quality_score=9,
            latency_score=8,
        ),
        "together": ProviderInfo(
            name="together",
            display_name="Together AI",
            cost_per_unit=Decimal("0.0005"),
            unit_type="1K tokens",
            quality_score=8,
            latency_score=8,
        ),
        "fireworks": ProviderInfo(
            name="fireworks",
            display_name="Fireworks AI",
            cost_per_unit=Decimal("0.0002"),
            unit_type="1K tokens",
            quality_score=8,
            latency_score=9,
        ),
        "deepseek": ProviderInfo(
            name="deepseek",
            display_name="DeepSeek",
            cost_per_unit=Decimal("0.0003"),
            unit_type="1K tokens",
            quality_score=8,
            latency_score=8,
        ),
        "mistral": ProviderInfo(
            name="mistral",
            display_name="Mistral AI",
            cost_per_unit=Decimal("0.0004"),
            unit_type="1K tokens",
            quality_score=8,
            latency_score=8,
        ),
        "google": ProviderInfo(
            name="google",
            display_name="Google Gemini",
            cost_per_unit=Decimal("0.001"),
            unit_type="1K tokens",
            quality_score=9,
            latency_score=8,
        ),
        "azure": ProviderInfo(
            name="azure",
            display_name="Azure OpenAI",
            cost_per_unit=Decimal("0.005"),
            unit_type="1K tokens",
            quality_score=10,
            latency_score=8,
        ),
    }
    LLMS_AVAILABLE = True
except ImportError as e:
    LLMS_AVAILABLE = False
    logger.warning(f"Some LLMs not available: {e}")


# ==================== INPUT HANDLERS ====================

SUPPORTED_INPUT_HANDLERS = {}
SUPPORTED_INPUT_TELEPHONY_HANDLERS = {}

try:
    from .input_handlers import (
        DefaultInputHandler,
        TwilioInputHandler,
        ExotelInputHandler,
        PlivoInputHandler,
    )
    
    SUPPORTED_INPUT_HANDLERS = {
        "default": DefaultInputHandler,
        "twilio": TwilioInputHandler,
        "exotel": ExotelInputHandler,
        "plivo": PlivoInputHandler,
    }
    
    SUPPORTED_INPUT_TELEPHONY_HANDLERS = {
        "twilio": TwilioInputHandler,
        "exotel": ExotelInputHandler,
        "plivo": PlivoInputHandler,
    }
    INPUT_HANDLERS_AVAILABLE = True
except ImportError as e:
    INPUT_HANDLERS_AVAILABLE = False
    logger.warning(f"Some input handlers not available: {e}")


# ==================== OUTPUT HANDLERS ====================

SUPPORTED_OUTPUT_HANDLERS = {}
SUPPORTED_OUTPUT_TELEPHONY_HANDLERS = {}

try:
    from .output_handlers import (
        DefaultOutputHandler,
        TwilioOutputHandler,
        ExotelOutputHandler,
        PlivoOutputHandler,
    )
    
    SUPPORTED_OUTPUT_HANDLERS = {
        "default": DefaultOutputHandler,
        "twilio": TwilioOutputHandler,
        "exotel": ExotelOutputHandler,
        "plivo": PlivoOutputHandler,
    }
    
    SUPPORTED_OUTPUT_TELEPHONY_HANDLERS = {
        "twilio": TwilioOutputHandler,
        "exotel": ExotelOutputHandler,
        "plivo": PlivoOutputHandler,
    }
    OUTPUT_HANDLERS_AVAILABLE = True
except ImportError as e:
    OUTPUT_HANDLERS_AVAILABLE = False
    logger.warning(f"Some output handlers not available: {e}")


# ==================== TELEPHONY INFO ====================

TELEPHONY_INFO = {
    "twilio": ProviderInfo(
        name="twilio",
        display_name="Twilio",
        cost_per_unit=Decimal("0.022"),
        unit_type="minute",
        quality_score=9,
        latency_score=9,
    ),
    "plivo": ProviderInfo(
        name="plivo",
        display_name="Plivo",
        cost_per_unit=Decimal("0.015"),
        unit_type="minute",
        quality_score=8,
        latency_score=8,
    ),
    "exotel": ProviderInfo(
        name="exotel",
        display_name="Exotel",
        cost_per_unit=Decimal("0.01"),
        unit_type="minute",
        quality_score=7,
        latency_score=7,
        languages=["en", "hi"],
    ),
}


# ==================== FREE MODELS ====================

FREE_LLM_MODELS = [
    "mistralai/mistral-7b-instruct:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "google/gemma-2-9b-it:free",
    "huggingfaceh4/zephyr-7b-beta:free",
    "openchat/openchat-7b:free",
    "gryphe/mythomist-7b:free",
]


# ==================== RECOMMENDED CONFIGS ====================

RECOMMENDED_VOICE_AI_STACK = {
    "low_latency": {
        "transcriber": "deepgram",
        "llm": "groq",
        "synthesizer": "deepgram",
        "description": "Fastest response times for voice AI",
    },
    "high_quality": {
        "transcriber": "deepgram",
        "llm": "openai",
        "synthesizer": "elevenlabs",
        "description": "Best quality for premium experiences",
    },
    "budget": {
        "transcriber": "deepgram",
        "llm": "openrouter",
        "synthesizer": "openai",
        "description": "Cost-effective without sacrificing quality",
    },
    "free": {
        "transcriber": "deepgram",
        "llm": "openrouter",
        "synthesizer": "openai",
        "description": "Lowest cost option",
    },
    "indian_languages": {
        "transcriber": "sarvam",
        "llm": "openai",
        "synthesizer": "sarvam",
        "description": "Best for Hindi and Indian languages",
    },
}


# ==================== HELPER FUNCTIONS ====================

def get_provider_class(provider_type: str, provider_name: str) -> Optional[Type]:
    """Get provider class by type and name."""
    registries = {
        "synthesizer": SUPPORTED_SYNTHESIZER_MODELS,
        "transcriber": SUPPORTED_TRANSCRIBER_PROVIDERS,
        "llm": SUPPORTED_LLM_PROVIDERS,
        "input": SUPPORTED_INPUT_HANDLERS,
        "output": SUPPORTED_OUTPUT_HANDLERS,
    }
    
    registry = registries.get(provider_type, {})
    return registry.get(provider_name)


def get_provider_info(provider_type: str, provider_name: str) -> Optional[ProviderInfo]:
    """Get provider metadata."""
    info_registries = {
        "synthesizer": SYNTHESIZER_INFO,
        "transcriber": TRANSCRIBER_INFO,
        "llm": LLM_INFO,
        "telephony": TELEPHONY_INFO,
    }
    
    registry = info_registries.get(provider_type, {})
    return registry.get(provider_name)


def get_cheapest_provider(provider_type: str) -> Optional[str]:
    """Get the cheapest provider of a type."""
    info_registries = {
        "synthesizer": SYNTHESIZER_INFO,
        "transcriber": TRANSCRIBER_INFO,
        "llm": LLM_INFO,
        "telephony": TELEPHONY_INFO,
    }
    
    registry = info_registries.get(provider_type, {})
    if not registry:
        return None
    
    cheapest = min(registry.items(), key=lambda x: x[1].cost_per_unit)
    return cheapest[0]


def get_fastest_provider(provider_type: str) -> Optional[str]:
    """Get the fastest (lowest latency) provider of a type."""
    info_registries = {
        "synthesizer": SYNTHESIZER_INFO,
        "transcriber": TRANSCRIBER_INFO,
        "llm": LLM_INFO,
    }
    
    registry = info_registries.get(provider_type, {})
    if not registry:
        return None
    
    fastest = max(registry.items(), key=lambda x: x[1].latency_score)
    return fastest[0]


def get_best_quality_provider(provider_type: str) -> Optional[str]:
    """Get the highest quality provider of a type."""
    info_registries = {
        "synthesizer": SYNTHESIZER_INFO,
        "transcriber": TRANSCRIBER_INFO,
        "llm": LLM_INFO,
    }
    
    registry = info_registries.get(provider_type, {})
    if not registry:
        return None
    
    best = max(registry.items(), key=lambda x: x[1].quality_score)
    return best[0]


def list_providers(provider_type: str) -> list:
    """List all available providers of a type."""
    registries = {
        "synthesizer": SUPPORTED_SYNTHESIZER_MODELS,
        "transcriber": SUPPORTED_TRANSCRIBER_PROVIDERS,
        "llm": SUPPORTED_LLM_PROVIDERS,
        "input": SUPPORTED_INPUT_HANDLERS,
        "output": SUPPORTED_OUTPUT_HANDLERS,
    }
    
    registry = registries.get(provider_type, {})
    return list(registry.keys())


def supports_language(provider_type: str, provider_name: str, language: str) -> bool:
    """Check if a provider supports a language."""
    info = get_provider_info(provider_type, provider_name)
    if info and info.languages:
        return language in info.languages
    return language == "en"


def estimate_cost(
    provider_type: str,
    provider_name: str,
    units: float,
) -> Decimal:
    """Estimate cost for usage."""
    info = get_provider_info(provider_type, provider_name)
    if not info:
        return Decimal("0")
    
    if info.unit_type == "1K characters":
        multiplier = Decimal(units) / Decimal("1000")
    elif info.unit_type == "1K tokens":
        multiplier = Decimal(units) / Decimal("1000")
    else:
        multiplier = Decimal(str(units))
    
    return info.cost_per_unit * multiplier
