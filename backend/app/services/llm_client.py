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