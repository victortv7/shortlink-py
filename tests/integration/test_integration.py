import httpx
import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from unittest.mock import patch, ANY
from src.app.main import app
from src.app.schemas import CreateLinkResponse, LinkStatsResponse
from sqlalchemy.exc import NoResultFound


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://localhost") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_short_link():
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://localhost") as ac:
        test_long_url = "https://example.com"
        test_short_link = "6laZE"
        
        response = await ac.post("/create", json={"long_url": test_long_url})
        print(response.json())

        assert response.status_code == 200
        assert response.json() == {"short_link": test_short_link}

