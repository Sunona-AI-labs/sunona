"""
Sunona Voice AI - White Label Configuration

Customizable branding and provider settings for white-labeling.
"""

import os
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class VoiceConfig:
    """Voice configuration for white-labeling."""
    voice_id: str
    provider: str = "elevenlabs"  # elevenlabs, openai, playht, etc.
    name: str = ""
    language: str = "en"
    speaking_rate: float = 1.0
    pitch: float = 1.0
    
    # Custom voice clone
    is_cloned: bool = False
    clone_source_url: Optional[str] = None


@dataclass
class BrandingConfig:
    """Branding configuration."""
    company_name: str
    logo_url: Optional[str] = None
    primary_color: str = "#4F46E5"  # Indigo
    secondary_color: str = "#10B981"  # Emerald
    
    # Email templates
    email_from_name: Optional[str] = None
    email_from_address: Optional[str] = None
    
    # Custom domain
    custom_domain: Optional[str] = None
    
    # Terms & Privacy
    terms_url: Optional[str] = None
    privacy_url: Optional[str] = None


@dataclass
class TelephonyConfig:
    """Telephony white-label settings."""
    provider: str = "twilio"  # twilio, plivo, vonage, signalwire, telnyx, bandwidth
    
    # Credentials (use your own provider account)
    account_sid: Optional[str] = None
    auth_token: Optional[str] = None
    api_key: Optional[str] = None
    
    # Phone numbers
    phone_numbers: List[str] = field(default_factory=list)
    default_caller_id: Optional[str] = None
    
    # Region
    region: str = "us"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "phone_numbers": self.phone_numbers,
            "default_caller_id": self.default_caller_id,
            "region": self.region,
        }


@dataclass
class AIConfig:
    """AI provider white-label settings."""
    # LLM
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    llm_api_key: Optional[str] = None
    
    # STT
    stt_provider: str = "deepgram"
    stt_api_key: Optional[str] = None
    
    # TTS
    tts_provider: str = "elevenlabs"
    tts_api_key: Optional[str] = None
    
    # Custom endpoints (for on-premise)
    llm_base_url: Optional[str] = None
    stt_base_url: Optional[str] = None
    tts_base_url: Optional[str] = None


@dataclass
class WhiteLabelConfig:
    """
    Complete white-label configuration for an organization.
    
    Allows customers to use their own:
    - Telephony accounts (Twilio, Plivo, etc.)
    - AI provider API keys
    - Custom voice clones
    - Branding (logo, colors, domain)
    """
    org_id: str
    name: str
    
    # Configuration sections
    branding: BrandingConfig = field(default_factory=lambda: BrandingConfig(company_name="Sunona"))
    telephony: TelephonyConfig = field(default_factory=TelephonyConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    voices: List[VoiceConfig] = field(default_factory=list)
    
    # Features
    features_enabled: Dict[str, bool] = field(default_factory=lambda: {
        "batch_calling": True,
        "conference": True,
        "recording": True,
        "transcripts": True,
        "analytics": True,
        "api_access": True,
    })
    
    # Limits
    max_concurrent_calls: int = 10
    max_agents: int = 100
    
    # Status
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def get_voice(self, voice_id: str) -> Optional[VoiceConfig]:
        """Get voice by ID."""
        for voice in self.voices:
            if voice.voice_id == voice_id:
                return voice
        return None
    
    def add_voice(self, voice: VoiceConfig) -> None:
        """Add custom voice."""
        self.voices.append(voice)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "org_id": self.org_id,
            "name": self.name,
            "branding": {
                "company_name": self.branding.company_name,
                "primary_color": self.branding.primary_color,
                "custom_domain": self.branding.custom_domain,
            },
            "telephony": self.telephony.to_dict(),
            "ai": {
                "llm_provider": self.ai.llm_provider,
                "llm_model": self.ai.llm_model,
                "stt_provider": self.ai.stt_provider,
                "tts_provider": self.ai.tts_provider,
            },
            "voice_count": len(self.voices),
            "features_enabled": self.features_enabled,
            "max_concurrent_calls": self.max_concurrent_calls,
            "is_active": self.is_active,
        }


