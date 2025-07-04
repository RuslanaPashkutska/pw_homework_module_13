from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from src.database import models
from src.schemas.user import UserCreate


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(
        select(models.User).filter(models.User.email == email)
    )
    return result.scalar_one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(models.User).filter(models.User.id == user_id)
    )
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: UserCreate, hashed_password: str):
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def update_user_is_verified(db: AsyncSession, user_id: int, is_verified: bool) -> Optional[models.User]:
    user = await get_user_by_id(db, user_id)
    if user:
        user.is_verified = is_verified
        await db.commit()
        await db.refresh(user)
    return user


async def update_user_password(db: AsyncSession, user_id: int, new_hashed_password: str) -> Optional[models.User]:
    user = await get_user_by_id(db, user_id)
    if user:
        user.hashed_password = new_hashed_password
        await db.commit()
        await db.refresh(user)
    return user

async def update_user_avatar(db: AsyncSession, user_id: int, avatar_url: str) -> Optional[models.User]:
    user = await  get_user_by_id(db, user_id)
    if user:
        user.avatar = avatar_url
        await db.commit()
        await db.refresh(user)
    return user