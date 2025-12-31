"""
Sunona Voice AI - Health Check API

Kubernetes-ready health endpoints for production deployment.
"""

import os
import asyncio
import logging
import psutil
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from fastapi import APIRouter, Response, status

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])


@dataclass
class HealthStatus:
    """Health status tracker."""
    is_healthy: bool = True
    is_ready: bool = False
    startup_time: datetime = field(default_factory=datetime.now)
    last_check: Optional[datetime] = None
    
    # Component status
    components: Dict[str, bool] = field(default_factory=dict)
    
    # Metrics
    total_requests: int = 0
    failed_requests: int = 0
    active_calls: int = 0
    
    def update(self):
        self.last_check = datetime.now()


# Global health instance
_health = HealthStatus()


def set_ready():
    """Mark service as ready."""
    _health.is_ready = True
    logger.info("Service marked as ready")


def set_not_ready():
    """Mark service as not ready."""
    _health.is_ready = False


def set_unhealthy(reason: str = ""):
    """Mark service as unhealthy."""
    _health.is_healthy = False
    logger.error(f"Service marked unhealthy: {reason}")


def set_healthy():
    """Mark service as healthy."""
    _health.is_healthy = True


def register_component(name: str, healthy: bool = True):
    """Register a component health status."""
    _health.components[name] = healthy


def increment_requests(failed: bool = False):
    """Track request metrics."""
    _health.total_requests += 1
    if failed:
        _health.failed_requests += 1


def set_active_calls(count: int):
    """Update active call count."""
    _health.active_calls = count


# ==================== Endpoints ====================

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check.
    
    Returns 200 if service is alive.
    Used by load balancers for basic availability.
    """
    _health.update()
    
    return {
        "status": "healthy" if _health.is_healthy else "unhealthy",
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/health/live")
async def liveness_probe(response: Response) -> Dict[str, Any]:
    """
    Kubernetes liveness probe.
    
    Returns:
        - 200: Service is alive (should not restart)
        - 503: Service is dead (should restart)
    """
    _health.update()
    
    is_alive = _health.is_healthy
    
    if not is_alive:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return {
        "alive": is_alive,
        "uptime_seconds": (datetime.now() - _health.startup_time).total_seconds(),
    }


@router.get("/health/ready")
async def readiness_probe(response: Response) -> Dict[str, Any]:
    """
    Kubernetes readiness probe.
    
    Returns:
        - 200: Ready to receive traffic
        - 503: Not ready (exclude from load balancer)
    """
    _health.update()
    
    is_ready = _health.is_ready and _health.is_healthy
    
    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return {
        "ready": is_ready,
        "components": _health.components,
    }


@router.get("/health/startup")
async def startup_probe(response: Response) -> Dict[str, Any]:
    """
    Kubernetes startup probe.
    
    Allows slow startup without being killed.
    """
    _health.update()
    
    # Give 60 seconds for startup
    startup_grace = timedelta(seconds=60)
    startup_complete = (datetime.now() - _health.startup_time) > startup_grace or _health.is_ready
    
    if not startup_complete:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return {
        "started": startup_complete,
        "startup_time": _health.startup_time.isoformat(),
    }


@router.get("/health/detailed")
async def detailed_health() -> Dict[str, Any]:
    """
    Detailed health check with metrics.
    
    For monitoring dashboards and alerting.
    """
    _health.update()
    
    # Get system metrics
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Calculate error rate
    error_rate = 0.0
    if _health.total_requests > 0:
        error_rate = (_health.failed_requests / _health.total_requests) * 100
    
    return {
        "status": "healthy" if _health.is_healthy else "unhealthy",
        "ready": _health.is_ready,
        "uptime_seconds": (datetime.now() - _health.startup_time).total_seconds(),
        
        "components": _health.components,
        
        "metrics": {
            "total_requests": _health.total_requests,
            "failed_requests": _health.failed_requests,
            "error_rate_percent": round(error_rate, 2),
            "active_calls": _health.active_calls,
        },
        
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_mb": memory.available / (1024 * 1024),
            "disk_percent": disk.percent,
        },
        
        "environment": {
            "python_version": os.sys.version.split()[0],
            "hostname": os.environ.get("HOSTNAME", "unknown"),
            "pod_name": os.environ.get("POD_NAME", "unknown"),
        },
        
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/metrics")
async def prometheus_metrics() -> Response:
    """
    Prometheus-compatible metrics endpoint.
    
    Format: metric_name{labels} value
    """
    _health.update()
    
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    uptime = (datetime.now() - _health.startup_time).total_seconds()
    
    metrics = f"""# HELP sunona_up Service health status
# TYPE sunona_up gauge
sunona_up {1 if _health.is_healthy else 0}

# HELP sunona_ready Service readiness status
# TYPE sunona_ready gauge
sunona_ready {1 if _health.is_ready else 0}

# HELP sunona_uptime_seconds Service uptime in seconds
# TYPE sunona_uptime_seconds counter
sunona_uptime_seconds {uptime:.2f}

# HELP sunona_requests_total Total requests processed
# TYPE sunona_requests_total counter
sunona_requests_total {_health.total_requests}

# HELP sunona_requests_failed_total Failed requests
# TYPE sunona_requests_failed_total counter
sunona_requests_failed_total {_health.failed_requests}

# HELP sunona_active_calls Current active calls
# TYPE sunona_active_calls gauge
sunona_active_calls {_health.active_calls}

# HELP sunona_cpu_percent CPU usage percentage
# TYPE sunona_cpu_percent gauge
sunona_cpu_percent {cpu_percent}

# HELP sunona_memory_percent Memory usage percentage
# TYPE sunona_memory_percent gauge
sunona_memory_percent {memory.percent}
"""
    
    return Response(
        content=metrics,
        media_type="text/plain; charset=utf-8",
    )
