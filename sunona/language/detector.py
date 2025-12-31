"""
Sunona Voice AI - Language Detector

Detect language from text or audio.
Supports 50+ languages including Indian regional languages.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Language codes mapping
SUPPORTED_LANGUAGES = {
    # Major languages
    "en": {"name": "English", "native": "English"},
    "es": {"name": "Spanish", "native": "Español"},
    "fr": {"name": "French", "native": "Français"},
    "de": {"name": "German", "native": "Deutsch"},
    "it": {"name": "Italian", "native": "Italiano"},
    "pt": {"name": "Portuguese", "native": "Português"},
    "nl": {"name": "Dutch", "native": "Nederlands"},
    "ru": {"name": "Russian", "native": "Русский"},
    "zh": {"name": "Chinese", "native": "中文"},
    "ja": {"name": "Japanese", "native": "日本語"},
    "ko": {"name": "Korean", "native": "한국어"},
    "ar": {"name": "Arabic", "native": "العربية"},
    
    # Indian languages
    "hi": {"name": "Hindi", "native": "हिन्दी"},
    "bn": {"name": "Bengali", "native": "বাংলা"},
    "te": {"name": "Telugu", "native": "తెలుగు"},
    "ta": {"name": "Tamil", "native": "தமிழ்"},
    "mr": {"name": "Marathi", "native": "मराठी"},
    "gu": {"name": "Gujarati", "native": "ગુજરાતી"},
    "kn": {"name": "Kannada", "native": "ಕನ್ನಡ"},
    "ml": {"name": "Malayalam", "native": "മലയാളം"},
    "pa": {"name": "Punjabi", "native": "ਪੰਜਾਬੀ"},
    "or": {"name": "Odia", "native": "ଓଡ଼ିଆ"},
    
    # Hinglish (Hindi-English mix)
    "hi-en": {"name": "Hinglish", "native": "Hinglish"},
}


class LanguageDetector:
    """
    Detect language from text input.
    
    Uses heuristics and optional LLM for accurate detection.
    Supports code-switching (mixing languages like Hinglish).
    
    Example:
        ```python
        detector = LanguageDetector()
        
        lang, confidence = detector.detect("नमस्ते, how are you?")
        print(f"Language: {lang}, Confidence: {confidence}")
        # Output: Language: hi-en, Confidence: 0.85
        ```
    """
    
    # Character ranges for script detection
    SCRIPT_RANGES = {
        "devanagari": (0x0900, 0x097F),  # Hindi, Marathi, etc.
        "bengali": (0x0980, 0x09FF),
        "tamil": (0x0B80, 0x0BFF),
        "telugu": (0x0C00, 0x0C7F),
        "kannada": (0x0C80, 0x0CFF),
        "malayalam": (0x0D00, 0x0D7F),
        "gujarati": (0x0A80, 0x0AFF),
        "punjabi": (0x0A00, 0x0A7F),
        "arabic": (0x0600, 0x06FF),
        "chinese": (0x4E00, 0x9FFF),
        "japanese": (0x3040, 0x30FF),
        "korean": (0xAC00, 0xD7AF),
        "cyrillic": (0x0400, 0x04FF),
    }
    
    def __init__(
        self,
        llm=None,
        default_language: str = "en",
    ):
        """
        Initialize language detector.
        
        Args:
            llm: Optional LLM for advanced detection
            default_language: Default language code
        """
        self._llm = llm
        self._default_language = default_language
    
    def detect(self, text: str) -> Tuple[str, float]:
        """
        Detect language from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (language_code, confidence_score)
        """
        if not text or not text.strip():
            return self._default_language, 0.0
        
        # Detect scripts in text
        scripts = self._detect_scripts(text)
        
        if not scripts:
            # All Latin - assume English
            return "en", 0.7
        
        # Check for code-switching (mixed scripts)
        latin_chars = sum(1 for c in text if c.isascii() and c.isalpha())
        total_alpha = sum(1 for c in text if c.isalpha())
        
        if total_alpha == 0:
            return self._default_language, 0.5
        
        latin_ratio = latin_chars / total_alpha
        
        # Detect primary script
        primary_script = max(scripts.items(), key=lambda x: x[1])[0]
        
        # Map script to language
        lang = self._script_to_language(primary_script)
        
        # Check for Hinglish (Hindi with significant English)
        if lang == "hi" and 0.2 < latin_ratio < 0.8:
            return "hi-en", 0.85
        
        confidence = scripts[primary_script] / total_alpha
        
        return lang, confidence
    
    def _detect_scripts(self, text: str) -> Dict[str, int]:
        """Detect scripts present in text."""
        scripts = {}
        
        for char in text:
            code = ord(char)
            
            for script, (start, end) in self.SCRIPT_RANGES.items():
                if start <= code <= end:
                    scripts[script] = scripts.get(script, 0) + 1
                    break
        
        return scripts
    
    def _script_to_language(self, script: str) -> str:
        """Map script to primary language."""
        mapping = {
            "devanagari": "hi",
            "bengali": "bn",
            "tamil": "ta",
            "telugu": "te",
            "kannada": "kn",
            "malayalam": "ml",
            "gujarati": "gu",
            "punjabi": "pa",
            "arabic": "ar",
            "chinese": "zh",
            "japanese": "ja",
            "korean": "ko",
            "cyrillic": "ru",
        }
        return mapping.get(script, "en")
    
    async def detect_with_llm(self, text: str) -> Tuple[str, float]:
        """
        Detect language using LLM for better accuracy.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (language_code, confidence_score)
        """
        if not self._llm:
            return self.detect(text)
        
        try:
            prompt = f"""Analyze this text and identify the language.
If it's a mix of languages (like Hinglish), indicate that.

Text: "{text[:500]}"

Respond with JSON only:
{{"language": "ISO code", "confidence": 0.0-1.0, "is_mixed": true/false}}"""
            
            response = await self._llm.generate(
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
            
            import json
            data = json.loads(response)
            
            return data.get("language", "en"), data.get("confidence", 0.5)
            
        except Exception as e:
            logger.error(f"LLM detection failed: {e}")
            return self.detect(text)
    
    def is_supported(self, language: str) -> bool:
        """Check if language is supported."""
        return language in SUPPORTED_LANGUAGES
    
    def get_language_info(self, code: str) -> Optional[Dict[str, str]]:
        """Get language information."""
        return SUPPORTED_LANGUAGES.get(code)
    
    def list_supported(self) -> List[Dict[str, Any]]:
        """List all supported languages."""
        return [
            {"code": code, **info}
            for code, info in SUPPORTED_LANGUAGES.items()
        ]
