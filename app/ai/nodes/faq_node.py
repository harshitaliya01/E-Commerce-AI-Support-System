from app.ai.state import AgentState
from langchain_core.messages import AIMessage
from app.rag.generator import generate_rag_response

async def faq_node(state: AgentState) -> dict:
    last_msg = state.messages[-1].content
    """Answer FAQ from knowledge base, fallback to LLM."""
    answer= await generate_rag_response(last_msg)
    reply = f"ℹ️ {answer}"
    return {"response": reply, "messages": [AIMessage(content=reply)]}