# Servicio para lógica de cuestionario con OpenAI y YouTube
from app.schemas import QuizQuestion, QuizAnswer
from app.services.youtube_service import get_transcript_from_youtube
from app.services.openai_client import client
from fastapi import HTTPException
import os
import json
import re

def build_quiz_prompt(language: str, num_questions: int) -> str:
    base_prompt = os.getenv("QUIZ_PROMPT") or ""
    prompt_lang = f"Create the quiz in {language} (IMPORTANT). " if language else ""
    return f"{prompt_lang}{base_prompt} Create {num_questions} questions."

def parse_quiz_response(response_text: str) -> list[QuizQuestion]:
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
    try:
        transcript = get_transcript_from_youtube(youtube_url)
        prompt = build_quiz_prompt(language, num_questions)
        response = client.responses.create(
            model="gpt-4o-mini",
            instructions=prompt,
            input=transcript
        )
        return parse_quiz_response(response.output_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(e)}")
