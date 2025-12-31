"""
Sunona Voice AI - Silero VAD

High-accuracy Voice Activity Detection using Silero VAD.
Detects speech in audio with low latency for interruption handling.

Features:
- State-of-the-art accuracy
- Low latency (~50ms)
- Configurable thresholds
- Streaming support
- CPU-friendly (no GPU required)
"""

import os
import logging
import asyncio
from typing import Optional, Callable, Awaitable, List
from dataclasses import dataclass, field
from collections import deque

logger = logging.getLogger(__name__)

# Try to import torch (optional dependency)
try:
    import torch
    import numpy as np
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    np = None


@dataclass
class VADConfig:
    """
    VAD configuration.
    
    Attributes:
        threshold: Speech probability threshold (0-1)
        min_speech_duration_ms: Minimum speech duration to trigger
        min_silence_duration_ms: Minimum silence to end speech
        speech_pad_ms: Padding around detected speech
        sample_rate: Audio sample rate (must be 8000 or 16000)
        window_size_samples: Samples per VAD window
    """
    threshold: float = 0.5
    min_speech_duration_ms: int = 250  # Original threshold
    min_silence_duration_ms: int = 500  # Original threshold
    speech_pad_ms: int = 100
    sample_rate: int = 16000
    window_size_samples: int = 512  # 32ms at 16kHz
    

@dataclass
class VADState:
    """Internal VAD state."""
    is_speaking: bool = False
    speech_start_sample: int = 0
    speech_end_sample: int = 0
    current_sample: int = 0
    speech_probs: deque = field(default_factory=lambda: deque(maxlen=100))


