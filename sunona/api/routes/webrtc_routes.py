"""
Sunona Voice AI - WebRTC API Routes

REST API endpoints for WebRTC browser calling.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
import numpy as np

from sunona.api.auth import get_api_key, require_auth
from sunona.multitenancy import APIKey
from sunona.billing.middleware import BillingMiddleware
from sunona.webrtc.handler import get_webrtc_handler, SessionDescription, ICECandidate
from sunona.assistant import Assistant
from sunona.agent_manager.task_manager import PipelineResult
from sunona.core.storage import get_agent_store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webrtc", tags=["WebRTC"])
agents_store = get_agent_store()


# =============================================================================
# Request/Response Models
# =============================================================================

class CreateSessionRequest(BaseModel):
    agent_id: str
    user_id: Optional[str] = None


class HandleOfferRequest(BaseModel):
    sdp: str
    type: str = "offer"


class ICECandidateRequest(BaseModel):
    candidate: str
    sdp_mid: Optional[str] = None
    sdp_m_line_index: Optional[int] = None


# =============================================================================
# WebRTC Routes
# =============================================================================

@router.post("/session")
async def create_session(
    request: CreateSessionRequest,
    api_key: APIKey = Depends(get_api_key),
):
    """Create a new WebRTC session."""
    # Enforce billing
    billing = BillingMiddleware()
    await billing.check_balance(api_key.organization_id)
    
    handler = get_webrtc_handler()
    
    # Get agent config for session
    agent_data = await agents_store.get(request.agent_id)
    if not agent_data:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Create assistant for this session
    assistant = Assistant(
        name=agent_data.get("agent_config", {}).get("agent_name", "sunona_agent"),
        organization_id=api_key.organization_id,
        user_id=request.user_id or api_key.id
    )
    
    # Configure assistant tasks
    agent_config = agent_data.get("agent_config", {})
    agent_prompts = agent_data.get("agent_prompts", {})
    for i, task_cfg in enumerate(agent_config.get("tasks", [])):
        task_id = f"task_{i + 1}"
        assistant.tasks.append(task_cfg)
        if task_id in agent_prompts:
            assistant.prompts[task_id] = agent_prompts[task_id]

    async def assistant_audio_callback(audio_bytes: bytes) -> None:
        """Feed audio from WebRTC to Assistant."""
        await assistant.send_input(audio_bytes)

    session = await handler.create_session(
        agent_id=request.agent_id,
        organization_id=api_key.organization_id,
        user_id=request.user_id or api_key.id,
        audio_callback=assistant_audio_callback
    )
    
    # Background task to handle assistant results and push to WebRTC
    async def process_results():
        try:
            async for result_dict in assistant.execute():
                result = PipelineResult(**result_dict)
                
                if result.type == "audio":
                    # Send audio to WebRTC peer
                    await handler.send_audio(session.session_id, result.data)
                elif result.type == "interrupt":
                    # Handle browser-side interruption
                    logger.info(f"Sending interrupt signal to WebRTC session {session.session_id}")
                    # In a real implementation, we might send a DataChannel message
                    # or clear the local buffer if using a custom audio sink.
                    pass
                elif result.type == "transcription":
                    logger.debug(f"WebRTC Transcript: {result.data}")
                    
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in WebRTC assistant result loop: {e}")
        finally:
            await assistant.stop()

    # Store task to cancel later
    session_task = asyncio.create_task(process_results())
    
    # Attach task to session so it gets cleaned up
    # (Note: We'd ideally add a 'tasks' list to WebRTCSession dataclass)
    if not hasattr(session, '_worker_tasks'):
        session._worker_tasks = []
    session._worker_tasks.append(session_task)
    
    return {
        "session_id": session.session_id,
        "state": session.state.value,
        "created_at": session.created_at.isoformat(),
    }


@router.get("/session/{session_id}")
async def get_session(
    session_id: str,
    api_key: APIKey = Depends(get_api_key),
):
    """Get session status."""
    handler = get_webrtc_handler()
    session = handler.get_session(session_id)
    
    if not session or session.organization_id != api_key.organization_id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session.session_id,
        "state": session.state.value,
        "created_at": session.created_at.isoformat(),
    }


@router.post("/session/{session_id}/offer")
async def handle_offer(
    session_id: str,
    request: HandleOfferRequest,
    api_key: APIKey = Depends(get_api_key),
):
    """Handle WebRTC offer and return answer SDP."""
    handler = get_webrtc_handler()
    session = handler.get_session(session_id)
    
    if not session or session.organization_id != api_key.organization_id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Create SessionDescription object for the offer
    offer = SessionDescription(type=request.type, sdp=request.sdp)
    
    answer = await handler.handle_offer(
        session_id=session_id,
        offer=offer,
    )
    
    if not answer:
        raise HTTPException(status_code=400, detail="Failed to process offer")
    
    return {
        "session_id": session_id,
        "answer": {
            "sdp": answer.sdp,
            "type": answer.type,
        },
    }


@router.post("/session/{session_id}/ice")
async def add_ice_candidate(
    session_id: str,
    request: ICECandidateRequest,
    api_key: APIKey = Depends(get_api_key),
):
    """Add ICE candidate."""
    handler = get_webrtc_handler()
    session = handler.get_session(session_id)
    
    if not session or session.organization_id != api_key.organization_id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    candidate = ICECandidate(
        candidate=request.candidate,
        sdp_mid=request.sdp_mid,
        sdp_m_line_index=request.sdp_m_line_index,
    )
    
    success = await handler.add_ice_candidate(session_id, candidate)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add ICE candidate")
    
    return {"status": "added"}


@router.delete("/session/{session_id}")
async def close_session(
    session_id: str,
    api_key: APIKey = Depends(get_api_key),
):
    """Close a WebRTC session."""
    handler = get_webrtc_handler()
    session = handler.get_session(session_id)
    
    if not session or session.organization_id != api_key.organization_id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    await handler.close_session(session_id)
    
    return {"status": "closed"}


@router.get("/sessions")
async def list_sessions(
    api_key: APIKey = Depends(get_api_key),
):
    """List active WebRTC sessions for the organization."""
    handler = get_webrtc_handler()
    sessions = handler.get_active_sessions(organization_id=api_key.organization_id)
    
    return {
        "sessions": [
            {
                "session_id": s.session_id,
                "agent_id": s.agent_id,
                "state": s.state.value,
                "created_at": s.created_at.isoformat(),
            }
            for s in sessions
        ],
        "total": len(sessions),
    }


@router.get("/stats")
async def get_webrtc_stats(
    api_key: APIKey = Depends(get_api_key),
):
    """Get WebRTC service statistics."""
    # Stats are currently global, but in prod we might filter by organization
    handler = get_webrtc_handler()
    return handler.get_stats()


