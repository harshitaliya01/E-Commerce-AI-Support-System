from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
import asyncio
import json

from app.ai.schemas import ChatRequest, ChatResponse
from app.ai.graph import agent
from app.ai.state import AgentState
from app.ai.session import (
    get_history,
    save_history,
    get_state,
    save_state
)
from app.ai.session import clear_session
from app.core.logging import get_logger

from app.core.logging import get_logger
from app.core.limiter import limiter

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/chatbot", tags=["Chatbot"])


# ── POST /chat/stream  — streaming response (SSE) ────────────────────────────
@router.post("/chat/stream")
@limiter.limit("15/minute")
async def chat_stream(req: ChatRequest, request: Request):
    """
    Streaming version — returns Server-Sent Events (SSE).
    Useful for word-by-word rendering in the frontend.
    """
    async def event_generator():
        try:
            history = await get_history(req.session_id)
            new_message = HumanMessage(content=req.message)
            saved_state = await get_state(req.session_id)
            logger.debug(f"history: {history} ----------------New Message: {new_message} -----------------saved state: {saved_state}")
            initial_state = AgentState(
                **saved_state,
                messages=history+[new_message],
            )

            final_state= await agent.ainvoke(initial_state)
            final_state = AgentState(**final_state)
            await save_state(
                req.session_id,
                {
                    "order_id":final_state.order_id,
                    "escalation_ticket_created":
                        final_state.escalation_ticket_created
                }
            )

            await save_history(req.session_id, final_state.messages)

            reply = final_state.response or "Sorry, I could not process that."

            # Stream word by word
            for word in reply.split():
                chunk = {"token": word + " "}
                yield f"data: {json.dumps(chunk)}\n\n"
                await asyncio.sleep(0.005)  # simulate streaming delay

            # Final done event
            done_payload = {
                "done": True,
                "intent": final_state.intent,
                "escalation_ticket_created": final_state.escalation_ticket_created,
                "order_id": final_state.order_id,
            }
            yield f"data: {json.dumps(done_payload)}\n\n"

        except Exception as e:
            logger.error(f"Chat stream error: {e}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ── DELETE /session/{session_id}  — clear conversation history ────────────────
@router.delete("/session/{session_id}")
async def clear_chat_session(session_id: str):
    """Clear conversation history for a session."""
    try:
        await clear_session(session_id)
        logger.info(f"Session {session_id} cleared.")
        return {"message": f"Session {session_id} cleared."}
    except Exception as e:
        logger.error(f"Error clearing session {session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

# ── GET /health ───────────────────────────────────────────────────────────────
@router.get("/health")
async def health():
    try:
        return {"status": "ok", "agent": "langgraph-ecommerce-support"}
    except Exception as e:
        logger.error(f"Error in health check: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")