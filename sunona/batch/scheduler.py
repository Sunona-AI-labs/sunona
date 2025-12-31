"""
Sunona Voice AI - Batch Scheduler

Schedule batch calling campaigns with time-based rules.

Features:
- Cron-like scheduling
- Time window enforcement
- Timezone support
- Holiday exclusions
"""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime, time, timedelta
from dataclasses import dataclass, field
from enum import Enum
import calendar

logger = logging.getLogger(__name__)


class ScheduleType(str, Enum):
    """Types of schedule."""
    IMMEDIATE = "immediate"     # Start now
    SCHEDULED = "scheduled"     # Start at specific time
    RECURRING = "recurring"     # Repeat on schedule


@dataclass
class TimeWindow:
    """Time window for calling."""
    start_time: time = time(9, 0)   # 9 AM
    end_time: time = time(18, 0)    # 6 PM
    timezone: str = "UTC"
    exclude_weekends: bool = True
    exclude_holidays: List[str] = field(default_factory=list)  # YYYY-MM-DD
    
    def is_within_window(self, dt: Optional[datetime] = None) -> bool:
        """Check if current time is within calling window."""
        dt = dt or datetime.now()
        current_time = dt.time()
        
        # Check weekend
        if self.exclude_weekends and dt.weekday() >= 5:
            return False
        
        # Check holiday
        date_str = dt.strftime("%Y-%m-%d")
        if date_str in self.exclude_holidays:
            return False
        
        # Check time window
        return self.start_time <= current_time <= self.end_time
    
    def next_available_time(self, dt: Optional[datetime] = None) -> datetime:
        """Get next available time within window."""
        dt = dt or datetime.now()
        
        # If currently in window, return now
        if self.is_within_window(dt):
            return dt
        
        # Move to start of next valid day
        next_dt = dt
        
        # If past end time, move to next day
        if dt.time() > self.end_time:
            next_dt = next_dt + timedelta(days=1)
        
        # Set to window start time
        next_dt = next_dt.replace(
            hour=self.start_time.hour,
            minute=self.start_time.minute,
            second=0,
            microsecond=0
        )
        
        # Skip weekends if needed
        while self.exclude_weekends and next_dt.weekday() >= 5:
            next_dt = next_dt + timedelta(days=1)
        
        # Skip holidays
        while next_dt.strftime("%Y-%m-%d") in self.exclude_holidays:
            next_dt = next_dt + timedelta(days=1)
        
        return next_dt


@dataclass
class Schedule:
    """Schedule configuration for a campaign."""
    schedule_id: str
    campaign_id: str
    schedule_type: ScheduleType = ScheduleType.IMMEDIATE
    
    # For scheduled/recurring
    start_datetime: Optional[datetime] = None
    time_window: TimeWindow = field(default_factory=TimeWindow)
    
    # For recurring
    repeat_days: List[int] = field(default_factory=list)  # 0=Mon, 6=Sun
    repeat_interval_hours: int = 24
    max_occurrences: int = 1
    
    # State
    is_active: bool = True
    occurrences: int = 0
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None


