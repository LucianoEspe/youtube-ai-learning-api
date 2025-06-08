import logging
from urllib.parse import urlparse
from app.utils.exceptions import ValidationException, YouTubeException

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = {
    'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 'ar', 'hi'
}

def validate_youtube_url(url: str) -> str:
    """Validate and normalize a YouTube URL. Raises ValidationException or YouTubeException."""
    if not url or not url.strip():
        raise ValidationException("YouTube URL is required")
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        parsed = urlparse(url)
        valid_domains = ["youtube.com", "www.youtube.com", "youtu.be", "m.youtube.com"]
        if parsed.netloc not in valid_domains:
            raise YouTubeException("Must be a valid YouTube URL")
        if parsed.netloc == "youtu.be":
            if not parsed.path or len(parsed.path) < 2:
                raise YouTubeException("Invalid YouTube short URL format")
        elif "youtube.com" in parsed.netloc:
            if parsed.path == "/watch" and "v=" not in parsed.query:
                raise YouTubeException("Missing video ID in YouTube URL")
            elif parsed.path.startswith("/embed/") and len(parsed.path.split("/")) < 3:
                raise YouTubeException("Invalid YouTube embed URL format")
        logger.debug(f"YouTube URL validated: {url}")
        return url
    except Exception as e:
        if isinstance(e, (ValidationException, YouTubeException)):
            raise
        logger.error(f"URL validation error: {str(e)}")
        raise ValidationException(f"Invalid URL format: {str(e)}")

def validate_language(language: str) -> str:
    """Validate a language code. Returns 'en' if invalid or unsupported."""
    if not language or not language.strip():
        return "en"
    language = language.strip().lower()
    if len(language) != 2:
        raise ValidationException("Language code must be exactly 2 characters")
    if language not in SUPPORTED_LANGUAGES:
        logger.warning(f"Unsupported language code: {language}, using 'en' as fallback")
        return "en"
    return language
