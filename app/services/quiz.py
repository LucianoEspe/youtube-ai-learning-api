import logging
from app.schemas.quiz import QuizQuestion, QuizAnswer
from app.services.youtube import get_transcript_from_youtube
from app.services.openai import client
from app.utils.exceptions import APIException, TranscriptException
import os
import json
import re
from app.services.redis_client import redis_client

def build_quiz_prompt(language: str, num_questions: int) -> str:
    """Build the prompt for quiz generation."""
    base_prompt = os.getenv("QUIZ_PROMPT") or ""
    prompt_lang = f"Create the quiz in {language} (IMPORTANT). " if language else ""
    return f"{prompt_lang}{base_prompt} Create {num_questions} questions."

def parse_quiz_response(response_text: str) -> list[QuizQuestion]:
    """Parse the quiz response from the OpenAI API."""
    raw = response_text.strip()
    raw = re.sub(r'^```json|^```|```$', '', raw, flags=re.MULTILINE).strip()
    quiz_data = json.loads(raw)
    if isinstance(quiz_data, dict) and 'questions' in quiz_data:
        quiz_data = quiz_data['questions']
    return [
        QuizQuestion(
            order=q.get('order'),
            question=q.get('question'),
            type=q.get('type'),
            answers=[QuizAnswer(**a) for a in q.get('answers', [])]
        ) for q in quiz_data
    ]

def generate_quiz_from_youtube(youtube_url: str, language: str = "en", num_questions: int = 5) -> list[QuizQuestion]:
    """Generate a quiz from a YouTube video transcript."""
    logger = logging.getLogger(__name__)
    cache_key = f"quiz:{youtube_url}:{language}:{num_questions}"
    cached = redis_client.get(cache_key)
    if cached:
        logger.info("Quiz fetched from Redis cache")
        quiz_data = json.loads(cached.decode("utf-8") if isinstance(cached, bytes) else str(cached))
        return [QuizQuestion(**q) for q in quiz_data]
    try:
        logger.info(f"Fetching transcript for URL: {youtube_url}")
        transcript = get_transcript_from_youtube(youtube_url)
        prompt = build_quiz_prompt(language, num_questions)
        response = client.responses.create(
            model="gpt-4o-mini",
            instructions=prompt,
            input=transcript
        )
        logger.info(f"Quiz generated for URL: {youtube_url} with {num_questions} questions")
        quiz_questions = parse_quiz_response(response.output_text)
        redis_client.setex(cache_key, 60 * 60, json.dumps([q.model_dump() for q in quiz_questions]))
        return quiz_questions
    except TranscriptException as e:
        logger.error(f"TranscriptException: {str(e)}")
        raise APIException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate quiz: {str(e)}")
        raise APIException(status_code=500, detail="An unexpected error occurred while generating the quiz")
