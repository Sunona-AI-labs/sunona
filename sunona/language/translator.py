"""
Sunona Voice AI - Translator

Real-time translation for multilingual conversations.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class Translator:
    """
    Real-time translation for voice AI conversations.
    
    Supports translation between any supported language pair
    using LLM or external translation services.
    
    Example:
        ```python
        translator = Translator(llm=my_llm)
        
        # Translate user input
        english = await translator.translate(
            text="मैं एक रूम बुक करना चाहता हूं",
            source="hi",
            target="en"
        )
        
        # Translate response back
        hindi = await translator.translate(
            text="I'd be happy to help you book a room",
            source="en",
            target="hi"
        )
        ```
    """
    
    def __init__(
        self,
        llm=None,
        cache_translations: bool = True,
    ):
        """
        Initialize translator.
        
        Args:
            llm: LLM instance for translation
            cache_translations: Cache repeated translations
        """
        self._llm = llm
        self._cache_enabled = cache_translations
        self._cache: Dict[str, str] = {}
    
    async def translate(
        self,
        text: str,
        source: str,
        target: str,
        context: Optional[str] = None,
    ) -> str:
        """
        Translate text between languages.
        
        Args:
            text: Text to translate
            source: Source language code
            target: Target language code
            context: Optional context for better translation
            
        Returns:
            Translated text
        """
        if source == target:
            return text
        
        # Check cache
        cache_key = f"{source}:{target}:{text}"
        if self._cache_enabled and cache_key in self._cache:
            return self._cache[cache_key]
        
        if self._llm:
            translated = await self._translate_with_llm(
                text, source, target, context
            )
        else:
            # Fallback to simple phrase replacement
            translated = text
            logger.warning("No LLM configured, returning original text")
        
        # Cache result
        if self._cache_enabled:
            self._cache[cache_key] = translated
        
        return translated
    
    async def _translate_with_llm(
        self,
        text: str,
        source: str,
        target: str,
        context: Optional[str] = None,
    ) -> str:
        """Translate using LLM."""
        context_hint = ""
        if context:
            context_hint = f"\nContext: {context}"
        
        prompt = f"""Translate the following text from {source} to {target}.
Maintain the same tone and meaning. For conversational text, keep it natural.
{context_hint}

Text to translate: "{text}"

Provide only the translated text, no explanations."""
        
        try:
            response = await self._llm.generate(
                messages=[{"role": "user", "content": prompt}],
            )
            
            # Clean up response
            translated = response.strip().strip('"').strip("'")
            
            return translated
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text
    
    async def translate_batch(
        self,
        texts: List[str],
        source: str,
        target: str,
    ) -> List[str]:
        """
        Translate multiple texts at once.
        
        Args:
            texts: List of texts to translate
            source: Source language
            target: Target language
            
        Returns:
            List of translated texts
        """
        results = []
        for text in texts:
            translated = await self.translate(text, source, target)
            results.append(translated)
        return results
    
    def clear_cache(self) -> None:
        """Clear translation cache."""
        self._cache.clear()


class ConversationTranslator:
    """
    Bidirectional translation for voice conversations.
    
    Handles translating user input to agent language and
    agent responses back to user language.
    """
    
    def __init__(
        self,
        llm=None,
        agent_language: str = "en",
    ):
        """
        Initialize conversation translator.
        
        Args:
            llm: LLM for translation
            agent_language: Language agent operates in
        """
        self._translator = Translator(llm=llm)
        self._agent_language = agent_language
        self._user_language: Optional[str] = None
    
    def set_user_language(self, language: str) -> None:
        """Set the user's language."""
        self._user_language = language
        logger.info(f"User language set to: {language}")
    
    async def translate_user_input(
        self,
        text: str,
        detected_language: Optional[str] = None,
    ) -> str:
        """
        Translate user input to agent language.
        
        Args:
            text: User's message
            detected_language: Detected language (if known)
            
        Returns:
            Translated text for agent
        """
        source = detected_language or self._user_language or "en"
        
        if source == self._agent_language:
            return text
        
        return await self._translator.translate(
            text,
            source=source,
            target=self._agent_language,
        )
    
    async def translate_agent_response(
        self,
        text: str,
    ) -> str:
        """
        Translate agent response to user language.
        
        Args:
            text: Agent's response
            
        Returns:
            Translated text for user
        """
        if not self._user_language or self._user_language == self._agent_language:
            return text
        
        return await self._translator.translate(
            text,
            source=self._agent_language,
            target=self._user_language,
        )
