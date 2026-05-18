from app.ai.state import AgentState, Intent
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from app.core.config import settings
from pydantic import BaseModel, Field

_llm = ChatOpenAI(
    base_url=settings.BASE_URL,
    model=settings.STRUCTURE_MODEL,
    api_key=settings.OPENAI_API_KEY,
    temperature=0.3,
)

_INTENT_SYSTEM = """
Classify the user's intent.

Rules:

- Greetings like:
  hi
  hello
  hy
  hey
  good morning

→ greeting

- Use previous USER messages for context if latest message is short:
  yes
  no
  345
  tomorrow
  refund

Valid intents:
- greeting
- order_tracking
- return_refund
- payment_issue
- faq
- escalate_human
- out_of_scope
"""

class IntentSchema(BaseModel):

    intent: Intent

    reason:str=Field(
        description="reason for selection"
    )

intent_llm=_llm.with_structured_output(IntentSchema)

async def intent_router_node(state: AgentState) -> dict:
    conversation = "\n".join([f"{m.type}: {m.content}" for m in state.messages[-4:]])

    response= await intent_llm.ainvoke([
        SystemMessage(content=_INTENT_SYSTEM),
        HumanMessage(content=conversation),
    ])
    print("intent: ",response.intent)
    return {
        "intent":
        response.intent
    }