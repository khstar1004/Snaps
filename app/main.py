from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.config import settings
from app.services.supabase import SupabaseClient
from app.api.routes.auth import router as auth_router
from app.api.routes.instagram import router as instagram_router
from app.api.routes.content import router as content_router
from app.api.routes.unlink import router as unlink_router
from app.api.routes.thread import router as thread_router
from app.api.routes.content_conversion import router as content_conversion_router
from app.api.routes.content_management import router as content_management_router
from app.api.routes.statistics import router as statistics_router
import logging
from datetime import datetime
from mangum import Mangum

logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="templates")
supabase = SupabaseClient()
logger.info("Supabase client initialized successfully.")

# FastAPI 인스턴스 생성
app = FastAPI(
    title="SnapS API",
    description="Social Media Content Management API",
    version="1.0.0"
)

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. 정적 파일 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. API 라우터 등록
app.include_router(auth_router, prefix="/auth")
app.include_router(instagram_router, prefix="/api/instagram")
app.include_router(content_router, prefix="/api/content")
app.include_router(unlink_router, prefix="/api/unlink")
app.include_router(thread_router, prefix="/api/thread")
app.include_router(content_conversion_router, prefix="/content-conversion")
app.include_router(content_management_router, prefix="/content-management")
app.include_router(statistics_router, prefix="/statistics")

# 3. 템플릿 컨텍스트 프로세서
@app.middleware("http")
async def add_session_to_templates(request: Request, call_next):
    response = await call_next(request)
    if hasattr(response, 'context'):
        response.context["session"] = request.session
    return response

# 4. 세션 유지를 위한 커스텀 미들웨어
@app.middleware("http")
async def session_middleware(request: Request, call_next):
    response = await call_next(request)
    if isinstance(response, RedirectResponse):
        return response
    session = request.cookies.get('session')
    if session:
        response.set_cookie(
            key='session',
            value=session,
            httponly=True,
            max_age=3600,
            samesite="lax",
            secure=settings.PRODUCTION
        )
    return response

# 5. 인증 미들웨어
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    public_paths = [
        "/",
        "/login",
        "/register",
        "/static",
        "/auth/instagram",
        "/auth/instagram/callback",
        "/auth/thread",
        "/auth/thread/callback",
        "/favicon.ico"
    ]

    is_public = any(request.url.path.startswith(path) for path in public_paths)
    user_id = request.session.get("user_id")

    if not is_public and not user_id:
        if request.url.path.startswith("/api"):
            return JSONResponse(status_code=401, content={"detail": "인증이 필요합니다."})
        return RedirectResponse(url="/login", status_code=303)

    response = await call_next(request)
    return response

# 7. 마지막으로 세션 미들웨어 추가
if settings.PRODUCTION:
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        max_age=3600,
        same_site="lax",
        https_only=True,
        session_cookie="session",
        path="/"
    )
else:
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        max_age=3600,
        same_site="lax",
        https_only=False,
        session_cookie="session",
        path="/"
    )

# 라우트 정의
@app.get("/", name="index")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "settings": settings
    })

@app.get("/converter", name="content_conversion")
async def converter(request: Request):
    return templates.TemplateResponse("converter.html", {
        "request": request,
        "settings": settings
    })

@app.get("/test-session")
async def test_session(request: Request):
    request.session["test"] = "session works"
    test_value = request.session.get("test")
    return {"message": f"Session is working: {test_value}"}

# 로그인 페이지 (GET 요청)
@app.get("/login", name="login")
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# 로그인 처리 (POST 요청)
@app.post("/login")
async def login_post(request: Request, email: str = Form(...), password: str = Form(...)):
    user = await supabase.sign_in_with_password(email, password)
    if user:
        request.session["user_id"] = user["id"]  # 'user_id'로 세션 저장
        return RedirectResponse(url="/", status_code=303)
    else:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "이메일 또는 비밀번호가 잘못되었습니다."
        })

