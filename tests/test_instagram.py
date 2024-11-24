import pytest
from app.services.instagram import InstagramService
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_get_user_profile():
    service = InstagramService(access_token="test_token")
    
    with patch("app.services.instagram.httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "id": "123456",
            "username": "testuser",
            "account_type": "BUSINESS",
            "media_count": 10
        }
        mock_response.raise_for_status = AsyncMock()
        mock_get.return_value = mock_response
        
        profile = await service.get_user_profile()
        assert profile["username"] == "testuser"
        assert profile["account_type"] == "BUSINESS"

@pytest.mark.asyncio
async def test_reply_to_comment():
    service = InstagramService(access_token="test_token")
    comment_id = "comment_123456"
    message = "Thanks for your feedback!"
    
    with patch("app.services.instagram.httpx.AsyncClient.post") as mock_post:
        mock_response = AsyncMock()
        mock_response.json.return_value = {"id": "reply_123456"}
        mock_response.raise_for_status = AsyncMock()
        mock_post.return_value = mock_response
        
        reply = await service.reply_to_comment(comment_id=comment_id, message=message)
        assert reply["id"] == "reply_123456"

@pytest.mark.asyncio
async def test_hide_comment():
    service = InstagramService(access_token="test_token")
    comment_id = "comment_123456"
    hide = True
    
    with patch("app.services.instagram.httpx.AsyncClient.post") as mock_post:
        mock_response = AsyncMock()
        mock_response.json.return_value = {"success": True}
        mock_response.raise_for_status = AsyncMock()
        mock_post.return_value = mock_response
        
        result = await service.hide_or_unhide_comment(comment_id=comment_id, hide=hide)
        assert result == True

@pytest.mark.asyncio
async def test_create_media_post():
    service = InstagramService(access_token="test_token")
    image_url = "https://www.example.com/image.jpg"
    caption = "Check out this image!"
    
    with patch("app.services.instagram.httpx.AsyncClient.post") as mock_post:
        # Mock media creation response
        mock_create_response = AsyncMock()
        mock_create_response.json.return_value = {"id": "media_123456"}
        mock_create_response.raise_for_status = AsyncMock()
        
        # Mock media publish response
        mock_publish_response = AsyncMock()
        mock_publish_response.json.return_value = {"id": "published_media_123456"}
        mock_publish_response.raise_for_status = AsyncMock()
        
        # Configure the side effects
        mock_post.side_effect = [mock_create_response, mock_publish_response]
        
        published_post = await service.create_media_post(image_url=image_url, caption=caption)
        assert published_post["id"] == "published_media_123456"

@pytest.mark.asyncio
async def test_get_media_list():
    service = InstagramService(access_token="test_token")
    
    with patch("app.services.instagram.httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "media_1",
                    "caption": "First post",
                    "media_type": "IMAGE",
                    "media_url": "https://www.example.com/media1.jpg",
                    "permalink": "https://www.instagram.com/p/media1/",
                    "timestamp": "2023-10-17T05:42:03+0000"
                },
                {
                    "id": "media_2",
                    "caption": "Second post",
                    "media_type": "VIDEO",
                    "media_url": "https://www.example.com/media2.mp4",
                    "permalink": "https://www.instagram.com/p/media2/",
                    "timestamp": "2023-10-18T06:30:00+0000"
                }
            ]
        }
        mock_response.raise_for_status = AsyncMock()
        mock_get.return_value = mock_response
        
        media_list = await service.get_media_list(limit=2)
        assert len(media_list) == 2
        assert media_list[0]["id"] == "media_1"
        assert media_list[1]["id"] == "media_2"