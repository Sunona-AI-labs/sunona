"""
Sunona Voice AI - Food Delivery Template

Template for food ordering, delivery tracking, and restaurants.
"""

from typing import List

from sunona.templates.base_template import (
    DomainTemplate, 
    ToolDefinition, 
    ExtractionField,
    ToolType,
)


class FoodDeliveryTemplate(DomainTemplate):
    """Food delivery and restaurant domain template."""
    
    @property
    def domain_name(self) -> str:
        return "food_delivery"
    
    @property
    def domain_description(self) -> str:
        return "Food ordering, delivery tracking, and restaurant services"
    
    def get_base_prompt(self) -> str:
        return f"""# Food Delivery Assistant

You are an assistant for {self.business_name}. Help customers with food orders, delivery tracking, and menu inquiries.

## Responsibilities
1. Take and modify orders
2. Track delivery status  
3. Handle refunds and issues
4. Provide menu information
5. Apply promotions and discounts"""
    
    def get_tools(self) -> List[ToolDefinition]:
        return [
            ToolDefinition(name="get_menu", description="Get restaurant menu",
                          parameters=[{"name": "restaurant_id", "type": "string"}, {"name": "category", "type": "string"}], tool_type=ToolType.DATABASE),
            ToolDefinition(name="place_order", description="Place a food order",
                          parameters=[{"name": "items", "type": "string", "required": True}, {"name": "address", "type": "string", "required": True}], tool_type=ToolType.API),
            ToolDefinition(name="track_order", description="Track order status",
                          parameters=[{"name": "order_id", "type": "string", "required": True}], tool_type=ToolType.API),
            ToolDefinition(name="modify_order", description="Modify existing order",
                          parameters=[{"name": "order_id", "type": "string", "required": True}, {"name": "changes", "type": "string", "required": True}], tool_type=ToolType.DATABASE),
            ToolDefinition(name="cancel_order", description="Cancel an order",
                          parameters=[{"name": "order_id", "type": "string", "required": True}, {"name": "reason", "type": "string"}], tool_type=ToolType.DATABASE),
            ToolDefinition(name="apply_promo", description="Apply promo code",
                          parameters=[{"name": "order_id", "type": "string"}, {"name": "promo_code", "type": "string", "required": True}], tool_type=ToolType.DATABASE),
            ToolDefinition(name="request_refund", description="Request order refund",
                          parameters=[{"name": "order_id", "type": "string", "required": True}, {"name": "reason", "type": "string", "required": True}], tool_type=ToolType.PAYMENT),
            ToolDefinition(name="rate_order", description="Rate delivery and food",
                          parameters=[{"name": "order_id", "type": "string", "required": True}, {"name": "rating", "type": "integer", "required": True}], tool_type=ToolType.DATABASE),
            ToolDefinition(name="get_delivery_time", description="Get estimated delivery time",
                          parameters=[{"name": "restaurant_id", "type": "string"}, {"name": "address", "type": "string"}], tool_type=ToolType.API),
        ]
    
    def get_extraction_fields(self) -> List[ExtractionField]:
        return [
            ExtractionField(name="customer_name", description="Customer name", field_type="string", required=True),
            ExtractionField(name="phone", description="Phone number", field_type="string", required=True),
            ExtractionField(name="delivery_address", description="Delivery address", field_type="string", required=True),
            ExtractionField(name="order_items", description="Items ordered", field_type="string"),
            ExtractionField(name="order_id", description="Order ID", field_type="string"),
            ExtractionField(name="special_instructions", description="Special instructions", field_type="string"),
            ExtractionField(name="promo_code", description="Promo code", field_type="string"),
        ]
