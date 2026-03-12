# backend/app/services/llm_client.py

from __future__ import annotations

from typing import Any

import httpx

from app.exceptions import AgentExecutionError


class LLMClient:
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "qwen3:4b",
        timeout_seconds: float = 20.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = httpx.Timeout(timeout_seconds)

    async def chat(self, messages: list[dict[str, str]]) -> str:
        url = f"{self.base_url}/api/chat"

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "keep_alive": "10m",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
        except httpx.RequestError as exc:
            raise AgentExecutionError(f"Failed to reach Ollama: {exc}") from exc

        if response.status_code >= 400:
            raise AgentExecutionError(
                f"Ollama returned {response.status_code}: {response.text}"
            )

        data = response.json()
        message = data.get("message", {})
        content = message.get("content")

        if not content:
            raise AgentExecutionError("Ollama returned an empty response.")

        return content.strip()

    async def classify_intent(self, message: str) -> str | None:
        system_prompt = (
            "You are an intent classifier for a payments agent. "
            "Return exactly one of these labels only:\n"
            "- create_payment_link\n"
            "- check_payment_status\n"
            "- get_reserve_balance\n"
            "- none\n"
            "Do not add any explanation."
        )

        result = await self.chat(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ]
        )

        normalized = result.strip().lower()

        allowed = {
            "create_payment_link",
            "check_payment_status",
            "get_reserve_balance",
            "none",
        }

        if normalized not in allowed:
            return None

        if normalized == "none":
            return None

        return normalized