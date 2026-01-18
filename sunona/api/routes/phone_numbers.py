"""
Sunona Voice AI - Phone Numbers API Routes
REST API for managing phone numbers with Twilio integration.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from sunona.api.auth import get_api_key, APIKey

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/phone-numbers", tags=["Phone Numbers"])


class NumberType(str, Enum):
    LOCAL = "local"
    TOLL_FREE = "toll_free"
    MOBILE = "mobile"


class NumberStatus(str, Enum):
    ACTIVE = "active"
    PENDING = "pending"
    RELEASED = "released"


class PhoneNumberConfig(BaseModel):
    friendly_name: Optional[str] = None
    agent_id: Optional[str] = None
    voice_url: Optional[str] = None


class ProvisionNumberRequest(BaseModel):
    country_code: str = "US"
    area_code: Optional[str] = None
    number_type: NumberType = NumberType.LOCAL
    config: Optional[PhoneNumberConfig] = None


class PhoneNumberResponse(BaseModel):
    number_id: str
    phone_number: str
    friendly_name: Optional[str] = None
    country_code: str
    number_type: str
    status: str
    capabilities: List[str]
    agent_id: Optional[str] = None
    monthly_cost: float = 1.00
    account_id: str
    created_at: str
    updated_at: str


# In-memory storage
_phone_numbers: Dict[str, Dict] = {
    "pn_000001": {
        "number_id": "pn_000001",
        "phone_number": "+14155551234",
        "friendly_name": "Main Support Line",
        "country_code": "US",
        "number_type": "local",
        "status": "active",
        "capabilities": ["voice", "sms"],
        "agent_id": "agent_001",
        "monthly_cost": 1.00,
        "account_id": "demo_account",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
    },
}
_counter = 1


@router.get("")
async def list_phone_numbers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    api_key: APIKey = Depends(get_api_key),
) -> Dict[str, Any]:
    numbers = list(_phone_numbers.values())
    total = len(numbers)
    start = (page - 1) * page_size
    return {"numbers": numbers[start:start+page_size], "total": total, "page": page}


@router.get("/available")
async def search_available(
    country_code: str = "US",
    area_code: Optional[str] = None,
    api_key: APIKey = Depends(get_api_key),
) -> List[Dict]:
    area = area_code or "415"
    return [{"phone_number": f"+1{area}555{1000+i}", "monthly_cost": 1.00} for i in range(10)]


@router.get("/{number_id}")
async def get_phone_number(number_id: str, api_key: APIKey = Depends(get_api_key)):
    number = _phone_numbers.get(number_id)
    if not number:
        raise HTTPException(status_code=404, detail="Number not found")
    return number


@router.post("", status_code=201)
async def provision_number(request: ProvisionNumberRequest, api_key: APIKey = Depends(get_api_key)):
    global _counter
    _counter += 1
    number_id = f"pn_{_counter:06d}"
    now = datetime.now().isoformat()
    area = request.area_code or "415"
    import random
    phone = f"+1{area}555{random.randint(1000,9999)}"
    
    number = {
        "number_id": number_id,
        "phone_number": phone,
        "friendly_name": request.config.friendly_name if request.config else None,
        "country_code": request.country_code,
        "number_type": request.number_type.value,
        "status": "active",
        "capabilities": ["voice", "sms"],
        "agent_id": request.config.agent_id if request.config else None,
        "monthly_cost": 1.00,
        "account_id": api_key.account_id,
        "created_at": now,
        "updated_at": now,
    }
    _phone_numbers[number_id] = number
    return number


@router.put("/{number_id}")
async def update_number(number_id: str, config: PhoneNumberConfig, api_key: APIKey = Depends(get_api_key)):
    number = _phone_numbers.get(number_id)
    if not number:
        raise HTTPException(status_code=404, detail="Number not found")
    if config.friendly_name:
        number["friendly_name"] = config.friendly_name
    if config.agent_id:
        number["agent_id"] = config.agent_id
    number["updated_at"] = datetime.now().isoformat()
    return number


@router.post("/{number_id}/assign")
async def assign_agent(number_id: str, agent_id: str, api_key: APIKey = Depends(get_api_key)):
    number = _phone_numbers.get(number_id)
    if not number:
        raise HTTPException(status_code=404, detail="Number not found")
    number["agent_id"] = agent_id
    return {"number_id": number_id, "agent_id": agent_id, "status": "assigned"}


@router.delete("/{number_id}", status_code=204)
async def release_number(number_id: str, api_key: APIKey = Depends(get_api_key)):
    if number_id in _phone_numbers:
        _phone_numbers[number_id]["status"] = "released"


@router.get("/{number_id}/stats")
async def get_number_stats(number_id: str, api_key: APIKey = Depends(get_api_key)):
    number = _phone_numbers.get(number_id)
    if not number:
        raise HTTPException(status_code=404, detail="Number not found")
    return {
        "number_id": number_id,
        "total_calls": 150,
        "inbound_calls": 100,
        "outbound_calls": 50,
        "total_minutes": 450.5,
    }
