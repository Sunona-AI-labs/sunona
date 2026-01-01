"""
Sunona Voice AI - Account Models

Data models for multi-tenant account management.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pydantic import BaseModel, Field


class AccountTier(str, Enum):
    """Account tier levels."""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class AccountStatus(str, Enum):
    """Account status."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


@dataclass
class UsageLimits:
    """Usage limits per account tier."""
    max_agents: int = 1
    max_monthly_minutes: int = 100
    max_concurrent_calls: int = 1
    max_campaigns_per_month: int = 0
    allow_custom_voices: bool = False
    allow_api_access: bool = False
    allow_sub_accounts: bool = False
    
    @classmethod
    def for_tier(cls, tier: AccountTier) -> "UsageLimits":
        """Get limits for a tier."""
        limits = {
            AccountTier.FREE: cls(1, 100, 1, 0, False, False, False),
            AccountTier.STARTER: cls(5, 1000, 3, 5, False, True, False),
            AccountTier.PROFESSIONAL: cls(20, 10000, 10, 50, True, True, True),
            AccountTier.ENTERPRISE: cls(100, 100000, 50, 500, True, True, True),
        }
        return limits.get(tier, cls())


@dataclass
class UsageRecord:
    """Usage tracking record."""
    record_id: str
    account_id: str
    period: str  # YYYY-MM
    
    # Minutes used
    call_minutes: float = 0.0
    
    # Counts
    total_calls: int = 0
    agents_used: int = 0
    campaigns_run: int = 0
    
    # Costs
    llm_cost: float = 0.0
    stt_cost: float = 0.0
    tts_cost: float = 0.0
    telephony_cost: float = 0.0
    
    @property
    def total_cost(self) -> float:
        return self.llm_cost + self.stt_cost + self.tts_cost + self.telephony_cost
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "account_id": self.account_id,
            "period": self.period,
            "call_minutes": self.call_minutes,
            "total_calls": self.total_calls,
            "total_cost": self.total_cost,
        }


@dataclass
class SubAccount:
    """Sub-account for multi-tenant management."""
    sub_account_id: str
    parent_account_id: str
    name: str
    
    # Status
    status: AccountStatus = AccountStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    
    # Limits (inherited or custom)
    custom_limits: Optional[UsageLimits] = None
    
    # Usage
    current_usage: Optional[UsageRecord] = None
    
    def get_limits(self, parent_limits: UsageLimits) -> UsageLimits:
        """Get effective limits."""
        return self.custom_limits or parent_limits
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sub_account_id": self.sub_account_id,
            "parent_account_id": self.parent_account_id,
            "name": self.name,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Account:
    """Main account for users/organizations."""
    account_id: str
    name: str
    email: str
    
    # Tier and status
    tier: AccountTier = AccountTier.FREE
    status: AccountStatus = AccountStatus.ACTIVE
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Sub-accounts
    sub_accounts: List[SubAccount] = field(default_factory=list)
    
    # Current usage
    current_usage: Optional[UsageRecord] = None
    
    # Billing
    billing_email: Optional[str] = None
    payment_method_id: Optional[str] = None
    
    @property
    def limits(self) -> UsageLimits:
        """Get account limits."""
        return UsageLimits.for_tier(self.tier)
    
    def can_create_sub_account(self) -> bool:
        """Check if sub-accounts allowed."""
        return self.limits.allow_sub_accounts
    
    def get_usage_percentage(self, field: str) -> float:
        """Get usage as percentage of limit."""
        if not self.current_usage:
            return 0.0
        
        limits = self.limits
        usage_map = {
            "minutes": (self.current_usage.call_minutes, limits.max_monthly_minutes),
            "agents": (self.current_usage.agents_used, limits.max_agents),
            "campaigns": (self.current_usage.campaigns_run, limits.max_campaigns_per_month),
        }
        
        current, limit = usage_map.get(field, (0, 1))
        if limit == 0:
            return 100.0 if current > 0 else 0.0
        return (current / limit) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "account_id": self.account_id,
            "name": self.name,
            "email": self.email,
            "tier": self.tier.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "sub_account_count": len(self.sub_accounts),
        }
