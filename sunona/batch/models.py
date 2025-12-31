"""
Sunona Voice AI - Batch Models

Data models for batch calling campaigns.
"""

import re
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pydantic import BaseModel, Field, validator


# Phone validation regex (E.164 format)
PHONE_REGEX = re.compile(r'^\+?[1-9]\d{1,14}$')


class CampaignStatus(str, Enum):
    """Status of a campaign."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CallStatus(str, Enum):
    """Status of individual call."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NO_ANSWER = "no_answer"
    BUSY = "busy"
    VOICEMAIL = "voicemail"
    CANCELLED = "cancelled"


class CallOutcome(str, Enum):
    """Outcome of a completed call."""
    SUCCESS = "success"
    CALLBACK_REQUESTED = "callback_requested"
    NOT_INTERESTED = "not_interested"
    WRONG_NUMBER = "wrong_number"
    DO_NOT_CALL = "do_not_call"
    TRANSFERRED = "transferred"
    INCOMPLETE = "incomplete"


@dataclass
class Contact:
    """A contact to call."""
    phone: str
    name: Optional[str] = None
    email: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Call tracking
    attempts: int = 0
    last_attempt: Optional[datetime] = None
    status: CallStatus = CallStatus.PENDING
    outcome: Optional[CallOutcome] = None
    
    def __post_init__(self):
        """Validate phone number format."""
        # Normalize phone number
        if self.phone:
            self.phone = self.phone.strip().replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            if not self.phone.startswith('+'):
                # Assume E.164 without +
                self.phone = '+' + self.phone if self.phone else self.phone
    
    @property
    def is_valid_phone(self) -> bool:
        """Check if phone number is valid E.164 format."""
        if not self.phone:
            return False
        return bool(PHONE_REGEX.match(self.phone))


@dataclass
class CallResult:
    """Result of a single call."""
    contact: Contact
    status: CallStatus
    outcome: Optional[CallOutcome] = None
    duration_seconds: float = 0.0
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    transcript: Optional[str] = None
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    recording_url: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "phone": self.contact.phone,
            "name": self.contact.name,
            "status": self.status.value,
            "outcome": self.outcome.value if self.outcome else None,
            "duration_seconds": self.duration_seconds,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "transcript": self.transcript,
            "extracted_data": self.extracted_data,
            "error": self.error,
        }


class CampaignConfig(BaseModel):
    """Configuration for a batch campaign."""
    
    # Agent configuration
    agent_id: Optional[str] = None
    system_prompt: Optional[str] = None
    template_name: Optional[str] = None
    template_config: Dict[str, Any] = Field(default_factory=dict)
    
    # Provider settings
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    stt_provider: str = "deepgram"
    tts_provider: str = "elevenlabs"
    telephony_provider: str = "twilio"
    
    # Call settings
    max_call_duration_seconds: int = 300  # 5 minutes
    max_retries: int = 2
    retry_delay_minutes: int = 60
    concurrent_calls: int = 5
    
    # Schedule settings
    call_window_start: str = "09:00"  # 9 AM
    call_window_end: str = "18:00"    # 6 PM
    timezone: str = "UTC"
    exclude_weekends: bool = True
    
    # Voice settings
    voice_id: Optional[str] = None
    speaking_rate: float = 1.0
    
    class Config:
        extra = "allow"


@dataclass
class BatchJob:
    """A batch job within a campaign."""
    job_id: str
    campaign_id: str
    contacts: List[Contact]
    config: CampaignConfig
    
    # Status
    status: CampaignStatus = CampaignStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results
    results: List[CallResult] = field(default_factory=list)
    
    # Progress
    total_calls: int = 0
    completed_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    
    def __post_init__(self):
        self.total_calls = len(self.contacts)
    
    @property
    def progress_percent(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return (self.completed_calls / self.total_calls) * 100
    
    @property
    def success_rate(self) -> float:
        if self.completed_calls == 0:
            return 0.0
        return (self.successful_calls / self.completed_calls) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "campaign_id": self.campaign_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_calls": self.total_calls,
            "completed_calls": self.completed_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "progress_percent": self.progress_percent,
            "success_rate": self.success_rate,
        }


@dataclass
class Campaign:
    """A batch calling campaign."""
    campaign_id: str
    name: str
    description: str = ""
    config: CampaignConfig = field(default_factory=CampaignConfig)
    
    # Status
    status: CampaignStatus = CampaignStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Contact list
    contacts: List[Contact] = field(default_factory=list)
    
    # Jobs
    jobs: List[BatchJob] = field(default_factory=list)
    
    # Aggregate stats
    total_calls: int = 0
    completed_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    
    # Account
    account_id: Optional[str] = None
    created_by: Optional[str] = None
    
    def add_contacts(self, contacts: List[Dict[str, Any]], validate: bool = True) -> int:
        """
        Add contacts to the campaign.
        
        Args:
            contacts: List of contact dictionaries
            validate: If True, only add contacts with valid phone numbers
            
        Returns:
            Number of contacts added
        """
        added = 0
        skipped = 0
        
        for c in contacts:
            contact = Contact(
                phone=c.get("phone", ""),
                name=c.get("name"),
                email=c.get("email"),
                metadata=c.get("metadata", {}),
            )
            
            if not contact.phone:
                skipped += 1
                continue
            
            if validate and not contact.is_valid_phone:
                skipped += 1
                continue
            
            self.contacts.append(contact)
            added += 1
        
        self.total_calls = len(self.contacts)
        return added
    
    def update_stats(self) -> None:
        """Update aggregate statistics from jobs."""
        self.completed_calls = sum(j.completed_calls for j in self.jobs)
        self.successful_calls = sum(j.successful_calls for j in self.jobs)
        self.failed_calls = sum(j.failed_calls for j in self.jobs)
    
    @property
    def progress_percent(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return (self.completed_calls / self.total_calls) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "campaign_id": self.campaign_id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_calls": self.total_calls,
            "completed_calls": self.completed_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "progress_percent": self.progress_percent,
            "job_count": len(self.jobs),
        }
