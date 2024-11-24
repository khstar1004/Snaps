from fastapi import APIRouter, Depends, HTTPException
from app.services.supabase import SupabaseClient
from app.auth.dependencies import get_current_user
from typing import Dict, Any
import logging

router = APIRouter(prefix="/unlink", tags=["unlink"])
logger = logging.getLogger(__name__)

@router.post("/instagram")
async def unlink_instagram(
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: SupabaseClient = Depends()
):
    """Instagram 연동 해제"""
    try:
        await supabase.unlink_platform_token(current_user["id"], "instagram")
        return {"message": "Instagram 연동이 해제되었습니다."}
    except Exception as e:
        logger.error(f"Error unlinking Instagram: {str(e)}")
        raise HTTPException(status_code=500, detail="연동 해제 중 오류가 발생했습니다.") 