# 회원가입 페이지 (GET 요청) 추가
@app.get("/register", name="register")
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# 회원가입 처리 (POST 요청)
@app.post("/register")
def register_post(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    try:
        # 비밀번호 확인
        if password != confirm_password:
            return templates.TemplateResponse("register.html", {
                "request": request,
                "error": "비밀번호가 일치하지 않습니다."
            })

        user = supabase.sign_up(email, password, username)
        if user:
            # datetime 객체를 ISO 형식 문자열로 변환하여 세션에 저
            session_user = {
                "id": user["id"],
                "email": user["email"],
                "username": user["username"],
                "created_at": user["created_at"].isoformat() if isinstance(user["created_at"], datetime) else user["created_at"]
            }
            request.session["user"] = session_user
            return RedirectResponse(url="/", status_code=303)
        else:
            return templates.TemplateResponse("register.html", {
                "request": request,
                "error": "회원가입에 실패했습니다. 다시 시도해주세요."
            })
    except ValueError as ve:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": str(ve)
        })
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "회원가입 중 오류가 발생했습니다."
        })

# 로그아웃 라우트 추가
@app.get("/logout", name="logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)

# 마이페이지 라우트 추가
@app.get("/my-page", name="my_page")
async def my_page(request: Request):
    user_id = request.session.get("user_id")
    if user_id:
        try:
            user_data = await supabase.get_user(user_id)
            if not user_data:
                user_data = {
                    "username": "사용자",
                    "email": "",
                    "created_at": "",
                    "profile_pic": None
                }
            
            # 플랫폼 연동 상태 확인
            try:
                instagram_linked = await supabase.check_platform_connection(user_id, "instagram")
            except Exception as e:
                logger.error(f"Instagram connection check error: {e}")
                instagram_linked = False

            try:
                thread_linked = await supabase.check_platform_connection(user_id, "thread")
            except Exception as e:
                logger.error(f"Thread connection check error: {e}")
                thread_linked = False

            return templates.TemplateResponse(
                "my_page.html",
                {
                    "request": request,
                    "user": user_data,
                    "session": request.session,
                    "is_authenticated": True,
                    "instagram_linked": instagram_linked,
                    "thread_linked": thread_linked,
                    "settings": settings
                }
            )
        except Exception as e:
            logger.error(f"Error in my_page: {e}")
            return templates.TemplateResponse(
                "my_page.html",
                {
                    "request": request,
                    "error": "프로필 정보를 불러오는 중 오류가 발생했습니다.",
                    "is_authenticated": True
                }
            )
    else:
        return RedirectResponse(url="/login", status_code=303)

# 404 에러 핸들러
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("404.html", {
        "request": request
    }, status_code=404)

# 500 에러 핸들러
@app.exception_handler(500)
async def server_error_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("500.html", {
        "request": request
    }, status_code=500)

# Supabase DB 연결 확인을 위한 스타트업 이벤트 수정
@app.on_event("startup")
async def startup_event():
    try:
        # Supabase에서 platform_tokens 테이블 데이터 조회
        test_token = supabase.client.table("platform_tokens").select("*").limit(1).execute()
        if test_token.data:
            logger.info("Supabase DB 연결이 성공적으로 이루어졌습니다.")
        else:
            logger.warning("Supabase DB는 연결되었으나, 플랫폼 토큰 데이터를 찾 수 없습니다.")
    except Exception as e:
        logger.error(f"Supabase DB 연결에 실패했습니다: {e}")

# 새로운 라우트 추가
@app.get("/content-conversion")
async def content_conversion(request: Request):
    return templates.TemplateResponse("content_conversion.html", {
        "request": request,
        "settings": settings
    })

@app.get("/content-management")
async def content_management(request: Request):
    return templates.TemplateResponse("content_management.html", {
        "request": request,
        "settings": settings
    })

@app.get("/statistics")
async def statistics(request: Request):
    return templates.TemplateResponse("statistics.html", {
        "request": request,
        "settings": settings
    })

@app.get("/privacy-policy")
async def privacy_policy(request: Request):
    return templates.TemplateResponse("privacy_policy.html", {
        "request": request,
        "settings": settings
    })

logger.info(f"SECRET_KEY: {settings.SECRET_KEY}")
logger.info(f"PRODUCTION: {settings.PRODUCTION}")