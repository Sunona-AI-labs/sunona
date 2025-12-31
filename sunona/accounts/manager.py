"""
Sunona Voice AI - Account Manager

Manage accounts, sub-accounts, and usage tracking.
"""

import logging
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime

from sunona.accounts.models import (
    Account,
    SubAccount,
    UsageRecord,
    AccountTier,
    AccountStatus,
    UsageLimits,
)

logger = logging.getLogger(__name__)


class AccountManager:
    """
    Manage multi-tenant accounts and usage.
    
    Features:
        - Account CRUD operations
        - Sub-account management
        - Usage tracking and limits
        - Tier management
    
    Example:
        ```python
        manager = AccountManager()
        
        # Create account
        account = manager.create_account(
            name="Acme Corp",
            email="admin@acme.com",
            tier=AccountTier.PROFESSIONAL
        )
        
        # Create sub-account
        sub = manager.create_sub_account(
            parent_id=account.account_id,
            name="Sales Team"
        )
        
        # Track usage
        manager.record_usage(
            account_id=account.account_id,
            call_minutes=5.5,
            llm_cost=0.02
        )
        ```
    """
    
    def __init__(self, storage_backend=None):
        """
        Initialize account manager.
        
        Args:
            storage_backend: Optional database backend
        """
        self._accounts: Dict[str, Account] = {}
        self._storage = storage_backend
        
        logger.info("Account manager initialized")
    
    def create_account(
        self,
        name: str,
        email: str,
        tier: AccountTier = AccountTier.FREE,
    ) -> Account:
        """
        Create a new account.
        
        Args:
            name: Account/organization name
            email: Primary email
            tier: Account tier
            
        Returns:
            Created account
        """
        account_id = f"acc_{uuid.uuid4().hex[:12]}"
        
        account = Account(
            account_id=account_id,
            name=name,
            email=email,
            tier=tier,
        )
        
        # Initialize usage record
        period = datetime.now().strftime("%Y-%m")
        account.current_usage = UsageRecord(
            record_id=f"usage_{account_id}_{period}",
            account_id=account_id,
            period=period,
        )
        
        self._accounts[account_id] = account
        logger.info(f"Created account: {account_id} - {name}")
        
        return account
    
    def get_account(self, account_id: str) -> Optional[Account]:
        """Get account by ID."""
        return self._accounts.get(account_id)
    
    def list_accounts(
        self,
        tier: Optional[AccountTier] = None,
        status: Optional[AccountStatus] = None,
    ) -> List[Account]:
        """List accounts with optional filters."""
        accounts = list(self._accounts.values())
        
        if tier:
            accounts = [a for a in accounts if a.tier == tier]
        
        if status:
            accounts = [a for a in accounts if a.status == status]
        
        return accounts
    
    def update_tier(
        self,
        account_id: str,
        new_tier: AccountTier,
    ) -> bool:
        """Update account tier."""
        account = self._accounts.get(account_id)
        if not account:
            return False
        
        old_tier = account.tier
        account.tier = new_tier
        account.updated_at = datetime.now()
        
        logger.info(f"Updated tier for {account_id}: {old_tier.value} -> {new_tier.value}")
        return True
    
    def suspend_account(self, account_id: str) -> bool:
        """Suspend an account."""
        account = self._accounts.get(account_id)
        if not account:
            return False
        
        account.status = AccountStatus.SUSPENDED
        account.updated_at = datetime.now()
        
        logger.info(f"Suspended account: {account_id}")
        return True
    
    def create_sub_account(
        self,
        parent_id: str,
        name: str,
        custom_limits: Optional[UsageLimits] = None,
    ) -> Optional[SubAccount]:
        """
        Create a sub-account.
        
        Args:
            parent_id: Parent account ID
            name: Sub-account name
            custom_limits: Optional custom limits
            
        Returns:
            Created sub-account or None
        """
        parent = self._accounts.get(parent_id)
        if not parent:
            logger.error(f"Parent account not found: {parent_id}")
            return None
        
        if not parent.can_create_sub_account():
            logger.error(f"Account {parent_id} cannot create sub-accounts")
            return None
        
        sub_id = f"sub_{uuid.uuid4().hex[:12]}"
        
        sub = SubAccount(
            sub_account_id=sub_id,
            parent_account_id=parent_id,
            name=name,
            custom_limits=custom_limits,
        )
        
        parent.sub_accounts.append(sub)
        
        logger.info(f"Created sub-account: {sub_id} under {parent_id}")
        
        return sub
    
    def get_sub_account(
        self,
        parent_id: str,
        sub_id: str,
    ) -> Optional[SubAccount]:
        """Get a sub-account."""
        parent = self._accounts.get(parent_id)
        if not parent:
            return None
        
        for sub in parent.sub_accounts:
            if sub.sub_account_id == sub_id:
                return sub
        
        return None
    
    def list_sub_accounts(self, parent_id: str) -> List[SubAccount]:
        """List sub-accounts for an account."""
        parent = self._accounts.get(parent_id)
        if not parent:
            return []
        
        return parent.sub_accounts
    
    def record_usage(
        self,
        account_id: str,
        call_minutes: float = 0.0,
        calls: int = 0,
        llm_cost: float = 0.0,
        stt_cost: float = 0.0,
        tts_cost: float = 0.0,
        telephony_cost: float = 0.0,
    ) -> bool:
        """
        Record usage for an account.
        
        Args:
            account_id: Account to record for
            call_minutes: Minutes used
            calls: Number of calls
            llm_cost: LLM cost
            stt_cost: STT cost
            tts_cost: TTS cost
            telephony_cost: Telephony cost
            
        Returns:
            True if recorded
        """
        account = self._accounts.get(account_id)
        if not account:
            return False
        
        # Ensure usage record exists
        period = datetime.now().strftime("%Y-%m")
        if not account.current_usage or account.current_usage.period != period:
            account.current_usage = UsageRecord(
                record_id=f"usage_{account_id}_{period}",
                account_id=account_id,
                period=period,
            )
        
        usage = account.current_usage
        usage.call_minutes += call_minutes
        usage.total_calls += calls
        usage.llm_cost += llm_cost
        usage.stt_cost += stt_cost
        usage.tts_cost += tts_cost
        usage.telephony_cost += telephony_cost
        
        return True
    
    def check_limits(
        self,
        account_id: str,
    ) -> Dict[str, Any]:
        """
        Check account usage against limits.
        
        Returns:
            Dict with limit status
        """
        account = self._accounts.get(account_id)
        if not account:
            return {"error": "Account not found"}
        
        limits = account.limits
        usage = account.current_usage
        
        if not usage:
            return {"within_limits": True}
        
        return {
            "within_limits": (
                usage.call_minutes < limits.max_monthly_minutes and
                usage.agents_used <= limits.max_agents
            ),
            "minutes_used": usage.call_minutes,
            "minutes_limit": limits.max_monthly_minutes,
            "minutes_remaining": max(0, limits.max_monthly_minutes - usage.call_minutes),
            "agents_used": usage.agents_used,
            "agents_limit": limits.max_agents,
        }
    
    def get_billing_summary(
        self,
        account_id: str,
        period: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get billing summary for an account."""
        account = self._accounts.get(account_id)
        if not account:
            return {}
        
        usage = account.current_usage
        if not usage:
            return {"total_cost": 0.0}
        
        return {
            "account_id": account_id,
            "period": usage.period,
            "total_minutes": usage.call_minutes,
            "total_calls": usage.total_calls,
            "llm_cost": usage.llm_cost,
            "stt_cost": usage.stt_cost,
            "tts_cost": usage.tts_cost,
            "telephony_cost": usage.telephony_cost,
            "total_cost": usage.total_cost,
        }
