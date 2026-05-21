from typing import Annotated, Literal, Optional
from pydantic import BaseModel
from langgraph.graph.message import add_messages


# ── Intent labels the router assigns ──────────────────────────────────────────
Intent = Literal[
    "unknown",
    "order_tracking",
    "return_refund",
    "payment_issue",
    "faq",
]


# ── Per-turn agent state (persisted across the graph nodes) ───────────────────
class AgentState(BaseModel):
    # Full conversation history (LangGraph merges lists automatically)
    messages: Annotated[list, add_messages] = []
    intent: Optional[Intent] = None

    order_id: Optional[str] = None

    ticket_created: bool=False
    track_order: bool=False
    track_payment: bool=False
    track_return: bool=False
    needs_review: bool=False

    response: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True