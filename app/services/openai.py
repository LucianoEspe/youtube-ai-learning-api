import os
from openai import AsyncOpenAI

async_client = AsyncOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)