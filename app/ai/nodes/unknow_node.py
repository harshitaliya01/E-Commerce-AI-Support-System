from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

from app.ai.state import AgentState
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_llm = ChatOpenAI(
    base_url=settings.BASE_URL,
    model=settings.STRUCTURE_MODEL,
    api_key=settings.OPENAI_API_KEY,
    temperature=0.2,
)

GREETING_PROMPT = """
You are a friendly ecommerce support assistant.
When users greet with messages like:
- hi
- hello
- hey
- good morning
- good evening
Reply warmly and briefly.
Introduce yourself as an ecommerce support assistant and explain what you can help with.
Mention these services:
📦 Order tracking
🔄 Returns & Refunds
💳 Payment Issues
❓ FAQs
Rules:
- Be friendly and professional
- Use emojis naturally
- Keep response under 5 lines
- End with a question encouraging the user to continue
"""

FALLBACK_REPLY = (
    "👋 **Hello! I'm your e-commerce support assistant.**\n\n"
    "I can help you with:\n"
    "📦 **Order tracking**\n"
    "🔄 **Returns & Refunds**\n"
    "💳 **Payment Issues**\n"
    "❓ **FAQs**\n\n"
    "How can I assist you today?"
)


async def unknown_node(state: AgentState) -> dict:
    if not state.messages:
        return {"response": FALLBACK_REPLY, "messages": [AIMessage(content=FALLBACK_REPLY)]}

    conversation = "\n".join(
        f"{m.type}: {m.content}" for m in state.messages[-2:] if getattr(m, "content", None)
    )
    try:
        response = await _llm.ainvoke(
            [SystemMessage(content=GREETING_PROMPT), HumanMessage(content=conversation)]
        )
        reply = response.content or FALLBACK_REPLY
        return {"response": reply, "messages": [AIMessage(content=reply)]}
    except Exception as e:
        logger.error(f"unknown_node error: {e}", exc_info=True)
        return {"response": FALLBACK_REPLY, "messages": [AIMessage(content=FALLBACK_REPLY)]}
