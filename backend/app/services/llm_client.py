from __future__ import annotations

from app.services.bedrock_client import get_bedrock_client


class LLMClient:
    async def chat(self, messages: list[dict[str, str]]) -> str:
        system_parts: list[str] = []
        user_parts: list[str] = []

        for message in messages:
            role = message.get("role", "")
            content = message.get("content", "")

            if role == "system":
                system_parts.append(content)
            else:
                user_parts.append(f"{role.upper()}:\n{content}")

        system_prompt = "\n\n".join(part for part in system_parts if part).strip()
        user_prompt = "\n\n".join(part for part in user_parts if part).strip()

        client = get_bedrock_client()
        return await client.generate_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.0,
            max_tokens=400,
        )

    async def classify_intent(self, message: str) -> str | None:
        system_prompt = (
            "You are an intent classifier for a payments agent.\n"
            "Return exactly one label and nothing else.\n"
            "Allowed labels:\n"
            "create_payment_link\n"
            "check_payment_status\n"
            "get_reserve_balance\n"
            "none"
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

        if normalized not in allowed or normalized == "none":
            return None

        return normalized