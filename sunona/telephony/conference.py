"""
Sunona Voice AI - Conference Bridging

Multi-party call conferencing and bridging.
"""

import asyncio
import logging
import uuid
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ConferenceStatus(str, Enum):
    """Conference status."""
    WAITING = "waiting"
    ACTIVE = "active"
    ENDED = "ended"


class ParticipantRole(str, Enum):
    """Participant role in conference."""
    MODERATOR = "moderator"
    PARTICIPANT = "participant"
    LISTENER = "listener"


@dataclass
class Participant:
    """A participant in a conference."""
    participant_id: str
    call_sid: str
    phone: Optional[str] = None
    name: Optional[str] = None
    role: ParticipantRole = ParticipantRole.PARTICIPANT
    
    # State
    is_muted: bool = False
    joined_at: Optional[datetime] = None
    left_at: Optional[datetime] = None
    
    @property
    def is_active(self) -> bool:
        return self.joined_at is not None and self.left_at is None


@dataclass
class Conference:
    """A conference call."""
    conference_id: str
    name: str
    
    # Config
    max_participants: int = 10
    record: bool = False
    announce_joins: bool = True
    
    # State
    status: ConferenceStatus = ConferenceStatus.WAITING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    
    # Participants
    participants: List[Participant] = field(default_factory=list)
    
    # Recording
    recording_url: Optional[str] = None
    
    @property
    def active_participants(self) -> List[Participant]:
        return [p for p in self.participants if p.is_active]
    
    @property
    def participant_count(self) -> int:
        return len(self.active_participants)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "conference_id": self.conference_id,
            "name": self.name,
            "status": self.status.value,
            "participant_count": self.participant_count,
            "max_participants": self.max_participants,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
        }


class ConferenceManager:
    """
    Manage conference calls and bridging.
    
    Supports creating conferences, adding participants,
    and managing multi-party calls.
    
    Example:
        ```python
        manager = ConferenceManager(telephony_handler)
        
        # Create conference
        conf = manager.create_conference("Team Meeting")
        
        # Add participants
        await manager.add_participant(
            conference_id=conf.conference_id,
            phone="+1234567890",
            role=ParticipantRole.MODERATOR
        )
        
        await manager.add_participant(
            conference_id=conf.conference_id,
            phone="+0987654321"
        )
        ```
    """
    
    def __init__(
        self,
        telephony_handler=None,
        on_conference_start: Optional[Callable] = None,
        on_conference_end: Optional[Callable] = None,
    ):
        """
        Initialize conference manager.
        
        Args:
            telephony_handler: Telephony handler for calls
            on_conference_start: Callback when conference starts
            on_conference_end: Callback when conference ends
        """
        self._telephony = telephony_handler
        self._conferences: Dict[str, Conference] = {}
        self._on_start = on_conference_start
        self._on_end = on_conference_end
        
        logger.info("Conference manager initialized")
    
    def create_conference(
        self,
        name: str,
        max_participants: int = 10,
        record: bool = False,
        announce_joins: bool = True,
    ) -> Conference:
        """
        Create a new conference.
        
        Args:
            name: Conference name
            max_participants: Max allowed participants
            record: Whether to record
            announce_joins: Announce when people join
            
        Returns:
            Created conference
        """
        conf_id = f"conf_{uuid.uuid4().hex[:12]}"
        
        conference = Conference(
            conference_id=conf_id,
            name=name,
            max_participants=max_participants,
            record=record,
            announce_joins=announce_joins,
        )
        
        self._conferences[conf_id] = conference
        
        logger.info(f"Created conference: {conf_id} - {name}")
        
        return conference
    
    def get_conference(self, conference_id: str) -> Optional[Conference]:
        """Get conference by ID."""
        return self._conferences.get(conference_id)
    
    def list_conferences(
        self,
        status: Optional[ConferenceStatus] = None,
    ) -> List[Conference]:
        """List conferences."""
        conferences = list(self._conferences.values())
        
        if status:
            conferences = [c for c in conferences if c.status == status]
        
        return conferences
    
    async def add_participant(
        self,
        conference_id: str,
        phone: Optional[str] = None,
        call_sid: Optional[str] = None,
        name: Optional[str] = None,
        role: ParticipantRole = ParticipantRole.PARTICIPANT,
    ) -> Optional[Participant]:
        """
        Add a participant to a conference.
        
        Args:
            conference_id: Conference to add to
            phone: Phone number to dial
            call_sid: Existing call SID to bridge
            name: Participant name
            role: Participant role
            
        Returns:
            Added participant or None
        """
        conference = self._conferences.get(conference_id)
        if not conference:
            logger.error(f"Conference not found: {conference_id}")
            return None
        
        if conference.participant_count >= conference.max_participants:
            logger.error(f"Conference {conference_id} is full")
            return None
        
        participant_id = f"part_{uuid.uuid4().hex[:8]}"
        
        # If phone provided, initiate call
        if phone and self._telephony:
            # Generate conference TwiML/BXML
            twiml = self._generate_conference_twiml(conference)
            call_sid = self._telephony.make_call(to=phone, twiml=twiml)
        
        if not call_sid:
            logger.error("No call_sid available")
            return None
        
        participant = Participant(
            participant_id=participant_id,
            call_sid=call_sid,
            phone=phone,
            name=name,
            role=role,
            joined_at=datetime.now(),
        )
        
        conference.participants.append(participant)
        
        # Start conference if first participant
        if conference.status == ConferenceStatus.WAITING:
            conference.status = ConferenceStatus.ACTIVE
            conference.started_at = datetime.now()
            
            if self._on_start:
                self._on_start(conference)
        
        logger.info(f"Added participant {participant_id} to {conference_id}")
        
        return participant
    
    def _generate_conference_twiml(self, conference: Conference) -> str:
        """Generate TwiML for joining conference."""
        record_attr = 'record="record-from-start"' if conference.record else ""
        
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Dial>
        <Conference 
            {record_attr}
            startConferenceOnEnter="true"
            endConferenceOnExit="false"
            waitUrl="https://twimlets.com/holdmusic?Bucket=com.twilio.music.classical">
            {conference.name}
        </Conference>
    </Dial>
