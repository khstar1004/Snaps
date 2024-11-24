from supabase import create_client, Client
from fastapi import Request, HTTPException
from typing import Optional, Dict, Any
import logging
from app.config import settings
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class SupabaseClient:
    def __init__(self):
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )

    def _validate_email(self, email: str) -> bool:
        """이메일 형식 검증"""
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(pattern, email))

    def sign_up(self, email: str, password: str, username: str):
        """새 사용자 등록"""
        try:
            # 입력값 검증
            if not self._validate_email(email):
                raise ValueError("유효하지 않은 이메일 형식입니다.")
            if len(password) < 6:
                raise ValueError("비밀번호는 최소 6자리 이상이어야 합니다.")
            if not username:
                raise ValueError("사용자명은 필수입니다.")

            # 사용자 생성
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "username": username
                    }
                }
            })
            
            if response.user:
                # datetime 객체를 ISO 형식 문자열로 변환
                created_at = response.user.created_at
                if isinstance(created_at, datetime):
                    created_at = created_at.isoformat()
                
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "username": username,
                    "created_at": created_at
                }
            return None

        except Exception as e:
            logger.error(f"Sign up error: {str(e)}")
            raise

    async def sign_in_with_password(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """이메일과 비밀번호로 사용자를 인증"""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "user_metadata": response.user.user_metadata,
                    "access_token": response.session.access_token if response.session else None,
                    "refresh_token": response.session.refresh_token if response.session else None
                }
            return None
        except Exception as e:
            logger.error(f"로그인 에러: {str(e)}")
            return None

    async def get_current_user(self, request: Request) -> Optional[Dict[str, Any]]:
        """현재 로그인된 사용자 정보 조회"""
        try:
            user_id = request.session.get("user_id")
            if user_id:
                return await self.get_user(user_id)  # 사용자 정보 가져오기
            return None
        except Exception as e:
            logger.error(f"Get current user error: {str(e)}")
            return None

    async def save_platform_token(self, user_id: str, platform: str, access_token: str, metadata: Dict[str, Any] = None) -> bool:
        """플랫폼 토큰 저장"""
        try:
            data = {
                "user_id": user_id,
                "platform": platform,
                "access_token": access_token,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            if metadata:
                data["metadata"] = metadata

            response = self.client.table("platform_tokens").upsert(data).execute()
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error saving platform token: {str(e)}")
            raise

    async def get_platform_token(self, user_id: str, platform: str) -> Optional[str]:
        """플랫폼 토큰 조회"""
        try:
            response = await self.client.table("platform_tokens").select("access_token").eq("user_id", user_id).eq("platform", platform).execute()
            if response.data:
                return response.data[0]["access_token"]
            return None
        except Exception as e:
            logger.error(f"Error getting platform token: {str(e)}")
            return None

    async def check_platform_connection(self, user_id: str, platform: str) -> bool:
        """플랫폼 연동 상태 확인"""
        try:
            response = self.client.table("platform_tokens").select("*").eq("user_id", user_id).eq("platform", platform).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error checking platform connection: {e}")
            return False

    async def unlink_platform_token(self, user_id: str, platform: str) -> bool:
        """플랫폼 연동 해제"""
        try:
            response = await self.client.table("platform_tokens").delete().eq("user_id", user_id).eq("platform", platform).execute()
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error unlinking platform token: {str(e)}")
            raise

    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """사용자 정보 조회"""
        try:
            # auth.users 테이블에서 기본 정보 조회
            user = self.client.auth.admin.get_user_by_id(user_id)
            
            if user and user.user:  # user.user로 접근
                return {
                    "id": user.user.id,
                    "email": user.user.email,
                    "username": user.user.user_metadata.get("username", "사용자"),
                    "created_at": user.user.created_at.isoformat() if user.user.created_at else "",
                    "profile_pic": user.user.user_metadata.get("avatar_url", None)
                }
            return None
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None