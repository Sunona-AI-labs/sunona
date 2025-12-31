"""
Sunona Voice AI - Built-in Tools

Production-ready tools for common use cases:
- Calendar/Appointment scheduling
- CRM operations
- Database queries
- Email/SMS
- HTTP requests
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
import re

from sunona.tools.function_calling import (
    BaseTool, ToolParameter, ToolCategory, ToolDefinition, tool
)

logger = logging.getLogger(__name__)


# =============================================================================
# Calendar Tools
# =============================================================================

class CheckAvailabilityTool(BaseTool):
    """Check calendar availability for a date/time range."""
    
    name = "check_availability"
    description = "Check if a specific date and time slot is available for scheduling"
    category = ToolCategory.CALENDAR
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="date",
                type="string",
                description="Date to check in YYYY-MM-DD format",
                required=True,
            ),
            ToolParameter(
                name="time",
                type="string",
                description="Time to check in HH:MM format (24-hour)",
                required=True,
            ),
            ToolParameter(
                name="duration_minutes",
                type="number",
                description="Duration of the appointment in minutes",
                required=False,
                default=30,
            ),
        ]
    
    async def execute(
        self,
        date: str,
        time: str,
        duration_minutes: int = 30,
    ) -> Dict[str, Any]:
        """Check availability (mock implementation)."""
        # Parse date/time
        try:
            dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        except ValueError:
            return {
                "available": False,
                "error": "Invalid date/time format",
            }
        
        # Check if in the past
        if dt < datetime.now():
            return {
                "available": False,
                "reason": "Cannot schedule appointments in the past",
            }
        
        # Check business hours (9 AM - 5 PM)
        if dt.hour < 9 or dt.hour >= 17:
            return {
                "available": False,
                "reason": "Outside business hours (9 AM - 5 PM)",
                "suggested_times": ["09:00", "10:00", "14:00", "15:00"],
            }
        
        # Check if weekend
        if dt.weekday() >= 5:
            return {
                "available": False,
                "reason": "Weekends are not available",
                "suggested_dates": self._get_next_weekdays(dt, 3),
            }
        
        # Mock availability (80% chance available)
        import random
        available = random.random() > 0.2
        
        if available:
            return {
                "available": True,
                "date": date,
                "time": time,
                "duration_minutes": duration_minutes,
                "timezone": "America/New_York",
            }
        else:
            return {
                "available": False,
                "reason": "Slot already booked",
                "suggested_times": self._get_alternative_times(dt),
            }
    
    def _get_next_weekdays(self, dt: datetime, count: int) -> List[str]:
        """Get next N weekdays."""
        dates = []
        current = dt
        while len(dates) < count:
            current += timedelta(days=1)
            if current.weekday() < 5:
                dates.append(current.strftime("%Y-%m-%d"))
        return dates
    
    def _get_alternative_times(self, dt: datetime) -> List[str]:
        """Get alternative time slots."""
        times = []
        for hour in [9, 10, 11, 14, 15, 16]:
            if hour != dt.hour:
                times.append(f"{hour:02d}:00")
        return times[:3]


class BookAppointmentTool(BaseTool):
    """Book an appointment."""
    
    name = "book_appointment"
    description = "Book an appointment for a customer"
    category = ToolCategory.CALENDAR
    requires_confirmation = True  # Important action
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="customer_name",
                type="string",
                description="Full name of the customer",
                required=True,
            ),
            ToolParameter(
                name="customer_phone",
                type="string",
                description="Customer phone number",
                required=True,
            ),
            ToolParameter(
                name="customer_email",
                type="string",
                description="Customer email address",
                required=False,
            ),
            ToolParameter(
                name="date",
                type="string",
                description="Appointment date (YYYY-MM-DD)",
                required=True,
            ),
            ToolParameter(
                name="time",
                type="string",
                description="Appointment time (HH:MM)",
                required=True,
            ),
            ToolParameter(
                name="service_type",
                type="string",
                description="Type of service/appointment",
                required=False,
                default="consultation",
            ),
            ToolParameter(
                name="notes",
                type="string",
                description="Additional notes or requests",
                required=False,
            ),
        ]
    
    async def execute(
        self,
        customer_name: str,
        customer_phone: str,
        date: str,
        time: str,
        customer_email: Optional[str] = None,
        service_type: str = "consultation",
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Book the appointment (mock implementation)."""
        import uuid
        
        # Validate phone
        phone_clean = re.sub(r'\D', '', customer_phone)
        if len(phone_clean) < 10:
            return {
                "success": False,
                "error": "Invalid phone number",
            }
        
        # Generate confirmation
        confirmation_id = f"APT-{uuid.uuid4().hex[:8].upper()}"
        
        return {
            "success": True,
            "confirmation_id": confirmation_id,
            "appointment": {
                "customer_name": customer_name,
                "customer_phone": customer_phone,
                "customer_email": customer_email,
                "date": date,
                "time": time,
                "service_type": service_type,
                "notes": notes,
            },
            "message": f"Appointment confirmed! Your confirmation number is {confirmation_id}. "
                       f"We'll see you on {date} at {time}.",
        }


