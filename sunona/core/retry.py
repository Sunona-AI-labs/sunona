"""
Sunona Voice AI - Retry Logic

Production-grade retry mechanisms with exponential backoff,
jitter, and configurable strategies for resilient operations.

Strategies:
    - Exponential backoff with jitter
    - Linear backoff
    - Constant delay
    - Custom backoff functions

Features:
    - Configurable max attempts
    - Exception filtering
    - Timeout support
    - Callbacks for retry events
    - Context preservation
"""

import asyncio
import logging
import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import wraps
from typing import (
    Any, Awaitable, Callable, Optional, Sequence, 
    Tuple, Type, TypeVar, Union
)

from sunona.core.exceptions import SunonaError, TimeoutError as SunonaTimeoutError

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Type aliases
ExceptionTypes = Union[Type[Exception], Tuple[Type[Exception], ...]]
BackoffFunc = Callable[[int], float]


class RetryExhausted(SunonaError):
    """Raised when all retry attempts are exhausted."""
    
    default_message = "All retry attempts exhausted"
    default_error_code = "RETRY_EXHAUSTED"
    default_retryable = False
    
    def __init__(
        self,
        message: Optional[str] = None,
        attempts: int = 0,
        last_exception: Optional[Exception] = None,
        **kwargs
    ):
        context = kwargs.pop("context", {})
        context["attempts"] = attempts
        if last_exception:
            context["last_error"] = str(last_exception)
        
        super().__init__(
            message=message,
            cause=last_exception,
            context=context,
            **kwargs
        )


@dataclass
class RetryConfig:
    """
    Retry configuration.
    
    Attributes:
        max_attempts: Maximum number of retry attempts (including first try)
        base_delay: Base delay in seconds
        max_delay: Maximum delay cap in seconds
        exponential_base: Base for exponential backoff (default: 2)
        jitter: Whether to add random jitter
        jitter_range: Range for jitter as (min_factor, max_factor)
        timeout: Total timeout for all retries
        exceptions: Exception types to retry on
        exceptions_to_ignore: Exception types to NOT retry on
        on_retry: Callback when retry happens (attempt, exception, delay)
        on_success: Callback on success after retries (attempt)
        on_failure: Callback when all retries exhausted (attempts, exception)
    """
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    jitter_range: Tuple[float, float] = (0.8, 1.2)
    timeout: Optional[float] = None
    exceptions: ExceptionTypes = (Exception,)
    exceptions_to_ignore: ExceptionTypes = ()
    on_retry: Optional[Callable[[int, Exception, float], None]] = None
    on_success: Optional[Callable[[int], None]] = None
    on_failure: Optional[Callable[[int, Exception], None]] = None


@dataclass
class RetryState:
    """Tracks retry state for a single operation."""
    attempt: int = 0
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_exception: Optional[Exception] = None
    delays: list = field(default_factory=list)
    
    @property
    def elapsed_seconds(self) -> float:
        """Get elapsed time since start."""
        return (datetime.now(timezone.utc) - self.start_time).total_seconds()


def exponential_backoff(
    attempt: int,
    base_delay: float = 1.0,
    exponential_base: float = 2.0,
    max_delay: float = 60.0,
) -> float:
    """
    Calculate exponential backoff delay.
    
    Formula: min(base_delay * (exponential_base ^ attempt), max_delay)
    
    Args:
        attempt: Current attempt number (0-indexed)
        base_delay: Base delay in seconds
        exponential_base: Base for exponentiation
        max_delay: Maximum delay cap
    
    Returns:
        Delay in seconds
    """
    delay = base_delay * (exponential_base ** attempt)
    return min(delay, max_delay)


def linear_backoff(
    attempt: int,
    base_delay: float = 1.0,
    increment: float = 1.0,
    max_delay: float = 60.0,
) -> float:
    """
    Calculate linear backoff delay.
    
    Formula: min(base_delay + (increment * attempt), max_delay)
    """
    delay = base_delay + (increment * attempt)
    return min(delay, max_delay)


def constant_delay(delay: float) -> BackoffFunc:
    """Return a constant delay function."""
    return lambda attempt: delay


