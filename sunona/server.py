"""
Sunona Voice AI - FastAPI Server

Production-ready REST API server for managing voice AI agents.

Features:
- Agent CRUD operations
- WebSocket real-time chat
- Playground API (no-code tools)
- WebRTC browser calling
- Multi-tenant organizations
- Rate limiting
- Structured logging
- Health checks
"""

import os
import uuid
import json
import asyncio
import logging
import time
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request, Depends, APIRouter
from sunona.api.auth import get_api_key, require_auth, require_permission
try:
    from sunona.multitenancy import APIKey
except ImportError:
    APIKey = Any
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from sunona.models import CreateAgentRequest, AgentResponse
from sunona.assistant import Assistant
from sunona.helpers.logger import setup_logging
from sunona.core.storage import get_agent_store

# Import production infrastructure
from sunona.core import (
    setup_logging as setup_structured_logging,
    get_logger,
    set_request_context,
    clear_request_context,
    HealthCheck,
    HealthStatus,
    ComponentHealth,
    SunonaError,
    RateLimitError,
    SlidingWindowRateLimiter,
)
try:
    from sunona.billing.middleware import BillingMiddleware
except ImportError:
    BillingMiddleware = None

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

# Persistent agent storage
agents_store = get_agent_store()

# Production components
from sunona.core.websocket_manager import get_websocket_manager
ws_manager = get_websocket_manager()

