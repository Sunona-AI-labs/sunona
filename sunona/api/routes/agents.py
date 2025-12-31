"""
Sunona Voice AI - Agent API Routes

CRUD endpoints for managing voice agents.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from sunona.api.auth import get_api_key, APIKey

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agents", tags=["Agents"])


# ============================================================
# Models
# ============================================================

class AgentConfig(BaseModel):
    """Agent configuration."""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = ""
    
    # LLM settings
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    system_prompt: Optional[str] = None
    temperature: float = Field(0.7, ge=0, le=2)
    max_tokens: int = Field(1024, ge=1, le=16384)
    
    # STT settings
    stt_provider: str = "deepgram"
    language: str = "en"
    
    # TTS settings
    tts_provider: str = "elevenlabs"
    voice_id: Optional[str] = None
    speaking_rate: float = Field(1.0, ge=0.5, le=2.0)
    
    # Template
    template_name: Optional[str] = None
    template_config: Dict[str, Any] = Field(default_factory=dict)
    
    # Tools
    enabled_tools: List[str] = Field(default_factory=list)
    
    class Config:
        extra = "allow"


class AgentResponse(BaseModel):
    """Agent response model."""
    agent_id: str
    name: str
    description: str
    config: AgentConfig
    account_id: str
    created_at: str
    updated_at: str
    is_active: bool


class AgentListResponse(BaseModel):
    """List of agents response."""
    agents: List[AgentResponse]
    total: int
    page: int
    page_size: int


# ============================================================
# In-memory storage (replace with database in production)
# ============================================================

_agents: Dict[str, Dict[str, Any]] = {}
_agent_counter = 0


def _get_next_id() -> str:
    global _agent_counter
    _agent_counter += 1
    return f"agent_{_agent_counter:06d}"


# ============================================================
# Endpoints
# ============================================================

@router.post("", response_model=AgentResponse, status_code=201)
async def create_agent(
    config: AgentConfig,
    api_key: APIKey = Depends(get_api_key),
) -> AgentResponse:
    """
    Create a new voice agent.
    
    - **name**: Agent name
    - **llm_provider**: LLM provider (openai, anthropic, etc.)
    - **stt_provider**: STT provider (deepgram, whisper, etc.)
    - **tts_provider**: TTS provider (elevenlabs, openai, etc.)
    """
    agent_id = _get_next_id()
    now = datetime.now().isoformat()
    
    agent = {
        "agent_id": agent_id,
        "name": config.name,
        "description": config.description,
        "config": config.dict(),
        "account_id": api_key.account_id,
        "created_at": now,
        "updated_at": now,
        "is_active": True,
    }
    
    _agents[agent_id] = agent
    logger.info(f"Created agent: {agent_id}")
    
    return AgentResponse(**agent)


@router.get("", response_model=AgentListResponse)
async def list_agents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    active_only: bool = True,
    api_key: APIKey = Depends(get_api_key),
) -> AgentListResponse:
    """List all agents for the account."""
    # Filter by account
    agents = [
        a for a in _agents.values()
        if a["account_id"] == api_key.account_id or "admin" in api_key.permissions
    ]
    
    # Filter active
    if active_only:
        agents = [a for a in agents if a["is_active"]]
    
    # Paginate
    total = len(agents)
    start = (page - 1) * page_size
    end = start + page_size
    agents = agents[start:end]
    
    return AgentListResponse(
        agents=[AgentResponse(**a) for a in agents],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    api_key: APIKey = Depends(get_api_key),
) -> AgentResponse:
    """Get agent by ID."""
    agent = _agents.get(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Check permission
    if agent["account_id"] != api_key.account_id and "admin" not in api_key.permissions:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return AgentResponse(**agent)


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    config: AgentConfig,
    api_key: APIKey = Depends(get_api_key),
) -> AgentResponse:
    """Update an agent."""
    agent = _agents.get(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if agent["account_id"] != api_key.account_id and "admin" not in api_key.permissions:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update
    agent["name"] = config.name
    agent["description"] = config.description
    agent["config"] = config.dict()
    agent["updated_at"] = datetime.now().isoformat()
    
    logger.info(f"Updated agent: {agent_id}")
    
    return AgentResponse(**agent)


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(
    agent_id: str,
    api_key: APIKey = Depends(get_api_key),
) -> None:
    """Delete (deactivate) an agent."""
    agent = _agents.get(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if agent["account_id"] != api_key.account_id and "admin" not in api_key.permissions:
        raise HTTPException(status_code=403, detail="Access denied")
    
    agent["is_active"] = False
    agent["updated_at"] = datetime.now().isoformat()
    
    logger.info(f"Deleted agent: {agent_id}")


@router.post("/{agent_id}/duplicate", response_model=AgentResponse, status_code=201)
async def duplicate_agent(
    agent_id: str,
    new_name: Optional[str] = None,
    api_key: APIKey = Depends(get_api_key),
) -> AgentResponse:
    """Duplicate an existing agent."""
    agent = _agents.get(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if agent["account_id"] != api_key.account_id and "admin" not in api_key.permissions:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Create copy
    new_id = _get_next_id()
    now = datetime.now().isoformat()
    
    new_agent = {
        **agent,
        "agent_id": new_id,
        "name": new_name or f"{agent['name']} (Copy)",
        "created_at": now,
        "updated_at": now,
    }
    
    _agents[new_id] = new_agent
    logger.info(f"Duplicated agent {agent_id} to {new_id}")
    
    return AgentResponse(**new_agent)
