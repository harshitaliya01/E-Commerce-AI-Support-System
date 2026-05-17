from __future__ import annotations

import json

from redis.asyncio import Redis

from langchain_core.messages import (
    BaseMessage,
    messages_from_dict,
    messages_to_dict,
)


REDIS_URL="redis://localhost:6379"

# temporary memory → 5 min
MEMORY_TTL = 60 * 5

redis_client=Redis.from_url(
    REDIS_URL,
    decode_responses=True
)


def session_key(
    session_id:str
)->str:

    return f"chat_session:{session_id}"


async def get_history(
    session_id:str
)->list[BaseMessage]:

    data=await redis_client.get(
        session_key(session_id)
    )

    if not data:
        return []

    return messages_from_dict(
        json.loads(data)
    )


async def save_history(
    session_id:str,
    messages:list[BaseMessage]
)->None:

    serialized=messages_to_dict(
        messages
    )

    await redis_client.setex(
        session_key(session_id),
        MEMORY_TTL,
        json.dumps(serialized)
    )


async def clear_session(
    session_id:str
)->None:

    await redis_client.delete(
        session_key(session_id)
    )


async def save_state(
    session_id:str,
    state:dict
):
    await redis_client.setex(
        f"state:{session_id}",
        MEMORY_TTL,
        json.dumps(state)
    )


async def get_state(
    session_id:str
):
    data=await redis_client.get(
        f"state:{session_id}"
    )

    return json.loads(data) if data else {}