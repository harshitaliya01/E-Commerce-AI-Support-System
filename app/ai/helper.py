import re
from typing import Literal

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def extract_order_id(last_msg: str | None) -> str | None:
    """Extract normalized order id (ORD-###) from user text."""
    if not last_msg or not isinstance(last_msg, str):
        return None
    match = re.search(r"(?:ORD[- ]?)?(\d{5,})", last_msg, re.IGNORECASE)
    if match:
        order_num = match.group(1).zfill(3)
        return f"ORD-{order_num}"
    return None


def user_confirmed(msg: str) -> bool:
    """True when the user agrees to escalate or confirm an action."""
    lower = msg.lower().strip()
    return any(token in lower for token in ("yes", "confirm", "yep", "sure", "go ahead", "please do"))


def normalize_order_id(raw: str | None) -> str | None:
    """Normalize LLM- or user-provided order id to ORD-### format."""
    if not raw:
        return None
    return extract_order_id(raw) or raw.strip().upper()


_llm = ChatOpenAI(
    base_url=settings.BASE_URL,
    model=settings.STRUCTURE_MODEL,
    api_key=settings.OPENAI_API_KEY,
    temperature=0.2,
)


class EscalationDecision(BaseModel):
    action: Literal["required", "not_required"]
    issue: str | None = Field(
        default=None,
        description="Brief issue summary if escalation needed",
    )


decision_llm = _llm.with_structured_output(EscalationDecision)

DECISION_PROMPT = """
You are an ecommerce support supervisor.

Decide if a human support ticket should be created.

Escalation REQUIRED when:
- customer repeatedly says issue not solved
- angry/frustrated customer
- refund/payment still failing
- missing package
- security issue
- customer explicitly asks for human
- bot cannot solve issue

Escalation NOT REQUIRED when:
- issue already resolved
- tracking/payment/refund info answered successfully
- user says thanks/ok/fixed

Return only structured output.
"""


async def review_decision_node(conversation: str) -> dict:
    if not conversation or not conversation.strip():
        return {"action": "not_required", "issue": None}

    try:
        response = await decision_llm.ainvoke(
            [
                SystemMessage(content=DECISION_PROMPT),
                HumanMessage(content=conversation),
            ]
        )
        issue = response.issue
        if response.action == "required" and not issue:
            issue = "Customer issue requires human review"
        return {"action": response.action, "issue": issue}
    except Exception as e:
        logger.error(f"review_decision_node error: {e}", exc_info=True)
        return {"action": "required", "issue": "Unable to determine issue"}

def ticket_failure_reply(result: dict) -> str:
    return f"❌ {result.get('error', 'Could not create support ticket. Please try again later.')}"

