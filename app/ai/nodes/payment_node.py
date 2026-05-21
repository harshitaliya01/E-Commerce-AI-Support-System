from langchain_core.messages import AIMessage

from app.ai.helper import (
    extract_order_id,
    review_decision_node,
    ticket_failure_reply,
    user_confirmed,
)
from app.ai.state import AgentState
from app.services.create_support_tickets import create_support_ticket
from app.services.payment_details import get_payment_details


async def payment_issue_node(state: AgentState) -> dict:
    if not state.messages:
        reply = "Please share your message and Order ID so I can check payment status."
        return {"response": reply, "messages": [AIMessage(content=reply)]}

    last_msg = state.messages[-1].content
    order_id = state.order_id or extract_order_id(last_msg)

    if not order_id:
        reply = (
            "💳 I can help with payment issues.\n\n"
            "Please share your Order ID."
        )
        return {"response": reply, "messages": [AIMessage(content=reply)]}

    if state.ticket_created:
        reply = (
            "🙋 Your payment case is already open with our team.\n\n"
            "You'll hear back within 2 hours — thank you for your patience."
        )
        return {"response": reply, "messages": [AIMessage(content=reply)]}

    if state.track_payment:
        conversation = "\n".join(
            f"{m.type}: {m.content}" for m in state.messages[-5:] if getattr(m, "content", None)
        )
        decision = await review_decision_node(conversation)
        if decision["action"] == "required":
            issue = decision.get("issue") or "Payment issue"
            if not user_confirmed(last_msg):
                reply = (
                    "It looks like this may need help from a support specialist.\n\n"
                    "Would you like me to create a ticket and connect you with a human agent? Reply **Yes**."
                )
                return {"response": reply, "messages": [AIMessage(content=reply)]}

            result = await create_support_ticket(issue, order_id, "payment")
            if result.get("success"):
                ticket_msg = result["message"]
                return {
                    "ticket_created": True,
                    "response": ticket_msg,
                    "messages": [AIMessage(content=ticket_msg)],
                }
            reply = ticket_failure_reply(result)
            return {"response": reply, "messages": [AIMessage(content=reply)]}

        reply = (
            "Thanks for the update. If your payment still looks wrong, "
            "describe what you see and I'll review again."
        )
        return {"response": reply, "messages": [AIMessage(content=reply)]}

    payment = await get_payment_details(order_id)

    if "error" in payment:
        reply = f"❌ {payment['error']}"
        updates = {"response": reply, "messages": [AIMessage(content=reply)]}
        if payment.get("clear_order"):
            updates["order_id"] = None
        return updates

    status = payment.get("status")
    if status == "pending":
        reply = (
            f"⏳ **Payment processing** for **{payment['order_id']}**\n\n"
            f"Method: {payment['method']}\n"
            f"Amount: ₹{payment['amount']}\n\n"
            "Payments usually confirm within **5–15 minutes**.\n\n"
            "If money was already deducted but the order still shows pending, "
            "message me again and I will review whether a human agent is needed."
        )
    elif status == "completed":
        reply = (
            "✅ Payment received\n\n"
            f"Order: {payment['order_id']}\n"
            f"Amount: ₹{payment['amount']}\n"
            f"Method: {payment['method']}\n"
            f"Transaction: {payment['transaction']}\n\n"
            "Your payment was successful."
        )
    elif status == "failed":
        reply = (
            "❌ Payment failed\n\n"
            f"Method: {payment['method']}\n\n"
            "Common reasons:\n"
            "- insufficient balance\n"
            "- bank timeout\n"
            "- UPI issue\n\n"
            "Would you like to retry payment?"
        )
    elif status == "refunded":
        reply = (
            "💰 Refund completed\n\n"
            f"Amount: ₹{payment['amount']}\n\n"
            "Money should arrive in 3–7 business days."
        )
    else:
        reply = "Payment status is unavailable right now. Please try again shortly."

    return {
        "track_payment": True,
        "order_id": order_id,
        "response": reply,
        "messages": [AIMessage(content=reply)],
    }
