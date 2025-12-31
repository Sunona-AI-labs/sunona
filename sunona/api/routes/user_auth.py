"""
Sunona Voice AI - User Authentication & API Key Management

Self-service endpoints for user registration and API key generation.
Users can sign up, log in, and manage their own API keys.
"""

import os
import re
import secrets
import hashlib
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, EmailStr

from fastapi import APIRouter, HTTPException, Depends, Request

from sunona.api.auth import get_api_key, get_auth_instance, APIKey
from sunona.auth import OrganizationManager, UserRole

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Managers
_org_manager = OrganizationManager()
_users: Dict[str, Dict] = {}  # email -> user data


# ==================== Request/Response Models ====================

class SignUpRequest(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=2)
    company_name: Optional[str] = None


class LoginRequest(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class CreateAPIKeyRequest(BaseModel):
    """Create API key request."""
    name: str = Field(..., min_length=3, max_length=50)
    permissions: List[str] = ["read", "write"]
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)


class APIKeyResponse(BaseModel):
    """API key response (key only shown once!)."""
    key_id: str
    key: str  # Plain key - ONLY shown once!
    name: str
    permissions: List[str]
    expires_at: Optional[str]
    warning: str = "Save this key! It will never be shown again."


class UserProfile(BaseModel):
    """User profile response."""
    user_id: str
    email: str
    name: str
    org_id: str
    org_name: str
    created_at: str


# ==================== Helper Functions ====================

def _hash_password(password: str) -> str:
    """Hash password with salt."""
    salt = os.getenv("JWT_SECRET", "default_salt")
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()


def _verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return _hash_password(password) == hashed


def _create_session_token(user_id: str, org_id: str) -> str:
    """Create a simple session token."""
    data = f"{user_id}:{org_id}:{datetime.now().timestamp()}"
    return hashlib.sha256(data.encode()).hexdigest()[:32]


# ==================== Endpoints ====================

@router.post("/signup")
async def signup(request: SignUpRequest) -> Dict[str, Any]:
    """
    Register a new user account.
    
    Creates:
    - User account
    - Organization (if company_name provided)
    - Initial API key
    
    Returns:
        User profile and initial API key
    """
    email = request.email.lower()
    
    # Check if email already exists
    if email in _users:
        raise HTTPException(400, "Email already registered")
    
    # Create organization
    org = _org_manager.create_org(
        name=request.company_name or f"{request.name}'s Organization",
        email=email,
        owner_name=request.name,
    )
    
    # Get owner user
    owner = org.users[0]
    
    # Store user
    _users[email] = {
        "user_id": owner.user_id,
        "email": email,
        "password_hash": _hash_password(request.password),
        "name": request.name,
        "org_id": org.org_id,
        "created_at": datetime.now().isoformat(),
    }
    
    # Create initial API key
    auth = get_auth_instance()
    key_result = auth.create_key(
        name="Default API Key",
        account_id=org.org_id,
        permissions=["read", "write", "call"],
        expires_in_days=365,
    )
    
    logger.info(f"New user registered: {email}")
    
    return {
        "success": True,
        "message": "Account created successfully",
        "user": {
            "user_id": owner.user_id,
            "email": email,
            "name": request.name,
            "org_id": org.org_id,
            "org_name": org.name,
        },
        "api_key": {
            "key_id": key_result["key_id"],
            "key": key_result["key"],
            "warning": "⚠️ Save this key! It will NEVER be shown again.",
        },
    }


@router.post("/login")
async def login(request: LoginRequest) -> Dict[str, Any]:
    """
    Log in to get a session token.
    
    Use the session token or your API key to access protected endpoints.
    """
    email = request.email.lower()
    
    user = _users.get(email)
    if not user:
        raise HTTPException(401, "Invalid email or password")
    
    if not _verify_password(request.password, user["password_hash"]):
        raise HTTPException(401, "Invalid email or password")
    
    # Create session
    token = _create_session_token(user["user_id"], user["org_id"])
    
    logger.info(f"User logged in: {email}")
    
    return {
        "success": True,
        "message": "Login successful",
        "session_token": token,
        "user": {
            "user_id": user["user_id"],
            "email": email,
            "name": user["name"],
            "org_id": user["org_id"],
        },
    }


