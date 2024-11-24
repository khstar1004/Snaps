from typing import Dict, List, Any, Optional

import httpx

import logging

from fastapi import HTTPException

from datetime import datetime



logger = logging.getLogger(__name__)



class ThreadService:

    def __init__(self, access_token: str):

        self.access_token = access_token

        self.base_url = "https://api.thread.com/v1"



    async def create_post(self, content: str, media_type: str = "TEXT", media_url: Optional[str] = None) -> Dict[str, Any]:

        """Thread 포스트 생성"""

        try:

            endpoint = f"{self.base_url}/me/media"

            creation_params = {

                "caption": content,

                "media_type": media_type,

                "access_token": self.access_token

            }

            

            if media_url:

                creation_params["image_url"] = media_url



            async with httpx.AsyncClient() as client:

                response = await client.post(

                    endpoint,

                    params={"access_token": self.access_token},

                    json=creation_params

                )

                response.raise_for_status()

                return response.json()

        except Exception as e:

            logger.error(f"Error creating Thread post: {str(e)}")

            raise



    async def get_thread(self, thread_id: str) -> Dict[str, Any]:

        """Thread 포스트 조회"""

        try:

            async with httpx.AsyncClient() as client:

                response = await client.get(

                    f"{self.base_url}/threads/{thread_id}",

                    params={

                        "fields": "id,text,media_type,media_url,created_time,replies_count,likes_count",

                        "access_token": self.access_token

                    }

                )

                response.raise_for_status()

                return response.json()

        except Exception as e:

            logger.error(f"Error fetching thread: {str(e)}")

            raise 



    async def get_thread_statistics(self, thread_id: str) -> Dict[str, Any]:

        """Thread 게시물 통계 조회"""

        try:

            async with httpx.AsyncClient() as client:

                response = await client.get(

                    f"{self.base_url}/threads/{thread_id}/insights",

                    params={

                        "metric": "impressions,reach,engagement,saves,shares",

                        "access_token": self.access_token

                    }

                )

                response.raise_for_status()

                return response.json()

        except Exception as e:

            logger.error(f"Error getting thread statistics: {str(e)}")

            raise



    async def reply_to_thread(self, thread_id: str, content: str) -> Dict[str, Any]:

        """Thread 댓글 작성"""

        try:

            async with httpx.AsyncClient() as client:

                response = await client.post(

                    f"{self.base_url}/threads/{thread_id}/replies",

                    json={

                        "text": content,

                        "access_token": self.access_token

                    }

                )

                response.raise_for_status()

                return response.json()

        except Exception as e:

            logger.error(f"Error replying to thread: {str(e)}")

            raise



    async def get_user_profile(self) -> Dict[str, Any]:

        """Thread 프로필 정보 조회"""

        try:

            fields = "id,username,name,threads_profile_picture_url,threads_biography"

            async with httpx.AsyncClient() as client:

                response = await client.get(

                    f"{self.base_url}/me",

                    params={

                        "fields": fields,

                        "access_token": self.access_token

                    }

                )

                response.raise_for_status()

                return response.json()

        except Exception as e:

            logger.error(f"Error getting Thread profile: {str(e)}")

            raise



    async def get_media_list(self, limit: int = 25) -> List[Dict[str, Any]]:

        """Thread 게시물 목록 조회"""

        try:

            fields = "id,media_product_type,media_type,media_url,permalink,text,timestamp,shortcode,thumbnail_url,children,is_quote_post"

            async with httpx.AsyncClient() as client:

                response = await client.get(

                    f"{self.base_url}/me/threads",

                    params={

                        "fields": fields,

                        "limit": limit,

                        "access_token": self.access_token

                    }

                )

                response.raise_for_status()

                return response.json().get("data", [])

        except Exception as e:

            logger.error(f"Error fetching Thread media list: {str(e)}")

            raise



    async def get_media_insights(self, media_id: str) -> Dict[str, Any]:

        """Thread 게시물 인사이트 조회"""

        try:

            metrics = "views,likes,replies,reposts,quotes"

            async with httpx.AsyncClient() as client:

                response = await client.get(

                    f"{self.base_url}/{media_id}/insights",

                    params={

                        "metric": metrics,

                        "access_token": self.access_token

                    }

                )

                response.raise_for_status()

                return response.json()

        except Exception as e:

            logger.error(f"Error fetching Thread media insights: {str(e)}")

            raise



    async def get_user_insights(self, since: Optional[str] = None, until: Optional[str] = None) -> Dict[str, Any]:

        """Thread 사용자 인사이트 조회"""

        try:

            metrics = "views,likes,replies,reposts,quotes,followers_count"

            params = {

                "metric": metrics,

                "access_token": self.access_token

            }

            if since:

                params["since"] = since

            if until:

                params["until"] = until



            async with httpx.AsyncClient() as client:

                response = await client.get(

                    f"{self.base_url}/me/threads_insights",

                    params=params

                )

                response.raise_for_status()

                return response.json()

        except Exception as e:

            logger.error(f"Error fetching Thread user insights: {str(e)}")

            raise
