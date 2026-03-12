# backend/app/services/llm_router.py

from __future__ import annotations

from typing import Any

from app.constants import (
    CHECK_PAYMENT_STATUS,
    CREATE_PAYMENT_LINK,
    GET_RESERVE_BALANCE,
)

SUPPORTED_TOOLS = {
    CREATE_PAYMENT_LINK,
    CHECK_PAYMENT_STATUS,
    GET_RESERVE_BALANCE,
}


class LLMRouter:
    """
    Placeholder LLM router.

    Current behavior:
    - returns None, so the system continues using rule-based routing only.

    Later behavior:
    - call an LLM with a small intent-classification prompt
    - return one of the supported tool names
    """

    async def detect_intent(self, message: str) -> str | None:
        _ = message
        return None

    async def extract_tool_args(
        self,
        tool_name: str,
        message: str,
        session_state: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        _ = message
        _ = session_state

        if tool_name not in SUPPORTED_TOOLS:
            return {}

        return {}