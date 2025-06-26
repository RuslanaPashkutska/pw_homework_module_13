from sqlalchemy.ext.asyncio import  AsyncSession
from sqlalchemy import select, delete
from src.database import models
from typing import Optional

async def create_verification_token(token_db: models.VerificationToken, db:AsyncSession) -> models.VerificationToken:
    db.add(token_db)
    await db.commit()
    await db.refresh(token_db)
    return token_db

async def get_verification_token(token: str, token_type, db: AsyncSession) -> Optional[models.VerificationToken]:
    result = await db.execute(
        select(models.VerificationToken).filter(
            models.VerificationToken.token == token,
            models.VerificationToken.token_type == token_type
        )
    )
    return result.scalar_one_or_none()

async def delete_verification_token(token_id: int, db: AsyncSession) -> None:
    stmt = delete(models.VerificationToken).where(models.VerificationToken.id == token_id)
    await db.execute(stmt)
    await db.commit()