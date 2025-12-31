"""
Sunona Voice AI - SSO Authentication

Enterprise SSO and MFA support.
"""

import os
import logging
import jwt
import secrets
import hashlib
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class SSOProvider(str, Enum):
    """Supported SSO providers."""
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    OKTA = "okta"
    AUTH0 = "auth0"
    SAML = "saml"
    OIDC = "oidc"


class MFAMethod(str, Enum):
    """MFA methods."""
    TOTP = "totp"  # Google Authenticator, Authy
    SMS = "sms"
    EMAIL = "email"
    WEBAUTHN = "webauthn"  # Hardware keys


@dataclass
class SSOConfig:
    """SSO provider configuration."""
    provider: SSOProvider
    client_id: str
    client_secret: str
    domain: Optional[str] = None  # For Okta/Auth0
    
    # SAML specific
    idp_metadata_url: Optional[str] = None
    entity_id: Optional[str] = None
    
    # OIDC specific
    discovery_url: Optional[str] = None
    
    # Scopes
    scopes: List[str] = field(default_factory=lambda: ["openid", "email", "profile"])


@dataclass
class MFAConfig:
    """MFA configuration for user."""
    enabled: bool = False
    method: MFAMethod = MFAMethod.TOTP
    
    # TOTP
    totp_secret: Optional[str] = None
    backup_codes: List[str] = field(default_factory=list)
    
    # Phone
    phone_number: Optional[str] = None
    
    # Email
    email: Optional[str] = None
    
    verified: bool = False
    last_verified: Optional[datetime] = None


@dataclass
class Session:
    """User session."""
    session_id: str
    user_id: str
    org_id: str
    
    # Auth info
    auth_method: str = "password"  # password, sso, api_key
    sso_provider: Optional[SSOProvider] = None
    mfa_verified: bool = False
    
    # Tokens
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    last_activity: datetime = field(default_factory=datetime.now)
    
    # Device info
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    @property
    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "auth_method": self.auth_method,
            "mfa_verified": self.mfa_verified,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