def add_jitter(
    delay: float,
    jitter_range: Tuple[float, float] = (0.8, 1.2)
) -> float:
    """
    Add random jitter to delay.
    
    Args:
        delay: Base delay
        jitter_range: Range as (min_factor, max_factor)
    
    Returns:
        Delay with jitter applied
    """
    min_factor, max_factor = jitter_range
    jitter_factor = random.uniform(min_factor, max_factor)
    return delay * jitter_factor


def should_retry(
    exception: Exception,
    config: RetryConfig,
) -> bool:
    """
    Determine if an exception should trigger a retry.
    
    Args:
        exception: The exception that occurred
        config: Retry configuration
    
    Returns:
        True if should retry
    """
    # First check if it's in the ignore list
    if isinstance(exception, config.exceptions_to_ignore):
        return False
    
    # Then check if it's in the retry list
    return isinstance(exception, config.exceptions)


async def retry_async(
    func: Callable[..., Awaitable[T]],
    *args,
    config: Optional[RetryConfig] = None,
    **kwargs
) -> T:
    """
    Execute an async function with retry logic.
    
    Args:
        func: Async function to execute
        *args: Positional arguments for the function
        config: Retry configuration (uses defaults if not provided)
        **kwargs: Keyword arguments for the function
    
    Returns:
        Result of the function
    
    Raises:
        RetryExhausted: When all retries are exhausted
        Original exception if not retryable
    """
    if config is None:
        config = RetryConfig()
    
    state = RetryState()
    
    while state.attempt < config.max_attempts:
        try:
            # Check timeout
            if config.timeout and state.elapsed_seconds >= config.timeout:
                raise SunonaTimeoutError(
                    message=f"Retry timeout exceeded ({config.timeout}s)",
                    context={
                        "attempts": state.attempt,
                        "elapsed": state.elapsed_seconds,
                    },
                )
            
            # Execute the function
            result = await func(*args, **kwargs)
            
            # Success callback
            if state.attempt > 0 and config.on_success:
                try:
                    config.on_success(state.attempt + 1)
                except Exception as e:
                    logger.error(f"Error in success callback: {e}")
            
            return result
        
        except Exception as exc:
            state.last_exception = exc
            state.attempt += 1
            
            # Check if we should retry
            if not should_retry(exc, config):
                logger.debug(f"Exception not retryable: {type(exc).__name__}")
                raise
            
            # Check if we've exhausted attempts
            if state.attempt >= config.max_attempts:
                logger.warning(
                    f"Retry exhausted after {state.attempt} attempts: {exc}"
                )
                
                if config.on_failure:
                    try:
                        config.on_failure(state.attempt, exc)
                    except Exception as e:
                        logger.error(f"Error in failure callback: {e}")
                
                raise RetryExhausted(
                    message=f"Failed after {state.attempt} attempts",
                    attempts=state.attempt,
                    last_exception=exc,
                )
            
            # Calculate delay
            delay = exponential_backoff(
                state.attempt - 1,  # 0-indexed for delay calculation
                base_delay=config.base_delay,
                exponential_base=config.exponential_base,
                max_delay=config.max_delay,
            )
            
            if config.jitter:
                delay = add_jitter(delay, config.jitter_range)
            
            # Check if delay would exceed timeout
            if config.timeout:
                remaining = config.timeout - state.elapsed_seconds
                if delay > remaining:
                    delay = max(0, remaining)
            
            state.delays.append(delay)
            
            logger.warning(
                f"Retry {state.attempt}/{config.max_attempts} "
                f"after {delay:.2f}s due to: {exc}"
            )
            
            # Retry callback
            if config.on_retry:
                try:
                    config.on_retry(state.attempt, exc, delay)
                except Exception as e:
                    logger.error(f"Error in retry callback: {e}")
            
            # Wait before retry
            if delay > 0:
                await asyncio.sleep(delay)
    
    # Should never reach here, but just in case
    raise RetryExhausted(
        message="Retry logic error",
        attempts=state.attempt,
        last_exception=state.last_exception,
    )


