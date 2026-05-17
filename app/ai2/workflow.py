# from langchain_openai import ChatOpenAI
# from langgraph.prebuilt import ToolNode, tools_condition
# from langgraph.graph import StateGraph,END, START
# from langchain_core.messages import SystemMessage, BaseMessage
# from app.core.config import settings
# from app.ai.agents.order_agent import handle_order_tracking
# from app.ai.agents.refund_agent import handle_refund
# from app.ai.agents.faq_agent import handle_faq
# from app.ai.agents.ticket_agent import create_ticket
# from typing import TypedDict, Annotated
# from langgraph.graph.message import add_messages

# llm= ChatOpenAI(
#     base_url= settings.BASE_URL,
#     api_key= settings.API_KEY,
#     model=settings.MODEL
# )
# tools=[handle_order_tracking,handle_refund,handle_faq,create_ticket]

# llm_with_tools=llm.bind_tools(tools)


# class ChatState(TypedDict):

#     messages: Annotated[
#         list[BaseMessage],
#         add_messages
#     ]

# async def chat_node(state:ChatState):
#     """LLM node that may answer or request a tool call."""

#     SYSTEM_PROMPT="""
# You are ShopAssist AI.

# Rules:

# Never invent order details

# Use tools before answering

# Track context from memory

# Escalate payment failures

# Escalate angry customers

# Create tickets automatically

# Support multilingual replies

# If confidence below 70%,
# escalate to human
# """

#     response=await llm_with_tools.ainvoke([SYSTEM_PROMPT]+state["messages"])

#     return {
#         "messages":[response]
#     }



# import os
# from dotenv import load_dotenv
# load_dotenv()
# llm= ChatOpenAI(
#     base_url= os.getenv("BASE_URL"),
#     api_key= os.getenv("API_KEY"),
#     model="openai/gpt-oss-20b",
#     temperature=0
# )

# from pydantic import BaseModel,Field
# from typing import Literal

# class IntentSchema(BaseModel):

#     intent:Literal[
#         "track_order",
#         "refund",
#         "complaint",
#         "faq",
#         "payment",
#         "multi_intent"
#     ]

#     reason:str=Field(
#         description="reason for selection"
#     )


# intent_llm=llm.with_structured_output(IntentSchema)



# def detect_intent(
#     state:State
# ):

#     user_query=(
#         state["messages"][-1]
#         .content
#     )

#     prompt=f"""
# You are ecommerce intent classifier.

# Allowed intents:

# track_order
# refund
# complaint
# faq
# payment
# multi_intent

# Rules:

# Tracking related →
# track_order

# Refund related →
# refund

# Complaint or issue →
# complaint

# Policies/questions →
# faq

# Payment issue →
# payment

# More than one request →
# multi_intent


# Query:

# {user_query}
# """

#     response=(
#         intent_llm.invoke(
#             prompt
#         )
#     )

#     print(response)

#     return {

#         "intent":
#         response.intent
#     }
