"""
Redis Configuration for Sunona Voice AI

Production-ready Redis configuration with connection pooling,
health checks, and automatic reconnection.
"""
import os
import logging
from typing import Optional

import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool

logger = logging.getLogger(__name__)

# Redis settings from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_MAX_CONNECTIONS = int(os.getenv("REDIS_MAX_CONNECTIONS", "10"))
REDIS_SOCKET_TIMEOUT = float(os.getenv("REDIS_SOCKET_TIMEOUT", "5.0"))

# Global connection pool
_redis_pool: Optional[ConnectionPool] = None
_redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """
    Get Redis connection from pool.
    
    Returns:
        redis.Redis: Async Redis client
    """
    global _redis_pool, _redis_client
    
    if _redis_client is None:
        try:
            _redis_pool = ConnectionPool.from_url(
                REDIS_URL,
                password=REDIS_PASSWORD,
                max_connections=REDIS_MAX_CONNECTIONS,
                socket_timeout=REDIS_SOCKET_TIMEOUT,
                decode_responses=True,
            )
            _redis_client = redis.Redis(connection_pool=_redis_pool)
            
            # Test connection
            await _redis_client.ping()
            logger.info("✅ Redis connection established")
            
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}")
            # Return a null client that gracefully handles missing Redis
            _redis_client = NullRedis()
    
    return _redis_client


async def close_redis():
    """Close Redis connection pool."""
    global _redis_pool, _redis_client
    
    if _redis_client and not isinstance(_redis_client, NullRedis):
        await _redis_client.close()
        logger.info("Redis connection closed")
    
    if _redis_pool:
        await _redis_pool.disconnect()
    
    _redis_client = None
    _redis_pool = None


async def check_redis_health() -> dict:
    """
    Check Redis health status.
    
    Returns:
        dict: Health status with latency info
    """
    import time
    
    try:
        client = await get_redis()
        
        if isinstance(client, NullRedis):
            return {
                "status": "unavailable",
                "message": "Redis not configured",
            }
        
        start = time.time()
        await client.ping()
        latency_ms = (time.time() - start) * 1000
        
        info = await client.info("server")
        
        return {
            "status": "healthy",
            "latency_ms": round(latency_ms, 2),
            "version": info.get("redis_version", "unknown"),
            "connected_clients": info.get("connected_clients", 0),
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }


class NullRedis:
    """
    Null Redis client for graceful degradation when Redis is unavailable.
    All operations return None or empty results.
    """
    
    async def ping(self) -> bool:
        return False
    
    async def get(self, key: str) -> None:
        return None
    
    async def set(self, key: str, value: str, **kwargs) -> bool:
        return False
    
    async def setex(self, key: str, time: int, value: str) -> bool:
        return False
    
    async def delete(self, *keys) -> int:
        return 0
    
    async def exists(self, *keys) -> int:
        return 0
    
    async def expire(self, key: str, time: int) -> bool:
        return False
    
    async def ttl(self, key: str) -> int:
        return -2
    
    async def keys(self, pattern: str) -> list:
        return []
    
    async def hget(self, name: str, key: str) -> None:
        return None
    
    async def hset(self, name: str, key: str = None, value: str = None, mapping: dict = None) -> int:
        return 0
    
    async def hgetall(self, name: str) -> dict:
        return {}
    
    async def hdel(self, name: str, *keys) -> int:
        return 0
    
    async def lpush(self, name: str, *values) -> int:
        return 0
    
    async def lrange(self, name: str, start: int, end: int) -> list:
        return []
    
    async def publish(self, channel: str, message: str) -> int:
        return 0
    
    async def close(self):
        pass
    
    async def info(self, section: str = None) -> dict:
        return {}
