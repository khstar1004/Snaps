from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.services.supabase import SupabaseClient
import logging

router = APIRouter(
    prefix="/statistics",
    tags=["statistics"]
)

supabase = SupabaseClient()
logger = logging.getLogger(__name__)

@router.get("/", name="statistics")
async def get_statistics(request: Request):
    try:
        stats_data = await supabase.get_statistics()
        return JSONResponse(content=stats_data)
    except Exception as e:
        logger.error(f"통계 데이터 가져오기 오류: {str(e)}")
        return JSONResponse(
            content={"error": "통계 데이터를 가져오는 중 오류가 발생했습니다."},
            status_code=500
        ) 