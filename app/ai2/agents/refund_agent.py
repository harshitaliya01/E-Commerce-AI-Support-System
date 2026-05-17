from datetime import datetime

from sqlalchemy import select

from langchain_core.tools import tool

from app.orders.models import Order
from app.core.logging import get_logger

logger = get_logger(__name__)

@tool
async def handle_refund(user_id:int,order_id:int):    

    """ 
    Handles refund requests for users.

    Args:
        user_id: The ID of the user.
        order_id: The ID of the order.

    Returns:
        A success message with the refund request status.
    """

    # order=(
    #     await db.execute(
    #         select(Order).where(
    #             Order.id==order_id,
    #             Order.user_id==user_id
    #         )
    #     )
    # ).scalar_one_or_none()
    logger.info(
        f"Tracking order {order_id} for user {user_id}"
    )
    Order= {
        "product_name":"Laptop",
        "order_status":"Shipped",
        "payment_status":"Paid",
        "tracking_number":"123456789",
        "estimated_delivery":"2022-01-01",
        "total_amount":100000,
        "refund_status":"pending",
        "refund_window_days":7
    }
    
    if not Order:

        return "Order not found"

    if Order["order_status"] =="cancelled":

        return (
            "Cancelled orders "
            "cannot be refunded"
        )

    if Order["refund_status"]:

        return (
            f"Refund already refunded"
        )


    if not Order["estimated_delivery"]:

        return (
            "Refund available "
            "after delivery"
        )


    days=(
        datetime.utcnow()-
        Order["estimated_delivery"]
    ).days


    if days>Order["refund_window_days"]:    

        return (
            "Refund window expired"
        )


    # Order["refund_status"]="pending"

    # await db.commit()

    return (
        "Refund request created. "
        "Pickup will be scheduled "
        "within 24 hours."
    )