from langchain_core.messages import AIMessage

from app.ai.helper import (
    extract_order_id,
    review_decision_node,
    ticket_failure_reply,
    user_confirmed,
)
from app.ai.state import AgentState
from app.services.create_support_tickets import create_support_ticket
from app.services.order_details import get_order_details


async def order_tracking_node(state: AgentState) -> dict:
    if not state.messages:
        reply = "Please send a message so I can help you track your order."
        return {"response": reply, "messages": [AIMessage(content=reply)]}

    last_msg = state.messages[-1].content
    order_id = state.order_id or extract_order_id(last_msg)

    if not order_id:
        reply = (
            "I'd love to help you track your order! "
            "Could you please share your **Order ID**? "
            "You can find it in your order confirmation email or the 'My Orders' section."
        )
        return {"response": reply, "messages": [AIMessage(content=reply)]}

    if state.ticket_created:
        reply = (
            "🙋 Your support request is already assigned.\n\n"
            "Our team will contact you shortly."
        )
        return {"response": reply, "messages": [AIMessage(content=reply)]}

    if state.track_order:
        conversation = "\n".join(
            f"{m.type}: {m.content}" for m in state.messages[-5:] if getattr(m, "content", None)
        )
        decision = await review_decision_node(conversation)
        if decision["action"] == "required":
            issue = decision.get("issue") or "Order tracking issue"
            if not user_confirmed(last_msg):
                reply = (
                    "It looks like this may need help from a support specialist.\n\n"
                    "Would you like me to create a ticket and connect you with a human agent? Reply **Yes**."
                )
                return {"response": reply, "messages": [AIMessage(content=reply)]}

            result = await create_support_ticket(issue, order_id, "order")
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
            "Glad I could help with your order! "
            "If anything else comes up about this shipment, just let me know."
        )
        return {"response": reply, "messages": [AIMessage(content=reply)]}

    data = await get_order_details(order_id)

    if "error" in data:
        reply = f"❌ {data['error']}"
        updates = {"response": reply, "messages": [AIMessage(content=reply)]}
        if data.get("clear_order"):
            updates["order_id"] = None
        return updates

    items_str = ", ".join(f"{i['name']} (x{i['qty']})" for i in data["items"])
    reply = (
        f"📦 **Order {data['order_id']} Status**\n\n"
        f"**Status:** {data['status']}\n"
        f"**Items:** {items_str}\n"
        f"**Estimated Delivery:** {data['estimated_delivery']}\n"
        f"**Carrier:** {data.get('carrier', 'TBD')}\n"
        "Is there anything else I can help you with?"
    )

    return {
        "order_id": order_id,
        "track_order": True,
        "response": reply,
        "messages": [AIMessage(content=reply)],
    }
