from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

from app.orders.models import Order

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.get("/")
async def get_orders(
    db: AsyncSession = Depends(get_db)
):

    query = select(Order)

    result = await db.execute(query)

    orders = result.scalars().all()

    return orders


@router.get("/{order_id}")
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
):

    query = select(Order).where(
        Order.id == order_id
    )

    result = await db.execute(query)

    order = result.scalar_one_or_none()

    return order