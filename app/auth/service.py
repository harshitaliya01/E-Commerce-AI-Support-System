from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.router import RegisterSchema
from app.core.security import (
    hash_password,
    verify_password,
)


async def create_user(
    db: AsyncSession,
    payload: RegisterSchema,
):

    query = select(User).where(
        User.email == payload.email
    )

    result = await db.execute(query)

    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise Exception("Email already exists")

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(
            payload.password
        ),
    )

    db.add(user)

    await db.commit()

    await db.refresh(user)

    return user


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
):

    query = select(User).where(
        User.email == email
    )

    result = await db.execute(query)

    user = result.scalar_one_or_none()

    if not user:
        return None

    if not verify_password(
        password,
        user.hashed_password,
    ):
        return None

    return user