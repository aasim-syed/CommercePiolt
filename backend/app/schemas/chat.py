from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str | None = None
    merchant_id: str | None = None


class ToolCall(BaseModel):
    tool_name: str
    arguments: dict[str, Any]


class ChatResponse(BaseModel):
    reply: str
    tool_called: ToolCall | None = None
    data: dict[str, Any] | None = None
    session_state: dict[str, Any] | None = None
