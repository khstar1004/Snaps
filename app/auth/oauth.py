from fastapi import APIRouter, HTTPException, Request, Depends, Query
from fastapi.responses import RedirectResponse
from app.config import settings
from app.services.supabase import SupabaseClient
import httpx
import logging
import json
from urllib.parse import quote
from datetime import datetime, timedelta
import secrets

router = APIRouter()
supabase = SupabaseClient()
logger = logging.getLogger(__name__)

@router.get("/instagram")
async def instagram_auth():
    """Instagram OAuth 인증 시작 - Facebook Business Login 사용"""
    try:
        redirect_uri = f"{settings.BASE_URL}auth/instagram/callback"
        
        # Facebook Login URL 구성 (최신 API 버전 사용)
        extras = json.dumps({
            "setup": {
                "channel": "IG_API_ONBOARDING",
                "platform": "instagram"
            }
        })
        
        scope = ",".join([
            'instagram_basic',
            'instagram_content_publish',
            'instagram_manage_insights',
            'pages_show_list',
            'pages_read_engagement',
            'pages_manage_metadata',
            'business_management'
        ])
        
        auth_url = (
            f"https://www.facebook.com/v21.0/dialog/oauth?"
            f"client_id={settings.FACEBOOK_APP_ID}&"
            f"redirect_uri={quote(redirect_uri)}&"
            f"state={secrets.token_urlsafe(32)}&"
            f"scope={quote(scope)}&"
            f"response_type=code&"
            f"extras={quote(extras)}"
        )
        
        return RedirectResponse(url=auth_url)
    except Exception as e:
        logger.error(f"Instagram auth error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Instagram 연동 중 오류가 발생했습니다."
        )

@router.get("/instagram/callback")
async def instagram_callback(
    code: str = Query(None),
    state: str = Query(None),
    error: str = Query(None),
    error_reason: str = Query(None),
    request: Request = None
):
    """Instagram OAuth 콜백 처리"""
    try:
        if error:
            raise HTTPException(
                status_code=400,
                detail=f"Facebook 인증 오류: {error_reason}"
            )

        # 액세스 토큰 교환
        token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
        redirect_uri = f"{settings.BASE_URL}auth/instagram/callback"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                token_url,
                params={
                    "client_id": settings.FACEBOOK_APP_ID,
                    "client_secret": settings.FACEBOOK_APP_SECRET,
                    "redirect_uri": redirect_uri,
                    "code": code
                }
            )
            token_data = response.json()
            
            if "error" in token_data:
                raise HTTPException(
                    status_code=400,
                    detail=f"토큰 교환 실패: {token_data['error']['message']}"
                )

            access_token = token_data["access_token"]

            # 현재 사용자 확인
            user = await supabase.get_current_user(request)
            if not user:
                raise HTTPException(status_code=401, detail="인증된 사용자가 아닙니다.")

            # Instagram 비즈니스 계정 정보 조회
            accounts_response = await client.get(
                "https://graph.facebook.com/v18.0/me/accounts",
                params={
                    "access_token": access_token,
                    "fields": "instagram_business_account,name,access_token"
                }
            )
            accounts_data = accounts_response.json()

            if not accounts_data.get("data"):
                raise HTTPException(
                    status_code=400,
                    detail="연결된 Instagram 비즈니스 계정이 없습니다."
                )

            # 첫 번째 페이지의 Instagram 비즈니스 계정 사용
            page = accounts_data["data"][0]
            instagram_business_account = page.get("instagram_business_account")

            if not instagram_business_account:
                raise HTTPException(
                    status_code=400,
                    detail="Instagram 비즈니스 계정이 연결되어 있지 않습니다."
                )

            # 토큰 저장
            await supabase.save_platform_token(
                user_id=user["id"],
                platform="instagram",
                access_token=page["access_token"],
                metadata={
                    "page_id": page["id"],
                    "page_name": page["name"],
                    "instagram_business_account_id": instagram_business_account["id"],
                    "token_type": "long_lived",
                    "expires_at": (datetime.utcnow() + timedelta(days=60)).isoformat()
                }
            )

            return RedirectResponse(url="/my-page")

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Instagram callback error: {str(e)}")
        raise HTTPException(status_code=500, detail="Instagram 연동 중 오류가 발생했습니다.")

@router.get("/thread")
async def thread_auth():
    """Thread OAuth 인증 시작"""
    try:
        redirect_uri = f"{settings.BASE_URL}auth/thread/callback"

        scope = ",".join([
            'threads_basic',
            'threads_content_publish',
            'threads_manage_insights'
        ])

        state = secrets.token_urlsafe(32)

        auth_url = (
            f"https://www.facebook.com/v18.0/dialog/oauth?"
            f"client_id={settings.FACEBOOK_APP_ID}&"
            f"redirect_uri={quote(redirect_uri)}&"
            f"state={state}&"
            f"scope={quote(scope)}&"
            f"response_type=code"
        )

        return RedirectResponse(url=auth_url)
    except Exception as e:
        logger.error(f"Thread auth error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Thread 연동 중 오류가 발생했습니다."
        )

@router.get("/thread/callback")
async def thread_callback(
    code: str = Query(None),
    state: str = Query(None),
    error: str = Query(None),
    error_reason: str = Query(None),
    request: Request = None
):
    """Thread OAuth 콜백 처리"""
    try:
        if error:
            raise HTTPException(
                status_code=400,
                detail=f"Facebook 인증 오류: {error_reason}"
            )

        # 액세스 토큰 교환
        token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
        redirect_uri = f"{settings.BASE_URL}auth/thread/callback"

        async with httpx.AsyncClient() as client:
            response = await client.get(
                token_url,
                params={
                    "client_id": settings.FACEBOOK_APP_ID,
                    "client_secret": settings.FACEBOOK_APP_SECRET,
                    "redirect_uri": redirect_uri,
                    "code": code
                }
            )
            token_data = response.json()

            if "error" in token_data:
                raise HTTPException(
                    status_code=400,
                    detail=f"토큰 교환 실패: {token_data['error']['message']}"
                )

            access_token = token_data["access_token"]

            # 현재 사용자 확인
            user = await supabase.get_current_user(request)
            if not user:
                raise HTTPException(status_code=401, detail="인증된 사용자가 아닙니다.")

            # Thread 프로필 정보 조회
            account_response = await client.get(
                "https://graph.facebook.com/v18.0/me/accounts",
                params={
                    "access_token": access_token,
                    "fields": "threads_profile,name,access_token"
                }
            )
            accounts_data = account_response.json()

            if not accounts_data.get("data"):
                raise HTTPException(
                    status_code=400,
                    detail="연결된 Thread 계정이 없습니다."
                )

            # 첫 번째 페이지의 Thread 프로필 사용
            page = accounts_data["data"][0]
            threads_profile = page.get("threads_profile")

            if not threads_profile:
                raise HTTPException(
                    status_code=400,
                    detail="Thread 계정이 연결되어 있지 않습니다."
                )

            # 토큰 저장
            await supabase.save_platform_token(
                user_id=user["id"],
                platform="thread",
                access_token=page["access_token"],
                metadata={
                    "page_id": page["id"],
                    "page_name": page["name"],
                    "threads_profile_id": threads_profile["id"],
                    "token_type": "long_lived",
                    "expires_at": (datetime.utcnow() + timedelta(days=60)).isoformat()
                }
            )

            return RedirectResponse(url="/my-page")

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Thread callback error: {str(e)}")
        raise HTTPException(status_code=500, detail="Thread 연동 중 오류가 발생했습니다.")
