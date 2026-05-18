from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.ai.state import AgentState
from app.ai.tools import (
    escalate_to_human,
)

from app.services.order_service import get_order_details, initiate_return
from app.ai.helper import extract_order_id
# ── Shared LLM ────────────────────────────────────────────────────────────────
_llm = ChatOpenAI(
    base_url=settings.BASE_URL,
    model=settings.MODEL,
    api_key=settings.OPENAI_API_KEY,
    temperature=0.3,
)

# ─────────────────────────────────────────────────────────────────────────────
# NODE 4 — Return & Refund
# ─────────────────────────────────────────────────────────────────────────────
async def return_refund_node(state: AgentState) -> dict:
    """Handle return / refund requests end-to-end."""
    last_msg = state.messages[-1].content

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

    # Ask for confirmation before initiating
    msg_lower = last_msg.lower()
    if "confirm" not in msg_lower and "yes" not in msg_lower and "initiate" not in msg_lower:
        reply = (
            f"✅ **Order {order_id}** is eligible for a return/refund.\n\n"
            f"Would you like me to initiate the return process now? "
            f"Please reply with **'Yes, confirm return'** to proceed."
        )
        return {"response": reply, "messages": [AIMessage(content=reply)]}

    # Initiate return
    result = await initiate_return(order_id)
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


async def greeting_node(state: AgentState) -> dict:
    """Welcome the user and list capabilities."""
    reply = (
        "👋 **Hello! I'm your e-commerce support assistant.**\n\n"
        "I can help you with:\n"
        "📦 **Order tracking**\n"
        "🔄 **Returns & Refunds**\n"
        "💳 **Payment Issues**\n"
        "❓ **FAQs**\n\n"
        "How can I assist you today?"
    )
    return {"response": reply, "messages": [AIMessage(content=reply)]}