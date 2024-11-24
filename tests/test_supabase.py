import pytest
from app.services.supabase import SupabaseClient
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_sign_up_success():
    client = SupabaseClient()
    email = "test@example.com"
    password = "password123"
    username = "testuser"
    expected_user = {
        "id": "user123",
        "email": email,
        "user_metadata": {"username": username},
        "created_at": "2023-01-01T00:00:00Z"
    }

    with patch("supabase.AsyncClient.auth.sign_up", new_callable=AsyncMock) as mock_sign_up:
        mock_sign_up.return_value.user = type('User', (object,), {
            'id': expected_user['id'],
            'email': expected_user['email'],
            'user_metadata': expected_user['user_metadata'],
            'created_at': expected_user['created_at']
        })()
        result = await client.sign_up(email, password, username)
        assert result == expected_user
        mock_sign_up.assert_called_once()

@pytest.mark.asyncio
async def test_sign_up_invalid_email():
    client = SupabaseClient()
    email = "invalid_email"
    password = "password123"
    username = "testuser"

    with pytest.raises(ValueError) as exc_info:
        await client.sign_up(email, password, username)
    assert str(exc_info.value) == "유효하지 않은 이메일 형식입니다."

# 추가 테스트 케이스... 