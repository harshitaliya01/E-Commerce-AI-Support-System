"""
LangGraph nodes — each node is an async function that receives AgentState
and returns a partial state dict to merge.
"""
from __future__ import annotations

import re

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.ai.state import AgentState, Intent
from app.ai.tools import (
    escalate_to_human,
    get_recommendations,
)

from app.services.order_service import get_order_details, initiate_return
from app.ai.helper import extract_order_id
# ── Shared LLM ────────────────────────────────────────────────────────────────
_llm = ChatOpenAI(
    base_url=settings.BASE_URL,
    model=settings.OPENAI_MODEL,
    api_key=settings.OPENAI_API_KEY,
    temperature=0.3,
)

# ─────────────────────────────────────────────────────────────────────────────
# NODE 4 — Return & Refund
# ─────────────────────────────────────────────────────────────────────────────
async def return_refund_node(state: AgentState) -> dict:
    """Handle return / refund requests end-to-end."""
    last_msg = state.messages[-1].content

    match = re.search(r"(ORD[-\s]?\d+)", last_msg, re.IGNORECASE)
    order_id = extract_order_id(state)

    if not order_id:
        reply = (
            "I can help you with a return or refund. "
            "Please share your **Order ID** so I can check eligibility right away."
        )
        return {"response": reply, "messages": [AIMessage(content=reply)]}

    # First confirm eligibility
    order_data = await get_order_details(order_id)
    if "error" in order_data:
        reply = f"❌ {order_data['error']}"
        return {"response": reply, "messages": [AIMessage(content=reply)]}

    if not order_data.get("return_eligible"):
        reply = (
            f"⚠️ Unfortunately, **Order {order_id}** is no longer eligible for return.\n\n"
            f"Our return window is **7 days** from delivery. "
            f"If you believe this is an error or received a damaged item, "
            f"I can escalate this to our support team immediately."
        )
        return {"response": reply, "messages": [AIMessage(content=reply)]}

    # Initiate return
    result = await initiate_return(order_id)
    # result = await initiate_return(order_id, reason="Customer requested via chatbot")
    if result["success"]:
        reply = (
            f"✅ **Return Initiated Successfully!**\n\n"
            f"🆔 Return ID: **{result['return_id']}**\n\n"
            f"{result['message']}\n\n"
            f"Please keep the item ready in its original packaging for pickup."
        )
    else:
        reply = f"❌ {result['message']}"

    return {
        "order_id": order_id,
        "return_eligible": order_data.get("return_eligible"),
        "response": reply,
        "messages": [AIMessage(content=reply)],
    }


# ─────────────────────────────────────────────────────────────────────────────
# NODE 5 — Payment Issue
# ─────────────────────────────────────────────────────────────────────────────
_PAYMENT_SYSTEM = """
You are a payment support specialist for an Indian e-commerce platform (like Amazon/Flipkart).
Help the customer resolve their payment issue clearly and concisely.
Mention common solutions: retry after 30 min, check bank statement, contact bank,
or raise a ticket. Be empathetic. Use ₹ for currency. Keep it under 100 words.
"""


async def payment_issue_node(state: AgentState) -> dict:
    """Resolve payment-related queries using LLM."""
    messages = [SystemMessage(content=_PAYMENT_SYSTEM)] + [
        HumanMessage(content=m.content) if m.type == "human" else AIMessage(content=m.content)
        for m in state.messages[-6:]  # last 3 turns for context
    ]
    result = await _llm.ainvoke(messages)
    reply = result.content.strip()
    return {"response": reply, "messages": [AIMessage(content=reply)]}


