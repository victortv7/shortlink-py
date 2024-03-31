from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, sessionmaker
from .config import settings

async_engine = create_async_engine(settings.POSTGRES_ASYNC_URL, echo=True, future=True)
AsyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession)

class Base(DeclarativeBase, MappedAsDataclass):
    pass

async def async_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
