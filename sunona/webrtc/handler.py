"""
Sunona Voice AI - WebRTC Handler

Production-grade WebRTC support for browser-based voice calls.
Enables direct browser-to-server calling without a phone number.

Features:
- WebRTC signaling (offer/answer/ICE)
- Audio track handling
- Voice pipeline integration
- Low-latency streaming
- Browser compatibility
"""

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Awaitable

logger = logging.getLogger(__name__)


class WebRTCState(Enum):
    """WebRTC connection states."""
    NEW = "new"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    FAILED = "failed"
    CLOSED = "closed"
    CLOSING = "closing"


@dataclass
class ICECandidate:
    """ICE candidate for WebRTC."""
    candidate: str
    sdp_mid: Optional[str] = None
    sdp_m_line_index: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate": self.candidate,
            "sdpMid": self.sdp_mid,
            "sdpMLineIndex": self.sdp_m_line_index,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ICECandidate":
        return cls(
            candidate=data.get("candidate", ""),
            sdp_mid=data.get("sdpMid"),
            sdp_m_line_index=data.get("sdpMLineIndex"),
        )


@dataclass
class SessionDescription:
    """SDP session description for WebRTC."""
    type: str  # "offer" or "answer"
    sdp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type, "sdp": self.sdp}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionDescription":
        return cls(type=data.get("type", ""), sdp=data.get("sdp", ""))


@dataclass
class WebRTCSession:
    """
    WebRTC session state.
    
    Tracks connection state, media tracks, and signaling.
    """
    session_id: str
    agent_id: str
    organization_id: Optional[str] = None
    user_id: Optional[str] = None
    state: WebRTCState = WebRTCState.NEW
    local_description: Optional[SessionDescription] = None
    remote_description: Optional[SessionDescription] = None
    ice_candidates: List[ICECandidate] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    connected_at: Optional[datetime] = None
    
    # Audio processing
    audio_callback: Optional[Callable[[bytes], Awaitable[None]]] = None
    
    # Statistics
    audio_packets_received: int = 0
    audio_packets_sent: int = 0
    bytes_received: int = 0
    bytes_sent: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "organization_id": self.organization_id,
            "user_id": self.user_id,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "connected_at": self.connected_at.isoformat() if self.connected_at else None,
            "stats": {
                "audio_packets_received": self.audio_packets_received,
                "audio_packets_sent": self.audio_packets_sent,
                "bytes_received": self.bytes_received,
                "bytes_sent": self.bytes_sent,
            }
        }


