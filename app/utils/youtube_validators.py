from fastapi import HTTPException
from urllib.parse import urlparse

def validate_youtube_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    if "youtube.com" not in parsed.netloc and "youtu.be" not in parsed.netloc:
        raise HTTPException(status_code=422, detail="You must provide a valid YouTube URL.")
    return url
