from fastapi import APIRouter

router = APIRouter(
    prefix="/content",
    tags=["content"]
)

@router.get("/")
async def get_content():
    return {"message": "Content endpoint"} 