import os
import logging
from typing import Any, Callable, Dict, Optional, List
from functools import wraps

from fastapi import HTTPException, Header, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

try:
    from sunona.multitenancy import (
        get_tenant_manager,
        APIKey,
        Permission,
        Organization,
    )
    HAS_MULTITENANCY = True
except ImportError:
    HAS_MULTITENANCY = False
    # Stub classes for standalone mode
    class APIKey:
        id = "master"
        organization_id = "default"
        def has_permission(self, perm): return True
    class Permission(str): pass
    Organization = Any
    def get_tenant_manager(): return None

from sunona.core import AuthenticationError, SunonaError

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


async def get_api_key(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> APIKey:
    """
    FastAPI dependency for API key validation via TenantManager.
    
    Accepts key via:
    - Authorization: Bearer <key>
    - X-API-Key header
    """
    key = None
    
    if credentials:
        key = credentials.credentials
    elif x_api_key:
        key = x_api_key
    
    if not key:
        raise HTTPException(
            status_code=401,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # First, check if it's the master key (works regardless of multitenancy)
    master_key = os.getenv("SUNONA_MASTER_KEY")
    if master_key and key == master_key:
        # Master key authentication - create a simple admin APIKey object
        # Use a simple namespace object to avoid class instantiation issues
        class MasterAPIKey:
            id = "master"
            organization_id = "default"
            def has_permission(self, perm): return True
        
        api_key = MasterAPIKey()
        request.state.organization_id = "default"
        request.state.api_key_id = "master"
        return api_key
    
    # Otherwise, try multitenancy validation
    if HAS_MULTITENANCY:
        manager = get_tenant_manager()
        client_ip = request.client.host if request.client else "unknown"
        
        # Validate via TenantManager
        api_key = await manager.validate_api_key(key, client_ip=client_ip)
        
        if not api_key:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired API key",
            )
    else:
        # Standalone Mode: No valid key found
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
        )
    
    # Ingest into request state for later use
    request.state.organization_id = api_key.organization_id
    request.state.api_key_id = api_key.id
    
    return api_key


async def get_current_organization(
    api_key: APIKey = Depends(get_api_key)
) -> Organization:
    """Dependency to get the organization for the current API key."""
    if not HAS_MULTITENANCY:
        return {"id": "default", "name": "Default Organization"}
        
    manager = get_tenant_manager()
    org = await manager.get_organization(api_key.organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


def require_permission(permission_name: str):
    """
    FastAPI dependency to require a specific permission.
    
    Args:
        permission_name: The permission string (e.g. 'agent:create')
    """
    async def permission_dependency(
        api_key: APIKey = Depends(get_api_key)
    ) -> APIKey:
        try:
            perm = Permission(permission_name)
        except ValueError:
            logger.error(f"Invalid permission requested: {permission_name}")
            raise HTTPException(status_code=500, detail="Configuration error")
            
        if not api_key.has_permission(perm):
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied: '{permission_name}' required"
            )
        return api_key
    
    return permission_dependency


def require_auth(permission: Optional[str] = None):
    """
    Factory that returns a dependency callable for authentication.
    
    Usage:
        @router.get("/agents", dependencies=[Depends(require_auth())])
        async def list_agents(): ...
        
        @router.get("/protected", dependencies=[Depends(require_auth("agent:read"))])
        async def protected_route(): ...
    """
    if permission:
        # Return the permission dependency callable (not wrapped in Depends)
        return require_permission(permission)
    # Return the get_api_key callable directly (not wrapped in Depends)
    return get_api_key


