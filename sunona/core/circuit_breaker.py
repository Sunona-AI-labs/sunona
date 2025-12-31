"""
Sunona Voice AI - Circuit Breaker

Production-grade circuit breaker pattern for fault tolerance.
Prevents cascading failures and provides graceful degradation.

States:
    CLOSED: Normal operation, requests pass through
    OPEN: Failures exceeded threshold, requests blocked
    HALF_OPEN: Testing if service recovered

Usage:
    @circuit_breaker(name="deepgram", failure_threshold=5)
    async def call_deepgram(audio: bytes) -> str:
        ...

    # Or manual usage:
    cb = CircuitBreaker("openai")
    async with cb:
        result = await openai_call()
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from functools import wraps
from typing import Any, Awaitable, Callable, Dict, List, Optional, Type, TypeVar

from sunona.core.exceptions import CircuitBreakerOpenError

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """
    Circuit breaker configuration.
    
    Attributes:
        failure_threshold: Failures before opening circuit
        success_threshold: Successes in half-open before closing
        timeout_seconds: Time before transitioning from open to half-open
        half_open_max_calls: Max concurrent calls in half-open state
        failure_rate_threshold: Failure rate (0-1) to trigger open
        min_calls_before_rate: Minimum calls before rate calculation
        exceptions_to_track: Exception types that count as failures
        exceptions_to_ignore: Exception types that don't count as failures
    """
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout_seconds: float = 30.0
    half_open_max_calls: int = 3
    failure_rate_threshold: float = 0.5
    min_calls_before_rate: int = 10
    exceptions_to_track: tuple = (Exception,)
    exceptions_to_ignore: tuple = ()


@dataclass
class CircuitStats:
    """Circuit breaker statistics."""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    state_changed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    @property
    def failure_rate(self) -> float:
        """Calculate failure rate."""
        if self.total_calls == 0:
            return 0.0
        return self.failed_calls / self.total_calls
    
    def reset(self) -> None:
        """Reset statistics."""
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.consecutive_failures = 0
        self.consecutive_successes = 0


class CircuitBreaker:
    """
    Production-grade circuit breaker implementation.
    
    Features:
    - Configurable thresholds
    - Failure rate tracking
    - Half-open state with limited concurrency
    - Detailed statistics
    - Thread-safe with asyncio locks
    - Event callbacks
    
    Example:
        cb = CircuitBreaker(
            name="deepgram",
            failure_threshold=5,
            timeout_seconds=30.0
        )
        
        async with cb:
            result = await risky_operation()
        
        # Check state
        print(cb.state)  # CircuitState.CLOSED
        print(cb.stats.failure_rate)  # 0.0
    """
    
    # Global registry of circuit breakers
    _registry: Dict[str, "CircuitBreaker"] = {}
    
    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
        *,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout_seconds: float = 30.0,
        half_open_max_calls: int = 3,
        on_state_change: Optional[Callable[[CircuitState, CircuitState], None]] = None,
        on_failure: Optional[Callable[[Exception], None]] = None,
        on_success: Optional[Callable[[], None]] = None,
    ):
        """
        Initialize circuit breaker.
        
        Args:
            name: Unique identifier for this circuit breaker
            config: Full configuration object (overrides individual params)
            failure_threshold: Failures before opening circuit
            success_threshold: Successes in half-open before closing
            timeout_seconds: Time before transitioning to half-open
            half_open_max_calls: Max concurrent calls in half-open
            on_state_change: Callback when state changes
            on_failure: Callback on failure
            on_success: Callback on success
        """
        self.name = name
        
        if config:
            self.config = config
        else:
            self.config = CircuitBreakerConfig(
                failure_threshold=failure_threshold,
                success_threshold=success_threshold,
                timeout_seconds=timeout_seconds,
                half_open_max_calls=half_open_max_calls,
            )
        
        self._state = CircuitState.CLOSED
        self._stats = CircuitStats()
        self._lock = asyncio.Lock()
        self._half_open_calls = 0
        
        # Callbacks
        self._on_state_change = on_state_change
        self._on_failure = on_failure
        self._on_success = on_success
        
        # Recent failures for windowing (last N failures with timestamps)
        self._recent_failures: List[datetime] = []
        
        # Register in global registry
        CircuitBreaker._registry[name] = self
        
        logger.info(f"Circuit breaker '{name}' initialized with config: {self.config}")
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state
    
    @property
    def stats(self) -> CircuitStats:
        """Get circuit statistics."""
        return self._stats
    
    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)."""
        return self._state == CircuitState.CLOSED
    
    @property
    def is_open(self) -> bool:
        """Check if circuit is open (blocking requests)."""
        return self._state == CircuitState.OPEN
    
    @property
    def is_half_open(self) -> bool:
        """Check if circuit is half-open (testing)."""
        return self._state == CircuitState.HALF_OPEN
    
    async def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new state with logging and callbacks."""
        if self._state == new_state:
            return
        
        old_state = self._state
        self._state = new_state
        self._stats.state_changed_at = datetime.now(timezone.utc)
        
        logger.warning(
            f"Circuit breaker '{self.name}' state changed: "
            f"{old_state.value} -> {new_state.value}"
        )
        
        if new_state == CircuitState.HALF_OPEN:
            self._half_open_calls = 0
        
        if new_state == CircuitState.CLOSED:
            self._stats.reset()
        
        if self._on_state_change:
            try:
                self._on_state_change(old_state, new_state)
            except Exception as e:
                logger.error(f"Error in state change callback: {e}")
    
    async def _check_state(self) -> None:
        """Check and update state based on conditions."""
        if self._state == CircuitState.OPEN:
            # Check if timeout has passed
            elapsed = (
                datetime.now(timezone.utc) - self._stats.state_changed_at
            ).total_seconds()
            
            if elapsed >= self.config.timeout_seconds:
                await self._transition_to(CircuitState.HALF_OPEN)
    
    def _should_open(self) -> bool:
        """Determine if circuit should open based on failures."""
        # Check consecutive failures
        if self._stats.consecutive_failures >= self.config.failure_threshold:
            return True
        
        # Check failure rate (only if enough calls)
        if self._stats.total_calls >= self.config.min_calls_before_rate:
            if self._stats.failure_rate >= self.config.failure_rate_threshold:
                return True
        
        return False
    
    def _is_tracked_exception(self, exc: Exception) -> bool:
        """Check if exception should be tracked as a failure."""
        # First check if it's in the ignore list
        if isinstance(exc, self.config.exceptions_to_ignore):
            return False
        
        # Then check if it's in the track list
        return isinstance(exc, self.config.exceptions_to_track)
    
    async def _record_success(self) -> None:
        """Record a successful call."""
        async with self._lock:
            self._stats.total_calls += 1
            self._stats.successful_calls += 1
            self._stats.consecutive_successes += 1
            self._stats.consecutive_failures = 0
            self._stats.last_success_time = datetime.now(timezone.utc)
            
            if self._state == CircuitState.HALF_OPEN:
                if self._stats.consecutive_successes >= self.config.success_threshold:
                    await self._transition_to(CircuitState.CLOSED)
            
            if self._on_success:
                try:
                    self._on_success()
                except Exception as e:
                    logger.error(f"Error in success callback: {e}")
    
    async def _record_failure(self, exc: Exception) -> None:
        """Record a failed call."""
        async with self._lock:
            self._stats.total_calls += 1
            self._stats.failed_calls += 1
            self._stats.consecutive_failures += 1
            self._stats.consecutive_successes = 0
            self._stats.last_failure_time = datetime.now(timezone.utc)
            
            # Add to recent failures
            self._recent_failures.append(datetime.now(timezone.utc))
            
            # Keep only recent failures (last N)
            if len(self._recent_failures) > 100:
                self._recent_failures = self._recent_failures[-100:]
            
            logger.warning(
                f"Circuit breaker '{self.name}' recorded failure "
                f"({self._stats.consecutive_failures}/{self.config.failure_threshold}): {exc}"
            )
            
            if self._state == CircuitState.HALF_OPEN:
                # Any failure in half-open immediately opens
                await self._transition_to(CircuitState.OPEN)
            elif self._state == CircuitState.CLOSED:
                if self._should_open():
                    await self._transition_to(CircuitState.OPEN)
            
            if self._on_failure:
                try:
                    self._on_failure(exc)
                except Exception as e:
                    logger.error(f"Error in failure callback: {e}")
    
    async def _can_execute(self) -> bool:
        """Check if a call can be executed."""
        async with self._lock:
            await self._check_state()
            
            if self._state == CircuitState.CLOSED:
                return True
            
            if self._state == CircuitState.OPEN:
                self._stats.rejected_calls += 1
                return False
            
            # Half-open: limited concurrency
            if self._half_open_calls >= self.config.half_open_max_calls:
                self._stats.rejected_calls += 1
                return False
            
            self._half_open_calls += 1
            return True
    
    async def execute(
        self,
        func: Callable[..., Awaitable[T]],
        *args,
        **kwargs
    ) -> T:
        """
        Execute a function through the circuit breaker.
        
        Args:
            func: Async function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Result of the function
        
        Raises:
            CircuitBreakerOpenError: If circuit is open
            Original exception if function fails
        """
        if not await self._can_execute():
            raise CircuitBreakerOpenError(
                service_name=self.name,
                retry_after=int(self.config.timeout_seconds),
            )
        
        try:
            result = await func(*args, **kwargs)
            await self._record_success()
            return result
        except Exception as exc:
            if self._is_tracked_exception(exc):
                await self._record_failure(exc)
            raise
        finally:
            if self._state == CircuitState.HALF_OPEN:
                async with self._lock:
                    self._half_open_calls = max(0, self._half_open_calls - 1)
    
    async def __aenter__(self) -> "CircuitBreaker":
        """Context manager entry - check if can execute."""
        if not await self._can_execute():
            raise CircuitBreakerOpenError(
                service_name=self.name,
                retry_after=int(self.config.timeout_seconds),
            )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Context manager exit - record success or failure."""
        if self._state == CircuitState.HALF_OPEN:
            async with self._lock:
                self._half_open_calls = max(0, self._half_open_calls - 1)
        
        if exc_type is None:
            await self._record_success()
        elif exc_val and self._is_tracked_exception(exc_val):
            await self._record_failure(exc_val)
        
        return False  # Don't suppress exceptions
    
    def reset(self) -> None:
        """Manually reset the circuit breaker to closed state."""
        self._state = CircuitState.CLOSED
        self._stats.reset()
        self._half_open_calls = 0
        self._recent_failures.clear()
        logger.info(f"Circuit breaker '{self.name}' manually reset")
    
    def to_dict(self) -> Dict[str, Any]:
        """Get circuit breaker status as dictionary."""
        return {
            "name": self.name,
            "state": self._state.value,
            "stats": {
                "total_calls": self._stats.total_calls,
                "successful_calls": self._stats.successful_calls,
                "failed_calls": self._stats.failed_calls,
                "rejected_calls": self._stats.rejected_calls,
                "failure_rate": round(self._stats.failure_rate, 3),
                "consecutive_failures": self._stats.consecutive_failures,
                "consecutive_successes": self._stats.consecutive_successes,
            },
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "success_threshold": self.config.success_threshold,
                "timeout_seconds": self.config.timeout_seconds,
            },
            "last_failure": (
                self._stats.last_failure_time.isoformat()
                if self._stats.last_failure_time else None
            ),
            "state_changed_at": self._stats.state_changed_at.isoformat(),
        }
    
    @classmethod
    def get(cls, name: str) -> Optional["CircuitBreaker"]:
        """Get a circuit breaker by name from the registry."""
        return cls._registry.get(name)
    
    @classmethod
    def get_all(cls) -> Dict[str, "CircuitBreaker"]:
        """Get all registered circuit breakers."""
        return cls._registry.copy()
    
    @classmethod
    def get_all_status(cls) -> Dict[str, Dict[str, Any]]:
        """Get status of all circuit breakers."""
        return {name: cb.to_dict() for name, cb in cls._registry.items()}


