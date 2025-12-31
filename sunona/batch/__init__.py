"""
Sunona Voice AI - Batch Calling Package

Automated outbound calling campaigns for scaled operations.

Features:
- Campaign management
- Batch job execution
- Scheduled calls
- Result aggregation
- Retry logic
"""

from sunona.batch.models import (
    Campaign,
    CampaignStatus,
    BatchJob,
    CallResult,
    CampaignConfig,
)
from sunona.batch.campaign_manager import CampaignManager
from sunona.batch.scheduler import BatchScheduler

__all__ = [
    "Campaign",
    "CampaignStatus",
    "BatchJob",
    "CallResult",
    "CampaignConfig",
    "CampaignManager",
    "BatchScheduler",
]
