from typing import Annotated, Literal, Optional
from pydantic import BaseModel
from langgraph.graph.message import add_messages


# ── Intent labels the router assigns ──────────────────────────────────────────
Intent = Literal[
    "order_tracking",
    "return_refund",
    "payment_issue",
    "delivery_update",
    "product_recommendation",
    "faq",
    "escalate_human",
    "out_of_scope",
]


# ── Per-turn agent state (persisted across the graph nodes) ───────────────────
class AgentState(BaseModel):
    # Full conversation history (LangGraph merges lists automatically)
    messages: Annotated[list, add_messages] = []

    # Detected intent for the current turn
    intent: Optional[Intent] = None

    # Customer / order context resolved from DB (injected by tools)
    order_id: Optional[str] = None
    order_status: Optional[str] = None
    order_items: Optional[list[dict]] = None
    payment_status: Optional[str] = None
    return_eligible: Optional[bool] = None

    # Whether the conversation has been escalated to a human agent
    escalation_ticket_created: bool = False

    # Final reply text produced by this turn
    response: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True