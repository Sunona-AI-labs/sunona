"""
Sunona Voice AI - Domain Templates Package

Pre-built templates for common industry use cases.
Provides system prompts, tools, and extraction schemas.

Domains:
- hospitality: Hotels, restaurants, travel
- support: Customer service, helpdesk
- recruitment: Hiring, interviews
- healthcare: Appointments, patient support
- retail: E-commerce, order management
- banking: Financial services, transactions
- education: Tutoring, enrollment
- real_estate: Property listings, viewings
- food_delivery: Orders, tracking
- utilities: Bill payments, service requests
"""

from sunona.templates.base_template import DomainTemplate, ToolDefinition
from sunona.templates.hospitality import HospitalityTemplate
from sunona.templates.support import SupportTemplate
from sunona.templates.recruitment import RecruitmentTemplate
from sunona.templates.healthcare import HealthcareTemplate
from sunona.templates.retail import RetailTemplate
from sunona.templates.banking import BankingTemplate

__all__ = [
    "DomainTemplate",
    "ToolDefinition",
    "HospitalityTemplate",
    "SupportTemplate",
    "RecruitmentTemplate",
    "HealthcareTemplate",
    "RetailTemplate",
    "BankingTemplate",
    "get_template",
    "list_templates",
]

# Template registry
TEMPLATES = {
    "hospitality": HospitalityTemplate,
    "hotel": HospitalityTemplate,
    "restaurant": HospitalityTemplate,
    "support": SupportTemplate,
    "customer_service": SupportTemplate,
    "helpdesk": SupportTemplate,
    "recruitment": RecruitmentTemplate,
    "hiring": RecruitmentTemplate,
    "hr": RecruitmentTemplate,
    "healthcare": HealthcareTemplate,
    "medical": HealthcareTemplate,
    "clinic": HealthcareTemplate,
    "retail": RetailTemplate,
    "ecommerce": RetailTemplate,
    "shopping": RetailTemplate,
    "banking": BankingTemplate,
    "finance": BankingTemplate,
    "bank": BankingTemplate,
}


def get_template(domain: str, **kwargs) -> DomainTemplate:
    """
    Get a domain template by name.
    
    Args:
        domain: Domain name (hospitality, support, etc.)
        **kwargs: Template configuration
        
    Returns:
        Configured domain template
    """
    domain_lower = domain.lower().replace("-", "_").replace(" ", "_")
    
    if domain_lower not in TEMPLATES:
        available = list(set(TEMPLATES.values()))
        raise ValueError(
            f"Unknown domain: '{domain}'. "
            f"Available: hospitality, support, recruitment, healthcare, retail, banking"
        )
    
    return TEMPLATES[domain_lower](**kwargs)


def list_templates() -> dict:
    """List all available templates with descriptions."""
    return {
        "hospitality": "Hotels, restaurants, travel booking",
        "support": "Customer service, helpdesk, tickets",
        "recruitment": "Hiring, interviews, HR",
        "healthcare": "Medical appointments, patient support",
        "retail": "E-commerce, orders, shopping",
        "banking": "Financial services, account management",
    }
