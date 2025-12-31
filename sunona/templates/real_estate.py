"""
Sunona Voice AI - Real Estate Template

Template for property listings, viewings, and real estate services.
"""

from typing import List

from sunona.templates.base_template import (
    DomainTemplate, 
    ToolDefinition, 
    ExtractionField,
    ToolType,
)


class RealEstateTemplate(DomainTemplate):
    """Real estate and property domain template."""
    
    def __init__(self, property_type: str = "residential", **kwargs):
        super().__init__(**kwargs)
        self.property_type = property_type
    
    @property
    def domain_name(self) -> str:
        return "real_estate"
    
    @property
    def domain_description(self) -> str:
        return "Real estate, property listings, and viewing scheduling"
    
    def get_base_prompt(self) -> str:
        return f"""# Real Estate Assistant

You are an agent for {self.business_name}. Help clients find properties, schedule viewings, and answer real estate inquiries.

## Responsibilities
1. Property search and recommendations
2. Schedule property viewings
3. Provide property details and pricing
4. Answer neighborhood questions
5. Collect buyer/renter requirements"""
    
    def get_tools(self) -> List[ToolDefinition]:
        return [
            ToolDefinition(name="search_properties", description="Search available properties",
                          parameters=[{"name": "location", "type": "string"}, {"name": "price_max", "type": "number"}, 
                                     {"name": "bedrooms", "type": "integer"}, {"name": "property_type", "type": "string"}], tool_type=ToolType.SEARCH),
            ToolDefinition(name="get_property_details", description="Get property details",
                          parameters=[{"name": "property_id", "type": "string", "required": True}], tool_type=ToolType.DATABASE),
            ToolDefinition(name="schedule_viewing", description="Schedule property viewing",
                          parameters=[{"name": "property_id", "type": "string", "required": True}, {"name": "date", "type": "string", "required": True},
                                     {"name": "time", "type": "string", "required": True}], tool_type=ToolType.CALENDAR),
            ToolDefinition(name="check_availability", description="Check property availability",
                          parameters=[{"name": "property_id", "type": "string", "required": True}], tool_type=ToolType.DATABASE),
            ToolDefinition(name="get_neighborhood_info", description="Get neighborhood information",
                          parameters=[{"name": "location", "type": "string", "required": True}], tool_type=ToolType.API),
            ToolDefinition(name="submit_offer", description="Submit an offer on property",
                          parameters=[{"name": "property_id", "type": "string", "required": True}, {"name": "offer_amount", "type": "number", "required": True}], tool_type=ToolType.DATABASE),
            ToolDefinition(name="get_mortgage_estimate", description="Get mortgage estimate",
                          parameters=[{"name": "property_price", "type": "number", "required": True}, {"name": "down_payment", "type": "number"}], tool_type=ToolType.API),
            ToolDefinition(name="register_interest", description="Register buyer interest",
                          parameters=[{"name": "property_id", "type": "string"}, {"name": "requirements", "type": "string"}], tool_type=ToolType.DATABASE),
        ]
    
    def get_extraction_fields(self) -> List[ExtractionField]:
        return [
            ExtractionField(name="client_name", description="Client's name", field_type="string", required=True),
            ExtractionField(name="email", description="Email address", field_type="string", required=True),
            ExtractionField(name="phone", description="Phone number", field_type="string"),
            ExtractionField(name="budget_max", description="Maximum budget", field_type="number"),
            ExtractionField(name="preferred_location", description="Preferred location/area", field_type="string"),
            ExtractionField(name="bedrooms", description="Number of bedrooms needed", field_type="integer"),
            ExtractionField(name="property_type", description="Type of property wanted", field_type="string"),
            ExtractionField(name="move_in_date", description="Desired move-in date", field_type="date"),
            ExtractionField(name="special_requirements", description="Special requirements", field_type="string"),
        ]
