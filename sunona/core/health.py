"""
Sunona Voice AI - Health Check System

Production-grade health monitoring for all system components.
Provides comprehensive health status for load balancers, 
monitoring systems, and operational dashboards.

Components monitored:
- Database connections (PostgreSQL, Redis)
- External providers (STT, TTS, LLM, Telephony)
- Internal services
- Memory and resource usage
"""

import asyncio
import logging
import os
import psutil
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"       # All good
    DEGRADED = "degraded"     # Partially working
    UNHEALTHY = "unhealthy"   # Not working
    UNKNOWN = "unknown"       # Cannot determine


@dataclass
class ComponentHealth:
    """
    Health status for a single component.
    
    Attributes:
        name: Component name
        status: Health status
        message: Status message
        latency_ms: Response time in milliseconds
        last_check: When last checked
        details: Additional details
        error: Error information if unhealthy
    """
    name: str
    status: HealthStatus = HealthStatus.UNKNOWN
    message: str = ""
    latency_ms: Optional[float] = None
    last_check: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "last_check": self.last_check.isoformat(),
        }
        
        if self.latency_ms is not None:
            result["latency_ms"] = round(self.latency_ms, 2)
        
        if self.details:
            result["details"] = self.details
        
        if self.error:
            result["error"] = self.error
        
        return result


@dataclass
class SystemHealth:
    """
    Overall system health status.
    
    Aggregates health from all components.
    """
    status: HealthStatus = HealthStatus.UNKNOWN
    components: Dict[str, ComponentHealth] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = ""
    uptime_seconds: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "version": self.version,
            "uptime_seconds": round(self.uptime_seconds, 2),
            "components": {
                name: comp.to_dict() 
                for name, comp in self.components.items()
            },
        }


# Type for health check functions
HealthCheckFunc = Callable[[], Awaitable[ComponentHealth]]


