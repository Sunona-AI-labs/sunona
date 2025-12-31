"""
Sunona Voice AI - Structured Logging

Production-grade logging with structured format, correlation IDs,
and integrations with monitoring systems.

Features:
- Structured JSON logging
- Request correlation IDs
- Automatic context injection
- Performance timing
- Error tracking
- Log level management
"""

import asyncio
import contextvars
import json
import logging
import sys
import time
import traceback
import uuid
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar

# Context variable for request correlation
request_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "request_id", default=None
)
user_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "user_id", default=None
)
session_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "session_id", default=None
)

T = TypeVar("T")


class StructuredFormatter(logging.Formatter):
    """
    JSON structured log formatter.
    
    Output format:
    {
        "timestamp": "2024-01-01T00:00:00.000Z",
        "level": "INFO",
        "logger": "sunona.llm",
        "message": "Request completed",
        "request_id": "uuid-here",
        "user_id": "user_123",
        "duration_ms": 150.5,
        "extra": {...}
    }
    """
    
    def __init__(
        self,
        include_timestamp: bool = True,
        include_level: bool = True,
        include_logger: bool = True,
        include_location: bool = False,
        pretty: bool = False,
    ):
        super().__init__()
        self.include_timestamp = include_timestamp
        self.include_level = include_level
        self.include_logger = include_logger
        self.include_location = include_location
        self.pretty = pretty
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {}
        
        # Timestamp
        if self.include_timestamp:
            log_data["timestamp"] = datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat()
        
        # Level
        if self.include_level:
            log_data["level"] = record.levelname
        
        # Logger name
        if self.include_logger:
            log_data["logger"] = record.name
        
        # Message
        log_data["message"] = record.getMessage()
        
        # Location (file, line, function)
        if self.include_location:
            log_data["location"] = {
                "file": record.filename,
                "line": record.lineno,
                "function": record.funcName,
            }
        
        # Context variables
        request_id = request_id_var.get()
        if request_id:
            log_data["request_id"] = request_id
        
        user_id = user_id_var.get()
        if user_id:
            log_data["user_id"] = user_id
        
        session_id = session_id_var.get()
        if session_id:
            log_data["session_id"] = session_id
        
        # Extra fields from record
        if hasattr(record, "__dict__"):
            standard_fields = {
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "pathname", "process", "processName", "relativeCreated",
                "stack_info", "exc_info", "exc_text", "thread", "threadName",
                "message", "asctime",
            }
            
            extra = {}
            for key, value in record.__dict__.items():
                if key not in standard_fields and not key.startswith("_"):
                    try:
                        # Attempt to serialize
                        json.dumps(value)
                        extra[key] = value
                    except (TypeError, ValueError):
                        extra[key] = str(value)
            
            if extra:
                log_data["extra"] = extra
        
        # Exception info
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }
        
        # Format as JSON
        if self.pretty:
            return json.dumps(log_data, indent=2, default=str)
        return json.dumps(log_data, default=str)


