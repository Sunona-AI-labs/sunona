"""
Sunona Voice AI - Interrupt Manager

Manages TTS interruption when user starts speaking.
Coordinates between VAD and synthesizer for natural turn-taking.

Features:
- Automatic TTS cancellation on user speech
- Configurable interruption thresholds
- Debouncing to prevent false triggers
- Event callbacks for interruption handling
"""

import asyncio
import logging
from typing import Optional, Callable, Awaitable, Any
from dataclasses import dataclass
from enum import Enum

from sunona.vad.silero_vad import SileroVAD, SimpleVAD, VADConfig

logger = logging.getLogger(__name__)


class InterruptState(Enum):
    """Interrupt manager states."""
    IDLE = "idle"  # Not playing, not listening
    LISTENING = "listening"  # Waiting for user speech
    USER_SPEAKING = "user_speaking"  # User is speaking
    ASSISTANT_SPEAKING = "assistant_speaking"  # TTS is playing
    INTERRUPTED = "interrupted"  # User interrupted TTS


@dataclass
class InterruptConfig:
    """
    Interrupt manager configuration.
    
    Attributes:
        vad_threshold: VAD speech probability threshold
        interrupt_threshold_ms: Minimum speech duration to interrupt
        debounce_ms: Debounce time to prevent false triggers
        cooldown_ms: Cooldown after interruption
    """
    vad_threshold: float = 0.5
    interrupt_threshold_ms: int = 200  # Original threshold
    debounce_ms: int = 50
    cooldown_ms: int = 500  # Original cooldown


