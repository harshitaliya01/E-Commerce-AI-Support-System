from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.ai.state import AgentState


async def fallback_node(state: AgentState) -> dict:
    """Politely decline and redirect."""
    reply = (
        "I'm your e-commerce support assistant and can help with:\n\n"
        "📦 Order tracking  |  🔄 Returns & Refunds  |  💳 Payment Issues\n"
        "🚚 Delivery Updates  |  ❓ FAQs\n\n"
        "How can I assist you today?"
    )
    return {"response": reply, "messages": [AIMessage(content=reply)]}