class ConsoleFormatter(logging.Formatter):
    """
    Human-readable console formatter with colors.
    
    Output format:
    2024-01-01 00:00:00 | INFO     | sunona.llm | Request completed
    """
    
    # ANSI colors
    COLORS = {
        "DEBUG": "\033[36m",    # Cyan
        "INFO": "\033[32m",     # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",    # Red
        "CRITICAL": "\033[35m", # Magenta
    }
    RESET = "\033[0m"
    
    def __init__(self, use_colors: bool = True):
        super().__init__()
        self.use_colors = use_colors
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record for console."""
        timestamp = datetime.fromtimestamp(
            record.created, tz=timezone.utc
        ).strftime("%Y-%m-%d %H:%M:%S")
        
        level = record.levelname.ljust(8)
        logger_name = record.name[:30].ljust(30)
        message = record.getMessage()
        
        # Color the level
        if self.use_colors and record.levelname in self.COLORS:
            level = f"{self.COLORS[record.levelname]}{level}{self.RESET}"
        
        # Add request ID if present
        request_id = request_id_var.get()
        if request_id:
            prefix = f"[{request_id[:8]}] "
        else:
            prefix = ""
        
        output = f"{timestamp} | {level} | {logger_name} | {prefix}{message}"
        
        # Add exception
        if record.exc_info:
            output += "\n" + self.formatException(record.exc_info)
        
        return output


def setup_logging(
    level: str = "INFO",
    format_type: str = "console",
    log_file: Optional[str] = None,
    include_location: bool = False,
) -> None:
    """
    Set up application logging.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: "console" for human-readable or "json" for structured
        log_file: Optional file path for file logging
        include_location: Include file/line/function in logs
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    if format_type == "json":
        console_handler.setFormatter(StructuredFormatter(
            include_location=include_location,
        ))
    else:
        console_handler.setFormatter(ConsoleFormatter(
            use_colors=sys.stdout.isatty(),
        ))
    
    root_logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(StructuredFormatter(
            include_location=True,
        ))
        root_logger.addHandler(file_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("websockets").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured logger
    """
    return logging.getLogger(name)


# =============================================================================
# Context Management
# =============================================================================

def generate_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())


def set_request_context(
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> str:
    """
    Set logging context for the current request.
    
    Args:
        request_id: Request correlation ID (generated if not provided)
        user_id: User identifier
        session_id: Session identifier
    
    Returns:
        The request ID
    """
    req_id = request_id or generate_request_id()
    request_id_var.set(req_id)
    
    if user_id:
        user_id_var.set(user_id)
    
    if session_id:
        session_id_var.set(session_id)
    
    return req_id


def clear_request_context() -> None:
    """Clear logging context."""
    request_id_var.set(None)
    user_id_var.set(None)
    session_id_var.set(None)


class LogContext:
    """
    Context manager for request logging context.
    
    Example:
        async with LogContext(user_id="user_123"):
            logger.info("Processing request")  # Includes user_id
    """
    
    def __init__(
        self,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        self.request_id = request_id
        self.user_id = user_id
        self.session_id = session_id
        self._tokens: Dict[str, Any] = {}
    
    def __enter__(self) -> "LogContext":
        if self.request_id or not request_id_var.get():
            req_id = self.request_id or generate_request_id()
            self._tokens["request_id"] = request_id_var.set(req_id)
        
        if self.user_id:
            self._tokens["user_id"] = user_id_var.set(self.user_id)
        
        if self.session_id:
            self._tokens["session_id"] = session_id_var.set(self.session_id)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        for key, token in self._tokens.items():
            if key == "request_id":
                request_id_var.reset(token)
            elif key == "user_id":
                user_id_var.reset(token)
            elif key == "session_id":
                session_id_var.reset(token)
    
    async def __aenter__(self) -> "LogContext":
        return self.__enter__()
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self.__exit__(exc_type, exc_val, exc_tb)


# =============================================================================
# Performance Logging
# =============================================================================

class Timer:
    """
    Timer for measuring and logging execution time.
    
    Example:
        with Timer("process_audio", logger):
            result = process_audio(data)
        
        # Logs: "process_audio completed in 150.5ms"
    """
    
    def __init__(
        self,
        name: str,
        logger: Optional[logging.Logger] = None,
        log_level: int = logging.DEBUG,
        threshold_ms: Optional[float] = None,
    ):
        """
        Initialize timer.
        
        Args:
            name: Operation name
            logger: Logger to use (creates one if not provided)
            log_level: Log level for timing message
            threshold_ms: Only log if duration exceeds this threshold
        """
        self.name = name
        self.logger = logger or logging.getLogger(__name__)
        self.log_level = log_level
        self.threshold_ms = threshold_ms
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
    
    @property
    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds."""
        if self.start_time is None:
            return 0.0
        end = self.end_time or time.perf_counter()
        return (end - self.start_time) * 1000
    
    def __enter__(self) -> "Timer":
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.end_time = time.perf_counter()
        elapsed = self.elapsed_ms
        
        # Check threshold
        if self.threshold_ms and elapsed < self.threshold_ms:
            return
        
        # Log the timing
        extra = {"duration_ms": round(elapsed, 2), "operation": self.name}
        
        if exc_type:
            self.logger.log(
                self.log_level,
                f"{self.name} failed after {elapsed:.1f}ms: {exc_val}",
                extra=extra,
            )
        else:
            self.logger.log(
                self.log_level,
                f"{self.name} completed in {elapsed:.1f}ms",
                extra=extra,
            )
    
    async def __aenter__(self) -> "Timer":
        return self.__enter__()
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self.__exit__(exc_type, exc_val, exc_tb)


def log_timing(
    name: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
    log_level: int = logging.DEBUG,
    threshold_ms: Optional[float] = None,
) -> Callable:
    """
    Decorator to log function execution time.
    
    Example:
        @log_timing("process_request", threshold_ms=100)
        async def process_request(data):
            ...
    """
    def decorator(func: Callable) -> Callable:
        operation_name = name or func.__name__
        log = logger or logging.getLogger(func.__module__)
        
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                async with Timer(operation_name, log, log_level, threshold_ms):
                    return await func(*args, **kwargs)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                with Timer(operation_name, log, log_level, threshold_ms):
                    return func(*args, **kwargs)
            return sync_wrapper
    
    return decorator


# =============================================================================
# Convenience Functions
# =============================================================================

def log_error(
    logger: logging.Logger,
    message: str,
    error: Exception,
    **extra
) -> None:
    """Log an error with full context."""
    logger.error(
        message,
        exc_info=error,
        extra={
            "error_type": type(error).__name__,
            "error_message": str(error),
            **extra,
        },
    )


def log_api_call(
    logger: logging.Logger,
    method: str,
    url: str,
    status_code: int,
    duration_ms: float,
    **extra
) -> None:
    """Log an API call with standard fields."""
    level = logging.INFO if status_code < 400 else logging.WARNING
    
    logger.log(
        level,
        f"{method} {url} -> {status_code} ({duration_ms:.1f}ms)",
        extra={
            "http_method": method,
            "url": url,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 2),
            **extra,
        },
    )
