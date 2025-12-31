"""
Sunona Voice AI - Rate Limiting

Production-grade rate limiting implementations for API protection.
Supports multiple algorithms and distributed environments.

Algorithms:
- Sliding Window Counter
- Token Bucket
- Fixed Window (simple)

Features:
- In-memory and Redis-backed
- Per-user, per-IP, per-endpoint limiting
- Configurable limits and windows
- Rate limit headers
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from sunona.core.exceptions import RateLimitError

logger = logging.getLogger(__name__)


@dataclass
class RateLimitResult:
    """
    Result of a rate limit check.
    
    Attributes:
        allowed: Whether the request is allowed
        limit: Total limit for the window
        remaining: Remaining requests in window
        reset_at: When the window resets (Unix timestamp)
        retry_after: Seconds until next allowed request
    """
    allowed: bool
    limit: int
    remaining: int
    reset_at: float
    retry_after: Optional[int] = None
    
    def to_headers(self) -> Dict[str, str]:
        """Convert to rate limit headers."""
        headers = {
            "X-RateLimit-Limit": str(self.limit),
            "X-RateLimit-Remaining": str(max(0, self.remaining)),
            "X-RateLimit-Reset": str(int(self.reset_at)),
        }
        
        if self.retry_after:
            headers["Retry-After"] = str(self.retry_after)
        
        return headers


@dataclass
class RateLimitConfig:
    """
    Rate limit configuration.
    
    Attributes:
        limit: Maximum requests allowed
        window_seconds: Time window in seconds
        burst_limit: Optional burst allowance
        key_prefix: Prefix for rate limit keys
    """
    limit: int = 60
    window_seconds: int = 60
    burst_limit: Optional[int] = None
    key_prefix: str = "ratelimit"


class RateLimiter(ABC):
    """Abstract base class for rate limiters."""
    
    @abstractmethod
    async def check(self, key: str) -> RateLimitResult:
        """
        Check if a request is allowed.
        
        Args:
            key: Unique identifier (user_id, IP, etc.)
        
        Returns:
            RateLimitResult with allow/deny decision
        """
        pass
    
    @abstractmethod
    async def reset(self, key: str) -> None:
        """Reset rate limit for a key."""
        pass
    
    async def check_or_raise(self, key: str) -> RateLimitResult:
        """
        Check rate limit and raise if exceeded.
        
        Raises:
            RateLimitError if limit exceeded
        """
        result = await self.check(key)
        
        if not result.allowed:
            raise RateLimitError(
                message=f"Rate limit exceeded for {key}",
                retry_after=result.retry_after or 60,
                limit=result.limit,
                window=int(result.reset_at - time.time()),
            )
        
        return result


class SlidingWindowRateLimiter(RateLimiter):
    """
    Sliding window counter rate limiter.
    
    More accurate than fixed window, smoother distribution.
    Uses two windows to approximate a true sliding window.
    
    Example:
        limiter = SlidingWindowRateLimiter(limit=100, window_seconds=60)
        
        result = await limiter.check("user_123")
        if result.allowed:
            # Process request
            pass
        else:
            # Rate limited
            raise RateLimitError(retry_after=result.retry_after)
    """
    
    def __init__(
        self,
        limit: int = 60,
        window_seconds: int = 60,
        config: Optional[RateLimitConfig] = None,
    ):
        """
        Initialize sliding window limiter.
        
        Args:
            limit: Maximum requests per window
            window_seconds: Window size in seconds
            config: Full configuration (overrides individual params)
        """
        if config:
            self.limit = config.limit
            self.window = config.window_seconds
        else:
            self.limit = limit
            self.window = window_seconds
        
        # Store counts per key: {key: {window_start: count}}
        self._counts: Dict[str, Dict[int, int]] = defaultdict(dict)
        self._lock = asyncio.Lock()
    
    async def check(self, key: str) -> RateLimitResult:
        """Check if request is allowed using sliding window."""
        async with self._lock:
            now = time.time()
            current_window = int(now // self.window)
            previous_window = current_window - 1
            
            # Get position in current window (0.0 to 1.0)
            window_position = (now % self.window) / self.window
            
            # Get counts
            current_count = self._counts[key].get(current_window, 0)
            previous_count = self._counts[key].get(previous_window, 0)
            
            # Calculate weighted count (sliding window approximation)
            weighted_count = (
                previous_count * (1 - window_position) + current_count
            )
            
            # Check if allowed
            allowed = weighted_count < self.limit
            remaining = max(0, self.limit - int(weighted_count) - 1)
            
            if allowed:
                # Increment current window count
                self._counts[key][current_window] = current_count + 1
                
                # Clean old windows
                old_windows = [
                    w for w in self._counts[key] 
                    if w < previous_window
                ]
                for w in old_windows:
                    del self._counts[key][w]
            
            # Calculate reset time
            reset_at = (current_window + 1) * self.window
            
            # Calculate retry_after if not allowed
            retry_after = None
            if not allowed:
                # Estimate when we'll have capacity
                excess = weighted_count - self.limit + 1
                # Time for excess requests to "expire" from sliding window
                retry_after = int(self.window * (excess / self.limit))
                retry_after = max(1, min(retry_after, self.window))
            
            return RateLimitResult(
                allowed=allowed,
                limit=self.limit,
                remaining=remaining if allowed else 0,
                reset_at=reset_at,
                retry_after=retry_after,
            )
    
    async def reset(self, key: str) -> None:
        """Reset rate limit for a key."""
        async with self._lock:
            self._counts.pop(key, None)
    
    async def get_usage(self, key: str) -> Dict[str, Any]:
        """Get current usage for a key."""
        async with self._lock:
            now = time.time()
            current_window = int(now // self.window)
            previous_window = current_window - 1
            window_position = (now % self.window) / self.window
            
            current_count = self._counts[key].get(current_window, 0)
            previous_count = self._counts[key].get(previous_window, 0)
            weighted_count = (
                previous_count * (1 - window_position) + current_count
            )
            
            return {
                "key": key,
                "current_count": current_count,
                "previous_count": previous_count,
                "weighted_count": round(weighted_count, 2),
                "limit": self.limit,
                "remaining": max(0, self.limit - int(weighted_count)),
                "window_seconds": self.window,
            }


class TokenBucketRateLimiter(RateLimiter):
    """
    Token bucket rate limiter.
    
    Allows bursts while maintaining average rate.
    Tokens are added at a constant rate up to maximum capacity.
    
    Example:
        limiter = TokenBucketRateLimiter(
            capacity=100,      # Max tokens (burst size)
            rate=10,           # Tokens added per second
        )
        
        result = await limiter.check("user_123")
    """
    
    def __init__(
        self,
        capacity: int = 100,
        rate: float = 10.0,
        initial_tokens: Optional[int] = None,
    ):
        """
        Initialize token bucket limiter.
        
        Args:
            capacity: Maximum tokens (bucket size)
            rate: Tokens added per second
            initial_tokens: Starting tokens (defaults to capacity)
        """
        self.capacity = capacity
        self.rate = rate
        self.initial_tokens = initial_tokens if initial_tokens is not None else capacity
        
        # Store bucket state: {key: (tokens, last_update)}
        self._buckets: Dict[str, Tuple[float, float]] = {}
        self._lock = asyncio.Lock()
    
    async def check(self, key: str, tokens_needed: int = 1) -> RateLimitResult:
        """
        Check if request is allowed (consume tokens).
        
        Args:
            key: Unique identifier
            tokens_needed: Tokens to consume (default: 1)
        """
        async with self._lock:
            now = time.time()
            
            # Get or create bucket
            if key in self._buckets:
                tokens, last_update = self._buckets[key]
                
                # Calculate tokens to add since last update
                elapsed = now - last_update
                tokens_to_add = elapsed * self.rate
                tokens = min(self.capacity, tokens + tokens_to_add)
            else:
                tokens = float(self.initial_tokens)
            
            # Check if enough tokens
            allowed = tokens >= tokens_needed
            
            if allowed:
                tokens -= tokens_needed
            
            # Update bucket
            self._buckets[key] = (tokens, now)
            
            # Calculate when bucket will be full (for reset_at)
            tokens_needed_for_full = self.capacity - tokens
            seconds_to_full = tokens_needed_for_full / self.rate if self.rate > 0 else 0
            reset_at = now + seconds_to_full
            
            # Calculate retry_after if not allowed
            retry_after = None
            if not allowed:
                tokens_deficit = tokens_needed - tokens
                retry_after = int(tokens_deficit / self.rate) + 1
            
            return RateLimitResult(
                allowed=allowed,
                limit=self.capacity,
                remaining=int(tokens),
                reset_at=reset_at,
                retry_after=retry_after,
            )
    
    async def reset(self, key: str) -> None:
        """Reset bucket for a key."""
        async with self._lock:
            self._buckets.pop(key, None)
    
    async def add_tokens(self, key: str, tokens: int) -> None:
        """Manually add tokens to a bucket."""
        async with self._lock:
            now = time.time()
            
            if key in self._buckets:
                current_tokens, _ = self._buckets[key]
                new_tokens = min(self.capacity, current_tokens + tokens)
            else:
                new_tokens = min(self.capacity, float(tokens))
            
            self._buckets[key] = (new_tokens, now)


class FixedWindowRateLimiter(RateLimiter):
    """
    Simple fixed window rate limiter.
    
    Fastest and simplest, but can allow 2x burst at window boundaries.
    Use SlidingWindowRateLimiter for more accuracy.
    """
    
    def __init__(
        self,
        limit: int = 60,
        window_seconds: int = 60,
    ):
        self.limit = limit
        self.window = window_seconds
        self._counts: Dict[str, Tuple[int, int]] = {}  # key: (window, count)
        self._lock = asyncio.Lock()
    
    async def check(self, key: str) -> RateLimitResult:
        """Check if request is allowed."""
        async with self._lock:
            now = time.time()
            current_window = int(now // self.window)
            
            # Get or reset count
            if key in self._counts:
                stored_window, count = self._counts[key]
                if stored_window != current_window:
                    count = 0
            else:
                count = 0
            
            # Check if allowed
            allowed = count < self.limit
            
            if allowed:
                count += 1
                self._counts[key] = (current_window, count)
            
            remaining = max(0, self.limit - count)
            reset_at = (current_window + 1) * self.window
            
            retry_after = None
            if not allowed:
                retry_after = int(reset_at - now) + 1
            
            return RateLimitResult(
                allowed=allowed,
                limit=self.limit,
                remaining=remaining,
                reset_at=reset_at,
                retry_after=retry_after,
            )
    
    async def reset(self, key: str) -> None:
        """Reset counter for a key."""
        async with self._lock:
            self._counts.pop(key, None)


class RateLimitManager:
    """
    Manager for multiple rate limit tiers.
    
    Allows different limits for different tiers (free, pro, enterprise).
    
    Example:
        manager = RateLimitManager()
        
        manager.add_tier("free", limit=60, window=60)
        manager.add_tier("pro", limit=1000, window=60)
        manager.add_tier("enterprise", limit=10000, window=60)
        
        result = await manager.check("user_123", tier="pro")
    """
    
    def __init__(self):
        self._tiers: Dict[str, RateLimiter] = {}
        self._default_tier = "default"
    
    def add_tier(
        self,
        name: str,
        limit: int,
        window: int = 60,
        limiter_type: str = "sliding_window",
    ) -> None:
        """
        Add a rate limit tier.
        
        Args:
            name: Tier name
            limit: Requests per window
            window: Window size in seconds
            limiter_type: "sliding_window", "token_bucket", or "fixed_window"
        """
        if limiter_type == "token_bucket":
            limiter = TokenBucketRateLimiter(
                capacity=limit,
                rate=limit / window,
            )
        elif limiter_type == "fixed_window":
            limiter = FixedWindowRateLimiter(limit=limit, window_seconds=window)
        else:
            limiter = SlidingWindowRateLimiter(limit=limit, window_seconds=window)
        
        self._tiers[name] = limiter
        
        if not self._default_tier or name == "default":
            self._default_tier = name
    
    def set_default_tier(self, name: str) -> None:
        """Set the default tier."""
        if name not in self._tiers:
            raise ValueError(f"Tier '{name}' not found")
        self._default_tier = name
    
    async def check(
        self,
        key: str,
        tier: Optional[str] = None,
    ) -> RateLimitResult:
        """
        Check rate limit for a key in a tier.
        
        Args:
            key: Unique identifier
            tier: Tier name (uses default if not specified)
        """
        tier_name = tier or self._default_tier
        
        if tier_name not in self._tiers:
            raise ValueError(f"Tier '{tier_name}' not found")
        
        return await self._tiers[tier_name].check(key)
    
    async def check_or_raise(
        self,
        key: str,
        tier: Optional[str] = None,
    ) -> RateLimitResult:
        """Check rate limit and raise if exceeded."""
        tier_name = tier or self._default_tier
        
        if tier_name not in self._tiers:
            raise ValueError(f"Tier '{tier_name}' not found")
        
        return await self._tiers[tier_name].check_or_raise(key)


# =============================================================================
# Convenience Functions
# =============================================================================

# Global rate limiter instance
_global_limiter: Optional[SlidingWindowRateLimiter] = None


def get_rate_limiter(
    limit: int = 60,
    window: int = 60,
) -> SlidingWindowRateLimiter:
    """Get or create global rate limiter."""
    global _global_limiter
    if _global_limiter is None:
        _global_limiter = SlidingWindowRateLimiter(limit=limit, window_seconds=window)
    return _global_limiter


async def rate_limit(
    key: str,
    limit: int = 60,
    window: int = 60,
) -> RateLimitResult:
    """
    Quick rate limit check.
    
    Example:
        result = await rate_limit(f"user:{user_id}")
        if not result.allowed:
            raise HTTPException(429, headers=result.to_headers())
    """
    limiter = get_rate_limiter(limit, window)
    return await limiter.check(key)
