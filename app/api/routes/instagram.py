from fastapi import APIRouter, Depends, HTTPException, Query, Body
from app.services.instagram import InstagramService
from app.services.supabase import SupabaseClient
from app.auth.dependencies import get_current_user
from app.models.schemas import InstagramProfile, InstagramPost
from typing import List, Dict, Any, Optional

router = APIRouter(prefix="/instagram", tags=["instagram"])

async def get_instagram_service(
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: SupabaseClient = Depends()
) -> InstagramService:
    """Instagram 서비스 인스턴스를 생성합니다."""
    if not current_user:
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")
    
    token = await supabase.get_platform_token(current_user["id"], "instagram")
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Instagram 연동이 필요합니다."
        )
    
    return InstagramService(access_token=token)

@router.get("/profile", response_model=InstagramProfile)
async def get_profile(
    instagram_service: InstagramService = Depends(get_instagram_service)
):
    """Instagram 프로필 조회"""
    try:
        return await instagram_service.get_user_profile()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/media")
async def get_media_list(
    limit: int = Query(25, ge=1, le=100),
    instagram_service: InstagramService = Depends(get_instagram_service)
):
    """Instagram 게시물 목록 조회"""
    return await instagram_service.get_media_list(limit=limit)

@router.get("/media/{media_id}/comments")
async def get_media_comments(
    media_id: str,
    limit: int = Query(50, ge=1, le=100),
    instagram_service: InstagramService = Depends(get_instagram_service)
):
    """게시물의 댓글 목록 조회"""
    return await instagram_service.get_media_comments(media_id, limit=limit)

@router.post("/comments/{comment_id}/reply")
async def reply_to_comment(
    comment_id: str,
    message: str = Body(..., embed=True),
    instagram_service: InstagramService = Depends(get_instagram_service)
):
    """댓글에 답글 달기"""
    return await instagram_service.reply_to_comment(comment_id, message)

@router.post("/comments/{comment_id}/visibility")
async def update_comment_visibility(
    comment_id: str,
    hide: bool = Body(..., embed=True),
    instagram_service: InstagramService = Depends(get_instagram_service)
):
    """댓글 숨기기/보이기"""
    return await instagram_service.hide_or_unhide_comment(comment_id, hide)

@router.post("/media")
async def create_post(
    image_url: str = Body(...),
    caption: str = Body(""),
    instagram_service: InstagramService = Depends(get_instagram_service)
):
    """새 게시물 생성"""
    return await instagram_service.create_media_post(image_url, caption)

@router.get("/insights")
async def get_insights(
    period: str = Query("day", regex="^(day|week|month)$"),
    instagram_service: InstagramService = Depends(get_instagram_service)
):
    """인사이트 데이터 조회"""
    return await instagram_service.get_detailed_insights(period=period)