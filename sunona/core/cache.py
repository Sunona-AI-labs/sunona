"""
Redis Cache Service for Sunona Voice AI

High-performance caching layer with typed methods for:
- Session management
- Agent configuration caching
- Call data caching
- Analytics caching
- Rate limiting support
"""
import json
import logging
from typing import Any, Optional, TypeVar, Generic
from datetime import datetime, timedelta

from sunona.config.redis import get_redis, NullRedis

logger = logging.getLogger(__name__)

# Type variable for generic cache operations
T = TypeVar("T")

# Cache key prefixes (namespacing)
class CachePrefix:
    SESSION = "session:"
    AGENT = "agent:"
    AGENT_LIST = "agents:"
    CALL = "call:"
    CALL_LIST = "calls:"
    ANALYTICS = "analytics:"
    BILLING = "billing:"
    USER = "user:"
    ORG = "org:"
    RATE_LIMIT = "ratelimit:"
    LOCK = "lock:"


# Default TTL values (in seconds)
class CacheTTL:
    SESSION = 7 * 24 * 3600  # 7 days
    AGENT = 300  # 5 minutes
    AGENT_LIST = 60  # 1 minute
    CALL = 3600  # 1 hour
    CALL_LIST = 30  # 30 seconds
    ANALYTICS = 300  # 5 minutes
    BILLING = 60  # 1 minute
    USER = 300  # 5 minutes
    SHORT = 30  # 30 seconds
    MEDIUM = 300  # 5 minutes
    LONG = 3600  # 1 hour


