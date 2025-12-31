"""
Sunona Voice AI - Insurance Template

Template for insurance inquiries, claims, and policy management.
"""

from typing import List

from sunona.templates.base_template import (
    DomainTemplate, 
    ToolDefinition, 
    ExtractionField,
    ToolType,
)


class InsuranceTemplate(DomainTemplate):
    """Insurance domain template."""
    
    @property
    def domain_name(self) -> str:
        return "insurance"
    
    @property
    def domain_description(self) -> str:
        return "Insurance claims, policy management, and coverage inquiries"
    
    def get_base_prompt(self) -> str:
        return f"""# Insurance Assistant

You are an agent for {self.business_name}. Help customers with policies, claims, and coverage inquiries.

## Responsibilities
1. Policy information and quotes
2. Claims filing and status
3. Coverage questions
4. Premium payments
5. Policy changes and renewals"""
    
    def get_tools(self) -> List[ToolDefinition]:
        return [
            ToolDefinition(name="lookup_policy", description="Look up policy details",
                          parameters=[{"name": "policy_number", "type": "string", "required": True}], tool_type=ToolType.DATABASE),
            ToolDefinition(name="file_claim", description="File a new claim",
                          parameters=[{"name": "policy_number", "type": "string", "required": True}, {"name": "incident_type", "type": "string", "required": True},
                                     {"name": "description", "type": "string", "required": True}], tool_type=ToolType.DATABASE),
            ToolDefinition(name="check_claim_status", description="Check claim status",
                          parameters=[{"name": "claim_number", "type": "string", "required": True}], tool_type=ToolType.DATABASE),
            ToolDefinition(name="get_quote", description="Get insurance quote",
                          parameters=[{"name": "coverage_type", "type": "string", "required": True}, {"name": "details", "type": "string"}], tool_type=ToolType.API),
            ToolDefinition(name="make_payment", description="Make premium payment",
                          parameters=[{"name": "policy_number", "type": "string", "required": True}, {"name": "amount", "type": "number", "required": True}], tool_type=ToolType.PAYMENT),
            ToolDefinition(name="update_policy", description="Update policy details",
                          parameters=[{"name": "policy_number", "type": "string", "required": True}, {"name": "changes", "type": "string", "required": True}], tool_type=ToolType.DATABASE),
            ToolDefinition(name="add_coverage", description="Add coverage to policy",
                          parameters=[{"name": "policy_number", "type": "string", "required": True}, {"name": "coverage_type", "type": "string", "required": True}], tool_type=ToolType.DATABASE),
            ToolDefinition(name="schedule_inspection", description="Schedule property/vehicle inspection",
                          parameters=[{"name": "claim_number", "type": "string", "required": True}, {"name": "date", "type": "string", "required": True}], tool_type=ToolType.CALENDAR),
            ToolDefinition(name="request_documents", description="Request policy documents",
                          parameters=[{"name": "policy_number", "type": "string", "required": True}, {"name": "document_type", "type": "string"}], tool_type=ToolType.NOTIFICATION),
        ]
    
    def get_extraction_fields(self) -> List[ExtractionField]:
        return [
            ExtractionField(name="customer_name", description="Customer name", field_type="string", required=True),
            ExtractionField(name="policy_number", description="Policy number", field_type="string"),
            ExtractionField(name="claim_number", description="Claim number", field_type="string"),
            ExtractionField(name="phone", description="Phone number", field_type="string"),
            ExtractionField(name="email", description="Email address", field_type="string"),
            ExtractionField(name="incident_date", description="Date of incident", field_type="date"),
            ExtractionField(name="incident_type", description="Type of incident", field_type="string"),
            ExtractionField(name="coverage_type", description="Type of coverage", field_type="string"),
        ]
