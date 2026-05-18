from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from app.core.database import AsyncSessionLocal

from app.models.model import Order
from app.core.logging import get_logger

logger = get_logger(__name__)

async def get_order_details(order_id: str) -> dict:
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Order).where(
                    Order.order_number == order_id.upper()
                )
            )
    
            order = result.scalar_one_or_none()
    
        if not order:
            return {
                "error":
                f"Order {order_id} not found"
            }
    
        # calculate return eligibility dynamically
        return_eligible = False
    
        if order.delivered_at:
            now = datetime.now(timezone.utc)
            if order.delivered_at.tzinfo is None:
                now = now.replace(tzinfo=None)
                
            if now <= order.delivered_at + timedelta(days=order.refund_window_days):
                return_eligible = True
    
        return {
            "order_id":order.order_number,
            "user_id":order.user_id,
    
            "status":order.order_status,
    
            "items":[
                {
                    "name":order.product_name,
                    "qty":order.quantity,
                    "price":order.total_amount
                }
            ],
    
            "estimated_delivery":
            order.estimated_delivery.strftime(
                "%d %b %Y, %I:%M %p"
            )
            if order.estimated_delivery
            else "Not available",
    
            "payment_status":
            order.payment_status,
    
            "return_eligible":
            return_eligible,
    
            "carrier":
            order.courier_name,
    
            "tracking_url":
            f"https://track.example.com/{order.tracking_number}"
            if order.tracking_number
            else None,
    
            "refund_status":
            order.refund_status
        }
    except Exception as e:
        logger.error(f"Error fetching order {order_id}: {e}", exc_info=True)
        return {"error": "Internal server error"}

import random
import string


async def initiate_return(order_id:str):
    try:
        data = await get_order_details(order_id)
    
        if "error" in data:
            return {
                "success":False,
                "message":data["error"]
            }
    
        if not data["return_eligible"]:
            return {
                "success":False,
                "message":
                "Return window expired"
            }
    
        ref = (
            "RET-" +
            "".join(
                random.choices(
                    string.digits,
                    k=6
                )
            )
        )
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Order).where(
                    Order.order_number ==
                    order_id
                )
            )
    
            order = result.scalar_one()
    
            order.refund_status = (
                f"Requested ({ref})"
            )
    
            await db.commit()
    
        return {
            "success":True,
            "return_id":ref,
    
            "message":(
                f"Return request "
                f"{ref} created."
            )
        }
    except Exception as e:
        logger.error(f"Error initiating return for {order_id}: {e}", exc_info=True)
        return {"success":False, "message":"Internal server error"}