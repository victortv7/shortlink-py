from fastapi import FastAPI
from .routes import router as url_router
from .core.config import settings, EnvironmentOption

docs_url = None if settings.ENVIRONMENT == EnvironmentOption.PRODUCTION else "/docs"
redoc_url = None if settings.ENVIRONMENT == EnvironmentOption.PRODUCTION else "/redoc"

app = FastAPI(docs_url=docs_url, redoc_url=redoc_url)

app.include_router(url_router)