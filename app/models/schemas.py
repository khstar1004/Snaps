from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class User(BaseModel):
    id: int
    username: str
    email: str

class OAuthResponse(BaseModel):
    access_token: str
    token_type: str

class InstagramPost(BaseModel):
    id: str
    caption: Optional[str]
    media_type: str
    media_urls: List[str]
    permalink: str
    timestamp: str
    insights: Optional[List[Dict[str, Any]]] = []

class InstagramProfile(BaseModel):
    id: str
    username: str
    account_type: str
    media_count: int
    profile_picture_url: Optional[str] = None
    biography: Optional[str] = None

class ContentGenerationRequest(BaseModel):
    prompt: str
    target_platform: str
    has_image: bool = False

class ContentGenerationResponse(BaseModel):
    basic_converted_post: str
    rag_converted_post: str

class ThreadPostRequest(BaseModel):
    content: str
    media_type: str = "TEXT"
    media_url: Optional[str] = None 