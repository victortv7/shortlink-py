from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from .models import URL
from .base62 import encode, decode

REDIS_SHORTLINK_PREFIX = "shortlink:"

async def create_short_link(long_url: str, db: AsyncSession, redis: Redis) -> str:
    new_url = URL(long_url=long_url, access_count=0)
    db.add(new_url)
    await db.commit()
    await db.refresh(new_url)
    # Get the ID of the new row of DB and encode it to generate the short link
    short_link = encode(new_url.id)

    await redis.set(f"{REDIS_SHORTLINK_PREFIX}{short_link}", long_url)

    return short_link


async def get_long_url(short_link: str, db: AsyncSession, redis: Redis) -> str:
    # Try to find the short link in Redis
    long_url = await redis.get(f"{REDIS_SHORTLINK_PREFIX}{short_link}")
    if long_url:
        return long_url
    
    # If not found in Redis, query the database
    id = decode(short_link)
    query = select(URL).where(URL.id == id)
    result = await db.execute(query)
    url_obj = result.scalars().first()

    if not url_obj:
        raise NoResultFound(f"No URL found for short link: {short_link}")

    await redis.set(f"{REDIS_SHORTLINK_PREFIX}{short_link}", url_obj.long_url)

    return url_obj.long_url

async def get_link_stats(short_link: str, db: AsyncSession) -> dict:
    id = decode(short_link)
    query = select(URL).where(URL.id == id)
    result = await db.execute(query)
    url_obj = result.scalars().first()

    if not url_obj:
        raise NoResultFound(f"No stats found for short link: {short_link}")

    return {
        "long_url": url_obj.long_url,
        "short_link": short_link,
        "access_count": url_obj.access_count,
    }

async def increment_access_count(short_link: str, db: AsyncSession):
    id = decode(short_link)
    query = select(URL).where(URL.id == id)
    result = await db.execute(query)
    url_obj = result.scalars().first()

    if url_obj:
        url_obj.access_count += 1
        await db.commit()