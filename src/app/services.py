from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from .models import URL
from .base62 import encode, decode

async def create_short_link(db: AsyncSession, long_url: str) -> str:
    new_url = URL(long_url=long_url, access_count=0)
    db.add(new_url)
    await db.commit()

    await db.refresh(new_url)

    short_link = encode(new_url.id)
    return short_link


async def get_long_url(db: AsyncSession, short_link: str) -> str:
    id = decode(short_link)
    query = select(URL).where(URL.id == id) #.limit(1)
    result = await db.execute(query)
    url_obj = result.scalars().first()

    if not url_obj:
        raise NoResultFound(f"No URL found for short link: {short_link}")

    # Increment access count
    # url_obj.access_count += 1
    # await db.commit()

    return url_obj.long_url

async def get_link_stats(db: AsyncSession, short_link: str) -> dict:
    query = select(URL).where(URL.short_link == short_link)
    result = await db.execute(query)
    url_obj = result.scalars().first()

    if not url_obj:
        raise NoResultFound(f"No stats found for short link: {short_link}")

    # No need to increment access count here as we're just fetching stats
    return {
        "long_url": url_obj.long_url,
        "short_link": url_obj.short_link,
        "access_count": url_obj.access_count,
    }

async def increment_access_count(db: AsyncSession, short_link: str):
    id = decode(short_link)
    query = select(URL).where(URL.id == id)
    result = await db.execute(query)
    url_obj = result.scalars().first()

    if url_obj:
        url_obj.access_count += 1
        await db.commit()