# =============================================================================
# CRM Tools
# =============================================================================

class LookupCustomerTool(BaseTool):
    """Look up customer information."""
    
    name = "lookup_customer"
    description = "Look up customer information by phone number or email"
    category = ToolCategory.CRM
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="phone",
                type="string",
                description="Customer phone number",
                required=False,
            ),
            ToolParameter(
                name="email",
                type="string",
                description="Customer email address",
                required=False,
            ),
        ]
    
    async def execute(
        self,
        phone: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Look up customer (mock implementation)."""
        if not phone and not email:
            return {
                "found": False,
                "error": "Please provide either phone or email",
            }
        
        # Mock customer data
        return {
            "found": True,
            "customer": {
                "id": "CUST-12345",
                "name": "John Smith",
                "email": email or "john.smith@example.com",
                "phone": phone or "+1-555-123-4567",
                "member_since": "2022-03-15",
                "tier": "gold",
                "total_appointments": 12,
                "notes": "Prefers morning appointments",
            },
        }


class CreateLeadTool(BaseTool):
    """Create a new lead in the CRM."""
    
    name = "create_lead"
    description = "Create a new lead/prospect in the CRM system"
    category = ToolCategory.CRM
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="name",
                type="string",
                description="Lead's full name",
                required=True,
            ),
            ToolParameter(
                name="phone",
                type="string",
                description="Phone number",
                required=True,
            ),
            ToolParameter(
                name="email",
                type="string",
                description="Email address",
                required=False,
            ),
            ToolParameter(
                name="company",
                type="string",
                description="Company name",
                required=False,
            ),
            ToolParameter(
                name="source",
                type="string",
                description="Lead source (e.g., 'phone_call', 'website')",
                required=False,
                default="phone_call",
            ),
            ToolParameter(
                name="interest",
                type="string",
                description="What the lead is interested in",
                required=False,
            ),
        ]
    
    async def execute(
        self,
        name: str,
        phone: str,
        email: Optional[str] = None,
        company: Optional[str] = None,
        source: str = "phone_call",
        interest: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create the lead (mock implementation)."""
        import uuid
        
        lead_id = f"LEAD-{uuid.uuid4().hex[:8].upper()}"
        
        return {
            "success": True,
            "lead_id": lead_id,
            "lead": {
                "id": lead_id,
                "name": name,
                "phone": phone,
                "email": email,
                "company": company,
                "source": source,
                "interest": interest,
                "status": "new",
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
            "message": f"Lead created successfully with ID {lead_id}",
        }


# =============================================================================
# Utility Tools
# =============================================================================

class GetCurrentTimeTool(BaseTool):
    """Get the current date and time."""
    
    name = "get_current_time"
    description = "Get the current date and time in a specific timezone"
    category = ToolCategory.UTILITY
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="timezone",
                type="string",
                description="Timezone (e.g., 'America/New_York', 'Europe/London')",
                required=False,
                default="UTC",
            ),
        ]
    
    async def execute(self, timezone_str: str = "UTC") -> Dict[str, Any]:
        """Get current time."""
        try:
            from zoneinfo import ZoneInfo
            tz = ZoneInfo(timezone_str)
        except Exception:
            tz = timezone.utc
            timezone_str = "UTC"
        
        now = datetime.now(tz)
        
        return {
            "datetime": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "day_of_week": now.strftime("%A"),
            "timezone": timezone_str,
        }