class InterruptManager:
    """
    Manages interruption between user and assistant.
    
    Coordinates VAD detection with TTS playback to enable
    natural turn-taking and user interruption of the assistant.
    
    Example:
        ```python
        manager = InterruptManager(
            on_interrupt=cancel_tts,
            on_user_speech_start=pause_listening,
            on_user_speech_end=resume_listening
        )
        
        async with manager:
            # Start assistant speaking
            manager.start_assistant_turn()
            
            # Process audio
            for audio in stream:
                await manager.process_audio(audio)
        ```
    """
    
    def __init__(
        self,
        config: Optional[InterruptConfig] = None,
        on_interrupt: Optional[Callable[[], Awaitable[None]]] = None,
        on_user_speech_start: Optional[Callable[[], Awaitable[None]]] = None,
        on_user_speech_end: Optional[Callable[[], Awaitable[None]]] = None,
        use_silero: bool = True,
        **kwargs
    ):
        """
        Initialize the interrupt manager.
        
        Args:
            config: Interrupt configuration
            on_interrupt: Callback when interruption occurs
            on_user_speech_start: Callback when user starts speaking
            on_user_speech_end: Callback when user stops speaking
            use_silero: Whether to use Silero VAD (requires torch)
        """
        self.config = config or InterruptConfig()
        self.on_interrupt = on_interrupt
        self.on_user_speech_start = on_user_speech_start
        self.on_user_speech_end = on_user_speech_end
        
        self._state = InterruptState.IDLE
        self._vad: Optional[Any] = None
        self._use_silero = use_silero
        
        self._speech_start_time: Optional[float] = None
        self._last_interrupt_time: Optional[float] = None
        self._initialized = False
        
        # Lock for state changes
        self._state_lock = asyncio.Lock()
    
    async def initialize(self) -> None:
        """Initialize the interrupt manager and VAD."""
        if self._initialized:
            return
        
        async with self._state_lock:
            # Re-check after acquiring lock
            if self._initialized:
                return
                
            # Create VAD instance
            vad_config = VADConfig(threshold=self.config.vad_threshold)
            
            try:
                if self._use_silero:
                    self._vad = SileroVAD(
                        config=vad_config,
                        on_speech_start=self._on_vad_speech_start,
                        on_speech_end=self._on_vad_speech_end
                    )
                else:
                    self._vad = SimpleVAD(
                        threshold=self.config.vad_threshold / 10,  # Adjust for energy-based
                        on_speech_start=self._on_vad_speech_start,
                        on_speech_end=self._on_vad_speech_end
                    )
                
                await self._vad.initialize()
                
                self._initialized = True
                logger.info("Interrupt manager initialized")
            except ImportError:
                logger.warning("Silero VAD not available, using simple VAD")
                self._vad = SimpleVAD(
                    on_speech_start=self._on_vad_speech_start,
                    on_speech_end=self._on_vad_speech_end
                )
                self._initialized = True
            except Exception as e:
                logger.error(f"Failed to initialize interrupt manager: {e}")
                raise
    
    async def _on_vad_speech_start(self) -> None:
        """Called when VAD detects speech start."""
        import time
        
        async with self._state_lock:
            self._speech_start_time = time.time()
            
            if self._state == InterruptState.ASSISTANT_SPEAKING:
                # Check if in cooldown
                if self._last_interrupt_time:
                    elapsed = (time.time() - self._last_interrupt_time) * 1000
                    if elapsed < self.config.cooldown_ms:
                        return
                
                # Trigger interruption
                self._state = InterruptState.INTERRUPTED
                self._last_interrupt_time = time.time()
                
                logger.info("User interrupted assistant")
                
                if self.on_interrupt:
                    self._run_callback(self.on_interrupt, "on_interrupt")
            else:
                self._state = InterruptState.USER_SPEAKING
            
            if self.on_user_speech_start:
                self._run_callback(self.on_user_speech_start, "on_user_speech_start")
    
    async def _on_vad_speech_end(self) -> None:
        """Called when VAD detects speech end."""
        async with self._state_lock:
            if self._state in [InterruptState.USER_SPEAKING, InterruptState.INTERRUPTED]:
                self._state = InterruptState.LISTENING
            
            self._speech_start_time = None
            
            if self.on_user_speech_end:
                self._run_callback(self.on_user_speech_end, "on_user_speech_end")

    def _run_callback(self, callback: Callable[[], Awaitable[None]], name: str) -> None:
        """Run a callback in a background task with error handling."""
        async def _wrapper():
            try:
                await callback()
            except Exception as e:
                logger.error(f"Error in InterruptManager {name} callback: {e}")
        
        asyncio.create_task(_wrapper())
    
    async def process_audio(self, audio_chunk: bytes) -> bool:
        """
        Process audio for interruption detection.
        
        Args:
            audio_chunk: Raw audio bytes
            
        Returns:
            True if speech detected
        """
        if not self._initialized:
            await self.initialize()
        
        return await self._vad.process(audio_chunk)
    
    def start_assistant_turn(self) -> None:
        """Signal that assistant TTS is starting."""
        self._state = InterruptState.ASSISTANT_SPEAKING
        logger.debug("Assistant turn started")
    
    def end_assistant_turn(self) -> None:
        """Signal that assistant TTS has finished."""
        if self._state == InterruptState.ASSISTANT_SPEAKING:
            self._state = InterruptState.LISTENING
        logger.debug("Assistant turn ended")
    
    def start_user_turn(self) -> None:
        """Signal that we're waiting for user input."""
        self._state = InterruptState.LISTENING
    
    @property
    def state(self) -> InterruptState:
        """Get current state."""
        return self._state
    
    def is_user_speaking(self) -> bool:
        """Check if user is currently speaking."""
        return self._state == InterruptState.USER_SPEAKING
    
    def is_assistant_speaking(self) -> bool:
        """Check if assistant is speaking."""
        return self._state == InterruptState.ASSISTANT_SPEAKING
    
    def was_interrupted(self) -> bool:
        """Check if interruption occurred."""
        return self._state == InterruptState.INTERRUPTED
    
    def reset(self) -> None:
        """Reset to initial state."""
        self._state = InterruptState.IDLE
        self._speech_start_time = None
        if self._vad:
            self._vad.reset()
    
    async def close(self) -> None:
        """Close the interrupt manager."""
        if self._vad:
            await self._vad.close()
        self._initialized = False
    
    async def __aenter__(self):
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
