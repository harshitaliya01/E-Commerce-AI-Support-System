from fastapi import APIRouter, HTTPException
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
from app.ai.session import get_history, save_history, clear_session

router = APIRouter(prefix="/api/v1/chatbot", tags=["Chatbot"])


# ── POST /chat/stream  — streaming response (SSE) ────────────────────────────
@router.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    """
    Streaming version — returns Server-Sent Events (SSE).
    Useful for word-by-word rendering in the frontend.
    """
    async def event_generator():
        try:
            history = await get_history(req.session_id)
            new_message = HumanMessage(content=req.message)
            saved_state = await get_state(req.session_id)
            print(history,"--------------------------/n",[new_message])
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
                await asyncio.sleep(0.03)  # simulate streaming delay

            # Final done event
            done_payload = {
                "done": True,
                "intent": final_state.intent,
                "escalation_ticket_created": final_state.escalation_ticket_created,
                "order_id": final_state.order_id,
            }
            yield f"data: {json.dumps(done_payload)}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ── DELETE /session/{session_id}  — clear conversation history ────────────────
@router.delete("/session/{session_id}")
async def clear_chat_session(session_id: str):
    """Clear conversation history for a session."""
    clear_session(session_id)
    return {"message": f"Session {session_id} cleared."}


# ── GET /health ───────────────────────────────────────────────────────────────
@router.get("/health")
async def health():
    return {"status": "ok", "agent": "langgraph-ecommerce-support"}