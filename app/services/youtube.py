import logging
from urllib.parse import urlparse, parse_qs, quote
import os
from app.utils.exceptions import TranscriptException
from app.services.redis_client import redis_client
import httpx


def extract_youtube_id(youtube_url: str) -> str:
    """Extract the video ID from a YouTube URL. Raises TranscriptException if invalid."""
    parsed = urlparse(str(youtube_url))
    if parsed.hostname in ["youtu.be"]:
        if parsed.path and len(parsed.path) > 1 and not parsed.query:
            return parsed.path[1:]
        else:
            raise TranscriptException("Invalid YouTube short URL format")
    if parsed.hostname in ["www.youtube.com", "youtube.com"]:
        if parsed.path == "/watch":
            if "v" in parse_qs(parsed.query):
                return parse_qs(parsed.query)["v"][0]
            else:
                raise TranscriptException("Missing video ID in YouTube URL")
        if parsed.path.startswith("/embed/"):
            if len(parsed.path.split("/")) >= 3:
                return parsed.path.split("/")[2]
            else:
                raise TranscriptException("Invalid YouTube embed URL format")
        if parsed.path.startswith("/v/"):
            if len(parsed.path.split("/")) >= 3:
                return parsed.path.split("/")[2]
            else:
                raise TranscriptException("Invalid YouTube embed URL format")
    raise TranscriptException("Must be a valid YouTube URL")

def build_transcript_endpoint(video_url: str, language: str = "en") -> str:
    """Build the endpoint URL for the transcript API request."""
    encoded_url = quote(video_url, safe='')
    lang = language or "en"
    return f"/api/transcript-with-url?url={encoded_url}&flat_text=true&lang={lang}"

async def fetch_transcript_from_api(endpoint: str) -> str:
    """Fetch the transcript from the external API. Raises TranscriptException on error."""
    logger = logging.getLogger(__name__)
    cache_key = f"transcript:{endpoint}"
    cached = await redis_client.get(cache_key)
    if cached:
        logger.info("Transcript fetched from Redis cache")
        if isinstance(cached, bytes):
            return cached.decode("utf-8")
        return str(cached)
    rapidapi_key = os.getenv("RAPIDAPI_KEY")
    if not rapidapi_key:
        logger.error("RAPIDAPI_KEY environment variable not set.")
        raise TranscriptException("RAPIDAPI_KEY environment variable not set.")
    headers = {
        'x-rapidapi-key': rapidapi_key,
        'x-rapidapi-host': "youtube-transcript3.p.rapidapi.com"
    }
    logger.info(f"Requesting transcript from endpoint: {endpoint}")
    url = f"https://youtube-transcript3.p.rapidapi.com{endpoint}"
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=headers)
            res.raise_for_status()
            result = res.json()
        if 'transcript' in result:
            logger.info("Transcript fetched from API successfully")
            await redis_client.setex(cache_key, 60 * 60, result['transcript'])  # 1 hora
            return result['transcript']
        else:
            logger.error(f"Unexpected API response: {result}")
            raise TranscriptException(f"Unexpected API response: {result}")
    except Exception as e:
        logger.error(f"Could not fetch YouTube transcript: {e}")
        raise TranscriptException(f"Could not fetch YouTube transcript: {e}")

async def get_transcript_from_youtube(youtube_url: str, language: str = "es") -> str:
    """Get the transcript for a YouTube video, given its URL and language."""
    logger = logging.getLogger(__name__)
    try:
        logger.info(f"Extracting video ID from URL: {youtube_url}")
        video_id = extract_youtube_id(youtube_url)
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        endpoint = build_transcript_endpoint(video_url, language)
        transcript = await fetch_transcript_from_api(endpoint)
        logger.info(f"Transcript fetched for URL: {youtube_url}")
        return transcript
    except Exception as e:
        logger.error(f"TranscriptException: Could not get transcript: {str(e)}")
        raise TranscriptException(f"Could not get transcript: {str(e)}")
