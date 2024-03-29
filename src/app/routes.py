from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from .core.db import async_get_db
from .schemas import CreateLinkRequest, CreateLinkResponse, LinkStatsResponse
from .services import create_short_link, get_long_url, get_link_stats, increment_access_count

router = APIRouter()

@router.post("/create", response_model=CreateLinkResponse)
async def create_short_link_endpoint(request: CreateLinkRequest, db: AsyncSession = Depends(async_get_db)):
    try:
        short_link = await create_short_link(db, str(request.long_url))
        return CreateLinkResponse(short_link=short_link)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your request: {str(e)}"
        )


@router.get("/{short_link}", response_class=RedirectResponse)
async def redirect_to_long_url(short_link: str, db: AsyncSession = Depends(async_get_db)):
    try:
        long_url = await get_long_url(db, short_link)
        await increment_access_count(db, short_link)
        return RedirectResponse(url=long_url)
    # TODO: Handle the case where the short link is not found
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short link not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while processing your request: {str(e)}")


@router.get("/stats/{short_link}", response_model=LinkStatsResponse)
async def get_stats(short_link: str, db: AsyncSession = Depends(async_get_db)):
    try:
        stats = await get_link_stats(db, short_link)
        return stats
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short link not found")