from fastapi import APIRouter, Depends, HTTPException, Query
from app.services.thread import ThreadService
from app.services.supabase import SupabaseClient
from app.auth.dependencies import get_current_user
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/threads", tags=["threads"])

async def get_thread_service(
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: SupabaseClient = Depends()
) -> ThreadService:
    """Thread 서비스 인스턴스 생성"""
    if not current_user:
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")
    
    token = await supabase.get_platform_token(current_user["id"], "thread")
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Thread 연동이 필요합니다."
        )
    
    return ThreadService(access_token=token)

@router.get("/profile")
async def get_profile(
    thread_service: ThreadService = Depends(get_thread_service)
):
    """Thread 프로필 조회"""
    return await thread_service.get_user_profile()

@router.get("/media")
async def get_media_list(
    limit: int = Query(25, ge=1, le=100),
    thread_service: ThreadService = Depends(get_thread_service)
):
    """Thread 게시물 목록 조회"""
    return await thread_service.get_media_list(limit=limit)

@router.get("/media/{media_id}/insights")
async def get_media_insights(
    media_id: str,
    thread_service: ThreadService = Depends(get_thread_service)
):
    """Thread 게시물 인사이트 조회"""
    return await thread_service.get_media_insights(media_id)

@router.get("/insights")
async def get_user_insights(
    since: Optional[str] = None,
    until: Optional[str] = None,
    thread_service: ThreadService = Depends(get_thread_service)
):
    """Thread 사용자 인사이트 조회"""
    return await thread_service.get_user_insights(since, until)

@router.post("/media")
async def create_post(
    text: str,
    media_url: Optional[str] = None,
    media_type: str = "TEXT_POST",
    thread_service: ThreadService = Depends(get_thread_service)
):
    """Thread 게시물 생성"""
    try:
        result = await thread_service.create_post(text, media_url, media_type)
        return result
    except Exception as e:
        logger.error(f"Error creating Thread post: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"게시물 생성 중 오류가 발생했습니다: {str(e)}"
        ) 