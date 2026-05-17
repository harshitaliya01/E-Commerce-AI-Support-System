from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

from pydantic import BaseModel, EmailStr


class RegisterSchema(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    is_admin: bool

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"



from app.auth.service import (
    create_user,
    authenticate_user,
)

from app.core.security import create_access_token


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
)
async def register(
    payload: RegisterSchema,
    db: AsyncSession = Depends(get_db),
):

    user = await create_user(db, payload)

    return user


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    payload: LoginSchema,
    db: AsyncSession = Depends(get_db),
):

    user = await authenticate_user(
        db,
        payload.email,
        payload.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token({
        "sub": str(user.id)
    })

    return {
        "access_token": token
    }