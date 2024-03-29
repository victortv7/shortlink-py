import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from unittest.mock import patch, MagicMock, ANY
from src.app.main import app
from src.app.schemas import CreateLinkResponse, LinkStatsResponse

@pytest.mark.asyncio
async def test_create_short_link_endpoint_success():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        test_long_url = "https://example.com"
        test_short_link = "abc123"
        
        with patch("src.app.routes.create_short_link", return_value=test_short_link) as mock_service:
            response = await ac.post("/create", json={"long_url": test_long_url})
            
            assert response.status_code == 200
            assert response.json() == {"short_link": test_short_link}
            mock_service.assert_awaited_once()

@pytest.mark.asyncio
async def test_redirect_to_long_url_found():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        test_short_link = "abc123"
        test_long_url = "https://example.com"
        
        with patch("src.app.routes.get_long_url", return_value=test_long_url) as mock_get_long_url, \
            patch("src.app.routes.increment_access_count") as mock_increment_access_count:
            response = await ac.get(f"/{test_short_link}")
            print(f"Response text: {response.text}")
            assert response.status_code == 307
            assert response.headers["Location"] == test_long_url
            mock_get_long_url.assert_awaited_once_with(test_short_link, ANY, ANY)
            mock_increment_access_count.assert_awaited_once_with(test_short_link, ANY)

@pytest.mark.asyncio
async def test_get_link_stats_success():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        test_short_link = "abc123"
        mock_response = {"long_url": "https://example.com", "short_link": test_short_link, "access_count": 1}
        
        with patch("src.app.routes.get_link_stats", return_value=mock_response) as mock_service:
            response = await ac.get(f"/stats/{test_short_link}")
            
            assert response.status_code == 200
            assert response.json() == mock_response
            mock_service.assert_awaited_once_with(test_short_link, ANY)
