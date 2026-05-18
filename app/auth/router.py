from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from app.auth.service import create_user,authenticate_user
from app.core.security import create_access_token
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from pydantic import BaseModel, EmailStr
from app.core.logging import get_logger

logger = get_logger(__name__)

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



router = APIRouter(prefix="/auth",tags=["Authentication"])


@router.post("/register",response_model=UserResponse,)
async def register(payload: RegisterSchema,db: AsyncSession = Depends(get_db),):
    try:
        user = await create_user(db, payload)
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error in register endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.post("/login",response_model=TokenResponse)
async def login(payload: LoginSchema,db: AsyncSession = Depends(get_db),):
    try:
        user = await authenticate_user(db,payload.email,payload.password)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid credentials",)
        token = create_access_token({"sub": str(user.id)})
        return {"access_token": token}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error in login endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")