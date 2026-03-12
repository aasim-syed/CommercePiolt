from __future__ import annotations

import re
from typing import Any

from app.tools.payments import (
    check_payment_status,
    create_payment_link,
    get_reserve_balance,
)

SESSION_STORE: dict[str, dict[str, Any]] = {}


def _get_or_create_session(session_id: str | None) -> tuple[str, dict[str, Any]]:
    if not session_id:
        session_id = "demo-session"

    if session_id not in SESSION_STORE:
        SESSION_STORE[session_id] = {
            "merchant_id": None,
            "last_payment_ref": None,
            "last_order_id": None,
            "last_tool_call": None,
        }

    return session_id, SESSION_STORE[session_id]


def _extract_amount(message: str) -> float | None:
    match = re.search(r"(\d+(?:\.\d{1,2})?)", message)
    if not match:
        return None
    return float(match.group(1))


def _extract_payment_ref(message: str) -> str | None:
    match = re.search(r"(pay_[a-zA-Z0-9]+)", message)
    if not match:
        return None
    return match.group(1)


def handle_chat(
    message: str,
    session_id: str | None = None,
    merchant_id: str | None = None,
) -> tuple[str, dict[str, Any] | None, dict[str, Any], dict[str, Any] | None]:
    normalized = message.strip().lower()
    session_id, state = _get_or_create_session(session_id)

    if merchant_id:
        state["merchant_id"] = merchant_id

    active_merchant_id = state.get("merchant_id") or merchant_id

    if "payment link" in normalized or "pay" in normalized or "collect" in normalized:
        amount = _extract_amount(message)
        if amount is None:
            reply = "I could not find the amount. Please specify an amount like 1200."
            return reply, None, state, None

        result = create_payment_link(amount=amount, merchant_id=active_merchant_id)
        state["last_payment_ref"] = result["payment_ref"]
        state["last_order_id"] = result["order_id"]
        state["last_tool_call"] = "create_payment_link"

        reply = (
            f"Created payment link for ₹{result['amount']:.2f}. "
            f"Payment ref: {result['payment_ref']}. "
            f"URL: {result['payment_url']}"
        )

        return (
            reply,
            {"tool_name": "create_payment_link", "arguments": {"amount": amount}},
            state,
            result,
        )

    if "status" in normalized:
        payment_ref = _extract_payment_ref(message) or state.get("last_payment_ref")
        if not payment_ref:
            reply = "I could not find a payment reference. Please share one like pay_abc123."
            return reply, None, state, None

        result = check_payment_status(payment_ref=payment_ref)
        state["last_tool_call"] = "check_payment_status"

        reply = f"Payment {result['payment_ref']} status: {result['status']}."
        return (
            reply,
            {"tool_name": "check_payment_status", "arguments": {"payment_ref": payment_ref}},
            state,
            result,
        )

    if "balance" in normalized or "reserve" in normalized:
        result = get_reserve_balance(merchant_id=active_merchant_id)
        state["last_tool_call"] = "get_reserve_balance"

        reply = (
            f"Your reserve balance is ₹{result['available_balance']:.2f} "
            f"{result['currency']}."
        )
        return (
            reply,
            {"tool_name": "get_reserve_balance", "arguments": {"merchant_id": active_merchant_id}},
            state,
            result,
        )

    reply = (
        "I can help with creating payment links, checking payment status, "
        "and fetching reserve balance."
    )
    return reply, None, state, None
