import os
from redis import Redis

# Standard local Redis fallback settings
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

def get_redis_connection():
    """Returns a unified Redis client network link instance."""
    # decode_responses=False is required by RQ to handle binary payloads correctly
    return Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=False)
