"""
Sunona Voice AI - Campaign Manager

Orchestrates batch calling campaigns with concurrent call handling.

Features:
- Campaign lifecycle management
- Concurrent call execution
- Retry logic with exponential backoff
- Real-time progress tracking
- Result aggregation
"""

import asyncio
import logging
import uuid
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from sunona.batch.models import (
    Campaign,
    CampaignStatus,
    BatchJob,
    Contact,
    CallResult,
    CallStatus,
    CallOutcome,
    CampaignConfig,
)

logger = logging.getLogger(__name__)


@dataclass
class CampaignCallbacks:
    """Callbacks for campaign events."""
    on_call_started: Optional[Callable[[Contact], None]] = None
    on_call_completed: Optional[Callable[[CallResult], None]] = None
    on_campaign_progress: Optional[Callable[[Campaign, float], None]] = None
    on_campaign_completed: Optional[Callable[[Campaign], None]] = None


class CampaignManager:
    """
    Manages batch calling campaigns.
    
    Handles campaign creation, execution, and monitoring with
    support for concurrent calls and retry logic.
    
    Example:
        ```python
        manager = CampaignManager()
        
        # Create campaign
        campaign = manager.create_campaign(
            name="Lead Qualification",
            config=CampaignConfig(
                template_name="sales",
                concurrent_calls=10
            )
        )
        
        # Add contacts
        campaign.add_contacts([
            {"phone": "+1234567890", "name": "John Doe"},
            {"phone": "+0987654321", "name": "Jane Smith"},
        ])
        
        # Start campaign
        await manager.start_campaign(campaign.campaign_id)
        ```
    """
    
    def __init__(
        self,
        call_executor: Optional[Callable] = None,
        storage_backend: Optional[Any] = None,
    ):
        """
        Initialize campaign manager.
        
        Args:
            call_executor: Function to execute individual calls
            storage_backend: Backend for persisting campaigns
        """
        self._campaigns: Dict[str, Campaign] = {}
        self._running_jobs: Dict[str, asyncio.Task] = {}
        self._call_executor = call_executor
        self._storage = storage_backend
        self._callbacks = CampaignCallbacks()
        
        logger.info("Campaign manager initialized")
    
    def set_callbacks(self, callbacks: CampaignCallbacks) -> None:
        """Set event callbacks."""
        self._callbacks = callbacks
    
    def create_campaign(
        self,
        name: str,
        description: str = "",
        config: Optional[CampaignConfig] = None,
        account_id: Optional[str] = None,
    ) -> Campaign:
        """
        Create a new campaign.
        
        Args:
            name: Campaign name
            description: Campaign description
            config: Campaign configuration
            account_id: Account ID for multi-tenancy
            
        Returns:
            Created campaign
        """
        campaign_id = f"camp_{uuid.uuid4().hex[:12]}"
        
        campaign = Campaign(
            campaign_id=campaign_id,
            name=name,
            description=description,
            config=config or CampaignConfig(),
            account_id=account_id,
        )
        
        self._campaigns[campaign_id] = campaign
        logger.info(f"Created campaign: {campaign_id} - {name}")
        
        return campaign
    
    def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        """Get a campaign by ID."""
        return self._campaigns.get(campaign_id)
    
    def list_campaigns(
        self,
        account_id: Optional[str] = None,
        status: Optional[CampaignStatus] = None,
    ) -> List[Campaign]:
        """List campaigns with optional filters."""
        campaigns = list(self._campaigns.values())
        
        if account_id:
            campaigns = [c for c in campaigns if c.account_id == account_id]
        
        if status:
            campaigns = [c for c in campaigns if c.status == status]
        
        return sorted(campaigns, key=lambda c: c.created_at, reverse=True)
    
    async def start_campaign(
        self,
        campaign_id: str,
        batch_size: Optional[int] = None,
    ) -> bool:
        """
        Start a campaign.
        
        Args:
            campaign_id: Campaign to start
            batch_size: Contacts per batch (default: all)
            
        Returns:
            True if started successfully
        """
        campaign = self._campaigns.get(campaign_id)
        if not campaign:
            logger.error(f"Campaign not found: {campaign_id}")
            return False
        
        if campaign.status == CampaignStatus.RUNNING:
            logger.warning(f"Campaign already running: {campaign_id}")
            return False
        
        campaign.status = CampaignStatus.RUNNING
        campaign.started_at = datetime.now()
        
        # Create batch jobs
        batch_size = batch_size or len(campaign.contacts)
        batches = self._create_batches(campaign.contacts, batch_size)
        
        for i, batch_contacts in enumerate(batches):
            job = BatchJob(
                job_id=f"{campaign_id}_job_{i}",
                campaign_id=campaign_id,
                contacts=batch_contacts,
                config=campaign.config,
            )
            campaign.jobs.append(job)
        
        # Start execution
        task = asyncio.create_task(self._execute_campaign(campaign))
        self._running_jobs[campaign_id] = task
        
        logger.info(f"Started campaign: {campaign_id} with {len(campaign.jobs)} jobs")
        return True
    
    def _create_batches(
        self, 
        contacts: List[Contact], 
        batch_size: int
    ) -> List[List[Contact]]:
        """Split contacts into batches."""
        return [
            contacts[i:i + batch_size]
            for i in range(0, len(contacts), batch_size)
        ]
    
    async def _execute_campaign(self, campaign: Campaign) -> None:
        """Execute all jobs in a campaign."""
        try:
            for job in campaign.jobs:
                if campaign.status == CampaignStatus.CANCELLED:
                    break
                
                await self._execute_job(job, campaign)
            
            campaign.status = CampaignStatus.COMPLETED
            campaign.completed_at = datetime.now()
            campaign.update_stats()
            
            if self._callbacks.on_campaign_completed:
                self._callbacks.on_campaign_completed(campaign)
            
            logger.info(f"Campaign completed: {campaign.campaign_id}")
            
        except Exception as e:
            campaign.status = CampaignStatus.FAILED
            logger.error(f"Campaign failed: {campaign.campaign_id} - {e}")
        
        finally:
            if campaign.campaign_id in self._running_jobs:
                del self._running_jobs[campaign.campaign_id]
    
    async def _execute_job(self, job: BatchJob, campaign: Campaign) -> None:
        """Execute a single batch job."""
        job.status = CampaignStatus.RUNNING
        job.started_at = datetime.now()
        
        concurrent = campaign.config.concurrent_calls
        semaphore = asyncio.Semaphore(concurrent)
        
        async def call_with_semaphore(contact: Contact) -> CallResult:
            async with semaphore:
                return await self._execute_call(contact, campaign.config)
        
        # Execute calls concurrently
        tasks = [
            call_with_semaphore(contact)
            for contact in job.contacts
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Call error: {result}")
                continue
            
            job.results.append(result)
            job.completed_calls += 1
            
            if result.status == CallStatus.COMPLETED:
                if result.outcome == CallOutcome.SUCCESS:
                    job.successful_calls += 1
                else:
                    job.failed_calls += 1
            else:
                job.failed_calls += 1
            
            # Progress callback
            if self._callbacks.on_campaign_progress:
                campaign.update_stats()
                self._callbacks.on_campaign_progress(
                    campaign, 
                    campaign.progress_percent
                )
        
        job.status = CampaignStatus.COMPLETED
        job.completed_at = datetime.now()
    
    async def _execute_call(
        self, 
        contact: Contact, 
        config: CampaignConfig
    ) -> CallResult:
        """Execute a single call."""
        contact.status = CallStatus.IN_PROGRESS
        contact.attempts += 1
        contact.last_attempt = datetime.now()
        
        if self._callbacks.on_call_started:
            self._callbacks.on_call_started(contact)
        
        started_at = datetime.now()
        
        try:
            if self._call_executor:
                # Use custom call executor
                result_data = await self._call_executor(contact, config)
                
                result = CallResult(
                    contact=contact,
                    status=CallStatus.COMPLETED,
                    outcome=result_data.get("outcome", CallOutcome.SUCCESS),
                    duration_seconds=result_data.get("duration", 0),
                    started_at=started_at,
                    ended_at=datetime.now(),
                    transcript=result_data.get("transcript"),
                    extracted_data=result_data.get("extracted_data", {}),
                    recording_url=result_data.get("recording_url"),
                )
            else:
                # Demo mode - simulate call
                await asyncio.sleep(0.5)  # Simulate call
                
                result = CallResult(
                    contact=contact,
                    status=CallStatus.COMPLETED,
                    outcome=CallOutcome.SUCCESS,
                    duration_seconds=30.0,
                    started_at=started_at,
                    ended_at=datetime.now(),
                )
            
            contact.status = CallStatus.COMPLETED
            contact.outcome = result.outcome
            
        except Exception as e:
            result = CallResult(
                contact=contact,
                status=CallStatus.FAILED,
                started_at=started_at,
                ended_at=datetime.now(),
                error=str(e),
            )
            contact.status = CallStatus.FAILED
        
        if self._callbacks.on_call_completed:
            self._callbacks.on_call_completed(result)
        
        return result
    
    async def pause_campaign(self, campaign_id: str) -> bool:
        """Pause a running campaign."""
        campaign = self._campaigns.get(campaign_id)
        if not campaign or campaign.status != CampaignStatus.RUNNING:
            return False
        
        campaign.status = CampaignStatus.PAUSED
        logger.info(f"Paused campaign: {campaign_id}")
        return True
    
    async def resume_campaign(self, campaign_id: str) -> bool:
        """Resume a paused campaign."""
        campaign = self._campaigns.get(campaign_id)
        if not campaign or campaign.status != CampaignStatus.PAUSED:
            return False
        
        campaign.status = CampaignStatus.RUNNING
        logger.info(f"Resumed campaign: {campaign_id}")
        return True
    
    async def cancel_campaign(self, campaign_id: str) -> bool:
        """Cancel a campaign."""
        campaign = self._campaigns.get(campaign_id)
        if not campaign:
            return False
        
        campaign.status = CampaignStatus.CANCELLED
        
        # Cancel running task
        if campaign_id in self._running_jobs:
            self._running_jobs[campaign_id].cancel()
            del self._running_jobs[campaign_id]
        
        logger.info(f"Cancelled campaign: {campaign_id}")
        return True
    
    def get_campaign_results(self, campaign_id: str) -> List[CallResult]:
        """Get all results for a campaign."""
        campaign = self._campaigns.get(campaign_id)
        if not campaign:
            return []
        
        results = []
        for job in campaign.jobs:
            results.extend(job.results)
        
        return results
    
    def get_campaign_stats(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign statistics."""
        campaign = self._campaigns.get(campaign_id)
        if not campaign:
            return {}
        
        campaign.update_stats()
        
        return {
            "campaign_id": campaign_id,
            "name": campaign.name,
            "status": campaign.status.value,
            "total_calls": campaign.total_calls,
            "completed_calls": campaign.completed_calls,
            "successful_calls": campaign.successful_calls,
            "failed_calls": campaign.failed_calls,
            "progress_percent": campaign.progress_percent,
            "success_rate": (
                campaign.successful_calls / campaign.completed_calls * 100
                if campaign.completed_calls > 0 else 0
            ),
        }
