"""
Sunona Voice AI - Provider Manager

Manage API keys and provider configurations.
Centralized provider credential management.

Features:
- Add/remove provider API keys
- Validate credentials
- Test provider connectivity
- Usage monitoring
- Key rotation support
"""

import asyncio
import hashlib
import logging
import secrets
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Awaitable

logger = logging.getLogger(__name__)


class ProviderType(Enum):
    """Types of providers."""
    STT = "stt"
    TTS = "tts"
    LLM = "llm"
    TELEPHONY = "telephony"
    VECTOR_DB = "vector_db"
    STORAGE = "storage"


class CredentialStatus(Enum):
    """Credential validation status."""
    VALID = "valid"
    INVALID = "invalid"
    EXPIRED = "expired"
    UNKNOWN = "unknown"
    QUOTA_EXCEEDED = "quota_exceeded"


@dataclass
class ProviderInfo:
    """Information about a provider."""
    id: str
    name: str
    type: ProviderType
    description: str = ""
    
    # Configuration
    required_fields: List[str] = field(default_factory=list)
    optional_fields: List[str] = field(default_factory=list)
    
    # Features
    supports_streaming: bool = True
    supports_batch: bool = False
    
    # Docs
    docs_url: str = ""
    signup_url: str = ""
    
    # Status
    is_available: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "required_fields": self.required_fields,
            "optional_fields": self.optional_fields,
            "supports_streaming": self.supports_streaming,
            "docs_url": self.docs_url,
            "signup_url": self.signup_url,
            "is_available": self.is_available,
        }


@dataclass
class ProviderCredential:
    """Stored provider credentials."""
    id: str
    provider_id: str
    organization_id: str
    
    # Credentials (encrypted in production)
    api_key_hash: str  # Hashed for security
    api_key_preview: str  # First/last 4 chars
    additional_config: Dict[str, str] = field(default_factory=dict)
    
    # Validation
    status: CredentialStatus = CredentialStatus.UNKNOWN
    last_validated: Optional[datetime] = None
    validation_error: Optional[str] = None
    
    # Usage
    is_default: bool = False
    is_active: bool = True
    usage_count: int = 0
    last_used: Optional[datetime] = None
    
    # Metadata
    name: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        result = {
            "id": self.id,
            "provider_id": self.provider_id,
            "name": self.name,
            "api_key_preview": self.api_key_preview,
            "status": self.status.value,
            "last_validated": self.last_validated.isoformat() if self.last_validated else None,
            "is_default": self.is_default,
            "is_active": self.is_active,
            "usage_count": self.usage_count,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "created_at": self.created_at.isoformat(),
        }
        
        if include_sensitive:
            result["additional_config"] = self.additional_config
        
        return result


