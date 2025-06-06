from fastapi import APIRouter, Query, Depends
from app.schemas import SummaryResponse
from app.services.summary_service import generate_summary_from_youtube
from app.security.api_key import validate_api_key
from app.utils.youtube_validators import validate_youtube_url

router = APIRouter(prefix="/summary", tags=["Summary"], dependencies=[Depends(validate_api_key)])

def get_summary_response(youtube_url: str, language: str) -> SummaryResponse:
    summary = generate_summary_from_youtube(youtube_url, language=language)
    return SummaryResponse(summary=summary)

@router.get(
    "/",
    response_model=SummaryResponse,
    summary="Generate a summary from a YouTube video transcript",
    description="Returns a summary generated from the transcript of the provided YouTube video."
)
def generate_summary(
    youtube_url: str = Query(..., description="YouTube video URL"),
    language: str = Query("en", description="Language for the OpenAI response (e.g., 'en', 'es')", pattern="^[a-z]{2}$")
):
    youtube_url = validate_youtube_url(youtube_url)
    return get_summary_response(youtube_url, language)
