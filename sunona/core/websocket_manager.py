"""
Sunona Voice AI - WebSocket Connection Manager

Production-grade WebSocket connection management for real-time
voice streaming with heartbeats, reconnection, and session tracking.

Features:
- Connection lifecycle management
- Session state persistence
- Heartbeat/ping-pong
- Graceful disconnection
- Message buffering
- Broadcasting capabilities
"""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional, Set

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """WebSocket connection states."""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUTHENTICATED = "authenticated"
    ACTIVE = "active"  # In a call/session
    CLOSING = "closing"
    CLOSED = "closed"


@dataclass
class ConnectionInfo:
    """
    Information about a WebSocket connection.
    
    Attributes:
        connection_id: Unique connection identifier
        websocket: The WebSocket instance
        state: Current connection state
        connected_at: Connection timestamp
        last_activity: Last message timestamp
        user_id: Authenticated user ID
        agent_id: Associated agent ID
        session_id: Call/chat session ID
        metadata: Additional connection data
    """
    connection_id: str
    websocket: WebSocket
    state: ConnectionState = ConnectionState.CONNECTING
    connected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Message buffer for reconnection
    message_buffer: List[Dict] = field(default_factory=list)
    buffer_size: int = 100
    
    # Heartbeat tracking
    last_ping: Optional[datetime] = None
    last_pong: Optional[datetime] = None
    missed_pings: int = 0
    
    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.now(timezone.utc)
    
    def is_stale(self, timeout_seconds: float = 60.0) -> bool:
        """Check if connection is stale (no activity)."""
        elapsed = (datetime.now(timezone.utc) - self.last_activity).total_seconds()
        return elapsed > timeout_seconds
    
    def add_to_buffer(self, message: Dict) -> None:
        """Add message to buffer (for replay on reconnection)."""
        self.message_buffer.append(message)
        # Keep buffer size limited
        if len(self.message_buffer) > self.buffer_size:
            self.message_buffer = self.message_buffer[-self.buffer_size:]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excluding websocket)."""
        return {
            "connection_id": self.connection_id,
            "state": self.state.value,
            "connected_at": self.connected_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "metadata": self.metadata,
        }


class WebSocketManager:
    """
    Manages WebSocket connections with heartbeats and session tracking.
    
    Features:
    - Connection registry
    - Heartbeat monitoring
    - Session-based grouping
    - Broadcast capabilities
    - Connection health checks
    
    Example:
        manager = WebSocketManager()
        
        @app.websocket("/ws/{agent_id}")
        async def websocket_endpoint(websocket: WebSocket, agent_id: str):
            connection = await manager.connect(websocket, agent_id=agent_id)
            
            try:
                async for message in manager.receive_messages(connection):
                    # Process message
                    await manager.send_json(connection, {"response": "ok"})
            finally:
                await manager.disconnect(connection)
    """
    
    def __init__(
        self,
        heartbeat_interval: float = 30.0,
        heartbeat_timeout: float = 10.0,
        stale_timeout: float = 120.0,
        max_connections: int = 10000,
    ):
        """
        Initialize WebSocket manager.
        
        Args:
            heartbeat_interval: Seconds between heartbeat pings
            heartbeat_timeout: Seconds to wait for pong response
            stale_timeout: Seconds before considering connection stale
            max_connections: Maximum allowed connections
        """
        self.heartbeat_interval = heartbeat_interval
        self.heartbeat_timeout = heartbeat_timeout
        self.stale_timeout = stale_timeout
        self.max_connections = max_connections
        
        # Connection storage
        self._connections: Dict[str, ConnectionInfo] = {}
        self._user_connections: Dict[str, Set[str]] = {}  # user_id -> connection_ids
        self._session_connections: Dict[str, Set[str]] = {}  # session_id -> connection_ids
        self._agent_connections: Dict[str, Set[str]] = {}  # agent_id -> connection_ids
        
        # Locks for thread safety
        self._lock = asyncio.Lock()
        
        # Heartbeat task
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Event callbacks
        self._on_connect_callbacks: List[Callable[[ConnectionInfo], Awaitable[None]]] = []
        self._on_disconnect_callbacks: List[Callable[[ConnectionInfo], Awaitable[None]]] = []
        self._on_message_callbacks: List[Callable[[ConnectionInfo, Dict], Awaitable[None]]] = []
    
    @property
    def connection_count(self) -> int:
        """Get current number of connections."""
        return len(self._connections)
    
    async def start(self) -> None:
        """Start the connection manager (heartbeat loop)."""
        if self._running:
            return
        
        self._running = True
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        logger.info("WebSocket manager started")
    
    async def stop(self) -> None:
        """Stop the connection manager and close all connections."""
        self._running = False
        
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # Close all connections
        for connection in list(self._connections.values()):
            await self.disconnect(connection, reason="server_shutdown")
        
        logger.info("WebSocket manager stopped")
    
    async def connect(
        self,
        websocket: WebSocket,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> ConnectionInfo:
        """
        Accept and register a new WebSocket connection.
        
        Args:
            websocket: FastAPI WebSocket instance
            user_id: Optional user identifier
            agent_id: Optional agent identifier
            session_id: Optional session identifier
            metadata: Additional connection metadata
        
        Returns:
            ConnectionInfo for the new connection
        
        Raises:
            ConnectionRefusedError if at max connections
        """
        async with self._lock:
            # Check connection limit
            if len(self._connections) >= self.max_connections:
                logger.warning(f"Connection refused: max connections ({self.max_connections}) reached")
                await websocket.close(code=1013, reason="Server overloaded")
                raise ConnectionRefusedError("Maximum connections reached")
            
            # Accept the connection
            await websocket.accept()
            
            # Create connection info
            connection_id = str(uuid.uuid4())
            connection = ConnectionInfo(
                connection_id=connection_id,
                websocket=websocket,
                state=ConnectionState.CONNECTED,
                user_id=user_id,
                agent_id=agent_id,
                session_id=session_id,
                metadata=metadata or {},
            )
            
            # Register connection
            self._connections[connection_id] = connection
            
            if user_id:
                if user_id not in self._user_connections:
                    self._user_connections[user_id] = set()
                self._user_connections[user_id].add(connection_id)
            
            if agent_id:
                if agent_id not in self._agent_connections:
                    self._agent_connections[agent_id] = set()
                self._agent_connections[agent_id].add(connection_id)
            
            if session_id:
                if session_id not in self._session_connections:
                    self._session_connections[session_id] = set()
                self._session_connections[session_id].add(connection_id)
        
        logger.info(
            f"WebSocket connected: {connection_id}",
            extra={
                "connection_id": connection_id,
                "user_id": user_id,
                "agent_id": agent_id,
                "session_id": session_id,
            },
        )
        
        # Call connect callbacks
        for callback in self._on_connect_callbacks:
            try:
                await callback(connection)
            except Exception as e:
                logger.error(f"Error in connect callback: {e}")
        
        return connection
    
    async def disconnect(
        self,
        connection: ConnectionInfo,
        reason: str = "normal",
    ) -> None:
        """
        Disconnect and unregister a WebSocket connection.
        
        Args:
            connection: Connection to disconnect
            reason: Disconnect reason
        """
        connection_id = connection.connection_id
        
        async with self._lock:
            # Update state
            connection.state = ConnectionState.CLOSING
            
            # Remove from registries
            self._connections.pop(connection_id, None)
            
            if connection.user_id and connection.user_id in self._user_connections:
                self._user_connections[connection.user_id].discard(connection_id)
                if not self._user_connections[connection.user_id]:
                    del self._user_connections[connection.user_id]
            
            if connection.agent_id and connection.agent_id in self._agent_connections:
                self._agent_connections[connection.agent_id].discard(connection_id)
                if not self._agent_connections[connection.agent_id]:
                    del self._agent_connections[connection.agent_id]
            
            if connection.session_id and connection.session_id in self._session_connections:
                self._session_connections[connection.session_id].discard(connection_id)
                if not self._session_connections[connection.session_id]:
                    del self._session_connections[connection.session_id]
        
        # Close the WebSocket
        try:
            await connection.websocket.close()
        except Exception as e:
            logger.debug(f"Error closing WebSocket: {e}")
        
        connection.state = ConnectionState.CLOSED
        
        logger.info(
            f"WebSocket disconnected: {connection_id} ({reason})",
            extra={
                "connection_id": connection_id,
                "reason": reason,
                "user_id": connection.user_id,
            },
        )
        
        # Call disconnect callbacks
        for callback in self._on_disconnect_callbacks:
            try:
                await callback(connection)
            except Exception as e:
                logger.error(f"Error in disconnect callback: {e}")
    
    def get_connection(self, connection_id: str) -> Optional[ConnectionInfo]:
        """Get a connection by ID."""
        return self._connections.get(connection_id)
    
    def get_user_connections(self, user_id: str) -> List[ConnectionInfo]:
        """Get all connections for a user."""
        connection_ids = self._user_connections.get(user_id, set())
        return [
            self._connections[cid] 
            for cid in connection_ids 
            if cid in self._connections
        ]
    
    def get_session_connections(self, session_id: str) -> List[ConnectionInfo]:
        """Get all connections for a session."""
        connection_ids = self._session_connections.get(session_id, set())
        return [
            self._connections[cid] 
            for cid in connection_ids 
            if cid in self._connections
        ]
    
    def get_agent_connections(self, agent_id: str) -> List[ConnectionInfo]:
        """Get all connections for an agent."""
        connection_ids = self._agent_connections.get(agent_id, set())
        return [
            self._connections[cid] 
            for cid in connection_ids 
            if cid in self._connections
        ]
    
    async def send_json(
        self,
        connection: ConnectionInfo,
        data: Dict[str, Any],
        save_to_buffer: bool = False,
    ) -> bool:
        """
        Send JSON data to a connection.
        
        Args:
            connection: Target connection
            data: JSON-serializable data
            save_to_buffer: Whether to save to replay buffer
        
        Returns:
            True if sent successfully
        """
        try:
            await connection.websocket.send_json(data)
            connection.update_activity()
            
            if save_to_buffer:
                connection.add_to_buffer(data)
            
            return True
        except Exception as e:
            logger.error(f"Failed to send to {connection.connection_id}: {e}")
            # If a send fails, the connection is usually dead. Disconnect it.
            asyncio.create_task(self.disconnect(connection, reason=f"send_error: {type(e).__name__}"))
            return False
    
    async def send_bytes(
        self,
        connection: ConnectionInfo,
        data: bytes,
    ) -> bool:
        """
        Send binary data to a connection.
        
        Args:
            connection: Target connection
            data: Binary data
        
        Returns:
            True if sent successfully
        """
        try:
            await connection.websocket.send_bytes(data)
            connection.update_activity()
            return True
        except Exception as e:
            logger.error(f"Failed to send bytes to {connection.connection_id}: {e}")
            return False
    
    async def send_text(
        self,
        connection: ConnectionInfo,
        text: str,
    ) -> bool:
        """Send text data to a connection."""
        try:
            await connection.websocket.send_text(text)
            connection.update_activity()
            return True
        except Exception as e:
            logger.error(f"Failed to send text to {connection.connection_id}: {e}")
            return False
    
    async def broadcast_json(
        self,
        data: Dict[str, Any],
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None,
        exclude: Optional[Set[str]] = None,
    ) -> int:
        """
        Broadcast JSON to multiple connections.
        
        Args:
            data: Data to broadcast
            session_id: Filter by session
            agent_id: Filter by agent
            user_id: Filter by user
            exclude: Connection IDs to exclude
        
        Returns:
            Number of successful sends
        """
        # Determine target connections
        async with self._lock:
            if session_id:
                connections = self.get_session_connections(session_id)
            elif agent_id:
                connections = self.get_agent_connections(agent_id)
            elif user_id:
                connections = self.get_user_connections(user_id)
            else:
                connections = list(self._connections.values())
        
        # Apply exclusions
        exclude_ids = exclude or set()
        connections = [c for c in connections if c.connection_id not in exclude_ids]
        
        # Send to all
        success_count = 0
        for conn in connections:
            if await self.send_json(conn, data):
                success_count += 1
        
        return success_count
    
    async def receive_json(
        self,
        connection: ConnectionInfo,
        timeout: Optional[float] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Receive JSON from a connection.
        
        Args:
            connection: Source connection
            timeout: Optional timeout in seconds
        
        Returns:
            Received data or None on timeout/error
        """
        try:
            if timeout:
                data = await asyncio.wait_for(
                    connection.websocket.receive_json(),
                    timeout=timeout,
                )
            else:
                data = await connection.websocket.receive_json()
            
            connection.update_activity()
            
            # Handle pong response
            if isinstance(data, dict) and data.get("type") == "pong":
                connection.last_pong = datetime.now(timezone.utc)
                connection.missed_pings = 0
                return None  # Don't return pong messages
            
            return data
        except asyncio.TimeoutError:
            return None
        except WebSocketDisconnect:
            raise
        except Exception as e:
            logger.error(f"Error receiving from {connection.connection_id}: {e}")
            return None
    
    async def receive_bytes(
        self,
        connection: ConnectionInfo,
        timeout: Optional[float] = None,
    ) -> Optional[bytes]:
        """Receive binary data from a connection."""
        try:
            if timeout:
                data = await asyncio.wait_for(
                    connection.websocket.receive_bytes(),
                    timeout=timeout,
                )
            else:
                data = await connection.websocket.receive_bytes()
            
            connection.update_activity()
            return data
        except asyncio.TimeoutError:
            return None
        except WebSocketDisconnect:
            raise
        except Exception as e:
            logger.error(f"Error receiving bytes from {connection.connection_id}: {e}")
            return None
    
    async def receive_messages(
        self,
        connection: ConnectionInfo,
    ):
        """
        Async generator for receiving messages from a connection.
        Yields either a Dict (JSON) or bytes (binary).
        """
        while connection.state in [ConnectionState.CONNECTED, ConnectionState.AUTHENTICATED, ConnectionState.ACTIVE]:
            try:
                data = await connection.websocket.receive()
                
                if data["type"] == "websocket.receive":
                    connection.update_activity()
                    
                    if "text" in data:
                        try:
                            message = json.loads(data["text"])
                            # Handle pong response
                            if isinstance(message, dict) and message.get("type") == "pong":
                                connection.last_pong = datetime.now(timezone.utc)
                                connection.missed_pings = 0
                                continue
                            yield message
                        except json.JSONDecodeError:
                            yield data["text"]
                    elif "bytes" in data:
                        yield data["bytes"]
                
                elif data["type"] == "websocket.disconnect":
                    break
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in receive_messages for {connection.connection_id}: {e}")
                break
        
        # Connection closed or error occurred
        await self.disconnect(connection, reason="receive_loop_ended")
    
    async def _heartbeat_loop(self):
        """Background task for connection heartbeats."""
        while self._running:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                
                stale_connections = []
                
                for connection in list(self._connections.values()):
                    # Check for stale connections
                    if connection.is_stale(self.stale_timeout):
                        stale_connections.append(connection)
                        continue
                    
                    # Check for missed pongs
                    if connection.missed_pings >= 3:
                        stale_connections.append(connection)
                        continue
                    
                    # Send ping
                    try:
                        connection.last_ping = datetime.now(timezone.utc)
                        connection.missed_pings += 1
                        await connection.websocket.send_json({
                            "type": "ping",
                            "timestamp": connection.last_ping.isoformat(),
                        })
                    except Exception:
                        stale_connections.append(connection)
                
                # Disconnect stale connections concurrently
                if stale_connections:
                    tasks = [
                        asyncio.create_task(self.disconnect(conn, reason="stale"))
                        for conn in stale_connections
                    ]
                    # We don't await them all strictly to keep the loop moving,
                    # but we allow them a bit of time or just let them run in bg.
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
    
    def on_connect(
        self,
        callback: Callable[[ConnectionInfo], Awaitable[None]],
    ) -> None:
        """Register a callback for new connections."""
        self._on_connect_callbacks.append(callback)
    
    def on_disconnect(
        self,
        callback: Callable[[ConnectionInfo], Awaitable[None]],
    ) -> None:
        """Register a callback for disconnections."""
        self._on_disconnect_callbacks.append(callback)
    
    def on_message(
        self,
        callback: Callable[[ConnectionInfo, Dict], Awaitable[None]],
    ) -> None:
        """Register a callback for messages."""
        self._on_message_callbacks.append(callback)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection manager statistics."""
        return {
            "total_connections": len(self._connections),
            "unique_users": len(self._user_connections),
            "active_sessions": len(self._session_connections),
            "active_agents": len(self._agent_connections),
            "connections_by_state": self._count_by_state(),
        }
    
    def _count_by_state(self) -> Dict[str, int]:
        """Count connections by state."""
        counts: Dict[str, int] = {}
        for conn in self._connections.values():
            state = conn.state.value
            counts[state] = counts.get(state, 0) + 1
        return counts


# Global WebSocket manager instance
_global_ws_manager: Optional[WebSocketManager] = None


def get_websocket_manager() -> WebSocketManager:
    """Get or create global WebSocket manager."""
    global _global_ws_manager
    if _global_ws_manager is None:
        _global_ws_manager = WebSocketManager()
    return _global_ws_manager
