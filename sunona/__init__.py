"""
Sunona - End-to-end Voice AI Platform

A comprehensive voice AI framework for building conversational assistants
with speech-to-text, LLM processing, and text-to-speech capabilities.
"""

__version__ = "0.2.0"
__author__ = "Sunona AI"

# Lazy imports to avoid import errors
def _get_assistant():
    from sunona.assistant import Assistant
    return Assistant

def _get_models():
    from sunona.models import (
        Transcriber,
        Synthesizer,
        LlmAgent,
        SimpleLlmAgent,
        ElevenLabsConfig,
        AgentModel,
        Task,
        ConversationConfig,
    )
    return {
        "Transcriber": Transcriber,
        "Synthesizer": Synthesizer,
        "LlmAgent": LlmAgent,
        "SimpleLlmAgent": SimpleLlmAgent,
        "ElevenLabsConfig": ElevenLabsConfig,
        "AgentModel": AgentModel,
        "Task": Task,
        "ConversationConfig": ConversationConfig,
    }

# For backwards compatibility when importing directly
try:
    from sunona.assistant import Assistant
    from sunona.models import (
        Transcriber,
        Synthesizer,
        LlmAgent,
        SimpleLlmAgent,
        ElevenLabsConfig,
        AgentModel,
        Task,
        ConversationConfig,
    )
    
    # Alias for backwards compatibility
    AgentConfig = AgentModel
except ImportError as e:
    # Handle import errors gracefully
    import warnings
    warnings.warn(f"Some Sunona components failed to import: {e}")
    
    Assistant = None
    Transcriber = None
    Synthesizer = None
    LlmAgent = None
    SimpleLlmAgent = None
    ElevenLabsConfig = None
    AgentModel = None
    AgentConfig = None
    Task = None
    ConversationConfig = None

__all__ = [
    "Assistant",
    "Transcriber",
    "Synthesizer", 
    "LlmAgent",
    "SimpleLlmAgent",
    "ElevenLabsConfig",
    "AgentModel",
    "AgentConfig",
    "Task",
    "ConversationConfig",
    "__version__",
]
