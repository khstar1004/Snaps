from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from app.config import settings
from app.services.supabase import SupabaseClient
import httpx
import logging

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

supabase = SupabaseClient()
logger = logging.getLogger(__name__)

@router.get("/instagram", name="instagram_auth")
async def instagram_auth():
    """Instagram OAuth 인증 시작"""
    try:
        redirect_uri = f"{settings.BASE_URL}/auth/instagram/callback"
        auth_url = (
            f"https://api.instagram.com/oauth/authorize?"
            f"client_id={settings.INSTAGRAM_CLIENT_ID}&"
            f"redirect_uri={redirect_uri}&"
            f"scope=user_profile,user_media&"
            f"response_type=code"
        )
        return RedirectResponse(url=auth_url)
    except Exception as e:
        logger.error(f"Instagram auth error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Instagram 연동 중 오류가 발생했습니다."
        )

@router.get("/instagram/callback")
async def instagram_callback(code: str, request: Request):
    """Instagram OAuth 콜백 핸들러"""
    try:
        token_url = "https://api.instagram.com/oauth/access_token"
        data = {
            "client_id": settings.INSTAGRAM_CLIENT_ID,
            "client_secret": settings.INSTAGRAM_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "redirect_uri": settings.INSTAGRAM_REDIRECT_URI,
            "code": code
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            response.raise_for_status()
            token_data = response.json()
            access_token = token_data.get("access_token")

            if not access_token:
                raise HTTPException(status_code=400, detail="Access token을 가져올 수 없습니다.")

            # Supabase를 사용하여 사용자와 토큰을 연동
            user = await supabase.get_current_user(request)
            if not user:
                raise HTTPException(status_code=401, detail="인증된 사용자가 아닙니다.")

            await supabase.save_platform_token(user["id"], "instagram", access_token)

            return RedirectResponse(url="/my-page")
    except Exception as e:
        logger.error(f"Instagram callback error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Instagram 연동 중 오류가 발생했습니다."
        )