class CacheService:
    """
    Production-ready Redis cache service with typed operations.
    Gracefully degrades when Redis is unavailable.
    """
    
    # ==========================================================================
    # Core Operations
    # ==========================================================================
    
    async def get(self, key: str) -> Optional[Any]:
        """Get and deserialize value from cache."""
        try:
            redis = await get_redis()
            value = await redis.get(key)
            
            if value is None:
                return None
            
            return json.loads(value)
            
        except json.JSONDecodeError:
            # Return raw value if not JSON
            return value
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int = CacheTTL.MEDIUM,
    ) -> bool:
        """Serialize and set value with TTL."""
        try:
            redis = await get_redis()
            
            if isinstance(redis, NullRedis):
                return False
            
            serialized = json.dumps(value, default=str)
            result = await redis.setex(key, ttl_seconds, serialized)
            return bool(result)
            
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            redis = await get_redis()
            result = await redis.delete(key)
            return result > 0
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        try:
            redis = await get_redis()
            keys = await redis.keys(pattern)
            
            if not keys:
                return 0
            
            return await redis.delete(*keys)
            
        except Exception as e:
            logger.warning(f"Cache delete pattern error: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            redis = await get_redis()
            return await redis.exists(key) > 0
        except Exception:
            return False
    
    # ==========================================================================
    # Session Management
    # ==========================================================================
    
    async def create_session(
        self,
        session_id: str,
        user_id: str,
        org_id: str,
        email: str,
        role: str = "member",
        ttl_hours: int = 168,  # 7 days
    ) -> bool:
        """Create user session."""
        key = f"{CachePrefix.SESSION}{session_id}"
        
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "org_id": org_id,
            "email": email,
            "role": role,
            "created_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
        }
        
        return await self.set(key, session_data, ttl_hours * 3600)
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data."""
        key = f"{CachePrefix.SESSION}{session_id}"
        session = await self.get(key)
        
        if session:
            # Update last active time
            session["last_active"] = datetime.now().isoformat()
            await self.set(key, session, CacheTTL.SESSION)
        
        return session
    
    async def destroy_session(self, session_id: str) -> bool:
        """Destroy session (logout)."""
        key = f"{CachePrefix.SESSION}{session_id}"
        return await self.delete(key)
    
    async def destroy_user_sessions(self, user_id: str) -> int:
        """Destroy all sessions for a user."""
        # This requires scanning - in production use a session index
        pattern = f"{CachePrefix.SESSION}*"
        count = 0
        
        try:
            redis = await get_redis()
            keys = await redis.keys(pattern)
            
            for key in keys:
                session = await self.get(key)
                if session and session.get("user_id") == user_id:
                    await self.delete(key)
                    count += 1
            
            return count
            
        except Exception as e:
            logger.warning(f"Destroy user sessions error: {e}")
            return count
    
    # ==========================================================================
    # Agent Caching
    # ==========================================================================
    
    async def cache_agent(self, agent_id: str, data: dict) -> bool:
        """Cache agent configuration."""
        key = f"{CachePrefix.AGENT}{agent_id}"
        return await self.set(key, data, CacheTTL.AGENT)
    
    async def get_agent(self, agent_id: str) -> Optional[dict]:
        """Get cached agent."""
        key = f"{CachePrefix.AGENT}{agent_id}"
        return await self.get(key)
    
    async def invalidate_agent(self, agent_id: str) -> bool:
        """Invalidate agent cache."""
        key = f"{CachePrefix.AGENT}{agent_id}"
        # Also invalidate agent list cache
        await self.delete_pattern(f"{CachePrefix.AGENT_LIST}*")
        return await self.delete(key)
    
    async def cache_agent_list(
        self,
        org_id: str,
        agents: list,
        page: int = 1,
    ) -> bool:
        """Cache agent list for organization."""
        key = f"{CachePrefix.AGENT_LIST}{org_id}:page:{page}"
        return await self.set(key, agents, CacheTTL.AGENT_LIST)
    
    async def get_agent_list(
        self,
        org_id: str,
        page: int = 1,
    ) -> Optional[list]:
        """Get cached agent list."""
        key = f"{CachePrefix.AGENT_LIST}{org_id}:page:{page}"
        return await self.get(key)
    
    # ==========================================================================
    # Call Caching
    # ==========================================================================
    
    async def cache_call(self, call_id: str, data: dict) -> bool:
        """Cache call data."""
        key = f"{CachePrefix.CALL}{call_id}"
        return await self.set(key, data, CacheTTL.CALL)
    
    async def get_call(self, call_id: str) -> Optional[dict]:
        """Get cached call."""
        key = f"{CachePrefix.CALL}{call_id}"
        return await self.get(key)
    
    async def cache_call_list(
        self,
        org_id: str,
        calls: list,
        filters_hash: str = "default",
    ) -> bool:
        """Cache call list with filters."""
        key = f"{CachePrefix.CALL_LIST}{org_id}:{filters_hash}"
        return await self.set(key, calls, CacheTTL.CALL_LIST)
    
    # ==========================================================================
    # Analytics Caching
    # ==========================================================================
    
    async def cache_analytics(
        self,
        org_id: str,
        metric_type: str,
        data: dict,
        period: str = "7d",
    ) -> bool:
        """Cache analytics data."""
        key = f"{CachePrefix.ANALYTICS}{org_id}:{metric_type}:{period}"
        return await self.set(key, data, CacheTTL.ANALYTICS)
    
    async def get_analytics(
        self,
        org_id: str,
        metric_type: str,
        period: str = "7d",
    ) -> Optional[dict]:
        """Get cached analytics."""
        key = f"{CachePrefix.ANALYTICS}{org_id}:{metric_type}:{period}"
        return await self.get(key)
    
    # ==========================================================================
    # Billing Caching
    # ==========================================================================
    
    async def cache_balance(self, account_id: str, data: dict) -> bool:
        """Cache account balance."""
        key = f"{CachePrefix.BILLING}balance:{account_id}"
        return await self.set(key, data, CacheTTL.BILLING)
    
    async def get_balance(self, account_id: str) -> Optional[dict]:
        """Get cached balance."""
        key = f"{CachePrefix.BILLING}balance:{account_id}"
        return await self.get(key)
    
    async def invalidate_balance(self, account_id: str) -> bool:
        """Invalidate balance cache (after transaction)."""
        key = f"{CachePrefix.BILLING}balance:{account_id}"
        return await self.delete(key)
    
    # ==========================================================================
    # Rate Limiting
    # ==========================================================================
    
    async def check_rate_limit(
        self,
        identifier: str,
        limit: int,
        window_seconds: int,
    ) -> tuple[bool, int]:
        """
        Check rate limit using sliding window.
        
        Returns:
            tuple: (is_allowed, remaining_requests)
        """
        try:
            redis = await get_redis()
            
            if isinstance(redis, NullRedis):
                return (True, limit)  # Allow if no Redis
            
            key = f"{CachePrefix.RATE_LIMIT}{identifier}"
            now = datetime.now().timestamp()
            window_start = now - window_seconds
            
            # Use Redis pipeline for atomic operations
            pipe = redis.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)
            # Add current request
            pipe.zadd(key, {str(now): now})
            # Count requests in window
            pipe.zcard(key)
            # Set expiry
            pipe.expire(key, window_seconds)
            
            results = await pipe.execute()
            current_count = results[2]
            
            is_allowed = current_count <= limit
            remaining = max(0, limit - current_count)
            
            return (is_allowed, remaining)
            
        except Exception as e:
            logger.warning(f"Rate limit check error: {e}")
            return (True, limit)  # Allow on error
    
    # ==========================================================================
    # Distributed Locking
    # ==========================================================================
    
    async def acquire_lock(
        self,
        lock_name: str,
        ttl_seconds: int = 30,
    ) -> bool:
        """Acquire a distributed lock."""
        try:
            redis = await get_redis()
            
            if isinstance(redis, NullRedis):
                return True  # Pretend lock acquired
            
            key = f"{CachePrefix.LOCK}{lock_name}"
            result = await redis.set(key, "1", nx=True, ex=ttl_seconds)
            return result is not None
            
        except Exception as e:
            logger.warning(f"Lock acquire error: {e}")
            return False
    
    async def release_lock(self, lock_name: str) -> bool:
        """Release a distributed lock."""
        key = f"{CachePrefix.LOCK}{lock_name}"
        return await self.delete(key)


# Singleton instance
cache = CacheService()
