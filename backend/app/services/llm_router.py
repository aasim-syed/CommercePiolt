from __future__ import annotations

import json
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
        if tool_name not in SUPPORTED_TOOLS:
            return {}

        state = session_state or {}

        if tool_name == CREATE_PAYMENT_LINK:
            prompt = (
                "Extract arguments for tool create_payment_link.\n"
                "Return strict JSON only.\n"
                "Schema:\n"
                '{"amount": number|null, "merchant_id": string|null}\n'
                "Rules:\n"
                "- amount must be numeric if present\n"
                "- merchant_id can be null if not present in message\n"
                "- no explanation, no markdown"
            )

        elif tool_name == CHECK_PAYMENT_STATUS:
            prompt = (
                "Extract arguments for tool check_payment_status.\n"
                "Return strict JSON only.\n"
                "Schema:\n"
                '{"payment_ref": string|null}\n'
                "Rules:\n"
                "- payment_ref should look like pay_xxx if present\n"
                "- no explanation, no markdown"
            )

        elif tool_name == GET_RESERVE_BALANCE:
            prompt = (
                "Extract arguments for tool get_reserve_balance.\n"
                "Return strict JSON only.\n"
                "Schema:\n"
                '{"merchant_id": string|null}\n'
                "Rules:\n"
                "- merchant_id can be null if not present in message\n"
                "- no explanation, no markdown"
            )

        else:
            return {}

        user_payload = {
            "message": message,
            "session_state": {
                "merchant_id": state.get("merchant_id"),
                "last_payment_ref": state.get("last_payment_ref"),
                "last_order_id": state.get("last_order_id"),
            },
        }

        raw = await self.client.chat(
            [
                {"role": "system", "content": prompt},
                {"role": "user", "content": json.dumps(user_payload)},
            ]
        )

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