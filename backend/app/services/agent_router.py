# backend/app/services/agent_router.py

from __future__ import annotations

import re
from typing import Any

from app.constants import (
    CHECK_PAYMENT_STATUS,
    CREATE_PAYMENT_LINK,
    GET_RESERVE_BALANCE,
)
from app.services.llm_router import LLMRouter


def extract_amount(message: str) -> float | None:
    match = re.search(r"(\d+(?:\.\d{1,2})?)", message)
    if not match:
        return None
    return float(match.group(1))


def extract_payment_ref(message: str) -> str | None:
    match = re.search(r"(pay_[a-zA-Z0-9]+)", message)
    if not match:
        return None
    return match.group(1)


def detect_intent_rule_based(message: str) -> str | None:
    text = message.lower()

    if "payment link" in text or "collect" in text or "pay" in text:
        return CREATE_PAYMENT_LINK

    if "status" in text:
        return CHECK_PAYMENT_STATUS

    if "balance" in text or "reserve" in text:
        return GET_RESERVE_BALANCE

    return None


async def resolve_route(
    message: str,
    session_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Resolution order:
    1. Rule-based detection
    2. LLM fallback
    """

    intent = detect_intent_rule_based(message)
    source = "rule"

    if intent is None:
        llm_router = LLMRouter()
        intent = await llm_router.detect_intent(message)
        source = "llm" if intent else "none"

    if intent is None:
        return {
            "intent": None,
            "source": source,
            "args": {},
        }

    args: dict[str, Any] = {}

    if intent == CREATE_PAYMENT_LINK:
        amount = extract_amount(message)
        if amount is not None:
            args["amount"] = amount

    elif intent == CHECK_PAYMENT_STATUS:
        payment_ref = extract_payment_ref(message)
        if payment_ref is not None:
            args["payment_ref"] = payment_ref

    elif intent == GET_RESERVE_BALANCE:
        pass

    return {
        "intent": intent,
        "source": source,
        "args": args,
    }