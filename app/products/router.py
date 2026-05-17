from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

from app.products.models import Product

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.get("/")
async def get_products(
    db: AsyncSession = Depends(get_db)
):

    query = select(Product)

    result = await db.execute(query)

    products = result.scalars().all()

    return products