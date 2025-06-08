from pydantic import BaseModel, field_validator
from urllib.parse import urlparse

class QuizRequest(BaseModel):
    youtube_url: str

    @field_validator("youtube_url")
    def ensure_valid_youtube_url(cls, v):
        if not v.startswith(("http://", "https://")):
            v = "https://" + v
        parsed = urlparse(v)
        if "youtube.com" not in parsed.netloc and "youtu.be" not in parsed.netloc:
            raise ValueError("Debe ser una URL válida de YouTube.")
        return v

class QuizAnswer(BaseModel):
    answer: str
    is_correct: bool = False

class QuizQuestion(BaseModel):
    order: int
    question: str
    type: str
    answers: list[QuizAnswer]

class QuizResponse(BaseModel):
    quiz: list[QuizQuestion]
