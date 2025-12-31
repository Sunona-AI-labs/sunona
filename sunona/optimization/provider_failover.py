"""
Sunona Voice AI - Provider Failover

Automatic failover between providers for high availability.
Ensures service continuity when a provider fails.

Features:
- Automatic failover on errors
- Health-based routing
- Weighted provider selection
- Cost-aware fallback
- Recovery detection
"""

import asyncio
import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Awaitable, TypeVar

from sunona.core.circuit_breaker import CircuitBreaker, CircuitState

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ProviderHealth(Enum):
    """Provider health states."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ProviderStatus:
    """Status of a single provider."""
    name: str
    health: ProviderHealth = ProviderHealth.UNKNOWN
    
    # Metrics
    success_count: int = 0
    failure_count: int = 0
    total_latency_ms: float = 0.0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    last_error: Optional[str] = None
    
    # Circuit breaker
    circuit_state: CircuitState = CircuitState.CLOSED
    
    # Cost
    cost_per_unit: float = 0.0
    
    # Priority (lower = higher priority)
    priority: int = 0
    weight: float = 1.0
    
    # Times
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total = self.success_count + self.failure_count
        if total == 0:
            return 1.0
        return self.success_count / total
    
    @property
    def avg_latency_ms(self) -> float:
        """Calculate average latency."""
        if self.success_count == 0:
            return 0.0
        return self.total_latency_ms / self.success_count
    
    def record_success(self, latency_ms: float) -> None:
        """Record a successful call."""
        self.success_count += 1
        self.total_latency_ms += latency_ms
        self.last_success = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        
        # Update health
        if self.success_rate >= 0.95:
            self.health = ProviderHealth.HEALTHY
        elif self.success_rate >= 0.80:
            self.health = ProviderHealth.DEGRADED
    
    def record_failure(self, error: str) -> None:
        """Record a failed call."""
        self.failure_count += 1
        self.last_failure = datetime.now(timezone.utc)
        self.last_error = error
        self.updated_at = datetime.now(timezone.utc)
        
        # Update health
        if self.success_rate < 0.50:
            self.health = ProviderHealth.UNHEALTHY
        elif self.success_rate < 0.80:
            self.health = ProviderHealth.DEGRADED
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "health": self.health.value,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": round(self.success_rate * 100, 2),
            "avg_latency_ms": round(self.avg_latency_ms, 2),
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "last_failure": self.last_failure.isoformat() if self.last_failure else None,
            "last_error": self.last_error,
            "circuit_state": self.circuit_state.value,
            "priority": self.priority,
            "weight": self.weight,
        }


class FailoverStrategy(Enum):
    """Failover selection strategies."""
    PRIORITY = "priority"      # Use provider with highest priority
    ROUND_ROBIN = "round_robin"  # Cycle through providers
    WEIGHTED = "weighted"      # Weighted random selection
    LEAST_LATENCY = "least_latency"  # Use fastest provider
    LEAST_COST = "least_cost"  # Use cheapest provider
    RANDOM = "random"          # Random selection


@dataclass
class FailoverConfig:
    """Configuration for failover behavior."""
    strategy: FailoverStrategy = FailoverStrategy.PRIORITY
    max_retries: int = 3
    retry_delay_ms: float = 100
    timeout_ms: float = 30000
    
    # Health thresholds
    health_check_interval_seconds: int = 60
    unhealthy_threshold: int = 3  # Consecutive failures
    healthy_threshold: int = 2    # Consecutive successes to recover
    
    # Exclude unhealthy
    exclude_unhealthy: bool = True


class ProviderFailover:
    """
    Provider failover manager.
    
    Automatically routes requests to healthy providers and
    handles failures gracefully.
    
    Example:
        failover = ProviderFailover()
        
        # Register providers
        failover.register_provider("deepgram", deepgram_transcribe, priority=1)
        failover.register_provider("whisper", whisper_transcribe, priority=2)
        failover.register_provider("azure", azure_transcribe, priority=3)
        
        # Execute with failover
        result = await failover.execute(audio_data)
        
        # If deepgram fails, automatically tries whisper, then azure
    """
    
    def __init__(
        self,
        config: Optional[FailoverConfig] = None,
    ):
        """
        Initialize failover manager.
        
        Args:
            config: Failover configuration
        """
        self.config = config or FailoverConfig()
        
        self._providers: Dict[str, ProviderStatus] = {}
        self._handlers: Dict[str, Callable[..., Awaitable[Any]]] = {}
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        self._round_robin_index = 0
        self._lock = asyncio.Lock()
    
    def register_provider(
        self,
        name: str,
        handler: Callable[..., Awaitable[Any]],
        priority: int = 0,
        weight: float = 1.0,
        cost_per_unit: float = 0.0,
    ) -> None:
        """
        Register a provider.
        
        Args:
            name: Provider name
            handler: Async function to call
            priority: Lower = higher priority
            weight: Weight for weighted selection
            cost_per_unit: Cost per unit (for cost-aware routing)
        """
        self._providers[name] = ProviderStatus(
            name=name,
            priority=priority,
            weight=weight,
            cost_per_unit=cost_per_unit,
            health=ProviderHealth.HEALTHY,
        )
        
        self._handlers[name] = handler
        
        # Create circuit breaker
        self._circuit_breakers[name] = CircuitBreaker(
            name=f"provider_{name}",
            failure_threshold=self.config.unhealthy_threshold,
            success_threshold=self.config.healthy_threshold,
            timeout=self.config.timeout_ms / 1000,
        )
        
        logger.info(f"Registered provider: {name} (priority={priority})")
    
    def unregister_provider(self, name: str) -> bool:
        """Remove a provider."""
        if name in self._providers:
            del self._providers[name]
            del self._handlers[name]
            del self._circuit_breakers[name]
            return True
        return False
    
    def _select_providers(self) -> List[str]:
        """Select providers based on strategy."""
        available = []
        
        for name, status in self._providers.items():
            # Skip unhealthy if configured
            if self.config.exclude_unhealthy:
                if status.health == ProviderHealth.UNHEALTHY:
                    continue
                # Also check circuit breaker
                cb = self._circuit_breakers.get(name)
                if cb and cb.state == CircuitState.OPEN:
                    continue
            
            available.append((name, status))
        
        if not available:
            # Fallback to all providers
            available = list(self._providers.items())
        
        # Sort based on strategy
        if self.config.strategy == FailoverStrategy.PRIORITY:
            available.sort(key=lambda x: x[1].priority)
        
        elif self.config.strategy == FailoverStrategy.LEAST_LATENCY:
            available.sort(key=lambda x: x[1].avg_latency_ms or float('inf'))
        
        elif self.config.strategy == FailoverStrategy.LEAST_COST:
            available.sort(key=lambda x: x[1].cost_per_unit)
        
        elif self.config.strategy == FailoverStrategy.ROUND_ROBIN:
            # Rotate list based on index
            self._round_robin_index = (self._round_robin_index + 1) % len(available)
            available = available[self._round_robin_index:] + available[:self._round_robin_index]
        
        elif self.config.strategy == FailoverStrategy.WEIGHTED:
            # Weighted random shuffle
            total_weight = sum(s.weight for _, s in available)
            if total_weight > 0:
                # Sort by weighted random
                available.sort(
                    key=lambda x: random.random() * (x[1].weight / total_weight),
                    reverse=True,
                )
        
        elif self.config.strategy == FailoverStrategy.RANDOM:
            random.shuffle(available)
        
        return [name for name, _ in available]
    
    async def execute(
        self,
        *args,
        preferred_provider: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Execute with automatic failover.
        
        Args:
            *args: Arguments to pass to handler
            preferred_provider: Override provider selection
            **kwargs: Keyword arguments to pass to handler
        
        Returns:
            Result from successful provider
        
        Raises:
            Exception: If all providers fail
        """
        if not self._providers:
            raise RuntimeError("No providers registered")
        
        # Get provider order
        if preferred_provider and preferred_provider in self._providers:
            providers = [preferred_provider] + [
                p for p in self._select_providers()
                if p != preferred_provider
            ]
        else:
            providers = self._select_providers()
        
        last_error = None
        
        for attempt, provider_name in enumerate(providers):
            if attempt >= self.config.max_retries:
                break
            
            handler = self._handlers.get(provider_name)
            status = self._providers.get(provider_name)
            cb = self._circuit_breakers.get(provider_name)
            
            if not handler or not status:
                continue
            
            try:
                start_time = time.perf_counter()
                
                # Use circuit breaker
                if cb:
                    result = await cb.execute(handler, *args, **kwargs)
                    status.circuit_state = cb.state
                else:
                    result = await asyncio.wait_for(
                        handler(*args, **kwargs),
                        timeout=self.config.timeout_ms / 1000,
                    )
                
                latency_ms = (time.perf_counter() - start_time) * 1000
                status.record_success(latency_ms)
                
                logger.debug(
                    f"Provider {provider_name} succeeded in {latency_ms:.1f}ms"
                )
                
                return result
                
            except Exception as e:
                error_str = str(e)
                status.record_failure(error_str)
                
                if cb:
                    status.circuit_state = cb.state
                
                last_error = e
                logger.warning(
                    f"Provider {provider_name} failed: {error_str}"
                )
                
                # Delay before retry
                if attempt < len(providers) - 1:
                    await asyncio.sleep(self.config.retry_delay_ms / 1000)
        
        # All providers failed
        raise RuntimeError(
            f"All {len(providers)} providers failed. Last error: {last_error}"
        )
    
    async def execute_parallel(
        self,
        *args,
        return_first: bool = True,
        **kwargs
    ) -> Any:
        """
        Execute on multiple providers in parallel.
        
        Args:
            *args: Arguments to pass to handlers
            return_first: Return first successful result
            **kwargs: Keyword arguments to pass to handlers
        
        Returns:
            First successful result or list of all results
        """
        providers = self._select_providers()
        
        if return_first:
            # Race - return first to complete
            tasks = []
            for provider_name in providers:
                handler = self._handlers.get(provider_name)
                if handler:
                    tasks.append(handler(*args, **kwargs))
            
            if not tasks:
                raise RuntimeError("No providers available")
            
            done, pending = await asyncio.wait(
                tasks,
                return_when=asyncio.FIRST_COMPLETED,
            )
            
            # Cancel pending
            for task in pending:
                task.cancel()
            
            # Return first result
            for task in done:
                try:
                    return task.result()
                except Exception:
                    pass
            
            raise RuntimeError("All parallel executions failed")
        else:
            # Wait for all
            tasks = []
            for provider_name in providers:
                handler = self._handlers.get(provider_name)
                if handler:
                    tasks.append(handler(*args, **kwargs))
            
            return await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_provider_status(self, name: str) -> Optional[ProviderStatus]:
        """Get status of a provider."""
        return self._providers.get(name)
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers."""
        return {
            name: status.to_dict()
            for name, status in self._providers.items()
        }
    
    def get_healthy_providers(self) -> List[str]:
        """Get list of healthy providers."""
        return [
            name for name, status in self._providers.items()
            if status.health == ProviderHealth.HEALTHY
        ]
    
    async def health_check(self, name: str) -> ProviderHealth:
        """
        Perform health check on a provider.
        
        Subclass and override for custom health checks.
        """
        status = self._providers.get(name)
        if not status:
            return ProviderHealth.UNKNOWN
        
        return status.health
    
    async def force_healthy(self, name: str) -> bool:
        """Force a provider to healthy state."""
        status = self._providers.get(name)
        if not status:
            return False
        
        status.health = ProviderHealth.HEALTHY
        status.failure_count = 0
        
        cb = self._circuit_breakers.get(name)
        if cb:
            cb.reset()
            status.circuit_state = cb.state
        
        logger.info(f"Forced provider {name} to healthy")
        return True
    
    async def force_unhealthy(self, name: str) -> bool:
        """Force a provider to unhealthy state."""
        status = self._providers.get(name)
        if not status:
            return False
        
        status.health = ProviderHealth.UNHEALTHY
        logger.info(f"Forced provider {name} to unhealthy")
        return True


class ProviderPool:
    """
    Pool of provider failover managers by type.
    
    Manages separate failover pools for STT, TTS, LLM, etc.
    """
    
    def __init__(self):
        self._pools: Dict[str, ProviderFailover] = {}
    
    def get_or_create(
        self,
        pool_type: str,
        config: Optional[FailoverConfig] = None,
    ) -> ProviderFailover:
        """Get or create a failover pool."""
        if pool_type not in self._pools:
            self._pools[pool_type] = ProviderFailover(config)
        return self._pools[pool_type]
    
    def get(self, pool_type: str) -> Optional[ProviderFailover]:
        """Get a failover pool if it exists."""
        return self._pools.get(pool_type)
    
    def list_pools(self) -> List[str]:
        """List all pool types."""
        return list(self._pools.keys())
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all pools and their providers."""
        return {
            pool_type: failover.get_all_status()
            for pool_type, failover in self._pools.items()
        }


# Global provider pool
_global_pool: Optional[ProviderPool] = None


def get_provider_pool() -> ProviderPool:
    """Get or create global provider pool."""
    global _global_pool
    if _global_pool is None:
        _global_pool = ProviderPool()
    return _global_pool