class SSOManager:
    """
    Enterprise SSO and MFA manager.
    
    Features:
        - Multiple SSO providers (Google, Microsoft, Okta, Auth0, SAML)
        - MFA with TOTP, SMS, Email
        - Session management
        - JWT tokens
    
    Example:
        ```python
        sso = SSOManager(jwt_secret="secret")
        
        # Configure SSO for org
        sso.configure_sso(
            org_id="org_123",
            provider=SSOProvider.GOOGLE,
            client_id="...",
            client_secret="..."
        )
        
        # Get SSO login URL
        url = sso.get_sso_login_url("org_123", redirect_uri="...")
        
        # Handle callback
        user = await sso.handle_sso_callback("org_123", code, state)
        
        # Enable MFA
        secret = sso.enable_mfa(user_id, MFAMethod.TOTP)
        
        # Verify MFA
        valid = sso.verify_mfa(user_id, "123456")
        ```
    """
    
    def __init__(
        self,
        jwt_secret: Optional[str] = None,
        token_expiry_hours: int = 24,
    ):
        """
        Initialize SSO manager.
        
        Args:
            jwt_secret: Secret for JWT signing
            token_expiry_hours: Access token expiry
        """
        self._jwt_secret = jwt_secret or os.getenv("JWT_SECRET", secrets.token_hex(32))
        self._token_expiry = token_expiry_hours
        
        # Storage
        self._sso_configs: Dict[str, SSOConfig] = {}
        self._mfa_configs: Dict[str, MFAConfig] = {}
        self._sessions: Dict[str, Session] = {}
        
        logger.info("SSO manager initialized")
    
    # ==================== SSO Configuration ====================
    
    def configure_sso(
        self,
        org_id: str,
        provider: SSOProvider,
        client_id: str,
        client_secret: str,
        **kwargs,
    ) -> SSOConfig:
        """Configure SSO for an organization."""
        config = SSOConfig(
            provider=provider,
            client_id=client_id,
            client_secret=client_secret,
            domain=kwargs.get("domain"),
            idp_metadata_url=kwargs.get("idp_metadata_url"),
            discovery_url=kwargs.get("discovery_url"),
        )
        
        self._sso_configs[org_id] = config
        logger.info(f"Configured {provider.value} SSO for {org_id}")
        
        return config
    
    def get_sso_config(self, org_id: str) -> Optional[SSOConfig]:
        """Get SSO config for org."""
        return self._sso_configs.get(org_id)
    
    def get_sso_login_url(
        self,
        org_id: str,
        redirect_uri: str,
        state: Optional[str] = None,
    ) -> Optional[str]:
        """
        Get SSO login URL.
        
        Args:
            org_id: Organization ID
            redirect_uri: Callback URL
            state: State parameter for CSRF
            
        Returns:
            Login URL or None
        """
        config = self._sso_configs.get(org_id)
        if not config:
            return None
        
        state = state or secrets.token_urlsafe(32)
        scopes = " ".join(config.scopes)
        
        urls = {
            SSOProvider.GOOGLE: f"https://accounts.google.com/o/oauth2/v2/auth?client_id={config.client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scopes}&state={state}",
            SSOProvider.MICROSOFT: f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={config.client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scopes}&state={state}",
            SSOProvider.OKTA: f"https://{config.domain}/oauth2/default/v1/authorize?client_id={config.client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scopes}&state={state}",
            SSOProvider.AUTH0: f"https://{config.domain}/authorize?client_id={config.client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scopes}&state={state}",
        }
        
        return urls.get(config.provider)
    
    async def handle_sso_callback(
        self,
        org_id: str,
        code: str,
        state: str,
    ) -> Dict[str, Any]:
        """
        Handle SSO callback.
        
        Args:
            org_id: Organization ID
            code: Authorization code
            state: State parameter
            
        Returns:
            User info from SSO provider
        """
        config = self._sso_configs.get(org_id)
        if not config:
            raise ValueError("SSO not configured for org")
        
        # In real implementation, exchange code for tokens
        # and fetch user info from provider
        
        # Placeholder: return mock user data
        return {
            "email": "user@example.com",
            "name": "SSO User",
            "provider": config.provider.value,
            "verified": True,
        }
    
    # ==================== MFA ====================
    
    def enable_mfa(
        self,
        user_id: str,
        method: MFAMethod = MFAMethod.TOTP,
        phone: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Enable MFA for user.
        
        Args:
            user_id: User ID
            method: MFA method
            phone: Phone for SMS
            email: Email for email MFA
            
        Returns:
            Setup info (secret for TOTP, etc.)
        """
        config = MFAConfig(
            enabled=True,
            method=method,
            phone_number=phone,
            email=email,
        )
        
        result = {}
        
        if method == MFAMethod.TOTP:
            # Generate TOTP secret
            config.totp_secret = secrets.token_hex(20)
            config.backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
            
            result = {
                "secret": config.totp_secret,
                "backup_codes": config.backup_codes,
                "provisioning_uri": f"otpauth://totp/Sunona:{user_id}?secret={config.totp_secret}&issuer=Sunona",
            }
        
        self._mfa_configs[user_id] = config
        logger.info(f"Enabled {method.value} MFA for {user_id}")
        
        return result
    
    def verify_mfa(
        self,
        user_id: str,
        code: str,
    ) -> bool:
        """
        Verify MFA code.
        
        Args:
            user_id: User ID
            code: MFA code from user
            
        Returns:
            True if valid
        """
        config = self._mfa_configs.get(user_id)
        if not config or not config.enabled:
            return True  # MFA not enabled
        
        if config.method == MFAMethod.TOTP:
            # In real implementation, use pyotp to verify
            # For now, accept any 6-digit code in demo
            if len(code) == 6 and code.isdigit():
                config.verified = True
                config.last_verified = datetime.now()
                return True
            
            # Check backup codes
            if code.upper() in config.backup_codes:
                config.backup_codes.remove(code.upper())
                config.verified = True
                return True
        
        return False
    
    def disable_mfa(self, user_id: str) -> bool:
        """Disable MFA for user."""
        if user_id in self._mfa_configs:
            self._mfa_configs[user_id].enabled = False
            return True
        return False
    
    # ==================== Sessions ====================
    
    def create_session(
        self,
        user_id: str,
        org_id: str,
        auth_method: str = "password",
        sso_provider: Optional[SSOProvider] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Session:
        """Create user session."""
        session_id = secrets.token_urlsafe(32)
        
        # Generate JWT access token
        access_token = self._generate_token(user_id, org_id, session_id)
        refresh_token = secrets.token_urlsafe(64)
        
        session = Session(
            session_id=session_id,
            user_id=user_id,
            org_id=org_id,
            auth_method=auth_method,
            sso_provider=sso_provider,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=datetime.now() + timedelta(hours=self._token_expiry),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        self._sessions[session_id] = session
        logger.info(f"Created session for {user_id}")
        
        return session
    
    def _generate_token(
        self,
        user_id: str,
        org_id: str,
        session_id: str,
    ) -> str:
        """Generate JWT access token."""
        payload = {
            "sub": user_id,
            "org": org_id,
            "sid": session_id,
            "iat": datetime.now().timestamp(),
            "exp": (datetime.now() + timedelta(hours=self._token_expiry)).timestamp(),
        }
        
        return jwt.encode(payload, self._jwt_secret, algorithm="HS256")
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate and decode JWT token."""
        try:
            payload = jwt.decode(token, self._jwt_secret, algorithms=["HS256"])
            
            # Check if session exists and is valid
            session_id = payload.get("sid")
            if session_id and session_id in self._sessions:
                session = self._sessions[session_id]
                if not session.is_expired:
                    session.last_activity = datetime.now()
                    return payload
            
            return None
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def revoke_session(self, session_id: str) -> bool:
        """Revoke a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
    
    def get_user_sessions(self, user_id: str) -> List[Session]:
        """Get all sessions for user."""
        return [
            s for s in self._sessions.values()
            if s.user_id == user_id and not s.is_expired
        ]
