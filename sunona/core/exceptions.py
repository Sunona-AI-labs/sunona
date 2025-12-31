"""
Sunona Voice AI - Exception Hierarchy

Production-grade exception classes with rich error context,
structured for logging, monitoring, and user-friendly messaging.

Exception Hierarchy:
    SunonaError (base)
    ├── ConfigurationError
    ├── AuthenticationError
    ├── RateLimitError
    ├── InsufficientBalanceError
    ├── ProviderError (base for provider issues)
    │   ├── TranscriptionError
    │   ├── SynthesisError
    │   ├── LLMError
    │   └── TelephonyError
    ├── CircuitBreakerOpenError
    ├── ValidationError
    └── TimeoutError
"""

import traceback
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Type
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels for monitoring and alerting."""
    LOW = "low"           # Recoverable, no action needed
    MEDIUM = "medium"     # May need attention, logged
    HIGH = "high"         # Needs investigation
    CRITICAL = "critical" # Immediate action required


class ErrorCategory(Enum):
    """Error categories for classification and routing."""
    CONFIGURATION = "configuration"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    PROVIDER = "provider"
    NETWORK = "network"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    BILLING = "billing"
    INTERNAL = "internal"


class SunonaError(Exception):
    """
    Base exception for all Sunona errors.
    
    Provides structured error information for:
    - Logging with full context
    - API responses with safe user messages
    - Monitoring and alerting
    - Error aggregation and analysis
    
    Attributes:
        message: Technical error message
        user_message: Safe message for end users
        error_code: Unique error identifier
        severity: Error severity level
        category: Error category
        context: Additional context data
        timestamp: When the error occurred
        trace_id: Request trace ID for correlation
    """
    
    # Default error properties - override in subclasses
    default_message = "An unexpected error occurred"
    default_user_message = "Something went wrong. Please try again."
    default_error_code = "SUNONA_ERROR"
    default_severity = ErrorSeverity.MEDIUM
    default_category = ErrorCategory.INTERNAL
    default_http_status = 500
    default_retryable = False
    
    def __init__(
        self,
        message: Optional[str] = None,
        *,
        user_message: Optional[str] = None,
        error_code: Optional[str] = None,
        severity: Optional[ErrorSeverity] = None,
        category: Optional[ErrorCategory] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        trace_id: Optional[str] = None,
        retryable: Optional[bool] = None,
        retry_after: Optional[int] = None,  # seconds
    ):
        self.message = message or self.default_message
        self.user_message = user_message or self.default_user_message
        self.error_code = error_code or self.default_error_code
        self.severity = severity or self.default_severity
        self.category = category or self.default_category
        self.context = context or {}
        self.cause = cause
        self.trace_id = trace_id
        self.retryable = retryable if retryable is not None else self.default_retryable
        self.retry_after = retry_after
        self.timestamp = datetime.now(timezone.utc)
        self.http_status = self.default_http_status
        
        # Capture stack trace
        self.stack_trace = traceback.format_exc() if cause else None
        
        super().__init__(self.message)
        
        # Log the error with appropriate level
        self._log_error()
    
    def _log_error(self) -> None:
        """Log the error with appropriate severity level."""
        log_data = {
            "error_code": self.error_code,
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "context": self.context,
            "trace_id": self.trace_id,
            "timestamp": self.timestamp.isoformat(),
        }
        
        if self.cause:
            log_data["cause"] = str(self.cause)
        
        if self.severity == ErrorSeverity.CRITICAL:
            logger.critical(f"[{self.error_code}] {self.message}", extra=log_data)
        elif self.severity == ErrorSeverity.HIGH:
            logger.error(f"[{self.error_code}] {self.message}", extra=log_data)
        elif self.severity == ErrorSeverity.MEDIUM:
            logger.warning(f"[{self.error_code}] {self.message}", extra=log_data)
        else:
            logger.info(f"[{self.error_code}] {self.message}", extra=log_data)
    
    def to_dict(self, include_internal: bool = False) -> Dict[str, Any]:
        """
        Convert to dictionary for API responses.
        
        Args:
            include_internal: Include internal details (for debugging)
        """
        result = {
            "error": True,
            "error_code": self.error_code,
            "message": self.user_message,
            "timestamp": self.timestamp.isoformat(),
            "retryable": self.retryable,
        }
        
        if self.retry_after:
            result["retry_after"] = self.retry_after
        
        if self.trace_id:
            result["trace_id"] = self.trace_id
        
        if include_internal:
            result["internal"] = {
                "technical_message": self.message,
                "category": self.category.value,
                "severity": self.severity.value,
                "context": self.context,
            }
            if self.cause:
                result["internal"]["cause"] = str(self.cause)
        
        return result
    
    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"
    
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"error_code={self.error_code!r}, "
            f"severity={self.severity.value!r})"
        )


# =============================================================================
# Configuration Errors
# =============================================================================

class ConfigurationError(SunonaError):
    """Raised when configuration is invalid or missing."""
    
    default_message = "Invalid or missing configuration"
    default_user_message = "The service is not properly configured."
    default_error_code = "CONFIG_ERROR"
    default_severity = ErrorSeverity.HIGH
    default_category = ErrorCategory.CONFIGURATION
    default_http_status = 500
    
    @classmethod
    def missing_env_var(cls, var_name: str) -> "ConfigurationError":
        """Factory for missing environment variable errors."""
        return cls(
            message=f"Missing required environment variable: {var_name}",
            error_code="CONFIG_MISSING_ENV",
            context={"variable": var_name},
        )
    
    @classmethod
    def invalid_value(
        cls, 
        key: str, 
        value: Any, 
        expected: str
    ) -> "ConfigurationError":
        """Factory for invalid configuration value errors."""
        return cls(
            message=f"Invalid configuration value for '{key}': {value}. Expected: {expected}",
            error_code="CONFIG_INVALID_VALUE",
            context={"key": key, "value": str(value), "expected": expected},
        )


# =============================================================================
# Authentication & Authorization Errors
# =============================================================================

class AuthenticationError(SunonaError):
    """Raised when authentication fails."""
    
    default_message = "Authentication failed"
    default_user_message = "Invalid credentials. Please check your API key."
    default_error_code = "AUTH_FAILED"
    default_severity = ErrorSeverity.MEDIUM
    default_category = ErrorCategory.AUTHENTICATION
    default_http_status = 401
    
    @classmethod
    def invalid_api_key(cls) -> "AuthenticationError":
        return cls(
            message="Invalid or expired API key",
            error_code="AUTH_INVALID_KEY",
        )
    
    @classmethod
    def expired_token(cls) -> "AuthenticationError":
        return cls(
            message="Authentication token has expired",
            error_code="AUTH_EXPIRED",
            user_message="Your session has expired. Please log in again.",
        )


class AuthorizationError(SunonaError):
    """Raised when authorization fails."""
    
    default_message = "Access denied"
    default_user_message = "You don't have permission to perform this action."
    default_error_code = "AUTHZ_DENIED"
    default_severity = ErrorSeverity.MEDIUM
    default_category = ErrorCategory.AUTHORIZATION
    default_http_status = 403


# =============================================================================
# Rate Limiting Errors
# =============================================================================

class RateLimitError(SunonaError):
    """Raised when rate limit is exceeded."""
    
    default_message = "Rate limit exceeded"
    default_user_message = "Too many requests. Please wait and try again."
    default_error_code = "RATE_LIMIT_EXCEEDED"
    default_severity = ErrorSeverity.LOW
    default_category = ErrorCategory.RATE_LIMIT
    default_http_status = 429
    default_retryable = True
    
    def __init__(
        self,
        message: Optional[str] = None,
        retry_after: int = 60,
        limit: Optional[int] = None,
        window: Optional[int] = None,
        **kwargs
    ):
        context = kwargs.pop("context", {})
        context.update({
            "limit": limit,
            "window_seconds": window,
            "retry_after": retry_after,
        })
        
        super().__init__(
            message=message,
            retry_after=retry_after,
            context=context,
            **kwargs
        )


# =============================================================================
# Billing Errors
# =============================================================================

class InsufficientBalanceError(SunonaError):
    """Raised when account balance is too low."""
    
    default_message = "Insufficient account balance"
    default_user_message = "Your account balance is too low. Please top up to continue."
    default_error_code = "BILLING_INSUFFICIENT"
    default_severity = ErrorSeverity.MEDIUM
    default_category = ErrorCategory.BILLING
    default_http_status = 402
    
    def __init__(
        self,
        message: Optional[str] = None,
        current_balance: Optional[float] = None,
        required_amount: Optional[float] = None,
        **kwargs
    ):
        context = kwargs.pop("context", {})
        context.update({
            "current_balance": current_balance,
            "required_amount": required_amount,
        })
        
        super().__init__(message=message, context=context, **kwargs)


# =============================================================================
# Provider Errors (Base for STT/TTS/LLM/Telephony)
# =============================================================================

class ProviderError(SunonaError):
    """
    Base class for provider-related errors.
    
    Used for errors from external services like:
    - Speech-to-text providers (Deepgram, Azure, etc.)
    - Text-to-speech providers (ElevenLabs, OpenAI, etc.)
    - LLM providers (OpenAI, Anthropic, etc.)
    - Telephony providers (Twilio, Plivo, etc.)
    """
    
    default_message = "External provider error"
    default_user_message = "A service is temporarily unavailable. Please try again."
    default_error_code = "PROVIDER_ERROR"
    default_severity = ErrorSeverity.MEDIUM
    default_category = ErrorCategory.PROVIDER
    default_http_status = 502
    default_retryable = True
    
    def __init__(
        self,
        message: Optional[str] = None,
        provider: Optional[str] = None,
        provider_error_code: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.pop("context", {})
        context.update({
            "provider": provider,
            "provider_error_code": provider_error_code,
        })
        
        super().__init__(message=message, context=context, **kwargs)


class TranscriptionError(ProviderError):
    """Raised when speech-to-text transcription fails."""
    
    default_message = "Transcription failed"
    default_user_message = "I didn't catch that. Could you please repeat?"
    default_error_code = "STT_ERROR"
    
    @classmethod
    def no_speech_detected(cls, provider: str) -> "TranscriptionError":
        return cls(
            message="No speech detected in audio",
            error_code="STT_NO_SPEECH",
            provider=provider,
            severity=ErrorSeverity.LOW,
            retryable=False,
        )
    
    @classmethod
    def unsupported_format(
        cls, 
        provider: str, 
        format: str
    ) -> "TranscriptionError":
        return cls(
            message=f"Audio format '{format}' not supported by {provider}",
            error_code="STT_UNSUPPORTED_FORMAT",
            provider=provider,
            context={"audio_format": format},
            retryable=False,
        )


class SynthesisError(ProviderError):
    """Raised when text-to-speech synthesis fails."""
    
    default_message = "Speech synthesis failed"
    default_user_message = "I'm having trouble speaking. Please hold."
    default_error_code = "TTS_ERROR"
    
    @classmethod
    def voice_not_found(cls, provider: str, voice_id: str) -> "SynthesisError":
        return cls(
            message=f"Voice '{voice_id}' not found in {provider}",
            error_code="TTS_VOICE_NOT_FOUND",
            provider=provider,
            context={"voice_id": voice_id},
            retryable=False,
        )


class LLMError(ProviderError):
    """Raised when LLM inference fails."""
    
    default_message = "Language model error"
    default_user_message = "I'm having trouble thinking. Let me try again."
    default_error_code = "LLM_ERROR"
    
    @classmethod
    def context_length_exceeded(
        cls, 
        provider: str, 
        model: str,
        token_count: int,
        max_tokens: int
    ) -> "LLMError":
        return cls(
            message=f"Context length exceeded: {token_count}/{max_tokens} tokens",
            error_code="LLM_CONTEXT_EXCEEDED",
            provider=provider,
            context={
                "model": model,
                "token_count": token_count,
                "max_tokens": max_tokens,
            },
            retryable=False,
        )
    
    @classmethod
    def content_filtered(cls, provider: str) -> "LLMError":
        return cls(
            message="Content was filtered by safety systems",
            error_code="LLM_CONTENT_FILTERED",
            provider=provider,
            user_message="I can't respond to that. Let's talk about something else.",
            severity=ErrorSeverity.LOW,
            retryable=False,
        )


class TelephonyError(ProviderError):
    """Raised when telephony operations fail."""
    
    default_message = "Telephony error"
    default_user_message = "Call connection issue. Please try again."
    default_error_code = "TELEPHONY_ERROR"
    
    @classmethod
    def call_failed(
        cls, 
        provider: str, 
        reason: str
    ) -> "TelephonyError":
        return cls(
            message=f"Call failed: {reason}",
            error_code="TELEPHONY_CALL_FAILED",
            provider=provider,
            context={"reason": reason},
        )
    
    @classmethod
    def invalid_phone_number(
        cls, 
        phone_number: str
    ) -> "TelephonyError":
        return cls(
            message=f"Invalid phone number format: {phone_number}",
            error_code="TELEPHONY_INVALID_NUMBER",
            user_message="The phone number format is invalid.",
            retryable=False,
        )


# =============================================================================
# Circuit Breaker & Resilience Errors
# =============================================================================

class CircuitBreakerOpenError(SunonaError):
    """Raised when circuit breaker is open (service unavailable)."""
    
    default_message = "Service temporarily unavailable (circuit open)"
    default_user_message = "This service is temporarily unavailable. Please try again later."
    default_error_code = "CIRCUIT_OPEN"
    default_severity = ErrorSeverity.HIGH
    default_category = ErrorCategory.PROVIDER
    default_http_status = 503
    default_retryable = True
    
    def __init__(
        self,
        message: Optional[str] = None,
        service_name: Optional[str] = None,
        retry_after: int = 30,
        **kwargs
    ):
        context = kwargs.pop("context", {})
        context["service_name"] = service_name
        
        super().__init__(
            message=message or f"Circuit breaker open for {service_name}",
            retry_after=retry_after,
            context=context,
            **kwargs
        )


class TimeoutError(SunonaError):
    """Raised when an operation times out."""
    
    default_message = "Operation timed out"
    default_user_message = "The operation took too long. Please try again."
    default_error_code = "TIMEOUT"
    default_severity = ErrorSeverity.MEDIUM
    default_category = ErrorCategory.TIMEOUT
    default_http_status = 504
    default_retryable = True


# =============================================================================
# Validation Errors
# =============================================================================

class ValidationError(SunonaError):
    """Raised when input validation fails."""
    
    default_message = "Validation failed"
    default_user_message = "Invalid input. Please check your request."
    default_error_code = "VALIDATION_ERROR"
    default_severity = ErrorSeverity.LOW
    default_category = ErrorCategory.VALIDATION
    default_http_status = 400
    default_retryable = False
    
    def __init__(
        self,
        message: Optional[str] = None,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ):
        context = kwargs.pop("context", {})
        if field:
            context["field"] = field
        if value is not None:
            context["value"] = str(value)
        
        super().__init__(message=message, context=context, **kwargs)
    
    @classmethod
    def required_field(cls, field: str) -> "ValidationError":
        return cls(
            message=f"Field '{field}' is required",
            error_code="VALIDATION_REQUIRED",
            field=field,
            user_message=f"'{field}' is required.",
        )
    
    @classmethod
    def invalid_format(
        cls, 
        field: str, 
        value: Any, 
        expected_format: str
    ) -> "ValidationError":
        return cls(
            message=f"Invalid format for '{field}': {value}. Expected: {expected_format}",
            error_code="VALIDATION_FORMAT",
            field=field,
            value=value,
            user_message=f"Invalid format for '{field}'. Expected: {expected_format}",
        )


# =============================================================================
# Exception Handler Utility
# =============================================================================

def handle_provider_exception(
    exception: Exception,
    provider: str,
    error_type: Type[ProviderError] = ProviderError,
) -> ProviderError:
    """
    Convert generic exceptions to appropriate ProviderError subclass.
    
    Args:
        exception: The original exception
        provider: Name of the provider
        error_type: The ProviderError subclass to use
    
    Returns:
        Appropriate ProviderError instance
    """
    # Check for known exception types
    exc_name = type(exception).__name__
    exc_str = str(exception).lower()
    
    # Rate limiting
    if "rate" in exc_str and "limit" in exc_str:
        return RateLimitError(
            message=f"{provider} rate limit exceeded: {exception}",
            provider=provider,
            cause=exception,
        )
    
    # Authentication
    if any(word in exc_str for word in ["auth", "unauthorized", "401", "forbidden", "403"]):
        return AuthenticationError(
            message=f"{provider} authentication failed: {exception}",
            cause=exception,
            context={"provider": provider},
        )
    
    # Timeout
    if any(word in exc_str for word in ["timeout", "timed out", "deadline"]):
        return TimeoutError(
            message=f"{provider} request timed out: {exception}",
            cause=exception,
            context={"provider": provider},
        )
    
    # Default to the specified error type
    return error_type(
        message=f"{provider} error: {exception}",
        provider=provider,
        cause=exception,
    )
