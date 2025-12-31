"""
Sunona Voice AI - Smart LLM Model Selector

Automatically selects the best cost-effective LLM models for voice conversations.
Ranks models by: cost, speed, quality, and suitability for voice AI.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum

logger = logging.getLogger(__name__)


class UseCase(Enum):
    """Conversation use cases with different requirements."""
    SIMPLE_QA = "simple_qa"           # FAQ, simple questions
    CUSTOMER_SUPPORT = "customer_support"  # Support conversations
    SALES = "sales"                   # Sales calls, negotiations
    HEALTHCARE = "healthcare"         # Medical, sensitive
    LEGAL = "legal"                   # Legal advice
    GENERAL = "general"               # General purpose


@dataclass
class LLMModel:
    """LLM model with pricing and capabilities."""
    provider: str           # openrouter, openai, groq, etc.
    model_id: str           # Full model ID
    name: str               # Display name
    
    # Pricing (per 1K tokens)
    input_cost: Decimal
    output_cost: Decimal
    
    # Capabilities
    context_length: int = 8192
    supports_streaming: bool = True
    supports_functions: bool = True
    
    # Quality scores (1-10)
    quality_score: int = 7       # Overall quality
    speed_score: int = 7         # Response speed
    voice_suitability: int = 7   # How good for voice AI (concise, natural)
    
    # Best for
    recommended_for: List[UseCase] = field(default_factory=list)
    
    # Is it free?
    is_free: bool = False
    
    @property
    def avg_cost(self) -> Decimal:
        """Average cost per 1K tokens."""
        return (self.input_cost + self.output_cost) / 2
    
    @property
    def cost_effectiveness(self) -> float:
        """Higher = better value (quality / cost)."""
        cost = float(self.avg_cost) if self.avg_cost > 0 else 0.0001
        return (self.quality_score * self.voice_suitability) / cost


# ==================== Model Database ====================

CONVERSATION_MODELS: List[LLMModel] = [
    # === FREE MODELS (OpenRouter) ===
    LLMModel(
        provider="openrouter",
        model_id="mistralai/mistral-7b-instruct:free",
        name="Mistral 7B (Free)",
        input_cost=Decimal("0"),
        output_cost=Decimal("0"),
        context_length=8192,
        quality_score=7,
        speed_score=8,
        voice_suitability=8,
        recommended_for=[UseCase.SIMPLE_QA, UseCase.CUSTOMER_SUPPORT, UseCase.GENERAL],
        is_free=True,
    ),
    LLMModel(
        provider="openrouter",
        model_id="meta-llama/llama-3.1-8b-instruct:free",
        name="Llama 3.1 8B (Free)",
        input_cost=Decimal("0"),
        output_cost=Decimal("0"),
        context_length=8192,
        quality_score=7,
        speed_score=8,
        voice_suitability=7,
        recommended_for=[UseCase.SIMPLE_QA, UseCase.GENERAL],
        is_free=True,
    ),
    LLMModel(
        provider="openrouter",
        model_id="google/gemma-2-9b-it:free",
        name="Gemma 2 9B (Free)",
        input_cost=Decimal("0"),
        output_cost=Decimal("0"),
        context_length=8192,
        quality_score=7,
        speed_score=7,
        voice_suitability=7,
        recommended_for=[UseCase.SIMPLE_QA, UseCase.GENERAL],
        is_free=True,
    ),
    
    # === ULTRA-LOW COST (< $0.0005/1K tokens) ===
    LLMModel(
        provider="groq",
        model_id="groq/llama-3.1-8b-instant",
        name="Llama 3.1 8B (Groq)",
        input_cost=Decimal("0.00005"),
        output_cost=Decimal("0.00008"),
        context_length=8192,
        quality_score=7,
        speed_score=10,  # Groq is FAST
        voice_suitability=8,
        recommended_for=[UseCase.SIMPLE_QA, UseCase.CUSTOMER_SUPPORT, UseCase.GENERAL],
    ),
    LLMModel(
        provider="openrouter",
        model_id="gpt-4o-mini",
        name="GPT-4o Mini",
        input_cost=Decimal("0.00015"),
        output_cost=Decimal("0.0006"),
        context_length=128000,
        quality_score=9,
        speed_score=8,
        voice_suitability=9,
        recommended_for=[UseCase.CUSTOMER_SUPPORT, UseCase.SALES, UseCase.GENERAL],
    ),
    LLMModel(
        provider="openrouter",
        model_id="claude-3-haiku-20240307",
        name="Claude 3 Haiku",
        input_cost=Decimal("0.00025"),
        output_cost=Decimal("0.00125"),
        context_length=200000,
        quality_score=8,
        speed_score=9,
        voice_suitability=9,
        recommended_for=[UseCase.CUSTOMER_SUPPORT, UseCase.SALES, UseCase.GENERAL],
    ),
    
    # === LOW COST ($0.0005-0.002/1K tokens) ===
    LLMModel(
        provider="groq",
        model_id="groq/llama-3.1-70b-versatile",
        name="Llama 3.1 70B (Groq)",
        input_cost=Decimal("0.00059"),
        output_cost=Decimal("0.00079"),
        context_length=8192,
        quality_score=8,
        speed_score=9,
        voice_suitability=8,
        recommended_for=[UseCase.CUSTOMER_SUPPORT, UseCase.SALES, UseCase.GENERAL],
    ),
    LLMModel(
        provider="openrouter",
        model_id="gemini-1.5-flash",
        name="Gemini 1.5 Flash",
        input_cost=Decimal("0.000075"),
        output_cost=Decimal("0.0003"),
        context_length=1000000,
        quality_score=8,
        speed_score=9,
        voice_suitability=8,
        recommended_for=[UseCase.CUSTOMER_SUPPORT, UseCase.GENERAL],
    ),
    
    # === MEDIUM COST ($0.002-0.01/1K tokens) ===
    LLMModel(
        provider="openrouter",
        model_id="gemini-1.5-pro",
        name="Gemini 1.5 Pro",
        input_cost=Decimal("0.00125"),
        output_cost=Decimal("0.005"),
        context_length=2000000,
        quality_score=9,
        speed_score=7,
        voice_suitability=8,
        recommended_for=[UseCase.SALES, UseCase.LEGAL, UseCase.HEALTHCARE],
    ),
    LLMModel(
        provider="openai",
        model_id="gpt-4o",
        name="GPT-4o",
        input_cost=Decimal("0.005"),
        output_cost=Decimal("0.015"),
        context_length=128000,
        quality_score=10,
        speed_score=7,
        voice_suitability=10,
        recommended_for=[UseCase.SALES, UseCase.LEGAL, UseCase.HEALTHCARE],
    ),
    LLMModel(
        provider="anthropic",
        model_id="claude-3.5-sonnet-20241022",
        name="Claude 3.5 Sonnet",
        input_cost=Decimal("0.003"),
        output_cost=Decimal("0.015"),
        context_length=200000,
        quality_score=10,
        speed_score=7,
        voice_suitability=10,
        recommended_for=[UseCase.SALES, UseCase.LEGAL, UseCase.HEALTHCARE],
    ),
]


class SmartModelSelector:
    """
    Intelligently selects the best LLM model based on:
    - Use case requirements
    - Budget constraints
    - Quality requirements
    - Speed requirements
    
    Example:
        ```python
        selector = SmartModelSelector()
        
        # Get cheapest model for simple Q&A
        model = selector.get_cheapest_for(UseCase.SIMPLE_QA)
        
        # Get best value model (quality/cost ratio)
        model = selector.get_best_value()
        
        # Get all free models
        models = selector.get_free_models()
        
        # Get models ranked by cost
        models = selector.get_ranked_by_cost()
        ```
    """
    
    def __init__(self, models: Optional[List[LLMModel]] = None):
        self.models = models or CONVERSATION_MODELS
    
    def get_free_models(self) -> List[LLMModel]:
        """Get all free models, sorted by quality."""
        free = [m for m in self.models if m.is_free]
        return sorted(free, key=lambda m: m.quality_score, reverse=True)
    
    def get_ranked_by_cost(self) -> List[LLMModel]:
        """Get all models sorted by cost (cheapest first)."""
        return sorted(self.models, key=lambda m: m.avg_cost)
    
    def get_ranked_by_value(self) -> List[LLMModel]:
        """Get all models sorted by value (best quality/cost ratio)."""
        return sorted(self.models, key=lambda m: m.cost_effectiveness, reverse=True)
    
    def get_ranked_by_speed(self) -> List[LLMModel]:
        """Get models sorted by speed (fastest first)."""
        return sorted(self.models, key=lambda m: m.speed_score, reverse=True)
    
    def get_cheapest_for(self, use_case: UseCase) -> Optional[LLMModel]:
        """Get cheapest model suitable for a use case."""
        suitable = [m for m in self.models if use_case in m.recommended_for]
        if not suitable:
            suitable = self.models
        return min(suitable, key=lambda m: m.avg_cost)
    
    def get_best_for(self, use_case: UseCase) -> Optional[LLMModel]:
        """Get best quality model for a use case."""
        suitable = [m for m in self.models if use_case in m.recommended_for]
        if not suitable:
            suitable = self.models
        return max(suitable, key=lambda m: m.quality_score)
    
    def get_best_value_for(self, use_case: UseCase) -> Optional[LLMModel]:
        """Get best value model for a use case."""
        suitable = [m for m in self.models if use_case in m.recommended_for]
        if not suitable:
            suitable = self.models
        return max(suitable, key=lambda m: m.cost_effectiveness)
    
    def get_fastest(self) -> LLMModel:
        """Get the fastest model (Groq recommended)."""
        return max(self.models, key=lambda m: m.speed_score)
    
    def get_best_voice_model(self) -> LLMModel:
        """Get model most suitable for voice AI."""
        return max(self.models, key=lambda m: m.voice_suitability)
    
    def get_within_budget(
        self,
        max_cost_per_1k: float,
        use_case: Optional[UseCase] = None,
    ) -> List[LLMModel]:
        """Get models within a budget, sorted by quality."""
        max_cost = Decimal(str(max_cost_per_1k))
        
        within_budget = [m for m in self.models if m.avg_cost <= max_cost]
        
        if use_case:
            within_budget = [m for m in within_budget if use_case in m.recommended_for]
        
        return sorted(within_budget, key=lambda m: m.quality_score, reverse=True)
    
    def recommend(
        self,
        use_case: UseCase = UseCase.GENERAL,
        priority: str = "value",  # cost, value, quality, speed
        max_cost: Optional[float] = None,
    ) -> LLMModel:
        """
        Get a model recommendation based on requirements.
        
        Args:
            use_case: What the model will be used for
            priority: What to optimize for (cost, value, quality, speed)
            max_cost: Maximum cost per 1K tokens (optional)
            
        Returns:
            Recommended model
        """
        candidates = self.models
        
        # Filter by use case
        suitable = [m for m in candidates if use_case in m.recommended_for]
        if suitable:
            candidates = suitable
        
        # Filter by budget
        if max_cost is not None:
            within_budget = [m for m in candidates if float(m.avg_cost) <= max_cost]
            if within_budget:
                candidates = within_budget
        
        # Sort by priority
        if priority == "cost":
            return min(candidates, key=lambda m: m.avg_cost)
        elif priority == "quality":
            return max(candidates, key=lambda m: m.quality_score)
        elif priority == "speed":
            return max(candidates, key=lambda m: m.speed_score)
        else:  # value
            return max(candidates, key=lambda m: m.cost_effectiveness)
    
    def get_model_info(self, model_id: str) -> Optional[LLMModel]:
        """Get info for a specific model."""
        for m in self.models:
            if m.model_id == model_id:
                return m
        return None
    
    def compare_costs(
        self,
        monthly_tokens: int,
    ) -> List[Dict[str, Any]]:
        """
        Compare monthly costs across all models.
        
        Args:
            monthly_tokens: Expected monthly token usage
            
        Returns:
            List of models with estimated monthly cost
        """
        results = []
        
        for m in sorted(self.models, key=lambda x: x.avg_cost):
            monthly_cost = float(m.avg_cost) * (monthly_tokens / 1000)
            
            results.append({
                "model": m.name,
                "model_id": m.model_id,
                "provider": m.provider,
                "cost_per_1k": float(m.avg_cost),
                "monthly_cost": round(monthly_cost, 2),
                "quality_score": m.quality_score,
                "voice_suitability": m.voice_suitability,
                "is_free": m.is_free,
            })
        
        return results
    
    def get_recommendations_summary(self) -> Dict[str, Any]:
        """Get a summary of recommendations for different needs."""
        return {
            "cheapest_overall": self.get_ranked_by_cost()[0].name,
            "best_free": self.get_free_models()[0].name if self.get_free_models() else None,
            "best_value": self.get_ranked_by_value()[0].name,
            "fastest": self.get_fastest().name,
            "best_for_voice": self.get_best_voice_model().name,
            "best_for_support": self.get_best_for(UseCase.CUSTOMER_SUPPORT).name,
            "best_for_sales": self.get_best_for(UseCase.SALES).name,
            "for_budget_users": {
                "model": "Mistral 7B (Free)",
                "cost": "FREE",
                "quality": "Good for most use cases",
            },
            "for_production": {
                "model": "GPT-4o Mini",
                "cost": "$0.00038/1K tokens avg",
                "quality": "Excellent for voice AI",
            },
            "for_enterprise": {
                "model": "Claude 3.5 Sonnet",
                "cost": "$0.009/1K tokens avg",
                "quality": "Best quality",
            },
        }


# Convenience function
def get_model_selector() -> SmartModelSelector:
    """Get the global model selector instance."""
    return SmartModelSelector()


# Quick access functions
def get_cheapest_model() -> LLMModel:
    """Get the cheapest model (free if available)."""
    selector = SmartModelSelector()
    free = selector.get_free_models()
    if free:
        return free[0]
    return selector.get_ranked_by_cost()[0]


def get_best_value_model() -> LLMModel:
    """Get the best value model (quality/cost)."""
    return SmartModelSelector().get_ranked_by_value()[0]


def get_recommended_model(use_case: str = "general") -> LLMModel:
    """Get recommended model for a use case."""
    use_case_map = {
        "simple": UseCase.SIMPLE_QA,
        "support": UseCase.CUSTOMER_SUPPORT,
        "sales": UseCase.SALES,
        "healthcare": UseCase.HEALTHCARE,
        "legal": UseCase.LEGAL,
        "general": UseCase.GENERAL,
    }
    uc = use_case_map.get(use_case.lower(), UseCase.GENERAL)
    return SmartModelSelector().recommend(use_case=uc)


# ==================== BALANCE-AWARE MODEL SELECTOR ====================

class BalanceAwareModelSelector:
    """
    Automatically selects the best LLM model based on user's wallet balance.
    
    - Low balance → Use FREE models
    - Medium balance → Use cheap models  
    - High balance → Use best quality models
    
    This ensures users never run out of balance mid-conversation
    and always get the best value for their money.
    
    Example:
        ```python
        selector = BalanceAwareModelSelector()
        
        # Get model based on user's balance
        model = selector.get_model_for_balance(
            account_id="user_123",
            use_case="support"
        )
        
        # System automatically picks:
        # - FREE Mistral 7B if balance < $1
        # - GPT-4o Mini if balance $1-$10
        # - Claude 3.5 if balance > $10
        ```
    """
    
    # Balance thresholds
    CRITICAL_BALANCE = Decimal("1.00")   # Below this → FREE models only
    LOW_BALANCE = Decimal("5.00")        # Below this → Cheap models
    MEDIUM_BALANCE = Decimal("20.00")    # Below this → Mid-tier models
    # Above MEDIUM = Premium models allowed
    
    def __init__(self):
        self._model_selector = SmartModelSelector()
        self._billing_manager = None
    
    def _get_billing_manager(self):
        """Lazy load billing manager to avoid circular imports."""
        if self._billing_manager is None:
            try:
                from sunona.billing import BillingManager
                self._billing_manager = BillingManager()
            except ImportError:
                logger.warning("Billing not available, using default model selection")
        return self._billing_manager
    
    def get_user_balance(self, account_id: str) -> Decimal:
        """Get user's current balance."""
        billing = self._get_billing_manager()
        if billing:
            account = billing.get_account(account_id)
            if account:
                return account.balance
        return Decimal("10.00")  # Default if billing unavailable
    
    def get_model_for_balance(
        self,
        account_id: str,
        use_case: str = "general",
        estimated_tokens: int = 1000,
    ) -> LLMModel:
        """
        Get the best model based on user's wallet balance.
        
        Args:
            account_id: User's account ID
            use_case: What the model is used for
            estimated_tokens: Estimated tokens for this request
            
        Returns:
            Best model that fits the user's budget
        """
        balance = self.get_user_balance(account_id)
        
        use_case_enum = {
            "simple": UseCase.SIMPLE_QA,
            "support": UseCase.CUSTOMER_SUPPORT,
            "sales": UseCase.SALES,
            "healthcare": UseCase.HEALTHCARE,
            "legal": UseCase.LEGAL,
            "general": UseCase.GENERAL,
        }.get(use_case.lower(), UseCase.GENERAL)
        
        logger.info(f"Selecting model for {account_id}: balance=${balance}, use_case={use_case}")
        
        # CRITICAL: Balance below $1 → FREE models only
        if balance < self.CRITICAL_BALANCE:
            model = self._get_free_model(use_case_enum)
            logger.info(f"Critical balance: Selected FREE model {model.name}")
            return model
        
        # LOW: Balance $1-$5 → Ultra-cheap models
        if balance < self.LOW_BALANCE:
            max_cost = 0.0005  # $0.0005 per 1K tokens max
            model = self._model_selector.recommend(
                use_case=use_case_enum,
                priority="cost",
                max_cost=max_cost,
            )
            # If no cheap model found, use free
            if float(model.avg_cost) > max_cost:
                model = self._get_free_model(use_case_enum)
            logger.info(f"Low balance: Selected cheap model {model.name}")
            return model
        
        # MEDIUM: Balance $5-$20 → Mid-tier models
        if balance < self.MEDIUM_BALANCE:
            max_cost = 0.002  # $0.002 per 1K tokens max
            model = self._model_selector.recommend(
                use_case=use_case_enum,
                priority="value",  # Best value at this tier
                max_cost=max_cost,
            )
            logger.info(f"Medium balance: Selected mid-tier model {model.name}")
            return model
        
        # HIGH: Balance > $20 → Best quality models
        model = self._model_selector.recommend(
            use_case=use_case_enum,
            priority="quality",
        )
        logger.info(f"High balance: Selected premium model {model.name}")
        return model
    
    def _get_free_model(self, use_case: UseCase) -> LLMModel:
        """Get the best free model for a use case."""
        free_models = self._model_selector.get_free_models()
        
        # Try to find one suitable for use case
        for m in free_models:
            if use_case in m.recommended_for:
                return m
        
        # Return best free model
        return free_models[0] if free_models else self._model_selector.get_ranked_by_cost()[0]
    
    def get_model_with_cost_estimate(
        self,
        account_id: str,
        use_case: str = "general",
        estimated_tokens: int = 1000,
    ) -> Dict[str, Any]:
        """
        Get model with cost estimate for this request.
        
        Returns model info and what it will cost.
        """
        balance = self.get_user_balance(account_id)
        model = self.get_model_for_balance(account_id, use_case, estimated_tokens)
        
        estimated_cost = float(model.avg_cost) * (estimated_tokens / 1000)
        remaining_after = float(balance) - estimated_cost
        
        # How many more requests at this rate?
        requests_remaining = int(remaining_after / estimated_cost) if estimated_cost > 0 else float('inf')
        
        return {
            "model": model.name,
            "model_id": model.model_id,
            "provider": model.provider,
            "is_free": model.is_free,
            "estimated_cost": round(estimated_cost, 6),
            "current_balance": float(balance),
            "balance_after": round(remaining_after, 4),
            "requests_remaining": requests_remaining if requests_remaining != float('inf') else "unlimited",
            "balance_tier": self._get_balance_tier(balance),
            "suggestion": self._get_suggestion(balance),
        }
    
    def _get_balance_tier(self, balance: Decimal) -> str:
        """Get balance tier name."""
        if balance < self.CRITICAL_BALANCE:
            return "critical"
        elif balance < self.LOW_BALANCE:
            return "low"
        elif balance < self.MEDIUM_BALANCE:
            return "medium"
        else:
            return "high"
    
    def _get_suggestion(self, balance: Decimal) -> str:
        """Get suggestion based on balance."""
        if balance < self.CRITICAL_BALANCE:
            return "⚠️ Balance critical! Using FREE models. Top up to access better models."
        elif balance < self.LOW_BALANCE:
            return "💡 Low balance. Using budget models to save costs."
        elif balance < self.MEDIUM_BALANCE:
            return "✅ Using mid-tier models. Good balance of cost and quality."
        else:
            return "🚀 Full access to premium models!"
    
    def should_warn_low_balance(self, account_id: str) -> Optional[str]:
        """Check if user should be warned about low balance."""
        balance = self.get_user_balance(account_id)
        
        if balance < Decimal("0.50"):
            return f"⚠️ Balance very low (${balance}). Please top up to continue using premium features."
        elif balance < self.CRITICAL_BALANCE:
            return f"💡 Balance at ${balance}. Switched to FREE models to save costs."
        elif balance < self.LOW_BALANCE:
            return f"📊 Balance at ${balance}. Using budget-friendly models."
        
        return None


# Global instance
_balance_aware_selector = None


def get_balance_aware_selector() -> BalanceAwareModelSelector:
    """Get the global balance-aware selector."""
    global _balance_aware_selector
    if _balance_aware_selector is None:
        _balance_aware_selector = BalanceAwareModelSelector()
    return _balance_aware_selector


def get_smart_model(
    account_id: str,
    use_case: str = "general",
) -> LLMModel:
    """
    Get the smartest model choice based on user's balance.
    
    This is the RECOMMENDED way to select models.
    It automatically picks the best model the user can afford.
    
    Args:
        account_id: User's account ID
        use_case: simple, support, sales, healthcare, legal, general
        
    Returns:
        Best model for user's budget
    """
    return get_balance_aware_selector().get_model_for_balance(account_id, use_case)


def get_smart_model_with_info(
    account_id: str,
    use_case: str = "general",
    estimated_tokens: int = 1000,
) -> Dict[str, Any]:
    """
    Get smart model with full cost and balance info.
    
    Returns model choice plus cost estimates.
    """
    return get_balance_aware_selector().get_model_with_cost_estimate(
        account_id, use_case, estimated_tokens
    )
