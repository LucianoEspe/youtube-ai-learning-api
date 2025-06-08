from pydantic import BaseModel, field_validator
from urllib.parse import urlparse

class SummaryRequest(BaseModel):
    youtube_url: str
    language: str = "es"

    @field_validator("youtube_url")
    def ensure_valid_youtube_url(cls, v):
        if not v.startswith(("http://", "https://")):
            v = "https://" + v
        parsed = urlparse(v)
        if "youtube.com" not in parsed.netloc and "youtu.be" not in parsed.netloc:
            raise ValueError("Debe ser una URL válida de YouTube.")
        return v

class SummaryResponse(BaseModel):
    summary: str
