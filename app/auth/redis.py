# app/auth/redis.py
import redis.asyncio as redis
from app.core.config import get_settings

settings = get_settings()

_redis_client = None

async def get_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL or "redis://localhost:6379",
            decode_responses=True
        )
    return _redis_client

async def add_to_blacklist(jti: str, exp: int):
    """Add a token's JTI to the blacklist"""
    r = await get_redis()
    await r.set(f"blacklist:{jti}", "1", ex=exp)

async def is_blacklisted(jti: str) -> bool:
    """Check if a token's JTI is blacklisted"""
    r = await get_redis()
    return await r.exists(f"blacklist:{jti}") > 0