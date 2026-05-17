from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    session_id: str = Field(..., description="Unique conversation session ID")
    order_id: Optional[str] = Field(None, description="Pre-filled order ID if known")


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    intent: Optional[str] = None
    escalated: bool = False
    order_id: Optional[str] = None