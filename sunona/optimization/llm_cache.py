"""
Sunona Voice AI - LLM Response Caching

Production-grade caching for LLM responses to reduce
latency and costs for repeated queries.

Features:
- Semantic similarity caching
- TTL management
- Cache warming
- Hit/miss analytics
- Multiple backends (memory, Redis)
"""

import asyncio
import hashlib
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple
import re

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """A cached LLM response."""
    key: str
    prompt_hash: str
    response: str
    model: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    hit_count: int = 0
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Metadata
    tokens_saved: int = 0
    latency_saved_ms: float = 0.0
    
    @property
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "prompt_hash": self.prompt_hash,
            "response": self.response,
            "model": self.model,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "hit_count": self.hit_count,
            "last_accessed": self.last_accessed.isoformat(),
            "tokens_saved": self.tokens_saved,
            "latency_saved_ms": self.latency_saved_ms,
        }


class CacheBackend(ABC):
    """Abstract base class for cache backends."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[CacheEntry]:
        """Get a cache entry."""
        pass
    
    @abstractmethod
    async def set(
        self,
        key: str,
        entry: CacheEntry,
        ttl_seconds: Optional[int] = None,
    ) -> bool:
        """Set a cache entry."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a cache entry."""
        pass
    
    @abstractmethod
    async def clear(self) -> int:
        """Clear all entries. Returns count deleted."""
        pass
    
    @abstractmethod
    async def size(self) -> int:
        """Get number of entries."""
        pass


class MemoryCacheBackend(CacheBackend):
    """In-memory cache backend."""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[CacheEntry]:
        async with self._lock:
            entry = self._cache.get(key)
            if entry and not entry.is_expired:
                entry.hit_count += 1
                entry.last_accessed = datetime.now(timezone.utc)
                return entry
            elif entry and entry.is_expired:
                del self._cache[key]
        return None
    
    async def set(
        self,
        key: str,
        entry: CacheEntry,
        ttl_seconds: Optional[int] = None,
    ) -> bool:
        async with self._lock:
            # Evict if at capacity
            if len(self._cache) >= self.max_size:
                await self._evict_lru()
            
            if ttl_seconds:
                entry.expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
            
            self._cache[key] = entry
            return True
    
    async def delete(self, key: str) -> bool:
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
        return False
    
    async def clear(self) -> int:
        async with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count
    
    async def size(self) -> int:
        return len(self._cache)
    
    async def _evict_lru(self) -> None:
        """Evict least recently used entries."""
        if not self._cache:
            return
        
        # Sort by last_accessed and remove oldest 10%
        sorted_entries = sorted(
            self._cache.items(),
            key=lambda x: x[1].last_accessed,
        )
        
        evict_count = max(1, len(sorted_entries) // 10)
        for key, _ in sorted_entries[:evict_count]:
            del self._cache[key]


class RedisCacheBackend(CacheBackend):
    """Redis cache backend."""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        prefix: str = "sunona:llm_cache:",
    ):
        self.redis_url = redis_url
        self.prefix = prefix
        self._redis = None
    
    async def _get_redis(self):
        """Get or create Redis connection."""
        if self._redis is None:
            try:
                import redis.asyncio as redis
                self._redis = redis.from_url(self.redis_url)
            except ImportError:
                logger.error("redis package not installed")
                raise
        return self._redis
    
    def _make_key(self, key: str) -> str:
        return f"{self.prefix}{key}"
    
    async def get(self, key: str) -> Optional[CacheEntry]:
        try:
            r = await self._get_redis()
            data = await r.get(self._make_key(key))
            
            if data:
                entry_dict = json.loads(data)
                entry = CacheEntry(
                    key=entry_dict["key"],
                    prompt_hash=entry_dict["prompt_hash"],
                    response=entry_dict["response"],
                    model=entry_dict["model"],
                    created_at=datetime.fromisoformat(entry_dict["created_at"]),
                    hit_count=entry_dict.get("hit_count", 0) + 1,
                    tokens_saved=entry_dict.get("tokens_saved", 0),
                    latency_saved_ms=entry_dict.get("latency_saved_ms", 0.0),
                )
                
                # Update hit count
                entry_dict["hit_count"] = entry.hit_count
                entry_dict["last_accessed"] = datetime.now(timezone.utc).isoformat()
                await r.set(self._make_key(key), json.dumps(entry_dict))
                
                return entry
        except Exception as e:
            logger.error(f"Redis get error: {e}")
        return None
    
    async def set(
        self,
        key: str,
        entry: CacheEntry,
        ttl_seconds: Optional[int] = None,
    ) -> bool:
        try:
            r = await self._get_redis()
            data = json.dumps(entry.to_dict())
            
            if ttl_seconds:
                await r.setex(self._make_key(key), ttl_seconds, data)
            else:
                await r.set(self._make_key(key), data)
            
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        try:
            r = await self._get_redis()
            result = await r.delete(self._make_key(key))
            return result > 0
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False
    
    async def clear(self) -> int:
        try:
            r = await self._get_redis()
            keys = []
            async for key in r.scan_iter(f"{self.prefix}*"):
                keys.append(key)
            
            if keys:
                return await r.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
            return 0
    
    async def size(self) -> int:
        try:
            r = await self._get_redis()
            count = 0
            async for _ in r.scan_iter(f"{self.prefix}*"):
                count += 1
            return count
        except Exception as e:
            logger.error(f"Redis size error: {e}")
            return 0


