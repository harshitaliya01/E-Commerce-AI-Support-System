from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.model import User
from app.auth.router import RegisterSchema
from app.core.security import hash_password, verify_password
from app.core.logging import get_logger

logger = get_logger(__name__)


async def create_user(db: AsyncSession, payload: RegisterSchema):
    try:
        query = select(User).where(User.email == payload.email)
        result = await db.execute(query)

        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise Exception("Email already exists")

        user = User(full_name=payload.full_name,email=payload.email,hashed_password=hash_password(payload.password),)
        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user
    except Exception as e:
        logger.error(f"Error creating user {payload.email}: {e}", exc_info=True)
        raise e


async def authenticate_user(db: AsyncSession,email: str,password: str):
    try:
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        if not user:
            return None

        if not verify_password(password,user.hashed_password,):
            return None

        return user
    except Exception as e:
        logger.error(f"Error authenticating user {email}: {e}", exc_info=True)
        raise e