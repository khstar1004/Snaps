from fastapi import Request, HTTPException
from typing import Optional, Dict, Any

async def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """현재 로그인된 사용자 정보를 가져옵니다."""
    user = request.session.get("user")
    if not user or not request.session.get("authenticated"):
        return None
    return user 