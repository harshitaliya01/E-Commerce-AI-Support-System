from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect

from app.websocket.manager import (
    ConnectionManager
)

from app.websocket.streaming import (
    stream_ai_response
)


router = APIRouter()

manager = ConnectionManager()


@router.websocket("/ws/chat")
async def websocket_chat(
    websocket: WebSocket,
):

    await manager.connect(websocket)

    try:

        while True:

            user_message = (
                await websocket.receive_text()
            )

            await manager.send_message(
                "AI is typing...",
                websocket,
            )

            async for token in stream_ai_response(
                user_message
            ):

                await manager.send_message(
                    token,
                    websocket,
                )

            await manager.send_message(
                "\n\n[END]",
                websocket,
            )

    except WebSocketDisconnect:

        manager.disconnect(websocket)