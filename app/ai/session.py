from __future__ import annotations

import json

from redis.asyncio import Redis

from langchain_core.messages import (
    BaseMessage,
    messages_from_dict,
    messages_to_dict,
)
from app.core.logging import get_logger

logger = get_logger(__name__)

REDIS_URL="redis://localhost:6379"

# temporary memory → 1 hour
MEMORY_TTL = 60 * 60

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
    try:
        data=await redis_client.get(
            session_key(session_id)
        )
    
        if not data:
            return []
    
        return messages_from_dict(
            json.loads(data)
        )
    except Exception as e:
        logger.error(f"Error getting history for {session_id}: {e}", exc_info=True)
        return []


async def save_history(
    session_id:str,
    messages:list[BaseMessage]
)->None:
    try:
        serialized=messages_to_dict(
            messages
        )
    
        await redis_client.setex(
            session_key(session_id),
            MEMORY_TTL,
            json.dumps(serialized)
        )
    except Exception as e:
        logger.error(f"Error saving history for {session_id}: {e}", exc_info=True)


async def clear_session(
    session_id:str
)->None:
    try:
        await redis_client.delete(
            session_key(session_id)
        )
    except Exception as e:
        logger.error(f"Error clearing session {session_id}: {e}", exc_info=True)


async def save_state(
    session_id:str,
    state:dict
):
    try:
        await redis_client.setex(
            f"state:{session_id}",
            MEMORY_TTL,
            json.dumps(state)
        )
    except Exception as e:
        logger.error(f"Error saving state for {session_id}: {e}", exc_info=True)


async def get_state(
    session_id:str
):
    try:
        data=await redis_client.get(
            f"state:{session_id}"
        )
    
        return json.loads(data) if data else {}
    except Exception as e:
        logger.error(f"Error getting state for {session_id}: {e}", exc_info=True)
        return {}