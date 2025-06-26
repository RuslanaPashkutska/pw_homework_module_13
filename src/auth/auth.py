from datetime import datetime, timedelta
from typing import Optional
import uuid
from jose import JWTError, jwt
from passlib.context import CryptContext

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User, VerificationToken
from src.schemas.user import TokenData
from src.repository import users as repository_users
from src.repository import auth as repository_auth
from src.conf.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_password_hash(password:str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password:str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=7))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

async def get_current_user(token:str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = await repository_users.get_user_by_email(token_data.email, db)
    if user is None:
        raise credentials_exception
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def create_email_verification_token_and_save(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=14))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.refresh_secret_key, algorithm=settings.algorithm)


def create_email_verification_token(user_id: int) -> str:
    token = str(uuid.uuid4())
    return token

async def save_verification_token(user_id: int, token: str, token_type:str, db:AsyncSession) -> None:
    expires_at = datetime.utcnow() + timedelta(hours=2)
    verification_token_db = VerificationToken(
        user_id=user_id,
        token=token,
        token_type=token_type,
        expires_at=expires_at
    )
    await repository_auth.create_verification_token(verification_token_db, db)

async def verify_email_token(token: str, db: AsyncSession) -> Optional[User]:
    verification_token = await repository_auth.get_verification_token(token, "email_verification", db)

    if verification_token is None or verification_token.expires_at < datetime.utcnow():
        return None

    user = await repository_users.get_user_by_id(verification_token.user_id, db)
    if user:
        user.is_verified = True
        await repository_users.update_user(user, db)
        await repository_auth.delete_verification_token(verification_token.id, db)
    return user


async def create_password_reset_token_and_save(user_email: str, db: AsyncSession) -> Optional[str]:
    user = await repository_users.get_user_by_email(user_email, db)
    if not user:
        return None

    token = str(uuid.uuid4())
    await save_verification_token(user.id, token, "password_reset", db)
    return token

async def reset_password(token: str, new_password: str, db: AsyncSession) -> Optional[User]:
    reset_token = await repository_auth.get_verification_token(token, "password_reset", db)

    if reset_token is None or reset_token.expires_at < datetime.utcnow():
        return None

    user = await repository_users.get_user_by_id(reset_token.user_id, db)
    if user:
        hashed_new_password = get_password_hash(new_password)
        await repository_users.update_user_password(user.id, hashed_new_password, db)
        await repository_auth.delete_verification_token(reset_token.id, db)
    return user