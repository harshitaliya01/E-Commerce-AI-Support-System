import uuid

from langchain_core.tools import tool

from app.tickets.models import (
    SupportTicket
)
from app.core.logging import get_logger

logger = get_logger(__name__)

@tool
async def create_ticket(user_id:int,issue:str,order_id:int|None):

    """
    Creates a new support ticket for a user.
    
    Args:
        user_id: The ID of the user.
        issue: The issue description.
        order_id: The ID of the order (optional).
        
    Returns:
        A success message with the ticket number.
    """
    
    ticket_no=(
        "SUP-"+
        str(uuid.uuid4())[:8]
    )

    ticket=SupportTicket(

        user_id=user_id,

        issue=issue,

        order_id=order_id,

        ticket_number=ticket_no
    )

    # db.add(ticket)

    # await db.commit()
    logger.info(
        f"Ticket created successfully"
        f"Ticket: {ticket_no}"
        f"User ID: {user_id}"
        f"Issue: {issue}"
        f"Order ID: {order_id}"
    )
    return (
        f"""
Ticket created successfully

Ticket:
{ticket_no}

Support team will contact you.
"""
    )