def retry_with_backoff(
    *,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    timeout: Optional[float] = None,
    exceptions: ExceptionTypes = (Exception,),
    exceptions_to_ignore: ExceptionTypes = (),
    on_retry: Optional[Callable[[int, Exception, float], None]] = None,
) -> Callable:
    """
    Decorator to add retry logic with exponential backoff.
    
    Args:
        max_attempts: Maximum retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay cap
        exponential_base: Base for exponential calculation
        jitter: Whether to add random jitter
        timeout: Total timeout for all retries
        exceptions: Exception types to retry on
        exceptions_to_ignore: Exception types to NOT retry
        on_retry: Callback when retry happens
    
    Example:
        @retry_with_backoff(max_attempts=3, base_delay=1.0)
        async def call_api():
            return await api.request()
        
        @retry_with_backoff(
            max_attempts=5,
            exceptions=(ConnectionError, TimeoutError),
            on_retry=lambda a, e, d: print(f"Retry {a}: {e}")
        )
        async def resilient_call():
            ...
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_base=exponential_base,
        jitter=jitter,
        timeout=timeout,
        exceptions=exceptions,
        exceptions_to_ignore=exceptions_to_ignore,
        on_retry=on_retry,
    )
    
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            return await retry_async(func, *args, config=config, **kwargs)
        
        # Attach config for inspection
        wrapper.retry_config = config
        return wrapper
    
    return decorator


class RetryContext:
    """
    Context manager for retry logic with more control.
    
    Example:
        async with RetryContext(max_attempts=3) as retry:
            while retry.should_continue():
                try:
                    result = await risky_operation()
                    retry.success()
                    break
                except Exception as e:
                    await retry.handle_error(e)
    """
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        jitter: bool = True,
        exceptions: ExceptionTypes = (Exception,),
    ):
        self.config = RetryConfig(
            max_attempts=max_attempts,
            base_delay=base_delay,
            max_delay=max_delay,
            jitter=jitter,
            exceptions=exceptions,
        )
        self.state = RetryState()
        self._succeeded = False
    
    async def __aenter__(self) -> "RetryContext":
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_val and not self._succeeded:
            # Re-raise with context
            if isinstance(exc_val, RetryExhausted):
                return False
            if should_retry(exc_val, self.config):
                raise RetryExhausted(
                    message=f"Failed after {self.state.attempt} attempts",
                    attempts=self.state.attempt,
                    last_exception=exc_val,
                )
        return False
    
    def should_continue(self) -> bool:
        """Check if should continue retrying."""
        return self.state.attempt < self.config.max_attempts and not self._succeeded
    
    def success(self) -> None:
        """Mark operation as successful."""
        self._succeeded = True
    
    async def handle_error(self, exception: Exception) -> None:
        """Handle an error and wait for retry."""
        self.state.last_exception = exception
        self.state.attempt += 1
        
        if not should_retry(exception, self.config):
            raise exception
        
        if self.state.attempt >= self.config.max_attempts:
            raise RetryExhausted(
                message=f"Failed after {self.state.attempt} attempts",
                attempts=self.state.attempt,
                last_exception=exception,
            )
        
        # Calculate and apply delay
        delay = exponential_backoff(
            self.state.attempt - 1,
            base_delay=self.config.base_delay,
            max_delay=self.config.max_delay,
        )
        
        if self.config.jitter:
            delay = add_jitter(delay)
        
        logger.warning(
            f"Retry {self.state.attempt}/{self.config.max_attempts} "
            f"after {delay:.2f}s: {exception}"
        )
        
        await asyncio.sleep(delay)


async def with_timeout(
    func: Callable[..., Awaitable[T]],
    timeout: float,
    *args,
    **kwargs
) -> T:
    """
    Execute an async function with a timeout.
    
    Args:
        func: Async function to execute
        timeout: Timeout in seconds
        *args: Positional arguments
        **kwargs: Keyword arguments
    
    Returns:
        Result of the function
    
    Raises:
        TimeoutError: If timeout exceeded
    """
    try:
        return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
    except asyncio.TimeoutError:
        raise SunonaTimeoutError(
            message=f"Operation timed out after {timeout}s",
            context={"timeout_seconds": timeout},
        )