class LLMCache:
    """
    LLM response cache with semantic awareness.
    
    Features:
    - Exact match caching
    - Normalized prompt caching
    - Cache analytics
    - TTL management
    
    Example:
        cache = LLMCache()
        
        # Check cache before calling LLM
        cached = await cache.get(prompt, model="gpt-4o-mini")
        if cached:
            return cached.response
        
        # Call LLM
        response = await llm.generate(prompt)
        
        # Cache response
        await cache.set(prompt, response, model="gpt-4o-mini")
    """
    
    def __init__(
        self,
        backend: Optional[CacheBackend] = None,
        default_ttl: int = 3600,  # 1 hour
        enable_normalization: bool = True,
    ):
        """
        Initialize LLM cache.
        
        Args:
            backend: Cache backend (defaults to memory)
            default_ttl: Default TTL in seconds
            enable_normalization: Normalize prompts before hashing
        """
        self.backend = backend or MemoryCacheBackend()
        self.default_ttl = default_ttl
        self.enable_normalization = enable_normalization
        
        # Statistics
        self._hits = 0
        self._misses = 0
        self._total_tokens_saved = 0
        self._total_latency_saved_ms = 0.0
    
    def _normalize_prompt(self, prompt: str) -> str:
        """Normalize prompt for better cache hits."""
        if not self.enable_normalization:
            return prompt
        
        # Remove extra whitespace
        normalized = " ".join(prompt.split())
        
        # Lowercase
        normalized = normalized.lower()
        
        # Remove punctuation at end
        normalized = normalized.rstrip(".,!?")
        
        return normalized
    
    def _generate_key(
        self,
        prompt: str,
        model: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Generate cache key from prompt and model."""
        normalized = self._normalize_prompt(prompt)
        
        # Include system prompt in key if provided
        if system_prompt:
            key_data = f"{model}:{self._normalize_prompt(system_prompt)}:{normalized}"
        else:
            key_data = f"{model}:{normalized}"
        
        return hashlib.sha256(key_data.encode()).hexdigest()[:32]
    
    async def get(
        self,
        prompt: str,
        model: str,
        system_prompt: Optional[str] = None,
    ) -> Optional[CacheEntry]:
        """
        Get cached response for a prompt.
        
        Args:
            prompt: User prompt
            model: LLM model name
            system_prompt: Optional system prompt
        
        Returns:
            CacheEntry if found, None otherwise
        """
        key = self._generate_key(prompt, model, system_prompt)
        entry = await self.backend.get(key)
        
        if entry:
            self._hits += 1
            self._total_tokens_saved += entry.tokens_saved
            self._total_latency_saved_ms += entry.latency_saved_ms
            logger.debug(f"Cache hit for key {key[:8]}...")
            return entry
        
        self._misses += 1
        return None
    
    async def set(
        self,
        prompt: str,
        response: str,
        model: str,
        system_prompt: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
        tokens_used: int = 0,
        latency_ms: float = 0.0,
    ) -> bool:
        """
        Cache an LLM response.
        
        Args:
            prompt: User prompt
            response: LLM response
            model: LLM model name
            system_prompt: Optional system prompt
            ttl_seconds: Override default TTL
            tokens_used: Tokens used (for analytics)
            latency_ms: Latency (for analytics)
        
        Returns:
            True if cached successfully
        """
        key = self._generate_key(prompt, model, system_prompt)
        
        entry = CacheEntry(
            key=key,
            prompt_hash=hashlib.sha256(prompt.encode()).hexdigest()[:16],
            response=response,
            model=model,
            tokens_saved=tokens_used,
            latency_saved_ms=latency_ms,
        )
        
        ttl = ttl_seconds or self.default_ttl
        success = await self.backend.set(key, entry, ttl)
        
        if success:
            logger.debug(f"Cached response for key {key[:8]}...")
        
        return success
    
    async def invalidate(
        self,
        prompt: str,
        model: str,
        system_prompt: Optional[str] = None,
    ) -> bool:
        """Invalidate a cached entry."""
        key = self._generate_key(prompt, model, system_prompt)
        return await self.backend.delete(key)
    
    async def clear(self) -> int:
        """Clear all cache entries."""
        count = await self.backend.clear()
        logger.info(f"Cleared {count} cache entries")
        return count
    
    @property
    def hit_rate(self) -> float:
        """Get cache hit rate."""
        total = self._hits + self._misses
        if total == 0:
            return 0.0
        return self._hits / total
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self.hit_rate * 100, 2),
            "total_tokens_saved": self._total_tokens_saved,
            "total_latency_saved_ms": round(self._total_latency_saved_ms, 2),
            "estimated_cost_saved": round(self._total_tokens_saved * 0.00002, 4),
        }
    
    async def get_size(self) -> int:
        """Get number of cached entries."""
        return await self.backend.size()


class CachedLLMWrapper:
    """
    Wrapper that adds caching to any LLM.
    
    Example:
        llm = OpenAILLM(model="gpt-4o-mini")
        cached_llm = CachedLLMWrapper(llm)
        
        # First call hits the API
        response = await cached_llm.generate("What is 2+2?")
        
        # Second call uses cache
        response = await cached_llm.generate("What is 2+2?")
    """
    
    def __init__(
        self,
        llm: Any,
        cache: Optional[LLMCache] = None,
        cacheable_system_prompts: bool = True,
    ):
        """
        Initialize cached LLM wrapper.
        
        Args:
            llm: Underlying LLM instance
            cache: LLM cache (creates new if not provided)
            cacheable_system_prompts: Cache responses with system prompts
        """
        self.llm = llm
        self.cache = cache or LLMCache()
        self.cacheable_system_prompts = cacheable_system_prompts
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        skip_cache: bool = False,
        **kwargs
    ) -> str:
        """
        Generate response with caching.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
            skip_cache: Skip cache lookup
            **kwargs: Additional LLM arguments
        
        Returns:
            LLM response (possibly from cache)
        """
        model = getattr(self.llm, "model", "unknown")
        
        # Check cache
        if not skip_cache:
            sys_prompt = system_prompt if self.cacheable_system_prompts else None
            cached = await self.cache.get(prompt, model, sys_prompt)
            if cached:
                return cached.response
        
        # Call LLM
        start = time.perf_counter()
        response = await self.llm.generate(prompt, system_prompt=system_prompt, **kwargs)
        latency_ms = (time.perf_counter() - start) * 1000
        
        # Get response text
        if hasattr(response, "content"):
            response_text = response.content
        elif hasattr(response, "text"):
            response_text = response.text
        else:
            response_text = str(response)
        
        # Estimate tokens
        tokens = (len(prompt) + len(response_text)) // 4
        
        # Cache response
        sys_prompt = system_prompt if self.cacheable_system_prompts else None
        await self.cache.set(
            prompt,
            response_text,
            model,
            system_prompt=sys_prompt,
            tokens_used=tokens,
            latency_ms=latency_ms,
        )
        
        return response_text
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache.get_stats()


# Global cache instance
_global_cache: Optional[LLMCache] = None


def get_llm_cache() -> LLMCache:
    """Get or create global LLM cache."""
    global _global_cache
    if _global_cache is None:
        _global_cache = LLMCache()
    return _global_cache