@router.get("/me")
async def get_current_user(
    api_key: APIKey = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    Get current user profile.
    
    Requires API key authentication.
    """
    org = _org_manager.get_org(api_key.account_id)
    
    return {
        "user_id": api_key.key_id,
        "org_id": api_key.account_id,
        "org_name": org.name if org else "Unknown",
        "permissions": api_key.permissions,
        "key_name": api_key.name,
    }


# ==================== API Key Management ====================

@router.post("/keys")
async def create_api_key(
    request: CreateAPIKeyRequest,
    api_key: APIKey = Depends(get_api_key),
) -> APIKeyResponse:
    """
    Create a new API key.
    
    ⚠️ The plain key is only returned ONCE in this response!
    
    Args:
        name: Descriptive name for the key
        permissions: List of permissions (read, write, call, admin)
        expires_in_days: Optional expiration (1-365 days)
        
    Returns:
        New API key (save it immediately!)
    """
    auth = get_auth_instance()
    
    result = auth.create_key(
        name=request.name,
        account_id=api_key.account_id,
        permissions=request.permissions,
        expires_in_days=request.expires_in_days,
    )
    
    # Get the created key details
    keys = auth.list_keys(api_key.account_id)
    created_key = next((k for k in keys if k["key_id"] == result["key_id"]), None)
    
    logger.info(f"API key created: {result['key_id']} for {api_key.account_id}")
    
    return APIKeyResponse(
        key_id=result["key_id"],
        key=result["key"],
        name=request.name,
        permissions=request.permissions,
        expires_at=created_key["expires_at"] if created_key else None,
    )


@router.get("/keys")
async def list_api_keys(
    api_key: APIKey = Depends(get_api_key),
) -> List[Dict[str, Any]]:
    """
    List all API keys for the account.
    
    Note: Key values are NOT returned (only shown when created).
    """
    auth = get_auth_instance()
    keys = auth.list_keys(api_key.account_id)
    
    return keys


@router.delete("/keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    api_key: APIKey = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    Revoke an API key.
    
    The key will immediately stop working.
    """
    auth = get_auth_instance()
    
    # Verify the key belongs to this account
    keys = auth.list_keys(api_key.account_id)
    if not any(k["key_id"] == key_id for k in keys):
        raise HTTPException(404, "Key not found")
    
    success = auth.revoke_key(key_id)
    
    if success:
        logger.info(f"API key revoked: {key_id}")
        return {"success": True, "message": "API key revoked"}
    else:
        raise HTTPException(500, "Failed to revoke key")


@router.post("/keys/{key_id}/rotate")
async def rotate_api_key(
    key_id: str,
    api_key: APIKey = Depends(get_api_key),
) -> APIKeyResponse:
    """
    Rotate an API key (revoke old, create new with same permissions).
    
    Returns a new key. The old key stops working immediately.
    """
    auth = get_auth_instance()
    
    # Get existing key info
    keys = auth.list_keys(api_key.account_id)
    old_key = next((k for k in keys if k["key_id"] == key_id), None)
    
    if not old_key:
        raise HTTPException(404, "Key not found")
    
    # Revoke old key
    auth.revoke_key(key_id)
    
    # Create new key with same settings
    result = auth.create_key(
        name=f"{old_key['name']} (rotated)",
        account_id=api_key.account_id,
        permissions=old_key.get("permissions", ["read", "write"]),
    )
    
    logger.info(f"API key rotated: {key_id} -> {result['key_id']}")
    
    return APIKeyResponse(
        key_id=result["key_id"],
        key=result["key"],
        name=f"{old_key['name']} (rotated)",
        permissions=old_key.get("permissions", ["read", "write"]),
        expires_at=None,
    )


# ==================== Password Management ====================

@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str = Field(..., min_length=8),
    api_key: APIKey = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    Change account password.
    """
    # Find user by org_id
    user = next(
        (u for u in _users.values() if u["org_id"] == api_key.account_id),
        None
    )
    
    if not user:
        raise HTTPException(404, "User not found")
    
    if not _verify_password(current_password, user["password_hash"]):
        raise HTTPException(401, "Current password is incorrect")
    
    user["password_hash"] = _hash_password(new_password)
    
    return {"success": True, "message": "Password changed successfully"}
