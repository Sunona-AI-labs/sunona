"""
Sunona Voice AI - Retail/E-commerce Template

Template for retail, e-commerce, and shopping services.

Features:
- Order tracking and status
- Product inquiries
- Returns and refunds
- Inventory check
- Promotions and deals
"""

from typing import List

from sunona.templates.base_template import (
    DomainTemplate, 
    ToolDefinition, 
    ExtractionField,
    ToolType,
)


class RetailTemplate(DomainTemplate):
    """
    Retail and e-commerce domain template.
    
    Example:
        ```python
        template = RetailTemplate(
            business_name="ShopMart",
            store_type="online"
        )
        ```
    """
    
    def __init__(
        self,
        store_type: str = "online",
        return_policy_days: int = 30,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.store_type = store_type
        self.return_policy_days = return_policy_days
    
    @property
    def domain_name(self) -> str:
        return "retail"
    
    @property
    def domain_description(self) -> str:
        return "E-commerce, retail, and shopping services"
    
    def get_base_prompt(self) -> str:
        return f"""# Retail Shopping Assistant

You are a shopping assistant for {self.business_name}. Your role is to help customers with orders, products, and shopping inquiries.

## Primary Responsibilities
1. **Order Support**: Track orders, update delivery status, handle issues
2. **Product Information**: Answer questions about products, availability, specifications
3. **Returns & Refunds**: Process return requests, explain policies
4. **Shopping Assistance**: Help find products, recommend items
5. **Account Help**: Assist with account issues, payment problems

## Return Policy
- Returns accepted within {self.return_policy_days} days of delivery
- Items must be unused and in original packaging
- Refunds processed to original payment method

## Order Support Flow
1. Verify customer identity (order number or email)
2. Look up order status
3. Address specific concerns
4. Provide solutions or next steps
5. Confirm customer satisfaction

## Product Assistance
- Provide accurate product information
- Check inventory and availability
- Suggest alternatives if item is out of stock
- Share current promotions when relevant"""
    
    def get_tools(self) -> List[ToolDefinition]:
        return [
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
                name="track_shipment",
                description="Get shipment tracking information",
                parameters=[
                    {"name": "order_id", "type": "string", "description": "Order number", "required": True},
                    {"name": "tracking_number", "type": "string", "description": "Tracking number"},
                ],
                tool_type=ToolType.API,
            ),
            ToolDefinition(
                name="lookup_product",
                description="Get product details and availability",
                parameters=[
                    {"name": "product_id", "type": "string", "description": "Product ID/SKU"},
                    {"name": "product_name", "type": "string", "description": "Product name search"},
                    {"name": "category", "type": "string", "description": "Product category"},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="check_inventory",
                description="Check product availability/stock",
                parameters=[
                    {"name": "product_id", "type": "string", "description": "Product ID", "required": True},
                    {"name": "store_location", "type": "string", "description": "Store location for in-store pickup"},
                    {"name": "quantity", "type": "integer", "description": "Quantity needed"},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="initiate_return",
                description="Start a return request",
                parameters=[
                    {"name": "order_id", "type": "string", "description": "Order number", "required": True},
                    {"name": "items", "type": "string", "description": "Items to return", "required": True},
                    {"name": "reason", "type": "string", "description": "Return reason", "required": True, "enum": ["wrong_item", "defective", "not_as_described", "changed_mind", "other"]},
                    {"name": "refund_method", "type": "string", "description": "Refund method", "enum": ["original_payment", "store_credit", "exchange"]},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="process_refund",
                description="Process a refund",
                parameters=[
                    {"name": "order_id", "type": "string", "description": "Order number", "required": True},
                    {"name": "return_id", "type": "string", "description": "Return request ID"},
                    {"name": "amount", "type": "number", "description": "Refund amount"},
                    {"name": "reason", "type": "string", "description": "Refund reason"},
                ],
                tool_type=ToolType.PAYMENT,
            ),
            ToolDefinition(
                name="apply_coupon",
                description="Check and apply a coupon code",
                parameters=[
                    {"name": "coupon_code", "type": "string", "description": "Coupon code", "required": True},
                    {"name": "order_id", "type": "string", "description": "Order to apply to"},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="get_promotions",
                description="Get current promotions and deals",
                parameters=[
                    {"name": "category", "type": "string", "description": "Product category"},
                    {"name": "customer_id", "type": "string", "description": "Customer for personalized offers"},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="update_shipping_address",
                description="Update shipping address for an order",
                parameters=[
                    {"name": "order_id", "type": "string", "description": "Order number", "required": True},
                    {"name": "new_address", "type": "string", "description": "New shipping address", "required": True},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="cancel_order",
                description="Cancel an order",
                parameters=[
                    {"name": "order_id", "type": "string", "description": "Order to cancel", "required": True},
                    {"name": "reason", "type": "string", "description": "Cancellation reason"},
                ],
                tool_type=ToolType.DATABASE,
            ),
        ]
    
    def get_extraction_fields(self) -> List[ExtractionField]:
        return [
            ExtractionField(
                name="customer_name",
                description="Customer's name",
                field_type="string",
            ),
            ExtractionField(
                name="email",
                description="Customer email address",
                field_type="string",
                required=True,
            ),
            ExtractionField(
                name="phone",
                description="Contact phone number",
                field_type="string",
            ),
            ExtractionField(
                name="order_id",
                description="Order number",
                field_type="string",
                required=True,
                examples=["ORD-123456", "#12345678"],
            ),
            ExtractionField(
                name="product_name",
                description="Product name or description",
                field_type="string",
            ),
            ExtractionField(
                name="product_id",
                description="Product ID or SKU",
                field_type="string",
            ),
            ExtractionField(
                name="issue_type",
                description="Type of issue",
                field_type="string",
                examples=["missing item", "damaged", "wrong product", "delayed"],
            ),
            ExtractionField(
                name="return_reason",
                description="Reason for return",
                field_type="string",
            ),
            ExtractionField(
                name="shipping_address",
                description="Shipping address",
                field_type="string",
            ),
            ExtractionField(
                name="coupon_code",
                description="Coupon or promo code",
                field_type="string",
            ),
        ]
