from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SessionState(BaseModel):
    merchant_id: str | None = None
    last_payment_ref: str | None = None
    last_order_id: str | None = None
    last_tool_call: str | None = None


class RouteResolution(BaseModel):
    intent: str | None = None
    source: str = Field(default="none")
    args: dict[str, Any] = Field(default_factory=dict)


class ToolExecutionResult(BaseModel):
    tool_name: str
    arguments: dict[str, Any]
    result: dict[str, Any] | None = None


class AgentResponse(BaseModel):
    reply: str
    tool_execution: ToolExecutionResult | None = None
    session_state: SessionState