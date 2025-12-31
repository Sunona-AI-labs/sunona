"""
Sunona Voice AI - Task Manager

Orchestrates the execution of voice AI pipelines (transcriber → LLM → synthesizer).
"""

import asyncio
import logging
import time
from typing import AsyncIterator, Dict, Any, Optional, List
from dataclasses import dataclass, field

from sunona.transcriber import create_transcriber, BaseTranscriber
from sunona.llms import create_llm, BaseLLM
from sunona.synthesizer import create_synthesizer, BaseSynthesizer
from sunona.vad.interrupt_manager import InterruptManager, InterruptConfig
from sunona.constants import (
    DEFAULT_PIPELINE,
    DEFAULT_HANGUP_AFTER_SILENCE,
)
from sunona.core import (
    SunonaError,
    LLMError,
    TranscriptionError,
    SynthesisError,
    CircuitBreaker,
    RetryConfig,
    retry_async,
    LogContext,
)
from sunona.optimization.llm_cache import get_llm_cache, CachedLLMWrapper
try:
    from sunona.billing.usage_tracker import get_usage_tracker
except ImportError:
    def get_usage_tracker(): return None

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Result from a pipeline execution step."""
    type: str  # 'transcription', 'llm_response', 'audio', 'error', 'metadata', 'interrupt'
    data: Any
    is_final: bool = False
    task_index: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "data": self.data,
            "is_final": self.is_final,
            "task_index": self.task_index,
            "metadata": self.metadata,
        }


class TaskManager:
    """
    Manages the execution of voice AI pipelines with production hardening.
    
    Features:
        - Parallel/sequential pipeline execution
        - LLM response caching
        - Circuit breakers for external services
        - Structured logging with context
        - Resilient error handling
        - Real-time barge-in (interruption) handling
    """
    
    def __init__(
        self,
        task_config: Dict[str, Any],
        prompts: Optional[Dict[str, str]] = None,
        input_queue: Optional[asyncio.Queue] = None,
        output_queue: Optional[asyncio.Queue] = None,
        task_index: int = 0,
        organization_id: Optional[str] = None,
        user_id: Optional[str] = None,
        call_id: Optional[str] = None,
    ):
        """
        Initialize the task manager.
        """
        self.task_config = task_config
        self.prompts = prompts or {}
        self.input_queue = input_queue or asyncio.Queue()
        self.output_queue = output_queue or asyncio.Queue()
        self.task_index = task_index
        self.organization_id = organization_id
        self.user_id = user_id
        self.call_id = call_id or f"call_{int(time.time())}"
        self.stream_id = f"stream_{int(time.time())}_{task_index}"
        self._usage_tracker = get_usage_tracker()
        
        # Extract configuration
        self.task_type = task_config.get("task_type", "conversation")
        self.toolchain = task_config.get("toolchain", {})
        self.tools_config = task_config.get("tools_config", {})
        self.task_settings = task_config.get("task_config", {})
        
        # Pipeline components
        self.pipelines: List[List[str]] = self.toolchain.get("pipelines", [DEFAULT_PIPELINE])
        self.execution_mode = self.toolchain.get("execution", "parallel")
        
        # Timeouts
        self.hangup_after_silence = self.task_settings.get(
            "hangup_after_silence", DEFAULT_HANGUP_AFTER_SILENCE
        )
        
        # Components
        self._transcriber: Optional[BaseTranscriber] = None
        self._llm: Optional[BaseLLM] = None
        self._synthesizer: Optional[BaseSynthesizer] = None
        
        # Resilience
        self._circuit_breakers = {
            "transcriber": CircuitBreaker(name=f"transcriber_{task_index}"),
            "llm": CircuitBreaker(name=f"llm_{task_index}"),
            "synthesizer": CircuitBreaker(name=f"synthesizer_{task_index}"),
        }
        
        self._interrupt_manager: Optional[InterruptManager] = None
        self._execution_task: Optional[asyncio.Task] = None
        self._ingestion_task: Optional[asyncio.Task] = None
        self._interrupt_event = asyncio.Event()
        self._current_gen_task: Optional[asyncio.Task] = None
        
        self._is_running = False
        self._tasks: List[asyncio.Task] = []
        
        # Set up log context
        self.log_context = LogContext(
            organization_id=organization_id,
            user_id=user_id,
            stream_id=self.stream_id,
            task_type=self.task_type
        )
    
    async def initialize(self) -> None:
        """Initialize pipeline components with circuit breakers."""
        with self.log_context:
            try:
                # Initialize transcriber
                if self._needs_component("transcriber"):
                    transcriber_config = self.tools_config.get("transcriber", {}).copy()
                    if transcriber_config:
                        provider = transcriber_config.pop("provider", "deepgram")
                        self._transcriber = create_transcriber(provider, **transcriber_config)
                        
                        # Use circuit breaker for connection
                        await self._circuit_breakers["transcriber"].call(self._transcriber.connect)
                        logger.info(f"Initialized transcriber: {provider}")
                
                # Initialize LLM
                if self._needs_component("llm"):
                    llm_agent = self.tools_config.get("llm_agent", {})
                    llm_config = llm_agent.get("llm_config", {}).copy()
                    provider = llm_config.pop("provider", "openrouter")
                    
                    base_llm = create_llm(provider, **llm_config)
                    
                    # Wrap with caching
                    cache = get_llm_cache()
                    self._llm = CachedLLMWrapper(base_llm, cache=cache)
                    
                    # Set system prompt
                    system_prompt = self.prompts.get("system_prompt")
                    if system_prompt:
                        self._llm.llm.set_system_prompt(system_prompt)
                    
                    logger.info(f"Initialized LLM with caching: {provider}")
                
                # Initialize synthesizer
                if self._needs_component("synthesizer"):
                    synth_config = self.tools_config.get("synthesizer", {}).copy()
                    if synth_config:
                        provider = synth_config.pop("provider", "elevenlabs")
                        provider_config = synth_config.pop("provider_config", {})
                        combined_config = {**synth_config, **provider_config}
                        self._synthesizer = create_synthesizer(provider, **combined_config)
                        
                        # Use circuit breaker for connection
                        await self._circuit_breakers["synthesizer"].call(self._synthesizer.connect)
                        logger.info(f"Initialized synthesizer: {provider}")
                
                # Initialize Interrupt Manager
                self._interrupt_manager = InterruptManager(
                    on_interrupt=self._handle_interruption
                )
                await self._interrupt_manager.initialize()
                logger.info("Initialized Interrupt Manager for barge-in")
                
            except Exception as e:
                logger.error(f"Failed to initialize task components: {e}")
                raise SunonaError(f"Initialization failed: {e}")
    
    def _needs_component(self, component: str) -> bool:
        """Check if a component is needed for any pipeline."""
        for pipeline in self.pipelines:
            if component in pipeline:
                return True
        return False
    
    async def _handle_interruption(self) -> None:
        """Handle interruption signal from VAD."""
        logger.info("Barge-in detected! Stopping current assistant turn.")
        self._interrupt_event.set()
        
        # Stop current generation tasks
        if self._current_gen_task and not self._current_gen_task.done():
            self._current_gen_task.cancel()
            
        # Clear synthesizer buffers if any
        if self._synthesizer:
            self._synthesizer.flush_buffer()
            
        # Notify output handlers to stop playback
        await self.output_queue.put(PipelineResult(
            type="interrupt", 
            data={"action": "stop_audio"}, 
            task_index=self.task_index
        ))

    async def cleanup(self) -> None:
        """Cleanup all components."""
        with self.log_context:
            if self._transcriber:
                try:
                    await self._transcriber.disconnect()
                except Exception:
                    pass
            if self._synthesizer:
                try:
                    await self._synthesizer.disconnect()
                except Exception:
                    pass
            if self._llm and hasattr(self._llm.llm, 'close'):
                try:
                    await self._llm.llm.close()
                except Exception:
                    pass
            if self._interrupt_manager:
                try:
                    await self._interrupt_manager.close()
                except Exception:
                    pass
            logger.debug("Cleaned up task components")
    
    async def run(self) -> AsyncIterator[PipelineResult]:
        """Run the task and yield results."""
        self._is_running = True
        
        with self.log_context:
            try:
                await self.initialize()
                
                # Send start metadata
                yield PipelineResult(
                    type="metadata",
                    data={"status": "started", "stream_id": self.stream_id},
                    task_index=self.task_index,
                )
                
                # Process each pipeline
                if self.execution_mode == "parallel":
                    async for result in self._run_parallel():
                        yield result
                else:
                    async for result in self._run_sequential():
                        yield result
                        
            except SunonaError as e:
                logger.error(f"Known Sunona error: {e}")
                yield PipelineResult(type="error", data=str(e), is_final=True, task_index=self.task_index)
            except Exception as e:
                logger.exception(f"Unexpected task execution error: {e}")
                yield PipelineResult(type="error", data="Internal server error", is_final=True, task_index=self.task_index)
            finally:
                self._is_running = False
                await self.cleanup()
    
    async def _run_parallel(self) -> AsyncIterator[PipelineResult]:
        """Run pipelines in parallel mode."""
        # For now, process the main pipeline
        main_pipeline = self.pipelines[0] if self.pipelines else DEFAULT_PIPELINE
        async for result in self._execute_pipeline(main_pipeline):
            yield result
    
    async def _run_sequential(self) -> AsyncIterator[PipelineResult]:
        """Run pipelines sequentially."""
        for pipeline in self.pipelines:
            async for result in self._execute_pipeline(pipeline):
                yield result
    
    async def _execute_pipeline(self, pipeline: List[str]) -> AsyncIterator[PipelineResult]:
        """Execute a single pipeline."""
        logger.debug(f"Executing pipeline: {pipeline}")
        
        has_transcriber = "transcriber" in pipeline
        has_llm = "llm" in pipeline
        has_synthesizer = "synthesizer" in pipeline
        
        if has_llm and not has_transcriber:
            async for result in self._run_text_pipeline(has_synthesizer):
                yield result
            return
        
        if has_transcriber and has_llm:
            async for result in self._run_voice_pipeline(has_synthesizer):
                yield result
            return
        
        logger.warning(f"Unsupported pipeline configuration: {pipeline}")
    
    async def _run_text_pipeline(self, with_synthesis: bool) -> AsyncIterator[PipelineResult]:
        """Execute text-only pipeline."""
        if not self._llm:
            return
        
        while self._is_running:
            try:
                text_input = await asyncio.wait_for(
                    self.input_queue.get(),
                    timeout=self.hangup_after_silence
                )
                
                if text_input is None:
                    break
                
                # Use circuit breaker for LLM call
                full_response = []
                
                try:
                    # Enforce circuit breaker on the start of the stream
                    await self._circuit_breakers["llm"].call(self._llm.llm.chat_stream, text_input)
                    
                    async for chunk in self._llm.llm.chat_stream(text_input):
                        full_response.append(chunk)
                        yield PipelineResult(type="llm_response", data=chunk, task_index=self.task_index)
                        
                        if with_synthesis and self._synthesizer:
                            buffered = self._synthesizer.add_to_buffer(chunk)
                            if buffered:
                                async for audio in self._synthesizer.speak(buffered):
                                    yield PipelineResult(type="audio", data=audio, task_index=self.task_index)
                        
                        # Track LLM usage
                        i_tokens = max(1, len(text_input) // 4)
                        o_tokens = max(1, len(chunk) // 4)
                        self._usage_tracker.add_llm_usage(self.call_id, input_tokens=i_tokens, output_tokens=o_tokens)

                    # Flush synthesis
                    if with_synthesis and self._synthesizer:
                        remaining = self._synthesizer.flush_buffer()
                        if remaining:
                            async for audio in self._synthesizer.speak(remaining):
                                yield PipelineResult(type="audio", data=audio, task_index=self.task_index)
                    
                    full_text_response = "".join(full_response)
                    if with_synthesis:
                         self._usage_tracker.add_tts_usage(self.call_id, full_text_response)

                    yield PipelineResult(type="llm_response", data=full_text_response, is_final=True, task_index=self.task_index)
                
                except Exception as e:
                    raise LLMError(f"LLM streaming failed: {e}")
                
            except asyncio.TimeoutError:
                logger.info("Text pipeline timeout")
                break
            except Exception as e:
                logger.error(f"Text pipeline error: {e}")
                yield PipelineResult(type="error", data=str(e), is_final=True, task_index=self.task_index)
                break
    
    async def _run_voice_pipeline(self, with_synthesis: bool) -> AsyncIterator[PipelineResult]:
        """Execute full voice pipeline with real-time barge-in."""
        if not self._transcriber or not self._llm:
            return

        # Queue for passing transcripts from ingestion to execution
        transcript_queue = asyncio.Queue()
        
        async def ingestion_loop():
            """Continuously process audio and detect interruptions."""
            try:
                while self._is_running:
                    chunk_data = await self.input_queue.get()
                    if chunk_data is None:
                        await transcript_queue.put(None)
                        break
                    
                    # Distinguish between raw bytes and possible tuples
                    chunk = chunk_data[1] if isinstance(chunk_data, tuple) else chunk_data
                    
                    # 1. Process for barge-in detection
                    if self._interrupt_manager:
                        await self._interrupt_manager.process_audio(chunk)
                    
                    # 2. Feed to transcriber
                    await self._transcriber.transcribe(chunk)
                    
                    # 3. Handle transcription results
                    result = await self._transcriber.get_transcription(timeout=0.01)
                    if result and result.get("is_final"):
                        text = result.get("text", "").strip()
                        if text:
                            await transcript_queue.put(text)
            except Exception as e:
                logger.error(f"Ingestion loop error: {e}")
                
        async def execution_loop():
            """Handle transcripts and generate responses."""
            try:
                while self._is_running:
                    text = await transcript_queue.get()
                    if text is None: break
                    
                    self._interrupt_event.clear()
                    if self._interrupt_manager:
                        self._interrupt_manager.start_assistant_turn()
                    
                    try:
                        yield PipelineResult(type="transcription", data=text, is_final=True, task_index=self.task_index)
                        
                        full_response = []
                        async for chunk in self._llm.llm.chat_stream(text):
                            if self._interrupt_event.is_set(): break
                            
                            full_response.append(chunk)
                            yield PipelineResult(type="llm_response", data=chunk, task_index=self.task_index)
                            
                            if with_synthesis and self._synthesizer:
                                buffered = self._synthesizer.add_to_buffer(chunk)
                                if buffered:
                                    async for audio in self._synthesizer.speak(buffered):
                                        if self._interrupt_event.is_set(): break
                                        yield PipelineResult(type="audio", data=audio, task_index=self.task_index)
                        
                        if with_synthesis and self._synthesizer and not self._interrupt_event.is_set():
                            remaining = self._synthesizer.flush_buffer()
                            if remaining:
                                async for audio in self._synthesizer.speak(remaining):
                                    if self._interrupt_event.is_set(): break
                                    yield PipelineResult(type="audio", data=audio, task_index=self.task_index)
                        
                        # Final usage recording
                        full_resp = "".join(full_response)
                        if full_resp:
                             # Record what we've generated so far
                            self._usage_tracker.add_llm_usage(self.call_id, input_tokens=len(text)//4, output_tokens=len(full_resp)//4)
                            if with_synthesis:
                                self._usage_tracker.add_tts_usage(self.call_id, full_resp)

                        if not self._interrupt_event.is_set():
                            yield PipelineResult(type="llm_response", data=full_resp, is_final=True, task_index=self.task_index)
                    
                    finally:
                        if self._interrupt_manager:
                            self._interrupt_manager.end_assistant_turn()
            except Exception as e:
                logger.error(f"Execution loop error: {e}")

        # Start loops
        self._ingestion_task = asyncio.create_task(ingestion_loop())
        async for r in execution_loop():
            yield r
        
        # Cleanup tasks
        if not self._ingestion_task.done():
            self._ingestion_task.cancel()
        return

    async def stop(self) -> None:
        """Stop the task manager."""
        self._is_running = False
        for task in self._tasks:
            if not task.done():
                task.cancel()
        if self._ingestion_task and not self._ingestion_task.done():
            self._ingestion_task.cancel()
        await self.cleanup()
    
    async def send_input(self, data: Any) -> None:
        """Send input to the task."""
        await self.input_queue.put(data)
    
    async def get_output(self, timeout: float = 10.0) -> Optional[PipelineResult]:
        """Get output from the task."""
        try:
            return await asyncio.wait_for(self.output_queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None
