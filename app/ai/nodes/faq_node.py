from langchain_core.messages import AIMessage

from app.ai.state import AgentState
from app.core.logging import get_logger
from app.rag.generator import generate_rag_response

logger = get_logger(__name__)


async def faq_node(state: AgentState) -> dict:
    if not state.messages:
        reply = "ℹ️ Ask me any question about shipping, returns, payments, or policies."
        return {"response": reply, "messages": [AIMessage(content=reply)]}

    last_msg = state.messages[-1].content
    try:
        answer = await generate_rag_response(last_msg)
    except Exception as e:
        logger.error(f"faq_node error: {e}", exc_info=True)
        answer = (
            "I'm having trouble accessing the knowledge base right now. "
            "Please try again in a moment."
        )

    reply = f"ℹ️ {answer}"
    return {"response": reply, "messages": [AIMessage(content=reply)]}
