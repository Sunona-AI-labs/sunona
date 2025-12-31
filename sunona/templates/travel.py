"""
Sunona Voice AI - Travel Template

Template for travel booking, flights, hotels, and itinerary.
"""

from typing import List

from sunona.templates.base_template import (
    DomainTemplate, 
    ToolDefinition, 
    ExtractionField,
    ToolType,
)


class TravelTemplate(DomainTemplate):
    """Travel and tourism domain template."""
    
    @property
    def domain_name(self) -> str:
        return "travel"
    
    @property
    def domain_description(self) -> str:
        return "Travel booking, flights, hotels, and itinerary planning"
    
    def get_base_prompt(self) -> str:
        return f"""# Travel Assistant

You are a travel agent for {self.business_name}. Help customers plan trips, book travel, and manage itineraries.

## Responsibilities
1. Flight searches and bookings
2. Hotel reservations
3. Travel packages
4. Itinerary planning
5. Booking modifications and cancellations"""
    
    def get_tools(self) -> List[ToolDefinition]:
        return [
            ToolDefinition(name="search_flights", description="Search available flights",
                          parameters=[{"name": "origin", "type": "string", "required": True}, {"name": "destination", "type": "string", "required": True},
                                     {"name": "date", "type": "string", "required": True}, {"name": "passengers", "type": "integer"}], tool_type=ToolType.SEARCH),
            ToolDefinition(name="book_flight", description="Book a flight",
                          parameters=[{"name": "flight_id", "type": "string", "required": True}, {"name": "passengers", "type": "string", "required": True}], tool_type=ToolType.API),
            ToolDefinition(name="search_hotels", description="Search hotels",
                          parameters=[{"name": "location", "type": "string", "required": True}, {"name": "check_in", "type": "string", "required": True},
                                     {"name": "check_out", "type": "string", "required": True}], tool_type=ToolType.SEARCH),
            ToolDefinition(name="book_hotel", description="Book hotel room",
                          parameters=[{"name": "hotel_id", "type": "string", "required": True}, {"name": "room_type", "type": "string"}], tool_type=ToolType.API),
            ToolDefinition(name="get_booking", description="Get booking details",
                          parameters=[{"name": "booking_id", "type": "string", "required": True}], tool_type=ToolType.DATABASE),
            ToolDefinition(name="modify_booking", description="Modify existing booking",
                          parameters=[{"name": "booking_id", "type": "string", "required": True}, {"name": "changes", "type": "string", "required": True}], tool_type=ToolType.DATABASE),
            ToolDefinition(name="cancel_booking", description="Cancel a booking",
                          parameters=[{"name": "booking_id", "type": "string", "required": True}], tool_type=ToolType.DATABASE),
            ToolDefinition(name="get_travel_insurance", description="Get travel insurance quote",
                          parameters=[{"name": "destination", "type": "string"}, {"name": "dates", "type": "string"}, {"name": "travelers", "type": "integer"}], tool_type=ToolType.API),
            ToolDefinition(name="check_visa_requirements", description="Check visa requirements",
                          parameters=[{"name": "nationality", "type": "string", "required": True}, {"name": "destination", "type": "string", "required": True}], tool_type=ToolType.API),
        ]
    
    def get_extraction_fields(self) -> List[ExtractionField]:
        return [
            ExtractionField(name="traveler_name", description="Primary traveler name", field_type="string", required=True),
            ExtractionField(name="email", description="Email address", field_type="string", required=True),
            ExtractionField(name="phone", description="Phone number", field_type="string"),
            ExtractionField(name="origin", description="Departure city", field_type="string"),
            ExtractionField(name="destination", description="Destination city", field_type="string"),
            ExtractionField(name="travel_dates", description="Travel dates", field_type="string"),
            ExtractionField(name="num_travelers", description="Number of travelers", field_type="integer"),
            ExtractionField(name="booking_id", description="Booking reference", field_type="string"),
        ]
