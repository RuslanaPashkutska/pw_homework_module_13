from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from src.schemas.contact import ContactCreate, ContactResponse, ContactUpdate
from src.database.db import get_db
from src.auth.auth import get_current_user
from src.database.models import User
from src.repository import contacts as repository_contacts
from typing import Optional
from fastapi_limiter.depends import RateLimiter
from src.cache.redis_client import redis_client
router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.get("/", response_model=List[ContactResponse])
async def get_contacts(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    contacts = await repository_contacts.get_contacts_by_user(current_user.id, db)
    return contacts

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def create_contact(contact: ContactCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    new_contact = await repository_contacts.create_contact(user_id=current_user.id, contact=contact, db=db)
    return new_contact

@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact_by_id(contact_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    contact = await repository_contacts.get_contact(db, contact_id, current_user.id)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: int, updated_contact: ContactUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    contact = await repository_contacts.update_contact(db, contact_id, updated_contact, current_user.id)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    contact = await repository_contacts.delete_contact(db, contact_id, current_user.id)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/search/", response_model=List[ContactResponse])
async def search_contacts(query: Optional[str] = None, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if query is None or not query.strip():
        return await repository_contacts.get_contacts(db, current_user.id)
    contacts = await repository_contacts.search_contacts(db, query, current_user.id)
    return contacts

@router.get("/birthdays/upcoming", response_model=List[ContactResponse])
async def get_upcoming_birthdays(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    birthdays = await repository_contacts.get_upcoming_birthdays(db, current_user.id)
    return birthdays

