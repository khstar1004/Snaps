import pytest
from app.services.snaps import MetaBusinessService
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_get_business_account_success():
    service = MetaBusinessService()
    access_token = "valid_token"
    expected_response = {"id": "12345", "name": "Test Business", "created_time": "2020-01-01T00:00:00Z"}

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json = AsyncMock(return_value={"data": [expected_response]})
        result = await service.get_business_account(access_token)
        assert result == expected_response
        mock_get.assert_called_once()

@pytest.mark.asyncio
async def test_get_business_account_no_business():
    service = MetaBusinessService()
    access_token = "valid_token"

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json = AsyncMock(return_value={"data": []})
        with pytest.raises(HTTPException) as exc_info:
            await service.get_business_account(access_token)
        assert exc_info.value.status_code == 404
        mock_get.assert_called_once()

@pytest.mark.asyncio
async def test_get_business_account_http_error():
    service = MetaBusinessService()
    access_token = "invalid_token"

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.HTTPError("Connection error")
        with pytest.raises(HTTPException) as exc_info:
            await service.get_business_account(access_token)
        assert exc_info.value.status_code == 502
        mock_get.assert_called_once()

@pytest.mark.asyncio
async def test_list_pages_success():
    service = MetaBusinessService()
    service.access_token = "valid_token"
    expected_pages = [
        {"id": "page1", "name": "Page One", "permalink": "https://facebook.com/page1"},
        {"id": "page2", "name": "Page Two", "permalink": "https://facebook.com/page2"}
    ]

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json = AsyncMock(return_value={"data": expected_pages})
        result = await service.list_pages()
        assert result == expected_pages
        mock_get.assert_called_once()

@pytest.mark.asyncio
async def test_get_page_insights_success():
    service = MetaBusinessService()
    service.access_token = "valid_token"
    page_id = "page1"
    metrics = ["impressions", "reach"]
    expected_insights = [
        {"name": "impressions", "period": "day", "values": [{"value": 1000, "end_time": "2020-01-01T00:00:00Z"}]},
        {"name": "reach", "period": "day", "values": [{"value": 800, "end_time": "2020-01-01T00:00:00Z"}]}
    ]

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json = AsyncMock(return_value={"data": expected_insights})
        result = await service.get_page_insights(page_id, metrics)
        assert result == expected_insights
        mock_get.assert_called_once() 