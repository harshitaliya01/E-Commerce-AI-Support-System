from sqlalchemy import select

from app.chatbot.models import (
    ChatSession,
    ChatMessage,
)


from sqlalchemy import select

from app.chatbot.models import (
    ChatSession,
)


async def get_or_create_session(
    db,
    user_id: int,
):

    query = select(ChatSession).where(
        ChatSession.user_id == user_id
    )

    result = await db.execute(query)

    session = result.scalar_one_or_none()

    if session:
        return session

    session = ChatSession(
        user_id=user_id
    )

    db.add(session)

    await db.commit()

    await db.refresh(session)

    return session


async def save_message(
    db,
    session_id: int,
    role: str,
    content: str,
):

    message = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
    )

    db.add(message)

    await db.commit()


async def get_conversation_history(
    db,
    session_id: int,
):

    query = select(ChatMessage).where(
        ChatMessage.session_id == session_id
    )

    result = await db.execute(query)

    messages = result.scalars().all()

    history = []

    for message in messages:

        history.append({

            "role": message.role,

            "message": message.content,
        })

    return history