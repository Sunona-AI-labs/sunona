"""
Sunona Voice AI - Optimization Package

Performance optimization modules for scale.
"""

from sunona.optimization.llm_cache import (
    LLMCache,
    CacheEntry,
    CacheBackend,
    MemoryCacheBackend,
    RedisCacheBackend,
    CachedLLMWrapper,
    get_llm_cache,
)

from sunona.optimization.provider_failover import (
    ProviderFailover,
    ProviderStatus,
    ProviderHealth,
    FailoverStrategy,
    FailoverConfig,
    ProviderPool,
    get_provider_pool,
)

__all__ = [
    # LLM Caching
    "LLMCache",
    "CacheEntry",
    "CacheBackend",
    "MemoryCacheBackend",
    "RedisCacheBackend",
    "CachedLLMWrapper",
    "get_llm_cache",
    # Provider Failover
    "ProviderFailover",
    "ProviderStatus",
    "ProviderHealth",
    "FailoverStrategy",
    "FailoverConfig",
    "ProviderPool",
    "get_provider_pool",
]
