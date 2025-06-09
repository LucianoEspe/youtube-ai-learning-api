import logging
from fastapi import APIRouter, Query, Depends, BackgroundTasks
from app.schemas.quiz import QuizResponse
from app.services.quiz import generate_quiz_from_youtube
from app.security.auth import validate_api_key
from app.utils.validators import validate_youtube_url, validate_language
from app.utils.exceptions import APIException

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/quiz",
    tags=["Quiz"],
    dependencies=[Depends(validate_api_key)]
)

@router.get(
    "/",
    response_model=QuizResponse,
    summary="Generate a quiz from a YouTube video transcript",
    description="Returns a quiz with questions and answers generated from the transcript of the provided YouTube video.",
    responses={
        200: {"description": "Quiz generated successfully"},
        400: {"description": "Invalid input parameters"},
        422: {"description": "Invalid YouTube URL"},
        503: {"description": "External service unavailable"},
    }
)
async def generate_quiz(
    background_tasks: BackgroundTasks,
    youtube_url: str = Query(
        ...,
        description="YouTube video URL",
        example="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    ),
    language: str = Query(
        "en",
        description="Language code for the quiz (e.g., 'en', 'es', 'fr')",
        pattern="^[a-z]{2}$",
        example="en"
    ),
    num_questions: int = Query(
        5,
        description="Number of questions to generate",
        example=5
    )
):
    """Endpoint to generate a quiz from a YouTube video transcript."""
    try:
        validated_url = validate_youtube_url(youtube_url)
        validated_language = validate_language(language)
        logger.info(
            f"Quiz request: URL={validated_url}, Language={validated_language}, "
            f"Questions={num_questions}"
        )
        quiz_questions = await generate_quiz_from_youtube(
            validated_url,
            validated_language,
            num_questions
        )
        background_tasks.add_task(
            logger.info,
            f"Quiz generated successfully for URL: {validated_url} "
            f"with {len(quiz_questions)} questions"
        )
        return QuizResponse(quiz=quiz_questions)
    except APIException as e:
        logger.error(f"APIException: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in quiz generation: {str(e)}")
        raise APIException(
            status_code=500,
            detail="An unexpected error occurred while generating the quiz"
        )
