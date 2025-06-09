import logging
from fastapi import APIRouter, Query, Depends, BackgroundTasks
from app.schemas.summary import SummaryResponse
from app.services.summary import generate_summary_from_youtube
from app.security.auth import validate_api_key
from app.utils.validators import validate_youtube_url, validate_language
from app.utils.exceptions import APIException

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/summary",
    tags=["Summary"],
    dependencies=[Depends(validate_api_key)]
)

@router.get(
    "/",
    response_model=SummaryResponse,
    summary="Generate a summary from a YouTube video transcript",
    description="Returns a summary generated from the transcript of the provided YouTube video.",
    responses={
        200: {"description": "Summary generated successfully"},
        400: {"description": "Invalid input parameters"},
        422: {"description": "Invalid YouTube URL"},
        503: {"description": "External service unavailable"},
    }
)
async def generate_summary(
    background_tasks: BackgroundTasks,
    youtube_url: str = Query(
        ...,
        description="YouTube video URL",
        example="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    ),
    language: str = Query(
        "en",
        description="Language code for the summary (e.g., 'en', 'es', 'fr')",
        pattern="^[a-z]{2}$",
        example="en"
    )
):
    """Endpoint to generate a summary from a YouTube video transcript."""
    try:
        validated_url = validate_youtube_url(youtube_url)
        validated_language = validate_language(language)
        logger.info(f"Summary request: URL={validated_url}, Language={validated_language}")
        summary = await generate_summary_from_youtube(validated_url, validated_language)
        background_tasks.add_task(
            logger.info,
            f"Summary generated successfully for URL: {validated_url}"
        )
        return SummaryResponse(summary=summary)
    except APIException as e:
        logger.error(f"APIException: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in summary generation: {str(e)}")
        raise APIException(
            status_code=500,
            detail="An unexpected error occurred while generating the summary"
        )
