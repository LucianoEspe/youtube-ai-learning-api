# Servicio para lógica de resumen con OpenAI y YouTube
from app.services.youtube_service import get_transcript_from_youtube
from app.services.openai_client import client
from fastapi import HTTPException
import os


def build_summary_prompt(language: str) -> str:
    base_prompt = os.getenv("SUMMARY_PROMPT") or ""
    prompt_lang = f"Respond in {language}. " if language else ""
    return f"{prompt_lang}{base_prompt}"


def generate_summary_from_youtube(youtube_url: str, language: str = "es") -> str:
    try:
        transcript = get_transcript_from_youtube(youtube_url)
        prompt = build_summary_prompt(language)
        response = client.responses.create(
            model="gpt-4o-mini",
            instructions=prompt,
            input=transcript
        )
        return response.output_text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")
