from fastapi import APIRouter, UploadFile, File, Depends
from src.services.cloudinary_service import upload_avatar
from src.database.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/")
async def get_users():
    return {"message": "List of users"}

@router.get("/{user_id}")
async def get_user(user_id: int):
    return {"message": f"Details of user {user_id}"}

@router.post("/avatar")
async def update_avatar(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    url = upload_avatar(file.file)
    return {"avatar_url": url}