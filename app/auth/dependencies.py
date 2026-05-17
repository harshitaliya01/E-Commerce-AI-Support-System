from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials

from jose import jwt

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings

from app.auth.models import User


security = HTTPBearer()


async def get_current_user(

    credentials: HTTPAuthorizationCredentials =
        Depends(security),

    db: AsyncSession = Depends(get_db)

):

    token = credentials.credentials

    try:

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[
                settings.ALGORITHM
            ],
        )

        user_id = int(
            payload["sub"]
        )

    except:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    query = select(User).where(
        User.id == user_id
    )

    result = await db.execute(
        query
    )

    user = result.scalar_one_or_none()

    if not user:

        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user