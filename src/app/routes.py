from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from redis.asyncio import Redis
from .core.db import async_get_db
from .core.redis import async_get_redis
from .schemas import CreateLinkRequest, CreateLinkResponse, LinkStatsResponse
from .services import create_short_link, get_long_url, get_link_stats, increment_access_count

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.post("/create", response_model=CreateLinkResponse)
async def create_short_link_endpoint(request: CreateLinkRequest, db: AsyncSession = Depends(async_get_db), redis: Redis = Depends(async_get_redis)):
    try:
        short_link = await create_short_link(str(request.long_url), db, redis)
        return CreateLinkResponse(short_link=short_link)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your request: {str(e)}"
        )


@router.get("/{short_link}", response_class=RedirectResponse)
async def redirect_to_long_url(short_link: str, db: AsyncSession = Depends(async_get_db), redis: Redis = Depends(async_get_redis)):
    try:
        long_url = await get_long_url(short_link, db, redis)
        await increment_access_count(short_link, db)
        return RedirectResponse(url=long_url)
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short link not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while processing your request: {str(e)}")


@router.get("/stats/{short_link}", response_model=LinkStatsResponse)
async def get_stats(short_link: str, db: AsyncSession = Depends(async_get_db)):
    try:
        stats = await get_link_stats(short_link, db)
        return stats
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short link not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while processing your request: {str(e)}")