class BatchScheduler:
    """
    Scheduler for batch calling campaigns.
    
    Handles time-based scheduling with support for:
    - Immediate execution
    - Scheduled execution
    - Recurring schedules
    - Time window enforcement
    
    Example:
        ```python
        scheduler = BatchScheduler(campaign_manager)
        
        # Schedule campaign for tomorrow at 10 AM
        await scheduler.schedule(
            campaign_id="camp_123",
            start_datetime=datetime(2024, 12, 28, 10, 0),
            time_window=TimeWindow(
                start_time=time(9, 0),
                end_time=time(17, 0),
                exclude_weekends=True
            )
        )
        
        # Start scheduler
        await scheduler.start()
        ```
    """
    
    def __init__(
        self,
        campaign_manager=None,
        check_interval_seconds: int = 60,
    ):
        """
        Initialize scheduler.
        
        Args:
            campaign_manager: Campaign manager instance
            check_interval_seconds: How often to check schedules
        """
        self._campaign_manager = campaign_manager
        self._check_interval = check_interval_seconds
        self._schedules: Dict[str, Schedule] = {}
        self._running = False
        self._task: Optional[asyncio.Task] = None
        
        logger.info("Batch scheduler initialized")
    
    def schedule(
        self,
        campaign_id: str,
        schedule_type: ScheduleType = ScheduleType.IMMEDIATE,
        start_datetime: Optional[datetime] = None,
        time_window: Optional[TimeWindow] = None,
        repeat_days: Optional[List[int]] = None,
        repeat_interval_hours: int = 24,
        max_occurrences: int = 1,
    ) -> Schedule:
        """
        Schedule a campaign.
        
        Args:
            campaign_id: Campaign to schedule
            schedule_type: Type of schedule
            start_datetime: When to start
            time_window: Calling time window
            repeat_days: Days to repeat (0=Mon)
            repeat_interval_hours: Repeat interval
            max_occurrences: Max times to run
            
        Returns:
            Created schedule
        """
        schedule_id = f"sched_{campaign_id}"
        
        schedule = Schedule(
            schedule_id=schedule_id,
            campaign_id=campaign_id,
            schedule_type=schedule_type,
            start_datetime=start_datetime or datetime.now(),
            time_window=time_window or TimeWindow(),
            repeat_days=repeat_days or [],
            repeat_interval_hours=repeat_interval_hours,
            max_occurrences=max_occurrences,
        )
        
        # Calculate next run
        schedule.next_run = self._calculate_next_run(schedule)
        
        self._schedules[schedule_id] = schedule
        logger.info(f"Scheduled campaign {campaign_id} for {schedule.next_run}")
        
        return schedule
    
    def _calculate_next_run(self, schedule: Schedule) -> Optional[datetime]:
        """Calculate next run time for a schedule."""
        if not schedule.is_active:
            return None
        
        if schedule.occurrences >= schedule.max_occurrences:
            return None
        
        if schedule.schedule_type == ScheduleType.IMMEDIATE:
            return datetime.now()
        
        if schedule.last_run is None:
            # First run
            base_time = schedule.start_datetime or datetime.now()
        else:
            # Subsequent run
            base_time = schedule.last_run + timedelta(
                hours=schedule.repeat_interval_hours
            )
        
        # Find next valid time in window
        return schedule.time_window.next_available_time(base_time)
    
    async def start(self) -> None:
        """Start the scheduler."""
        if self._running:
            logger.warning("Scheduler already running")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("Scheduler started")
    
    async def stop(self) -> None:
        """Stop the scheduler."""
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
        logger.info("Scheduler stopped")
    
    async def _run_loop(self) -> None:
        """Main scheduler loop."""
        while self._running:
            try:
                await self._check_schedules()
                await asyncio.sleep(self._check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(self._check_interval)
    
    async def _check_schedules(self) -> None:
        """Check and execute due schedules."""
        now = datetime.now()
        
        for schedule in list(self._schedules.values()):
            if not schedule.is_active:
                continue
            
            if schedule.next_run and schedule.next_run <= now:
                await self._execute_schedule(schedule)
    
    async def _execute_schedule(self, schedule: Schedule) -> None:
        """Execute a scheduled campaign."""
        logger.info(f"Executing schedule: {schedule.schedule_id}")
        
        try:
            if self._campaign_manager:
                await self._campaign_manager.start_campaign(
                    schedule.campaign_id
                )
            
            schedule.last_run = datetime.now()
            schedule.occurrences += 1
            
            # Calculate next run
            if schedule.schedule_type == ScheduleType.RECURRING:
                schedule.next_run = self._calculate_next_run(schedule)
            else:
                schedule.is_active = False
                schedule.next_run = None
            
        except Exception as e:
            logger.error(f"Schedule execution failed: {e}")
    
    def cancel_schedule(self, schedule_id: str) -> bool:
        """Cancel a schedule."""
        if schedule_id in self._schedules:
            self._schedules[schedule_id].is_active = False
            logger.info(f"Cancelled schedule: {schedule_id}")
            return True
        return False
    
    def get_schedule(self, schedule_id: str) -> Optional[Schedule]:
        """Get schedule by ID."""
        return self._schedules.get(schedule_id)
    
    def list_schedules(
        self, 
        active_only: bool = True
    ) -> List[Schedule]:
        """List all schedules."""
        schedules = list(self._schedules.values())
        if active_only:
            schedules = [s for s in schedules if s.is_active]
        return schedules
    
    def get_upcoming(self, hours: int = 24) -> List[Schedule]:
        """Get schedules due in the next N hours."""
        cutoff = datetime.now() + timedelta(hours=hours)
        
        upcoming = []
        for schedule in self._schedules.values():
            if schedule.is_active and schedule.next_run:
                if schedule.next_run <= cutoff:
                    upcoming.append(schedule)
        
        return sorted(upcoming, key=lambda s: s.next_run or datetime.max)
