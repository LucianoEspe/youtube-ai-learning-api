import logging
from app.services.youtube import get_transcript_from_youtube
from app.services.openai import client
from app.utils.exceptions import APIException, TranscriptException
import os


def build_summary_prompt(language: str) -> str:
    """Build the prompt for summary generation."""
    base_prompt = os.getenv("SUMMARY_PROMPT") or ""
    prompt_lang = f"Create the summary in {language} (IMPORTANT). " if language else ""
    return f"{prompt_lang}{base_prompt}"


def generate_summary_from_youtube(youtube_url: str, language: str = "es") -> str:
    """Generate a summary from a YouTube video transcript."""
    logger = logging.getLogger(__name__)
    try:
        logger.info(f"Fetching transcript for URL: {youtube_url}")
        transcript = get_transcript_from_youtube(youtube_url)
        prompt = build_summary_prompt(language)
        response = client.responses.create(
            model="gpt-4o-mini",
            instructions=prompt,
            input=transcript
        )
        logger.info(f"Summary generated for URL: {youtube_url}")
        return response.output_text
    except TranscriptException as e:
        logger.error(f"TranscriptException: {str(e)}")
        raise APIException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate summary: {str(e)}")
        raise APIException(status_code=500, detail="An unexpected error occurred while generating the summary")
