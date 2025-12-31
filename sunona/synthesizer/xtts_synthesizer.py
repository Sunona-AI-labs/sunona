"""
Sunona Voice AI - XTTS Local Synthesizer

Coqui XTTS for local, offline voice synthesis with cloning.
"""

import os
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from TTS.api import TTS
    XTTS_AVAILABLE = True
except ImportError:
    XTTS_AVAILABLE = False


class XTTSSynthesizer:
    """
    Local XTTS synthesizer - no API needed.
    
    Features:
        - Zero-shot voice cloning
        - Offline operation
        - Multi-language
        - GPU acceleration
    
    Example:
        ```python
        synth = XTTSSynthesizer()
        audio = await synth.synthesize("Hello", speaker_wav="voice.wav")
        ```
    """
    
    def __init__(
        self,
        model: str = "tts_models/multilingual/multi-dataset/xtts_v2",
        device: str = "auto",
        language: str = "en",
    ):
        if not XTTS_AVAILABLE:
            raise ImportError("TTS package required: pip install TTS")
        
        self.model_name = model
        self.device = device if device != "auto" else ("cuda" if self._has_cuda() else "cpu")
        self.language = language
        
        self._tts = TTS(model_name=model, progress_bar=False).to(self.device)
        
        logger.info(f"XTTS synthesizer initialized on {self.device}")
    
    def _has_cuda(self) -> bool:
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    async def synthesize(
        self,
        text: str,
        speaker_wav: Optional[str] = None,
        language: Optional[str] = None,
    ) -> bytes:
        """Synthesize with optional voice cloning."""
        loop = asyncio.get_event_loop()
        
        def _generate():
            if speaker_wav:
                # Voice cloning mode
                return self._tts.tts(
                    text=text,
                    speaker_wav=speaker_wav,
                    language=language or self.language,
                )
            else:
                return self._tts.tts(text=text, language=language or self.language)
        
        audio = await loop.run_in_executor(None, _generate)
        
        # Convert to bytes
        import numpy as np
        import struct
        
        audio_int16 = (np.array(audio) * 32767).astype(np.int16)
        return struct.pack(f'{len(audio_int16)}h', *audio_int16)
    
    async def synthesize_to_file(
        self,
        text: str,
        output_path: str,
        speaker_wav: Optional[str] = None,
    ) -> str:
        """Synthesize to file."""
        loop = asyncio.get_event_loop()
        
        def _generate():
            return self._tts.tts_to_file(
                text=text,
                file_path=output_path,
                speaker_wav=speaker_wav,
                language=self.language,
            )
        
        await loop.run_in_executor(None, _generate)
        return output_path
    
    def list_languages(self) -> list:
        """List supported languages."""
        return ["en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh-cn", "ja", "hi"]