# ─────────────────────────────────────────────────────────────────────────────
# NODE 6 — Delivery Update
# ─────────────────────────────────────────────────────────────────────────────
async def delivery_update_node(state: AgentState) -> dict:
    """Provide delivery updates using order data."""
    last_msg = state.messages[-1].content
    match = re.search(r"(ORD[-\s]?\d+)", last_msg, re.IGNORECASE)
    order_id = extract_order_id(state)

    if not order_id:
        reply = (
            "To check your delivery update, please provide your **Order ID**. "
            "You'll find it in your order confirmation email."
        )
        return {"response": reply, "messages": [AIMessage(content=reply)]}

    data = await get_order_details(order_id)
    if "error" in data:
        reply = f"❌ {data['error']}"
    else:
        reply = (
            f"🚚 **Delivery Update for Order {order_id}**\n\n"
            f"**Current Status:** {data['status']}\n"
            f"**Expected By:** {data['estimated_delivery']}\n"
            f"**Carrier:** {data.get('carrier', 'Not yet assigned')}\n\n"
            + (
                f"📍 [Live Tracking]({data['tracking_url']})"
                if data.get("tracking_url")
                else "Live tracking will be activated once your order is shipped."
            )
        )
    return {"response": reply, "messages": [AIMessage(content=reply)]}


# ─────────────────────────────────────────────────────────────────────────────
# NODE 7 — Product Recommendation
# ─────────────────────────────────────────────────────────────────────────────
async def product_recommendation_node(state: AgentState) -> dict:
    """Extract category/budget and return curated recommendations."""
    last_msg = state.messages[-1].content.lower()

    # Detect category
    category = "general"
    if any(w in last_msg for w in ["headphone", "earphone", "electronic", "gadget", "watch"]):
        category = "electronics"
    elif any(w in last_msg for w in ["shoe", "footwear", "sneaker", "boot"]):
        category = "shoes"

    # Detect budget (₹ or Rs or just a number)
    budget_match = re.search(r"(?:₹|rs\.?\s*|under\s*)(\d+)", last_msg)
    budget = int(budget_match.group(1)) if budget_match else None

    products = await get_recommendations(category, budget)
    lines = "\n".join(
        f"• **{p['name']}** — ₹{p['price']} ⭐ {p['rating']}"
        for p in products
    )
    budget_str = f" under ₹{budget}" if budget else ""
    reply = (
        f"🛍️ Here are my top picks for **{category}{budget_str}**:\n\n"
        f"{lines}\n\n"
        f"Want more details or comparisons on any of these?"
    )
    return {"response": reply, "messages": [AIMessage(content=reply)]}

# ─────────────────────────────────────────────────────────────────────────────
# NODE 9 — Escalate to Human
# ─────────────────────────────────────────────────────────────────────────────
async def escalate_node(state: AgentState) -> dict:
    """Create escalation ticket and inform the user."""

    if state.escalation_ticket_created:
        reply = (
            "🙋 Your support request is already assigned.\n\n"
            "Our team will contact you shortly."
        )

        return {
            "response": reply,
            "messages": [AIMessage(content=reply)],
        }
    
    last_msg = state.messages[-1].content

    result = await escalate_to_human(
        issue_summary=last_msg[:200],
    )
    reply = (
        f"🙋 **Connecting you to a human agent...**\n\n"
        f"🎫 {result['message']}\n\n"
        f"Thank you for your patience. Our team is here to help!"
    )
    return {
        "escalated": True,
        "escalation_ticket_created": True,
        "response": reply,
        "messages": [AIMessage(content=reply)],
    }


# ─────────────────────────────────────────────────────────────────────────────
# NODE 10 — Out of Scope / Fallback
# ─────────────────────────────────────────────────────────────────────────────
async def fallback_node(state: AgentState) -> dict:
    """Politely decline and redirect."""
    reply = (
        "I'm your e-commerce support assistant and can help with:\n\n"
        "📦 Order tracking  |  🔄 Returns & Refunds  |  💳 Payment Issues\n"
        "🚚 Delivery Updates  |  🛍️ Product Recommendations  |  ❓ FAQs\n\n"
        "How can I assist you today?"
    )
    return {"response": reply, "messages": [AIMessage(content=reply)]}