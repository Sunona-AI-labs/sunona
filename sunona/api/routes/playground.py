"""
Sunona Voice AI - Playground API Routes

REST API endpoints for no-code tools.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Query, Depends
from pydantic import BaseModel

# Import playground components
from sunona.playground import (
    get_agent_builder,
    get_flow_designer,
    get_voice_preview,
    get_knowledge_uploader,
    get_analytics_dashboard,
    get_provider_manager,
    AgentTemplateCategory,
    PreviewMode,
    TimeRange,
    ProviderType,
)

from sunona.api.auth import get_api_key, require_auth
from sunona.multitenancy import APIKey
from sunona.billing.middleware import BillingMiddleware

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/playground", tags=["Playground"])


# =============================================================================
# Request/Response Models
# =============================================================================

class CreateAgentFromTemplateRequest(BaseModel):
    template_id: str
    name: str
    customization: Optional[Dict[str, Any]] = None


class CreateFlowRequest(BaseModel):
    name: str
    description: Optional[str] = ""


class AddFlowNodeRequest(BaseModel):
    node_type: str
    position_x: float = 0
    position_y: float = 0
    properties: Optional[Dict[str, Any]] = None


class AddConnectionRequest(BaseModel):
    source_node_id: str
    target_node_id: str
    source_port: str = "default"
    condition: Optional[str] = None


class PreviewMessageRequest(BaseModel):
    message: str


class AddProviderCredentialRequest(BaseModel):
    provider_id: str
    api_key: str
    name: Optional[str] = ""
    additional_config: Optional[Dict[str, str]] = None


# =============================================================================
# Agent Builder Routes
# =============================================================================

@router.get("/templates")
async def list_templates(
    category: Optional[str] = None,
    api_key: APIKey = Depends(get_api_key),
):
    """List available agent templates."""
    builder = get_agent_builder()
    
    cat = None
    if category:
        try:
            cat = AgentTemplateCategory(category)
        except ValueError:
            pass
    
    templates = await builder.list_templates(category=cat)
    return {"templates": [t.to_dict() for t in templates]}


@router.get("/providers")
async def list_provider_options(
    api_key: APIKey = Depends(get_api_key),
):
    """List available provider options for agents."""
    builder = get_agent_builder()
    options = await builder.list_provider_options()
    return {"providers": [p.to_dict() for p in options]}


@router.post("/agents/build")
async def build_agent_from_template(
    request: CreateAgentFromTemplateRequest,
    api_key: APIKey = Depends(get_api_key),
):
    """Create a new agent builder configuration from a template."""
    builder = get_agent_builder()
    
    try:
        config = await builder.create_from_template(
            template_id=request.template_id,
            organization_id=api_key.organization_id,
            created_by=api_key.id,
        )
        
        if request.customization:
            await builder.update_config(config.id, request.customization)
            
        return {"config": config.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/agents/drafts")
async def list_agent_drafts(
    api_key: APIKey = Depends(get_api_key),
):
    """List agent builder configurations for the organization."""
    builder = get_agent_builder()
    configs = await builder.list_configs(organization_id=api_key.organization_id)
    return {"configs": [c.to_dict() for c in configs]}


@router.get("/agents/drafts/{config_id}")
async def get_agent_draft(
    config_id: str,
    api_key: APIKey = Depends(get_api_key),
):
    """Get a specific agent builder configuration."""
    builder = get_agent_builder()
    config = await builder.get_config(config_id)
    
    if not config or config.organization_id != api_key.organization_id:
        raise HTTPException(status_code=404, detail="Configuration not found")
        
    return {"config": config.to_dict()}


@router.post("/agents/deploy/{config_id}")
async def deploy_agent(
    config_id: str,
    api_key: APIKey = Depends(get_api_key),
):
    """Deploy an agent from a builder configuration."""
    builder = get_agent_builder()
    config = await builder.get_config(config_id)
    
    if not config or config.organization_id != api_key.organization_id:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    try:
        agent_config = await builder.deploy(config_id)
        # In a real system, this would register the agent in the main database
        return {
            "status": "deployed",
            "agent_config": agent_config,
        }
    except Exception as e:
        logger.error(f"Failed to deploy agent: {e}")
        raise HTTPException(status_code=500, detail="Deployment failed")


# =============================================================================
# Flow Designer Routes
# =============================================================================

@router.get("/flows")
async def list_flows(
    api_key: APIKey = Depends(get_api_key),
):
    """List conversational flows for the organization."""
    designer = get_flow_designer()
    flows = await designer.list_flows(organization_id=api_key.organization_id)
    return {"flows": [f.to_dict() for f in flows]}


@router.post("/flows")
async def create_flow(
    request: CreateFlowRequest,
    api_key: APIKey = Depends(get_api_key),
):
    """Create a new conversational flow."""
    designer = get_flow_designer()
    flow = await designer.create_flow(
        name=request.name,
        description=request.description,
        organization_id=api_key.organization_id,
        created_by=api_key.id,
    )
    return {"flow": flow.to_dict()}


@router.get("/flows/{flow_id}")
async def get_flow(
    flow_id: str,
    api_key: APIKey = Depends(get_api_key),
):
    """Get a specific conversational flow."""
    designer = get_flow_designer()
    flow = await designer.get_flow(flow_id)
    
    if not flow or flow.organization_id != api_key.organization_id:
        raise HTTPException(status_code=404, detail="Flow not found")
        
    return {"flow": flow.to_dict()}


@router.post("/flows/{flow_id}/nodes")
async def add_flow_node(
    flow_id: str,
    request: AddFlowNodeRequest,
    api_key: APIKey = Depends(get_api_key),
):
    """Add a node to a flow."""
    designer = get_flow_designer()
    flow = await designer.get_flow(flow_id)
    
    if not flow or flow.organization_id != api_key.organization_id:
        raise HTTPException(status_code=404, detail="Flow not found")
        
    from sunona.playground.flow_designer import NodeType, Position
    
    try:
        node_type = NodeType(request.node_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid node type: {request.node_type}")
    
    position = Position(x=request.position_x, y=request.position_y)
    
    node = await designer.add_node(
        flow_id=flow_id,
        node_type=node_type,
        position=position,
        properties=request.properties,
    )
    
    if not node:
        raise HTTPException(status_code=404, detail="Flow not found")
    
    return {"node": node.to_dict()}


@router.post("/flows/{flow_id}/connections")
async def add_flow_connection(
    flow_id: str,
    request: AddConnectionRequest,
    api_key: APIKey = Depends(get_api_key),
):
    """Connect two nodes in a flow."""
    designer = get_flow_designer()
    flow = await designer.get_flow(flow_id)
    
    if not flow or flow.organization_id != api_key.organization_id:
        raise HTTPException(status_code=404, detail="Flow not found")
        
    connection = await designer.add_connection(
        flow_id=flow_id,
        source_id=request.source_node_id,
        target_id=request.target_node_id,
        source_port=request.source_port,
        condition=request.condition,
    )
    
    if not connection:
        raise HTTPException(status_code=404, detail="Flow or nodes not found")
    
    return {"connection": connection.to_dict()}


@router.post("/flows/{flow_id}/validate")
async def validate_flow(
    flow_id: str,
    api_key: APIKey = Depends(get_api_key),
):
    """Validate a flow for errors."""
    designer = get_flow_designer()
    flow = await designer.get_flow(flow_id)
    
    if not flow or flow.organization_id != api_key.organization_id:
        raise HTTPException(status_code=404, detail="Flow not found")
        
    errors = await designer.validate_flow(flow_id)
    
    return {
        "valid": len(errors) == 0,
        "errors": [e.to_dict() for e in errors],
    }


@router.post("/flows/{flow_id}/publish")
async def publish_flow(
    flow_id: str,
    api_key: APIKey = Depends(get_api_key),
):
    """Publish a flow for use."""
    designer = get_flow_designer()
    flow = await designer.get_flow(flow_id)
    
    if not flow or flow.organization_id != api_key.organization_id:
        raise HTTPException(status_code=404, detail="Flow not found")
        
    success = await designer.publish_flow(flow_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Could not publish flow")
    
    return {"status": "published"}


# =============================================================================
# Voice Preview Routes
# =============================================================================

@router.get("/voices")
async def list_voices(
    provider: Optional[str] = None,
    api_key: APIKey = Depends(get_api_key),
):
    """List available voices for preview."""
    preview = get_voice_preview()
    voices = await preview.list_voices(provider=provider)
    return {"voices": voices}


@router.post("/voices/preview")
async def preview_voice(
    request: PreviewMessageRequest,
    voice_id: str,
    provider: str = "openai",
    api_key: APIKey = Depends(get_api_key),
):
    """Generate audio preview for a voice."""
    # Enforce billing
    billing = BillingMiddleware()
    await billing.check_balance(api_key.organization_id)
    
    preview = get_voice_preview()
    try:
        audio_url = await preview.generate_preview(
            text=request.message,
            voice_id=voice_id,
            provider=provider,
            organization_id=api_key.organization_id,
        )
        return {"audio_url": audio_url}
    except Exception as e:
        logger.error(f"Voice preview failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/preview/start")
async def start_preview(
    agent_id: str,
    mode: str = "text",
    config_override: Optional[Dict[str, Any]] = None,
    api_key: APIKey = Depends(get_api_key),
):
    """Start a voice preview session."""
    # Enforce billing
    billing = BillingMiddleware()
    await billing.check_balance(api_key.organization_id)
    
    preview = get_voice_preview()
    
    try:
        preview_mode = PreviewMode(mode)
    except ValueError:
        preview_mode = PreviewMode.TEXT
    
    session = await preview.start_session(
        agent_id=agent_id,
        mode=preview_mode,
        config_override=config_override or {},
        organization_id=api_key.organization_id,
    )
    
    return {"session": session.to_dict()}


@router.post("/preview/{session_id}/message")
async def send_preview_message(
    session_id: str,
    request: PreviewMessageRequest,
    api_key: APIKey = Depends(get_api_key),
):
    """Send a message in a preview session."""
    preview = get_voice_preview()
    
    response = await preview.send_message(session_id, request.message, organization_id=api_key.organization_id)
    
    if not response:
        raise HTTPException(status_code=404, detail="Session not found or not owned by organization")
    
    return {"message": response.to_dict()}


@router.get("/preview/{session_id}/history")
async def get_preview_history(
    session_id: str,
    api_key: APIKey = Depends(get_api_key),
):
    """Get conversation history for a preview."""
    preview = get_voice_preview()
    history = await preview.get_history(session_id, organization_id=api_key.organization_id)
    
    if history is None: # Assuming get_history returns None if session not found or not owned
        raise HTTPException(status_code=404, detail="Session not found or not owned by organization")
        
    return {"messages": [m.to_dict() for m in history]}


@router.delete("/preview/{session_id}")
async def end_preview(
    session_id: str,
    api_key: APIKey = Depends(get_api_key),
):
    """End a preview session."""
    preview = get_voice_preview()
    success = await preview.end_session(session_id, organization_id=api_key.organization_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found or not owned by organization")
    
    return {"status": "ended"}


# =============================================================================
# Knowledge Upload Routes
# =============================================================================

@router.post("/knowledge/upload")
async def upload_knowledge_file(
    knowledge_base_id: str,
    file: UploadFile = File(...),
    api_key: APIKey = Depends(get_api_key),
):
    """Upload a file to a knowledge base."""
    uploader = get_knowledge_uploader()
    
    content = await file.read()
    try:
        doc = await uploader.upload_file(
            file_data=content,
            filename=file.filename,
            knowledge_base_id=knowledge_base_id,
            organization_id=api_key.organization_id,
            uploaded_by=api_key.id,
        )
        return {"document": doc.to_dict()}
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge/upload-url")
async def upload_from_url(
    url: str,
    knowledge_base_id: str,
    api_key: APIKey = Depends(get_api_key),
):
    """Crawl and upload content from a URL."""
    uploader = get_knowledge_uploader()
    
    doc = await uploader.upload_url(
        url=url,
        knowledge_base_id=knowledge_base_id,
    )
    
    return {"document": doc.to_dict()}


@router.get("/knowledge/{document_id}/status")
async def get_upload_status(document_id: str):
    """Get document processing status."""
    uploader = get_knowledge_uploader()
    doc = await uploader.get_status(document_id)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"document": doc.to_dict()}


@router.get("/knowledge")
async def list_documents(
    knowledge_base_id: Optional[str] = None,
):
    """List uploaded documents."""
    uploader = get_knowledge_uploader()
    docs = await uploader.list_documents(knowledge_base_id=knowledge_base_id)
    
    return {"documents": [d.to_dict() for d in docs]}


@router.delete("/knowledge/{document_id}")
async def delete_document(document_id: str):
    """Delete an uploaded document."""
    uploader = get_knowledge_uploader()
    success = await uploader.delete_document(document_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"status": "deleted"}


# =============================================================================
# Analytics Routes
# =============================================================================

@router.get("/analytics/dashboard")
async def get_analytics_dashboard(
    time_range: str = "last_24h",
    agent_id: Optional[str] = None,
):
    """Get analytics dashboard data."""
    dashboard = get_analytics_dashboard()
    
    try:
        tr = TimeRange(time_range)
    except ValueError:
        tr = TimeRange.LAST_24H
    
    data = await dashboard.get_dashboard(
        time_range=tr,
        agent_id=agent_id,
    )
    
    return data.to_dict()


@router.get("/analytics/realtime")
async def get_realtime_stats():
    """Get real-time statistics."""
    dashboard = get_analytics_dashboard()
    stats = await dashboard.get_real_time_stats()
    return stats


# =============================================================================
# Provider Manager Routes
# =============================================================================

@router.get("/provider-manager/providers")
async def list_available_providers(provider_type: Optional[str] = None):
    """List available providers."""
    manager = get_provider_manager()
    
    pt = None
    if provider_type:
        try:
            pt = ProviderType(provider_type)
        except ValueError:
            pass
    
    providers = await manager.list_providers(provider_type=pt)
    return {"providers": [p.to_dict() for p in providers]}


@router.post("/provider-manager/credentials")
async def add_provider_credential(
    request: AddProviderCredentialRequest,
    organization_id: str = Query(...),
):
    """Add provider credentials."""
    manager = get_provider_manager()
    
    try:
        cred = await manager.add_credential(
            organization_id=organization_id,
            provider_id=request.provider_id,
            api_key=request.api_key,
            name=request.name or "",
            additional_config=request.additional_config,
        )
        return {"credential": cred.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/provider-manager/credentials")
async def list_credentials(organization_id: str):
    """List provider credentials for an organization."""
    manager = get_provider_manager()
    creds = await manager.list_credentials(organization_id)
    return {"credentials": [c.to_dict() for c in creds]}


@router.post("/provider-manager/credentials/{credential_id}/validate")
async def validate_credential(credential_id: str):
    """Validate a credential."""
    manager = get_provider_manager()
    status = await manager.validate_credential(credential_id)
    return {"status": status.value}


@router.post("/provider-manager/credentials/{credential_id}/test")
async def test_provider_connection(credential_id: str):
    """Test provider connectivity."""
    manager = get_provider_manager()
    result = await manager.test_provider(credential_id)
    return result


@router.delete("/provider-manager/credentials/{credential_id}")
async def delete_credential(credential_id: str):
    """Delete a credential."""
    manager = get_provider_manager()
    success = await manager.delete_credential(credential_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Credential not found")
    
    return {"status": "deleted"}
