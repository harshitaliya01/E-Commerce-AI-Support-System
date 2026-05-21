from langchain_core.messages import AIMessage

from app.ai.helper import (
    extract_order_id,
    review_decision_node,
    ticket_failure_reply,
    user_confirmed,
)
from app.ai.state import AgentState
from app.services.create_support_tickets import create_support_ticket
from app.services.initiate_return import initiate_return
from app.services.order_details import get_order_details


async def return_refund_node(state: AgentState) -> dict:
    if not state.messages:
        reply = "Please share your Order ID for return or refund help."
        return {"response": reply, "messages": [AIMessage(content=reply)]}

    last_msg = state.messages[-1].content
    order_id = state.order_id or extract_order_id(last_msg)

    if not order_id:
        reply = (
            "I can help you with a return or refund query. "
            "Please share your **Order ID** so I can check eligibility right away."
        )
        return {"response": reply, "messages": [AIMessage(content=reply)]}

    if state.ticket_created:
        reply = (
            "🙋 Your case is already open with our team.\n\n"
            "You'll hear back within 2 hours — thank you for your patience."
        )
        return {"response": reply, "messages": [AIMessage(content=reply)]}

    if state.track_return:
        conversation = "\n".join(
            f"{m.type}: {m.content}" for m in state.messages[-5:] if getattr(m, "content", None)
        )
        decision = await review_decision_node(conversation)
        if decision["action"] == "required":
            issue = decision.get("issue") or "Return/refund issue"
            if not user_confirmed(last_msg):
                reply = (
                    "It looks like this may need help from a support specialist.\n\n"
                    "Would you like me to create a ticket and connect you with a human agent? Reply **Yes**."
                )
                return {"response": reply, "messages": [AIMessage(content=reply)]}

            result = await create_support_ticket(issue, order_id, "return_refund")
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
            "Thanks for the details. If you still need help with your return or refund, "
            "let me know what is wrong and I will check again."
        )
        return {"response": reply, "messages": [AIMessage(content=reply)]}

    order_data = await get_order_details(order_id)
    if "error" in order_data:
        reply = f"❌ {order_data['error']}"
        return {"order_id": None, "response": reply, "messages": [AIMessage(content=reply)]}
    
    if order_data["refund_status"] is None:
        if order_data["status"] != "delivered":
            reply = (
                f"⚠️ Order {order_id} has not been delivered yet.\n\n"
                "Returns and refunds can only be requested after delivery."
            )
            return {
                "track_return": True,
                "order_id": order_id,
                "response": reply,
                "messages": [AIMessage(content=reply)],
            }

        if not order_data["return_eligible"]:
            reply = (
                f"⚠️ Unfortunately, **Order {order_id}** is no longer eligible for return.\n\n"
                "Our return window is **7 days** from delivery. "
                "If you believe this is an error or received a damaged item, "
                "I can escalate this to our support team immediately."
            )
            return {
                "track_return": True,
                "order_id": order_id,
                "response": reply,
                "messages": [AIMessage(content=reply)],
            }

        if not user_confirmed(last_msg):
            reply = (
                f"✅ **Order {order_id}** is eligible for a return/refund.\n\n"
                "Would you like me to initiate the return process now? "
                "Please reply with **'Yes, confirm return'** to proceed."
            )
            return {
                "track_return": True,
                "order_id": order_id,
                "response": reply,
                "messages": [AIMessage(content=reply)],
            }

        result = await initiate_return(order_id)
        if result.get("success"):
            reply = (
                "✅ **Return Initiated Successfully!**\n\n"
                f"🆔 Return ID: **{result['return_id']}**\n\n"
                f"{result['message']}\n\n"
                "Please keep the item ready in its original packaging for pickup."
            )
        else:
            reply = f"❌ {result.get('message', 'Could not initiate return.')}"
        return {
            "track_return": True,
            "order_id": order_id,
            "response": reply,
            "messages": [AIMessage(content=reply)],
        }
    refund_status = order_data.get("refund_status")
    if refund_status == "fully_refunded":
        amount = order_data["items"][0]["price"] if order_data.get("items") else "N/A"
        reply = (
            "✅ Refund completed successfully for your order.\n\n"
            f"📦 Order ID: {order_id} | Amount: {amount}\n"
            "❓ If you're still facing any issue, please briefly describe it."
        )
    elif refund_status == "requested":
        reply = (
            "💰 Your refund is currently being processed.\n\n"
            f"📦 Order: {order_id} | Refund Status: In Progress\n"
            "❓ Need help with anything else? Briefly describe the issue."
        )
    else:
        reply = (
            f"📦 Order {order_id} — refund status: **{refund_status}**.\n"
            "Tell me what problem you're seeing and I'll help."
        )

    return {
        "track_return": True,
        "order_id": order_id,
        "response": reply,
        "messages": [AIMessage(content=reply)],
    }
