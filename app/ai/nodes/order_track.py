from langchain_core.messages import AIMessage
from app.ai.helper import extract_order_id
from app.ai.state import AgentState
from app.services.order_service import get_order_details


async def order_tracking_node(state: AgentState) -> dict:
    """Extract order ID from message, fetch order, compose reply."""
    
    # Extract order ID (e.g. ORD-001 or just 001)
    order_id = extract_order_id(state)

    if not order_id:
        reply = (
            "I'd love to help you track your order! "
            "Could you please share your **Order ID**? "
            "You can find it in your order confirmation email or the 'My Orders' section."
        )
        return {"response": reply, "messages": [AIMessage(content=reply)]}

    data = await get_order_details(order_id)

    if "error" in data:
        reply = f"❌ {data['error']}"
    else:
        items_str = ", ".join(f"{i['name']} (x{i['qty']})" for i in data["items"])
        tracking_line = (
            f"🔗 [Track here]({data['tracking_url']})" if data.get("tracking_url")
            else "Tracking link will be available once the order is shipped."
        )
        reply = (
            f"📦 **Order {data['order_id']} Status**\n\n"
            f"**Status:** {data['status']}\n"
            f"**Items:** {items_str}\n"
            f"**Estimated Delivery:** {data['estimated_delivery']}\n"
            f"**Carrier:** {data.get('carrier', 'TBD')}\n"
            f"{tracking_line}\n\n"
            f"Is there anything else I can help you with?"
        )

    return {
        "order_id": order_id,
        "order_status": data.get("status"),
        "response": reply,
        "messages": [AIMessage(content=reply)],
    }