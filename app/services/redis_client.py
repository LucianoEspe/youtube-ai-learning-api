import os
import redis

REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    raise ValueError("REDIS_URL environment variable is not set")
redis_client = redis.Redis.from_url(REDIS_URL)
