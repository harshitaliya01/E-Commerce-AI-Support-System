# ─────────────────────────────────────────────────────
# Shared helper
# ─────────────────────────────────────────────────────
import re
from app.ai.state import AgentState


def extract_order_id(state: AgentState) -> str | None:
    """
    Extract order id from latest message.
    Falls back to previously stored state.order_id
    """

    last_msg = state.messages[-1].content

    match = re.search(
        r"(?:ORD[- ]?)?(\d+)",
        last_msg,
        re.IGNORECASE
    )

    if match:
        order_num = match.group(1).zfill(3)
        return f"ORD-{order_num}"

    if state.order_id:
        return state.order_id