class SileroVAD:
    """
    Silero Voice Activity Detection.
    
    Uses the Silero VAD model for accurate speech detection
    with minimal latency. Ideal for real-time voice applications.
    
    Example:
        ```python
        vad = SileroVAD(
            threshold=0.5,
            on_speech_start=lambda: print("Speech started"),
            on_speech_end=lambda: print("Speech ended")
        )
        
        async with vad:
            for audio_chunk in audio_stream:
                is_speech = await vad.process(audio_chunk)
        ```
    """
    
    def __init__(
        self,
        config: Optional[VADConfig] = None,
        threshold: float = 0.5,
        sample_rate: int = 16000,
        on_speech_start: Optional[Callable[[], Awaitable[None]]] = None,
        on_speech_end: Optional[Callable[[], Awaitable[None]]] = None,
        **kwargs
    ):
        """
        Initialize Silero VAD.
        
        Args:
            config: VAD configuration (overrides individual params)
            threshold: Speech probability threshold
            sample_rate: Audio sample rate (8000 or 16000)
            on_speech_start: Callback when speech starts
            on_speech_end: Callback when speech ends
        """
        if not TORCH_AVAILABLE:
            raise ImportError(
                "torch is required for SileroVAD. "
                "Install with: pip install torch"
            )
        
        if sample_rate not in [8000, 16000]:
            raise ValueError("sample_rate must be 8000 or 16000")
        
        # Use config or individual params
        if config:
            self.config = config
        else:
            self.config = VADConfig(
                threshold=threshold,
                sample_rate=sample_rate,
                **kwargs
            )
        
        self.on_speech_start = on_speech_start
        self.on_speech_end = on_speech_end
        
        self._model = None
        self._state = VADState()
        self._initialized = False
        self._init_lock = asyncio.Lock()
        
        # Samples to ms conversion
        self._samples_per_ms = self.config.sample_rate // 1000
        
        # Counters for duration tracking
        self._speech_samples = 0
        self._silence_samples = 0
    
    async def initialize(self) -> None:
        """Load the Silero VAD model."""
        if self._initialized:
            return
        
        async with self._init_lock:
            # Re-check after acquiring lock
            if self._initialized:
                return
                
            try:
                # Load Silero VAD from torch hub
                self._model, _ = torch.hub.load(
                    repo_or_dir='snakers4/silero-vad',
                    model='silero_vad',
                    force_reload=False,
                    onnx=False
                )
                self._model.eval()
                
                self._initialized = True
                logger.info("Silero VAD initialized")
                
            except Exception as e:
                logger.error(f"Failed to load Silero VAD: {e}")
                raise
    
    def _audio_to_tensor(self, audio: bytes) -> torch.Tensor:
        """Convert audio bytes to normalized tensor."""
        # Assume 16-bit PCM audio
        audio_array = np.frombuffer(audio, dtype=np.int16)
        
        # Normalize to [-1, 1]
        audio_float = audio_array.astype(np.float32) / 32768.0
        
        return torch.from_numpy(audio_float)
    
    async def process(self, audio_chunk: bytes) -> bool:
        """
        Process an audio chunk and detect speech.
        
        Args:
            audio_chunk: Raw audio bytes (16-bit PCM)
            
        Returns:
            True if speech is detected in this chunk
        """
        if not self._initialized:
            await self.initialize()
        
        # Convert to tensor
        audio_tensor = self._audio_to_tensor(audio_chunk)
        
        # Process in windows
        chunk_samples = len(audio_tensor)
        window_size = self.config.window_size_samples
        
        speech_detected = False
        
        for i in range(0, chunk_samples, window_size):
            window = audio_tensor[i:i + window_size]
            
            # Pad if necessary
            if len(window) < window_size:
                window = torch.nn.functional.pad(window, (0, window_size - len(window)))
            
            # Get speech probability
            with torch.no_grad():
                prob = self._model(window, self.config.sample_rate).item()
            
            self._state.speech_probs.append(prob)
            self._state.current_sample += len(window)
            
            # Detect speech based on threshold
            if prob >= self.config.threshold:
                speech_detected = True
                self._speech_samples += len(window)
                self._silence_samples = 0
                
                # Check if we should trigger speech start
                speech_duration_ms = self._speech_samples / self._samples_per_ms
                
                if not self._state.is_speaking:
                    if speech_duration_ms >= self.config.min_speech_duration_ms:
                        self._state.is_speaking = True
                        self._state.speech_start_sample = self._state.current_sample
                        
                        if self.on_speech_start:
                            self._run_callback(self.on_speech_start, "on_speech_start")
            else:
                self._silence_samples += len(window)
                
                # Check if we should trigger speech end
                if self._state.is_speaking:
                    silence_duration_ms = self._silence_samples / self._samples_per_ms
                    
                    if silence_duration_ms >= self.config.min_silence_duration_ms:
                        self._state.is_speaking = False
                        self._state.speech_end_sample = self._state.current_sample
                        self._speech_samples = 0
                        
                        if self.on_speech_end:
                            self._run_callback(self.on_speech_end, "on_speech_end")
    
    def _run_callback(self, callback: Callable[[], Awaitable[None]], name: str) -> None:
        """Run a callback in a background task with error handling."""
        async def _wrapper():
            try:
                await callback()
            except Exception as e:
                logger.error(f"Error in SileroVAD {name} callback: {e}")
        
        asyncio.create_task(_wrapper())
        
        return speech_detected
    
    def is_speaking(self) -> bool:
        """Check if currently in speech state."""
        return self._state.is_speaking
    
    def get_speech_probability(self) -> float:
        """Get the latest speech probability."""
        if self._state.speech_probs:
            return self._state.speech_probs[-1]
        return 0.0
    
    def get_average_probability(self, window: int = 10) -> float:
        """Get average speech probability over recent windows."""
        probs = list(self._state.speech_probs)[-window:]
        return sum(probs) / len(probs) if probs else 0.0
    
    def reset(self) -> None:
        """Reset VAD state."""
        self._state = VADState()
        self._speech_samples = 0
        self._silence_samples = 0
        
        # Reset model state if available
        if self._model and hasattr(self._model, 'reset_states'):
            self._model.reset_states()
    
    async def close(self) -> None:
        """Release resources."""
        self._model = None
        self._initialized = False
    
    async def __aenter__(self):
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class SimpleVAD:
    """
    Simple energy-based VAD (fallback when torch is not available).
    
    Uses RMS energy to detect speech. Less accurate but no dependencies.
    """
    
    def __init__(
        self,
        threshold: float = 0.02,
        sample_rate: int = 16000,
        on_speech_start: Optional[Callable[[], Awaitable[None]]] = None,
        on_speech_end: Optional[Callable[[], Awaitable[None]]] = None,
    ):
        """Initialize simple VAD."""
        self.threshold = threshold
        self.sample_rate = sample_rate
        self.on_speech_start = on_speech_start
        self.on_speech_end = on_speech_end
        
        self._is_speaking = False
        self._speech_count = 0
        self._silence_count = 0
    
    async def initialize(self) -> None:
        """No initialization needed."""
        pass
    
    async def process(self, audio_chunk: bytes) -> bool:
        """Process audio using RMS energy."""
        try:
            import numpy as np
        except ImportError:
            return False
        
        # Calculate RMS energy
        audio = np.frombuffer(audio_chunk, dtype=np.int16)
        audio_float = audio.astype(np.float32) / 32768.0
        rms = np.sqrt(np.mean(audio_float ** 2))
        
        is_speech = rms > self.threshold
        
        if is_speech:
            self._speech_count += 1
            self._silence_count = 0
            
            if not self._is_speaking and self._speech_count > 5:
                self._is_speaking = True
                if self.on_speech_start:
                    asyncio.create_task(self.on_speech_start())
        else:
            self._silence_count += 1
            
            if self._is_speaking and self._silence_count > 10:
                self._is_speaking = False
                self._speech_count = 0
                if self.on_speech_end:
                    asyncio.create_task(self.on_speech_end())
        
        return is_speech
    
    def is_speaking(self) -> bool:
        return self._is_speaking
    
    def reset(self) -> None:
        self._is_speaking = False
        self._speech_count = 0
        self._silence_count = 0
    
    async def close(self) -> None:
        pass
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
