from fastapi import FastAPI
from app.config import settings
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="SnapS API",
    description="Social Media Content Management API",
    version="1.0.0"
)

# 버전 정보 추가
__version__ = "1.0.0" 