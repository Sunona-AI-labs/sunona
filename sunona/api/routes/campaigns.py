"""
Sunona Voice AI - Campaigns API Routes

REST API endpoints for managing outbound calling campaigns.
Campaigns allow batch calling with scheduling, targeting, and analytics.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from pydantic import BaseModel, Field

from sunona.api.auth import get_api_key, APIKey
from sunona.core.cache import cache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


# ============================================================
# Enums
# ============================================================

class CampaignStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CampaignType(str, Enum):
    OUTBOUND = "outbound"
    FOLLOW_UP = "follow_up"
    REMINDER = "reminder"
    SURVEY = "survey"


# ============================================================
# Models
# ============================================================

class CampaignContact(BaseModel):
    """Contact in a campaign."""
    phone: str
    name: Optional[str] = None
    email: Optional[str] = None
    custom_data: Dict[str, Any] = Field(default_factory=dict)


class CampaignSchedule(BaseModel):
    """Campaign scheduling configuration."""
    start_date: str
    end_date: Optional[str] = None
    start_time: str = "09:00"  # Daily start time
    end_time: str = "18:00"    # Daily end time
    timezone: str = "UTC"
    days_of_week: List[int] = Field(default=[0, 1, 2, 3, 4])  # Mon-Fri
    max_concurrent_calls: int = Field(default=5, ge=1, le=50)
    calls_per_minute: int = Field(default=10, ge=1, le=100)


class CreateCampaignRequest(BaseModel):
    """Request to create a campaign."""
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    campaign_type: CampaignType = CampaignType.OUTBOUND
    agent_id: str
    schedule: Optional[CampaignSchedule] = None
    retry_config: Dict[str, Any] = Field(default_factory=lambda: {
        "max_retries": 2,
        "retry_delay_minutes": 60,
        "retry_on": ["no_answer", "busy"]
    })


class CampaignResponse(BaseModel):
    """Campaign response model."""
    campaign_id: str
    name: str
    description: str
    campaign_type: CampaignType
    status: CampaignStatus
    agent_id: str
    agent_name: Optional[str] = None
    schedule: Optional[CampaignSchedule] = None
    
    # Stats
    total_contacts: int = 0
    completed_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    pending_calls: int = 0
    
    # Metadata
    account_id: str
    created_at: str
    updated_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class CampaignListResponse(BaseModel):
    """List of campaigns response."""
    campaigns: List[CampaignResponse]
    total: int
    page: int
    page_size: int


class CampaignStats(BaseModel):
    """Campaign statistics."""
    total_calls: int
    completed_calls: int
    successful_calls: int
    failed_calls: int
    avg_call_duration: float
    success_rate: float
    cost_total: float
    calls_by_outcome: Dict[str, int]


# ============================================================
# In-memory storage (replace with database in production)
# ============================================================

_campaigns: Dict[str, Dict[str, Any]] = {}
_campaign_contacts: Dict[str, List[Dict[str, Any]]] = {}
_campaign_counter = 0


def _get_next_id() -> str:
    global _campaign_counter
    _campaign_counter += 1
    return f"camp_{_campaign_counter:06d}"


# ============================================================
# Campaign CRUD Endpoints
# ============================================================

@router.post("", response_model=CampaignResponse, status_code=201)
async def create_campaign(
    request: CreateCampaignRequest,
    api_key: APIKey = Depends(get_api_key),
) -> CampaignResponse:
    """
    Create a new campaign.
    
    Campaigns start in DRAFT status until contacts are added and started.
    """
    campaign_id = _get_next_id()
    now = datetime.now().isoformat()
    
    campaign = {
        "campaign_id": campaign_id,
        "name": request.name,
        "description": request.description,
        "campaign_type": request.campaign_type.value,
        "status": CampaignStatus.DRAFT.value,
        "agent_id": request.agent_id,
        "schedule": request.schedule.dict() if request.schedule else None,
        "retry_config": request.retry_config,
        "total_contacts": 0,
        "completed_calls": 0,
        "successful_calls": 0,
        "failed_calls": 0,
        "pending_calls": 0,
        "account_id": api_key.account_id,
        "created_at": now,
        "updated_at": now,
        "started_at": None,
        "completed_at": None,
    }
    
    _campaigns[campaign_id] = campaign
    _campaign_contacts[campaign_id] = []
    
    logger.info(f"Created campaign: {campaign_id}")
    
    return CampaignResponse(**campaign)


@router.get("", response_model=CampaignListResponse)
async def list_campaigns(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[CampaignStatus] = None,
    api_key: APIKey = Depends(get_api_key),
) -> CampaignListResponse:
    """List all campaigns for the account."""
    # Filter by account
    campaigns = [
        c for c in _campaigns.values()
        if c["account_id"] == api_key.account_id or "admin" in api_key.permissions
    ]
    
    # Filter by status
    if status:
        campaigns = [c for c in campaigns if c["status"] == status.value]
    
    # Sort by most recent
    campaigns.sort(key=lambda c: c["created_at"], reverse=True)
    
    # Paginate
    total = len(campaigns)
    start = (page - 1) * page_size
    end = start + page_size
    campaigns = campaigns[start:end]
    
    return CampaignListResponse(
        campaigns=[CampaignResponse(**c) for c in campaigns],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    api_key: APIKey = Depends(get_api_key),
) -> CampaignResponse:
    """Get campaign by ID."""
    campaign = _campaigns.get(campaign_id)
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign["account_id"] != api_key.account_id and "admin" not in api_key.permissions:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return CampaignResponse(**campaign)


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    request: CreateCampaignRequest,
    api_key: APIKey = Depends(get_api_key),
) -> CampaignResponse:
    """Update a campaign (only in DRAFT status)."""
    campaign = _campaigns.get(campaign_id)
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign["account_id"] != api_key.account_id and "admin" not in api_key.permissions:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if campaign["status"] != CampaignStatus.DRAFT.value:
        raise HTTPException(
            status_code=400, 
            detail="Can only update campaigns in DRAFT status"
        )
    
    # Update
    campaign["name"] = request.name
    campaign["description"] = request.description
    campaign["campaign_type"] = request.campaign_type.value
    campaign["agent_id"] = request.agent_id
    campaign["schedule"] = request.schedule.dict() if request.schedule else None
    campaign["retry_config"] = request.retry_config
    campaign["updated_at"] = datetime.now().isoformat()
    
    logger.info(f"Updated campaign: {campaign_id}")
    
    return CampaignResponse(**campaign)


@router.delete("/{campaign_id}", status_code=204)
async def delete_campaign(
    campaign_id: str,
    api_key: APIKey = Depends(get_api_key),
) -> None:
    """Delete a campaign (only if not running)."""
    campaign = _campaigns.get(campaign_id)
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign["account_id"] != api_key.account_id and "admin" not in api_key.permissions:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if campaign["status"] == CampaignStatus.RUNNING.value:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete a running campaign. Pause or stop it first."
        )
    
    del _campaigns[campaign_id]
    if campaign_id in _campaign_contacts:
        del _campaign_contacts[campaign_id]
    
    logger.info(f"Deleted campaign: {campaign_id}")


# ============================================================
# Contact Management
# ============================================================

@router.post("/{campaign_id}/contacts", status_code=201)
async def add_contacts(
    campaign_id: str,
    contacts: List[CampaignContact],
    api_key: APIKey = Depends(get_api_key),
) -> Dict[str, Any]:
    """Add contacts to a campaign."""
    campaign = _campaigns.get(campaign_id)
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign["account_id"] != api_key.account_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if campaign["status"] not in [CampaignStatus.DRAFT.value, CampaignStatus.PAUSED.value]:
        raise HTTPException(
            status_code=400,
            detail="Can only add contacts to DRAFT or PAUSED campaigns"
        )
    
    # Add contacts
    added = 0
    for contact in contacts:
        _campaign_contacts[campaign_id].append({
            **contact.dict(),
            "status": "pending",
            "attempts": 0,
            "last_attempt": None,
            "outcome": None,
        })
        added += 1
    
    # Update campaign stats
    campaign["total_contacts"] = len(_campaign_contacts[campaign_id])
    campaign["pending_calls"] = len([
        c for c in _campaign_contacts[campaign_id] 
        if c["status"] == "pending"
    ])
    campaign["updated_at"] = datetime.now().isoformat()
    
    return {
        "added": added,
        "total_contacts": campaign["total_contacts"],
    }


@router.post("/{campaign_id}/contacts/upload")
async def upload_contacts_csv(
    campaign_id: str,
    file: UploadFile = File(...),
    api_key: APIKey = Depends(get_api_key),
) -> Dict[str, Any]:
    """Upload contacts from CSV file."""
    campaign = _campaigns.get(campaign_id)
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign["account_id"] != api_key.account_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # In production, parse CSV and add contacts
    # For now, return mock response
    return {
        "message": "CSV upload processing",
        "filename": file.filename,
        "status": "queued",
    }


@router.get("/{campaign_id}/contacts")
async def list_contacts(
    campaign_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    status: Optional[str] = None,
    api_key: APIKey = Depends(get_api_key),
) -> Dict[str, Any]:
    """List contacts in a campaign."""
    campaign = _campaigns.get(campaign_id)
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign["account_id"] != api_key.account_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    contacts = _campaign_contacts.get(campaign_id, [])
    
    if status:
        contacts = [c for c in contacts if c["status"] == status]
    
    total = len(contacts)
    start = (page - 1) * page_size
    end = start + page_size
    
    return {
        "contacts": contacts[start:end],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


# ============================================================
# Campaign Actions
# ============================================================

@router.post("/{campaign_id}/start")
async def start_campaign(
    campaign_id: str,
    api_key: APIKey = Depends(get_api_key),
) -> Dict[str, Any]:
    """Start a campaign."""
    campaign = _campaigns.get(campaign_id)
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign["account_id"] != api_key.account_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if campaign["status"] not in [CampaignStatus.DRAFT.value, CampaignStatus.PAUSED.value]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot start campaign with status: {campaign['status']}"
        )
    
    if campaign["total_contacts"] == 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot start campaign without contacts"
        )
    
    campaign["status"] = CampaignStatus.RUNNING.value
    campaign["started_at"] = datetime.now().isoformat()
    campaign["updated_at"] = datetime.now().isoformat()
    
    logger.info(f"Started campaign: {campaign_id}")
    
    return {
        "campaign_id": campaign_id,
        "status": "running",
        "message": "Campaign started successfully",
    }


@router.post("/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: str,
    api_key: APIKey = Depends(get_api_key),
) -> Dict[str, Any]:
    """Pause a running campaign."""
    campaign = _campaigns.get(campaign_id)
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign["account_id"] != api_key.account_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if campaign["status"] != CampaignStatus.RUNNING.value:
        raise HTTPException(
            status_code=400,
            detail="Can only pause running campaigns"
        )
    
    campaign["status"] = CampaignStatus.PAUSED.value
    campaign["updated_at"] = datetime.now().isoformat()
    
    logger.info(f"Paused campaign: {campaign_id}")
    
    return {
        "campaign_id": campaign_id,
        "status": "paused",
        "message": "Campaign paused",
    }


@router.post("/{campaign_id}/stop")
async def stop_campaign(
    campaign_id: str,
    api_key: APIKey = Depends(get_api_key),
) -> Dict[str, Any]:
    """Stop and complete a campaign."""
    campaign = _campaigns.get(campaign_id)
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign["account_id"] != api_key.account_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if campaign["status"] not in [CampaignStatus.RUNNING.value, CampaignStatus.PAUSED.value]:
        raise HTTPException(
            status_code=400,
            detail="Can only stop running or paused campaigns"
        )
    
    campaign["status"] = CampaignStatus.COMPLETED.value
    campaign["completed_at"] = datetime.now().isoformat()
    campaign["updated_at"] = datetime.now().isoformat()
    
    logger.info(f"Stopped campaign: {campaign_id}")
    
    return {
        "campaign_id": campaign_id,
        "status": "completed",
        "message": "Campaign stopped and marked as completed",
    }


# ============================================================
# Campaign Analytics
# ============================================================

@router.get("/{campaign_id}/stats", response_model=CampaignStats)
async def get_campaign_stats(
    campaign_id: str,
    api_key: APIKey = Depends(get_api_key),
) -> CampaignStats:
    """Get campaign statistics."""
    campaign = _campaigns.get(campaign_id)
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign["account_id"] != api_key.account_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Calculate stats from contacts
    contacts = _campaign_contacts.get(campaign_id, [])
    completed = [c for c in contacts if c["status"] == "completed"]
    
    total = len(contacts)
    successful = len([c for c in completed if c.get("outcome") == "success"])
    
    return CampaignStats(
        total_calls=campaign["total_contacts"],
        completed_calls=campaign["completed_calls"],
        successful_calls=campaign["successful_calls"],
        failed_calls=campaign["failed_calls"],
        avg_call_duration=180.0,  # Mock
        success_rate=(successful / total * 100) if total > 0 else 0,
        cost_total=campaign["completed_calls"] * 0.15,  # Mock
        calls_by_outcome={
            "success": successful,
            "no_answer": campaign["failed_calls"],
            "voicemail": 0,
            "callback": 0,
        },
    )


@router.post("/{campaign_id}/duplicate", response_model=CampaignResponse, status_code=201)
async def duplicate_campaign(
    campaign_id: str,
    new_name: Optional[str] = None,
    api_key: APIKey = Depends(get_api_key),
) -> CampaignResponse:
    """Duplicate an existing campaign."""
    campaign = _campaigns.get(campaign_id)
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign["account_id"] != api_key.account_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    new_id = _get_next_id()
    now = datetime.now().isoformat()
    
    new_campaign = {
        **campaign,
        "campaign_id": new_id,
        "name": new_name or f"{campaign['name']} (Copy)",
        "status": CampaignStatus.DRAFT.value,
        "total_contacts": 0,
        "completed_calls": 0,
        "successful_calls": 0,
        "failed_calls": 0,
        "pending_calls": 0,
        "created_at": now,
        "updated_at": now,
        "started_at": None,
        "completed_at": None,
    }
    
    _campaigns[new_id] = new_campaign
    _campaign_contacts[new_id] = []
    
    logger.info(f"Duplicated campaign {campaign_id} to {new_id}")
    
    return CampaignResponse(**new_campaign)
