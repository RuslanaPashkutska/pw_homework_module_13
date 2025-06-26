from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select
from datetime import date, timedelta
from src.database import models
from src.schemas.contact import ContactCreate, ContactUpdate


async def create_contact(db: AsyncSession, contact: ContactCreate, user_id: int):
    db_contact = models.Contact(**contact.model_dump(), owner_id=user_id)
    db.add(db_contact)
    await db.commit()
    await db.refresh(db_contact)
    return db_contact



async def get_contact(db: AsyncSession, contact_id: int, user_id: int):
    result = await db.execute(
        select(models.Contact).filter(
            models.Contact.id == contact_id,
            models.Contact.owner_id == user_id
        )
    )
    return result.scalar_one_or_none()


async def get_contacts(db: AsyncSession, user_id: int, skip: int = 0, limit: int =100):
    result = await db.execute(
        select(models.Contact).filter(models.Contact.owner_id == user_id).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def update_contact(db: AsyncSession, contact_id: int, updated: ContactUpdate, user_id: int):
    contact = await get_contact(db, contact_id, user_id)
    if contact:
        for key, value in updated.model_dump(exclude_unset=True).items():
            setattr(contact, key, value)
        await db.commit()
        await db.refresh(contact)
    return contact

async def delete_contact(db: AsyncSession, contact_id: int, user_id: int):
    contact = await get_contact(db, contact_id, user_id)
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact

async def search_contacts(db: AsyncSession, query: str, user_id: int):
    result = await db.execute(
        select(models.Contact).filter(
            models.Contact.owner_id == user_id,
            or_(
                models.Contact.first_name.ilike(f"%{query}%"),
                models.Contact.last_name.ilike(f"%{query}%"),
                models.Contact.email.ilike(f"%{query}%")
            )
        )
    )
    return result.scalars().all()

async def get_upcoming_birthdays(db: AsyncSession, user_id: int):
    today = date.today()
    next_week = today + timedelta(days=7)
    result = await db.execute(
        select(models.Contact).filter(
            models.Contact.owner_id == user_id,
            models.Contact.birthday.between(today, next_week)
        )
    )
    return result.scalars().all()
