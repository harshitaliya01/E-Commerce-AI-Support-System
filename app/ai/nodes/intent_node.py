from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from app.ai.helper import extract_order_id, normalize_order_id
from app.ai.state import AgentState, Intent
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_llm = ChatOpenAI(
    base_url=settings.BASE_URL,
    model=settings.STRUCTURE_MODEL,
    api_key=settings.OPENAI_API_KEY,
    temperature=0.3,
)

_INTENT_SYSTEM = """
    Classify the user's intent.
    Rules:
    - Unknown like:
    hi
    hello
    hy
    hey
    good morning
    anything without related to ecommerce
    → Unknown
    - Use previous USER messages for context if latest message is short:
    yes
    no
    345
    tomorrow
    refund
    Valid intents:
    - unknown
    - order_tracking
    - return_refund
    - payment_issue
    - faq
"""


class IntentSchema(BaseModel):
    intent: Intent
    order_id: str | None = Field(
        default=None,
        description="Order id mentioned by the user, if any",
    )


intent_llm = _llm.with_structured_output(IntentSchema)


async def intent_router_node(state: AgentState) -> dict:
    if not state.messages:
        return {"intent": "unknown"}

    conversation = "\n".join(
        f"{m.type}: {m.content}"
        for m in state.messages[-4:]
        if getattr(m, "content", None)
    )

    try:
        response = await intent_llm.ainvoke(
            [
                SystemMessage(content=_INTENT_SYSTEM),
                HumanMessage(content=conversation),
            ]
        )
        intent = response.intent
    except Exception as e:
        logger.error(f"intent_router_node error: {e}", exc_info=True)
        return {"intent": "unknown"}

    order_id = state.order_id
    if response.order_id:
        order_id = normalize_order_id(response.order_id) or order_id

    return {"intent": intent, "order_id": order_id}
