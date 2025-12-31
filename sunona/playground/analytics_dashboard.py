"""
Sunona Voice AI - Analytics Dashboard

Real-time call metrics and analytics.
Provides insights into agent performance and usage.

Features:
- Real-time call statistics
- Agent performance metrics
- Cost tracking
- User engagement analytics
- Custom date ranges
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TimeRange(Enum):
    """Predefined time ranges."""
    LAST_HOUR = "last_hour"
    LAST_24H = "last_24h"
    LAST_7D = "last_7d"
    LAST_30D = "last_30d"
    CUSTOM = "custom"


@dataclass
class CallMetrics:
    """Aggregated call metrics."""
    total_calls: int = 0
    completed_calls: int = 0
    failed_calls: int = 0
    transferred_calls: int = 0
    
    total_duration_seconds: float = 0.0
    avg_duration_seconds: float = 0.0
    
    # By direction
    inbound_calls: int = 0
    outbound_calls: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_calls": self.total_calls,
            "completed_calls": self.completed_calls,
            "failed_calls": self.failed_calls,
            "transferred_calls": self.transferred_calls,
            "completion_rate": round(
                (self.completed_calls / max(1, self.total_calls)) * 100, 1
            ),
            "total_duration_seconds": round(self.total_duration_seconds, 0),
            "avg_duration_seconds": round(self.avg_duration_seconds, 1),
            "inbound_calls": self.inbound_calls,
            "outbound_calls": self.outbound_calls,
        }


@dataclass
class CostMetrics:
    """Cost breakdown metrics."""
    total_cost: float = 0.0
    
    stt_cost: float = 0.0
    llm_cost: float = 0.0
    tts_cost: float = 0.0
    telephony_cost: float = 0.0
    
    cost_per_call: float = 0.0
    cost_per_minute: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "total_cost": round(self.total_cost, 4),
            "breakdown": {
                "stt": round(self.stt_cost, 4),
                "llm": round(self.llm_cost, 4),
                "tts": round(self.tts_cost, 4),
                "telephony": round(self.telephony_cost, 4),
            },
            "cost_per_call": round(self.cost_per_call, 4),
            "cost_per_minute": round(self.cost_per_minute, 4),
        }


@dataclass
class AgentMetrics:
    """Per-agent performance metrics."""
    agent_id: str
    agent_name: str
    
    total_calls: int = 0
    successful_calls: int = 0
    avg_response_time_ms: float = 0.0
    avg_call_duration: float = 0.0
    customer_satisfaction: float = 0.0  # 0-5 scale
    
    # Conversation quality
    avg_turns_per_call: float = 0.0
    transfer_rate: float = 0.0
    resolution_rate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "total_calls": self.total_calls,
            "success_rate": round(
                (self.successful_calls / max(1, self.total_calls)) * 100, 1
            ),
            "avg_response_time_ms": round(self.avg_response_time_ms, 0),
            "avg_call_duration": round(self.avg_call_duration, 1),
            "customer_satisfaction": round(self.customer_satisfaction, 1),
            "avg_turns_per_call": round(self.avg_turns_per_call, 1),
            "transfer_rate": round(self.transfer_rate * 100, 1),
            "resolution_rate": round(self.resolution_rate * 100, 1),
        }


@dataclass
class TimeSeriesPoint:
    """A point in a time series."""
    timestamp: datetime
    value: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "value": self.value,
        }


@dataclass
class DashboardData:
    """Complete dashboard data."""
    # Summary
    call_metrics: CallMetrics
    cost_metrics: CostMetrics
    
    # Agent breakdown
    agent_metrics: List[AgentMetrics]
    
    # Time series
    calls_over_time: List[TimeSeriesPoint]
    cost_over_time: List[TimeSeriesPoint]
    
    # Top level stats
    active_calls: int = 0
    active_agents: int = 0
    
    # Time range
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": {
                "calls": self.call_metrics.to_dict(),
                "costs": self.cost_metrics.to_dict(),
                "active_calls": self.active_calls,
                "active_agents": self.active_agents,
            },
            "agents": [a.to_dict() for a in self.agent_metrics],
            "time_series": {
                "calls": [p.to_dict() for p in self.calls_over_time],
                "costs": [p.to_dict() for p in self.cost_over_time],
            },
            "time_range": {
                "start": self.start_time.isoformat() if self.start_time else None,
                "end": self.end_time.isoformat() if self.end_time else None,
            },
        }


class AnalyticsDashboard:
    """
    Analytics dashboard service.
    
    Provides real-time metrics and historical analytics
    for voice AI operations.
    
    Example:
        dashboard = AnalyticsDashboard()
        
        # Get dashboard data
        data = await dashboard.get_dashboard(
            organization_id="org_123",
            time_range=TimeRange.LAST_24H
        )
        
        # Get specific agent metrics
        agent_data = await dashboard.get_agent_metrics("agent_123")
        
        # Record events
        await dashboard.record_call_start(call_id="call_123", agent_id="agent_123")
        await dashboard.record_call_end(call_id="call_123", duration=120.5)
    """
    
    def __init__(self):
        # In-memory storage for demo
        self._calls: Dict[str, Dict[str, Any]] = {}
        self._events: List[Dict[str, Any]] = []
        self._agent_stats: Dict[str, AgentMetrics] = {}
    
    async def get_dashboard(
        self,
        organization_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        time_range: TimeRange = TimeRange.LAST_24H,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> DashboardData:
        """
        Get complete dashboard data.
        
        Args:
            organization_id: Filter by organization
            agent_id: Filter by agent
            time_range: Predefined time range
            start_time: Custom start time
            end_time: Custom end time
        
        Returns:
            DashboardData with all metrics
        """
        # Resolve time range
        if time_range == TimeRange.CUSTOM:
            s_time = start_time or datetime.now(timezone.utc) - timedelta(days=1)
            e_time = end_time or datetime.now(timezone.utc)
        else:
            s_time, e_time = self._resolve_time_range(time_range)
        
        # Filter calls
        calls = self._filter_calls(
            organization_id=organization_id,
            agent_id=agent_id,
            start_time=s_time,
            end_time=e_time,
        )
        
        # Calculate metrics
        call_metrics = self._calculate_call_metrics(calls)
        cost_metrics = self._calculate_cost_metrics(calls)
        agent_metrics = self._calculate_agent_metrics(calls)
        
        # Generate time series
        calls_ts = self._generate_time_series(calls, s_time, e_time, "calls")
        cost_ts = self._generate_time_series(calls, s_time, e_time, "cost")
        
        return DashboardData(
            call_metrics=call_metrics,
            cost_metrics=cost_metrics,
            agent_metrics=agent_metrics,
            calls_over_time=calls_ts,
            cost_over_time=cost_ts,
            active_calls=self._count_active_calls(),
            active_agents=len(set(c.get("agent_id") for c in calls)),
            start_time=s_time,
            end_time=e_time,
        )
    
    async def get_agent_metrics(
        self,
        agent_id: str,
        time_range: TimeRange = TimeRange.LAST_24H,
    ) -> Optional[AgentMetrics]:
        """Get metrics for a specific agent."""
        s_time, e_time = self._resolve_time_range(time_range)
        calls = self._filter_calls(agent_id=agent_id, start_time=s_time, end_time=e_time)
        
        if not calls:
            return None
        
        metrics = self._calculate_agent_metrics(calls)
        return metrics[0] if metrics else None
    
    async def get_real_time_stats(self) -> Dict[str, Any]:
        """Get real-time statistics."""
        active = self._count_active_calls()
        last_hour = datetime.now(timezone.utc) - timedelta(hours=1)
        recent_calls = [c for c in self._calls.values() if c.get("started_at", datetime.min) > last_hour]
        
        return {
            "active_calls": active,
            "calls_last_hour": len(recent_calls),
            "avg_wait_time_seconds": 0,  # Would require queue tracking
            "agents_online": len(self._agent_stats),
        }
    
    # Event recording
    async def record_call_start(
        self,
        call_id: str,
        agent_id: str,
        direction: str = "inbound",
        caller_number: Optional[str] = None,
        organization_id: Optional[str] = None,
    ) -> None:
        """Record a call starting."""
        self._calls[call_id] = {
            "call_id": call_id,
            "agent_id": agent_id,
            "direction": direction,
            "caller_number": caller_number,
            "organization_id": organization_id,
            "started_at": datetime.now(timezone.utc),
            "status": "active",
        }
        
        self._events.append({
            "type": "call_start",
            "call_id": call_id,
            "timestamp": datetime.now(timezone.utc),
        })
    
    async def record_call_end(
        self,
        call_id: str,
        duration_seconds: float,
        status: str = "completed",
        transferred: bool = False,
        cost: float = 0.0,
    ) -> None:
        """Record a call ending."""
        if call_id in self._calls:
            self._calls[call_id].update({
                "ended_at": datetime.now(timezone.utc),
                "duration_seconds": duration_seconds,
                "status": status,
                "transferred": transferred,
                "cost": cost,
            })
        
        self._events.append({
            "type": "call_end",
            "call_id": call_id,
            "duration": duration_seconds,
            "status": status,
            "timestamp": datetime.now(timezone.utc),
        })
    
    async def record_cost(
        self,
        call_id: str,
        service_type: str,
        cost: float,
    ) -> None:
        """Record a cost for a call."""
        if call_id in self._calls:
            costs = self._calls[call_id].setdefault("costs", {})
            costs[service_type] = costs.get(service_type, 0) + cost
            self._calls[call_id]["cost"] = sum(costs.values())
    
    # Private helpers
    def _resolve_time_range(
        self,
        time_range: TimeRange,
    ) -> tuple[datetime, datetime]:
        """Resolve time range to start/end times."""
        now = datetime.now(timezone.utc)
        
        if time_range == TimeRange.LAST_HOUR:
            return now - timedelta(hours=1), now
        elif time_range == TimeRange.LAST_24H:
            return now - timedelta(days=1), now
        elif time_range == TimeRange.LAST_7D:
            return now - timedelta(days=7), now
        elif time_range == TimeRange.LAST_30D:
            return now - timedelta(days=30), now
        else:
            return now - timedelta(days=1), now
    
    def _filter_calls(
        self,
        organization_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Filter calls by criteria."""
        calls = list(self._calls.values())
        
        if organization_id:
            calls = [c for c in calls if c.get("organization_id") == organization_id]
        
        if agent_id:
            calls = [c for c in calls if c.get("agent_id") == agent_id]
        
        if start_time:
            calls = [c for c in calls if c.get("started_at", datetime.min) >= start_time]
        
        if end_time:
            calls = [c for c in calls if c.get("started_at", datetime.max) <= end_time]
        
        return calls
    
    def _calculate_call_metrics(self, calls: List[Dict]) -> CallMetrics:
        """Calculate call metrics from call list."""
        metrics = CallMetrics()
        
        metrics.total_calls = len(calls)
        metrics.completed_calls = len([c for c in calls if c.get("status") == "completed"])
        metrics.failed_calls = len([c for c in calls if c.get("status") == "failed"])
        metrics.transferred_calls = len([c for c in calls if c.get("transferred")])
        
        metrics.inbound_calls = len([c for c in calls if c.get("direction") == "inbound"])
        metrics.outbound_calls = len([c for c in calls if c.get("direction") == "outbound"])
        
        durations = [c.get("duration_seconds", 0) for c in calls]
        metrics.total_duration_seconds = sum(durations)
        metrics.avg_duration_seconds = (
            sum(durations) / len(durations) if durations else 0
        )
        
        return metrics
    
    def _calculate_cost_metrics(self, calls: List[Dict]) -> CostMetrics:
        """Calculate cost metrics from call list."""
        metrics = CostMetrics()
        
        for call in calls:
            cost = call.get("cost", 0)
            metrics.total_cost += cost
            
            costs = call.get("costs", {})
            metrics.stt_cost += costs.get("stt", 0)
            metrics.llm_cost += costs.get("llm", 0)
            metrics.tts_cost += costs.get("tts", 0)
            metrics.telephony_cost += costs.get("telephony", 0)
        
        if calls:
            metrics.cost_per_call = metrics.total_cost / len(calls)
        
        total_minutes = sum(c.get("duration_seconds", 0) for c in calls) / 60
        if total_minutes > 0:
            metrics.cost_per_minute = metrics.total_cost / total_minutes
        
        return metrics
    
    def _calculate_agent_metrics(self, calls: List[Dict]) -> List[AgentMetrics]:
        """Calculate per-agent metrics."""
        by_agent: Dict[str, List[Dict]] = {}
        
        for call in calls:
            agent_id = call.get("agent_id", "unknown")
            by_agent.setdefault(agent_id, []).append(call)
        
        metrics = []
        for agent_id, agent_calls in by_agent.items():
            am = AgentMetrics(
                agent_id=agent_id,
                agent_name=agent_id,  # Would lookup real name
                total_calls=len(agent_calls),
                successful_calls=len([c for c in agent_calls if c.get("status") == "completed"]),
            )
            
            durations = [c.get("duration_seconds", 0) for c in agent_calls]
            am.avg_call_duration = sum(durations) / len(durations) if durations else 0
            
            transferred = len([c for c in agent_calls if c.get("transferred")])
            am.transfer_rate = transferred / len(agent_calls) if agent_calls else 0
            
            metrics.append(am)
        
        return metrics
    
    def _generate_time_series(
        self,
        calls: List[Dict],
        start_time: datetime,
        end_time: datetime,
        metric_type: str,
    ) -> List[TimeSeriesPoint]:
        """Generate time series data."""
        # Determine bucket size
        duration = end_time - start_time
        
        if duration <= timedelta(hours=1):
            bucket_size = timedelta(minutes=5)
        elif duration <= timedelta(days=1):
            bucket_size = timedelta(hours=1)
        elif duration <= timedelta(days=7):
            bucket_size = timedelta(hours=6)
        else:
            bucket_size = timedelta(days=1)
        
        # Create buckets
        points = []
        current = start_time
        
        while current < end_time:
            bucket_end = current + bucket_size
            
            bucket_calls = [
                c for c in calls
                if current <= c.get("started_at", datetime.min) < bucket_end
            ]
            
            if metric_type == "calls":
                value = len(bucket_calls)
            elif metric_type == "cost":
                value = sum(c.get("cost", 0) for c in bucket_calls)
            else:
                value = len(bucket_calls)
            
            points.append(TimeSeriesPoint(timestamp=current, value=value))
            current = bucket_end
        
        return points
    
    def _count_active_calls(self) -> int:
        """Count currently active calls."""
        return len([c for c in self._calls.values() if c.get("status") == "active"])


# Global dashboard
_global_dashboard: Optional[AnalyticsDashboard] = None


def get_analytics_dashboard() -> AnalyticsDashboard:
    """Get or create global analytics dashboard."""
    global _global_dashboard
    if _global_dashboard is None:
        _global_dashboard = AnalyticsDashboard()
    return _global_dashboard
