"""
Sunona Voice AI - Hospitality Domain Template

Template for hotels, restaurants, travel agencies, and tourism.

Features:
- Booking management
- Availability checking
- Guest preferences
- Reservation modifications
- Room/table allocation
"""

from typing import List

from sunona.templates.base_template import (
    DomainTemplate, 
    ToolDefinition, 
    ExtractionField,
    ToolType,
)


class HospitalityTemplate(DomainTemplate):
    """
    Hospitality domain template for hotels, restaurants, and travel.
    
    Example:
        ```python
        template = HospitalityTemplate(
            business_name="Grand Hotel",
            business_type="hotel",
            agent_name="Sarah"
        )
        
        prompt = template.get_system_prompt()
        tools = template.get_tools()
        ```
    """
    
    def __init__(
        self,
        business_type: str = "hotel",
        check_in_time: str = "3:00 PM",
        check_out_time: str = "11:00 AM",
        **kwargs
    ):
        """
        Initialize hospitality template.
        
        Args:
            business_type: Type of business (hotel, restaurant, resort)
            check_in_time: Default check-in time
            check_out_time: Default check-out time
        """
        super().__init__(**kwargs)
        self.business_type = business_type
        self.check_in_time = check_in_time
        self.check_out_time = check_out_time
    
    @property
    def domain_name(self) -> str:
        return "hospitality"
    
    @property
    def domain_description(self) -> str:
        return "Hotels, restaurants, resorts, and travel services"
    
    def get_base_prompt(self) -> str:
        if self.business_type == "hotel":
            return self._get_hotel_prompt()
        elif self.business_type == "restaurant":
            return self._get_restaurant_prompt()
        else:
            return self._get_generic_hospitality_prompt()
    
    def _get_hotel_prompt(self) -> str:
        return f"""# Hotel Reservation Assistant

You are a professional hotel receptionist for {self.business_name}. Your role is to help guests with:

## Primary Responsibilities
1. **Room Reservations**: Help guests book rooms, check availability, and provide pricing
2. **Booking Modifications**: Change dates, upgrade rooms, add services
3. **Guest Inquiries**: Answer questions about amenities, policies, and local attractions
4. **Check-in/Check-out**: Provide information about times and procedures

## Important Information
- Check-in time: {self.check_in_time}
- Check-out time: {self.check_out_time}

## Room Types Available
- Standard Room: Comfortable room with essential amenities
- Deluxe Room: Larger room with premium amenities
- Suite: Spacious suite with separate living area
- Executive Suite: Luxury suite with exclusive services

## Booking Process
1. Ask for guest name and contact information
2. Confirm dates of stay (check-in and check-out)
3. Determine room preferences and special requests
4. Check availability using the booking tool
5. Provide pricing and confirm reservation
6. Send confirmation to guest"""
    
    def _get_restaurant_prompt(self) -> str:
        return f"""# Restaurant Reservation Assistant

You are a professional host for {self.business_name}. Your role is to help guests with:

## Primary Responsibilities
1. **Table Reservations**: Book tables and manage waitlist
2. **Menu Inquiries**: Answer questions about menu, dietary options
3. **Special Events**: Handle private dining and event bookings
4. **Guest Preferences**: Note allergies, seating preferences

## Reservation Process
1. Ask for guest name and party size
2. Confirm date and preferred time
3. Note any special requests or dietary requirements
4. Check availability and confirm booking
5. Provide confirmation details"""
    
    def _get_generic_hospitality_prompt(self) -> str:
        return f"""# Hospitality Assistant

You are a hospitality professional for {self.business_name}. Your role is to provide excellent customer service and assist with reservations and inquiries."""
    
    def get_tools(self) -> List[ToolDefinition]:
        tools = [
            ToolDefinition(
                name="check_availability",
                description="Check room/table availability for given dates",
                parameters=[
                    {"name": "check_in_date", "type": "string", "description": "Check-in date (YYYY-MM-DD)", "required": True},
                    {"name": "check_out_date", "type": "string", "description": "Check-out date (YYYY-MM-DD)", "required": True},
                    {"name": "room_type", "type": "string", "description": "Type of room", "enum": ["standard", "deluxe", "suite", "executive"]},
                    {"name": "guests", "type": "integer", "description": "Number of guests"},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="create_reservation",
                description="Create a new booking/reservation",
                parameters=[
                    {"name": "guest_name", "type": "string", "description": "Full name of guest", "required": True},
                    {"name": "phone", "type": "string", "description": "Contact phone number", "required": True},
                    {"name": "email", "type": "string", "description": "Email address"},
                    {"name": "check_in_date", "type": "string", "description": "Check-in date", "required": True},
                    {"name": "check_out_date", "type": "string", "description": "Check-out date", "required": True},
                    {"name": "room_type", "type": "string", "description": "Room type", "required": True},
                    {"name": "guests", "type": "integer", "description": "Number of guests"},
                    {"name": "special_requests", "type": "string", "description": "Special requests or notes"},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="lookup_reservation",
                description="Look up an existing reservation",
                parameters=[
                    {"name": "confirmation_number", "type": "string", "description": "Reservation confirmation number"},
                    {"name": "guest_name", "type": "string", "description": "Guest name to search"},
                    {"name": "phone", "type": "string", "description": "Phone number to search"},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="modify_reservation",
                description="Modify an existing reservation",
                parameters=[
                    {"name": "confirmation_number", "type": "string", "description": "Reservation to modify", "required": True},
                    {"name": "new_check_in", "type": "string", "description": "New check-in date"},
                    {"name": "new_check_out", "type": "string", "description": "New check-out date"},
                    {"name": "new_room_type", "type": "string", "description": "New room type"},
                    {"name": "add_services", "type": "string", "description": "Additional services to add"},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="cancel_reservation",
                description="Cancel an existing reservation",
                parameters=[
                    {"name": "confirmation_number", "type": "string", "description": "Reservation to cancel", "required": True},
                    {"name": "reason", "type": "string", "description": "Cancellation reason"},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="get_pricing",
                description="Get pricing for room types and services",
                parameters=[
                    {"name": "room_type", "type": "string", "description": "Room type to price"},
                    {"name": "check_in_date", "type": "string", "description": "Check-in date"},
                    {"name": "check_out_date", "type": "string", "description": "Check-out date"},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="send_confirmation",
                description="Send booking confirmation to guest",
                parameters=[
                    {"name": "confirmation_number", "type": "string", "description": "Reservation number", "required": True},
                    {"name": "method", "type": "string", "description": "Delivery method", "enum": ["email", "sms", "both"]},
                ],
                tool_type=ToolType.NOTIFICATION,
            ),
        ]
        
        return tools
    
    def get_extraction_fields(self) -> List[ExtractionField]:
        return [
            ExtractionField(
                name="guest_name",
                description="Full name of the guest",
                field_type="string",
                required=True,
                examples=["John Smith", "Maria Garcia"],
            ),
            ExtractionField(
                name="phone",
                description="Contact phone number",
                field_type="string",
                required=True,
                validation_pattern=r"^\+?[\d\s\-\(\)]{10,}$",
                examples=["+1 555-123-4567", "9876543210"],
            ),
            ExtractionField(
                name="email",
                description="Email address",
                field_type="string",
                validation_pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$",
                examples=["guest@email.com"],
            ),
            ExtractionField(
                name="check_in_date",
                description="Date of check-in",
                field_type="date",
                required=True,
                examples=["2024-12-25", "tomorrow", "next Monday"],
            ),
            ExtractionField(
                name="check_out_date",
                description="Date of check-out",
                field_type="date",
                required=True,
                examples=["2024-12-28", "in 3 days"],
            ),
            ExtractionField(
                name="guests",
                description="Number of guests",
                field_type="integer",
                examples=["2", "4 adults and 2 children"],
            ),
            ExtractionField(
                name="room_preference",
                description="Room type preference",
                field_type="string",
                examples=["deluxe", "suite with ocean view"],
            ),
            ExtractionField(
                name="special_requests",
                description="Special requests or requirements",
                field_type="string",
                examples=["late check-in", "wheelchair accessible", "quiet room"],
            ),
            ExtractionField(
                name="confirmation_number",
                description="Existing reservation confirmation number",
                field_type="string",
                examples=["RES123456", "BK-2024-001"],
            ),
        ]
