from typing import Dict, Any, List
import httpx
from fastapi import HTTPException
import logging

from app.config import settings

logger = logging.getLogger(__name__)

class MetaBusinessService:
    def __init__(self):
        self.base_url = "https://graph.facebook.com"
        self.access_token = None  # 접근 토큰 저장을 위한 변수 선언
    
    async def get_business_account(self, access_token: str) -> Dict[str, Any]:
        """Meta Business 계정 정보 조회"""
        try:
            self.access_token = access_token  # 접근 토큰 저장
            endpoint = f"{self.base_url}/me/businesses"
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    endpoint,
                    params={
                        "access_token": self.access_token,
                        "fields": "id,name,created_time"
                    }
                )
                response.raise_for_status()
                businesses = response.json().get("data", [])
                if not businesses:
                    raise HTTPException(status_code=404, detail="비즈니스 계정을 찾을 수 없습니다.")
                return businesses[0]  # 첫 번째 비즈니스 계정 반환
        except httpx.HTTPError as e:
            logger.error(f"Error fetching business account: {str(e)}")
            raise HTTPException(status_code=502, detail="Meta Business API 요청에 실패했습니다.")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise

    async def list_pages(self) -> Dict[str, Any]:
        """비즈니스 계정에 연결된 페이지 목록 조회"""
        try:
            if not self.access_token:
                raise HTTPException(status_code=401, detail="접근 토큰이 설정되지 않았습니다.")
            
            endpoint = f"{self.base_url}/me/accounts"
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    endpoint,
                    params={
                        "access_token": self.access_token,
                        "fields": "id,name,permalink"
                    }
                )
                response.raise_for_status()
                pages = response.json().get("data", [])
                return pages
        except httpx.HTTPError as e:
            logger.error(f"Error listing pages: {str(e)}")
            raise HTTPException(status_code=502, detail="Meta Business API 요청에 실패했습니다.")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise

    async def get_page_insights(self, page_id: str, metrics: List[str], period: str = "day") -> Dict[str, Any]:
        """특정 페이지의 인사이트 데이터 조회"""
        try:
            endpoint = f"{self.base_url}/{page_id}/insights"
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    endpoint,
                    params={
                        "access_token": self.access_token,
                        "metric": ",".join(metrics),
                        "period": period
                    }
                )
                response.raise_for_status()
                insights = response.json().get("data", [])
                return insights
        except httpx.HTTPError as e:
            logger.error(f"Error fetching page insights: {str(e)}")
            raise HTTPException(status_code=502, detail="Meta Business API 요청에 실패했습니다.")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise