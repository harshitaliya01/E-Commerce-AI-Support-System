import random
import string
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.model import Order, SupportTicket
from app.core.logging import get_logger

logger = get_logger(__name__)

async def create_support_ticket(issue: str, order_id: str, category: str = "general") -> dict:
    if not issue or not str(issue).strip():
        issue = "Customer requested support"
    if not order_id:
        return {"success": False, "error": "Order ID is required to create a support ticket."}

    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Order).where(Order.order_number == order_id.upper())
            )
            order = result.scalar_one_or_none()
            if not order:
                return {
                    "success": False,
                    "error": f"Order number {order_id} not found.",
                }

            user_id = order.user_id
            db_order_id = order.id

            existing = await db.execute(
                select(SupportTicket).where(
                    SupportTicket.order_id == db_order_id
                )
            )
            if existing.scalar_one_or_none():
                return {
                    "success": True,
                    "message": (
                        "🙋 Your support request is already assigned.\n"
                        "Our team will contact you shortly. "
                        "A support agent will contact you within 2 hours."
                    ),
                }
            ticket_number = (
                "TKT-"
                + "".join(
                    random.choices(
                        string.ascii_uppercase + string.digits,
                        k=8
                    )
                )
            )
            ticket = SupportTicket(
                ticket_number=ticket_number,
                user_id= user_id,
                order_id=order.id,
                issue=issue,
                category=category,
                status="open",
            )

            db.add(ticket)
            await db.commit()
            await db.refresh(ticket)

            return {
                "success": True,
                "ticket_id": ticket.ticket_number,
                "message": (
                    f"🎫 Your issue has been escalated. "
                    f"Ticket ID: {ticket.ticket_number}. "
                    f"A support agent will contact you within 2 hours."
                ),
            }

    except Exception as e:
        logger.error(
            f"ticket creation error: {e}",
            exc_info=True
        )

        return {
            "success": False,
            "error": "Failed to create support ticket"
        }