def circuit_breaker(
    name: str,
    *,
    failure_threshold: int = 5,
    success_threshold: int = 2,
    timeout_seconds: float = 30.0,
    half_open_max_calls: int = 3,
    exceptions_to_track: tuple = (Exception,),
    exceptions_to_ignore: tuple = (),
) -> Callable:
    """
    Decorator to wrap a function with a circuit breaker.
    
    Args:
        name: Circuit breaker name
        failure_threshold: Failures before opening
        success_threshold: Successes before closing
        timeout_seconds: Time before half-open
        half_open_max_calls: Max calls in half-open
        exceptions_to_track: Exceptions that count as failures
        exceptions_to_ignore: Exceptions that don't count as failures
    
    Example:
        @circuit_breaker("openai", failure_threshold=3, timeout_seconds=60)
        async def call_openai(prompt: str) -> str:
            return await openai.chat(prompt)
    """
    config = CircuitBreakerConfig(
        failure_threshold=failure_threshold,
        success_threshold=success_threshold,
        timeout_seconds=timeout_seconds,
        half_open_max_calls=half_open_max_calls,
        exceptions_to_track=exceptions_to_track,
        exceptions_to_ignore=exceptions_to_ignore,
    )
    
    # Get or create circuit breaker
    cb = CircuitBreaker.get(name)
    if cb is None:
        cb = CircuitBreaker(name, config=config)
    
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            return await cb.execute(func, *args, **kwargs)
        
        # Attach circuit breaker reference
        wrapper.circuit_breaker = cb
        return wrapper
    
    return decorator
