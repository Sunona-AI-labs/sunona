"""
Sunona Voice AI - Calls API Routes

Endpoints for call logs and history.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from sunona.api.auth import get_api_key, APIKey

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/calls", tags=["Calls"])


# ============================================================
# Models
# ============================================================

class CallLog(BaseModel):
    """Call log entry."""
    call_id: str
    agent_id: str
    direction: str  # inbound, outbound
    phone_number: str
    status: str  # completed, failed, no_answer, busy
    duration_seconds: float
    started_at: str
    ended_at: Optional[str]
    
    # Metadata
    account_id: str
    campaign_id: Optional[str] = None
    
    # Content
    transcript: Optional[str] = None
    summary: Optional[str] = None
    extracted_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Quality
    sentiment: Optional[str] = None
    outcome: Optional[str] = None
    
    # Recordings
    recording_url: Optional[str] = None


class CallListResponse(BaseModel):
    """List of calls response."""
    calls: List[CallLog]
    total: int
    page: int
    page_size: int


class CallStats(BaseModel):
    """Call statistics."""
    total_calls: int
    completed_calls: int
    failed_calls: int
    total_duration_seconds: float
    avg_duration_seconds: float
    success_rate: float


# ============================================================
# In-memory storage (replace with database in production)
# ============================================================

_calls: Dict[str, Dict[str, Any]] = {}


# ============================================================
# Endpoints
# ============================================================

@router.get("", response_model=CallListResponse)
async def list_calls(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    agent_id: Optional[str] = None,
    campaign_id: Optional[str] = None,
    status: Optional[str] = None,
    direction: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    api_key: APIKey = Depends(get_api_key),
) -> CallListResponse:
    """
    List call logs with filtering.
    
    - **agent_id**: Filter by agent
    - **campaign_id**: Filter by campaign
    - **status**: Filter by status (completed, failed, etc.)
    - **direction**: Filter by direction (inbound, outbound)
    - **start_date**: Filter from date (YYYY-MM-DD)
    - **end_date**: Filter to date (YYYY-MM-DD)
    """
    # Filter by account
    calls = [
        c for c in _calls.values()
        if c["account_id"] == api_key.account_id or "admin" in api_key.permissions
    ]
    
    # Apply filters
    if agent_id:
        calls = [c for c in calls if c["agent_id"] == agent_id]
    
    if campaign_id:
        calls = [c for c in calls if c.get("campaign_id") == campaign_id]
    
    if status:
        calls = [c for c in calls if c["status"] == status]
    
    if direction:
        calls = [c for c in calls if c["direction"] == direction]
    
    if start_date:
        calls = [c for c in calls if c["started_at"] >= start_date]
    
    if end_date:
        calls = [c for c in calls if c["started_at"] <= end_date]
    
    # Sort by most recent
    calls.sort(key=lambda c: c["started_at"], reverse=True)
    
    # Paginate
    total = len(calls)
    start = (page - 1) * page_size
    end = start + page_size
    calls = calls[start:end]
    
    return CallListResponse(
        calls=[CallLog(**c) for c in calls],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/stats", response_model=CallStats)
async def get_call_stats(
    agent_id: Optional[str] = None,
    campaign_id: Optional[str] = None,
    days: int = Query(7, ge=1, le=90),
    api_key: APIKey = Depends(get_api_key),
) -> CallStats:
    """
    Get call statistics.
    
    - **agent_id**: Filter by agent
    - **campaign_id**: Filter by campaign
    - **days**: Number of days to include
    """
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    
    # Filter
    calls = [
        c for c in _calls.values()
        if (c["account_id"] == api_key.account_id or "admin" in api_key.permissions)
        and c["started_at"] >= cutoff
    ]
    
    if agent_id:
        calls = [c for c in calls if c["agent_id"] == agent_id]
    
    if campaign_id:
        calls = [c for c in calls if c.get("campaign_id") == campaign_id]
    
    # Calculate stats
    total = len(calls)
    completed = len([c for c in calls if c["status"] == "completed"])
    failed = len([c for c in calls if c["status"] == "failed"])
    total_duration = sum(c.get("duration_seconds", 0) for c in calls)
    
    return CallStats(
        total_calls=total,
        completed_calls=completed,
        failed_calls=failed,
        total_duration_seconds=total_duration,
        avg_duration_seconds=total_duration / total if total > 0 else 0,
        success_rate=completed / total * 100 if total > 0 else 0,
    )


@router.get("/{call_id}", response_model=CallLog)
async def get_call(
    call_id: str,
    api_key: APIKey = Depends(get_api_key),
) -> CallLog:
    """Get call details by ID."""
    call = _calls.get(call_id)
    
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    if call["account_id"] != api_key.account_id and "admin" not in api_key.permissions:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return CallLog(**call)


@router.get("/{call_id}/transcript")
async def get_call_transcript(
    call_id: str,
    api_key: APIKey = Depends(get_api_key),
) -> Dict[str, Any]:
    """Get call transcript."""
    call = _calls.get(call_id)
    
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    if call["account_id"] != api_key.account_id and "admin" not in api_key.permissions:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "call_id": call_id,
        "transcript": call.get("transcript", ""),
        "summary": call.get("summary", ""),
        "extracted_data": call.get("extracted_data", {}),
    }


@router.get("/{call_id}/recording")
async def get_call_recording(
    call_id: str,
    api_key: APIKey = Depends(get_api_key),
) -> Dict[str, Any]:
    """Get call recording URL."""
    call = _calls.get(call_id)
    
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    if call["account_id"] != api_key.account_id and "admin" not in api_key.permissions:
        raise HTTPException(status_code=403, detail="Access denied")
    
    recording_url = call.get("recording_url")
    
    if not recording_url:
        raise HTTPException(status_code=404, detail="Recording not available")
    
    return {
        "call_id": call_id,
        "recording_url": recording_url,
        "duration_seconds": call.get("duration_seconds", 0),
    }
