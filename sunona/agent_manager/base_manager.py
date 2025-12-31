"""
Sunona Voice AI - Base Manager

Abstract base class for agent managers.
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseManager(ABC):
    """
    Abstract base class for all manager implementations.
    """
    
    def __init__(self, agent_config: Dict[str, Any], **kwargs):
        """
        Initialize the base manager.
        
        Args:
            agent_config: Agent configuration dictionary
            **kwargs: Additional options
        """
        self.agent_config = agent_config
        self.agent_name = agent_config.get("agent_name", "sunona_agent")
        self.extra_config = kwargs
        
        self._is_running = False
    
    @abstractmethod
    async def run(self) -> AsyncIterator[tuple]:
        """
        Run the manager and yield results.
        
        Yields:
            Tuple of (task_index, result)
        """
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop the manager."""
        pass
    
    @property
    def is_running(self) -> bool:
        """Check if the manager is running."""
        return self._is_running
