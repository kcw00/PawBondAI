"""
Language detection service using Vertex AI Gemini
Provides fast, accurate language detection for multilingual content
"""
from typing import Optional
from app.core.logger import setup_logger

logger = setup_logger(__name__)


async def detect_language(text: str) -> str:
    """
    Detect the language of the given text.
    Uses simple heuristics for common languages to avoid API calls.
    Falls back to 'en' (English) if detection fails.
    
    Args:
        text: The text to detect language for
        
    Returns:
        Language code (e.g., 'en', 'ko', 'es', 'zh', 'ja')
    """
    if not text or len(text.strip()) < 5:
        return 'en'
    
    text_sample = text[:500].strip()
    
    # Simple character-based detection for Asian languages
    korean_chars = sum(1 for c in text_sample if '\uac00' <= c <= '\ud7a3')
    chinese_chars = sum(1 for c in text_sample if '\u4e00' <= c <= '\u9fff')
    japanese_hiragana = sum(1 for c in text_sample if '\u3040' <= c <= '\u309f')
    japanese_katakana = sum(1 for c in text_sample if '\u30a0' <= c <= '\u30ff')
    
    total_chars = len(text_sample)
    
    # If >30% of characters are from a specific script, classify as that language
    if korean_chars / total_chars > 0.3:
        logger.info(f"Detected Korean ({korean_chars}/{total_chars} Korean chars)")
        return 'ko'
    elif chinese_chars / total_chars > 0.3:
        logger.info(f"Detected Chinese ({chinese_chars}/{total_chars} Chinese chars)")
        return 'zh'
    elif (japanese_hiragana + japanese_katakana) / total_chars > 0.2:
        logger.info(f"Detected Japanese ({japanese_hiragana + japanese_katakana}/{total_chars} Japanese chars)")
        return 'ja'
    
    # Check for Spanish indicators
    spanish_words = ['el', 'la', 'de', 'que', 'y', 'en', 'es', 'por', 'para', 'con', 'una', 'un']
    words_lower = text_sample.lower().split()
    spanish_count = sum(1 for word in words_lower if word in spanish_words)
    if spanish_count >= 3:
        logger.info(f"Detected Spanish ({spanish_count} Spanish indicator words)")
        return 'es'
    
    # Check for French indicators
    french_words = ['le', 'la', 'de', 'et', 'un', 'une', 'est', 'dans', 'pour', 'avec']
    french_count = sum(1 for word in words_lower if word in french_words)
    if french_count >= 3:
        logger.info(f"Detected French ({french_count} French indicator words)")
        return 'fr'
    
    # Default to English
    logger.info("Detected English (default)")
    return 'en'


def get_language_name(code: str) -> str:
    """Get human-readable language name from code"""
    language_map = {
        'en': 'English',
        'ko': 'Korean',
        'es': 'Spanish',
        'zh': 'Chinese',
        'ja': 'Japanese',
        'fr': 'French',
        'de': 'German',
        'pt': 'Portuguese',
        'it': 'Italian',
        'ru': 'Russian',
        'ar': 'Arabic',
        'hi': 'Hindi',
    }
    return language_map.get(code, code.upper())
