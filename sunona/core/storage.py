"""
Sunona Voice AI - Persistent Storage

Production-grade storage backend for agent configurations and state.
"""

import json
import logging
import os
from typing import Dict, Any, Optional, List
try:
    from redis import asyncio as aioredis
except ImportError:
    import aioredis

logger = logging.getLogger(__name__)

class AgentStore:
    """
    Persistent storage for Agent configurations.
    
    Supports:
    - In-memory (default/development)
    - Redis (production)
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        self._redis_url = redis_url or os.getenv("REDIS_URL")
        self._redis = None
        self._in_memory: Dict[str, Dict[str, Any]] = {}
        
        if self._redis_url:
            logger.info(f"Using Redis storage for agents: {self._redis_url}")
        else:
            logger.warning("Using in-memory storage for agents. Data will be lost on restart.")

    async def connect(self):
        """Initialize connection to Redis if configured."""
        if self._redis_url and not self._redis:
            try:
                self._redis = aioredis.from_url(self._redis_url, decode_responses=True)
                await self._redis.ping()
                logger.info("Successfully connected to Redis storage")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}. Falling back to in-memory.")
                self._redis = None

    async def get(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent data by ID."""
        if self._redis:
            data = await self._redis.get(f"agent:{agent_id}")
            return json.loads(data) if data else None
        return self._in_memory.get(agent_id)

    async def set(self, agent_id: str, data: Dict[str, Any]):
        """Save agent data."""
        if self._redis:
            await self._redis.set(f"agent:{agent_id}", json.dumps(data))
        else:
            self._in_memory[agent_id] = data

    async def delete(self, agent_id: str):
        """Delete agent data."""
        if self._redis:
            await self._redis.delete(f"agent:{agent_id}")
        else:
            self._in_memory.pop(agent_id, None)

    async def list_all(self, organization_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List agents, optionally filtered by organization."""
        results = []
        if self._redis:
            keys = await self._redis.keys("agent:*")
            for key in keys:
                data = await self._redis.get(key)
                if data:
                    agent = json.loads(data)
                    agent['agent_id'] = key.split(":")[-1]
                    if not organization_id or agent.get("organization_id") == organization_id:
                        results.append(agent)
        else:
            for aid, data in self._in_memory.items():
                if not organization_id or data.get("organization_id") == organization_id:
                    agent = data.copy()
                    agent['agent_id'] = aid
                    results.append(agent)
        return results

# Singleton instance
_store = None

def get_agent_store() -> AgentStore:
    global _store
    if _store is None:
        _store = AgentStore()
    return _store
