from __future__ import annotations

from typing import Any

from app.constants import (
    CHECK_PAYMENT_STATUS,
    CREATE_PAYMENT_LINK,
    GET_RESERVE_BALANCE,
)
from app.services.llm_client import LLMClient

SUPPORTED_TOOLS = {
    CREATE_PAYMENT_LINK,
    CHECK_PAYMENT_STATUS,
    GET_RESERVE_BALANCE,
}


class LLMRouter:
    def __init__(self) -> None:
        self.client = LLMClient()

    async def detect_intent(self, message: str) -> str | None:
        intent = await self.client.classify_intent(message)
        if intent not in SUPPORTED_TOOLS:
            return None
        return intent

    async def extract_tool_args(
        self,
        tool_name: str,
        message: str,
        session_state: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        _ = tool_name
        _ = message
        _ = session_state
        return {}