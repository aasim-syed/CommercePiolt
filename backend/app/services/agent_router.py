from __future__ import annotations

import re
from typing import Any

from app.constants import (
    CHECK_PAYMENT_STATUS,
    CREATE_PAYMENT_LINK,
    GET_RESERVE_BALANCE,
)
from app.services.llm_router import LLMRouter


def extract_amount_rule_based(message: str) -> float | None:
    match = re.search(r"(\d+(?:\.\d{1,2})?)", message)
    if not match:
        return None
    return float(match.group(1))


def extract_payment_ref_rule_based(message: str) -> str | None:
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
    intent = detect_intent_rule_based(message)
    source = "rule"
    llm_router = LLMRouter()

    if intent is None:
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
        amount = extract_amount_rule_based(message)
        if amount is not None:
            args["amount"] = amount

    elif intent == CHECK_PAYMENT_STATUS:
        payment_ref = extract_payment_ref_rule_based(message)
        if payment_ref is not None:
            args["payment_ref"] = payment_ref

    elif intent == GET_RESERVE_BALANCE:
        pass

    missing_required = False

    if intent == CREATE_PAYMENT_LINK and args.get("amount") is None:
        missing_required = True

    if intent == CHECK_PAYMENT_STATUS and args.get("payment_ref") is None:
        missing_required = True

    if missing_required:
        llm_args = await llm_router.extract_tool_args(
            tool_name=intent,
            message=message,
            session_state=session_state,
        )
        args.update(_clean_args(llm_args))
        source = f"{source}+llm_args"

    return {
        "intent": intent,
        "source": source,
        "args": args,
    }


def _clean_args(args: dict[str, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}

    for key, value in args.items():
        if value is None:
            continue

        if isinstance(value, str):
            stripped = value.strip()
            if not stripped or stripped.lower() == "null":
                continue
            cleaned[key] = stripped
            continue

        cleaned[key] = value

    return cleaned