</Response>'''
    
    async def remove_participant(
        self,
        conference_id: str,
        participant_id: str,
    ) -> bool:
        """Remove a participant from conference."""
        conference = self._conferences.get(conference_id)
        if not conference:
            return False
        
        for participant in conference.participants:
            if participant.participant_id == participant_id:
                participant.left_at = datetime.now()
                
                # Hang up the call
                if self._telephony and participant.call_sid:
                    self._telephony.hangup(participant.call_sid)
                
                logger.info(f"Removed participant {participant_id}")
                
                # End conference if empty
                if conference.participant_count == 0:
                    await self.end_conference(conference_id)
                
                return True
        
        return False
    
    def mute_participant(
        self,
        conference_id: str,
        participant_id: str,
        muted: bool = True,
    ) -> bool:
        """Mute/unmute a participant."""
        conference = self._conferences.get(conference_id)
        if not conference:
            return False
        
        for participant in conference.participants:
            if participant.participant_id == participant_id:
                participant.is_muted = muted
                logger.info(f"{'Muted' if muted else 'Unmuted'} {participant_id}")
                return True
        
        return False
    
    async def end_conference(self, conference_id: str) -> bool:
        """End a conference."""
        conference = self._conferences.get(conference_id)
        if not conference:
            return False
        
        conference.status = ConferenceStatus.ENDED
        conference.ended_at = datetime.now()
        
        # Remove all participants
        for participant in conference.active_participants:
            participant.left_at = datetime.now()
            if self._telephony and participant.call_sid:
                self._telephony.hangup(participant.call_sid)
        
        if self._on_end:
            self._on_end(conference)
        
        logger.info(f"Ended conference: {conference_id}")
        
        return True
    
    async def bridge_calls(
        self,
        call_sid_1: str,
        call_sid_2: str,
        conference_name: Optional[str] = None,
    ) -> Optional[Conference]:
        """
        Bridge two existing calls into a conference.
        
        Args:
            call_sid_1: First call SID
            call_sid_2: Second call SID
            conference_name: Name for the bridge
            
        Returns:
            Conference for the bridge
        """
        name = conference_name or f"bridge_{uuid.uuid4().hex[:6]}"
        
        conference = self.create_conference(
            name=name,
            max_participants=2,
        )
        
        # Add both calls to conference
        await self.add_participant(
            conference_id=conference.conference_id,
            call_sid=call_sid_1,
        )
        
        await self.add_participant(
            conference_id=conference.conference_id,
            call_sid=call_sid_2,
        )
        
        return conference
