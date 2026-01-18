"""
Sunona Voice AI - Pricing API Routes

Provides endpoints for:
- Subscription tier pricing
- Cost estimation and comparison
- Smart provider recommendations
- Slippage buffer information
"""

import logging
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from sunona.billing.subscription_tiers import (
    subscription_manager,
    TierType,
    SUBSCRIPTION_TIERS,
)
from sunona.billing.smart_optimizer import (
    smart_optimizer,
    UseCase,
    QualityPreference,
)
from sunona.billing.usage_tracking import (
    PLATFORM_FEE_PER_SECOND,
    PROVIDER_COSTS_PER_SECOND,
    USER_COSTS_PER_SECOND,
    USER_PLATFORM_FEE_PER_SECOND,
    USER_FACING_RATE_PER_MINUTE,
    INTERNAL_COST_PER_MINUTE,
    SLIPPAGE_BUFFER_PER_MINUTE,
    SLIPPAGE_PERCENT,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pricing", tags=["pricing"])


# ============================================================
# Response Models
# ============================================================

class PricingOverview(BaseModel):
    """Current pricing overview."""
    platform_fee_per_minute: float
    llm_per_minute: float
    stt_per_minute: float
    tts_per_minute: float
    telephony_per_minute: float
    total_per_minute: float
    byok_rate: float  # Platform-only rate


# ============================================================
# Endpoints
# ============================================================

@router.get("/overview")
async def get_pricing_overview():
    """
    Get current pricing overview with slippage buffer details.
    
    Shows both user-facing rates and internal cost structure.
    """
    # User-facing rates (what users pay)
    user_platform = float(USER_PLATFORM_FEE_PER_SECOND * 60)
    user_llm = float(USER_COSTS_PER_SECOND["llm"] * 60)
    user_stt = float(USER_COSTS_PER_SECOND["stt"] * 60)
    user_tts = float(USER_COSTS_PER_SECOND["tts"] * 60)
    user_telephony = float(USER_COSTS_PER_SECOND["telephony"] * 60)
    user_total = float(USER_FACING_RATE_PER_MINUTE)
    
    # Internal costs (what we pay)
    internal_total = float(INTERNAL_COST_PER_MINUTE)
    slippage = float(SLIPPAGE_BUFFER_PER_MINUTE)
    
    return {
        "user_pricing": {
            "platform_fee": round(user_platform, 4),
            "llm": round(user_llm, 4),
            "stt": round(user_stt, 4),
            "tts": round(user_tts, 4),
            "telephony": round(user_telephony, 4),
            "total_per_minute": round(user_total, 4),
        },
        "slippage_buffer": {
            "user_pays": round(user_total, 4),
            "internal_cost": round(internal_total, 4),
            "buffer_amount": round(slippage, 4),
            "buffer_percent": round(float(SLIPPAGE_PERCENT), 1),
            "purpose": "Covers rate fluctuations, profit margin, and unexpected costs",
        },
        "byok_pricing": {
            "description": "Platform fee when using your own API keys",
            "platform_only": round(user_platform, 4),
        },
        "comparison": {
            "sunona_rate": round(user_total, 4),
            "industry_average": 0.07,
            "savings_percent": round((1 - user_total / 0.07) * 100, 1),
        },
    }


@router.get("/tiers")
async def get_subscription_tiers():
    """
    Get all subscription tier pricing.
    
    Returns all available plans with features and pricing.
    """
    tiers = []
    for tier_type, tier in SUBSCRIPTION_TIERS.items():
        tiers.append({
            "id": tier_type.value,
            "name": tier.name,
            "description": tier.description,
            "monthly_price": float(tier.monthly_price),
            "included_minutes": tier.included_minutes,
            "effective_rate": float(tier.effective_rate),
            "overage_rate": float(tier.overage_rate),
            "features": {
                "max_concurrency": tier.max_concurrency,
                "max_agents": tier.max_agents,
                "priority_support": tier.priority_support,
                "custom_voices": tier.custom_voices,
                "dedicated_manager": tier.dedicated_manager,
                "sla_guarantee": tier.sla_guarantee,
            },
            "limits": {
                "max_call_duration_minutes": tier.max_call_duration_minutes,
                "max_monthly_minutes": tier.max_monthly_minutes,
            },
        })
    
    return {"tiers": tiers}


@router.get("/recommend-tier")
async def recommend_tier(
    monthly_minutes: int = Query(1000, ge=0, le=100000),
):
    """
    Recommend the best subscription tier based on expected usage.
    
    Compares all tiers and finds the most cost-effective option.
    """
    comparison = subscription_manager.compare_tiers(
        current_tier=TierType.PAY_AS_YOU_GO,
        monthly_usage=monthly_minutes,
    )
    
    return comparison


@router.get("/stacks")
async def get_provider_stacks():
    """
    Get all available provider stacks with pricing.
    
    Returns pre-configured stacks from ultra-budget to premium.
    """
    return {
        "stacks": smart_optimizer.get_all_stacks(),
        "note": "Select a stack that matches your quality/cost preference",
    }


@router.get("/recommend-stack")
async def recommend_provider_stack(
    use_case: str = Query("general", description="Use case: simple_faq, customer_support, sales, appointment, survey, general"),
    quality: str = Query("balanced", description="Quality preference: budget, balanced, premium"),
):
    """
    Get optimal provider stack for a specific use case.
    
    Returns the best providers based on use case and quality preference.
    """
    try:
        use_case_enum = UseCase(use_case)
    except ValueError:
        use_case_enum = UseCase.GENERAL
    
    try:
        quality_enum = QualityPreference(quality)
    except ValueError:
        quality_enum = QualityPreference.BALANCED
    
    stack = smart_optimizer.get_optimal_stack(use_case_enum, quality_enum)
    
    return {
        "use_case": use_case,
        "quality_preference": quality,
        "recommended_stack": stack.to_dict(),
        "note": "You can customize providers in your agent config",
    }


@router.get("/estimate")
async def estimate_cost(
    monthly_minutes: int = Query(1000, ge=1, le=100000),
    stack: str = Query("balanced", description="Provider stack to use"),
):
    """
    Estimate monthly cost for given usage.
    
    Calculates total cost including any subscription savings.
    """
    # Calculate stack cost
    stack_estimate = smart_optimizer.estimate_monthly_cost(stack, monthly_minutes)
    
    # Calculate best tier cost
    tier_comparison = subscription_manager.compare_tiers(
        current_tier=TierType.PAY_AS_YOU_GO,
        monthly_usage=monthly_minutes,
    )
    
    return {
        "monthly_minutes": monthly_minutes,
        "pay_as_you_go": stack_estimate,
        "best_subscription": {
            "tier": tier_comparison["best_tier"],
            "cost": tier_comparison["best_cost"],
            "savings_vs_payg": round(
                stack_estimate.get("total_monthly_cost", 0) - tier_comparison["best_cost"], 2
            ),
        },
        "recommendation": (
            f"Subscribe to {tier_comparison['best_tier']} tier"
            if tier_comparison["best_cost"] < stack_estimate.get("total_monthly_cost", 0)
            else "Pay-as-you-go is more cost effective for your usage"
        ),
    }


@router.get("/compare")
async def compare_all_options(
    monthly_minutes: int = Query(5000, ge=100, le=100000),
):
    """
    Compare all pricing options for given usage.
    
    Comprehensive comparison of stacks and tiers.
    """
    # Compare stacks
    stack_comparison = smart_optimizer.compare_stacks(monthly_minutes)
    
    # Compare tiers
    tier_comparison = subscription_manager.compare_tiers(
        current_tier=TierType.PAY_AS_YOU_GO,
        monthly_usage=monthly_minutes,
    )
    
    return {
        "monthly_minutes": monthly_minutes,
        "provider_stacks": stack_comparison,
        "subscription_tiers": tier_comparison,
        "summary": {
            "cheapest_stack": stack_comparison["cheapest_stack"],
            "cheapest_stack_cost": stack_comparison["cheapest_cost"],
            "best_tier": tier_comparison["best_tier"],
            "best_tier_cost": tier_comparison["best_cost"],
            "recommended": (
                "subscription" if tier_comparison["best_cost"] < stack_comparison["cheapest_cost"]
                else "pay_as_you_go"
            ),
        },
    }


@router.get("/byok-savings")
async def calculate_byok_savings(
    monthly_minutes: int = Query(5000, ge=100, le=100000),
    own_llm_key: bool = Query(False),
    own_stt_key: bool = Query(False),
    own_tts_key: bool = Query(False),
    own_telephony_key: bool = Query(False),
):
    """
    Calculate savings when using your own API keys (BYOK).
    
    Shows how much you save by providing your own provider keys.
    """
    platform = float(PLATFORM_FEE_PER_SECOND * 60) * monthly_minutes
    
    llm = 0 if own_llm_key else float(PROVIDER_COSTS_PER_SECOND["llm"] * 60) * monthly_minutes
    stt = 0 if own_stt_key else float(PROVIDER_COSTS_PER_SECOND["stt"] * 60) * monthly_minutes
    tts = 0 if own_tts_key else float(PROVIDER_COSTS_PER_SECOND["tts"] * 60) * monthly_minutes
    telephony = 0 if own_telephony_key else float(PROVIDER_COSTS_PER_SECOND["telephony"] * 60) * monthly_minutes
    
    total_with_byok = platform + llm + stt + tts + telephony
    total_without_byok = float(PLATFORM_FEE_PER_SECOND * 60) * monthly_minutes + sum(
        float(v * 60) * monthly_minutes for v in PROVIDER_COSTS_PER_SECOND.values()
    )
    
    return {
        "monthly_minutes": monthly_minutes,
        "byok_status": {
            "llm": own_llm_key,
            "stt": own_stt_key,
            "tts": own_tts_key,
            "telephony": own_telephony_key,
        },
        "cost_breakdown": {
            "platform_fee": round(platform, 2),
            "llm": round(llm, 2),
            "stt": round(stt, 2),
            "tts": round(tts, 2),
            "telephony": round(telephony, 2),
            "total": round(total_with_byok, 2),
        },
        "savings": {
            "amount": round(total_without_byok - total_with_byok, 2),
            "percent": round((1 - total_with_byok / total_without_byok) * 100, 1) if total_without_byok > 0 else 0,
        },
        "effective_rate": round(total_with_byok / monthly_minutes, 4) if monthly_minutes > 0 else 0,
    }
