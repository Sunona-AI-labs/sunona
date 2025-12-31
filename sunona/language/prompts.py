"""
Sunona Voice AI - Localized Prompts

Multi-language system prompts and responses.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# Common phrases in multiple languages
COMMON_PHRASES = {
    "greeting": {
        "en": "Hello! How can I help you today?",
        "hi": "नमस्ते! आज मैं आपकी कैसे मदद कर सकता हूं?",
        "hi-en": "Hello! Main aapki kaise help kar sakta hoon?",
        "es": "¡Hola! ¿Cómo puedo ayudarte hoy?",
        "fr": "Bonjour! Comment puis-je vous aider aujourd'hui?",
        "de": "Hallo! Wie kann ich Ihnen heute helfen?",
        "ar": "مرحبا! كيف يمكنني مساعدتك اليوم؟",
        "zh": "您好！今天我能帮您什么？",
        "ja": "こんにちは！本日はどのようにお手伝いできますか？",
    },
    "goodbye": {
        "en": "Thank you for calling. Have a great day!",
        "hi": "कॉल करने के लिए धन्यवाद। आपका दिन शुभ हो!",
        "hi-en": "Call karne ke liye thank you. Have a great day!",
        "es": "Gracias por llamar. ¡Que tenga un buen día!",
        "fr": "Merci d'avoir appelé. Bonne journée!",
        "de": "Danke für Ihren Anruf. Einen schönen Tag noch!",
    },
    "hold_please": {
        "en": "Please hold while I look that up for you.",
        "hi": "कृपया रुकें, मैं यह जानकारी ढूंढ रहा हूं।",
        "hi-en": "Please thoda hold karein, main check karta hoon.",
        "es": "Por favor espere mientras verifico eso.",
        "fr": "Veuillez patienter pendant que je vérifie.",
    },
    "didnt_understand": {
        "en": "I'm sorry, I didn't quite catch that. Could you please repeat?",
        "hi": "माफ़ कीजिए, मुझे समझ नहीं आया। क्या आप दोहरा सकते हैं?",
        "hi-en": "Sorry, samajh nahi aaya. Kya aap repeat kar sakte hain?",
        "es": "Lo siento, no entendí. ¿Podría repetir?",
        "fr": "Désolé, je n'ai pas compris. Pourriez-vous répéter?",
    },
    "transfer": {
        "en": "Let me transfer you to a human agent.",
        "hi": "मैं आपको एक एजेंट से जोड़ता हूं।",
        "hi-en": "Main aapko ek agent se connect karta hoon.",
        "es": "Permítame transferirle a un agente.",
        "fr": "Permettez-moi de vous transférer à un agent.",
    },
    "confirm": {
        "en": "Just to confirm, you said",
        "hi": "पुष्टि के लिए, आपने कहा",
        "hi-en": "Confirm karne ke liye, aapne bola",
        "es": "Para confirmar, usted dijo",
        "fr": "Pour confirmer, vous avez dit",
    },
}


class LocalizedPrompts:
    """
    Manage localized prompts for voice agents.
    
    Provides language-specific versions of common phrases
    and system prompts.
    
    Example:
        ```python
        prompts = LocalizedPrompts(language="hi")
        
        greeting = prompts.get_phrase("greeting")
        system = prompts.get_system_prompt("support")
        ```
    """
    
    def __init__(
        self,
        language: str = "en",
        fallback_language: str = "en",
    ):
        """
        Initialize localized prompts.
        
        Args:
            language: Primary language code
            fallback_language: Fallback if phrase not available
        """
        self._language = language
        self._fallback = fallback_language
        self._custom_phrases: Dict[str, Dict[str, str]] = {}
    
    @property
    def language(self) -> str:
        """Get current language."""
        return self._language
    
    @language.setter
    def language(self, value: str) -> None:
        """Set language."""
        self._language = value
    
    def get_phrase(
        self,
        key: str,
        language: Optional[str] = None,
        **format_args,
    ) -> str:
        """
        Get a localized phrase.
        
        Args:
            key: Phrase key
            language: Override language
            **format_args: Format arguments
            
        Returns:
            Localized phrase
        """
        lang = language or self._language
        
        # Check custom phrases first
        if key in self._custom_phrases:
            phrases = self._custom_phrases[key]
            phrase = phrases.get(lang) or phrases.get(self._fallback, "")
        else:
            # Check built-in phrases
            phrases = COMMON_PHRASES.get(key, {})
            phrase = phrases.get(lang) or phrases.get(self._fallback, key)
        
        # Apply format args
        if format_args:
            try:
                phrase = phrase.format(**format_args)
            except KeyError:
                pass
        
        return phrase
    
    def add_phrase(
        self,
        key: str,
        translations: Dict[str, str],
    ) -> None:
        """
        Add a custom phrase with translations.
        
        Args:
            key: Phrase key
            translations: Dict of language code -> text
        """
        self._custom_phrases[key] = translations
    
    def get_system_prompt(
        self,
        domain: str,
        business_name: str = "Our Company",
        agent_name: str = "Alex",
    ) -> str:
        """
        Get localized system prompt for a domain.
        
        Args:
            domain: Domain type (support, hospitality, etc.)
            business_name: Business name
            agent_name: Agent name
            
        Returns:
            Localized system prompt
        """
        prompts = self._get_domain_prompts()
        
        base = prompts.get(domain, {}).get(self._language)
        if not base:
            base = prompts.get(domain, {}).get(self._fallback, "")
        
        return base.format(
            business_name=business_name,
            agent_name=agent_name,
        )
    
    def _get_domain_prompts(self) -> Dict[str, Dict[str, str]]:
        """Get domain-specific prompts."""
        return {
            "support": {
                "en": """You are {agent_name}, a customer support agent for {business_name}.
Help customers with their inquiries professionally and efficiently.
Be patient, understanding, and always aim to resolve issues.""",
                
                "hi": """आप {agent_name} हैं, {business_name} के ग्राहक सेवा प्रतिनिधि।
ग्राहकों की समस्याओं को पेशेवर तरीके से हल करें।
धैर्यवान और समझदार बनें।""",
                
                "hi-en": """Aap {agent_name} hain, {business_name} ke customer support agent.
Customers ki problems solve karein professionally.
Patient aur understanding rahein.""",
            },
            "hospitality": {
                "en": """You are {agent_name}, a receptionist at {business_name}.
Help guests with reservations, inquiries, and bookings.
Be warm, welcoming, and professional.""",
                
                "hi": """आप {agent_name} हैं, {business_name} के रिसेप्शनिस्ट।
मेहमानों की बुकिंग और पूछताछ में मदद करें।
गर्मजोशी और पेशेवर बनें।""",
            },
        }
    
    def get_available_languages(self) -> List[str]:
        """Get languages available for common phrases."""
        languages = set()
        for phrases in COMMON_PHRASES.values():
            languages.update(phrases.keys())
        return sorted(languages)
    
    def translate_template(
        self,
        template: str,
        target_language: str,
        llm=None,
    ) -> str:
        """
        Translate a system prompt template to another language.
        
        Note: This requires an LLM for accurate translation.
        """
        if not llm:
            logger.warning("LLM required for template translation")
            return template
        
        # Implementation would use LLM to translate
        # Left as placeholder for async implementation
        return template
