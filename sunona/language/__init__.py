"""
Sunona Voice AI - Language Package

Multi-language support with detection, translation, and localized prompts.
"""

from sunona.language.detector import LanguageDetector
from sunona.language.translator import Translator
from sunona.language.prompts import LocalizedPrompts

__all__ = [
    "LanguageDetector",
    "Translator",
    "LocalizedPrompts",
]
