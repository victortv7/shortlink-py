from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from redis.asyncio import Redis
from .core.db import async_get_db
from .core.redis import async_get_redis
from .schemas import CreateLinkRequest, CreateLinkResponse, LinkStatsResponse
from .services import create_short_link, get_long_url, get_link_stats
from .core.logger import get_logger

router = APIRouter(tags=["Endpoints"])
logger = get_logger(__name__)


@router.get("/health")
async def health_check():
    logger.debug("Health check requested")
    return {"status": "ok"}


@router.post(
    "/create", response_model=CreateLinkResponse, status_code=status.HTTP_201_CREATED
)
async def create_short_link_endpoint(
    request: CreateLinkRequest,
    db: AsyncSession = Depends(async_get_db),
    redis: Redis = Depends(async_get_redis),
):
    try:
        short_link = await create_short_link(str(request.long_url), db, redis)
        logger.info(f"Short link created: {short_link} for URL {request.long_url}")
        return CreateLinkResponse(short_link=short_link)
    except Exception as e:
        logger.error(
            f"Internal server error on creating short link: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request.",
        )


@router.get("/{short_link}", response_class=RedirectResponse)
async def redirect_to_long_url(
    short_link: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(async_get_db),
    redis: Redis = Depends(async_get_redis),
):
    try:
        long_url = await get_long_url(short_link, db, redis, background_tasks)
        logger.debug(f"Redirecting short link {short_link} to {long_url}")
        return RedirectResponse(url=long_url)
    except NoResultFound:
        logger.warning(f"Short link not found: {short_link}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Short link not found"
        )
    except Exception as e:
        logger.error(
            f"Internal server error on redirecting short link {short_link}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request.",
        )


@router.get("/stats/{short_link}", response_model=LinkStatsResponse)
async def get_stats(short_link: str, db: AsyncSession = Depends(async_get_db)):
    try:
        stats = await get_link_stats(short_link, db)
        logger.info(f"Stats requested for short link {short_link}")
        return stats
    except NoResultFound:
        logger.warning(f"Stats not found for short link: {short_link}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Short link not found"
        )
    except Exception as e:
        logger.error(
            f"Internal server error on getting stats for short link {short_link}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request.",
        )