class HttpRequestTool(BaseTool):
    """Make an HTTP request to an external API."""
    
    name = "http_request"
    description = "Make an HTTP request to an external API endpoint"
    category = ToolCategory.UTILITY
    timeout = 10.0
    retries = 2
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="url",
                type="string",
                description="API endpoint URL",
                required=True,
            ),
            ToolParameter(
                name="method",
                type="string",
                description="HTTP method (GET, POST, PUT, DELETE)",
                required=False,
                default="GET",
                enum=["GET", "POST", "PUT", "DELETE"],
            ),
            ToolParameter(
                name="headers",
                type="object",
                description="Request headers as key-value pairs",
                required=False,
            ),
            ToolParameter(
                name="body",
                type="object",
                description="Request body for POST/PUT requests",
                required=False,
            ),
        ]
    
    async def execute(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request."""
        try:
            import httpx
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method.upper(),
                    url=url,
                    headers=headers,
                    json=body if method.upper() in ("POST", "PUT") else None,
                )
                
                # Try to parse JSON response
                try:
                    data = response.json()
                except Exception:
                    data = response.text
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": data,
                }
        except ImportError:
            return {
                "success": False,
                "error": "httpx not installed",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }


class CalculateTool(BaseTool):
    """Perform mathematical calculations."""
    
    name = "calculate"
    description = "Perform a mathematical calculation"
    category = ToolCategory.UTILITY
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="expression",
                type="string",
                description="Mathematical expression to evaluate (e.g., '2 + 2', '10 * 5')",
                required=True,
            ),
        ]
    
    async def execute(self, expression: str) -> Dict[str, Any]:
        """Safely evaluate mathematical expression."""
        # Only allow safe characters
        allowed = set("0123456789+-*/().% ")
        if not all(c in allowed for c in expression):
            return {
                "success": False,
                "error": "Invalid characters in expression",
            }
        
        try:
            # Use eval with restricted builtins
            result = eval(expression, {"__builtins__": {}}, {})
            return {
                "success": True,
                "expression": expression,
                "result": result,
            }
        except Exception as e:
            return {
                "success": False,
                "expression": expression,
                "error": str(e),
            }


# =============================================================================
# Communication Tools
# =============================================================================

class SendSMSTool(BaseTool):
    """Send an SMS message."""
    
    name = "send_sms"
    description = "Send an SMS text message to a phone number"
    category = ToolCategory.COMMUNICATION
    requires_confirmation = True
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="to",
                type="string",
                description="Recipient phone number",
                required=True,
            ),
            ToolParameter(
                name="message",
                type="string",
                description="SMS message content (max 160 characters recommended)",
                required=True,
            ),
        ]
    
    async def execute(
        self,
        to: str,
        message: str,
    ) -> Dict[str, Any]:
        """Send SMS (mock implementation)."""
        import uuid
        
        # Validate phone
        phone_clean = re.sub(r'\D', '', to)
        if len(phone_clean) < 10:
            return {
                "success": False,
                "error": "Invalid phone number",
            }
        
        return {
            "success": True,
            "message_id": f"SMS-{uuid.uuid4().hex[:8].upper()}",
            "to": to,
            "message_length": len(message),
            "segments": (len(message) // 160) + 1,
            "status": "sent",
        }


class TransferCallTool(BaseTool):
    """Transfer the current call to another number or agent."""
    
    name = "transfer_call"
    description = "Transfer the current phone call to another number or agent"
    category = ToolCategory.COMMUNICATION
    requires_confirmation = True
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="transfer_to",
                type="string",
                description="Phone number or agent ID to transfer to",
                required=True,
            ),
            ToolParameter(
                name="reason",
                type="string",
                description="Reason for the transfer",
                required=False,
            ),
            ToolParameter(
                name="warm_transfer",
                type="boolean",
                description="If true, stay on the line to introduce the caller",
                required=False,
                default=False,
            ),
        ]
    
    async def execute(
        self,
        transfer_to: str,
        reason: Optional[str] = None,
        warm_transfer: bool = False,
    ) -> Dict[str, Any]:
        """Initiate call transfer (mock implementation)."""
        return {
            "success": True,
            "transfer_to": transfer_to,
            "transfer_type": "warm" if warm_transfer else "cold",
            "reason": reason,
            "status": "initiated",
            "message": f"Transferring your call to {transfer_to}. Please hold.",
        }


# =============================================================================
# Tool Registration Helper
# =============================================================================

def get_builtin_tools() -> List[BaseTool]:
    """Get all built-in tools."""
    return [
        # Calendar
        CheckAvailabilityTool(),
        BookAppointmentTool(),
        # CRM
        LookupCustomerTool(),
        CreateLeadTool(),
        # Utility
        GetCurrentTimeTool(),
        HttpRequestTool(),
        CalculateTool(),
        # Communication
        SendSMSTool(),
        TransferCallTool(),
    ]


def register_builtin_tools(registry) -> None:
    """Register all built-in tools with a registry."""
    for tool in get_builtin_tools():
        registry.register(tool)
    
    logger.info(f"Registered {len(get_builtin_tools())} built-in tools")
