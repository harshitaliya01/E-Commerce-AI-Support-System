from app.ai.state import AgentState, Intent
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from app.core.config import settings

_llm = ChatOpenAI(
    base_url=settings.BASE_URL,
    model=settings.OPENAI_MODEL,
    api_key=settings.OPENAI_API_KEY,
    temperature=0.3,
)

_INTENT_SYSTEM = """
You are an intent classifier for an e-commerce customer support chatbot.

You will receive the RECENT CONVERSATION, not only the latest message.

Infer the user's current intent using the whole conversation context.

Rules:
- If the user replies with short values like:
  "345"
  "yes"
  "cancel it"
  "tomorrow"
  "refund"
then use previous messages to determine intent.

Examples:

Conversation:
human: where is my order
ai: Please provide order ID
human: 345

Answer:
order_tracking

Conversation:
human: I want a refund
ai: Which order?
human: 345

Answer:
return_refund

Possible intents:

- order_tracking
- return_refund
- payment_issue
- delivery_update
- product_recommendation
- faq
- escalate_human
- out_of_scope

Reply ONLY the intent label.
"""


async def intent_router_node(state: AgentState) -> dict:
    """Classify user intent from the latest message."""
    conversation = "\n".join([f"{m.type}: {m.content}" for m in state.messages[-6:]])
    print("hello 1")
    result = await _llm.ainvoke([
        SystemMessage(content=_INTENT_SYSTEM),
        HumanMessage(content=conversation),
    ])
    print("hello 2")
    intent_raw = result.content.strip().lower().replace(" ", "_")
    valid: list[Intent] = [
        "order_tracking", "return_refund", "payment_issue",
        "delivery_update", "product_recommendation", "faq",
        "escalate_human", "out_of_scope",
    ]
    intent: Intent = intent_raw if intent_raw in valid else "out_of_scope"  # type: ignore
    return {"intent": intent}
