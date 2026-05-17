# from langchain_openai import ChatOpenAI
# from langchain_core.messages import SystemMessage, HumanMessage
# from app.core.config import settings

# # LangChain instance initialized with your custom config variables
# llm = ChatOpenAI(
#     base_url=settings.BASE_URL,
#     # api_key=settings.API_KEY,
#     model=settings.MODEL  # This will use the model specified in your settings
# )


# async def stream_ai_response(user_message: str):
#     # Construct standard LangChain structural messages
#     messages = [
#         SystemMessage(content="You are an ecommerce support AI assistant."),
#         HumanMessage(content=user_message),
#     ]

#     # Stream async chunks natively using LangChain's .astream interface
#     async for chunk in llm.astream(messages):
#         # LangChain automatically strips structure; chunk.content is directly accessible
#         if chunk.content:
#             yield chunk.content
