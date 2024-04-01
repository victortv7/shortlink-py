import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.exc import NoResultFound
from src.app.services import (
    create_short_link,
    get_long_url,
    get_link_stats,
    increment_access_count,
)
from src.app.models import URL
from src.app.base62 import encode, decode


@pytest.mark.asyncio
async def test_create_short_link():
    long_url = "https://example.com"
    current_db_url_id = 1000

    redis_mock = AsyncMock()
    redis_mock.set = AsyncMock()

    db_mock = AsyncMock()
    db_mock.add = AsyncMock()
    db_mock.commit = AsyncMock()

    async def custom_refresh(url_obj):
        url_obj.id = current_db_url_id

    # Simulate the behavior of returning the URL object from the DB with a new ID
    db_mock.refresh = AsyncMock(side_effect=custom_refresh)

    # Execute the function under test
    actual_short_link = await create_short_link(long_url, db_mock, redis_mock)

    expected_short_link = encode(current_db_url_id)

    # Assertions
    assert actual_short_link == expected_short_link
    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()
    redis_mock.set.assert_called_with(f"shortlink:{expected_short_link}", long_url)


@pytest.mark.asyncio
async def test_get_long_url_found_in_redis():
    short_link = "short123"
    long_url = "https://example.com"

    db_mock = AsyncMock()
    redis_mock = AsyncMock()
    redis_mock.get = AsyncMock(return_value=long_url)

    result = await get_long_url(short_link, db_mock, redis_mock)

    assert result == long_url
    redis_mock.get.assert_awaited_with(f"shortlink:{short_link}")
    db_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_long_url_found_in_db():
    short_link = "short123"
    id = decode(short_link)
    expected_long_url = "https://example.com"

    redis_mock = AsyncMock()
    redis_mock.get = AsyncMock(return_value=None)

    db_mock = AsyncMock()
    url_obj = URL(id=id, long_url=expected_long_url)
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = url_obj
    db_mock.execute = AsyncMock(return_value=mock_result)
    db_mock.commit = AsyncMock()

    actual_long_url = await get_long_url(short_link, db_mock, redis_mock)

    assert actual_long_url == expected_long_url
    db_mock.execute.assert_awaited_once()
    redis_mock.set.assert_awaited_with(f"shortlink:{short_link}", expected_long_url)


@pytest.mark.asyncio
async def test_get_long_url_not_found():
    db_mock = AsyncMock()
    redis_mock = AsyncMock()
    short_link = "nonexistent123"

    redis_mock.get = AsyncMock(return_value=None)
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    db_mock.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(NoResultFound):
        await get_long_url(short_link, db_mock, redis_mock)


@pytest.mark.asyncio
async def test_get_link_stats_success():
    long_url = "https://example.com"
    short_link = "abc123"
    access_count = 100
    id = decode(short_link)

    expected_stats = {
        "long_url": long_url,
        "short_link": short_link,
        "access_count": access_count,
    }

    db_mock = AsyncMock()
    url_obj = URL(id=id, long_url=long_url, access_count=access_count)
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = url_obj
    db_mock.execute = AsyncMock(return_value=mock_result)

    actual_stats = await get_link_stats(short_link, db_mock)

    assert actual_stats == expected_stats
    db_mock.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_link_stats_not_found():
    short_link = "nonexistent123"
    db_mock = AsyncMock()
    redis_mock = AsyncMock()
    redis_mock.get = AsyncMock(return_value=None)
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    db_mock.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(NoResultFound):
        await get_link_stats(short_link, db_mock)


@pytest.mark.asyncio
async def test_increment_access_count():
    db_mock = AsyncMock()
    short_link = "abc123"
    url_obj = URL(long_url="https://example.com", access_count=10)

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = url_obj
    db_mock.execute = AsyncMock(return_value=mock_result)
    db_mock.commit = AsyncMock()

    await increment_access_count(short_link, db_mock)

    assert url_obj.access_count == 11
    db_mock.commit.assert_awaited()