# Production components
health_check = HealthCheck()
rate_limiter = SlidingWindowRateLimiter(
    limit=100,
    window_seconds=60,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    logger.info("Sunona Voice AI Server starting...")
    
    # Connect to persistent storage
    await agents_store.connect()
    
    # Register health checks - must return ComponentHealth
    async def check_agents_store():
        return ComponentHealth(
            name="agents_store",
            status=HealthStatus.HEALTHY,
            message=f"{len(agents_store)} agents loaded",
        )
    
    health_check.register("agents_store", check_agents_store)
    
    # Start background tasks
    await ws_manager.start()
    
    yield
    
    logger.info("Sunona Voice AI Server shutting down...")
    
    # Graceful shutdown
    await ws_manager.stop()


# Create FastAPI app
app = FastAPI(
    title="Sunona Voice AI",
    description="End-to-end Voice AI Platform API",
    version="0.2.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optional Billing Middleware
if BillingMiddleware:
    app.add_middleware(BillingMiddleware)


# =============================================================================
# Production Middleware
# =============================================================================

@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Log all requests with timing and correlation IDs."""
    request_id = str(uuid.uuid4())[:8]
    start_time = time.perf_counter()
    
    # Set context for structured logging
    set_request_context(request_id=request_id)
    
    logger.info(f"[{request_id}] {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} "
            f"-> {response.status_code} ({duration_ms:.1f}ms)"
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.error(
            f"[{request_id}] {request.method} {request.url.path} "
            f"-> ERROR: {e} ({duration_ms:.1f}ms)"
        )
        raise
    finally:
        clear_request_context()


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limit requests per IP."""
    # Skip rate limiting for health checks
    if request.url.path in ["/health", "/health/liveness", "/health/readiness"]:
        return await call_next(request)
    
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    
    # Check rate limit - check() returns RateLimitResult
    result = await rate_limiter.check(client_ip)
    
    if not result.allowed:
        return JSONResponse(
            status_code=429,
            content={
                "error": "rate_limit_exceeded",
                "message": "Too many requests. Please slow down.",
                "retry_after": result.retry_after or 60,
            },
        )
    
    return await call_next(request)


@app.exception_handler(SunonaError)
async def sunona_error_handler(request: Request, exc: SunonaError):
    """Handle Sunona-specific errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": str(exc),
            "details": exc.details,
        },
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.exception(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "An unexpected error occurred",
        },
    )


# =============================================================================
# Health Check Endpoints
# =============================================================================

@app.get("/health")
async def health_check_endpoint():
    """Health check endpoint."""
    result = await health_check.check_all()
    
    status_code = 200 if result.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED] else 503
    
    return JSONResponse(
        status_code=status_code,
        content=result.to_dict(),
    )


@app.get("/health/liveness")
async def liveness_probe():
    """Kubernetes liveness probe."""
    return {"status": "alive"}


@app.get("/health/readiness")
async def readiness_probe():
    """Kubernetes readiness probe."""
    result = await health_check.check()
    
    if result["status"] == "unhealthy":
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready"},
        )
    
    return {"status": "ready"}


@app.get("/")
async def root():
    """Root endpoint with API documentation links."""
    return {
        "name": "Sunona Voice AI",
        "version": "0.2.0",
        "docs": "/docs",
        "health": "/health",
        "api": {
            "agents": "/agent",
            "playground": "/playground",
            "webrtc": "/webrtc",
            "organizations": "/organizations",
        },
    }



# =============================================================================
# Agent CRUD Endpoints (Protected)
# =============================================================================

router_agents = APIRouter(prefix="/agent", tags=["Agents"])

@router_agents.get("/{agent_id}")
async def get_agent(
    agent_id: str,
    api_key: APIKey = Depends(get_api_key),
):
    """Get an agent by ID."""
    agent_data = await agents_store.get(agent_id)
    if not agent_data:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    if agent_data.get("organization_id") != api_key.organization_id:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {
        "agent_id": agent_id,
        "data": agent_data,
    }


@router_agents.post("", response_model=AgentResponse)
async def create_agent(
    request: CreateAgentRequest,
    api_key: APIKey = Depends(get_api_key),
):
    """Create a new agent."""
    agent_id = str(uuid.uuid4())
    
    agent_data = {
        "agent_config": request.agent_config.model_dump(),
        "agent_prompts": request.agent_prompts,
        "organization_id": api_key.organization_id,
        "created_by": api_key.id,
    }
    
    await agents_store.set(agent_id, agent_data)
    
    logger.info(f"Created agent: {agent_id} (Org: {api_key.organization_id})")
    
    return AgentResponse(agent_id=agent_id, state="created")


@router_agents.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    request: CreateAgentRequest,
    api_key: APIKey = Depends(get_api_key),
):
    """Update an existing agent."""
    agent_data = await agents_store.get(agent_id)
    if not agent_data:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    if agent_data.get("organization_id") != api_key.organization_id:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    agent_data.update({
        "agent_config": request.agent_config.model_dump(),
        "agent_prompts": request.agent_prompts,
        "updated_at": time.time(),
    })
    
    await agents_store.set(agent_id, agent_data)
    
    logger.info(f"Updated agent: {agent_id}")
    
    return AgentResponse(agent_id=agent_id, state="updated")


@router_agents.delete("/{agent_id}", response_model=AgentResponse)
async def delete_agent(
    agent_id: str,
    api_key: APIKey = Depends(get_api_key),
):
    """Delete an agent."""
    agent_data = await agents_store.get(agent_id)
    if not agent_data:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    if agent_data.get("organization_id") != api_key.organization_id:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    await agents_store.delete(agent_id)
    
    logger.info(f"Deleted agent: {agent_id}")
    
    return AgentResponse(agent_id=agent_id, state="deleted")


@app.get("/agents")
async def list_agents(
    api_key: APIKey = Depends(get_api_key),
):
    """List all agents for the organization."""
    org_agents = await agents_store.list_all(organization_id=api_key.organization_id)
    return {"agents": org_agents}

# Include the agents router
app.include_router(router_agents)



# =============================================================================
# WebSocket Chat Endpoint
# =============================================================================

@app.websocket("/chat/{agent_id}")
async def websocket_chat(websocket: WebSocket, agent_id: str):
    """WebSocket endpoint for real-time chat with an agent."""
    # Note: Extracting API Key from WebSocket subprotocols or query params would be better in prod
    # For now, we'll use the organization_id from the stored agent as a proxy if no better auth
    
    # Get agent config
    agent_data = await agents_store.get(agent_id)
    if not agent_data:
        await websocket.accept()
        await websocket.send_json({"error": f"Agent {agent_id} not found"})
        await websocket.close()
        return
    
    organization_id = agent_data.get("organization_id")
    user_id = agent_data.get("created_by")
    
    # Enforce Billing
    billing_middleware = BillingMiddleware()
    if organization_id:
        try:
            await billing_middleware.check_balance(organization_id)
        except Exception as e:
            await websocket.accept()
            await websocket.send_json({
                "type": "error",
                "message": "Insufficient balance to start conversation. Please top up your account.",
            })
            await websocket.close()
            return

    # Use professional WebSocketManager
    connection = await ws_manager.connect(
        websocket, 
        user_id=user_id,
        agent_id=agent_id,
        metadata={"source": "direct_chat"}
    )
    
    agent_config = agent_data["agent_config"]
    agent_prompts = agent_data.get("agent_prompts", {})
    
    # Create assistant
    assistant = Assistant(
        name=agent_config.get("agent_name", "sunona_agent"),
        welcome_message=agent_config.get("agent_welcome_message", ""),
        organization_id=organization_id,
        user_id=user_id
    )
    
    # Add tasks from config
    for i, task_config in enumerate(agent_config.get("tasks", [])):
        task_id = f"task_{i + 1}"
        prompts = agent_prompts.get(task_id, {})
        assistant.tasks.append(task_config)
        if prompts:
            assistant.prompts[task_id] = prompts
    
    # Send welcome message
    welcome = agent_config.get("agent_welcome_message", "")
    if welcome:
        await ws_manager.send_json(connection, {
            "type": "welcome",
            "message": welcome,
        })
    
    try:
        # Start assistant execution in background
        async def run_assistant():
            try:
                async for result in assistant.execute():
                    await ws_manager.send_json(connection, result)
            except Exception as e:
                logger.error(f"Assistant execution error for {connection.connection_id}: {e}")
        
        assistant_task = asyncio.create_task(run_assistant())
        
        # Handle incoming messages via manager
        async for message in ws_manager.receive_messages(connection):
            if isinstance(message, dict):
                text = message.get("text", "")
                if text:
                    await assistant.send_input(text)
            elif isinstance(message, bytes):
                await assistant.send_input(message)
                
        # Cleanup
        await assistant.end_conversation()
        assistant_task.cancel()
        try:
            await assistant_task
        except asyncio.CancelledError:
            pass
            
    finally:
        await ws_manager.disconnect(connection)


# =============================================================================
# Mount API Routers
# =============================================================================

# Import and mount new API routers
try:
    from sunona.api.routes.playground import router as playground_router
    app.include_router(playground_router)
    logger.info("Mounted /playground routes")
except ImportError as e:
    logger.warning(f"Playground routes not available: {e}")

try:
    from sunona.api.routes.webrtc_routes import router as webrtc_router
    app.include_router(webrtc_router)
    logger.info("Mounted /webrtc routes")
except ImportError as e:
    logger.warning(f"WebRTC routes not available: {e}")

try:
    from sunona.api.routes.organizations import router as org_router
    app.include_router(org_router)
    logger.info("Mounted /organizations routes")
except ImportError as e:
    logger.warning(f"Organizations routes not available: {e}")


# =============================================================================
# Running the Server
# =============================================================================

def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the Sunona server."""
    import uvicorn
    uvicorn.run(
        "sunona.server:app",
        host=host,
        port=port,
        reload=reload,
    )


if __name__ == "__main__":
    run_server(
        host=os.getenv("SUNONA_HOST", "0.0.0.0"),
        port=int(os.getenv("SUNONA_PORT", "8000")),
        reload=os.getenv("SUNONA_DEBUG", "false").lower() == "true",
    )

