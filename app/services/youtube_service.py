# Servicio para obtener la transcripción de un video de YouTube
from urllib.parse import urlparse, parse_qs, quote
import http.client
import json
import os


def extract_youtube_id(youtube_url: str) -> str:
    """Extrae el ID del video de una URL de YouTube."""
    parsed = urlparse(str(youtube_url))
    if parsed.hostname in ["youtu.be"]:
        return parsed.path[1:]
    if parsed.hostname in ["www.youtube.com", "youtube.com"]:
        if parsed.path == "/watch":
            return parse_qs(parsed.query)["v"][0]
        if parsed.path.startswith("/embed/"):
            return parsed.path.split("/")[2]
        if parsed.path.startswith("/v/"):
            return parsed.path.split("/")[2]
    raise ValueError("Invalid YouTube URL")

def build_transcript_endpoint(video_url: str, language: str = "en") -> str:
    """Construye el endpoint para la API de transcripción."""
    encoded_url = quote(video_url, safe='')
    lang = language or "es"
    return f"/api/transcript-with-url?url={encoded_url}&flat_text=true&lang={lang}"

def fetch_transcript_from_api(endpoint: str) -> str:
    conn = http.client.HTTPSConnection("youtube-transcript3.p.rapidapi.com")
    rapidapi_key = os.getenv("RAPIDAPI_KEY")
    if not rapidapi_key:
        raise RuntimeError("RAPIDAPI_KEY environment variable not set.")
    headers = {
        'x-rapidapi-key': rapidapi_key,
        'x-rapidapi-host': "youtube-transcript3.p.rapidapi.com"
    }
    conn.request("GET", endpoint, headers=headers)
    res = conn.getresponse()
    data = res.read()
    try:
        result = json.loads(data.decode("utf-8"))
        if 'transcript' in result:
            return result['transcript']
        else:
            raise RuntimeError(f"Unexpected API response: {result}")
    except Exception as e:
        raise RuntimeError(f"Could not fetch YouTube transcript: {e}")

def get_transcript_from_youtube(youtube_url: str, language: str = "es") -> str:
    """Devuelve la transcripción del video de YouTube usando la API de RapidAPI."""
    video_id = extract_youtube_id(youtube_url)
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    endpoint = build_transcript_endpoint(video_url, language)
    return fetch_transcript_from_api(endpoint)
