from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import logging

router = APIRouter(
    prefix="/content-conversion",
    tags=["content_conversion"]
)

logger = logging.getLogger(__name__)

@router.get("/", name="content_conversion")
async def get_content_conversion(request: Request):
    try:
        return JSONResponse(content={
            "message": "준비 중입니다.",
            "conversions": [],
            "total": 0
        })
    except Exception as e:
        logger.error(f"콘텐츠 변환 데이터 가져오기 오류: {str(e)}")
        return JSONResponse(
            content={"error": "콘텐츠 변환 데이터를 가져오는 중 오류가 발생했습니다."},
            status_code=500
        ) 