class WebRTCHandler:
    """
    WebRTC signaling and media handler.
    
    Handles the signaling protocol for WebRTC and integrates
    with the voice processing pipeline.
    """
    
    def __init__(
        self,
        stun_servers: Optional[List[str]] = None,
        turn_servers: Optional[List[Dict[str, str]]] = None,
    ):
        """
        Initialize WebRTC handler.
        """
        self.stun_servers = stun_servers or [
            "stun:stun.l.google.com:19302",
            "stun:stun1.l.google.com:19302",
        ]
        self.turn_servers = turn_servers or []
        
        self._sessions: Dict[str, WebRTCSession] = {}
        self._peer_connections: Dict[str, Any] = {}  # aiortc.RTCPeerConnection
        self._lock = asyncio.Lock()
        
        # Check if aiortc is available
        self._aiortc_available = self._check_aiortc()
    
    def _check_aiortc(self) -> bool:
        """Check if aiortc is available."""
        try:
            import aiortc
            return True
        except ImportError:
            logger.warning(
                "aiortc not installed. WebRTC will use signaling-only mode."
            )
            return False
    
    def get_ice_servers(self) -> List[Dict[str, Any]]:
        """Get ICE server configuration for client."""
        servers = []
        for url in self.stun_servers:
            servers.append({"urls": url})
        for turn in self.turn_servers:
            servers.append(turn)
        return servers
    
    async def create_session(
        self,
        agent_id: str,
        organization_id: Optional[str] = None,
        user_id: Optional[str] = None,
        audio_callback: Optional[Callable[[bytes], Awaitable[None]]] = None,
    ) -> WebRTCSession:
        """
        Create a new WebRTC session.
        """
        session_id = f"webrtc_{uuid.uuid4().hex}"
        
        session = WebRTCSession(
            session_id=session_id,
            agent_id=agent_id,
            organization_id=organization_id,
            user_id=user_id,
            audio_callback=audio_callback,
        )
        
        async with self._lock:
            self._sessions[session_id] = session
        
        logger.info(f"Created WebRTC session {session_id} for agent {agent_id}")
        return session
    
    async def handle_offer(
        self,
        session_id: str,
        offer: SessionDescription,
    ) -> Optional[SessionDescription]:
        """
        Handle WebRTC offer and create answer.
        """
        session = self._sessions.get(session_id)
        if not session:
            logger.error(f"Session {session_id} not found")
            return None
        
        session.remote_description = offer
        session.state = WebRTCState.CONNECTING
        
        if self._aiortc_available:
            return await self._create_aiortc_answer(session, offer)
        else:
            return await self._create_signaling_answer(session, offer)
    
    async def _create_aiortc_answer(
        self,
        session: WebRTCSession,
        offer: SessionDescription,
    ) -> Optional[SessionDescription]:
        """Create answer using aiortc."""
        try:
            from aiortc import RTCPeerConnection, RTCSessionDescription
            
            pc = RTCPeerConnection()
            self._peer_connections[session.session_id] = pc
            
            @pc.on("track")
            async def on_track(track):
                logger.info(f"Received {track.kind} track")
                if track.kind == "audio":
                    asyncio.create_task(self._process_audio_track(session, track))
            
            @pc.on("connectionstatechange")
            async def on_connection_state_change():
                logger.info(f"Connection state: {pc.connectionState}")
                if pc.connectionState == "connected":
                    session.state = WebRTCState.CONNECTED
                    session.connected_at = datetime.now(timezone.utc)
                elif pc.connectionState in ("failed", "closed"):
                    session.state = WebRTCState.FAILED if pc.connectionState == "failed" else WebRTCState.CLOSED
            
            await pc.setRemoteDescription(RTCSessionDescription(sdp=offer.sdp, type=offer.type))
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)
            
            session.local_description = SessionDescription(
                type=pc.localDescription.type,
                sdp=pc.localDescription.sdp,
            )
            return session.local_description
        except Exception as e:
            logger.error(f"Error creating WebRTC answer: {e}")
            session.state = WebRTCState.FAILED
            return None
    
    async def _create_signaling_answer(self, session: WebRTCSession, offer: SessionDescription) -> SessionDescription:
        return SessionDescription(type="answer", sdp="v=0\no=-\n")

    async def _process_audio_track(
        self,
        session: WebRTCSession,
        track,
    ) -> None:
        """Process incoming audio track asynchronously."""
        try:
            while True:
                frame = await track.recv()
                audio_bytes = frame.to_ndarray().tobytes()
                
                session.audio_packets_received += 1
                session.bytes_received += len(audio_bytes)
                
                if session.audio_callback:
                    asyncio.create_task(session.audio_callback(audio_bytes))
        except Exception as e:
            if "MediaStreamTrack ended" not in str(e):
                logger.error(f"Audio track error for session {session.session_id}: {e}")

    async def send_audio(
        self,
        session_id: str,
        audio_pcm: bytes,
    ) -> bool:
        """
        Send audio to an active WebRTC session.
        """
        session = self._sessions.get(session_id)
        if not session or session.state != WebRTCState.CONNECTED:
            return False
            
        pc = self._peer_connections.get(session_id)
        if not pc:
            return False
            
        try:
            import av
            import numpy as np
            
            transceiver = next((t for t in pc.getTransceivers() if t.kind == "audio"), None)
            if not transceiver or not transceiver.sender or not transceiver.sender.track:
                return False
                
            frame = av.AudioFrame.from_ndarray(
                np.frombuffer(audio_pcm, dtype=np.int16).reshape(1, -1),
                layout='mono',
                format='s16'
            )
            frame.sample_rate = 16000
            
            await transceiver.sender.track.send(frame)
            
            session.audio_packets_sent += 1
            session.bytes_sent += len(audio_pcm)
            return True
        except Exception as e:
            logger.error(f"Error sending audio to WebRTC session {session_id}: {e}")
            return False

    async def add_ice_candidate(self, session_id: str, candidate: ICECandidate) -> bool:
        session = self._sessions.get(session_id)
        if not session or session_id not in self._peer_connections:
            return False
        try:
            from aiortc import RTCIceCandidate
            pc = self._peer_connections[session_id]
            await pc.addIceCandidate(RTCIceCandidate(candidate.candidate, sdpMid=candidate.sdp_mid, sdpMLineIndex=candidate.sdp_m_line_index))
            return True
        except Exception as e:
            logger.error(f"Error adding ICE candidate: {e}")
            return False

    async def close_session(self, session_id: str) -> bool:
        session = self._sessions.get(session_id)
        if not session:
            return False
        session.state = WebRTCState.CLOSING
        if session_id in self._peer_connections:
            pc = self._peer_connections.pop(session_id)
            await pc.close()
        async with self._lock:
            if session_id in self._sessions: del self._sessions[session_id]
        return True

    def get_session(self, session_id: str) -> Optional[WebRTCSession]:
        return self._sessions.get(session_id)

    def get_active_sessions(self, organization_id: Optional[str] = None) -> List[WebRTCSession]:
        sessions = [s for s in self._sessions.values() if s.state not in (WebRTCState.CLOSED, WebRTCState.FAILED)]
        if organization_id: sessions = [s for s in sessions if s.organization_id == organization_id]
        return sessions

    def set_audio_callback(self, session_id: str, callback: Callable[[bytes], Awaitable[None]]) -> bool:
        session = self._sessions.get(session_id)
        if not session: return False
        session.audio_callback = callback
        return True

    def get_stats(self) -> Dict[str, Any]:
        return {
            "active_sessions": len(self.get_active_sessions()),
            "total_sessions": len(self._sessions),
            "aiortc_available": self._aiortc_available,
        }

# Global handler
_global_handler: Optional[WebRTCHandler] = None

def get_webrtc_handler() -> WebRTCHandler:
    global _global_handler
    if _global_handler is None:
        _global_handler = WebRTCHandler()
    return _global_handler
