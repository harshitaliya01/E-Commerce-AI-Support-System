from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.logging import get_logger
from app.models.model import Order, Payment

logger = get_logger(__name__)


async def get_payment_details(order_number: str) -> dict:
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Order).where(Order.order_number == order_number.upper())
            )
            order = result.scalar_one_or_none()

            if not order:
                return {
                    "error": f"Order {order_number} not found",
                    "clear_order": True,
                }

            payment_result = await db.execute(
                select(Payment).where(Payment.order_id == order.id)
            )
            payment = payment_result.scalar_one_or_none()

            if not payment:
                return {"error": "No payment record found for this order."}

            return {
                "order_id": order.order_number,
                "status": payment.status,
                "method": payment.method,
                "amount": payment.amount,
                "transaction": payment.transaction_id,
                "created": payment.created_at,
            }
    except Exception as e:
        logger.error(f"payment details error: {e}", exc_info=True)
        return {"error": "Unable to fetch payment details. Please try again."}