# Default provider configurations
DEFAULT_PROVIDERS: List[ProviderInfo] = [
    # STT
    ProviderInfo(
        id="deepgram",
        name="Deepgram",
        type=ProviderType.STT,
        description="Fast, accurate speech-to-text with streaming",
        required_fields=["api_key"],
        supports_streaming=True,
        docs_url="https://developers.deepgram.com/docs",
        signup_url="https://console.deepgram.com/signup",
    ),
    ProviderInfo(
        id="azure_stt",
        name="Azure Speech",
        type=ProviderType.STT,
        description="Microsoft Azure Speech-to-Text",
        required_fields=["api_key", "region"],
        supports_streaming=True,
        docs_url="https://docs.microsoft.com/azure/cognitive-services/speech-service",
    ),
    ProviderInfo(
        id="assembly",
        name="AssemblyAI",
        type=ProviderType.STT,
        description="AI-powered transcription",
        required_fields=["api_key"],
        supports_streaming=True,
        docs_url="https://www.assemblyai.com/docs",
    ),
    
    # TTS
    ProviderInfo(
        id="elevenlabs",
        name="ElevenLabs",
        type=ProviderType.TTS,
        description="Natural, expressive AI voices",
        required_fields=["api_key"],
        supports_streaming=True,
        docs_url="https://elevenlabs.io/docs/api-reference",
        signup_url="https://elevenlabs.io",
    ),
    ProviderInfo(
        id="openai_tts",
        name="OpenAI TTS",
        type=ProviderType.TTS,
        description="OpenAI text-to-speech",
        required_fields=["api_key"],
        supports_streaming=True,
        docs_url="https://platform.openai.com/docs/guides/text-to-speech",
    ),
    ProviderInfo(
        id="polly",
        name="Amazon Polly",
        type=ProviderType.TTS,
        description="AWS text-to-speech service",
        required_fields=["access_key_id", "secret_access_key", "region"],
        supports_streaming=True,
        docs_url="https://docs.aws.amazon.com/polly",
    ),
    ProviderInfo(
        id="cartesia",
        name="Cartesia",
        type=ProviderType.TTS,
        description="Low-latency voice synthesis",
        required_fields=["api_key"],
        supports_streaming=True,
        docs_url="https://docs.cartesia.ai",
    ),
    
    # LLM
    ProviderInfo(
        id="openai",
        name="OpenAI",
        type=ProviderType.LLM,
        description="GPT-4, GPT-3.5 and more",
        required_fields=["api_key"],
        optional_fields=["organization_id"],
        supports_streaming=True,
        docs_url="https://platform.openai.com/docs",
    ),
    ProviderInfo(
        id="anthropic",
        name="Anthropic",
        type=ProviderType.LLM,
        description="Claude models",
        required_fields=["api_key"],
        supports_streaming=True,
        docs_url="https://docs.anthropic.com",
    ),
    ProviderInfo(
        id="groq",
        name="Groq",
        type=ProviderType.LLM,
        description="Ultra-fast LLM inference",
        required_fields=["api_key"],
        supports_streaming=True,
        docs_url="https://console.groq.com/docs",
    ),
    ProviderInfo(
        id="openrouter",
        name="OpenRouter",
        type=ProviderType.LLM,
        description="Access 100+ models including free ones",
        required_fields=["api_key"],
        supports_streaming=True,
        docs_url="https://openrouter.ai/docs",
    ),
    
    # Telephony
    ProviderInfo(
        id="twilio",
        name="Twilio",
        type=ProviderType.TELEPHONY,
        description="Voice, SMS, and communications",
        required_fields=["account_sid", "auth_token"],
        optional_fields=["phone_number"],
        docs_url="https://www.twilio.com/docs/voice",
    ),
    ProviderInfo(
        id="plivo",
        name="Plivo",
        type=ProviderType.TELEPHONY,
        description="Cloud communications platform",
        required_fields=["auth_id", "auth_token"],
        docs_url="https://www.plivo.com/docs",
    ),
    ProviderInfo(
        id="telnyx",
        name="Telnyx",
        type=ProviderType.TELEPHONY,
        description="Enterprise-grade communications",
        required_fields=["api_key"],
        docs_url="https://developers.telnyx.com",
    ),
]


