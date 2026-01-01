"""
Sunona Voice AI - Cost Tracker

Per-provider cost tracking for voice AI operations.
Tracks LLM, STT, and TTS costs based on usage.

Features:
- Real-time cost calculation
- Per-provider pricing models
- Token and audio-based pricing
- Cost aggregation and reporting
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
from enum import Enum

logger = logging.getLogger(__name__)


class CostCategory(str, Enum):
    """Cost categories."""
    LLM = "llm"
    TRANSCRIPTION = "transcription"
    SYNTHESIS = "synthesis"
    TELEPHONY = "telephony"


@dataclass
class ProviderPricing:
    """
    Pricing model for a provider.
    
    Attributes:
        provider: Provider name
        category: Cost category (llm, transcription, synthesis)
        input_cost_per_1k: Cost per 1000 input tokens (LLM)
        output_cost_per_1k: Cost per 1000 output tokens (LLM)
        cost_per_minute: Cost per minute of audio
        cost_per_character: Cost per character (TTS)
        base_cost: Fixed cost per request
    """
    provider: str
    category: CostCategory
    input_cost_per_1k: float = 0.0
    output_cost_per_1k: float = 0.0
    cost_per_minute: float = 0.0
    cost_per_character: float = 0.0
    base_cost: float = 0.0


# Default pricing models (as of 2024)
DEFAULT_PRICING = {
    # LLM Providers
    ("openai", "gpt-4o"): ProviderPricing(
        provider="openai",
        category=CostCategory.LLM,
        input_cost_per_1k=0.0025,
        output_cost_per_1k=0.01,
    ),
    ("openai", "gpt-4o-mini"): ProviderPricing(
        provider="openai",
        category=CostCategory.LLM,
        input_cost_per_1k=0.00015,
        output_cost_per_1k=0.0006,
    ),
    ("anthropic", "claude-3-5-sonnet"): ProviderPricing(
        provider="anthropic",
        category=CostCategory.LLM,
        input_cost_per_1k=0.003,
        output_cost_per_1k=0.015,
    ),
    ("groq", "llama-3.1-70b"): ProviderPricing(
        provider="groq",
        category=CostCategory.LLM,
        input_cost_per_1k=0.00059,
        output_cost_per_1k=0.00079,
    ),
    
    # Transcription
    ("deepgram", "nova-2"): ProviderPricing(
        provider="deepgram",
        category=CostCategory.TRANSCRIPTION,
        cost_per_minute=0.0043,
    ),
    ("openai", "whisper"): ProviderPricing(
        provider="openai",
        category=CostCategory.TRANSCRIPTION,
        cost_per_minute=0.006,
    ),
    
    # TTS
    ("elevenlabs", "turbo_v2_5"): ProviderPricing(
        provider="elevenlabs",
        category=CostCategory.SYNTHESIS,
        cost_per_character=0.00003,
    ),
    ("openai", "tts-1"): ProviderPricing(
        provider="openai",
        category=CostCategory.SYNTHESIS,
        cost_per_character=0.000015,
    ),
    ("deepgram", "aura"): ProviderPricing(
        provider="deepgram",
        category=CostCategory.SYNTHESIS,
        cost_per_character=0.000015,
    ),
    
    # Telephony
    ("twilio", "voice"): ProviderPricing(
        provider="twilio",
        category=CostCategory.TELEPHONY,
        cost_per_minute=0.014,
    ),
    ("plivo", "voice"): ProviderPricing(
        provider="plivo",
        category=CostCategory.TELEPHONY,
        cost_per_minute=0.01,
    ),
}


@dataclass
class CostEntry:
    """Single cost entry."""
    timestamp: datetime
    category: CostCategory
    provider: str
    model: str
    cost: float
    usage: Dict[str, Any] = field(default_factory=dict)
    conversation_id: Optional[str] = None


class CostTracker:
    """
    Track costs across providers.
    
    Calculates and aggregates costs for LLM, STT, TTS, and telephony usage.
    
    Example:
        ```python
        tracker = CostTracker()
        
        # Track LLM usage
        cost = tracker.track_llm(
            provider="openai",
            model="gpt-4o-mini",
            input_tokens=500,
            output_tokens=200
        )
        
        # Track TTS usage
        cost = tracker.track_synthesis(
            provider="elevenlabs",
            character_count=500
        )
        
        # Get total cost
        total = tracker.get_total_cost()
        ```
    """
    
    def __init__(
        self,
        custom_pricing: Optional[Dict[tuple, ProviderPricing]] = None,
    ):
        """
        Initialize cost tracker.
        
        Args:
            custom_pricing: Custom pricing overrides
        """
        self._pricing = {**DEFAULT_PRICING}
        if custom_pricing:
            self._pricing.update(custom_pricing)
        
        self._entries: List[CostEntry] = []
        self._totals: Dict[CostCategory, float] = defaultdict(float)
        
        logger.info("Cost tracker initialized")
    
    def _get_pricing(self, provider: str, model: str) -> Optional[ProviderPricing]:
        """Get pricing for a provider/model combination."""
        # Try exact match
        if (provider, model) in self._pricing:
            return self._pricing[(provider, model)]
        
        # Try provider-only match
        for (p, m), pricing in self._pricing.items():
            if p == provider:
                return pricing
        
        return None
    
    def track_llm(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        conversation_id: Optional[str] = None,
    ) -> float:
        """
        Track LLM usage cost.
        
        Args:
            provider: Provider name
            model: Model name
            input_tokens: Input token count
            output_tokens: Output token count
            conversation_id: Associated conversation
            
        Returns:
            Cost in USD
        """
        pricing = self._get_pricing(provider, model)
        
        if not pricing:
            logger.warning(f"No pricing for {provider}/{model}, using estimates")
            # Default estimate: $0.001 per 1K tokens
            cost = (input_tokens + output_tokens) * 0.000001
        else:
            input_cost = (input_tokens / 1000) * pricing.input_cost_per_1k
            output_cost = (output_tokens / 1000) * pricing.output_cost_per_1k
            cost = input_cost + output_cost + pricing.base_cost
        
        entry = CostEntry(
            timestamp=datetime.now(),
            category=CostCategory.LLM,
            provider=provider,
            model=model,
            cost=cost,
            usage={
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            },
            conversation_id=conversation_id,
        )
        
        self._entries.append(entry)
        self._totals[CostCategory.LLM] += cost
        
        return cost
    
    def track_transcription(
        self,
        provider: str,
        duration_seconds: float,
        model: str = "default",
        conversation_id: Optional[str] = None,
    ) -> float:
        """
        Track transcription usage cost.
        
        Args:
            provider: Provider name
            duration_seconds: Audio duration in seconds
            model: Model name
            conversation_id: Associated conversation
            
        Returns:
            Cost in USD
        """
        pricing = self._get_pricing(provider, model)
        
        duration_minutes = duration_seconds / 60
        
        if not pricing:
            # Default: $0.005 per minute
            cost = duration_minutes * 0.005
        else:
            cost = duration_minutes * pricing.cost_per_minute + pricing.base_cost
        
        entry = CostEntry(
            timestamp=datetime.now(),
            category=CostCategory.TRANSCRIPTION,
            provider=provider,
            model=model,
            cost=cost,
            usage={"duration_seconds": duration_seconds},
            conversation_id=conversation_id,
        )
        
        self._entries.append(entry)
        self._totals[CostCategory.TRANSCRIPTION] += cost
        
        return cost
    
    def track_synthesis(
        self,
        provider: str,
        character_count: int,
        model: str = "default",
        conversation_id: Optional[str] = None,
    ) -> float:
        """
        Track synthesis (TTS) usage cost.
        
        Args:
            provider: Provider name
            character_count: Number of characters synthesized
            model: Model name
            conversation_id: Associated conversation
            
        Returns:
            Cost in USD
        """
        pricing = self._get_pricing(provider, model)
        
        if not pricing:
            # Default: $0.00002 per character
            cost = character_count * 0.00002
        else:
            cost = character_count * pricing.cost_per_character + pricing.base_cost
        
        entry = CostEntry(
            timestamp=datetime.now(),
            category=CostCategory.SYNTHESIS,
            provider=provider,
            model=model,
            cost=cost,
            usage={"character_count": character_count},
            conversation_id=conversation_id,
        )
        
        self._entries.append(entry)
        self._totals[CostCategory.SYNTHESIS] += cost
        
        return cost
    
    def track_telephony(
        self,
        provider: str,
        duration_seconds: float,
        conversation_id: Optional[str] = None,
    ) -> float:
        """
        Track telephony usage cost.
        
        Args:
            provider: Provider name (twilio, plivo)
            duration_seconds: Call duration in seconds
            conversation_id: Associated conversation
            
        Returns:
            Cost in USD
        """
        pricing = self._get_pricing(provider, "voice")
        
        duration_minutes = duration_seconds / 60
        
        if not pricing:
            # Default: $0.015 per minute
            cost = duration_minutes * 0.015
        else:
            cost = duration_minutes * pricing.cost_per_minute + pricing.base_cost
        
        entry = CostEntry(
            timestamp=datetime.now(),
            category=CostCategory.TELEPHONY,
            provider=provider,
            model="voice",
            cost=cost,
            usage={"duration_seconds": duration_seconds},
            conversation_id=conversation_id,
        )
        
        self._entries.append(entry)
        self._totals[CostCategory.TELEPHONY] += cost
        
        return cost
    
    def get_total_cost(self) -> float:
        """Get total tracked cost."""
        return sum(self._totals.values())
    
    def get_cost_by_category(self) -> Dict[str, float]:
        """Get costs broken down by category."""
        return {cat.value: cost for cat, cost in self._totals.items()}
    
    def get_cost_by_provider(self) -> Dict[str, float]:
        """Get costs broken down by provider."""
        provider_costs = defaultdict(float)
        for entry in self._entries:
            provider_costs[entry.provider] += entry.cost
        return dict(provider_costs)
    
    def get_conversation_cost(self, conversation_id: str) -> float:
        """Get total cost for a specific conversation."""
        return sum(
            e.cost for e in self._entries 
            if e.conversation_id == conversation_id
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get cost summary."""
        return {
            "total_cost_usd": self.get_total_cost(),
            "by_category": self.get_cost_by_category(),
            "by_provider": self.get_cost_by_provider(),
            "entry_count": len(self._entries),
        }
    
    def clear(self) -> None:
        """Clear all tracked costs."""
        self._entries.clear()
        self._totals.clear()
