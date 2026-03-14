from __future__ import annotations

import json
from typing import Any

from app.constants import (
    CHECK_PAYMENT_STATUS,
    CREATE_PAYMENT_LINK,
    GET_RESERVE_BALANCE,
)
from app.services.llm_client import LLMClient
from app.services.logger import get_logger

SUPPORTED_TOOLS = {
    CREATE_PAYMENT_LINK,
    CHECK_PAYMENT_STATUS,
    GET_RESERVE_BALANCE,
}

logger = get_logger("llm_router")


class LLMRouter:
    def __init__(self) -> None:
        self.client = LLMClient()

    async def detect_intent(self, message: str) -> str | None:
        try:
            intent = await self.client.classify_intent(message)
        except Exception:
            logger.exception(
                "llm_intent_detection_failed",
                extra={"extra_data": {"message": message}},
            )
            return None

        if intent not in SUPPORTED_TOOLS:
            return None

        return intent

    async def extract_tool_args(
        self,
        tool_name: str,
        message: str,
        session_state: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if tool_name not in SUPPORTED_TOOLS:
            return {}

        state = session_state or {}

        if tool_name == CREATE_PAYMENT_LINK:
            prompt = (
                "Extract arguments for tool create_payment_link.\n"
                "Return ONLY strict JSON.\n"
                "Do not include markdown. Do not include explanation.\n"
                '{"amount": number|null, "merchant_id": string|null}'
            )
        elif tool_name == CHECK_PAYMENT_STATUS:
            prompt = (
                "Extract arguments for tool check_payment_status.\n"
                "Return ONLY strict JSON.\n"
                "Do not include markdown. Do not include explanation.\n"
                '{"payment_ref": string|null}'
            )
        elif tool_name == GET_RESERVE_BALANCE:
            prompt = (
                "Extract arguments for tool get_reserve_balance.\n"
                "Return ONLY strict JSON.\n"
                "Do not include markdown. Do not include explanation.\n"
                '{"merchant_id": string|null}'
            )
        else:
            return {}

        user_payload = {
            "message": message,
            "session_state": {
                "merchant_id": state.get("merchant_id"),
                "last_payment_ref": state.get("last_payment_ref"),
                "last_order_id": state.get("last_order_id"),
                "last_payment_status": state.get("last_payment_status"),
            },
        }

        try:
            raw = await self.client.chat(
                [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": json.dumps(user_payload)},
                ]
            )
        except Exception:
            logger.exception(
                "llm_arg_extraction_failed",
                extra={
                    "extra_data": {
                        "tool_name": tool_name,
                        "message": message,
                    }
                },
            )
            return {}

        return self._safe_parse_json(raw)

    def _safe_parse_json(self, raw: str) -> dict[str, Any]:
        text = raw.strip()

        if text.startswith("```"):
            text = text.strip("`").strip()
            if text.lower().startswith("json"):
                text = text[4:].strip()

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return {}

        if not isinstance(parsed, dict):
            return {}

        return parsed