class WhiteLabelManager:
    """
    Manage white-label configurations.
    
    Example:
        ```python
        manager = WhiteLabelManager()
        
        # Create white-label config
        config = manager.create_config(
            org_id="org_123",
            name="Acme Voice",
            telephony_provider="twilio",
            telephony_credentials={
                "account_sid": "AC...",
                "auth_token": "...",
            }
        )
        
        # Add custom voice
        manager.add_custom_voice(
            org_id="org_123",
            voice_id="custom_sarah",
            provider="playht",
            clone_source="https://..."
        )
        ```
    """
    
    def __init__(self):
        self._configs: Dict[str, WhiteLabelConfig] = {}
        logger.info("White-label manager initialized")
    
    def create_config(
        self,
        org_id: str,
        name: str,
        branding: Optional[Dict[str, Any]] = None,
        telephony_provider: str = "twilio",
        telephony_credentials: Optional[Dict[str, str]] = None,
        ai_providers: Optional[Dict[str, str]] = None,
    ) -> WhiteLabelConfig:
        """Create white-label configuration."""
        config = WhiteLabelConfig(
            org_id=org_id,
            name=name,
        )
        
        # Set branding
        if branding:
            config.branding = BrandingConfig(
                company_name=branding.get("company_name", name),
                logo_url=branding.get("logo_url"),
                primary_color=branding.get("primary_color", "#4F46E5"),
                custom_domain=branding.get("custom_domain"),
            )
        
        # Set telephony
        if telephony_credentials:
            config.telephony = TelephonyConfig(
                provider=telephony_provider,
                account_sid=telephony_credentials.get("account_sid"),
                auth_token=telephony_credentials.get("auth_token"),
                api_key=telephony_credentials.get("api_key"),
            )
        
        # Set AI providers
        if ai_providers:
            config.ai = AIConfig(
                llm_provider=ai_providers.get("llm_provider", "openai"),
                llm_model=ai_providers.get("llm_model", "gpt-4o-mini"),
                llm_api_key=ai_providers.get("llm_api_key"),
                stt_provider=ai_providers.get("stt_provider", "deepgram"),
                stt_api_key=ai_providers.get("stt_api_key"),
                tts_provider=ai_providers.get("tts_provider", "elevenlabs"),
                tts_api_key=ai_providers.get("tts_api_key"),
            )
        
        self._configs[org_id] = config
        logger.info(f"Created white-label config: {org_id}")
        
        return config
    
    def get_config(self, org_id: str) -> Optional[WhiteLabelConfig]:
        """Get config by org ID."""
        return self._configs.get(org_id)
    
    def update_branding(
        self,
        org_id: str,
        company_name: Optional[str] = None,
        logo_url: Optional[str] = None,
        primary_color: Optional[str] = None,
        custom_domain: Optional[str] = None,
    ) -> bool:
        """Update branding settings."""
        config = self._configs.get(org_id)
        if not config:
            return False
        
        if company_name:
            config.branding.company_name = company_name
        if logo_url:
            config.branding.logo_url = logo_url
        if primary_color:
            config.branding.primary_color = primary_color
        if custom_domain:
            config.branding.custom_domain = custom_domain
        
        config.updated_at = datetime.now()
        return True
    
    def update_telephony(
        self,
        org_id: str,
        provider: str,
        credentials: Dict[str, str],
        phone_numbers: Optional[List[str]] = None,
    ) -> bool:
        """Update telephony settings."""
        config = self._configs.get(org_id)
        if not config:
            return False
        
        config.telephony.provider = provider
        config.telephony.account_sid = credentials.get("account_sid")
        config.telephony.auth_token = credentials.get("auth_token")
        config.telephony.api_key = credentials.get("api_key")
        
        if phone_numbers:
            config.telephony.phone_numbers = phone_numbers
        
        config.updated_at = datetime.now()
        return True
    
    def add_custom_voice(
        self,
        org_id: str,
        voice_id: str,
        provider: str,
        name: str = "",
        clone_source: Optional[str] = None,
    ) -> Optional[VoiceConfig]:
        """Add custom/cloned voice."""
        config = self._configs.get(org_id)
        if not config:
            return None
        
        voice = VoiceConfig(
            voice_id=voice_id,
            provider=provider,
            name=name or voice_id,
            is_cloned=clone_source is not None,
            clone_source_url=clone_source,
        )
        
        config.voices.append(voice)
        config.updated_at = datetime.now()
        
        logger.info(f"Added custom voice {voice_id} to {org_id}")
        return voice
    
    def set_phone_numbers(
        self,
        org_id: str,
        phone_numbers: List[str],
        default_caller_id: Optional[str] = None,
    ) -> bool:
        """Set phone numbers for white-label."""
        config = self._configs.get(org_id)
        if not config:
            return False
        
        config.telephony.phone_numbers = phone_numbers
        if default_caller_id:
            config.telephony.default_caller_id = default_caller_id
        
        config.updated_at = datetime.now()
        return True
    
    def enable_feature(self, org_id: str, feature: str) -> bool:
        """Enable a feature."""
        config = self._configs.get(org_id)
        if not config or feature not in config.features_enabled:
            return False
        
        config.features_enabled[feature] = True
        return True
    
    def disable_feature(self, org_id: str, feature: str) -> bool:
        """Disable a feature."""
        config = self._configs.get(org_id)
        if not config or feature not in config.features_enabled:
            return False
        
        config.features_enabled[feature] = False
        return True
