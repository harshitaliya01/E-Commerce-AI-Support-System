from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
import asyncio
import json

from app.chatbot.schemas import ChatRequest
from app.ai.graph import agent
from app.ai.state import AgentState
from app.services.redis_service import get_history, save_history, get_state, save_state, clear_session
from app.core.logging import get_logger

from app.core.limiter import limiter

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/chatbot", tags=["Chatbot"])


# ── POST /chat/stream  — streaming response (SSE) ────────────────────────────
@router.post("/chat/stream")
@limiter.limit("15/minute")
async def chat_stream(req: ChatRequest, request: Request):
    async def event_generator():
        try:
            history = await get_history(req.session_id) or []
            new_message = HumanMessage(content=req.message)
            saved_state = await get_state(req.session_id) or {}
            logger.debug(f"saved state: {saved_state}")

            state_fields = set(AgentState.model_fields)
            persisted = {k: v for k, v in saved_state.items() if k in state_fields}
            initial_state = AgentState(
                messages=history + [new_message],
                **persisted,
            )

            result = await agent.ainvoke(initial_state)
            final_state = AgentState(**result)
            await save_state(
                req.session_id,
                {
                    "order_id": final_state.order_id,
                    "ticket_created": final_state.ticket_created,
                    "track_order": final_state.track_order,
                    "track_payment": final_state.track_payment,
                    "track_return": final_state.track_return,
                },
            )

            await save_history(req.session_id, final_state.messages)
            reply = final_state.response or "Sorry, I could not process that."
            # Stream word by word
            for char in reply:
                chunk = {"token": char}
                yield f"data: {json.dumps(chunk)}\n\n"
                await asyncio.sleep(0.005)  # simulate streaming delay

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