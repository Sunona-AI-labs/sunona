"""
Sunona Voice AI - Core Infrastructure

Production-grade utilities for resilient, scalable applications.

Modules:
- circuit_breaker: Fault tolerance for external services
- retry: Exponential backoff retry logic
- health: Health checking and monitoring
- logging: Structured logging with correlation IDs
- exceptions: Custom exception hierarchy
- rate_limiter: Request rate limiting
- websocket_manager: WebSocket connection management
"""

from sunona.core.exceptions import (
    SunonaError,
    ProviderError,
    ConfigurationError,
    AuthenticationError,
    RateLimitError,
    InsufficientBalanceError,
    TranscriptionError,
    SynthesisError,
    LLMError,
    TelephonyError,
    CircuitBreakerOpenError,
)

from sunona.core.circuit_breaker import (
    CircuitBreaker,
    CircuitState,
    circuit_breaker,
)

from sunona.core.retry import (
    RetryConfig,
    retry_async,
    retry_with_backoff,
)

from sunona.core.health import (
    HealthCheck,
    HealthStatus,
    ComponentHealth,
)

from sunona.core.rate_limiter import (
    RateLimiter,
    SlidingWindowRateLimiter,
    TokenBucketRateLimiter,
)

from sunona.core.logging import (
    setup_logging,
    get_logger,
    LogContext,
    Timer,
    log_timing,
    set_request_context,
    clear_request_context,
)

from sunona.core.websocket_manager import (
    WebSocketManager,
    ConnectionInfo,
    ConnectionState,
    get_websocket_manager,
)

__all__ = [
    # Exceptions
    "SunonaError",
    "ProviderError",
    "ConfigurationError",
    "AuthenticationError",
    "RateLimitError",
    "InsufficientBalanceError",
    "TranscriptionError",
    "SynthesisError",
    "LLMError",
    "TelephonyError",
    "CircuitBreakerOpenError",
    # Circuit Breaker
    "CircuitBreaker",
    "CircuitState",
    "circuit_breaker",
    # Retry
    "RetryConfig",
    "retry_async",
    "retry_with_backoff",
    # Health
    "HealthCheck",
    "HealthStatus",
    "ComponentHealth",
    # Rate Limiter
    "RateLimiter",
    "SlidingWindowRateLimiter",
    "TokenBucketRateLimiter",
    # Logging
    "setup_logging",
    "get_logger",
    "LogContext",
    "Timer",
    "log_timing",
    "set_request_context",
    "clear_request_context",
    # WebSocket
    "WebSocketManager",
    "ConnectionInfo",
    "ConnectionState",
    "get_websocket_manager",
]

