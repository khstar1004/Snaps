from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.services.supabase import SupabaseClient
import logging

router = APIRouter(
    prefix="/content-management",
    tags=["content_management"]
)

supabase = SupabaseClient()
logger = logging.getLogger(__name__)

@router.get("/", name="content_management")
async def get_content_management(request: Request):
    try:
        management_data = await supabase.get_content_management_data()
        return JSONResponse(content=management_data)
    except Exception as e:
        logger.error(f"콘텐츠 관리 데이터 가져오기 오류: {str(e)}")
        return JSONResponse(
            content={"error": "콘텐츠 관리 데이터를 가져오는 중 오류가 발생했습니다."},
            status_code=500
        ) 