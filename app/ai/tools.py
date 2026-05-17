"""
Real-world tools the agent nodes call.
Each tool is a plain async function. LangGraph nodes call them directly;
they can also be wrapped as OpenAI-compatible function-call tools.
"""
from __future__ import annotations

import random
import string
from datetime import datetime, timedelta
from typing import Optional

# ── Fake DB helpers (replace with real SQLAlchemy queries) ────────────────────
# In production: inject AsyncSession and do `await db.execute(select(Order)...)`


    # user_id
    # product_name
    # total_amount
    # order_status
    # tracking_number
    # estimated_delivery
    # payment_status
    # order_number
    # delivered_at
    # refund_window_days
    # refund_status
    # is_cancelled

    
_MOCK_ORDERS: dict[str, dict] = {
    "ORD-001": {
        "user_id": "USR-100",
        "status": "Out for delivery",
        "items": [{"name": "Wireless Headphones", "qty": 1, "price": 2499}],
        "estimated_delivery": (datetime.now() + timedelta(hours=3)).strftime("%d %b %Y, %I:%M %p"),
        "payment_status": "Paid",
        "return_eligible": True,
        "carrier": "Delhivery",
        "tracking_url": "https://www.delhivery.com/track/ORD-001",
    },
    "ORD-002": {
        "user_id": "USR-101",
        "status": "Delivered",
        "items": [{"name": "Men's Running Shoes", "qty": 1, "price": 1899}],
        "estimated_delivery": "Already delivered",
        "payment_status": "Paid",
        "return_eligible": False,   # 10-day window expired
        "carrier": "BlueDart",
        "tracking_url": "https://www.bluedart.com/track/ORD-002",
    },
    "ORD-003": {
        "user_id": "USR-102",
        "status": "Processing",
        "items": [{"name": "Smart Watch", "qty": 1, "price": 5999}],
        "estimated_delivery": (datetime.now() + timedelta(days=2)).strftime("%d %b %Y"),
        "payment_status": "Pending",
        "return_eligible": False,
        "carrier": None,
        "tracking_url": None,
    },
}


# ── Tool 1: Fetch order details ────────────────────────────────────────────────
async def get_order_details(order_id: str) -> dict:
    """Return order details dict or error."""
    order = _MOCK_ORDERS.get(order_id.upper())
    if not order:
        return {"error": f"Order {order_id} not found. Please check the order ID."}
    return {"order_id": order_id.upper(), **order}


# ── Tool 2: Initiate return / refund ──────────────────────────────────────────
async def initiate_return(order_id: str, reason: str) -> dict:
    """Attempt to create a return request."""
    order = _MOCK_ORDERS.get(order_id.upper())
    if not order:
        return {"success": False, "message": f"Order {order_id} not found."}
    if not order["return_eligible"]:
        return {
            "success": False,
            "message": (
                "This order is no longer eligible for return. "
                "The 7-day return window has expired or the item is non-returnable."
            ),
        }
    ref = "RET-" + "".join(random.choices(string.digits, k=6))
    return {
        "success": True,
        "return_id": ref,
        "message": (
            f"Return request {ref} created for order {order_id}. "
            f"You will receive a pickup confirmation within 24 hours. "
            f"Refund of ₹{order['items'][0]['price']} will be processed in 5–7 business days."
        ),
    }


# ── Tool 3: Escalate to human agent ───────────────────────────────────────────
async def escalate_to_human( issue_summary: str) -> dict:
    """Create a human-agent escalation ticket."""
    ticket_id = "TKT-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return {
        "ticket_id": ticket_id,
        "message": (
            f"Your issue has been escalated. Ticket ID: {ticket_id}. "
            f"A support agent will contact you within 2 hours via email/phone. "
            f"Issue summary: {issue_summary}"
        ),
    }


# ── Tool 4: Product recommendations ───────────────────────────────────────────
async def get_recommendations(category: str, budget: Optional[int] = None) -> list[dict]:
    """Return mock product recommendations."""
    catalogue = {
        "electronics": [
            {"name": "boAt Airdopes 141", "price": 999, "rating": 4.2},
            {"name": "Realme Buds Air 5", "price": 1799, "rating": 4.4},
            {"name": "JBL Tune 230NC", "price": 3499, "rating": 4.3},
        ],
        "shoes": [
            {"name": "Campus Men's Drift", "price": 799, "rating": 4.1},
            {"name": "Nike Air Max SC", "price": 4995, "rating": 4.5},
            {"name": "Puma Softride", "price": 2499, "rating": 4.3},
        ],
        "general": [
            {"name": "Philips Trimmer BT3231", "price": 699, "rating": 4.3},
            {"name": "Milton Thermosteel Flask", "price": 549, "rating": 4.4},
            {"name": "Prestige Iris 750W Mixer", "price": 2195, "rating": 4.2},
        ],
    }
    items = catalogue.get(category.lower(), catalogue["general"])
    if budget:
        items = [i for i in items if i["price"] <= budget] or items[:2]
    return items