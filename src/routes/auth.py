from fastapi import APIRouter, Depends, HTTPException, status, Form
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.user import RequestPasswordReset, ResetPassword, Token, UserLogin, UserCreate, UserResponse
from src.repository import users as repository_users
from src.auth.auth import get_password_hash, verify_password, create_access_token, create_refresh_token, verify_email_token, create_password_reset_token_and_save, reset_password, create_email_verification_token_and_save
from src.services.email import send_email
from src.database.db import get_db
from src.conf.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await repository_users.get_user_by_email(user.email, db)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    hashed_password = get_password_hash(user.password)
    new_user = await repository_users.create_user(user=user, hashed_password=hashed_password, db=db)
    verification_token = await create_email_verification_token_and_save(new_user.id, db)
    await send_email(new_user.email, new_user.email, verification_token, "verify_email")
    return new_user

@router.get("/verify_email/{token}")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    user = await verify_email_token(token, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification token")
    return {"message": "Email successfully verified"}

@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    db_user = await repository_users.get_user_by_email(user.email, db)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not db_user.is_verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Email not verified. Please check your inbox.")
    access_token = create_access_token(data={"sub": db_user.email})
    refresh_token = create_refresh_token(data={"sub": db_user.email})
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

@router.post("/request_password_reset", status_code=status.HTTP_200_OK)
async def request_password_reset(body: RequestPasswordReset, db: AsyncSession = Depends(get_db)):
    token = await create_password_reset_token_and_save(body.email, db)
    user = await repository_users.get_user_by_email(body.email, db)
    if token and user:
        await send_email(user.email, user.email, token, "reset_password")
    return {"message": "If a user with that email exists, a password reset link has been sent."}

@router.post("/reset_password", status_code=status.HTTP_200_OK)
async def reset_password_confirm(body: ResetPassword, db: AsyncSession = Depends(get_db)):
    user = await reset_password(body.token, body.new_password, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")
    return {"message": "Password has been reset successfully"}


@router.post("/reset-password")
async def reset_password(token:str = Form(...), new_password: str = Form(...), db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = await repository_users.get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    hashed_password = get_password_hash(new_password)
    user.hashed_password = hashed_password
    await db.commit()
    return {"message": "Password has been reset successfully"}