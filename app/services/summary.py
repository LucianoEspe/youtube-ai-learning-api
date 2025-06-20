import logging
from app.services.youtube import get_transcript_from_youtube
from app.services.openai import async_client
from app.utils.exceptions import APIException, TranscriptException
import os
from app.services.redis_client import redis_client


async def build_summary_prompt(language: str) -> str:
    """Build the prompt for summary generation."""
    base_prompt = os.getenv("SUMMARY_PROMPT") or ""
    prompt_lang = f"Create the summary in {language} (IMPORTANT). " if language else ""
    return f"{prompt_lang}{base_prompt}"


async def generate_summary_from_youtube(youtube_url: str, language: str = "es") -> str:
    """Generate a summary from a YouTube video transcript."""
    logger = logging.getLogger(__name__)
    cache_key = f"summary:{youtube_url}:{language}"
    cached = await redis_client.get(cache_key)
    if cached:
        logger.info("Summary fetched from Redis cache")
        if isinstance(cached, bytes):
            return cached.decode("utf-8")
        return str(cached)
    try:
        logger.info(f"Fetching transcript for URL: {youtube_url}")
        transcript = await get_transcript_from_youtube(youtube_url)
        prompt = await build_summary_prompt(language)
        response = await async_client.responses.create(
            model="gpt-4o-mini",
            instructions=prompt,
            input=transcript
        )
        logger.info(f"Summary generated for URL: {youtube_url}")
        await redis_client.setex(cache_key, 60 * 60, response.output_text)  # 1 hora
        return response.output_text
    except TranscriptException as e:
        logger.error(f"TranscriptException: {str(e)}")
        raise APIException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate summary: {str(e)}")
        raise APIException(status_code=500, detail="An unexpected error occurred while generating the summary")
