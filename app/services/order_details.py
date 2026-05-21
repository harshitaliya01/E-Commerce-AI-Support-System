from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.model import Order, Payment
from app.core.logging import get_logger

logger = get_logger(__name__)

async def get_order_details(order_id: str) -> dict:
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Order).where(Order.order_number == order_id.upper()))
            order = result.scalar_one_or_none()
    
            if not order:
                return {
                    "error": f"Order {order_id} not found",
                    "clear_order": True
                }
            payment_result=await db.execute(select(Payment).where(Payment.order_id==order.id))

            payment=payment_result.scalar_one_or_none()
            return_eligible= False
            delivered = order.delivered_at
            if delivered:
                    if delivered.tzinfo is None:
                        now = datetime.utcnow()
                    else:
                        now = datetime.now(timezone.utc)
                    return_eligible = (now <= delivered + timedelta(days=order.refund_window_days))
    
        return {
            "user_id":order.user_id,
            "order_id":order.order_number,
            "status":order.order_status,
            "items":[
                {
                    "name":order.product_name,
                    "qty":order.quantity,
                    "price":order.total_amount
                }
            ],
            "payment":{
                "status":
                payment.status if payment else "unknown",

                "method":
                payment.method if payment else None,

                "amount":
                payment.amount if payment else None,

                "transaction_id":
                payment.transaction_id if payment else None
            },
            "estimated_delivery": (order.estimated_delivery.strftime("%d %b %Y, %I:%M %p") if order.estimated_delivery else None),
            "carrier":order.courier_name,
            "tracking_number":order.tracking_number,
            "refund_status":order.refund_status,
            "return_eligible":return_eligible
        }
    except Exception as e:
        logger.error(f"order error:{e}",exc_info=True)
        return {"error": "Internal server error"}