from typing import Dict, List, Any, Optional
import httpx
import logging
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.config import settings

logger = logging.getLogger(__name__)

class InstagramService:
    def __init__(self, access_token: str, instagram_business_account_id: str = None):
        self.access_token = access_token
        self.instagram_business_account_id = instagram_business_account_id
        self.base_url = "https://graph.facebook.com/v18.0"

    async def get_media_list(self, limit: int = 25) -> List[Dict[str, Any]]:
        """Instagram 게시물 목록 조회"""
        try:
            account = await self.get_instagram_business_account()
            fields = "id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,comments_count,like_count"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/{account['id']}/media",
                    params={
                        "fields": fields,
                        "limit": limit,
                        "access_token": self.access_token
                    }
                )
                response.raise_for_status()
                return response.json().get("data", [])
        except Exception as e:
            logger.error(f"Error fetching media list: {str(e)}")
            raise

    async def get_media_comments(self, media_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """게시물의 댓글 목록 조회"""
        try:
            fields = "id,text,timestamp,username,replies{id,text,timestamp,username}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/{media_id}/comments",
                    params={
                        "fields": fields,
                        "limit": limit,
                        "access_token": self.access_token
                    }
                )
                response.raise_for_status()
                return response.json().get("data", [])
        except Exception as e:
            logger.error(f"Error fetching comments: {str(e)}")
            raise

    async def reply_to_comment(self, comment_id: str, message: str) -> Dict[str, Any]:
        """댓글에 답글 달기"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/{comment_id}/replies",
                    params={
                        "message": message,
                        "access_token": self.access_token
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error replying to comment: {str(e)}")
            raise

    async def hide_or_unhide_comment(self, comment_id: str, hide: bool) -> bool:
        """댓글 숨기기/보이기"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/{comment_id}",
                    params={
                        "hide": str(hide).lower(),
                        "access_token": self.access_token
                    }
                )
                response.raise_for_status()
                return response.json().get("success", False)
        except Exception as e:
            logger.error(f"Error {'hiding' if hide else 'unhiding'} comment: {str(e)}")
            raise

    async def create_media_post(self, image_url: str, caption: str) -> Dict[str, Any]:
        """새 Instagram 게시물 생성"""
        try:
            account = await self.get_instagram_business_account()
            endpoint = f"{self.base_url}/{account['id']}/media"

            data = {
                "image_url": image_url,
                "caption": caption,
                "access_token": self.access_token
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(endpoint, params={"access_token": self.access_token}, data=data)
                response.raise_for_status()
                media_id = response.json().get("id")

                # 게시물 게시
                publish_endpoint = f"{self.base_url}/{account['id']}/media_publish"
                publish_data = {
                    "creation_id": media_id,
                    "access_token": self.access_token
                }
                publish_response = await client.post(publish_endpoint, params={"access_token": self.access_token}, data=publish_data)
                publish_response.raise_for_status()
                return publish_response.json()
        except Exception as e:
            logger.error(f"Error creating media post: {str(e)}")
            raise

    async def get_detailed_insights(self, period: str = "day", metrics: List[str] = None) -> Dict[str, Any]:
        """상세 인사이트 데이터 조회"""
        if metrics is None:
            metrics = [
                "impressions", "reach", "profile_views",
                "follower_count", "website_clicks", "email_contacts",
                "get_directions_clicks", "phone_call_clicks",
                "text_message_clicks"
            ]

        try:
            account = await self.get_instagram_business_account()
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/{account['id']}/insights",
                    params={
                        "metric": ",".join(metrics),
                        "period": period,
                        "access_token": self.access_token
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching detailed insights: {str(e)}")
            raise

    async def get_instagram_business_account(self) -> Dict[str, Any]:
        """Instagram 비즈니스 계정 정보 조회"""
        try:
            if not self.instagram_business_account_id:
                # 메타데이터에 계정 ID가 없는 경우 페이지 정보에서 조회
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(
                        f"{self.base_url}/me/accounts",
                        params={
                            "fields": "instagram_business_account{id,name,username,profile_picture_url}",
                            "access_token": self.access_token
                        }
                    )
                    response.raise_for_status()
                    pages_data = response.json().get("data", [])
                    if not pages_data:
                        raise ValueError("연결된 Facebook 페이지가 없습니다.")
                    
                    page = pages_data[0]
                    instagram_account = page.get("instagram_business_account")
                    if not instagram_account:
                        raise ValueError("연결된 Instagram 비즈니스 계정이 없습니다.")
                    
                    self.instagram_business_account_id = instagram_account["id"]
                    return instagram_account

            # 이미 계정 ID가 있는 경우 직접 조회
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/{self.instagram_business_account_id}",
                    params={
                        "fields": "id,username,profile_picture_url,name,biography,follows_count,followers_count,media_count,website",
                        "access_token": self.access_token
                    }
                )
                response.raise_for_status()
                return response.json()

        except httpx.TimeoutException:
            logger.error("Instagram API 요청 시간 초과")
            raise HTTPException(status_code=504, detail="Instagram API 요청 시간이 초과되었습니다.")
        except httpx.RequestError as e:
            logger.error(f"Instagram API 요청 실패: {str(e)}")
            raise HTTPException(status_code=502, detail="Instagram API 요청에 실패했습니다.")
        except Exception as e:
            logger.error(f"Error fetching Instagram business account: {str(e)}")
            raise

    async def get_account_insights(self, metrics: List[str], period: str = "day") -> Dict[str, Any]:
        """Instagram 인사이트 데이터 조회 - 최신 메트릭 지원"""
        try:
            if not self.instagram_business_account_id:
                account = await self.get_instagram_business_account()
                self.instagram_business_account_id = account["id"]

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/{self.instagram_business_account_id}/insights",
                    params={
                        "metric": ",".join(metrics),
                        "period": period,
                        "access_token": self.access_token
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching insights: {str(e)}")
            raise

    async def get_media_insights(self, media_id: str) -> Dict[str, Any]:
        """특정 미디어의 인사이트 데이터 조회 - 확장된 메트릭"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/{media_id}/insights",
                    params={
                        "metric": "engagement,impressions,reach,saved,video_views,exits,replies,taps_forward,taps_back",
                        "access_token": self.access_token
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching media insights: {str(e)}")
            raise

    async def get_user_media(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Instagram 미디어 조회 (인사이트 데이터 포함)"""
        try:
            ig_account = await self.get_instagram_business_account()
            ig_account_id = ig_account["id"]
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/{ig_account_id}/media",
                    params={
                        "fields": "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,like_count,comments_count",
                        "access_token": self.access_token,
                        "limit": limit
                    }
                )
                response.raise_for_status()
                media_items = response.json().get("data", [])
                
                # 각 미디 항목에 인사이트 데이터 추가
                for item in media_items:
                    try:
                        insights = await self.get_media_insights(item["id"])
                        item["insights"] = insights.get("data", [])
                    except Exception as e:
                        logger.warning(f"Failed to fetch insights for media {item['id']}: {str(e)}")
                        item["insights"] = []
                
                return media_items
        except Exception as e:
            logger.error(f"Error fetching user media: {str(e)}")
            raise

    async def create_media_container(self, media_type: str, media_url: str, caption: Optional[str] = None) -> str:
        """미디어 컨테이너 생성"""
        try:
            async with httpx.AsyncClient() as client:
                data = {
                    "image_url": media_url,
                    "caption": caption,
                    "access_token": self.access_token
                }
                if media_type == "VIDEO":
                    data["media_type"] = "VIDEO"
                    data["video_url"] = media_url
                    del data["image_url"]

                response = await client.post(
                    f"{self.base_url}/me/media",
                    json=data
                )
                response.raise_for_status()
                result = response.json()
                return result.get("id")
        except Exception as e:
            logger.error(f"Error creating media container: {str(e)}")
            raise

    async def publish_media(self, container_id: str) -> Dict[str, Any]:
        """미디어 게시"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/me/media_publish",
                    json={
                        "creation_id": container_id,
                        "access_token": self.access_token
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error publishing media: {str(e)}")
            raise

    def format_posts(self, media_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Instagram 미디어 데이터를 원하는 형식으로 변환"""
        formatted = []
        for item in media_items:
            formatted_item = {
                "id": item.get("id"),
                "caption": item.get("caption", ""),
                "media_type": item.get("media_type"),
                "media_urls": [item.get("media_url")] if item.get("media_url") else [],
                "permalink": item.get("permalink", ""),
                "timestamp": item.get("timestamp"),
                "like_count": item.get("like_count", 0),
                "comments_count": item.get("comments_count", 0),
                "insights": item.get("insights", [])
            }
            
            # 캐러셀 미디어 처리
            if item.get("media_type") == "CAROUSEL_ALBUM" and "children" in item:
                formatted_item["media_urls"] = [
                    child.get("media_url") for child in item["children"]["data"]
                    if child.get("media_url")
                ]
            
            formatted.append(formatted_item)
        return formatted

    async def refresh_token(self) -> bool:
        """액세스 토큰 갱신"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://graph.instagram.com/refresh_access_token",
                    params={
                        "grant_type": "ig_refresh_token",
                        "access_token": self.access_token
                    }
                )
                response.raise_for_status()
                data = response.json()
                self.access_token = data["access_token"]
                return True
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return False

    async def get_user_statistics(self, limit: int = 30) -> Dict[str, Any]:
        """사용자의 Instagram 통계 정보 가져오기"""
        try:
            profile = await self.get_user_profile()
            metrics = ["reach", "impressions", "profile_views", "follower_count"]
            insights = await self.get_account_insights(metrics)
            
            return {
                "profile": profile,
                "insights": insights.get("data", []),
                "period": "day",
                "limit": limit
            }
        except Exception as e:
            logger.error(f"Error getting user statistics: {str(e)}")
            raise

    async def exchange_code_for_token(self, code: str) -> str:
        """인증 코드를 액세스 토큰으로 교환"""
        token_url = f"{settings.INSTAGRAM_GRAPH_API_BASE}/oauth/access_token"
        data = {
            "client_id": settings.FACEBOOK_APP_ID,
            "client_secret": settings.FACEBOOK_APP_SECRET,
            "grant_type": "authorization_code",
            "redirect_uri": settings.INSTAGRAM_REDIRECT_URI,
            "code": code
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(token_url, data=data)
                response.raise_for_status()
                token_data = response.json()
                access_token = token_data.get("access_token")
                if not access_token:
                    raise HTTPException(
                        status_code=400,
                        detail="Access token을 가져올 수 없습니다."
                    )
                return access_token
            except httpx.HTTPError as e:
                logger.error(f"Token exchange error: {str(e)}")
                raise HTTPException(
                    status_code=400,
                    detail="토큰 교환 중 오류가 발생했습니다."
                )

    async def get_user_profile(self) -> Dict[str, Any]:
        """Instagram 프로필 정보 가져오기"""
        try:
            ig_account = await self.get_instagram_business_account()
            ig_account_id = ig_account["id"]
            endpoint = f"{self.base_url}/{ig_account_id}"
            params = {
                "fields": "id,username,account_type,media_count,biography,profile_picture_url",
                "access_token": self.access_token
            }
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            raise
