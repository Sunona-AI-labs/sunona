"""
Sunona Voice AI - Default Input Handler

Default handler for processing audio and text input.
"""

import asyncio
import logging
from typing import Optional, AsyncIterator, Any

logger = logging.getLogger(__name__)


class DefaultInputHandler:
    """
    Default input handler for processing audio and text.
    
    Features:
        - Queue-based input buffering
        - Audio chunk aggregation
        - Text input support
    """
    
    def __init__(
        self,
        input_queue: Optional[asyncio.Queue] = None,
        audio_format: str = "pcm",
        sample_rate: int = 16000,
        chunk_size: int = 1024,
    ):
        """
        Initialize the input handler.
        
        Args:
            input_queue: Queue for receiving input
            audio_format: Expected audio format
            sample_rate: Expected sample rate
            chunk_size: Audio chunk size in bytes
        """
        self.input_queue = input_queue or asyncio.Queue()
        self.audio_format = audio_format
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        
        self._is_running = False
        self._audio_buffer: bytes = b""
    
    async def start(self) -> None:
        """Start the input handler."""
        self._is_running = True
        logger.info("Input handler started")
    
    async def stop(self) -> None:
        """Stop the input handler."""
        self._is_running = False
        logger.info("Input handler stopped")
    
    async def receive_audio(self, audio_chunk: bytes) -> None:
        """
        Receive an audio chunk.
        
        Args:
            audio_chunk: Raw audio bytes
        """
        if not self._is_running:
            return
        
        self._audio_buffer += audio_chunk
        
        # Emit chunks when we have enough data
        while len(self._audio_buffer) >= self.chunk_size:
            chunk = self._audio_buffer[:self.chunk_size]
            self._audio_buffer = self._audio_buffer[self.chunk_size:]
            await self.input_queue.put(("audio", chunk))
    
    async def receive_text(self, text: str) -> None:
        """
        Receive text input.
        
        Args:
            text: Input text
        """
        if not self._is_running:
            return
        
        await self.input_queue.put(("text", text))
    
    async def flush(self) -> None:
        """Flush any remaining buffered audio."""
        if self._audio_buffer:
            await self.input_queue.put(("audio", self._audio_buffer))
            self._audio_buffer = b""
    
    async def end_input(self) -> None:
        """Signal end of input."""
        await self.flush()
        await self.input_queue.put(("end", None))
    
    async def get_input(self, timeout: float = 10.0) -> Optional[tuple]:
        """
        Get the next input from the queue.
        
        Args:
            timeout: Maximum wait time in seconds
            
        Returns:
            Tuple of (type, data) or None if timeout
        """
        try:
            return await asyncio.wait_for(
                self.input_queue.get(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            return None
    
    async def stream_input(self) -> AsyncIterator[tuple]:
        """
        Stream input from the queue.
        
        Yields:
            Tuple of (type, data)
        """
        while self._is_running:
            result = await self.get_input()
            if result is None:
                continue
            
            input_type, data = result
            if input_type == "end":
                break
            
            yield result
