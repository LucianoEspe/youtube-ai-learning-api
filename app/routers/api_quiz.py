from fastapi import APIRouter, Query, Depends
from app.schemas import QuizResponse
from app.services.quiz_service import generate_quiz_from_youtube
from app.security.api_key import validate_api_key
from app.utils.youtube_validators import validate_youtube_url

router = APIRouter(prefix="/quiz", tags=["Quiz"], dependencies=[Depends(validate_api_key)])

def get_quiz_response(youtube_url: str, language: str, num_questions: int) -> QuizResponse:
    quiz = generate_quiz_from_youtube(youtube_url, language, num_questions)
    return QuizResponse(quiz=quiz)

@router.post(
    "/",
    response_model=QuizResponse,
    summary="Generate a quiz from a YouTube video transcript",
    description="Returns a quiz with questions and answers generated from the transcript of the provided YouTube video."
)
def generate_quiz(
    youtube_url: str = Query(..., description="YouTube video URL"),
    language: str = Query("en", description="Language for the OpenAI response (e.g., 'en', 'es')", pattern="^[a-z]{2}$"),
    num_questions: int = Query(5, description="Number of questions to generate")
):
    youtube_url = validate_youtube_url(youtube_url)
    return get_quiz_response(youtube_url, language, num_questions)
