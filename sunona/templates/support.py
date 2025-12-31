"""
Sunona Voice AI - Customer Support Template

Template for customer service, helpdesk, and technical support.

Features:
- Ticket creation and tracking
- Order status lookup
- Issue escalation
- FAQ handling
- Account management
"""

from typing import List

from sunona.templates.base_template import (
    DomainTemplate, 
    ToolDefinition, 
    ExtractionField,
    ToolType,
)


class SupportTemplate(DomainTemplate):
    """
    Customer support domain template.
    
    Example:
        ```python
        template = SupportTemplate(
            business_name="TechCorp",
            support_type="technical"
        )
        ```
    """
    
    def __init__(
        self,
        support_type: str = "general",
        sla_hours: int = 24,
        escalation_enabled: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.support_type = support_type
        self.sla_hours = sla_hours
        self.escalation_enabled = escalation_enabled
    
    @property
    def domain_name(self) -> str:
        return "support"
    
    @property
    def domain_description(self) -> str:
        return "Customer service, helpdesk, and technical support"
    
    def get_base_prompt(self) -> str:
        return f"""# Customer Support Assistant

You are a customer support agent for {self.business_name}. Your role is to help customers resolve issues efficiently and professionally.

## Primary Responsibilities
1. **Issue Resolution**: Help customers solve problems with products/services
2. **Order Support**: Track orders, process returns, handle complaints
3. **Account Management**: Help with account issues, password resets
4. **Ticket Management**: Create and track support tickets
5. **Escalation**: Transfer to human agents when needed

## Support Guidelines
- Always verify customer identity before accessing account information
- Listen carefully to understand the complete issue
- Provide clear, step-by-step solutions
- Follow up to ensure the issue is resolved
- SLA: Aim to resolve within {self.sla_hours} hours

## Issue Categories
- Billing & Payments
- Product/Service Issues
- Account Access
- Technical Problems
- Shipping & Delivery
- Returns & Refunds
- General Inquiries

## Resolution Flow
1. Greet customer and verify identity
2. Listen and understand the issue
3. Search for existing tickets or orders
4. Provide solution or escalate if needed
5. Create/update ticket with resolution
6. Confirm customer satisfaction"""
    
    def get_tools(self) -> List[ToolDefinition]:
        return [
            ToolDefinition(
                name="lookup_customer",
                description="Look up customer account information",
                parameters=[
                    {"name": "email", "type": "string", "description": "Customer email"},
                    {"name": "phone", "type": "string", "description": "Phone number"},
                    {"name": "account_id", "type": "string", "description": "Account/Customer ID"},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="lookup_order",
                description="Look up order status and details",
                parameters=[
                    {"name": "order_id", "type": "string", "description": "Order number", "required": True},
                    {"name": "email", "type": "string", "description": "Customer email for verification"},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="create_ticket",
                description="Create a new support ticket",
                parameters=[
                    {"name": "customer_id", "type": "string", "description": "Customer ID", "required": True},
                    {"name": "subject", "type": "string", "description": "Issue summary", "required": True},
                    {"name": "description", "type": "string", "description": "Detailed description", "required": True},
                    {"name": "priority", "type": "string", "description": "Priority level", "enum": ["low", "medium", "high", "urgent"]},
                    {"name": "category", "type": "string", "description": "Issue category", "enum": ["billing", "technical", "shipping", "account", "other"]},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="lookup_ticket",
                description="Look up existing support ticket",
                parameters=[
                    {"name": "ticket_id", "type": "string", "description": "Ticket number"},
                    {"name": "customer_id", "type": "string", "description": "Customer ID"},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="update_ticket",
                description="Update an existing ticket",
                parameters=[
                    {"name": "ticket_id", "type": "string", "description": "Ticket to update", "required": True},
                    {"name": "status", "type": "string", "description": "New status", "enum": ["open", "in_progress", "pending", "resolved", "closed"]},
                    {"name": "notes", "type": "string", "description": "Update notes"},
                    {"name": "resolution", "type": "string", "description": "Resolution details"},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="process_refund",
                description="Process a refund for an order",
                parameters=[
                    {"name": "order_id", "type": "string", "description": "Order to refund", "required": True},
                    {"name": "amount", "type": "number", "description": "Refund amount"},
                    {"name": "reason", "type": "string", "description": "Refund reason", "required": True},
                    {"name": "refund_type", "type": "string", "description": "Type of refund", "enum": ["full", "partial", "store_credit"]},
                ],
                tool_type=ToolType.PAYMENT,
            ),
            ToolDefinition(
                name="escalate_to_human",
                description="Transfer call to a human agent",
                parameters=[
                    {"name": "reason", "type": "string", "description": "Reason for escalation", "required": True},
                    {"name": "department", "type": "string", "description": "Department to transfer to", "enum": ["billing", "technical", "supervisor", "sales"]},
                    {"name": "ticket_id", "type": "string", "description": "Related ticket"},
                ],
                tool_type=ToolType.NOTIFICATION,
            ),
            ToolDefinition(
                name="send_notification",
                description="Send notification to customer",
                parameters=[
                    {"name": "customer_id", "type": "string", "description": "Customer to notify", "required": True},
                    {"name": "message", "type": "string", "description": "Message content", "required": True},
                    {"name": "channel", "type": "string", "description": "Notification channel", "enum": ["email", "sms", "both"]},
                ],
                tool_type=ToolType.NOTIFICATION,
            ),
            ToolDefinition(
                name="search_knowledge_base",
                description="Search knowledge base for solutions",
                parameters=[
                    {"name": "query", "type": "string", "description": "Search query", "required": True},
                    {"name": "category", "type": "string", "description": "Category to search"},
                ],
                tool_type=ToolType.SEARCH,
            ),
        ]
    
    def get_extraction_fields(self) -> List[ExtractionField]:
        return [
            ExtractionField(
                name="customer_name",
                description="Customer's full name",
                field_type="string",
                required=True,
            ),
            ExtractionField(
                name="email",
                description="Customer email address",
                field_type="string",
                validation_pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$",
            ),
            ExtractionField(
                name="phone",
                description="Customer phone number",
                field_type="string",
            ),
            ExtractionField(
                name="account_id",
                description="Customer account ID",
                field_type="string",
            ),
            ExtractionField(
                name="order_id",
                description="Order number",
                field_type="string",
                examples=["ORD-12345", "#123456"],
            ),
            ExtractionField(
                name="ticket_id",
                description="Support ticket number",
                field_type="string",
            ),
            ExtractionField(
                name="issue_description",
                description="Description of the customer's issue",
                field_type="string",
                required=True,
            ),
            ExtractionField(
                name="issue_category",
                description="Category of the issue",
                field_type="string",
                examples=["billing", "shipping", "product defect"],
            ),
            ExtractionField(
                name="priority",
                description="Urgency of the issue",
                field_type="string",
                examples=["urgent", "high", "normal"],
            ),
        ]