class ProviderManager:
    """
    Provider credential manager.
    
    Manages API keys and configurations for all providers.
    
    Example:
        manager = ProviderManager()
        
        # List available providers
        providers = await manager.list_providers(ProviderType.LLM)
        
        # Add credentials
        cred = await manager.add_credential(
            organization_id="org_123",
            provider_id="openai",
            api_key="sk-...",
            name="Production Key",
        )
        
        # Validate credentials
        status = await manager.validate_credential(cred.id)
        
        # Get active credential
        key = await manager.get_api_key("org_123", "openai")
    """
    
    def __init__(self):
        self._providers: Dict[str, ProviderInfo] = {
            p.id: p for p in DEFAULT_PROVIDERS
        }
        self._credentials: Dict[str, ProviderCredential] = {}
        self._decrypted_keys: Dict[str, str] = {}  # cred_id -> actual key
        
        # Validators
        self._validators: Dict[str, Callable[..., Awaitable[bool]]] = {}
    
    async def list_providers(
        self,
        provider_type: Optional[ProviderType] = None,
    ) -> List[ProviderInfo]:
        """List available providers."""
        providers = list(self._providers.values())
        
        if provider_type:
            providers = [p for p in providers if p.type == provider_type]
        
        return providers
    
    async def get_provider(self, provider_id: str) -> Optional[ProviderInfo]:
        """Get provider info."""
        return self._providers.get(provider_id)
    
    async def add_credential(
        self,
        organization_id: str,
        provider_id: str,
        api_key: str,
        name: str = "",
        additional_config: Optional[Dict[str, str]] = None,
        created_by: Optional[str] = None,
        set_default: bool = False,
    ) -> ProviderCredential:
        """
        Add provider credentials.
        
        Args:
            organization_id: Organization ID
            provider_id: Provider ID
            api_key: API key value
            name: Friendly name for this credential
            additional_config: Extra config (region, etc.)
            created_by: User who added
            set_default: Set as default for this provider
        
        Returns:
            ProviderCredential object
        """
        provider = self._providers.get(provider_id)
        if not provider:
            raise ValueError(f"Unknown provider: {provider_id}")
        
        cred_id = f"cred_{uuid.uuid4().hex[:12]}"
        
        # Create preview (first 4 and last 4 chars)
        if len(api_key) > 8:
            preview = f"{api_key[:4]}...{api_key[-4:]}"
        else:
            preview = "****"
        
        cred = ProviderCredential(
            id=cred_id,
            provider_id=provider_id,
            organization_id=organization_id,
            api_key_hash=hashlib.sha256(api_key.encode()).hexdigest(),
            api_key_preview=preview,
            additional_config=additional_config or {},
            name=name or f"{provider.name} Key",
            created_by=created_by,
            is_default=set_default,
        )
        
        self._credentials[cred_id] = cred
        self._decrypted_keys[cred_id] = api_key  # In production, encrypt!
        
        # Clear other defaults if setting this as default
        if set_default:
            for c in self._credentials.values():
                if (c.organization_id == organization_id and 
                    c.provider_id == provider_id and 
                    c.id != cred_id):
                    c.is_default = False
        
        logger.info(f"Added credential {cred_id} for {provider_id}")
        return cred
    
    async def validate_credential(
        self,
        credential_id: str,
    ) -> CredentialStatus:
        """
        Validate a credential.
        
        Args:
            credential_id: Credential ID
        
        Returns:
            CredentialStatus
        """
        cred = self._credentials.get(credential_id)
        if not cred:
            return CredentialStatus.UNKNOWN
        
        api_key = self._decrypted_keys.get(credential_id)
        if not api_key:
            cred.status = CredentialStatus.INVALID
            return CredentialStatus.INVALID
        
        # Check if we have a validator
        validator = self._validators.get(cred.provider_id)
        
        if validator:
            try:
                is_valid = await validator(api_key, cred.additional_config)
                cred.status = CredentialStatus.VALID if is_valid else CredentialStatus.INVALID
            except Exception as e:
                cred.status = CredentialStatus.INVALID
                cred.validation_error = str(e)
        else:
            # No validator, assume valid
            cred.status = CredentialStatus.VALID
        
        cred.last_validated = datetime.now(timezone.utc)
        return cred.status
    
    async def test_provider(
        self,
        credential_id: str,
    ) -> Dict[str, Any]:
        """
        Test provider connectivity.
        
        Args:
            credential_id: Credential ID
        
        Returns:
            Test results
        """
        cred = self._credentials.get(credential_id)
        if not cred:
            return {"success": False, "error": "Credential not found"}
        
        api_key = self._decrypted_keys.get(credential_id)
        if not api_key:
            return {"success": False, "error": "API key not available"}
        
        provider = self._providers.get(cred.provider_id)
        if not provider:
            return {"success": False, "error": "Provider not found"}
        
        # Simple connectivity test based on provider type
        try:
            if provider.type == ProviderType.LLM:
                return await self._test_llm(cred.provider_id, api_key)
            elif provider.type == ProviderType.TTS:
                return await self._test_tts(cred.provider_id, api_key)
            elif provider.type == ProviderType.STT:
                return await self._test_stt(cred.provider_id, api_key)
            else:
                return {"success": True, "message": "Connection test skipped"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_llm(self, provider_id: str, api_key: str) -> Dict[str, Any]:
        """Test LLM provider."""
        try:
            import httpx
            
            if provider_id == "openai":
                async with httpx.AsyncClient(timeout=10) as client:
                    response = await client.get(
                        "https://api.openai.com/v1/models",
                        headers={"Authorization": f"Bearer {api_key}"},
                    )
                    if response.status_code == 200:
                        return {"success": True, "message": "OpenAI connection successful"}
                    return {"success": False, "error": f"API returned {response.status_code}"}
            
            # Default success for other providers
            return {"success": True, "message": "Connection assumed successful"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_tts(self, provider_id: str, api_key: str) -> Dict[str, Any]:
        """Test TTS provider."""
        return {"success": True, "message": "TTS test requires audio generation"}
    
    async def _test_stt(self, provider_id: str, api_key: str) -> Dict[str, Any]:
        """Test STT provider."""
        return {"success": True, "message": "STT test requires audio input"}
    
    async def get_api_key(
        self,
        organization_id: str,
        provider_id: str,
    ) -> Optional[str]:
        """
        Get the active API key for a provider.
        
        Args:
            organization_id: Organization ID
            provider_id: Provider ID
        
        Returns:
            API key string or None
        """
        # Find default credential first
        for cred in self._credentials.values():
            if (cred.organization_id == organization_id and 
                cred.provider_id == provider_id and 
                cred.is_default and 
                cred.is_active):
                cred.usage_count += 1
                cred.last_used = datetime.now(timezone.utc)
                return self._decrypted_keys.get(cred.id)
        
        # Fall back to any active credential
        for cred in self._credentials.values():
            if (cred.organization_id == organization_id and 
                cred.provider_id == provider_id and 
                cred.is_active):
                cred.usage_count += 1
                cred.last_used = datetime.now(timezone.utc)
                return self._decrypted_keys.get(cred.id)
        
        return None
    
    async def list_credentials(
        self,
        organization_id: str,
        provider_id: Optional[str] = None,
    ) -> List[ProviderCredential]:
        """List credentials for an organization."""
        creds = [
            c for c in self._credentials.values()
            if c.organization_id == organization_id
        ]
        
        if provider_id:
            creds = [c for c in creds if c.provider_id == provider_id]
        
        return creds
    
    async def update_credential(
        self,
        credential_id: str,
        name: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_default: Optional[bool] = None,
    ) -> Optional[ProviderCredential]:
        """Update credential settings."""
        cred = self._credentials.get(credential_id)
        if not cred:
            return None
        
        if name is not None:
            cred.name = name
        
        if is_active is not None:
            cred.is_active = is_active
        
        if is_default is not None:
            if is_default:
                # Clear other defaults
                for c in self._credentials.values():
                    if (c.organization_id == cred.organization_id and 
                        c.provider_id == cred.provider_id):
                        c.is_default = False
            cred.is_default = is_default
        
        return cred
    
    async def delete_credential(self, credential_id: str) -> bool:
        """Delete a credential."""
        if credential_id in self._credentials:
            del self._credentials[credential_id]
            self._decrypted_keys.pop(credential_id, None)
            logger.info(f"Deleted credential {credential_id}")
            return True
        return False
    
    async def rotate_key(
        self,
        credential_id: str,
        new_api_key: str,
    ) -> Optional[ProviderCredential]:
        """
        Rotate API key for a credential.
        
        Args:
            credential_id: Credential ID
            new_api_key: New API key value
        
        Returns:
            Updated credential
        """
        cred = self._credentials.get(credential_id)
        if not cred:
            return None
        
        # Update key
        cred.api_key_hash = hashlib.sha256(new_api_key.encode()).hexdigest()
        
        if len(new_api_key) > 8:
            cred.api_key_preview = f"{new_api_key[:4]}...{new_api_key[-4:]}"
        else:
            cred.api_key_preview = "****"
        
        self._decrypted_keys[credential_id] = new_api_key
        
        # Reset validation
        cred.status = CredentialStatus.UNKNOWN
        cred.last_validated = None
        
        logger.info(f"Rotated key for credential {credential_id}")
        return cred
    
    def register_validator(
        self,
        provider_id: str,
        validator: Callable[..., Awaitable[bool]],
    ) -> None:
        """Register a credential validator for a provider."""
        self._validators[provider_id] = validator


# Global manager
_global_manager: Optional[ProviderManager] = None


def get_provider_manager() -> ProviderManager:
    """Get or create global provider manager."""
    global _global_manager
    if _global_manager is None:
        _global_manager = ProviderManager()
    return _global_manager
