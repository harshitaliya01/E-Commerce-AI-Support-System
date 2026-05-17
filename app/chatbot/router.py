from fastapi import APIRouter
# from fastapi import Depends

# from sqlalchemy.ext.asyncio import AsyncSession

# from app.core.database import get_db
# from app.core.config import settings

# from app.auth.models import User
# from app.auth.dependencies import get_current_user

# from app.ai.workflow import chatbot

# from app.chatbot.memory_service import (
#     get_or_create_session,
#     save_message,
#     get_conversation_history
# )

router = APIRouter(
    prefix="/chat",
    tags=["AI Chatbot"],
)


# @router.post("/")
# async def ai_chat(
#     message: str,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db),
# ):

#     user_message = message

#     session = await get_or_create_session(db,
#         current_user.id
#   )

#     await save_message(
#         db,
#         session.id,
#         "user",
#         user_message
#     )

#     history = (
#         await get_conversation_history(
#             db,
#             session.id
#         )
#     )

#     response = await chatbot.ainvoke({
#         "message":user_message,
#         # "history":history
#     })

#     await save_message(
#         db,
#         session.id,
#         "assistant",
#         response["messages"][-1].content
#     )

#     return response["messages"][-1].content