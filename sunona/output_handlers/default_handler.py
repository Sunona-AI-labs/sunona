"""
Sunona Voice AI - Default Output Handler

Default handler for processing and delivering output.
"""

import asyncio
import logging
from typing import Optional, AsyncIterator, Any, Callable

logger = logging.getLogger(__name__)


class DefaultOutputHandler:
    """
    Default output handler for processing audio and text output.
    
    Features:
        - Queue-based output buffering
        - Callback support
        - Audio streaming
    """
    
    def __init__(
        self,
        output_queue: Optional[asyncio.Queue] = None,
        audio_callback: Optional[Callable[[bytes], None]] = None,
        text_callback: Optional[Callable[[str], None]] = None,
    ):
        """
        Initialize the output handler.
        
        Args:
            output_queue: Queue for output data
            audio_callback: Callback for audio output
            text_callback: Callback for text output
        """
        self.output_queue = output_queue or asyncio.Queue()
        self.audio_callback = audio_callback
        self.text_callback = text_callback
        
        self._is_running = False
    
    async def start(self) -> None:
        """Start the output handler."""
        self._is_running = True
        logger.info("Output handler started")
    
    async def stop(self) -> None:
        """Stop the output handler."""
        self._is_running = False
        logger.info("Output handler stopped")
    
    async def send_audio(self, audio_bytes: bytes) -> None:
        """
        Send audio output.
        
        Args:
            audio_bytes: Audio data to send
        """
        if not self._is_running:
            return
        
        await self.output_queue.put(("audio", audio_bytes))
        
        if self.audio_callback:
            try:
                self.audio_callback(audio_bytes)
            except Exception as e:
                logger.error(f"Audio callback error: {e}")
    
    async def send_text(self, text: str, is_final: bool = False) -> None:
        """
        Send text output.
        
        Args:
            text: Text data to send
            is_final: Whether this is the final text
        """
        if not self._is_running:
            return
        
        await self.output_queue.put(("text", {"text": text, "is_final": is_final}))
        
        if self.text_callback:
            try:
                self.text_callback(text)
            except Exception as e:
                logger.error(f"Text callback error: {e}")
    
    async def send_event(self, event_type: str, data: Any) -> None:
        """
        Send a custom event.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        if not self._is_running:
            return
        
        await self.output_queue.put((event_type, data))
    
    async def get_output(self, timeout: float = 10.0) -> Optional[tuple]:
        """
        Get the next output from the queue.
        
        Args:
            timeout: Maximum wait time in seconds
            
        Returns:
            Tuple of (type, data) or None if timeout
        """
        try:
            return await asyncio.wait_for(
                self.output_queue.get(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            return None
    
    async def stream_output(self) -> AsyncIterator[tuple]:
        """
        Stream output from the queue.
        
        Yields:
            Tuple of (type, data)
        """
        while self._is_running:
            result = await self.get_output()
            if result is None:
                continue
            yield result