class HealthCheck:
    """
    Centralized health check system.
    
    Features:
    - Register custom health checks
    - Parallel health check execution
    - Caching to prevent frequent checks
    - Aggregate health status
    - Resource monitoring
    
    Example:
        health = HealthCheck()
        
        # Register checks
        health.register("redis", check_redis)
        health.register("postgres", check_postgres)
        
        # Run all checks
        result = await health.check_all()
        print(result.status)  # HealthStatus.HEALTHY
        
        # Get specific check
        redis_health = await health.check("redis")
    """
    
    def __init__(
        self,
        version: str = "1.0.0",
        cache_ttl_seconds: float = 5.0,
    ):
        """
        Initialize health check system.
        
        Args:
            version: Application version
            cache_ttl_seconds: How long to cache health results
        """
        self.version = version
        self.cache_ttl = cache_ttl_seconds
        self._checks: Dict[str, HealthCheckFunc] = {}
        self._cache: Dict[str, ComponentHealth] = {}
        self._cache_times: Dict[str, float] = {}
        self._start_time = time.time()
        
        # Register default checks
        self._register_defaults()
    
    def _register_defaults(self) -> None:
        """Register default health checks."""
        self.register("system", self._check_system)
    
    def register(
        self,
        name: str,
        check_func: HealthCheckFunc,
    ) -> None:
        """
        Register a health check.
        
        Args:
            name: Unique name for the check
            check_func: Async function that returns ComponentHealth
        """
        self._checks[name] = check_func
        logger.debug(f"Registered health check: {name}")
    
    def unregister(self, name: str) -> None:
        """Remove a health check."""
        self._checks.pop(name, None)
        self._cache.pop(name, None)
        self._cache_times.pop(name, None)
    
    async def check(
        self,
        name: str,
        use_cache: bool = True,
    ) -> ComponentHealth:
        """
        Run a specific health check.
        
        Args:
            name: Name of the check to run
            use_cache: Whether to use cached results
        
        Returns:
            ComponentHealth for the component
        """
        if name not in self._checks:
            return ComponentHealth(
                name=name,
                status=HealthStatus.UNKNOWN,
                message=f"Unknown health check: {name}",
            )
        
        # Check cache
        if use_cache and name in self._cache:
            cache_age = time.time() - self._cache_times.get(name, 0)
            if cache_age < self.cache_ttl:
                return self._cache[name]
        
        # Run check
        start = time.time()
        try:
            result = await asyncio.wait_for(
                self._checks[name](),
                timeout=10.0,  # 10 second timeout per check
            )
            result.latency_ms = (time.time() - start) * 1000
        except asyncio.TimeoutError:
            result = ComponentHealth(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message="Health check timed out",
                latency_ms=(time.time() - start) * 1000,
                error="Timeout after 10 seconds",
            )
        except Exception as e:
            result = ComponentHealth(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {e}",
                latency_ms=(time.time() - start) * 1000,
                error=str(e),
            )
        
        # Update cache
        self._cache[name] = result
        self._cache_times[name] = time.time()
        
        return result
    
    async def check_all(
        self,
        use_cache: bool = True,
        include_details: bool = True,
    ) -> SystemHealth:
        """
        Run all registered health checks.
        
        Args:
            use_cache: Whether to use cached results
            include_details: Whether to include component details
        
        Returns:
            SystemHealth with aggregate status
        """
        # Run all checks in parallel
        tasks = [
            self.check(name, use_cache=use_cache)
            for name in self._checks
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        components: Dict[str, ComponentHealth] = {}
        for name, result in zip(self._checks.keys(), results):
            if isinstance(result, Exception):
                components[name] = ComponentHealth(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=str(result),
                    error=str(result),
                )
            else:
                components[name] = result
        
        # Determine aggregate status
        overall_status = self._aggregate_status(components)
        
        return SystemHealth(
            status=overall_status,
            components=components if include_details else {},
            timestamp=datetime.now(timezone.utc),
            version=self.version,
            uptime_seconds=time.time() - self._start_time,
        )
    
    def _aggregate_status(
        self,
        components: Dict[str, ComponentHealth],
    ) -> HealthStatus:
        """Determine overall status from components."""
        if not components:
            return HealthStatus.UNKNOWN
        
        statuses = [c.status for c in components.values()]
        
        # Any unhealthy = unhealthy
        if any(s == HealthStatus.UNHEALTHY for s in statuses):
            return HealthStatus.UNHEALTHY
        
        # Any degraded = degraded
        if any(s == HealthStatus.DEGRADED for s in statuses):
            return HealthStatus.DEGRADED
        
        # All healthy = healthy
        if all(s == HealthStatus.HEALTHY for s in statuses):
            return HealthStatus.HEALTHY
        
        return HealthStatus.UNKNOWN
    
    async def _check_system(self) -> ComponentHealth:
        """Check system resources."""
        try:
            # Get memory info
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Get CPU info
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Get disk info
            disk = psutil.disk_usage("/")
            disk_percent = disk.percent
            
            # Determine status
            if memory_percent > 90 or disk_percent > 90:
                status = HealthStatus.UNHEALTHY
                message = "Critical resource usage"
            elif memory_percent > 80 or cpu_percent > 80 or disk_percent > 80:
                status = HealthStatus.DEGRADED
                message = "High resource usage"
            else:
                status = HealthStatus.HEALTHY
                message = "System resources OK"
            
            return ComponentHealth(
                name="system",
                status=status,
                message=message,
                details={
                    "memory_percent": round(memory_percent, 1),
                    "memory_available_mb": round(memory.available / 1024 / 1024, 1),
                    "cpu_percent": round(cpu_percent, 1),
                    "disk_percent": round(disk_percent, 1),
                    "disk_free_gb": round(disk.free / 1024 / 1024 / 1024, 1),
                    "python_pid": os.getpid(),
                },
            )
        except Exception as e:
            return ComponentHealth(
                name="system",
                status=HealthStatus.UNKNOWN,
                message=f"Failed to check system: {e}",
                error=str(e),
            )
    
    async def liveness(self) -> Dict[str, Any]:
        """
        Simple liveness check (is the service running?).
        Used by Kubernetes liveness probes.
        """
        return {
            "status": "alive",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    
    async def readiness(self) -> Dict[str, Any]:
        """
        Readiness check (is the service ready to accept traffic?).
        Used by Kubernetes readiness probes.
        """
        health = await self.check_all(use_cache=True)
        
        ready = health.status in (HealthStatus.HEALTHY, HealthStatus.DEGRADED)
        
        return {
            "ready": ready,
            "status": health.status.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# =============================================================================
# Pre-built Health Checks
# =============================================================================

async def check_redis(host: str = "localhost", port: int = 6379) -> ComponentHealth:
    """
    Health check for Redis.
    
    Args:
        host: Redis host
        port: Redis port
    """
    try:
        import redis.asyncio as redis
        
        client = redis.Redis(host=host, port=port, decode_responses=True)
        start = time.time()
        
        # Ping Redis
        pong = await client.ping()
        latency = (time.time() - start) * 1000
        
        # Get info
        info = await client.info("server")
        
        await client.close()
        
        return ComponentHealth(
            name="redis",
            status=HealthStatus.HEALTHY if pong else HealthStatus.UNHEALTHY,
            message="Redis connection OK",
            latency_ms=latency,
            details={
                "redis_version": info.get("redis_version"),
                "uptime_seconds": info.get("uptime_in_seconds"),
            },
        )
    except ImportError:
        return ComponentHealth(
            name="redis",
            status=HealthStatus.UNKNOWN,
            message="Redis client not installed",
        )
    except Exception as e:
        return ComponentHealth(
            name="redis",
            status=HealthStatus.UNHEALTHY,
            message=f"Redis connection failed: {e}",
            error=str(e),
        )


async def check_postgres(dsn: str) -> ComponentHealth:
    """
    Health check for PostgreSQL.
    
    Args:
        dsn: PostgreSQL connection string
    """
    try:
        import asyncpg
        
        start = time.time()
        conn = await asyncpg.connect(dsn, timeout=5.0)
        
        # Simple query
        result = await conn.fetchval("SELECT 1")
        version = await conn.fetchval("SELECT version()")
        latency = (time.time() - start) * 1000
        
        await conn.close()
        
        return ComponentHealth(
            name="postgres",
            status=HealthStatus.HEALTHY if result == 1 else HealthStatus.UNHEALTHY,
            message="PostgreSQL connection OK",
            latency_ms=latency,
            details={
                "version": version[:50] if version else None,
            },
        )
    except ImportError:
        return ComponentHealth(
            name="postgres",
            status=HealthStatus.UNKNOWN,
            message="asyncpg not installed",
        )
    except Exception as e:
        return ComponentHealth(
            name="postgres",
            status=HealthStatus.UNHEALTHY,
            message=f"PostgreSQL connection failed: {e}",
            error=str(e),
        )


async def check_provider(
    name: str,
    check_func: Callable[[], Awaitable[bool]],
    timeout: float = 5.0,
) -> ComponentHealth:
    """
    Generic provider health check.
    
    Args:
        name: Provider name
        check_func: Async function that returns True if healthy
        timeout: Check timeout in seconds
    """
    try:
        start = time.time()
        result = await asyncio.wait_for(check_func(), timeout=timeout)
        latency = (time.time() - start) * 1000
        
        return ComponentHealth(
            name=name,
            status=HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY,
            message=f"{name} is {'available' if result else 'unavailable'}",
            latency_ms=latency,
        )
    except asyncio.TimeoutError:
        return ComponentHealth(
            name=name,
            status=HealthStatus.UNHEALTHY,
            message=f"{name} health check timed out",
            error=f"Timeout after {timeout}s",
        )
    except Exception as e:
        return ComponentHealth(
            name=name,
            status=HealthStatus.UNHEALTHY,
            message=f"{name} check failed: {e}",
            error=str(e),
        )


# Global health check instance
_global_health: Optional[HealthCheck] = None


def get_health_checker() -> HealthCheck:
    """Get or create the global health checker."""
    global _global_health
    if _global_health is None:
        _global_health = HealthCheck()
    return _global_health
