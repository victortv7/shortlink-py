from fastapi import FastAPI
from .routes import router as url_router
from .core.config import settings, EnvironmentOption


def create_app() -> FastAPI:
    docs_url = None if settings.ENVIRONMENT == EnvironmentOption.PRODUCTION else "/docs"
    redoc_url = (
        None if settings.ENVIRONMENT == EnvironmentOption.PRODUCTION else "/redoc"
    )

    app = FastAPI(
        title="ShortLink-py",
        description="A URL shortening service built with FastAPI",
        version="0.1.0",
        docs_url=docs_url,
        redoc_url=redoc_url,
    )

    app.include_router(url_router)

    return app


app = create_app()
