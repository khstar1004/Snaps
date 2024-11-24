from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Supabase 설정
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # Facebook/Meta 설정
    FACEBOOK_APP_ID: str
    FACEBOOK_APP_SECRET: str
    
    # Instagram 설정
    INSTAGRAM_CLIENT_ID: str
    INSTAGRAM_CLIENT_SECRET: str
    INSTAGRAM_REDIRECT_URI: str
    
    # Thread 설정
    THREAD_CLIENT_ID: str
    THREAD_CLIENT_SECRET: str
    THREAD_REDIRECT_URI: str
    
    # OpenAI 설정
    OPENAI_API_KEY: str
    
    # 앱 설정
    BASE_URL: str
    SECRET_KEY: str
    PRODUCTION: bool = False  # 기본값 False
    ALLOW_NGROK: bool = False

    # 설정 모델
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='allow'  # 추가 환경 변수 허용
    )

    @property
    def use_https(self) -> bool:
        return self.PRODUCTION or self.ALLOW_NGROK

settings = Settings()