from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.model import Order
from app.core.logging import get_logger
from app.services.order_details import get_order_details
logger = get_logger(__name__)

import random
import string


async def initiate_return(order_id:str):
    try:
        data = await get_order_details(order_id)
        if "error" in data:
            return {"success":False,"message":data["error"]}
    
        if not data["return_eligible"]:
            return {"success":False,"message":"Return window expired"}
    
        ref = ("RET-" +"".join(random.choices(string.digits,k=6)))

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Order).where(Order.order_number == order_id.upper())
            )
            order = result.scalar_one()
            order.refund_status = (f"requested")
            await db.commit()
    
        return {
            "success":True,
            "return_id":ref,
            "message":("Return request created.")
        }
    except Exception as e:
        logger.error(f"Error initiating return for {order_id}: {e}", exc_info=True)
        return {"success":False, "message":"Internal server error"}