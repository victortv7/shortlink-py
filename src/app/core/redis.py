from typing import AsyncGenerator
import redis.asyncio as redis
from .config import settings


async def async_get_redis() -> AsyncGenerator[redis.Redis, None]:
    session = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DB,
        decode_responses=True,
    )
    try:
        yield session
    finally:
        await session.aclose()
