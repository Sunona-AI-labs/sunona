"""
Sunona Voice AI - VAD Package

Voice Activity Detection for interruption handling.

Provides:
- SileroVAD: High-accuracy voice detection
- InterruptManager: Manages TTS interruption
"""

from sunona.vad.silero_vad import SileroVAD
from sunona.vad.interrupt_manager import InterruptManager

__all__ = [
    "SileroVAD",
    "InterruptManager",
]
